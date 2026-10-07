"""Isolated exact retained replay; never updates source, rebuilds or changes ordinary launchers."""
import argparse,datetime,hashlib,os,pathlib,shutil,subprocess,sys,time,signal
from common import *
import live
if __name__=='__main__':
 q=argparse.ArgumentParser();q.add_argument('--task',default='math-rational');q.add_argument('--arm',choices=['REPLAY_CURRENT','ORACLE_FULL','ORACLE_IN_HISTORY_TC','ORACLE_IN_LOGISTIC_TC','LOGISTIC_OFF','HISTORY_OFF'],default='ORACLE_IN_HISTORY_TC');q.add_argument('--prepare-only',action='store_true');q.add_argument('--input-dir');args=q.parse_args();no_gpu();identity=live.identities();selection=load(C/'models/selection.json');assert selection['version']=='target-use-v1' and selection['threshold']==.5 and selection['post_use_events']==0 and selection['checkpoint_sha256']==identity['checkpoint_sha256']
 tasks={t['task_id']:t for t in load(P0/'benchmark-manifest.json')['tasks']};tasks['text-json-rfc8259']=load(C/'inputs/independent-task-manifest.json');assert args.task in tasks;task=tasks[args.task];tp=pathlib.Path(task['trace_path']);expected=task.get('tape_sha256',task.get('trace_hashes',{}).get(str(tp)));assert hashlib.file_digest(tp.open('rb'),'sha256').hexdigest()==expected
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');dest=W/'tmp'/('reproduction-'+stamp);dest.mkdir(parents=True,exist_ok=False)
 for name in ['code','models','configs','inputs']:
  shutil.copytree(C/name,dest/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (dest/'raw').mkdir();(dest/'analysis').mkdir();(dest/'results').mkdir();(dest/'references').mkdir()
 if args.input_dir:
  supplied=load(pathlib.Path(args.input_dir)/'manifest.json');fresh=supplied['payloads']['text-json-rfc8259'];original=load(C/'inputs/manifest.json')['payloads']['text-json-rfc8259']
  for key in ['payload_sha256','messages_sha256','input_ids_sha256','actual_input_tokens']:assert fresh[key]==original[key],('Frozen supplied input mismatch',key)
  assert hashlib.sha256(pathlib.Path(fresh['token_ids_path']).read_bytes()).hexdigest()==fresh['input_ids_sha256'];payload=load(fresh['path']);assert hashlib.sha256(__import__('json').dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()==fresh['payload_sha256'];manifest=load(dest/'inputs/manifest.json');manifest['payloads']['text-json-rfc8259']=fresh;save(dest/'inputs/manifest.json',manifest)
 clock=load(C/'clock.json');finished=(C/'completion-audit.json').exists() and load(C/'completion-audit.json').get('campaign_complete',False)
 if finished:
  now=datetime.datetime.now(datetime.timezone.utc);clock=dict(start_utc=now.isoformat(),deadline_utc=(now+datetime.timedelta(seconds=600)).isoformat(),start_monotonic_s=time.monotonic(),hard_budget_s=600,stop_substantial_utc=(now+datetime.timedelta(seconds=450)).isoformat(),scope='Separate explicitly invoked reproduction; original campaign clock untouched')
 elif time.monotonic()-clock['start_monotonic_s']>=310*60:raise RuntimeError('Original campaign reporting reserve; refuse new replay')
 save(dest/'clock.json',clock);save(dest/'progress.json',{'step':4,'status':'PREPARED'});(dest/'attempt-ledger.jsonl').touch()
 save(dest/'protocol.json',{'parent_campaign':str(C),'task':args.task,'arm':args.arm,'identity':identity,'tape_sha256':expected,'selection_sha256':hashlib.sha256((C/'models/selection.json').read_bytes()).hexdigest(),'output_namespace':str(dest),'no_update_no_build':True,'startup_warmup_cap_s':180,'request_cap_s':240,'complete_work_required':True})
 print('REPRODUCTION_DIRECTORY',dest,flush=True);ledger('Reproducer prepared',directory=str(dest),task=args.task,arm=args.arm,prepare_only=args.prepare_only)
 if args.prepare_only:sys.exit(0)
 # Run only in the isolated namespace; expose parent immutable inputs explicitly.
 env=os.environ.copy();env['RAD_INPUT_CAMPAIGNS']=str(INPUT_PARENT);env['RAD_WORK_ROOT']=str(W)
 cmd=[sys.executable,str(dest/'code/live.py'),'--task',args.task,'--arm',args.arm,'--label','replay-'+args.task+'-'+args.arm]
 # live CLI resolves existing corpus; independent CLI extension uses its own task manifest.
 with Heartbeat('isolated reproducer '+args.arm,5),(dest/'runner.log').open('x') as f:
  child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:exit_code=child.wait(timeout=440)
  except subprocess.TimeoutExpired:
   child.send_signal(signal.SIGTERM)
   try:child.wait(timeout=30)
   except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
   owned=dest/'owned-process.json'
   if owned.exists():record=load(owned);live.stop_owned(record['pid'],record['create_time'])
   exit_code=124
  r=type('Outcome',(),{'returncode':exit_code})()
 ledger('Reproducer finished',directory=str(dest),task=args.task,arm=args.arm,exit_code=r.returncode);save(C/'tests'/('reproduction-'+stamp+'.json'),{'directory':str(dest),'task':args.task,'arm':args.arm,'exit_code':r.returncode,'command':cmd,'parent_clock_unchanged':True});print('REPRODUCTION_EXIT',r.returncode,flush=True);sys.exit(r.returncode)
