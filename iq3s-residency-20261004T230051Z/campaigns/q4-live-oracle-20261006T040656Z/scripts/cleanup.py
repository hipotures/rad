"""Stop only explicitly recorded attempt-owned identities; safe if PIDs have been reused."""
from pathlib import Path
import json,os,signal,time,psutil,argparse
C=Path(__file__).resolve().parents[1]
def stop_record(path,group=False):
 if not path.exists():return {'record':str(path),'state':'NO_RECORD'}
 r=json.loads(path.read_text())
 try:
  p=psutil.Process(r['pid'])
  if abs(p.create_time()-r.get('create_time',r.get('created',0)))>.1:return {'record':str(path),'state':'PID_REUSED_REFUSED'}
  if p.status()==psutil.STATUS_ZOMBIE:return {'record':str(path),'state':'EXITED_ZOMBIE'}
  if group:
   assert os.getpgid(p.pid)==p.pid,'Refuse unrelated process group';os.killpg(p.pid,signal.SIGTERM)
  else:p.terminate()
  try:p.wait(timeout=20)
  except psutil.TimeoutExpired:
   if group:os.killpg(p.pid,signal.SIGKILL)
   else:p.kill()
   p.wait(timeout=10)
  return {'record':str(path),'state':'STOPPED_OWNED','pid':r['pid']}
 except psutil.NoSuchProcess:return {'record':str(path),'state':'ALREADY_EXITED'}
def cleanup_attempt(path):
 path=Path(path).resolve();assert path.is_relative_to(C/'raw'),'Attempt must belong to this campaign';out=[]
 out.append(stop_record(path/'process.json',True));out.append(stop_record(path/'raw/native-process.json'));out.append(stop_record(path/'collector-process.json'))
 (path/'cleanup-audit.json').write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('attempt');v=a.parse_args();print(json.dumps(cleanup_attempt(C/'raw'/v.attempt),indent=2))
