"""Small reproducible runner: frozen variants, serial requests, lightweight telemetry, owned cleanup."""
import argparse, copy, hashlib, json, os, pathlib, re, signal, socket, statistics, subprocess, sys, threading, time, urllib.request
import psutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
GIB=1024**3
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,obj):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n');tmp.replace(p)
def hashjson(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def deadline():
 # A later explicitly authorized campaign has its own immutable deadline.
 # Keep the original campaign deadline/evidence unchanged.
 p=ROOT/'active-campaign.json'
 if p.exists():return load(load(p)['deadline_path'])['deadline_epoch']
 return load(ROOT/'deadline.json')['deadline_epoch']
def api(url,path):
 try:
  with urllib.request.urlopen(url+path,timeout=3) as r:return json.load(r)
 except Exception:return None
def owned_stop(pid,created):
 try:
  p=psutil.Process(pid)
  if abs(p.create_time()-created)>0.1:raise RuntimeError('PID identity mismatch; refuse stop')
  os.killpg(pid,signal.SIGTERM)
  try:p.wait(timeout=20)
  except psutil.TimeoutExpired:os.killpg(pid,signal.SIGKILL)
 except psutil.NoSuchProcess:pass
class Sampler:
 def __init__(self,session,path):self.s=session;self.path=path;self.stop=threading.Event();self.rows=[];self.procs={};self.abort=None
 def __enter__(self):
  psutil.cpu_percent();self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start();return self
 def __exit__(self,*a):self.stop.set();self.thread.join(timeout=6)
 def run(self):
  with self.path.open('w') as out:
   while not self.stop.is_set():
    t=time.monotonic();m=psutil.virtual_memory();row={'wall_time':time.time(),'monotonic':t,'ram_used_gib':(m.total-m.available)/GIB,'mem_available_gib':m.available/GIB,'system_cpu_pct':psutil.cpu_percent(),'processes':[]}
    try:
     p=psutil.Process(self.s.proc.pid)
     for q in [p]+p.children(recursive=True):
      q=self.procs.setdefault(q.pid,q)
      with q.oneshot():
       io=q.io_counters();row['processes'].append({'pid':q.pid,'rss_gib':q.memory_info().rss/GIB,'cpu_pct':q.cpu_percent(),'read_bytes':io.read_bytes,'read_count':io.read_count})
    except psutil.Error:pass
    try:
     data=subprocess.check_output(['nvidia-smi','--query-gpu=index,utilization.gpu,power.draw,memory.used,clocks.sm','--format=csv,noheader,nounits'],text=True,timeout=3)
     row['gpus']=[dict(zip(['index','util_pct','power_w','vram_mib','sm_mhz'],map(float,line.split(',')))) for line in data.splitlines()]
    except Exception as e:row['gpu_error']=str(e)
    row['metrics']=api(self.s.url,'/metrics');self.rows.append(row);out.write(json.dumps(row)+'\n');out.flush()
    if m.available<12*GIB:
     self.abort='RAM_ABORT';owned_stop(self.s.proc.pid,self.s.created);return
    if self.s.budgeted and time.time()>deadline()-120:
     self.abort='DEADLINE_ABORT';owned_stop(self.s.proc.pid,self.s.created);return
    self.stop.wait(max(0,1-(time.monotonic()-t)))
 def summary(self):
  rows=self.rows
  def vals(f):return [v for r in rows if (v:=f(r)) is not None]
  cpu=vals(lambda r:r.get('system_cpu_pct'))
  return {'path':str(self.path),'samples':len(rows),'system_cpu_mean_pct':statistics.mean(cpu) if cpu else None,'system_cpu_peak_pct':max(cpu) if cpu else None,'peak_rss_gib':max(vals(lambda r:sum(p['rss_gib'] for p in r['processes'])),default=None),'peak_ram_used_gib':max(vals(lambda r:r['ram_used_gib']),default=None),'min_available_gib':min(vals(lambda r:r['mem_available_gib']),default=None),'gpus':{str(i):{'mean_util_pct':statistics.mean([g['util_pct'] for r in rows for g in r.get('gpus',[]) if g['index']==i]) if any(g['index']==i for r in rows for g in r.get('gpus',[])) else None,'peak_vram_mib':max([g['vram_mib'] for r in rows for g in r.get('gpus',[]) if g['index']==i],default=None)} for i in [0,1]},'abort':self.abort}
class Session:
 def __init__(self,variant,profile,path,port=18132,budgeted=True,diagnostic_env=None,host='127.0.0.1',console_logs=False):
  self.variant=variant;self.profile=profile;self.path=pathlib.Path(path);self.port=port;self.budgeted=budgeted
  self.cfg=load(ROOT/'variants'/variant/f'{profile}.json');self.url=f'http://127.0.0.1:{port}';self.proc=None;self.dmon=None;self.host=host;self.capture_requests=0;self.console_logs=console_logs;self.log_follower=None;self.monitor_recorder=None
  if diagnostic_env:self.cfg.setdefault('diagnostic_env',{}).update(diagnostic_env)
 def __enter__(self):
  for d in ['raw','logs','telemetry','traces']: (self.path/d).mkdir(parents=True,exist_ok=True)
  if self.budgeted and time.time()>deadline()-2700:raise RuntimeError('Consolidation window; no new inference session')
  if psutil.virtual_memory().available<100*GIB:raise RuntimeError('Insufficient available RAM for full arena')
  if subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip():raise RuntimeError('Existing CUDA compute process; refuse collision')
  with socket.socket() as sock:
   # A completed HTTP server can leave TIME_WAIT sockets. Reuse permits that
   # state, while bind still rejects an active listener (including wildcard).
   sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
   try:sock.bind((self.host,self.port))
   except OSError:raise RuntimeError('Port already occupied; use explicit --port override')
  expected=self.cfg['binary_sha256'];actual=hashlib.sha256(pathlib.Path(self.cfg['exe']).read_bytes()).hexdigest()
  if actual!=expected:raise RuntimeError('Frozen binary hash mismatch')
  head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=self.cfg['cwd'],text=True).strip()
  if head!=self.cfg['source_sha']:raise RuntimeError('Source identity mismatch')
  cfg=copy.deepcopy(self.cfg);cfg['log']=str(self.path/'logs/engine.log');cfg['port']=self.port;cfg['host']=self.host
  save(self.path/'config.json',cfg)
  print('RESOLVED_CONFIG',json.dumps(cfg),flush=True)
  env=os.environ.copy()
  for k in ['STRATA_SPLIT_OWN','STRATA_KV_ROT','STRATA_REFILL_SERIAL','STRATA_SPEC_COUPLED','STRATA_ADAPT_NOWAIT','STRATA_POOL_TRACE','STRATA_TRACE_ADAPT','STRATA_LAB_TRACE','STRATA_LAB_SIGNAL','STRATA_LAB_COMPATIBLE','STRATA_LAB_MISS_WAITS','STRATA_VERIFY_DEVICE_PLAN','STRATA_LAB_PLAN_IDS','STRATA_LAB_GPU_ROUTER','STRATA_LAB_PERSISTENT','STRATA_LAB_PERSISTENT_LOG','STRATA_LAB_PERSISTENT_CHECK','STRATA_LAB_PLAN_COMPARE','STRATA_LAB_PLAN_PLE_FENCE','STRATA_LAB_SKIP_LOCAL_PLAN','STRATA_LAB_DIRECT_PARTS','STRATA_POOL_SPIN_US','STRATA_DBG_NAN']:env.pop(k,None)
  env.update(cfg['env'])
  # Diagnostic environment is explicit and writes into this attempt only.
  for k,v in cfg.get('diagnostic_env',{}).items():env[k]=str(v).replace('{attempt}',str(self.path))
  entry=[cfg['server_entrypoint']] if cfg.get('server_entrypoint') else ['-m','serve.server']
  if cfg.get('server_entrypoint'):env['STRATA_RESEARCH_OUTPUT_IDS']=str(self.path/'raw/output-ids')
  cmd=[cfg['python'],*entry,'--engine','strata','--config',str(self.path/'config.json'),'--host',self.host,'--port',str(self.port)]
  self.out=(self.path/'logs/server.log').open('w');start=time.monotonic()
  self.proc=subprocess.Popen(cmd,cwd=cfg['cwd'],env=env,stdout=self.out,stderr=subprocess.STDOUT,start_new_session=True);self.created=psutil.Process(self.proc.pid).create_time()
  save(ROOT/'variants'/self.variant/'owned-process.json',{'pid':self.proc.pid,'create_time':self.created,'attempt':str(self.path),'command':cmd})
  save(self.path/'process.json',{'pid':self.proc.pid,'create_time':self.created,'command':cmd,'environment':{k:env.get(k) for k in cfg['env']|cfg.get('diagnostic_env',{})}})
  self.dmonout=(self.path/'telemetry/pcie-dmon.log').open('w');self.dmon=subprocess.Popen(['nvidia-smi','dmon','-i','0,1','-s','t','-d','1','-o','DT'],stdout=self.dmonout,stderr=subprocess.STDOUT)
  try:
   if self.console_logs:
    (self.path/'logs/engine.log').touch()
    print('LOGS',self.path/'logs',flush=True)
    self.log_follower=subprocess.Popen(['tail','-n','+1','-f','--sleep-interval=0.2',str(self.path/'logs/server.log'),str(self.path/'logs/engine.log')])
   with Sampler(self,self.path/'telemetry/startup.jsonl') as sampler:
    until=time.monotonic()+900
    while time.monotonic()<until:
     h=api(self.url,'/health')
     if h and h.get('loaded') and h.get('status')=='ok':break
     if self.proc.poll() is not None:raise RuntimeError(f'Server exited {self.proc.returncode}')
     if sampler.abort:raise RuntimeError(sampler.abort)
     time.sleep(1)
    else:raise RuntimeError('Startup timed out')
   metrics=api(self.url,'/metrics')
   if metrics['engine']['max_context']!=self.cfg['max_total_context']:raise RuntimeError('Runtime context differs from frozen profile')
   budgetpath=ROOT/'analysis/control-budgets-v2.json'
   budget=load(budgetpath if budgetpath.exists() else ROOT/'analysis/control-budgets.json')[self.profile]
   engine=metrics['engine'];primary=engine['expert_slots_primary'];secondary=engine['expert_slots']-primary
   if (primary,secondary)!=(budget['primary_slots'],budget['helper_or_stage1_slots']):raise RuntimeError(f'Expert capacity differs from frozen budget: {primary}/{secondary}')
   save(self.path/'raw/resource-check.json',{'state':'PASS','primary_slots':primary,'stage1_slots':secondary,'expert_cache_primary_mib':engine.get('expert_cache_primary_mib'),'expert_cache_total_mib':engine.get('expert_cache_mib'),'KV_resident_effective':engine.get('kv_resident'),'baseline':budget,'byte_class_basis':'same frozen allocator/profile/native formats and exact startup capacities; control classes independently captured in diagnostics; no extra GPU predictor allocation'})
   self.engine_commands=[p.cmdline() for p in psutil.Process(self.proc.pid).children(recursive=True) if p.exe()==self.cfg['exe']]
   save(self.path/'raw/engine-commands.json',self.engine_commands)
   save(self.path/'raw/startup.json',{'cold_start_s':time.monotonic()-start,'health':h,'metrics':metrics,'telemetry':sampler.summary()})
   if self.console_logs:
    from record_ui_metrics import MonitorRecorder
    output=self.path/'telemetry/ui-monitor'
    self.monitor_recorder=MonitorRecorder(self.url,output,self.proc.pid,self.created,self.path/'config.json').start()
    print('UI_MONITOR_LOGS',output,flush=True)
   print('READY',self.variant,self.profile,round(time.monotonic()-start,2),flush=True);return self
  except BaseException:self.__exit__();raise
 def __exit__(self,*a):
  if self.monitor_recorder:self.monitor_recorder.close()
  if self.proc:
   owned_stop(self.proc.pid,self.created)
   try:self.proc.wait(timeout=5)
   except subprocess.TimeoutExpired:pass
  if self.dmon:
   self.dmon.terminate()
   try:self.dmon.wait(timeout=3)
   except subprocess.TimeoutExpired:self.dmon.kill();self.dmon.wait()
   self.dmonout.close()
  if self.log_follower:
   self.log_follower.terminate()
   try:self.log_follower.wait(timeout=3)
   except subprocess.TimeoutExpired:self.log_follower.kill();self.log_follower.wait()
  if hasattr(self,'out'):self.out.close()
  time.sleep(1)
 def request(self,payload_name,label,kind='measured',manifest_path=None):
  manifest=load(manifest_path or ROOT/'workloads/manifest.json');info=manifest['payloads'][payload_name];p=load(info['path'])
  if hashjson(p)!=info['payload_sha256']:raise RuntimeError('Frozen payload hash mismatch')
  if info['actual_input_tokens']+p['max_tokens']+8>self.cfg['max_total_context']:raise RuntimeError('Admission budget exceeded')
  raw=self.path/'raw';save(raw/f'{label}-request.json',p)
  offset=pathlib.Path(self.cfg.get('log','/nonexistent')).stat().st_size if pathlib.Path(self.cfg.get('log','/nonexistent')).exists() else 0
  log=self.path/'logs/engine.log';offset=log.stat().st_size if log.exists() else 0
  record={'variant':self.variant,'profile':self.profile,'kind':kind,'payload':info,'source_sha':self.cfg['source_sha'],'binary_sha256':self.cfg['binary_sha256'],'full_config':self.cfg,'full_engine_commands':self.engine_commands,'started_epoch':time.time(),'requested_output':p['max_tokens']}
  self.capture_requests+=1
  start=time.perf_counter();first=None;events=[];text=[];reason=[];usage={};fin=[]
  try:
   req=urllib.request.Request(self.url+'/v1/chat/completions',data=json.dumps(p).encode(),headers={'Content-Type':'application/json'})
   with Sampler(self,self.path/'telemetry'/f'{label}.jsonl') as sampler:
    with urllib.request.urlopen(req,timeout=900) as response:
     for line in response:
      if not line.startswith(b'data:'):continue
      data=line[5:].strip()
      if data==b'[DONE]':break
      chunk=json.loads(data);events.append({'elapsed_s':time.perf_counter()-start,'chunk':chunk})
      if chunk.get('usage'):usage=chunk['usage']
      for ch in chunk.get('choices',[]):
       d=ch.get('delta') or {};a=d.get('content') or '';b=d.get('reasoning_content') or ''
       if (a or b or d.get('tool_calls')) and first is None:first=time.perf_counter()
       text.append(a);reason.append(b)
       if ch.get('finish_reason'):fin.append(ch['finish_reason'])
   end=time.perf_counter();time.sleep(.1);status=api(self.url,'/v1/status');metrics=api(self.url,'/metrics');t=status.get('last_timings') or {}
   lines=log.read_bytes()[offset:].decode(errors='replace');(raw/f'{label}-engine.log').write_text(lines)
   rounds=re.search(r'strata decode timing: (\d+) windows',lines)
   cache=re.search(r'expert cache hit rate: ([\d.]+)% \((\d+) hits / (\d+) lookups\)',lines)
   off=re.search(r'; (\d+) more read by the GPU over PCIe',lines)
   rec={'actual_input_tokens':usage.get('prompt_tokens'),'actual_output_tokens':usage.get('completion_tokens'),'PP':t.get('prompt_per_second'),'TG':t.get('predicted_per_second'),'TTFT_s':(first or end)-start,'wall_s':end-start,'pp_s':t.get('prompt_ms',0)/1000,'decode_s':t.get('predicted_ms',0)/1000,'reuse':t.get('cache_n'),'finish_reason':fin[-1] if fin else None,'mtp_proposed':t.get('draft_n'),'mtp_accepted':t.get('draft_n_accepted'),'verify_windows':int(rounds[1]) if rounds else None,'hit_rate_pct':float(cache[1]) if cache else None,'local_vram_entries':int(cache[2]) if cache else None,'cpu_fallback_entries':int(cache[3])-int(cache[2]) if cache else None,'offloaded_entries':int(off[1]) if off else None,'text':''.join(text),'reasoning':''.join(reason),'usage':usage,'timings':t,'telemetry':sampler.summary()}
   rec['output_text_sha256']=hashlib.sha256((rec['reasoning']+'\0'+rec['text']).encode()).hexdigest();rec['output_ids']='UNAVAILABLE: frontend strips internal special markers; text/reasoning and raw chunks hashed instead'
   rec['application_status']='REASONING_ONLY_LIMIT' if not rec['text'].strip() and rec['reasoning'].strip() else 'NONEMPTY_ANSWER_LENGTH_LIMIT' if rec['finish_reason']=='length' else 'STOPPED_WITH_ANSWER' if rec['text'].strip() else 'NO_ANSWER'
   rec['mtp_acceptance_pct']=100*rec['mtp_accepted']/rec['mtp_proposed'] if rec['mtp_proposed'] else None
   rec['mtp_accepted_per_window']=rec['mtp_accepted']/rec['verify_windows'] if rec['verify_windows'] else None
   if self.cfg.get('server_entrypoint'):
    output_path=raw/f'output-ids-request{self.capture_requests}.json';input_path=raw/f'output-ids-input-request{self.capture_requests}.json'
    if output_path.exists():
     true_ids=load(output_path);rec['actual_output_ids_path']=str(output_path);rec['actual_output_ids_sha256']=hashlib.sha256(output_path.read_bytes()).hexdigest();rec['actual_engine_output_ID_count']=len(true_ids);rec['output_ids']='AVAILABLE: actual engine integer IDs retained by common frontend wrapper'
    if input_path.exists():rec['actual_engine_input']=load(input_path);rec['actual_engine_input_evidence_path']=str(input_path)
   record.update(rec);save(raw/f'{label}-status.json',status);save(raw/f'{label}-metrics.json',metrics)
   errors=[]
   if rec['actual_input_tokens']!=info['actual_input_tokens']:errors.append('INPUT_TOKEN_MISMATCH')
   if rec['reuse']!=0:errors.append('REUSE_NONZERO')
   if kind in ['measured','warmup'] and rec['actual_output_tokens']!=p['max_tokens']:errors.append('EARLY_TERMINATION')
   if sampler.abort:errors.append(sampler.abort)
   if not rec['TG'] or not rec['PP']:errors.append('MISSING_TIMING')
   if 'tool_calls' in fin:errors.append('UNEXPECTED_TOOL_CALL')
   record.update(state='INVALID_PROTOCOL' if errors else 'VALID',invalid_reasons=errors)
  except Exception as e:record.update(state='FAILED',error=repr(e))
  save(raw/f'{label}-stream.json',events);save(raw/f'{label}.json',record)
  (raw/f'{label}-response.txt').write_text(record.get('text',''))
  print(label,record['state'],'input',record.get('actual_input_tokens'),'output',record.get('actual_output_tokens'),'PP',record.get('PP'),'TG',record.get('TG'),flush=True)
  return record
