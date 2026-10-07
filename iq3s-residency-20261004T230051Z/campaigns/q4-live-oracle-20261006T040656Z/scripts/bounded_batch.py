"""Serial immutable experiment plan. Finite owned subprocesses, heartbeat, audit between GPU jobs."""
from pathlib import Path
import json,time,subprocess,os,signal,psutil,sys
from runner import C,guard,save,status
from cleanup import cleanup_attempt
from fidelity import audit
from inspect_oracle import audit as oracle_audit
from progression import analyze
from system_metrics import analyze as system_analyze
from event_diagnostics import analyze as event_analyze
plan=Path(sys.argv[1]);jobs=json.loads(plan.read_text())['jobs'];PY=str(C.parents[1]/'src/control/.venv/bin/python');runs=[]
for job in jobs:
 guard();label=job['label'];assert not(C/'raw'/label).exists(),'Immutable attempt exists: '+label
 cmd=[PY,str(C/'scripts/runner.py'),*job['args']];start=time.monotonic();print('BATCH_START',label,flush=True)
 with (C/'logs'/f'{label}.log').open('x') as f:
  p=subprocess.Popen(cmd,cwd=C,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);save(C/'logs'/f'{label}-batch-pid.json',{'pid':p.pid,'create_time':psutil.Process(p.pid).create_time(),'command':cmd,'timeout':job.get('timeout_s',1200)});last=start
  try:
   while p.poll() is None:
    if time.monotonic()-start>job.get('timeout_s',1200):raise TimeoutError(label)
    if time.monotonic()-last>20:
     lines=(C/'logs'/f'{label}.log').read_text().splitlines();server=C/'raw'/label/'logs/server.log'
     if server.exists():
      native_lines=server.read_text().splitlines()
      if native_lines:lines=native_lines
     print('BATCH_PROGRESS',label,round(time.monotonic()-start),lines[-1][:350] if lines else '',flush=True);last=time.monotonic()
    time.sleep(1)
  finally:
   if p.poll() is None:
    os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=30)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10)
 cleanup_attempt(C/'raw'/label)
 rec={'label':label,'exit_code':p.returncode,'wall_s':time.monotonic()-start};runs.append(rec);save(plan.with_suffix('.completed.json'),runs);print('BATCH_EXIT',rec,flush=True)
 assert p.returncode==0,(label,p.returncode)
 if job.get('tape'):
  tape=C/job['tape'];v=audit(label,tape);assert v['state']=='PASS',v
  if (C/'raw'/label/'raw/oracle-layers.bin').exists():
   v=oracle_audit(label,tape);assert v['state']=='PASS',v
   event_analyze(label,tape)
  if len(v.get('tape',{})) or job.get('progression',True):analyze(label,tape)
  system_analyze(label,tape)
 status('BETWEEN_EXPERIMENTS',running=None,last_completed=label,next_exact_action='Next predeclared job or inspect completed plan; no concurrent requests')
print('BATCH_COMPLETE',str(plan),flush=True)
