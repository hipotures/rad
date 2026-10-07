"""Bounded policy competition. Simulated costs are not measured TG or live gain retention."""
import argparse,os,subprocess,time,csv,hashlib
import numpy as np
from common import *
from validate_traces import L,N
from legacy_tape import Tape

def recorded_current(task):
 p=P0/'raw'/task['task_id'];a=np.fromfile(p/'raw/native-layers.bin',L);n=np.fromfile(p/'raw/native-native.bin',N);r=load(p/'validation.json');return {'task':task['task_id'],'family':task['family'],'split':task['split'],'policy':'current','threshold':None,'local':r['main_dispatch_counts']['local'],'cpu':r['main_dispatch_counts']['cpu'],'mapped':r['main_dispatch_counts']['mapped'],'copied_bytes':int(n['bytes'].sum()),'issued':len(n),'published':int(np.count_nonzero(n['publish_ns'])),'victim_absent_observations':None,'measurement_kind':'RECORDED_NATIVE_DEMAND_ACCOUNTING_VALIDATED_WITH_RECONSTRUCTED_STATE','measured_model_TG':None}
def point(task,policy,threshold):
 label=task['task_id']+'-'+policy+('-'+str(threshold) if threshold is not None else '');p=C/'results/offline'/label;env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=task['trace_path'],STRATA_Q4_TAPE_MODE='replay',STRATA_Q4_ORACLE_MODE='full',STRATA_Q4_ORACLE_INCOMING='full',STRATA_Q4_ORACLE_VICTIM='full',STRATA_Q4_CAUSAL_VICTIM='off' if policy=='full' else policy)
 if threshold is not None:env['STRATA_Q4_VICTIM_THRESHOLD']=str(threshold)
 if policy in ['logistic','tree']:env['STRATA_Q4_VICTIM_MODEL']=str(C/'models'/(policy+'.txt'))
 cmd=[str(C/'builds/offline'),'transfer','0','0'];effective={k:v for k,v in env.items() if k.startswith('STRATA_')}
 if (p/'result.json').exists():
  prior=load(p/'command.json');assert prior['command']==cmd and prior['environment']==effective,'Existing evaluator point identity mismatch'
  stamp=(p/'command.json').stat().st_mtime_ns
  dependencies=[C/'builds/offline',C/'scripts/offline.cpp',C/'source/runtime/include/strata/research/q4_oracle.hpp',C/'source/runtime/include/strata/research/q4_victim_model.hpp']
  if policy in ['logistic','tree']:dependencies.append(C/'models'/(policy+'.txt'))
  assert all(x.stat().st_mtime_ns<=stamp for x in dependencies),'Evaluator dependency changed; version this point'
  r=load(p/'result.json');assert r['local']+r['cpu']+r['mapped']==load(P0/'raw'/task['task_id']/'validation.json')['main_routed_entries']
  save(p/'reuse-validation.json',{'state':'PASS','command_environment_equal':True,'unchanged_dependency_hashes':{str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in dependencies}});ledger('Reuse completed identical deterministic offline point after artifact-path repair',label=label);return r
 p.mkdir(parents=True,exist_ok=False)
 save(p/'command.json',{'command':cmd,'environment':{k:v for k,v in env.items() if k.startswith('STRATA_')},'seed':20261006});begin=time.monotonic()
 with Heartbeat('offline '+label,2):
  with (p/'stdout.log').open('x') as out,(p/'stderr.log').open('x') as err:result=subprocess.run(cmd,env=env,stdout=out,stderr=err,timeout=180)
 assert result.returncode==0,(label,result.returncode);r=load(p/'stdout.log');r.update(task=task['task_id'],family=task['family'],split=task['split'],policy=policy,threshold=threshold,evaluation_wall_s=time.monotonic()-begin,measurement_kind='MODELED_TRANSFER_DEMAND_NOT_MEASURED_TG',physical_spares=5,restoration_bytes=17305600,cost_model='Main0.57ms/invocation, MTP2.5ms/window; staging25GB/s,H2D13.2GB/s,publication45us; no exposed CPU latency model',guard='Common risk veto at incoming demand interval for causal models and cheap matched controls; weighted1/.5/.25/.125 cumulative return-risk ranking. No new incoming utility ranking.');save(p/'result.json',r);assert r['local']+r['cpu']+r['mapped']==load(P0/'raw'/task['task_id']/'validation.json')['main_routed_entries'];progress(2,'Offline '+label+' complete',task=task['task_id'],policy=policy,nonlocal_entries=r['cpu']+r['mapped'],copy_GB=r['copied_bytes']/1e9,evaluation_wall_s=r['evaluation_wall_s']);return r

def main():
 q=argparse.ArgumentParser();q.add_argument('phase',choices=['smoke','competition','reserved']);args=q.parse_args();no_gpu();tasks=load(P0/'benchmark-manifest.json')['tasks'];rows=[]
 if args.phase=='smoke':tasks=[next(t for t in tasks if t['task_id']=='math-rational')];policies=[('full',None),('recency',.5),('logistic',.5)]
 elif args.phase=='competition':tasks=[t for t in tasks if t['split']!='reserved_evaluation'];policies=[('full',None)]+[(p,th) for p in ['native','recency','logistic','tree'] for th in [.2,.5]]
 else:
  frozen=load(C/'models/selection.json');tasks=[t for t in tasks if t['split']=='reserved_evaluation'];policies=[('full',None),('native',frozen['threshold']),('recency',frozen['threshold']),(frozen['policy'],frozen['threshold'])]
 for task in tasks:
  rows.append(recorded_current(task))
  for policy,threshold in policies:rows.append(point(task,policy,threshold));save(C/'results'/('offline-'+args.phase+'.json'),rows)
 if args.phase=='competition':
  # Freeze before any reserved policy results: task-normalized demand, traffic/churn and score overhead.
  scores=[]
  for policy,threshold in policies:
   if policy=='full':continue
   vals=[];wins=0
   for task in [t for t in tasks if t['split']=='calibration']:
    current=next(r for r in rows if r['task']==task['task_id'] and r['policy']=='current');candidate=next(r for r in rows if r['task']==task['task_id'] and r['policy']==policy and r['threshold']==threshold)
    ratio=(candidate['cpu']+candidate['mapped'])/(current['cpu']+current['mapped']);traffic=candidate['copied_bytes']/max(1,current['copied_bytes']);wins+=ratio<1
    # Cost proxy is explicitly assumed: one extra baseline copy-budget costs .1 normalized miss demand.
    vals.append(ratio+.1*traffic+.01*candidate.get('scorer_selection_ms',0)/1000)
   scores.append({'policy':policy,'threshold':threshold,'calibration_mean_proxy':float(np.mean(vals)),'calibration_task_wins':wins})
  learned=[r for r in scores if r['policy'] in ['logistic','tree']];best=min(learned,key=lambda r:r['calibration_mean_proxy']);cheap=min([r for r in scores if r['policy'] in ['native','recency']],key=lambda r:r['calibration_mean_proxy']);best.update(selection_scope='All four families, predeclared; development fit and calibration operating point only',candidates=scores,cheap_reference=cheap,promising=best['calibration_task_wins']>=3,checkpoint_sha256=hashlib.sha256((C/'models'/(best['policy']+'.txt')).read_bytes()).hexdigest(),ranking_weights=[1,.5,.25,.125],fallback='Invalid scores use same causal native-heat proxy; no victim-future fallback',frozen_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat());save(C/'models/selection.json',best);ledger('Runtime finalist frozen before reserved evaluation',**best);print('FROZEN',best,flush=True)
if __name__=='__main__':main()
