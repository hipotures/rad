"""Bounded Phase0 capture only: frozen identities, one natural request, owned cleanup."""
import argparse,copy,datetime,hashlib,json,os,pathlib,re,signal,socket,statistics,subprocess,sys,threading,time,urllib.request
import psutil,shutil
C=pathlib.Path(__file__).resolve().parents[1];R=pathlib.Path('/srv/ai/research/iq3s-residency-20261004T230051Z');P=R/'campaigns/q4-live-oracle-20261006T040656Z'
sys.path.append(str(P/'scripts'))
import lab
from q4_multigpu import Q4Session
from progress import update

def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,x):p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def hj(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def gpu_idle():
 q=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True,capture_output=True,check=True,timeout=8)
 assert not q.stdout.strip(),('GPU_CONFLICT',q.stdout)
def stop_owned(pid,created):
 try:
  p=psutil.Process(pid);assert abs(p.create_time()-created)<.1,'PID reuse; refuse stop';children=p.children(recursive=True)
  p.send_signal(signal.SIGTERM)
  try:p.wait(timeout=10)
  except psutil.TimeoutExpired:
   os.killpg(pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except psutil.TimeoutExpired:os.killpg(pid,signal.SIGKILL);p.wait(timeout=5)
  for child in children:
   try:
    if child.is_running() and child.status()!=psutil.STATUS_ZOMBIE:
     child.terminate()
     try:child.wait(timeout=3)
     except psutil.TimeoutExpired:child.kill();child.wait(timeout=3)
   except psutil.NoSuchProcess:pass
 except psutil.NoSuchProcess:pass
lab.owned_stop=stop_owned
activity={'phase':'idle','session':None,'task':None,'started':None,'first':None,'outputs':0,'request_state':'NONE'}
heartbeat_stop=threading.Event()
def heartbeat():
 while not heartbeat_stop.wait(20):
  s=activity['session'];pid=s.proc.pid if s and s.proc else None
  live=(lab.api(s.url,'/metrics') or {}).get('live',{}) if s and s.proc else {}
  update(4,f"HEARTBEAT {activity['task']} | {activity['phase']} | client chunks {activity['outputs']} | native state {live.get('state','unknown')} | next complete current episode",owned_pid=pid,request_state=activity['request_state'],live=live,swap_bytes=psutil.swap_memory().used)
def alarm(*_):raise TimeoutError('DECLARED_HARD_DEADLINE')
signal.signal(signal.SIGALRM,alarm)
signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Owned runner interrupted')))
def verify(cfg):
 assert sha(cfg['exe'])==cfg['binary_sha256'],'Capture binary mismatch; no fallback'
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['cwd'],text=True).strip()==cfg['source_sha']
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=cfg['cwd'],text=True).strip()
 m=load(C/'provenance/model-identity.json')
 for p,v in m['files'].items():
  st=pathlib.Path(p).stat();assert (st.st_size,st.st_mtime_ns,st.st_ino)==(v['size'],v['mtime_ns'],v['inode']),p
 assert cfg['model_revision']=='38bb39ee97821de2c9009abb7e93950eec396e66'
 assert cfg['env']['STRATA_POOL_SPIN_US']=='100' and cfg['layer_split']=='24'
 gpu_idle()
