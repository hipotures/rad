import argparse,datetime,json,os,pathlib,time,threading
LOCK=threading.RLock()
C=pathlib.Path(__file__).resolve().parents[1]
def _update(step,activity,state='RUNNING',**kw):
 t=json.loads((C/'timing.json').read_text());now=time.monotonic();old=json.loads((C/'progress.json').read_text()) if (C/'progress.json').exists() else {}
 d={**old,'step':step,'activity':activity,'state':state,'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'last_heartbeat_monotonic':now,'elapsed_s':now-t['start_monotonic'],'remaining_s':max(0,t['deadline_monotonic']-now),'owned_pid':old.get('owned_pid'),'request_state':old.get('request_state','NONE'),'blocker_notes':old.get('blocker_notes',[]),**kw}
 tmp=C/'progress.json.tmp';tmp.write_text(json.dumps(d,indent=2)+'\n');os.replace(tmp,C/'progress.json')
 with (C/'progress.jsonl').open('a') as f:f.write(json.dumps(d)+'\n')
 (C/'STATUS.md').write_text('# Phase 0 progress\n\n'+json.dumps(d,indent=2)+'\n')
 print(f"[PHASE 0 | STEP {step}/5 {state}] {activity} | elapsed {d['elapsed_s']/60:.1f}m | remaining {d['remaining_s']/60:.1f}m",flush=True)
 return d
def update(*args,**kwargs):
 with LOCK:return _update(*args,**kwargs)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--step',type=int);p.add_argument('--activity');p.add_argument('--state',default='RUNNING');a=p.parse_args()
 if a.step:update(a.step,a.activity,a.state)
 else:print((C/'progress.json').read_text())
