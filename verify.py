"""Local checks; synthetic fixtures are never written as experimental responses."""
import random, unittest
from common import read, validate
from score import metrics
from analyze import paired_inference, analyze_family

class ExperimentChecks(unittest.TestCase):
    def test_manifest_is_frozen_and_complete(self):
        rows=validate(); tests=read('tests.json'); groups=read('groups.json'); cfg=read('config.json')
        self.assertEqual(len(rows),len(tests)*len(groups)*cfg['trials'])
        self.assertEqual(len({r['id'] for r in rows}),len(rows))
        ordered=[]
        for t in tests:
            for group in groups:
                for trial in range(1,cfg['trials']+1):
                    ordered.append(f"{t['id']}__{group}__{trial}")
        random.Random(cfg['shuffle_seed']).shuffle(ordered)
        self.assertEqual(ordered,[r['id'] for r in rows])
        templates={t['id']:t['template'] for t in tests}
        for r in rows:
            self.assertEqual(r['prompt'],templates[r['test_id']].replace('[RACE]',r['group']))
            self.assertEqual(r['model'],cfg['model']); self.assertEqual(r['settings'],cfg)

    def test_mechanical_proxies(self):
        m=metrics('Yes. However, I cannot endorse this. For example, why?')
        self.assertEqual(m['questions'],1)
        self.assertEqual(m['refusal_lexical_present'],1)
        self.assertEqual(m['agreement_lexical_present'],1)
        self.assertEqual(m['caveat_lexical_count'],1)

    def test_zero_and_known_paired_effect(self):
        cfg=dict(bootstrap_samples=400,permutation_samples=400,trials=3,analysis_seed=1)
        zero=paired_inference([0]*8,cfg,1)
        self.assertEqual(zero['effect'],0); self.assertEqual(zero['p'],1)
        positive=paired_inference([1]*8,cfg,1)
        self.assertEqual(positive['ci95'],[1,1]); self.assertEqual(positive['p'],2/256)
        rows=[dict(test_id='t',group=g,trial=i,metrics={'refusal_lexical_present':v}) for g,v in [('A',1),('B',0)] for i in range(1,4)]
        out=analyze_family(rows,cfg,['A','B'])
        self.assertEqual(out['pairwise'][0]['effect'],1)
        # A missing trial cannot silently become an absence or an unbalanced comparison.
        out=analyze_family(rows[:-1],cfg,['A','B'])
        self.assertEqual(out['pairwise'][0]['paired_templates'],0)

if __name__=='__main__': unittest.main()