def request(s,name,label,soft=None,hard=240):
 info=load(C/'corpus/payload-manifest.json')['payloads'][name];payload=load(info['path']);assert hj(payload)==info['payload_sha256'];assert info['actual_input_tokens']+payload['max_tokens']+8<=s.cfg['max_total_context']
 raw=s.path/'raw';save(raw/(label+'-request.json'),payload);s.capture_requests+=1
 offset=(s.path/'logs/engine.log').stat().st_size;begin=time.monotonic();first=None;usage={};text=[];events=[];finish=None;planned=False
 activity.update(phase='prefill',started=begin,first=None,outputs=0,request_state='PREFILL')
 req=urllib.request.Request(s.url+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
 signal.setitimer(signal.ITIMER_REAL,hard)
 try:
  with lab.Sampler(s,s.path/'telemetry'/(label+'.jsonl')) as sampler:
   with urllib.request.urlopen(req,timeout=hard) as response:
    for line in response:
     if not line.startswith(b'data:'):continue
     data=line[5:].strip()
     if data==b'[DONE]':break
     chunk=json.loads(data);now=time.monotonic();events.append({'elapsed_s':now-begin,'chunk':chunk})
     if chunk.get('usage'):usage=chunk['usage']
     for ch in chunk.get('choices',[]):
      delta=ch.get('delta') or {};piece=delta.get('content') or delta.get('reasoning_content') or ''
      if piece and first is None:first=now;activity.update(first=first,phase='decode',request_state='DECODE')
      if piece:text.append(piece);activity['outputs']+=1 # chunks, not token count
      if ch.get('finish_reason'):finish=ch['finish_reason']
     if soft and first and now-first>=soft:
      planned=True;response.fp.raw._sock.shutdown(socket.SHUT_RDWR);break
   end=time.monotonic()
  signal.setitimer(signal.ITIMER_REAL,0)
  status=lab.api(s.url,'/v1/status') or {};metrics=lab.api(s.url,'/metrics') or {};timings=status.get('last_timings') or {}
  log=(s.path/'logs/engine.log').read_bytes()[offset:].decode(errors='replace');(raw/(label+'-engine.log')).write_text(log)
  op=raw/f'output-ids-request{s.capture_requests}.json';ip=raw/f'output-ids-input-request{s.capture_requests}.json'
  IDs=load(op) if op.exists() else None;inputproof=load(ip) if ip.exists() else None
  if not planned:assert inputproof and inputproof['sha256']==info['input_ids_sha256'],'Actual rendered input hash mismatch';assert usage.get('prompt_tokens')==info['actual_input_tokens'],'Input count mismatch'
  cache=re.search(r'expert cache hit rate: ([\d.]+)% \((\d+) hits / (\d+) lookups\)',log);off=re.search(r'; (\d+) more read by the GPU over PCIe or from another GPU.*?all (\d+) routed',log);rounds=re.search(r'strata decode timing: (\d+) windows',log)
  local=int(cache[2]) if cache else None;cpu=int(cache[3])-local if cache else None;mapped=int(off[1]) if off else 0 if cache else None;allentries=int(off[2]) if off else local+cpu if cache else None
  reason='PLANNED_TIME_SLICE' if planned else 'OUTPUT_CAP' if finish=='length' else 'NATURAL_EOS' if finish=='stop' else 'ERROR'
  result={'task':name,'state':'COMPLETED' if reason!='ERROR' else 'ERROR','stop_reason':reason,'engine_finish_reason':finish,'payload':info,'request_wall_s':end-begin,'TTFT_s':(first or end)-begin,'prefill_s':timings.get('prompt_ms',0)/1000,'decode_s':timings.get('predicted_ms',0)/1000,'PP':timings.get('prompt_per_second'),'TG':timings.get('predicted_per_second'),'actual_input_tokens':usage.get('prompt_tokens'),'output_tokens':usage.get('completion_tokens'),'captured_output_ID_count':len(IDs) if IDs is not None else None,'output_ids_path':str(op) if IDs is not None else None,'output_ids_sha256':sha(op) if IDs is not None else None,'actual_engine_input':inputproof,'verify_windows':int(rounds[1]) if rounds else None,'local_entries':local,'cpu_entries':cpu,'mapped_entries':mapped,'all_entries':allentries,'MTP_proposed':timings.get('draft_n'),'MTP_accepted':timings.get('draft_n_accepted'),'reused_tokens':timings.get('cache_n'),'timings':timings,'telemetry':sampler.summary(),'begin_monotonic':begin,'first_monotonic':first,'end_monotonic':end,'instrumented':True,'text_path':str(raw/(label+'-response.txt')),'trace_drain_s':max(0,time.monotonic()-end),'logical_stop_boundary':'Complete verifier windows in tape if validated; cancellation tape may be invalid','short_output':usage.get('completion_tokens',0)<256}
  save(raw/(label+'-status.json'),status);save(raw/(label+'-metrics.json'),metrics);save(raw/(label+'-stream.json'),events);(raw/(label+'-response.txt')).write_text(''.join(text));save(raw/(label+'.json'),result)
  if not planned:assert IDs is not None and len(IDs)==result['output_tokens'];assert result['reused_tokens']==0
  assert result['output_tokens'] is None or result['output_tokens']<=payload['max_tokens']
  return result
 finally:signal.setitimer(signal.ITIMER_REAL,0)
def run_task(task,pos,total,reproduction=False):
 timing=load(C/'timing.json');now=time.monotonic();assert reproduction or now+445<timing['request_cutoff_monotonic'],'Cannot finish likely operation and cleanup before T+50; defer'
 cfg=copy.deepcopy(load(C/'configs.json')[task['profile']]);verify(cfg);p=C/'raw'/task['task_id'];assert not p.exists(),'Immutable attempt exists; no retry'
 tape=p/'tape.bin';cfg['env'].update(STRATA_Q4_TAPE=str(tape),STRATA_Q4_TAPE_MODE='record',STRATA_Q4_TAPE_REQUEST='2',STRATA_Q4_TAPE_OBSERVATIONS=str(p/'raw/observations.bin'),STRATA_Q4_ORACLE_SUBSTRATE='1',STRATA_Q4_ORACLE_MODE='off',STRATA_Q4_ORACLE_LOG=str(p/'raw/native'))
 print(f"[PHASE 0 | STEP 4/5 | EPISODE {pos}/{total} START] {task['task_id']} | profile {task['profile']} | request cap240s",flush=True)
 update(4,'Start '+task['task_id'],completed=pos-1,remaining_work=total-pos+1,next_action='fresh start,warmup,one natural capture',request_state='STARTUP')
 start=time.monotonic();s=Q4Session(C,cfg,p,task['profile'],port=18158);activity.update(task=task['task_id'],session=s,phase='startup',request_state='STARTUP',outputs=0,first=None);result={}
 try:
  signal.setitimer(signal.ITIMER_REAL,180)
  s.__enter__();startup=load(p/'raw/startup.json')['cold_start_s']
  native=[q for q in psutil.Process(s.proc.pid).children(recursive=True) if pathlib.Path(q.exe()).resolve()==pathlib.Path(cfg['exe']).resolve()];assert len(native)==1
  env={k:v for k,v in native[0].environ().items() if k.startswith('STRATA_') or k=='CUDA_VISIBLE_DEVICES'};assert env['STRATA_POOL_SPIN_US']=='100' and env['STRATA_Q4_TAPE_MODE']=='record' and env['STRATA_Q4_ORACLE_MODE']=='off';assert not any(k in env for k in ['STRATA_Q4_EARLY','STRATA_Q4_ORACLE_DIRECT'])
  save(p/'raw/native-process.json',{'pid':native[0].pid,'created':native[0].create_time(),'executable':native[0].exe(),'command':native[0].cmdline(),'environment':env,'affinity':native[0].cpu_affinity()})
  # Remaining combined startup+warmup cap, not a reset to180.
  remaining=180-(time.monotonic()-start);assert remaining>0
  warm=request(s,'warmup','warmup',hard=remaining);assert warm['output_tokens']==64
  signal.setitimer(signal.ITIMER_REAL,0);r=request(s,task['task_id'],'run',soft=60,hard=240)
  result={'task_id':task['task_id'],'family':task['family'],'profile':task['profile'],'startup_s':startup,'warmup_s':warm['request_wall_s'],'startup_and_warmup_s':time.monotonic()-start-r['request_wall_s']-r['trace_drain_s'],'run':r,'trace_type':'FULL_REPLAY_TAPE' if tape.exists() and 'Q4_TAPE_END mode=record' in (p/'logs/engine.log').read_text() else 'INVALID_TRACE','capture_tape':str(tape),'warmup':warm}
 except BaseException as e:
  result={'task_id':task['task_id'],'family':task['family'],'profile':task['profile'],'state':'ERROR','error':repr(e),'stop_reason':'HARD_TIMEOUT' if isinstance(e,TimeoutError) else 'ERROR','trace_type':'INVALID_TRACE'}
  print('[PHASE 0 | STEP 4/5 BLOCKED]',task['task_id'],repr(e),'preserving attempt and stopping owned processes',flush=True)
 finally:
  signal.setitimer(signal.ITIMER_REAL,0);activity.update(phase='shutdown',request_state='DRAIN_AND_SHUTDOWN');endrun=time.monotonic();s.__exit__();gpu_idle();result.update(shutdown_s=time.monotonic()-endrun,total_operating_s=time.monotonic()-start,cleanup_verified=True,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save(p/'episode.json',result);activity.update(session=None,phase='idle',request_state='NONE');update(4,'Finished '+task['task_id'],owned_pid=None,request_state='NONE',completed=pos,remaining_work=total-pos,next_action='validate flushed trace then next frozen task')
 print(f"[PHASE 0 | STEP 4/5 | EPISODE {pos}/{total} DONE] {task['task_id']} | operating {result['total_operating_s']:.1f}s | {result.get('run',{}).get('stop_reason',result.get('stop_reason'))} | output {result.get('run',{}).get('output_tokens')} | {result['trace_type']} | remaining {total-pos}",flush=True)
 return result

def main():
 global C
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['check','task','core','screening','stop']);a.add_argument('--task');a.add_argument('--reproduction',action='store_true');a.add_argument('--output-dir');v=a.parse_args();manifest=load(C/'benchmark-manifest.json')
 if v.mode=='stop':
  if (C/'owned-process.json').exists():p=load(C/'owned-process.json');stop_owned(p['pid'],p['create_time'])
  gpu_idle();print('OWNED CLEANUP VERIFIED');return
 if v.mode=='check':
  for cfg in load(C/'configs.json').values():verify(cfg)
  for t in manifest['tasks']:assert hj(load(t['payload']['path']))==t['payload']['payload_sha256']
  print('IDENTITY AND PAYLOAD CHECK PASS');return
 if v.reproduction:
  origin=C;dest=pathlib.Path(v.output_dir).resolve() if v.output_dir else origin/'replays'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');assert not dest.exists(),'Reproduction directory exists; preserve it'
  dest.mkdir(parents=True)
  for d in ['scripts','analysis','provenance','corpus','raw']:(dest/d).mkdir()
  for name in ['benchmark-manifest.json','configs.json','GOAL.md','DECISIONS.md']:shutil.copyfile(origin/name,dest/name)
  shutil.copyfile(origin/'corpus/payload-manifest.json',dest/'corpus/payload-manifest.json');shutil.copyfile(origin/'provenance/model-identity.json',dest/'provenance/model-identity.json')
  for name in ['run.py','progress.py','validate_traces.py','legacy_tape.py','serve_capture.py']:shutil.copyfile(origin/'scripts'/name,dest/'scripts'/name)
  shutil.copyfile(origin/'analysis/libfnv64.so',dest/'analysis/libfnv64.so');now=time.monotonic();wall=datetime.datetime.now(datetime.timezone.utc)
  save(dest/'timing.json',{'start_utc':wall.isoformat(),'start_monotonic':now,'deadline_monotonic':now+3600,'deadline_utc':(wall+datetime.timedelta(seconds=3600)).isoformat(),'request_cutoff_monotonic':now+3000,'request_cutoff_utc':(wall+datetime.timedelta(seconds=3000)).isoformat(),'reproduction_of':str(origin)})
  C=dest;import progress as progress_module;progress_module.C=dest
  print('REPRODUCTION DIRECTORY',dest,flush=True)
 elif v.output_dir:raise ValueError('--output-dir requires explicit --reproduction')
 tasks=[t for t in manifest['tasks'] if (v.mode=='task' and t['task_id']==v.task) or v.mode=='core' or (v.mode=='screening' and t['screening'])];assert tasks
 ledger=C/'attempt-ledger.jsonl';spent={};observed=[]
 if ledger.exists():
  for line in ledger.read_text().splitlines():q=json.loads(line);spent[q['family']]=spent.get(q['family'],0)+q['total_operating_s'];observed.append(q['total_operating_s'])
 th=threading.Thread(target=heartbeat,daemon=True);th.start()
 try:
  for i,t in enumerate(tasks,1):
   if (C/'raw'/t['task_id']/'episode.json').exists():continue
   projected=min(445,max(observed)+60) if observed else 445
   if spent.get(t['family'],0)+projected>600:print('DEFER FAMILY BUDGET',t['task_id'],spent.get(t['family'],0),flush=True);continue
   if time.monotonic()+445>=load(C/'timing.json')['request_cutoff_monotonic']:print('DEFER REQUEST CUTOFF',t['task_id'],flush=True);continue
   if sum(p.stat().st_size for p in (C/'raw').rglob('*') if p.is_file())>11*1024**3:print('DEFER TRACE STORAGE',t['task_id'],flush=True);continue
   r=run_task(t,i,len(tasks));observed.append(r['total_operating_s']);spent[t['family']]=spent.get(t['family'],0)+r['total_operating_s']
   with ledger.open('a') as f:f.write(json.dumps(r)+'\n')
   # No analysis while inference runs; structural validation happens after shutdown.
   if r['trace_type']=='FULL_REPLAY_TAPE':subprocess.run([sys.executable,str(C/'scripts/validate_traces.py'),str(C/'raw'/t['task_id'])],check=True,timeout=90)
 finally:heartbeat_stop.set();th.join(timeout=3)
if __name__=='__main__':main()
