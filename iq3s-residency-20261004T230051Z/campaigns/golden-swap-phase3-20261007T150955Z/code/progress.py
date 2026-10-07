import json,time,datetime,os,argparse,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def update(step,status,message,**extra):
 c=json.loads((ROOT/'clock.json').read_text());elapsed=time.monotonic()-c['start_monotonic_s']
 previous=json.loads((ROOT/'progress.json').read_text()) if (ROOT/'progress.json').exists() else {}
 retained={k:v for k,v in previous.items() if k in ['task','arm','version','completed','remaining','next_action','eta_range_s']} if previous.get('step')==step else {}
 retained.update(extra)
 extra=retained
 r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),step=step,status=status,message=message,elapsed_s=elapsed,remaining_s=max(0,c['hard_budget_s']-elapsed),**extra)
 r.setdefault('eta','unknown')
 tmp=ROOT/('progress.json.tmp.'+str(os.getpid())+'.'+str(threading.get_ident()));tmp.write_text(json.dumps(r,indent=2)+'\n');os.replace(tmp,ROOT/'progress.json')
 with (ROOT/'progress.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
 (ROOT/'STATUS.md').write_text(f"# Phase 3 status\n\nSTEP {step}/5 {status}: {message}\n\nElapsed {elapsed/60:.1f} min; remaining {r['remaining_s']/60:.1f} min. ETA: {r['eta']}.\n\n"+json.dumps(extra,indent=2)+'\n')
 print('[PHASE 3]',json.dumps(r),flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('step',type=int);a.add_argument('status');a.add_argument('message');v=a.parse_args();update(v.step,v.status,v.message)
