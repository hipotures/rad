"""Bounded fresh-server A/B runner. No native source changes; no selective retries."""
import argparse,collections,copy,datetime,hashlib,json,os,pathlib,re,signal,socket,statistics,subprocess,sys,threading,time,urllib.request
import psutil
C=pathlib.Path(__file__).resolve().parents[1]
def load(p):return json.loads(pathlib.Path(p).read_text())
def save(p,x):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');tmp.replace(p)
def hashjson(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def filehash(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(16*1024*1024),b''):h.update(b)
 return h.hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def status(state,**kw):
 j={'state':state,'updated_utc':utc(),**kw};save(C/'STATUS.json',j)
 (C/'STATUS.md').write_text('# Upstream921 spin validation\n\n'+json.dumps(j,indent=2)+'\n')
def get(url,path):
 try:
  with urllib.request.urlopen(url+path,timeout=3) as r:return json.load(r)
 except Exception:return None
def gpu_jobs():return subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'],text=True,timeout=5).strip()
def verify(cfg,full=False):
 assert filehash(cfg['exe'])==cfg['binary_sha256'],'BINARY_SHA'
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['cwd'],text=True).strip()==cfg['source_sha'],'SOURCE_SHA'
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=cfg['cwd'],text=True).strip(),'SOURCE_DIRTY'
 for p,j in load(cfg['model_manifest'])['files'].items():
  p=pathlib.Path(p);st=p.stat()
  assert (str(p.resolve()),st.st_size,st.st_mtime_ns,st.st_ino)==(j['resolved'],j['size'],j['mtime_ns'],j['inode']),f'MODEL_STAT {p}'
  if full:assert filehash(p)==j['sha256'],f'MODEL_SHA {p}'
def identity(proc):return {'pid':proc.pid,'create_time':proc.create_time()}
def alive(j):
 try:return abs(psutil.Process(j['pid']).create_time()-j['create_time'])<.01 and psutil.Process(j['pid']).status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
def owned_cleanup(parent,children):
 if parent and alive(parent):
  assert os.getpgid(parent['pid'])==parent['pid'],'OWNED_GROUP_ID'
  os.killpg(parent['pid'],signal.SIGTERM)
  try:psutil.Process(parent['pid']).wait(timeout=15)
  except psutil.TimeoutExpired:
   if alive(parent):os.killpg(parent['pid'],signal.SIGKILL)
 for j in children:
  if alive(j):psutil.Process(j['pid']).terminate()
 procs=[psutil.Process(j['pid']) for j in children if alive(j)]
 _,remaining=psutil.wait_procs(procs,timeout=5)
 for p in remaining:
  j=next(j for j in children if j['pid']==p.pid)
  if alive(j):p.kill()
 psutil.wait_procs(remaining,timeout=3)
 assert not any(alive(j) for j in children),'OWNED_CHILD_REMAINS'

class Sampler:
 def __init__(self,s,path):self.s=s;self.path=path;self.rows=[];self.event=threading.Event();self.error=None
 def __enter__(self):self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start();return self
 def __exit__(self,*a):self.event.set();self.thread.join(timeout=6)
 def run(self):
  keys=['index','util_pct','vram_mib','power_w','sm_mhz','mem_mhz','temperature_c','throttle_hex','pcie_gen','pcie_width']
  query='index,utilization.gpu,memory.used,power.draw,clocks.sm,clocks.mem,temperature.gpu,clocks_event_reasons.active,pcie.link.gen.current,pcie.link.width.current'
  try:
   with self.path.open('x') as out:
    while not self.event.is_set():
     start=time.monotonic();m=psutil.virtual_memory();cpu=psutil.cpu_times();sw=psutil.swap_memory()
     row={'monotonic':start,'epoch':time.time(),'cpu_times':cpu._asdict(),'ram_used_gib':(m.total-m.available)/1024**3,'ram_available_gib':m.available/1024**3,'swap':sw._asdict(),'psi':{p.name:p.read_text() for p in pathlib.Path('/proc/pressure').glob('*')}}
     try:
      procs=[psutil.Process(self.s.proc.pid)]+psutil.Process(self.s.proc.pid).children(recursive=True)
      row['processes']=[{'pid':p.pid,'rss_bytes':p.memory_info().rss,'cpu_times':p.cpu_times()._asdict()} for p in procs]
     except psutil.Error:pass
     try:
      data=subprocess.check_output(['nvidia-smi','--query-gpu='+query,'--format=csv,noheader,nounits'],text=True,timeout=3)
      row['gpus']=[]
      for line in data.splitlines():
       values=[x.strip() for x in line.split(',')];g={}
       for k,v in zip(keys,values):
        try:g[k]=float(v) if k!='throttle_hex' else v
        except ValueError:g[k]=v
       row['gpus'].append(g)
     except Exception as e:row['gpu_error']=repr(e)
     row['metrics']=get(self.s.url,'/metrics');row['sample_end_monotonic']=time.monotonic()
     self.rows.append(row);out.write(json.dumps(row)+'\n');out.flush()
     if m.available<10*1024**3:self.error='RAM_ABORT';self.s.abort='RAM_ABORT';return
     self.event.wait(max(0,1-(time.monotonic()-start)))
  except Exception as e:self.error=repr(e);self.s.abort='SAMPLER_FAILURE '+repr(e)

