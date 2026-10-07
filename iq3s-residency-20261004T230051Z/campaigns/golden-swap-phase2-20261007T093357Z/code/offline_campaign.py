"""Single deterministic evaluation per tape/scorer/lifecycle point. No latency claims."""
import os,subprocess,time,hashlib,argparse
from common import *
def point(task,policy,tc,post=0,th=.5):
 label=f"{task['task_id']}-{policy}-tc{tc}-post{post}-th{th}";p=pathlib.Path(os.environ.get('RAD_OFFLINE_OUTPUT_ROOT',str(W/'raw/offline')))/label;p.mkdir(parents=True,exist_ok=False)
 env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=task['trace_path'],STRATA_Q4_TAPE_MODE='replay',STRATA_Q4_ORACLE_MODE='full',STRATA_Q4_ORACLE_INCOMING='full',STRATA_Q4_ORACLE_VICTIM='full',STRATA_Q4_CAUSAL_VICTIM='off' if policy=='full' else policy,STRATA_Q4_VICTIM_THRESHOLD=str(th),STRATA_Q4_VICTIM_MODEL=str(C/'models/logistic.txt'),STRATA_Q4_TRANSACTION_CONTROL=str(tc),STRATA_Q4_POST_USE_EVENTS=str(post),STRATA_Q4_SIM_LOG=str(p/'transactions'))
 cmd=[str(W/'builds/offline'),'transfer','0','0'];save(p/'protocol.json',{'command':cmd,'env':{k:v for k,v in env.items() if k.startswith('STRATA_')},'simulator_sha256':hashlib.file_digest((W/'builds/offline').open('rb'),'sha256').hexdigest()});start=time.monotonic()
 with Heartbeat('offline '+label,3),(p/'stdout.json').open('x') as f,(p/'stderr.log').open('x') as err:subprocess.run(cmd,env=env,stdout=f,stderr=err,check=True,timeout=90)
 r=load(p/'stdout.json');r.update(task=task['task_id'],split=task['split'],policy=policy,tc=tc,post=post,threshold=th,simulation_s=time.monotonic()-start,transactions=str(p/'transactions-admissions.bin'),measured_TG=None)
 assert sum(r[k] for k in ['completed_unpublished_bytes','published_used_bytes','evicted_without_use_bytes','no_use_resident_end_bytes'])==r['copied_bytes']
 assert r['local']+r['cpu']+r['mapped']==load(P0/'raw'/task['task_id']/'validation.json')['main_routed_entries']
 save(p/'result.json',r);ledger('Offline point complete',label=label,copy_bytes=r['copied_bytes'],nonlocal_entries=r['cpu']+r['mapped']);print('OFFLINE',label,'nonlocal',r['cpu']+r['mapped'],'GB',round(r['copied_bytes']/1e9,3),'unusedGB',round(r['unused_bytes']/1e9,3),flush=True);return r
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--single-task');q.add_argument('--policy',choices=['full','native','logistic'],default='native');q.add_argument('--tc',type=int,choices=[0,1],default=1);q.add_argument('--post',type=int,choices=[0,48],default=0);q.add_argument('--threshold',type=float,choices=[.2,.5],default=.5);args=q.parse_args();no_gpu();tasks=[t for t in load(P0/'benchmark-manifest.json')['tasks'] if t['split']!='reserved_evaluation'];rows=[]
 if args.single_task:
  t=next(t for t in tasks if t['task_id']==args.single_task);assert 'RAD_OFFLINE_OUTPUT_ROOT' in os.environ,'Single-point reproduction requires a separate explicit output root';point(t,args.policy,args.tc,args.post,args.threshold);raise SystemExit(0)
 for t in tasks:
  v=load(P0/'raw'/t['task_id']/'validation.json');rows.append({'task':t['task_id'],'split':t['split'],'policy':'current','tc':0,'post':0,'cpu':v['main_dispatch_counts']['cpu'],'mapped':v['main_dispatch_counts']['mapped'],'local':v['main_dispatch_counts']['local'],'source':'Phase0 recorded current reconstruction validated at every service slot; no synthetic native adaptation'})
  for policy,tc,post,th in [('full',0,0,.5),('native',0,0,.5),('logistic',0,0,.5),('native',1,0,.5),('logistic',1,0,.5),('native',1,48,.5),('logistic',1,48,.5)]:
   rows.append(point(t,policy,tc,post,th));save(C/'results/offline-competition.json',rows)
 progress(3,'Matched development/calibration competition complete',points=len(rows),next_action='Freeze common treatment from frontier; check threshold sensitivity')
