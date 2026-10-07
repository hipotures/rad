"""Bound one owned process group, record exact command/environment and retain logs."""
import argparse,json,os,pathlib,signal,subprocess,time
import psutil
from lab import ROOT,save,deadline
ap=argparse.ArgumentParser();ap.add_argument('--path',required=True);ap.add_argument('--timeout',type=int,default=600);ap.add_argument('--completion-reserve',type=int,default=2700,help='Reserve 1800–2700 seconds for consolidation; does not permit new inference sessions after the original session gate');ap.add_argument('command',nargs=argparse.REMAINDER);a=ap.parse_args()
path=pathlib.Path(a.path);path.mkdir(parents=True,exist_ok=True)
if (path/'command.json').exists():raise RuntimeError('Command attempt exists; refuse overwrite')
command=a.command[1:] if a.command[:1]==['--'] else a.command
if not 1800<=a.completion_reserve<=2700:raise RuntimeError('Consolidation reserve must be 30–45 minutes')
limit=min(a.timeout,max(1,int(deadline()-time.time()-a.completion_reserve)));record={'command':command,'cwd':str(ROOT),'timeout_s':limit,'started_epoch':time.time(),'consolidation_reserve_s':a.completion_reserve,'environment':{k:os.environ.get(k) for k in ['CUDA_VISIBLE_DEVICES','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']}}
save(path/'command.json',record)
with (path/'output.log').open('w') as stream:
 proc=subprocess.Popen(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True);record['pid']=proc.pid;record['create_time']=psutil.Process(proc.pid).create_time();save(path/'command.json',record)
 try:rc=proc.wait(timeout=limit)
 except subprocess.TimeoutExpired:
  record['timeout']=True
  # Session servers deliberately have their own process group. Snapshot owned
  # descendants before ending the wrapper so they cannot become untracked.
  children=[]
  try:
   for child in psutil.Process(proc.pid).children(recursive=True):
    try:children.append({'pid':child.pid,'create_time':child.create_time(),'process_group':os.getpgid(child.pid)})
    except (psutil.Error,ProcessLookupError):pass
  except psutil.Error:pass
  record['timeout_owned_descendants']=children;save(path/'command.json',record)
  for child in reversed(children):
   try:
    current=psutil.Process(child['pid'])
    if abs(current.create_time()-child['create_time'])>.1:continue
    if child['process_group']==child['pid']:os.killpg(child['pid'],signal.SIGTERM)
    else:current.terminate()
   except (psutil.Error,ProcessLookupError):pass
  os.killpg(proc.pid,signal.SIGTERM)
  try:rc=proc.wait(timeout=15)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);rc=proc.wait()
  for child in reversed(children):
   try:
    current=psutil.Process(child['pid'])
    if abs(current.create_time()-child['create_time'])<=.1 and current.is_running():current.kill()
   except psutil.Error:pass
record.update(returncode=rc,elapsed_s=time.time()-record['started_epoch']);save(path/'command.json',record)
print(json.dumps(record,indent=2));print((path/'output.log').read_text()[-6000:]);raise SystemExit(rc)
