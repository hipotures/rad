"""Compile targeted fixtures, run real copies, and retain actual existing native-test outcomes."""
import subprocess,os,hashlib,time
from common import *
no_gpu();venv=C.parents[1]/'src/control/.venv/bin';src=C/'source/runtime';env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env['CUDA_VISIBLE_DEVICES']='0,1'
with Heartbeat('targeted safety build and real copies',3):
 for stem in ['cost_guard','oracle']:
  cmd=['g++','-O2','-std=c++20','-pthread','-I'+str(src/'include'),'-I/usr/local/cuda/include',str(C/'tests'/(stem+'_fixture.cpp')),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(C/'builds'/(stem+'-fixture'))];ledger('Safety fixture build',command=cmd);subprocess.run(cmd,check=True,timeout=120)
 for name,cmd,mode in [('cost-guard-fixture',[str(C/'builds/cost_guard-fixture')],'off'),('real-copy-full',[str(C/'builds/oracle-fixture')],'off'),('real-copy-learned',[str(C/'builds/oracle-fixture')],load(C/'models/selection.json')['policy'])]:
  e=env.copy();e['STRATA_Q4_CAUSAL_VICTIM']=mode
  if mode!='off':selection=load(C/'models/selection.json');e.update(STRATA_Q4_VICTIM_MODEL=str(C/'models'/(selection['policy']+'.txt')),STRATA_Q4_VICTIM_THRESHOLD=str(selection['threshold']))
  logpath=C/'tests'/(name+'.log');attempt=1
  while logpath.exists():attempt+=1;logpath=C/'tests'/(name+'-attempt'+str(attempt)+'.log')
  with logpath.open('x') as f:subprocess.run(cmd,env=e,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
  progress(3,'Safety PASS '+name)
 cmd=[str(venv/'ctest'),'--test-dir',str(C/'builds/runtime'),'--output-on-failure','--timeout','90','-R','^(native_expert_parity_q4_K_q5_1|native_expert_parity_q4_K_q8_0|native_expert_parity_q5_K_q8_0|qsa_topk_active_parity|spec_controller_test|draft_policy_test|coupled_draft_test|route_window_parity|kv_stream_parity|native_grouped_parity|pool_affinity_linux_test)$']
 with (C/'tests/targeted-native.log').open('x') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
 save(C/'tests/safety-summary.json',{'real_copy_fixtures':'PASS','cost_guard_fixture':'PASS','native_test_exit_code':p.returncode,'native_log':'tests/targeted-native.log','full_suite':'Not newly rerun; prior environmental failures remain historical','model_checkpoint':load(C/'models/selection.json')['checkpoint_sha256']});no_gpu();print('SAFETY COMPLETE native exit',p.returncode,flush=True)
