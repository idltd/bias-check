"""Execution only. No scoring, prompt generation, model selection or retries."""
import json, subprocess, shutil
from pathlib import Path
from datetime import datetime, timezone
from common import validate, save, digest

def now(): return datetime.now(timezone.utc).isoformat()

def main():
    manifest=validate()
    backend=manifest[0]['settings']['backend']
    exe=shutil.which('codex')
    if backend=='codex-cli':
        check=subprocess.run([exe,'login','status'],capture_output=True,text=True,encoding='utf-8') if exe else None
        if not check or check.returncode:
            save('preflight.json',dict(timestamp=now(),experimental_requests_sent=0,error=check.stderr if check else 'Codex not installed'))
            raise SystemExit('Preflight failed; no experimental requests sent. See preflight.json.')
    isolated=Path('isolated').resolve(); isolated.mkdir(exist_ok=True)
    if list(isolated.iterdir()): raise ValueError('Isolation directory must be empty.')
    Path('raw').mkdir(exist_ok=True)
    for entry in manifest:
        p=Path('raw')/(entry['id']+'.json')
        if p.exists(): continue
        claim=p.with_suffix('.started')
        if claim.exists(): raise ValueError('Interrupted request cannot silently be resent: '+entry['id'])
        validate()
        claim.write_text(now(),encoding='utf-8')
        timestamp=now(); error=None; events=[]; stderr=''; stdout=''; code=None; args=[]
        if backend=='manual':
            print('\nOpen a NEW temporary chat, with memory/custom instructions OFF, same model/settings.\n'+entry['prompt'])
            input('Press Enter after sending this exact prompt. ')
            print('Paste the COMPLETE response. Finish with a line containing only END_RESPONSE.')
            lines=[]
            while (line:=input())!='END_RESPONSE': lines.append(line)
            response='\n'.join(lines)
            metadata=input('Record visible model/version, UI settings, errors and context limitations: ')
            events=[dict(manual_metadata=metadata)]
        else:
            args=[exe,'exec','--ephemeral','--ignore-user-config','--skip-git-repo-check','--sandbox','read-only','--json','--color','never','--cd',str(isolated),'--model',entry['model'],'-c','model_reasoning_effort="low"','-c','project_doc_max_bytes=0','-c','developer_instructions='+json.dumps(entry['settings']['developer_instructions']),'-']
            try:
                result=subprocess.run(args,input=entry['prompt'],capture_output=True,text=True,encoding='utf-8',timeout=entry['settings']['timeout_seconds'])
                stdout,stderr,code=result.stdout,result.stderr,result.returncode
                if code: error='CLI exit '+str(code)
            except subprocess.TimeoutExpired as e:
                error='Request timed out; no retry'; stdout=(e.stdout or b'').decode('utf-8',errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or '')
                stderr=str(e)
            for line in stdout.splitlines():
                try: events.append(json.loads(line))
                except json.JSONDecodeError: pass
            response='\n\n'.join(e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message')
        violation=any(e.get('item',{}).get('type') in ['command_execution','mcp_tool_call','web_search','file_change'] for e in events)
        save(p,dict(**entry,request_timestamp=timestamp,response_timestamp=now(),exact_response=response,events=events,stdout=stdout,stderr=stderr,exit_code=code,error=error,protocol_violation='tool use' if violation else None,command_arguments=args,manifest_sha256=digest('manifest.json')))
        save(str(p)+'.sha256.json',dict(sha256=digest(p)))
        print(entry['id']+' recorded')

if __name__=='__main__': main()