class Session:
 def __init__(self,cfg,path,arm,parentenv,deadline):
  self.cfg=copy.deepcopy(cfg);self.path=path;self.arm=arm;self.parentenv=parentenv;self.deadline=deadline;self.proc=None;self.children=[];self.parent=None;self.abort=None;self.request_number=0;self.url='http://127.0.0.1:18139'
 def check(self):
  if self.abort:raise RuntimeError(self.abort)
  if time.monotonic()>self.deadline:raise TimeoutError('ARM_TOTAL_TIMEOUT')
  if self.proc and self.proc.poll() is not None:raise RuntimeError('SERVER_EXIT '+str(self.proc.returncode))
 def __enter__(self):
  self.path.mkdir(parents=True,exist_ok=False)
  for d in ['raw','logs','telemetry']:(self.path/d).mkdir()
  verify(self.cfg)
  assert not gpu_jobs(),'GPU_CONFLICT'
  assert psutil.virtual_memory().available>110*1024**3,'STARTUP_RAM'
  with socket.socket() as sock:sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);sock.bind(('127.0.0.1',18139))
  cfg=self.cfg;cfg.update(log=str(self.path/'logs/engine.log'),host='127.0.0.1',port=18139)
  cfg['env']={'CUDA_VISIBLE_DEVICES':'0,1','STRATA_DECODE_TIMING':'1','STRATA_SPLIT_TIMING':'1'}
  env=self.parentenv.copy();env.update(cfg['env'])
  if self.arm=='B':env['STRATA_POOL_SPIN_US']='100';cfg['env']['STRATA_POOL_SPIN_US']='100'
  else:env.pop('STRATA_POOL_SPIN_US',None)
  save(self.path/'config.json',cfg)
  cmd=[cfg['python'],cfg['server_entrypoint'],'--engine','strata','--config',str(self.path/'config.json'),'--host','127.0.0.1','--port','18139']
  self.out=(self.path/'logs/server.log').open('x');t=time.monotonic()
  self.proc=subprocess.Popen(cmd,cwd=cfg['cwd'],env=env,stdout=self.out,stderr=subprocess.STDOUT,start_new_session=True)
  self.parent=identity(psutil.Process(self.proc.pid));save(self.path/'process.json',{'parent':self.parent,'command':cmd,'created_utc':utc()});save(C/'owned-process.json',{'parent':self.parent,'children':[],'attempt':str(self.path)})
  self.watchstop=threading.Event()
  def watch():
   while not self.watchstop.wait(1):
    if time.monotonic()>self.deadline or self.abort:
     self.abort=self.abort or 'ARM_TOTAL_TIMEOUT'
     try:
      if alive(self.parent):os.killpg(self.parent['pid'],signal.SIGTERM)
     except ProcessLookupError:pass
     return
  self.watch=threading.Thread(target=watch,daemon=True);self.watch.start()
  try:
   with Sampler(self,self.path/'telemetry/startup.jsonl') as sample:
    stop=min(self.deadline,time.monotonic()+600)
    while time.monotonic()<stop:
     self.check();h=get(self.url,'/health')
     if h and h.get('loaded') and h.get('status')=='ok':break
     time.sleep(.5)
    else:raise TimeoutError('STARTUP_TIMEOUT')
   self.children=[identity(p) for p in psutil.Process(self.proc.pid).children(recursive=True)]
   engines=[psutil.Process(j['pid']) for j in self.children if pathlib.Path(psutil.Process(j['pid']).exe()).resolve()==pathlib.Path(cfg['exe']).resolve()]
   assert len(engines)==1,'NATIVE_CHILD_COUNT'
   self.native=engines[0]
   save(C/'owned-process.json',{'parent':self.parent,'children':self.children,'attempt':str(self.path)})
   metrics=get(self.url,'/metrics');assert metrics and metrics['engine']['max_context']==cfg['max_total_context'],'MAX_CONTEXT'
   self.engine=metrics['engine'];command=self.native.cmdline()
   expected={'--pool-workers':'15','--spec':'4','--spec-min-p':'0.5','--kv':'int8','--kv-resident':'32768','--prefill':'auto','--suffix-draft':'0','--prompt-cache':'0','--max-context':str(cfg['max_total_context']),'--pcie-frac':'0.28','--layer-split':cfg['layer_split']}
   for k,v in expected.items():assert command[command.index(k)+1]==v,('SETTING',k,v,command)
   for k in ['--pack','--native','--ple-gguf','--expert-profile','--mtp','--expert-cache']:
    assert command[command.index(k)+1]==cfg['args'][cfg['args'].index(k)+1],('MODEL_OPTION',k)
   for k in ['--pool-tasks','--remote-expert-opt','--expert-cache-device1']:assert k not in command,('FORBIDDEN',k)
   actualenv=self.native.environ();assert ('STRATA_POOL_SPIN_US' not in actualenv) if self.arm=='A' else actualenv.get('STRATA_POOL_SPIN_US')=='100'
   expectedstrata={k:v for k,v in cfg['env'].items() if k.startswith('STRATA_')}
   assert {k:v for k,v in actualenv.items() if k.startswith('STRATA_')}==expectedstrata,'EXTRA_STRATA_VARIABLE'
   jobs=gpu_jobs();pids={int(x.split(',')[0]) for x in jobs.splitlines() if x.strip()};assert pids=={self.native.pid},('GPU_PROCESS_DRIFT',jobs)
   self.native_manifest={'executable':self.native.exe(),'binary_sha256':cfg['binary_sha256'],'source_sha':cfg['source_sha'],'command':command,'environment_sha256_by_key':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in actualenv.items()},'relevant_environment':{k:v for k,v in actualenv.items() if k.startswith(('STRATA_','CUDA_')) or k in ['LD_LIBRARY_PATH','OMP_NUM_THREADS']},'affinity':self.native.cpu_affinity(),'capacity':{k:self.engine.get(k) for k in ['expert_slots','expert_slots_primary','expert_cache_mib','expert_cache_primary_mib','kv_resident','kv','max_context']},'resolved':expected,'model_manifest_sha256':filehash(cfg['model_manifest'])}
   save(self.path/'raw/native-manifest.json',self.native_manifest)
   text=(self.path/'logs/engine.log').read_text(errors='replace')
   split=re.search(r'layer split: CUDA0 runs layers 0-(\d+)',text);assert split and int(split[1])+1==int(cfg['layer_split']),'RESOLVED_SPLIT'
   save(self.path/'raw/startup.json',{'seconds':time.monotonic()-t,'health':h,'metrics':metrics,'graph_messages':[x for x in text.splitlines() if re.search('graph|capture|P2P|peer',x,re.I)]})
   print('READY',cfg['regime'],cfg['max_total_context'],self.arm,round(time.monotonic()-t,1),'capacity',self.native_manifest['capacity'],flush=True)
   return self
  except BaseException:self.__exit__();raise
 def __exit__(self,*args):
  if self.proc:
   try:self.children=list({j['pid']:(j) for j in self.children+[identity(p) for p in psutil.Process(self.proc.pid).children(recursive=True)]}.values())
   except psutil.NoSuchProcess:pass
  if hasattr(self,'watchstop'):self.watchstop.set();self.watch.join(timeout=2)
  owned_cleanup(self.parent,self.children)
  if self.proc:
   try:self.proc.wait(timeout=2)
   except subprocess.TimeoutExpired:pass
  if hasattr(self,'out'):self.out.close()
  time.sleep(.5)
  jobs=gpu_jobs();save(self.path/'cleanup.json',{'utc':utc(),'parent_alive':alive(self.parent) if self.parent else False,'children_alive':[j for j in self.children if alive(j)],'gpu_jobs':jobs})
  assert not jobs,'GPU_JOBS_AFTER_CLEANUP'
 def request(self,name,label,manifest):
  self.check();info=manifest['payloads'][name];p=load(info['path']);assert hashjson(p)==info['payload_sha256'],'PAYLOAD_SHA'
  assert info['actual_input_tokens']+p['max_tokens']+8<=self.cfg['max_total_context'],'ADMISSION'
  self.request_number+=1;save(self.path/'raw'/f'{label}-request.json',p)
  log=self.path/'logs/engine.log';offset=log.stat().st_size;begin=time.monotonic();first=None;usage={};finish=None;chunks=0
  text=[];reason=[]
  request=urllib.request.Request(self.url+'/v1/chat/completions',data=json.dumps(p).encode(),headers={'Content-Type':'application/json'})
  with Sampler(self,self.path/'telemetry'/f'{label}.jsonl') as sample:
   with urllib.request.urlopen(request,timeout=min(900,max(1,self.deadline-time.monotonic()))) as response,(self.path/'raw'/f'{label}-stream.jsonl').open('x') as out:
    for line in response:
     self.check()
     if time.monotonic()-begin>900:raise TimeoutError('REQUEST_TIMEOUT')
     if not line.startswith(b'data:'):continue
     data=line[5:].strip()
     if data==b'[DONE]':break
     chunk=json.loads(data);chunks+=1;out.write(json.dumps({'monotonic':time.monotonic(),'chunk':chunk})+'\n')
     if chunk.get('usage'):usage=chunk['usage']
     for ch in chunk.get('choices',[]):
      d=ch.get('delta') or {};a=d.get('content') or '';b=d.get('reasoning_content') or ''
      if (a or b or d.get('tool_calls')) and first is None:first=time.monotonic()
      text.append(a);reason.append(b)
      if ch.get('finish_reason'):finish=ch['finish_reason']
   end=time.monotonic()
  self.check();time.sleep(.15)
  capture=load(self.path/'raw'/f'capture-request{self.request_number}.json')
  assert capture['input_ids_sha256']==info['input_ids_sha256'],'INPUT_IDS_SHA'
  assert capture['output_count']==p['max_tokens'],'OUTPUT_ID_COUNT'
  assert usage.get('prompt_tokens')==info['actual_input_tokens'],'INPUT_COUNT'
  assert usage.get('completion_tokens')==p['max_tokens'] and finish=='length','OUTPUT_COUNT_OR_FINISH'
  assert self.native.pid==capture['native_pid'],'ENGINE_RESTART'
  lines=log.read_bytes()[offset:].decode(errors='replace');(self.path/'raw'/f'{label}-engine.log').write_text(lines)
  metrics=get(self.url,'/metrics');stat=get(self.url,'/v1/status');t=stat.get('last_timings') or {};native=capture['native_last']
  rounds=re.search(r'strata decode timing: (\d+) windows',lines);assert rounds,'VERIFY_WINDOWS'
  cache=re.search(r'expert cache hit rate: ([\d.]+)% \((\d+) hits / (\d+) lookups\)',lines);assert cache,'ROUTING'
  mapped=re.search(r'; (\d+) more read by the GPU over PCIe or from another GPU \(([\d.]+)% of all (\d+) routed\)',lines)
  local=int(cache[2]);cpu=int(cache[3])-local;nonlocal_gpu=int(mapped[1]) if mapped else 0;allentries=local+cpu+nonlocal_gpu
  if mapped:assert int(mapped[3])==allentries,'ROUTING_DENOMINATOR'
  work=re.search(r'per layer-window: CPU experts ([\d.]+) \(([\d.]+) entries\)',lines);assert work,'CPU_DEMAND'
  timing=re.search(r'per-layer host ([\d.]+) \[plan ([\d.]+) actq ([\d.]+) jobs ([\d.]+) CPU ([\d.]+)\]',lines)
  firstsnap=capture['first_token'];lastsnap=capture['end'];assert firstsnap,'FIRST_TOKEN'
  duration=lastsnap['monotonic']-firstsnap['monotonic'];ticks=[b-a for a,b in zip(firstsnap['system_cpu_ticks'],lastsnap['system_cpu_ticks'])];total=sum(ticks[:8]);busy=sum(ticks[i] for i in [0,1,2,5,6]);steal=ticks[7]
  native_ticks=lastsnap['native_cpu_ticks']-firstsnap['native_cpu_ticks'];nativecores=100*native_ticks/os.sysconf('SC_CLK_TCK')/duration
  pp_start=capture['begin']['monotonic'];pp_end=firstsnap['monotonic'];dec_end=lastsnap['monotonic']
  telemetry={}
  for phase,a,b in [('prefill',pp_start,pp_end),('decode',pp_end,dec_end)]:
   rows=[r for r in sample.rows if r['monotonic']>=a and r['sample_end_monotonic']<=b]
   gs={}
   for i in [0,1]:
    g=[v for r in rows for v in r.get('gpus',[]) if v['index']==i]
    gs[str(i)]={k:statistics.mean([v[k] for v in g if isinstance(v.get(k),(int,float))]) if any(isinstance(v.get(k),(int,float)) for v in g) else None for k in ['util_pct','vram_mib','power_w','sm_mhz','mem_mhz','temperature_c','pcie_gen','pcie_width']}
    gs[str(i)]['throttle_flags']=dict(collections.Counter(v.get('throttle_hex') for v in g));gs[str(i)]['samples']=len(g)
   telemetry[phase]={'samples':len(rows),'gpus':gs,'ram_mean_gib':statistics.mean(r['ram_used_gib'] for r in rows) if rows else None,'native_rss_mean_gib':statistics.mean(q['rss_bytes']/1024**3 for r in rows for q in r.get('processes',[]) if q['pid']==self.native.pid) if rows else None,'swap_max_bytes':max((r['swap']['used'] for r in rows),default=None),'sampler_error':sample.error}
  r={'state':'VALID','regime':self.cfg['regime'],'context':self.cfg['max_total_context'],'arm':self.arm,'payload':info,'label':label,'started_monotonic':begin,'ended_monotonic':end,'TG':t.get('predicted_per_second'),'PP':t.get('prompt_per_second'),'wall_s':end-begin,'TTFT_s':(first or end)-begin,'native_TTFT_s':pp_end-pp_start,'decode_s':t.get('predicted_ms',0)/1000,'pp_s':t.get('prompt_ms',0)/1000,'actual_input_tokens':usage['prompt_tokens'],'actual_output_tokens':usage['completion_tokens'],'finish_reason':finish,'reuse':t.get('cache_n'),'mtp_proposed':t.get('draft_n'),'mtp_accepted':t.get('draft_n_accepted'),'verify_windows':int(rounds[1]),'local_vram_entries':local,'cpu_fallback_entries':cpu,'mapped_nonlocal_gpu_entries':nonlocal_gpu,'all_routed_entries':allentries,'local_pct':100*local/allentries,'cpu_pct':100*cpu/allentries,'mapped_pct':100*nonlocal_gpu/allentries,'cpu_experts_per_layer_window':float(work[1]),'cpu_entries_per_layer_window':float(work[2]),'decode_cpu_pct':100*busy/total,'decode_cpu_with_steal_pct':100*(busy+steal)/total,'decode_cpu_steal_pct':100*steal/total,'decode_process_cpu_cores_pct':nativecores,'decode_process_cpu_vm_pct':nativecores/os.cpu_count(),'cpu_decode_duration_s':duration,'CPU_completion_ms_per_window':float(timing[5]) if timing else None,'pool_plus_plan_ms_per_window':float(timing[1]) if timing else None,'input_ids_sha256':capture['input_ids_sha256'],'output_ids_sha256':capture['output_ids_sha256'],'output_ids_path':str(self.path/'raw'/f'output-ids-request{self.request_number}.json'),'input_ids_path':str(self.path/'raw'/f'input-ids-request{self.request_number}.json'),'text_sha256':hashlib.sha256((''.join(reason)+'\0'+''.join(text)).encode()).hexdigest(),'capture':capture,'timings':t,'metrics':metrics,'telemetry':telemetry,'graph_messages':[x for x in lines.splitlines() if re.search('graph|capture',x,re.I)],'unavailable':['exact per-worker spin/sleep counters','CPU-positive wake-up latency isolated from computation','mapped RAM versus remote GPU sub-breakdown when aggregate only']}
  assert r['TG'] and r['PP'] and r['mtp_proposed'] is not None and r['mtp_accepted'] is not None,'TIMING_OR_MTP'
  assert r['reuse']==0,'PROMPT_REUSE'
  r['mtp_acceptance_pct']=100*r['mtp_accepted']/r['mtp_proposed'] if r['mtp_proposed'] else 0
  r['mtp_accepted_per_window']=r['mtp_accepted']/r['verify_windows']
  save(self.path/'raw'/f'{label}.json',r)
  return r