def benchmark(variant,profile,experiment,attempt='v1',port=18132,budgeted=True):
 path=ROOT/'experiments'/experiment/attempt/profile
 if path.exists():raise RuntimeError('Attempt exists; do not repeat unchanged point or overwrite')
 path.mkdir(parents=True)
 protocol={'variant':variant,'profile':profile,'warmup':'same saved 4096-input/64-output request','restart':'one fresh server per profile; serial three measured, adaptive cache history preserved','measured_attempts':3,'fixed_output':4096,'invalids':'preserved, no unbounded replacements','order':['warmup','run1','run2','run3']};save(path/'protocol.json',protocol)
 results=[]
 with Session(variant,profile,path,port=port,budgeted=budgeted) as s:
  warm=s.request('warmup','warmup','warmup')
  if warm['state']!='VALID':raise RuntimeError('Warmup failed')
  for n in range(1,4):
   r=s.request(f'{profile}-run{n}',f'run{n}');results.append(r)
   save(path/'results.json',{'protocol':protocol,'runs':results,'valid_count':sum(x['state']=='VALID' for x in results)})
   if r['state']=='FAILED':break
 return results
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['start','stop','benchmark']);ap.add_argument('--variant',default='control');ap.add_argument('--profile',choices=['32k','128k'],default='32k');ap.add_argument('--experiment',default='E002-controls');ap.add_argument('--attempt',default='v1');ap.add_argument('--port',type=int,default=18132);ap.add_argument('--host',default='127.0.0.1',help='Manual server bind address; benchmark always stays private');ap.add_argument('--reproduction',action='store_true',help='Explicit user replay after campaign completion or deadline; never extends active research');a=ap.parse_args()
 complete=(ROOT/'active-campaign.json').exists() and load(ROOT/'active-campaign.json').get('state')=='COMPLETE'
 if a.reproduction and time.time()<=deadline() and not complete:raise RuntimeError('Active research deadline remains binding; reproduction override requires campaign completion or recorded deadline')
 if a.mode=='stop':
  p=ROOT/'variants'/a.variant/'owned-process.json'
  if p.exists():r=load(p);owned_stop(r['pid'],r['create_time'])
 elif a.mode=='benchmark':benchmark(a.variant,a.profile,a.experiment,a.attempt,port=a.port,budgeted=not a.reproduction)
 else:
  path=ROOT/'variants'/a.variant/'manual'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
  with Session(a.variant,a.profile,path,a.port,budgeted=False,host=a.host,console_logs=True) as s:
   print('HTTP',s.url,'(bind '+s.host+':'+str(s.port)+')',flush=True);s.proc.wait()
if __name__=='__main__':main()
