"""Targeted inherited safety, frozen scorer, and actual flag-wait timing validation."""
import subprocess,os,shutil
from common import *
no_gpu();env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env['CUDA_VISIBLE_DEVICES']='0,1';env['STRATA_Q4_PUBLICATION_TRACE']='1';outcomes=[]
for stem in ['lifecycle','oracle','policy','cost_guard','information','history','scorer','wait','trace']:
 cmd=['g++','-O2','-std=c++20','-pthread','-I'+str(SOURCE/'include'),'-I/usr/local/cuda/include',str(C/'tests'/f'{stem}_fixture.cpp')]
 if stem in ['wait','trace']:cmd+=[str(BUILD/'libstrata_kernels.a')]
 cmd+=['-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(W/'builds'/f'{stem}-fixture')]
 with Heartbeat('compile '+stem,3),(W/'logs'/f'compile-{stem}.log').open('x') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 assert r.returncode==0,stem
 if stem in ['history','scorer']:continue
 e=env.copy()
 if stem=='information':
  task=next(t for t in load(P0/'benchmark-manifest.json')['tasks'] if t['task_id']=='math-rational');e.update(STRATA_Q4_TAPE=task['trace_path'],STRATA_Q4_TAPE_MODE='replay')
 cmd=[str(W/'builds'/f'{stem}-fixture')]
 with Heartbeat('fixture '+stem,3),(C/'tests'/f'{stem}-attempt1.log').open('x') as f:r=subprocess.run(cmd,env=e,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 outcomes.append({'fixture':stem,'exit_code':r.returncode});save(C/'tests/safety-outcomes.json',outcomes);assert r.returncode==0,stem
cmd=[str(INPUT_PARENT.parent/'src/control/.venv/bin/ctest'),'--test-dir',str(BUILD),'--output-on-failure','--timeout','90','-R','^(native_expert_parity_q4_K_q5_1|native_expert_parity_q4_K_q8_0|native_expert_parity_q5_K_q8_0|qsa_topk_active_parity|draft_policy_test|coupled_draft_test|route_window_parity|kv_stream_parity|native_grouped_parity)$']
with Heartbeat('targeted native tests',3),(C/'tests/native-attempt1.log').open('x') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
save(C/'tests/native-outcome.json',{'exit_code':r.returncode});assert r.returncode==0;no_gpu()
