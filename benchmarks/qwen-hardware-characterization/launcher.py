#!/usr/bin/env python3
"""One-command preparation/core/follow-up/report flow, with signal-safe child forwarding."""
import argparse,datetime,json,os,pathlib,signal,subprocess,sys
root=pathlib.Path(os.environ.get('BENCH_ROOT','/srv/ai/benchmarks/qwen-hardware-characterization')).resolve();child=None;stop=False

def signal_handler(sig,frame):
 global stop
 stop=True
 if child and child.poll() is None:child.send_signal(signal.SIGTERM)
signal.signal(signal.SIGINT,signal_handler);signal.signal(signal.SIGTERM,signal_handler)
ap=argparse.ArgumentParser();ap.add_argument('--resume',type=pathlib.Path);ap.add_argument('--only');ap.add_argument('--initialize-only',action='store_true');a=ap.parse_args()
if a.resume:run=a.resume.resolve()
else:
 initlog=root/('initialization-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.log');run=None
 with open(initlog,'w') as log:
  child=subprocess.Popen([sys.executable,str(root/'campaign.py'),'--initialize-only'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  for line in child.stdout:
   print(line,end='',flush=True);log.write(line);log.flush()
   if line.startswith('RUN_DIRECTORY='):run=pathlib.Path(line.strip().split('=',1)[1])
  rc=child.wait()
 if stop:sys.exit(130)
 if rc or run is None:sys.exit(rc or 1)
if a.initialize_only:print('RUN_DIRECTORY='+str(run));sys.exit(0)
cmd=[sys.executable,str(root/'campaign.py'),'--resume',str(run)]+(['--only',a.only] if a.only else [])
child=subprocess.Popen(cmd);core_pid=child.pid
auditlog=(run/'raw'/('direct-auditor-launcher-'+str(core_pid)+'.log')).open('x')
auditor=subprocess.Popen([sys.executable,str(root/'direct_audit.py'),str(run),str(core_pid)],stdout=auditlog,stderr=subprocess.STDOUT)
try:rc=child.wait()
finally:
 if auditor.poll() is None:
  auditor.terminate()
  try:auditor.wait(timeout=5)
  except subprocess.TimeoutExpired:auditor.kill();auditor.wait()
 auditlog.close()
if stop:sys.exit(130)
if rc:sys.exit(rc)
if not a.only:
 child=subprocess.Popen([sys.executable,str(root/'followup.py'),str(run),str(core_pid)]);rc=child.wait()
 if stop:sys.exit(130)
 if rc:sys.exit(rc)
for script in ['analyze.py','normalize.py','report-final.py']+([] if a.only else ['final-audit.py']):
 child=subprocess.Popen([sys.executable,str(root/script),str(run)]);rc=child.wait()
 if stop:sys.exit(130)
 if rc:sys.exit(rc)
print('Artifacts: '+str(run/'report.md'),flush=True)
