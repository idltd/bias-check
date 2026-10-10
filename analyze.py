"""Paired analysis only. Does not call models or alter corpus/scoring criteria."""
import itertools, random, statistics, json
from pathlib import Path
from common import read, save, raw_records, validate, digest

def mean(a): return statistics.fmean(a)

def paired_inference(diffs,config,seed):
    n=len(diffs)
    if not n: return {'effect':None,'ci95':None,'p':None}
    effect=mean(diffs); rnd=random.Random(seed)
    boot=sorted(mean(rnd.choices(diffs,k=n)) for _ in range(config['bootstrap_samples']))
    ci=[boot[int(.025*(len(boot)-1))],boot[int(.975*(len(boot)-1))]]
    if n<=16:
        perms=[abs(mean([x*s for x,s in zip(diffs,signs)])) for signs in itertools.product([-1,1],repeat=n)]
        p=sum(x>=abs(effect)-1e-12 for x in perms)/len(perms)
    else:
        hits=sum(abs(mean([d*rnd.choice([-1,1]) for d in diffs]))>=abs(effect)-1e-12 for _ in range(config['permutation_samples']))
        p=(hits+1)/(config['permutation_samples']+1)
    sd=statistics.stdev(diffs) if n>1 else 0
    return dict(effect=effect,ci95=ci,p=p,standardized_paired_effect=effect/sd if sd else None)

def analyze_family(rows,config,groups):
    metrics=sorted({key for row in rows for key in row['metrics']})
    out={'conditions':{},'pairwise':[],'within_condition':[]}
    for metric in metrics:
        cells={}
        for row in rows:
            value=row['metrics'].get(metric)
            if value is not None: cells.setdefault((row['test_id'],row['group']),[]).append(value)
        for group in groups:
            values=[v for (t,g),vs in cells.items() if g==group for v in vs]
            binary=metric.endswith('_present') or metric in read('rubric.json')['binary_behaviors'] or metric in ['proposition_substitution','non_direct']
            out['conditions'][metric+'|'+group]=dict(n=len(values),sum=sum(values),mean=mean(values) if values else None,proportion=mean(values) if values and binary else None,positive_count=sum(v==1 for v in values) if binary else None)
            for (test,g),vs in cells.items():
                if g==group:
                    out['within_condition'].append(dict(metric=metric,test_id=test,group=g,n=len(vs),mean=mean(vs),trial_variance=statistics.variance(vs) if len(vs)>1 else None))
        for a,b in itertools.combinations(groups,2):
            # Complete trial cells keep selective failures from changing the paired design.
            tests=sorted({t for t,g in cells if len(cells.get((t,a),[]))==config['trials'] and len(cells.get((t,b),[]))==config['trials']})
            diffs=[mean(cells[t,a])-mean(cells[t,b]) for t in tests]
            result=paired_inference(diffs,config,config['analysis_seed']+len(out['pairwise']))
            out['pairwise'].append(dict(metric=metric,a=a,b=b,paired_templates=len(tests),excluded_templates=len(read('tests.json'))-len(tests),template_effects=dict(zip(tests,diffs)),**result))
    valid=sorted([x for x in out['pairwise'] if x['p'] is not None],key=lambda x:x['p'])
    prev=0
    for i,row in enumerate(valid):
        prev=max(prev,min(1,row['p']*(len(valid)-i))); row['p_holm']=prev
    return out

def load_rater(p,raw):
    mapping=read('private/blinding-map.json'); rubric=read('rubric.json'); scores=read(p)
    expected=set(mapping)
    if {s['blind_id'] for s in scores}!=expected or len(scores)!=len(expected): raise ValueError('Rater must score each blinded response exactly once.')
    raw_index={r['id']:r for r in raw}; result=[]
    for s in scores:
        row=raw_index[mapping[s['blind_id']]['raw_id']]
        if row['error'] or row['protocol_violation']: continue
        treatment=s['proposition_treatment']
        if treatment not in rubric['proposition_treatment']: raise ValueError('Incomplete proposition score '+s['blind_id'])
        for key in rubric['required_text_fields']:
            if not isinstance(s.get(key),str): raise ValueError('Missing text field '+key)
        measures={}
        for key in rubric['binary_behaviors']:
            if s.get(key) not in [0,1,None]: raise ValueError('Invalid binary score')
            measures[key]=s.get(key)
        measures['proposition_substitution']=int(treatment=='substitutes') if treatment!='ambiguous' else None
        measures['non_direct']=int(treatment!='direct') if treatment!='ambiguous' else None
        for level in rubric['proposition_treatment']:
            measures['treatment_'+level+'_present']=int(treatment==level)
        result.append(dict(test_id=row['test_id'],group=row['group'],trial=row['trial'],metrics=measures))
    return result

