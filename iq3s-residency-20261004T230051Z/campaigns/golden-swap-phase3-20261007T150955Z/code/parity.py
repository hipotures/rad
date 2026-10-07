"""Deterministic OFF/ON comparison: every candidate outcome and complete logical journals."""
import subprocess,hashlib,os
import numpy as np
from inspect_oracle import E
from common import *
no_gpu();env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};rows=[]
compile_common=['g++','-O3','-std=c++20','-pthread','-I'+str(SOURCE/'include'),'-I/usr/local/cuda/include']
for src,out in [(C/'tests/memo_fixture.cpp',W/'builds/memo-fixture'),(C/'code/offline.cpp',W/'builds/offline')]:
 cmd=[*compile_common,str(src),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(out)]
 if not out.exists():
  with Heartbeat('parity compile '+src.name,3),(W/'logs'/('compile-'+src.stem+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
if not (C/'tests/memo-fixture.log').exists():
 with (C/'tests/memo-fixture.log').open('x') as f:subprocess.run([str(W/'builds/memo-fixture')],env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
tasks=load(P0/'benchmark-manifest.json')['tasks'];ind=load(C/'inputs/independent-task-manifest.json');tasks.append(ind)
for task in tasks:
 for policy in ['native','logistic']:
  pair=[]
  for opt in [0,1]:
   prefix=W/'raw'/f'parity-{task["task_id"]}-{policy}-opt{opt}';e=env.copy();e.update(STRATA_Q4_TAPE=task['trace_path'],STRATA_Q4_TAPE_MODE='replay',STRATA_Q4_CAUSAL_VICTIM=policy,STRATA_Q4_VICTIM_MODEL=str(C/'models/logistic.txt'),STRATA_Q4_VICTIM_THRESHOLD='0.5',STRATA_Q4_TRANSACTION_CONTROL='1',STRATA_Q4_POST_USE_EVENTS='0',STRATA_Q4_PLANNER_OPT=str(opt),STRATA_Q4_DECISION_AUDIT='1',STRATA_Q4_CACHE_TIMING='1',STRATA_Q4_SIM_LOG=str(prefix))
   begin=time.monotonic()
   log=W/'logs'/(prefix.name+'.log')
   if log.exists():output=log.read_text()
   else:
    with Heartbeat('parity '+prefix.name,3):r=subprocess.run([str(W/'builds/offline'),'transfer','0','0'],env=e,capture_output=True,text=True,timeout=120)
    log.write_text(r.stdout+r.stderr);assert r.returncode==0,(prefix,r.stderr);output=r.stdout
   parsed=[json.loads(x) for x in output.splitlines() if x.startswith('{')];assert len(parsed)==2
   pair.append({'opt':opt,'elapsed_s':time.monotonic()-begin,'accounting':parsed[0],'decisions':parsed[1],'journals':{suffix:hashlib.file_digest(pathlib.Path(str(prefix)+suffix).open('rb'),'sha256').hexdigest() for suffix in ['-admissions.bin','-lifecycle.bin']}})
  ignored={'scorer_feature_ms','scorer_model_ms','scorer_selection_ms','cache_hits'}
  assert {k:v for k,v in pair[0]['accounting'].items() if k not in ignored}=={k:v for k,v in pair[1]['accounting'].items() if k not in ignored},('accounting parity',task['task_id'],policy)
  for key in ['candidate_hash','candidate_records']:assert pair[0]['decisions'][key]==pair[1]['decisions'][key],('candidate parity',task['task_id'],policy,key)
  assert pair[0]['journals']['-lifecycle.bin']==pair[1]['journals']['-lifecycle.bin'],('lifecycle journals',task['task_id'],policy)
  logical=[]
  for opt in [0,1]:
   v=np.fromfile(W/'raw'/f'parity-{task["task_id"]}-{policy}-opt{opt}-admissions.bin',E);v['issue_ns']=0;logical.append(hashlib.sha256(v.tobytes()).hexdigest())
  assert logical[0]==logical[1],('logical admission/ownership journals',task['task_id'],policy)
  for point,h in zip(pair,logical):point['logical_admissions_sha256']=h
  pair[0]['normalization']='Only issue_ns is an actual host clock in the simulator, not a modeled policy input; cleared for logical hash. All other fields and complete lifecycle bytes match.'
  rows.append({'task':task['task_id'],'policy':policy,'state':'PASS','pair':pair});save(C/'tests/deterministic-parity.json',rows)
  progress(3,'Deterministic candidate and generation parity PASS',task=task['task_id'],arm=policy,completed=len(rows),remaining=26-len(rows),next_action='Next frozen tape/scorer pair')
print('PARITY ALL',len(rows),flush=True)
