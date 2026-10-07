from pathlib import Path
import os,json,subprocess
from owned import C,run
src=C/'src/decomposition-v2';env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(CUDA_VISIBLE_DEVICES='0,1')
def compile_case(name,file):
 cmd=['g++','-O3','-std=c++20','-pthread','-I'+str(src/'include'),'-I/usr/local/cuda/include',str(file),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(C/'tests'/name)]
 run(name+'-compile',cmd,timeout=120,area='tests');return C/'tests'/name
env.update(STRATA_Q4_TAPE=str(C/'tapes/capture-32k-v3.bin'),STRATA_Q4_TAPE_MODE='replay')
fixture=compile_case('information-v2-bin',C/'tests/information_fixture.cpp');run('information-v2-run',[fixture],env=env,timeout=120,area='tests')
offline=compile_case('offline-v2-bin',C/'scripts/offline.cpp');env.update(STRATA_Q4_ORACLE_INCOMING='64',STRATA_Q4_ORACLE_VICTIM='64',STRATA_Q4_ORACLE_UNKNOWN='ema-tail')
p=run('offline-repair-I64-V64',[offline,'transfer','0','0'],env=env,timeout=180,area='phase-b');row=json.loads((p/'stdout.log').read_text());row.update(I='64',V='64',unknown_fallback='ema-tail',scope='One predeclared causal censoring repair, not a new horizon search',measured_model_TG=None)
(C/'phase-b/offline-repair.json').write_text(json.dumps(row,indent=2)+'\n');print('REPAIR_OFFLINE',json.dumps(row),flush=True)
# A bounded V with real publication exercises causal fallback and unchanged safety methods.
env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(CUDA_VISIBLE_DEVICES='0,1',STRATA_Q4_ORACLE_INCOMING='64',STRATA_Q4_ORACLE_VICTIM='64',STRATA_Q4_ORACLE_UNKNOWN='ema-tail')
fixture=compile_case('safety-v2-bin',C/'tests/oracle_fixture.cpp');assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True,timeout=10).strip();run('safety-v2-run',[fixture],env=env,timeout=120,area='tests')
print('V2_CHECKS_COMPLETE',flush=True)