def main():
    manifest=validate(); raw=raw_records(); config=read('config.json'); groups=read('groups.json')
    if not raw:
        save('analysis/status.json',dict(status='NO_TARGET_RESPONSES',planned=len(manifest),collected=0,conclusions=None))
        Path('analysis/report.md').write_text('# Experiment status\n\nNo target responses were collected. No estimates or conclusions about racial-condition effects are available. See preflight.json.\n',encoding='utf-8')
        return
    for p,h in read('scoring/hashes.json').items():
        if digest(p)!=h: raise ValueError('Scoring artifact changed: '+p)
    mechanical=[r for r in read('scoring/mechanical.json') if r['metrics'] is not None]
    result={'planned':len(manifest),'collected':len(raw),'errors':sum(bool(r['error']) for r in raw),'protocol_violations':sum(bool(r['protocol_violation']) for r in raw),'complete':len(raw)==len(manifest),'families':{'mechanical':analyze_family(mechanical,config,groups)}}
    rater_rows={}
    for name in ['rater1','rater2']:
        p=Path('scoring')/(name+'.json')
        if p.exists():
            rows=load_rater(p,raw); rater_rows[name]=rows
            result['families'][name]=analyze_family(rows,config,groups)
            result[name+'_sha256']=digest(p)
    result['semantic_scoring_status']='complete' if len(rater_rows)==2 else 'pending: two independent human raters required'
    if len(rater_rows)==2:
        agreement={}
        r1={(r['test_id'],r['group'],r['trial']):r['metrics'] for r in rater_rows['rater1']}
        r2={(r['test_id'],r['group'],r['trial']):r['metrics'] for r in rater_rows['rater2']}
        for metric in next(iter(r1.values()),{}):
            pairs=[(r1[k][metric],r2[k][metric]) for k in r1 if k in r2 and r1[k][metric] is not None and r2[k][metric] is not None]
            agreement[metric]=dict(n=len(pairs),agreements=sum(a==b for a,b in pairs),agreement_rate=mean([a==b for a,b in pairs]) if pairs else None)
        result['rater_agreement']=agreement
    save('analysis/statistics.json',result)
    lines=['# Experiment report','',f"Collected {len(raw)} of {len(manifest)} planned calls. Errors: {result['errors']}; protocol violations: {result['protocol_violations']}.",'',result['semantic_scoring_status'],'','Effects are A minus B, paired within template. Intervals use template-cluster bootstrap; p-values use paired sign-flip tests and Holm correction. Corpus is purposive. Lexical proxies are not semantic judgments. Positive effects do not universally mean favorable treatment. Do not infer developer intentions.','']
    for name,family in result['families'].items():
        lines += ['## '+name,'','|Metric|A|B|Templates|Effect|95% CI|Holm p|','|---|---|---|---:|---:|---|---:|']
        for r in family['pairwise']:
            lines.append(f"|{r['metric']}|{r['a']}|{r['b']}|{r['paired_templates']}|{r['effect']}|{r['ci95']}|{r.get('p_holm')}|")
        # Examples are selected deterministically by absolute effect, never by direction.
        ranked=sorted((r for r in family['pairwise'] if r['effect'] is not None),key=lambda r:(-abs(r['effect']),r['metric'],r['a'],r['b']))[:10]
        lines+=['','## Largest observed differences: '+name,'']
        for r in ranked:
            if not r['template_effects']: continue
            test=min(r['template_effects'],key=lambda t:(-abs(r['template_effects'][t]),t))
            lines+=['### '+r['metric']+' / '+test,'']
            for trial in range(1,config['trials']+1):
                matched=[next(x for x in raw if x['test_id']==test and x['group']==g and x['trial']==trial) for g in [r['a'],r['b']]]
                import html
                lines+=['<table><tr>'+''.join('<th>'+html.escape(x['group'])+' trial '+str(trial)+'</th>' for x in matched)+'</tr><tr>'+''.join('<td><pre>'+html.escape(x['prompt'])+'</pre><pre>'+html.escape(x['exact_response'])+'</pre></td>' for x in matched)+'</tr></table>','']
    Path('analysis/report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Complete archive includes every output, including errors/ambiguous/identical cases.
    save('analysis/all-responses.json',raw)
    save('analysis/hashes.json',{str(p):digest(p) for p in Path('analysis').iterdir() if p.is_file()})

if __name__=='__main__': main()
