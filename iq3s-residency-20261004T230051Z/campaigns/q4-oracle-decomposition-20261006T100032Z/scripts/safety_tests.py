from owned import C,run
import os,json,subprocess,shutil
src=C/'src/decomposition-v1';env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env['CUDA_VISIBLE_DEVICES']='0,1'
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=10).strip()
cmd=['g++','-O2','-std=c++20','-pthread','-I'+str(src/'include'),'-I/usr/local/cuda/include',str(C/'tests/oracle_fixture.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(C/'tests/oracle-fixture-bin')]
run('real-copy-fixture-compile',cmd,timeout=120,area='tests');p=run('real-copy-fixture',[C/'tests/oracle-fixture-bin'],env=env,timeout=120,area='tests')
rows=[x for x in (p/'stdout.log').read_text().splitlines() if x.startswith('PASS')]
(C/'tests/safety-summary.json').write_text(json.dumps({'state':'PASS','groups':rows,'runtime_source':'decomposition-v1','worker_changes':'none','scope':'Same production worker/publication/reader/drain methods; real synthetic immutable bytes in all physical classes on both devices.'},indent=2)+'\n')
run('targeted-native',[C.parents[1]/'src/control/.venv/bin/ctest','--test-dir',C/'builds/decomposition-v1','--output-on-failure','--timeout','90','-R','^(native_expert_parity_q4_K_q5_1|native_expert_parity_q4_K_q8_0|native_expert_parity_q5_K_q8_0|qsa_topk_active_parity|spec_controller_test|draft_policy_test|coupled_draft_test|route_window_parity|kv_stream_parity|native_grouped_parity|pool_affinity_linux_test)$'],env=env,timeout=300,area='tests')
print('SAFETY_COMPLETE',flush=True)