def pairaudit(path):
 A=load(path/'A/raw/native-manifest.json');B=load(path/'B/raw/native-manifest.json')
 envdiff={k:[A['environment_sha256_by_key'].get(k),B['environment_sha256_by_key'].get(k)] for k in A['environment_sha256_by_key'].keys()|B['environment_sha256_by_key'].keys() if A['environment_sha256_by_key'].get(k)!=B['environment_sha256_by_key'].get(k)}
 assert set(envdiff)=={'STRATA_POOL_SPIN_US'},('ENVIRONMENT_DIFF',envdiff)
 for k in ['executable','binary_sha256','source_sha','command','affinity','capacity','resolved','model_manifest_sha256']:
  assert A[k]==B[k],('MANIFEST_DRIFT',k,A[k],B[k])
 a=load(path/'A/raw/measured.json');b=load(path/'B/raw/measured.json')
 assert a['input_ids_sha256']==b['input_ids_sha256'],'PAIR_INPUT_IDS'
 aid=load(a['output_ids_path']);bid=load(b['output_ids_path']);div=next((i for i,(x,y) in enumerate(zip(aid,bid)) if x!=y),None)
 same={k:a[k]==b[k] for k in ['mtp_proposed','mtp_accepted','verify_windows','all_routed_entries','local_vram_entries','cpu_fallback_entries','mapped_nonlocal_gpu_entries']}
 save(path/'audit.json',{'state':'PASS','environment_diff':envdiff,'spin_values':{'A':'ABSENT','B':'100'},'native_manifests_equal_except_spin':True,'input_ids_equal':True,'output_ids_identical':aid==bid,'first_output_divergence_zero_based':div,'counters_identical':same,'capacities_equal':True})
 return a,b

