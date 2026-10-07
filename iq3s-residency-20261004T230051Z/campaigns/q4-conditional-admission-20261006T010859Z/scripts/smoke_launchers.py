"""Validate every advertised launcher after experiments, with bounded cleanup."""
from campaign import C,save,guard
from pathlib import Path
import subprocess,os,psutil,time,signal
def main():
 guard();save(C/'logs/launcher-smokes-driver-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'timeout_s':1800});runs=[]
 for variant in ('control','conditional'):
  for profile in ('32k','128k','256k'):
   command=[str(C/'launchers'/variant/f'start-{profile}.sh'),'--host','0.0.0.0','--port','18144','--smoke'];log=C/'logs'/f'launcher-smoke-{variant}-{profile}.log';assert not log.exists()
   with log.open('x') as f:
    p=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);save(C/'logs'/f'launcher-smoke-{variant}-{profile}-pid.json',{'pid':p.pid,'create_time':psutil.Process(p.pid).create_time(),'command':command,'timeout_s':300});start=time.time()
    try:
     while p.poll() is None:
      if time.time()-start>300:raise TimeoutError('Advertised launcher300s')
      print('LAUNCHER_SMOKE_PROGRESS',variant,profile,p.pid,round(time.time()-start,1),flush=True);time.sleep(15)
    finally:
     if p.poll() is None:
      subprocess.run([str(C/'launchers'/variant/'stop.sh')],timeout=20,capture_output=True);os.killpg(p.pid,signal.SIGTERM)
      try:p.wait(timeout=15)
      except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   assert p.returncode==0,(command,p.returncode,str(log));runs.append({'variant':variant,'profile':profile,'command':command,'log':str(log),'wall_s':time.time()-start,'PASS':True});save(C/'analysis/launcher-smokes.json',runs)
if __name__=='__main__':main()
