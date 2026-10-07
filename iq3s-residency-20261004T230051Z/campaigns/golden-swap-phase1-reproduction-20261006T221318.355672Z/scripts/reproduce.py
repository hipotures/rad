"""Create an isolated reproduction; preserve the original campaign clock and artifacts."""
import argparse,shutil,datetime,subprocess,hashlib,psutil,os,signal
from common import *
q=argparse.ArgumentParser();q.add_argument('--prepare-only',action='store_true');q.add_argument('--task',default='code-archive',choices=['code-archive','math-inventory','text-websocket','mixed-chinook','math-rational','math-sensor','text-tls']);q.add_argument('--arm',default='REPLAY_CURRENT',choices=['REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_LEARNED_VICTIM']);q.add_argument('--output-dir');args=q.parse_args();no_gpu();clock=load(C/'clock.json');dest=pathlib.Path(args.output_dir).resolve() if args.output_dir else C.parents[1]/'campaigns'/('golden-swap-phase1-reproduction-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));assert dest.parent==C.parent,'Reproduction must be a sibling campaign directory to preserve authoritative research-root addressing';assert not dest.exists();dest.mkdir()
for d in ['scripts','data','models','results','logs','source','tests','analysis','builds','references','raw','phase-a','configs','inputs','patches']:(dest/d).mkdir()
for p in (C/'scripts').glob('*.py'):shutil.copyfile(p,dest/'scripts'/p.name)
for p in (C/'models').glob('*'):
 if p.is_file():shutil.copyfile(p,dest/'models'/p.name)
for relative in ['GOAL.md','source-group-splits.json','run-order.json','requirements.txt','builds/runtime-identity.json','inputs/manifest.json','analysis/libfnv64.so']:shutil.copyfile(C/relative,dest/relative)
for p in (C/'tests').glob('*.cpp'):shutil.copyfile(p,dest/'tests'/p.name)
if (C/'tests/legacy_oracle.hpp').exists():shutil.copyfile(C/'tests/legacy_oracle.hpp',dest/'tests/legacy_oracle.hpp')
(dest/'source/runtime').symlink_to(C/'source/runtime',target_is_directory=True);(dest/'.venv').symlink_to(C/'.venv',target_is_directory=True)
start=datetime.datetime.now(datetime.timezone.utc);s={'start_utc':start.isoformat(),'deadline_utc':(start+datetime.timedelta(minutes=20)).isoformat(),'measurement_cutoff_utc':(start+datetime.timedelta(minutes=15)).isoformat(),'start_monotonic':time.monotonic(),'campaign':str(dest),'step':3,'status':'REPRODUCTION','original_campaign':str(C),'original_deadline_preserved':clock['deadline_utc']};save(dest/'clock.json',s);save(dest/'progress.json',s);(dest/'progress.jsonl').write_text('');(dest/'DECISIONS.md').write_text('# Isolated reproduction\n');print('REPRODUCTION_DIRECTORY',dest,flush=True)
if not args.prepare_only:
 identity=load(dest/'builds/runtime-identity.json');assert hashlib.sha256(pathlib.Path(identity['exe']).read_bytes()).hexdigest()==identity['binary_sha256'];python=C.parents[1]/'src/control/.venv/bin/python'
 try:subprocess.run([str(python),str(dest/'scripts/live.py'),'point','--task',args.task,'--arm',args.arm,'--label','reproduction-'+args.task+'-'+args.arm],check=True,timeout=600)
 finally:
  # Outer timeout cleanup also verifies the recorded frontend identity; unrelated processes are never stopped.
  record_path=dest/'owned-process.json'
  if record_path.exists():
   record=load(record_path)
   try:
    owner=psutil.Process(record['pid']);assert abs(owner.create_time()-record['create_time'])<.1,'Reproduction PID reused; refuse stop';assert any(str(dest) in a for a in owner.cmdline()),'Owner command changed; refuse stop';children=[(q,q.create_time()) for q in owner.children(recursive=True)];owner.terminate()
    try:owner.wait(5)
    except psutil.TimeoutExpired:os.killpg(owner.pid,signal.SIGKILL);owner.wait(5)
    for child,created in children:
     try:
      if abs(child.create_time()-created)<.1 and child.is_running() and child.status()!=psutil.STATUS_ZOMBIE:
       child.terminate()
       try:child.wait(3)
       except psutil.TimeoutExpired:child.kill();child.wait(3)
     except psutil.NoSuchProcess:pass
   except psutil.NoSuchProcess:pass
  no_gpu()
