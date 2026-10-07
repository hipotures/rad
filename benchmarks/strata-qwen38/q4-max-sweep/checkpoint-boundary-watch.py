from pathlib import Path
import os,signal,time,json,psutil
r=Path(__file__).resolve().parent
pid=177088
while True:
 try:
  proc=psutil.Process(pid)
  if proc.status()==psutil.STATUS_ZOMBIE:state='TERMINAL';break
 except psutil.NoSuchProcess:state='MISSING';break
 if (r/'raw/AGENT-63400-done.json').exists():
  os.kill(pid,signal.SIGSTOP);state='CANDIDATE_COMPLETE_PROCESS_STOPPED_AT_BOUNDARY';break
 time.sleep(.02)
(r/'raw/v0131-safe-boundary.json').write_text(json.dumps({'status':state,'candidate':'AGENT-63400','pid':pid,'observed':time.time(),'parent_driver_stopped':177087},indent=2))
