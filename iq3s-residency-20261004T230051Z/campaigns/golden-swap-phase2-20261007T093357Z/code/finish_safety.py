import subprocess,os
from common import *
no_gpu();env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(STRATA_Q4_TAPE=next(t for t in load(P0/'benchmark-manifest.json')['tasks'] if t['task_id']=='math-rational')['trace_path'],STRATA_Q4_TAPE_MODE='replay')
with Heartbeat('information fixture environment repair',2),(C/'tests/information-attempt2.log').open('x') as f:r=subprocess.run([str(W/'builds/information-fixture')],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90)
ledger('Information fixture repair: supplied required real development tape',exit_code=r.returncode,earlier_failure='missing environment, no source or binary change');assert r.returncode==0
for stem in ['offline','history-fixture','scorer-fixture']:
 source=C/'code/offline.cpp' if stem=='offline' else C/'tests'/str(stem.replace('-','_')+'.cpp')
 cmd=['g++','-O3','-std=c++20','-pthread','-I'+str(SOURCE/'include'),'-I/usr/local/cuda/include',str(source),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(W/'builds'/stem)]
 with Heartbeat('compile '+stem,2),(W/'logs'/f'compile-{stem}-finish.log').open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=120)
cmd=[str(C.parents[1]/'src/control/.venv/bin/ctest'),'--test-dir',str(BUILD),'--output-on-failure','--timeout','90','-R','^(native_expert_parity_q4_K_q5_1|native_expert_parity_q4_K_q8_0|native_expert_parity_q5_K_q8_0|qsa_topk_active_parity|spec_controller_test|draft_policy_test|coupled_draft_test|route_window_parity|kv_stream_parity|native_grouped_parity|pool_affinity_linux_test)$']
with Heartbeat('native targeted tests',2),(C/'tests/native-attempt1.log').open('x') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
ledger('Targeted native tests',exit_code=r.returncode);save(C/'tests/native-outcome.json',{'exit_code':r.returncode});no_gpu()
