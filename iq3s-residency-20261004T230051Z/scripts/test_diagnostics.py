"""Bounded diagnostic tests; failures retained and reviewed before inference."""
import json,pathlib,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1];SRC=ROOT/'src/diagnostic-v5';BUILD=ROOT/'builds/diagnostic-v5';OUT=ROOT/'experiments/E003-diagnostics/v5/tests';OUT.mkdir(parents=True,exist_ok=True)
commands=[]
def call(name,cmd,timeout=900):
 p=OUT/f'{name}.log';start=time.time()
 with p.open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 rec={'name':name,'command':cmd,'returncode':r.returncode,'wall_s':time.time()-start,'log':str(p)};commands.append(rec)
 (OUT/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 print(name,r.returncode,p.read_text()[-1800:],flush=True);return r.returncode
if call('trace-test-build',['c++','-std=c++20','-O2','-I'+str(SRC/'include'),str(ROOT/'scripts/trace_test.cpp'),'-o',str(OUT/'trace-test')]):raise SystemExit('Trace test compile failed')
if call('trace-test',[str(OUT/'trace-test'),str(OUT/'trace')]):raise SystemExit('Trace schema test failed')
call('native-tests',[str(ROOT/'src/control/.venv/bin/ctest'),'--test-dir',str(BUILD),'--output-on-failure','--timeout','60','-j','1'])
call('iq3s-real-expert-parity',[str(BUILD/'native_expert_parity'),'/srv/ai/models/strata/models/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf','0','1','2','12'],timeout=300)
