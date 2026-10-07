from pathlib import Path
import subprocess,json,time
C=Path(__file__).resolve().parents[1];out=C/'tests/attention-v2';out.mkdir(exist_ok=False);s=C/'src/oracle-v2';b=C/'builds/oracle-v2'
cmd=['g++','-O2','-std=c++20','-I'+str(s/'include'),'-I/usr/local/cuda/include',str(C/'tests/attention_fixture.cpp'),str(b/'libstrata_kernels.a'),str(b/'libstrata_core.a'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-ldl','-lpthread','-o',str(out/'fixture')]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);(out/'compile.json').write_text(json.dumps({'command':cmd,'exit_code':r.returncode,'stderr':r.stderr},indent=2)+'\n');assert r.returncode==0,r.stderr
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip()
start=time.monotonic();r=subprocess.run([str(out/'fixture')],capture_output=True,text=True,timeout=60);(out/'result.json').write_text(json.dumps({'exit_code':r.returncode,'wall_s':time.monotonic()-start,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');print(r.stdout+r.stderr,flush=True);assert r.returncode==0
