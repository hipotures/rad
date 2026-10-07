"""Finite owned subprocess, visible progress, retained exit status, no pipelines."""
from pathlib import Path
import subprocess,time,json,os,signal,psutil
C=Path(__file__).resolve().parents[1]
def run(label,cmd,cwd=None,env=None,timeout=300,area='logs'):
 pth=C/area/label;pth.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 with (pth/'stdout.log').open('x') as out,(pth/'stderr.log').open('x') as err:
  p=subprocess.Popen(list(map(str,cmd)),cwd=cwd,env=env,stdout=out,stderr=err,start_new_session=True)
  rec={'command':list(map(str,cmd)),'cwd':str(cwd),'pid':p.pid,'create_time':psutil.Process(p.pid).create_time(),'timeout_s':timeout}
  (pth/'process.json').write_text(json.dumps(rec,indent=2)+'\n');mark=start
  try:
   while p.poll() is None:
    if time.monotonic()-start>timeout:raise TimeoutError(label)
    if time.monotonic()-mark>=20:print('PROGRESS',label,round(time.monotonic()-start,1),flush=True);mark=time.monotonic()
    time.sleep(.5)
  finally:
   if p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10)
   rec.update(exit_code=p.returncode,wall_s=time.monotonic()-start);(pth/'result.json').write_text(json.dumps(rec,indent=2)+'\n')
 print('EXIT',label,p.returncode,round(rec['wall_s'],2),flush=True)
 if p.returncode:raise RuntimeError(label+' failed: '+(pth/'stderr.log').read_text()[-4000:])
 return pth
