"""Finite targeted initial-state contract fixture, only when GPUs are idle."""
from pathlib import Path
import subprocess,time,json,os,psutil,signal
C=Path(__file__).resolve().parents[1];dest=C/'tests/v3-state-fixture-v2';dest.mkdir(exist_ok=False)
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip(),'GPU conflict'
commands=[('compile',['g++','-O2','-std=c++17','-I'+str(C/'src/oracle-v3/include'),'-I/usr/local/cuda/include',str(C/'tests/state_fixture.cpp'),'-L/usr/local/cuda/lib64','-Wl,-rpath,/usr/local/cuda/lib64','-lcudart','-pthread','-o',str(dest/'fixture')],120),('run',[str(dest/'fixture'),str(dest/'data')],60)]
records=[];env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')}
for label,cmd,limit in commands:
 start=time.monotonic()
 with (dest/f'{label}.log').open('x') as f:
  p=subprocess.Popen(cmd,cwd=C,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);r={'command':cmd,'pid':p.pid,'create_time':psutil.Process(p.pid).create_time(),'timeout_s':limit};records.append(r)
  try:p.wait(timeout=limit)
  finally:
   if p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10)
  r.update(exit_code=p.returncode,wall_s=time.monotonic()-start);(dest/'commands.json').write_text(json.dumps(records,indent=2)+'\n');print('STATE_TEST',label,p.returncode,flush=True);assert p.returncode==0,(dest/f'{label}.log').read_text()
