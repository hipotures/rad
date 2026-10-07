"""Complete unrun safety checks after standalone-header repair; preserve passed attempts."""
from common import *
import os
no_gpu();env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(CUDA_VISIBLE_DEVICES='0,1',STRATA_Q4_PUBLICATION_TRACE='1');outcomes=load(C/'tests/safety-outcomes.json')
for stem in ['wait','trace','memo']:
 cmd=['g++','-O2','-std=c++20','-pthread','-I'+str(SOURCE/'include'),'-I/usr/local/cuda/include',str(C/'tests'/f'{stem}_fixture.cpp')]
 if stem in ['wait','trace']:cmd+=[str(BUILD/'libstrata_kernels.a')]
 cmd+=['-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(W/'builds'/f'{stem}-fixture')]
 with Heartbeat('compile remaining '+stem,2),(W/'logs'/f'compile-{stem}-header-repair.log').open('x') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 assert r.returncode==0,stem
 with Heartbeat('fixture remaining '+stem,2),(C/'tests'/f'{stem}-attempt1.log').open('x') as f:r=subprocess.run([str(W/'builds'/f'{stem}-fixture')],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=120)
 outcomes.append({'fixture':stem,'exit_code':r.returncode});save(C/'tests/safety-outcomes.json',outcomes);assert r.returncode==0,stem
cmd=[str(INPUT_PARENT.parent/'src/control/.venv/bin/ctest'),'--test-dir',str(BUILD),'--output-on-failure','--timeout','90','-R','^(native_expert_parity_q4_K_q5_1|native_expert_parity_q4_K_q8_0|native_expert_parity_q5_K_q8_0|qsa_topk_active_parity|draft_policy_test|coupled_draft_test|route_window_parity|kv_stream_parity|native_grouped_parity)$']
with Heartbeat('targeted native tests',2),(C/'tests/native-attempt1.log').open('x') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
save(C/'tests/native-outcome.json',{'exit_code':r.returncode});assert r.returncode==0;no_gpu()
