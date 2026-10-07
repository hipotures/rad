"""Compile and run production scheduler methods with real CUDA copies, finite timeout."""
from pathlib import Path
import subprocess,time,json,os,psutil,signal
C=Path(__file__).resolve().parents[1];out=C/'tests/oracle-fixture';out.mkdir(exist_ok=False)
cmd=['g++','-O2','-std=c++20','-pthread','-I'+str(C/'src/oracle-v1/include'),'-I/usr/local/cuda/include',str(C/'tests/oracle_fixture.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-o',str(out/'fixture')]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);(out/'compile.json').write_text(json.dumps({'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');assert r.returncode==0,r.stderr
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'Conflicting GPU test/inference'
env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env['CUDA_VISIBLE_DEVICES']='0,1';start=time.monotonic()
with (out/'output.log').open('x') as f:
 p=subprocess.Popen([str(out/'fixture')],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);(out/'owned-process.json').write_text(json.dumps({'pid':p.pid,'create_time':psutil.Process(p.pid).create_time(),'timeout_s':120,'command':[str(out/'fixture')]},indent=2)+'\n')
 try:rc=p.wait(timeout=120)
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGTERM);rc=p.wait(timeout=10)
text=(out/'output.log').read_text();(out/'result.json').write_text(json.dumps({'exit_code':rc,'wall_s':time.monotonic()-start,'passes':[x for x in text.splitlines() if x.startswith('PASS ')],'scope':'Real Q4Oracle worker/publication methods with canonical immutable synthetic byte backing in all real Q4 classes; no quantized model-quality claim'},indent=2)+'\n');print(text,flush=True);assert rc==0