def runpair(cell,point,env,bases,manifest,timing,directory=None):
 regime,profile=cell.split('-');cfg=copy.deepcopy(bases[regime]);limit={'32k':32768,'128k':131072}[profile]
 cfg['args'][cfg['args'].index('--max-context')+1]=str(limit);cfg['max_total_context']=limit
 path=C/'raw'/cell/(directory or f"pair{point['pair']:02d}");path.mkdir(parents=True,exist_ok=False)
 save(path/'protocol.json',point);status('RUNNING',cell=cell,pair=point['pair'],order=point['order'],family=point['family'])
 for arm in point['order']:
  if time.monotonic()>timing['measurement_cutoff_monotonic']:raise TimeoutError('NO_NEW_ARM_AFTER_CUTOFF')
  print(f"{regime} {profile.upper()} pair {point['pair']}/12 arm {arm} family {point['family']}",flush=True)
  with Session(cfg,path/arm,arm,env,min(time.monotonic()+1800,timing['deadline_monotonic']-120)) as s:
   warm=s.request(f'{regime}/warmup','warmup',manifest)
   r=s.request(f"{regime}/{point['family']}-{profile}-run{point['payload_variant']}",'measured',manifest)
   save(path/arm/'result.json',r)
   print('RESULT',cell,point['pair'],arm,'TG',r['TG'],'wall',round(r['wall_s'],3),'CPU',round(r['decode_cpu_pct'],2),'steal',round(r['decode_cpu_steal_pct'],3),flush=True)
 a,b=pairaudit(path)
 save(path/'pair.json',{'state':'VALID','cell':cell,'point':point,'path':str(path),'TG_ratio':b['TG']/a['TG'],'wall_ratio':b['wall_s']/a['wall_s'],'CPU_ratio':b['decode_cpu_pct']/a['decode_cpu_pct']})
 print('PAIR VALID',cell,point['pair'],'TG ratio',round(b['TG']/a['TG'],5),flush=True)
 return path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['campaign','verify','stop']);ap.add_argument('--cell',choices=['IQ3_S-32k','IQ3_S-128k','Q4-32k','Q4-128k']);ap.add_argument('--full-model-hash',action='store_true');ap.add_argument('--reproduction',action='store_true',help='Create isolated replay directory and a new bounded deadline; never overwrite original campaign');a=ap.parse_args()
 if a.action=='stop':
  j=load(C/'owned-process.json');owned_cleanup(j['parent'],j['children']);print('OWNED STOP COMPLETE');return
 bases=load(C/'configs-base.json')
 for cfg in bases.values():verify(cfg,a.full_model_hash)
 if a.action=='verify':print('IDENTITIES VERIFIED');return
 timing=load(C/'timing.json');orders=load(C/'orders/all.json');manifest=load(C/'workloads/manifest.json');protocol=load(C/'protocol.json')
 # Environment never changes between arms/pairs. Retain hashes, not secrets.
 env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')}
 envmanifest={k:hashlib.sha256(v.encode()).hexdigest() for k,v in env.items()}
 if (C/'provenance/parent-environment-hashes.json').exists():assert load(C/'provenance/parent-environment-hashes.json')==envmanifest,'PARENT_ENVIRONMENT_DRIFT'
 else:save(C/'provenance/parent-environment-hashes.json',envmanifest)
 cells=[a.cell] if a.cell else protocol['cells']
 if a.reproduction:
  replay=C/'replays'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');replay.mkdir(parents=True)
  # Exact frozen cell/order/binary, bounded8h; separate data and ownership ledger.
  global_original=C
  globals()['C']=replay
  timing={'measurement_cutoff_monotonic':time.monotonic()+26100,'deadline_monotonic':time.monotonic()+28800}
  save(C/'timing.json',timing)
 def stop(*_):raise KeyboardInterrupt('Owned campaign interrupted')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  for n in range(1,13):
   for cell in cells:
    point=orders[cell]['pairs'][n-1];path=C/'raw'/cell/f'pair{n:02d}'
    if (path/'pair.json').exists():assert load(path/'pair.json')['state']=='VALID';continue
    if path.exists():raise RuntimeError('Preserved incomplete pair requires explicit objective invalidation audit; refuse silent repair: '+str(path))
    if time.monotonic()>timing['measurement_cutoff_monotonic']-1800:
     status('MEASUREMENT_CUTOFF',reason='Reserve one bounded pair plus reporting45min',next='aggregate');return
    runpair(cell,point,env,bases,manifest,timing)
  status('MATRIX_COMPLETE',valid_pairs_by_cell={cell:len(list((C/'raw'/cell).glob('*/pair.json'))) for cell in cells},next='Regenerate analysis/report and audit cleanup')
 except BaseException as e:
  status('NEEDS_PROTOCOL_AUDIT',error=repr(e),next='Preserve failing pair; diagnose objective cause before any replacement')
  raise
if __name__=='__main__':main()
