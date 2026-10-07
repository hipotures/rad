"""Serial Q4 campaign runner and safe foreground launchers for the frozen CURRENT binary."""
import argparse, copy, datetime, hashlib, json, os, pathlib, re, signal, socket, statistics, subprocess, sys, time
import psutil
from lab import ROOT, Session as BaseSession, Sampler, api, load, save, owned_stop

def option(cfg,key,value):
 a=cfg['args']
 if key in a:a[a.index(key)+1]=str(value)
 else:a.extend([key,str(value)])

def status(C,state,running=None,**extra):
 old=load(C/'STATUS.json');old.update(state=state,running=running,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra);save(C/'STATUS.json',old)
 (C/'STATUS.md').write_text('# Q4 controlled multi-GPU campaign\n\n'+state+'\n\n```json\n'+json.dumps(old,indent=2)+'\n```\n')

class Q4Session(BaseSession):
 def __init__(self,C,cfg,path,profile,port=18134,host='127.0.0.1',console=False):
  self.C=C;self.cfg=copy.deepcopy(cfg);self.variant=cfg.get('method','layer-split');self.profile=profile;self.path=path;self.port=port;self.host=host;self.url=f'http://127.0.0.1:{port}';self.console_logs=console;self.capture_requests=0;self.proc=None;self.dmon=None;self.log_follower=None;self.monitor_recorder=None;self.budgeted=False
 def __enter__(self):
  if self.path.exists():raise RuntimeError('Refuse overwriting existing attempt '+str(self.path))
  for d in ['raw','logs','telemetry']:(self.path/d).mkdir(parents=True,exist_ok=True)
  cfg=self.cfg;cfg.update(log=str(self.path/'logs/engine.log'),host=self.host,port=self.port)
  actual=hashlib.sha256(pathlib.Path(cfg['exe']).resolve().read_bytes()).hexdigest()
  if actual!=cfg['binary_sha256']:raise RuntimeError('Binary SHA mismatch')
  head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['cwd'],text=True).strip()
  if head!=cfg['source_sha']:raise RuntimeError('Source SHA mismatch')
  if subprocess.check_output(['git','status','--porcelain'],cwd=cfg['cwd'],text=True).strip():raise RuntimeError('Frozen source dirty')
  if psutil.virtual_memory().available<110*1024**3:raise RuntimeError('Q4 full arena requires110GiB available before start')
  if subprocess.check_output(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader'],text=True).strip():raise RuntimeError('Conflicting GPU compute process')
  # Also refuse stale/other Strata servers using no GPU yet.
  for p in psutil.process_iter(['pid','cmdline']):
   try:
    words=p.info['cmdline'] or []
    if p.pid!=os.getpid() and any(x in ['-m','--engine'] for x in words) and ('serve.server' in words or ('strata' in words and '--engine' in words)):raise RuntimeError('Conflicting Strata frontend PID'+str(p.pid))
   except (psutil.NoSuchProcess,psutil.AccessDenied):pass
  with socket.socket() as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind((self.host,self.port))
  save(self.path/'config.json',cfg);print('BINARY',str(pathlib.Path(cfg['exe']).resolve()),actual,'SOURCE',head,flush=True);print('RESOLVED_CONFIG',json.dumps(cfg),flush=True)
  env={k:v for k,v in os.environ.items() if not k.startswith('STRATA_')};env.update(cfg['env']);env['STRATA_RESEARCH_OUTPUT_IDS']=str(self.path/'raw/output-ids')
  cmd=[cfg['python'],cfg['server_entrypoint'],'--engine','strata','--config',str(self.path/'config.json'),'--host',self.host,'--port',str(self.port)]
  self.out=(self.path/'logs/server.log').open('x');start=time.monotonic()
  self.proc=subprocess.Popen(cmd,cwd=cfg['cwd'],env=env,stdout=self.out,stderr=subprocess.STDOUT,start_new_session=True);self.created=psutil.Process(self.proc.pid).create_time()
  record={'pid':self.proc.pid,'create_time':self.created,'attempt':str(self.path),'command':cmd,'environment':cfg['env']};save(self.C/'owned-process.json',record);save(self.path/'process.json',record)
  self.dmonout=(self.path/'telemetry/pcie-dmon.log').open('x');self.dmon=subprocess.Popen(['nvidia-smi','dmon','-i','0,1','-s','t','-d','1','-o','DT'],stdout=self.dmonout,stderr=subprocess.STDOUT)
  save(self.path/'collector-process.json',{'pid':self.dmon.pid,'create_time':psutil.Process(self.dmon.pid).create_time(),'command':['nvidia-smi','dmon','-i','0,1','-s','t','-d','1','-o','DT'],'owner_attempt':str(self.path)})
  try:
   if self.console_logs:
    (self.path/'logs/engine.log').touch();print('LOGS',self.path/'logs',flush=True);self.log_follower=subprocess.Popen(['tail','-n','+1','-f','--sleep-interval=0.2',str(self.path/'logs/server.log'),str(self.path/'logs/engine.log')])
   with Sampler(self,self.path/'telemetry/startup.jsonl') as sampler:
    until=time.monotonic()+300;heartbeat=time.monotonic()
    while time.monotonic()<until:
     if time.monotonic()-heartbeat>=15:print('STARTUP_PROGRESS',self.proc.pid,round(time.monotonic()-start,1),flush=True);heartbeat=time.monotonic()
     h=api(self.url,'/health')
     if h and h.get('loaded') and h.get('status')=='ok':break
     if self.proc.poll() is not None:raise RuntimeError('Server exited '+str(self.proc.returncode))
     if sampler.abort:raise RuntimeError(sampler.abort)
     time.sleep(1)
    else:raise RuntimeError('Startup timeout')
   metrics=api(self.url,'/metrics');e=metrics['engine']
   assert e['max_context']==cfg['max_total_context'],e
   text=(self.path/'logs/engine.log').read_text(errors='replace');self.engine_commands=[]
   for p in psutil.Process(self.proc.pid).children(recursive=True):
    if pathlib.Path(p.exe()).resolve()==pathlib.Path(cfg['exe']).resolve():self.engine_commands.append(p.cmdline())
   assert len(self.engine_commands)==1,'wrong/no/multiple engine binary'
   command=self.engine_commands[0];resolved={}
   for key in ['--pool-workers','--spec','--spec-min-p','--kv','--kv-resident','--prefill','--suffix-draft','--prompt-cache','--max-context']:
    assert key in command,key;resolved[key]=command[command.index(key)+1]
   assert resolved=={'--pool-workers':'15','--spec':'4','--spec-min-p':'0.5','--kv':'int8','--kv-resident':'32768','--prefill':'auto','--suffix-draft':'0','--prompt-cache':'0','--max-context':str(cfg['max_total_context'])},resolved
   assert e.get('model') in (None,cfg['model_name']);assert '0.1.39' in text or '0.1.39' in json.dumps(metrics), 'startup version not verified'
   save(self.path/'raw/engine-commands.json',self.engine_commands)
   resource={'engine':e,'resolved_options':resolved,'primary_slots':e.get('expert_slots_primary'),'helper_or_stage1_slots':e.get('expert_slots',0)-e.get('expert_slots_primary',0),'cache_MiB_primary':e.get('expert_cache_primary_mib'),'cache_MiB_total':e.get('expert_cache_mib'),'initial_overlap':0 if '--expert-cache-device1' in cfg['args'] else 0,'overlap_evidence':'Startup source excludes primary-owned pairs and claimed pairs from helper; layer split owns disjoint layer sets. Actual per-expert IDs unavailable on frozen speed binary.','overlap_after_warmup':None,'overlap_after_run3':None,'initial_resident_count':e.get('expert_slots'),'version_verified':'0.1.39','pool_spin_us':cfg['env'].get('STRATA_POOL_SPIN_US','DEFAULT_UNSET')}
   split=re.search(r'layer split: CUDA0 runs layers 0-(\d+)',text);resource['split_K']=int(split[1])+1 if split else None
   resource['cache_GiB_reported']={m[1]:float(m[2]) for m in re.finditer(r'CUDA(\d).*?(?:expert cache.*?\(|additional experts, )(\d+\.\d+) GiB',text)}
   save(self.path/'raw/resource-check.json',resource);save(self.path/'raw/startup.json',{'cold_start_s':time.monotonic()-start,'health':h,'metrics':metrics,'telemetry':sampler.summary()})
   print('READY',self.variant,self.profile,round(time.monotonic()-start,2),'RESOURCE',json.dumps(resource),flush=True)
   return self
  except BaseException:self.__exit__();raise
 def request(self,name,label,kind='measured',manifest_path=None):
  r=super().request(name,label,kind,manifest_path or self.C/'inputs/manifest.json')
  p=self.path/'raw'/f'{label}-engine.log';text=p.read_text(errors='replace') if p.exists() else ''
  off=re.search(r'; (\d+) more read by the GPU over PCIe or from another GPU \(([\d.]+)% of all (\d+) routed\)',text)
  if off:r.update(nonlocal_gpu_entries=int(off[1]),nonlocal_gpu_share_pct=float(off[2]),all_routed_entries=int(off[3]))
  elif r.get('local_vram_entries') is not None:r.update(nonlocal_gpu_entries=0,nonlocal_gpu_share_pct=0,all_routed_entries=r['local_vram_entries']+r['cpu_fallback_entries'])
  if r.get('all_routed_entries'):
   r['local_vram_share_all_pct']=100*r['local_vram_entries']/r['all_routed_entries'];r['cpu_share_all_pct']=100*r['cpu_fallback_entries']/r['all_routed_entries']
  r['remote_counters']=[{'device':int(m[1]),'entries':int(m[2]),'layer_launches':int(m[3]),'returned_MiB':float(m[4]),'full_row_MiB':float(m[5])} for m in re.finditer(r'CUDA(\d): (\d+) expert entries, (\d+) active layer launches, ([\d.]+) MiB returned.*?([\d.]+) MiB',text)]
  r['stage_timings']=[{'stage':int(m[1]),'windows_cumulative':int(m[2]),'GPU_wait_ms_cumulative_mean':float(m[3]),'pool_plan_ms_cumulative_mean':float(m[4]),'host_staging_ms_cumulative_mean':float(m[5]),'commit_ms_cumulative_mean':float(m[6])} for m in re.finditer(r'stage (\d): (\d+) windows; per window: wait for the GPU ([\d.]+) ms, pool \+ plan ([\d.]+) ms, host staging ([\d.]+) ms, commit ([\d.]+) ms',text)]
  r['expert_tier_counters']=[{'RAM_blobs_cumulative':int(m[1]),'file_blobs_cumulative':int(m[2]),'file_MB_cumulative':float(m[3])} for m in re.finditer(r'since the start RAM (\d+) blobs, files (\d+) blobs ([\d.]+) MB',text)]
  r['unavailable_counters']=['per-thread pool sleep/wake counts','per-expert cache overlap after adaptation','mapped-RAM vs remote breakdown if aggregate only','expert logical reads separated into PP/decode if cumulative only']
  r['actual_engine_input_verified']=r.get('actual_engine_input',{}).get('sha256')==r['payload']['input_ids_sha256']
  if r['state']=='VALID' and not r['actual_engine_input_verified']:r['state']='INVALID_PROTOCOL';r['invalid_reasons'].append('ACTUAL_ENGINE_ID_HASH_MISMATCH')
  save(self.path/'raw'/f'{label}.json',r);return r

def config(C,profile,method,K='auto',pcie='.28'):
 c=load(C/'configs/base.json');limits={'32k':32768,'128k':131072,'256k':262144};c.update(max_total_context=limits[profile],method=method);option(c,'--max-context',limits[profile]);option(c,'--pcie-frac',pcie)
 if method=='layer-split':c.update(gpu=[0,1],layer_split=str(K))
 else:
  c.update(gpu=0);c.pop('layer_split',None);option(c,'--expert-cache-device1','auto')
  if method=='optimized-helper':c['args'].append('--remote-expert-opt')
 return c

def point(C,cfg,profile,path,n=1,kind='exploratory'):
 if path.exists():
  if (path/'results.json').exists():return load(path/'results.json')
  raise RuntimeError('Incomplete preserved attempt; diagnose and version a repair, do not overwrite '+str(path))
 with Q4Session(C,cfg,path,profile) as s:
  resource=load(path/'raw/resource-check.json')
  if kind=='measured' and cfg['method'] in ['original-helper','optimized-helper']:
   other='optimized-helper' if cfg['method']=='original-helper' else 'original-helper';ref=C/'raw'/other/profile/'raw/resource-check.json'
   if ref.exists():
    ref=load(ref);assert (resource['primary_slots'],resource['helper_or_stage1_slots'])==(ref['primary_slots'],ref['helper_or_stage1_slots']),'HELPER_STARTUP_CAPACITY_MISMATCH'
  warm=s.request('warmup','warmup','warmup')
  if warm['state']!='VALID':raise RuntimeError('Warmup invalid; preserve and diagnose')
  results=[]
  for i in range(1,n+1):
   r=s.request(f'{profile}-run{i}',f'run{i}',kind)
   results.append(r);save(path/'partial-results.json',results)
   if r['state']!='VALID':raise RuntimeError('Invalid fixed-length request; preserve and diagnose before proceeding')
  save(path/'results.json',results)
 return results

def screen(C):
 auto=config(C,'32k','layer-split',pcie='.28');status(C,'EXPLORATORY',running='auto32K/.28',next_exact_action='complete auto4096 and inspect K/capacities')
 r=point(C,auto,'32k',C/'exploratory/LS-auto-pcie028');K=load(C/'exploratory/LS-auto-pcie028/raw/resource-check.json')['split_K'];assert K
 candidates=[('LS-auto-pcie028',K,'.28',r[0])]
 for label,k,p in [('LS-minus2-pcie028',K-2,'.28'),('LS-plus2-pcie028',K+2,'.28'),('LS-autoK-pcie037',K,'.37')]:
  status(C,'EXPLORATORY',running=label,next_exact_action='one warmup plus one4096 exploratory, no additional repeats')
  cfg=config(C,'32k','layer-split',k,p);save(C/'configs'/f'{label}.json',cfg);r=point(C,cfg,'32k',C/'exploratory'/label);candidates.append((label,k,p,r[0]))
 # Workload-aligned request wall includes both PP and4096 decode. All exact inputs equal.
 best=min(candidates,key=lambda t:t[3]['wall_s']);selection={'scope':'single bounded exploratory request per candidate, no final ranking','K':best[1],'pcie_frac':best[2],'choice':best[0],'criterion':'minimum full4096 request wall; differences below3% prefer auto-K/.28','candidates':[{'label':x[0],'K':x[1],'pcie_frac':x[2],'PP':x[3]['PP'],'TG':x[3]['TG'],'wall_s':x[3]['wall_s']} for x in candidates]}
 if candidates[0][3]['wall_s']<=best[3]['wall_s']*1.03:selection.update(K=K,pcie_frac='.28',choice=candidates[0][0])
 save(C/'analysis/layer-selection.json',selection)
 for profile in ['32k','128k','256k']:
  for method in ['layer-split','original-helper','optimized-helper']:
   cfg=config(C,profile,method,selection['K'],selection['pcie_frac'] if method=='layer-split' else '.28');save(C/'configs'/f'{method}-{profile}.json',cfg)
 status(C,'READY_FINAL',running=None,completed=['runtime/model/input provenance','bounded Q4 layer screening','frozen final configs'],next_exact_action='final matrix; one fresh server + fixed warmup +3 measured per cell')

def matrix(C):
 assert (C/'analysis/layer-selection.json').exists()
 # Rotate strategy order across context sizes to reduce chronology confounding.
 orders={'32k':['layer-split','original-helper','optimized-helper'],'128k':['original-helper','optimized-helper','layer-split'],'256k':['optimized-helper','layer-split','original-helper']}
 for profile,methods in orders.items():
  for method in methods:
   status(C,'FINAL_MATRIX',running=f'{method}/{profile}',next_exact_action='finish this cell: fixed warmup + at most3valid measured')
   cfg=load(C/'configs'/f'{method}-{profile}.json');point(C,cfg,profile,C/'raw'/method/profile,3,'measured')
   paths=list((C/'raw').glob('*/*/results.json'));status(C,'FINAL_MATRIX',running=None,completed_cells=[str(p.parent.relative_to(C/'raw')) for p in paths],valid_final_requests=sum(len(load(p)) for p in paths),next_exact_action='next frozen cell')
 status(C,'MATRIX_COMPLETE',running=None,pending=['analysis','safe winner launchers','reproducibility audit','GPU cleanup'],next_exact_action='derive medians and system phases from preserved raw data')

def manual(C,profile,host,port):
 cfg=load(C/'launchers'/f'{profile}.json');path=C/'manual'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
 stopping=False
 def stop(*a):
  nonlocal stopping;stopping=True
 signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
 with Q4Session(C,cfg,path,profile,port,host,True) as s:
  from record_ui_metrics import MonitorRecorder
  monitor=MonitorRecorder(s.url,path/'telemetry/ui-monitor',s.proc.pid,s.created,path/'config.json').start()
  print('HTTP',f'http://{host}:{port}','UI_MONITOR_LOGS',path/'telemetry/ui-monitor',flush=True)
  try:
   while not stopping and s.proc.poll() is None:
    if psutil.virtual_memory().available<12*1024**3:raise RuntimeError('RAM_ABORT')
    time.sleep(1)
  finally:monitor.close()

def main():
 a=argparse.ArgumentParser();a.add_argument('--campaign',type=pathlib.Path,required=True);a.add_argument('action',choices=['screen','matrix','start','stop']);a.add_argument('--profile',choices=['32k','128k','256k']);a.add_argument('--host',default='127.0.0.1');a.add_argument('--port',type=int,default=8080);a.add_argument('--check',action='store_true');v=a.parse_args();C=v.campaign
 try:
  if v.action=='screen':screen(C)
  elif v.action=='matrix':matrix(C)
  elif v.action=='start':
   if v.check:
    cfg=load(C/'launchers'/f'{v.profile}.json');cfg.update(host=v.host,port=v.port)
    assert hashlib.sha256(pathlib.Path(cfg['exe']).resolve().read_bytes()).hexdigest()==cfg['binary_sha256']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['cwd'],text=True).strip()==cfg['source_sha']
    for s in load(cfg['model_manifest'])['shards']:assert pathlib.Path(s['path']).stat().st_size==s['bytes']
    print('RESOLVED_CONFIG',json.dumps(cfg,indent=2));print('CHECK PASS; no server started',flush=True)
   else:manual(C,v.profile,v.host,v.port)
  else:
   p=C/'owned-process.json'
   if p.exists():r=load(p);owned_stop(r['pid'],r['create_time'])
 except BaseException as e:
  if v.action in ['screen','matrix']:status(C,'NEEDS_DIAGNOSIS',error=repr(e),next_exact_action='inspect preserved failing attempt; repair protocol/config without changing engine')
  raise
if __name__=='__main__':main()
