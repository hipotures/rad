#!/usr/bin/env python3
import sys,json,os,time,signal,subprocess,uuid,re,statistics,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parent; BASE=ROOT.parent
BASE=ROOT  # isolated campaign support module and output paths
import campaign as c
from telemetry import Sampler,capture_pss
c.Sampler=Sampler
c.BASE=ROOT/'configs';c.RESULTS=ROOT;c.URL='http://127.0.0.1:18086'
SEED=json.loads((ROOT/'configs/resident-baseline-seed.json').read_text())
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=c.REPO,text=True).strip()
assert HEAD=='c499bd102e7a4135c0de389dcfe38c399759ccc8'
assert not Path('/srv/ai/models/strata/packs/ud-q4_k_xl/experts.bin').exists()

_ORIGINAL_SAVE=c.save
ACTIVE_CONFIG=None
MODEL_REVISION='38bb39ee97821de2c9009abb7e93950eec396e66'
def provenance_save(path,data):
 path=Path(path)
 if path.parent==ROOT/'raw' and isinstance(data,dict) and not any(path.name.endswith(x) for x in ['-request.json','-stream.json','-official-config.json','-metrics.json','-status.json']):
  data=dict(data)
  data.update(Strata_HEAD=HEAD,Strata_version='0.1.32',build_variant='default',model_revision=MODEL_REVISION)
  if ACTIVE_CONFIG is not None:
   data['full_config']=copy.deepcopy(ACTIVE_CONFIG)
   data['full_engine_command']=[ACTIVE_CONFIG['exe'],'--serve',*ACTIVE_CONFIG['args']]+(['--layer-split',str(ACTIVE_CONFIG['layer_split'])] if ACTIVE_CONFIG.get('layer_split') else [])
   data['topology']='layer_split' if ACTIVE_CONFIG.get('layer_split') else 'single_gpu_resident' if '--resident-budget-gib' in ACTIVE_CONFIG['args'] else 'full_arena'
 _ORIGINAL_SAVE(path,data)
c.save=provenance_save

def setarg(args,k,v):
 a=list(args)
 if k in a:
  i=a.index(k);del a[i:i+2]
 if v is not None:a += [k,str(v)]
 return a

def config(label,topology='arena1',split=None,context=65536,**options):
 cfg=copy.deepcopy(SEED);a=cfg['args']
 if topology!='resident1':a=setarg(a,'--resident-budget-gib',None)
 cfg.pop('layer_split',None);cfg.pop('gpu',None)
 if topology=='split':cfg.update(gpu=[0,1],layer_split=str(split or 'auto'))
 elif topology!='helper':cfg['gpu']=0
 a=setarg(a,'--max-context',context)
 for key,val in options.items():a=setarg(a,'--'+key.replace('_','-'),val)
 cfg.update(args=a,port=18086,log=str(ROOT/'logs'/f'{label}-engine.log'))
 c.save(ROOT/'configs'/f'{label}.json',cfg)
 return cfg

class Session:
 def __init__(self,label,cfg):
  global ACTIVE_CONFIG
  ACTIVE_CONFIG=copy.deepcopy(cfg)
  self.label=label;self.cfg=cfg;self.proc=None
  self.run=c.Campaign(ROOT/'configs'/f'{label}.json',label)
  self.run.log=Path(cfg['log']);self.run.cfg['log']=str(self.run.log);c.save(self.run.config,self.run.cfg)
 def __enter__(self):
  assert c.psutil.virtual_memory().available>=100*c.GIB,'Insufficient MemAvailable before full-arena startup'
  env=dict(os.environ,CUDA_VISIBLE_DEVICES='0,1' if self.cfg.get('gpu')==[0,1] or '--expert-cache-device1' in self.cfg['args'] else '0',STRATA_SPLIT_TIMING='1',STRATA_DECODE_TIMING='1')
  cmd=[str(c.REPO/'.venv/bin/python'),'-m','serve.server','--engine','strata','--config',str(self.run.config),'--host','127.0.0.1','--port','18086']
  self.output=(ROOT/'logs'/f'{self.label}-server.log').open('w');t=time.monotonic()
  self.dmon_log=(ROOT/'telemetry'/f'{self.label}-pcie-dmon.log').open('w')
  self.dmon=subprocess.Popen(['nvidia-smi','dmon','-i','0,1','-s','t','-d','1','-o','DT'],stdout=self.dmon_log,stderr=subprocess.STDOUT)
  self.proc=subprocess.Popen(cmd,cwd=c.REPO,env=env,stdout=self.output,stderr=subprocess.STDOUT,start_new_session=True);self.run.pid=self.proc.pid
  c.save(ROOT/'live.json',{'pid':self.proc.pid,'label':self.label,'command':cmd,'started':time.time()})
  try:
   with c.Sampler(self.proc.pid,f'{self.label}-startup') as s:
    while time.monotonic()-t<1800:
     h=c.api('/health')
     if isinstance(h,dict) and h.get('loaded') and h.get('status')=='ok':break
     if self.proc.poll() is not None:raise RuntimeError(f'Engine exited {self.proc.returncode}')
     if s.abort:raise RuntimeError(s.abort)
     time.sleep(1)
    else:raise RuntimeError('Startup timeout')
   c.save(ROOT/'raw'/f'{self.label}-startup.json',{'cold_start_s':time.monotonic()-t,'health':h,'metrics':c.api('/metrics'),'telemetry':s.summary()})
   capture_pss(self.proc.pid)  # outside PP/TG/TTFT timer; startup duration was already saved
   print(self.label,'READY',round(time.monotonic()-t,2),flush=True)
   return self
  except BaseException:
   self.__exit__();raise
 def __exit__(self,*args):
  if self.proc and self.proc.poll() is None:
   os.killpg(self.proc.pid,signal.SIGTERM)
   try:self.proc.wait(timeout=25)
   except subprocess.TimeoutExpired:os.killpg(self.proc.pid,signal.SIGKILL);self.proc.wait()
  if hasattr(self,'dmon'):
   self.dmon.terminate()
   try:self.dmon.wait(timeout=3)
   except subprocess.TimeoutExpired:self.dmon.kill();self.dmon.wait()
   self.dmon_log.close()
  if hasattr(self,'output'):self.output.close()
  time.sleep(2)
 def request(self,target=63400,output=256,tag='measure',kind='candidate'):
  name=f'{self.label}-{tag}';messages,count,_=self.run.exact_prompt(target,uuid.uuid4().hex)
  assert count+output+16<=int(self.cfg['args'][self.cfg['args'].index('--max-context')+1])
  pss_before=capture_pss(self.proc.pid)  # expensive smaps walk occurs before client/engine request clocks
  original_stream=c.upstream.post_stream;client_times={}
  def timed_stream(*args,**kwargs):
   result=original_stream(*args,**kwargs)
   client_times.update(t_start_monotonic_s=result['t_start'],t_first_monotonic_s=result['t_first'],t_end_monotonic_s=result['t_end'])
   return result
  c.upstream.post_stream=timed_stream
  try:rec=self.run.request(messages,output,name,kind,str(target))
  finally:c.upstream.post_stream=original_stream
  rec.update(client_times)
  pss_after=capture_pss(self.proc.pid)
  rec.update(pss_before=pss_before,pss_after=pss_after,pss_note='smaps snapshots outside timed request; cached PSS in1Hz telemetry has timestamp')
  assert rec['generated_tokens']==output,'Unexpected early EOS in fixed-length speed request'
  rec.update(candidate=self.label,config=str(ROOT/'configs'/f'{self.label}.json'))
  c.save(ROOT/'raw'/f'{name}.json',rec)
  if rec['generated_tokens']<output:print('EARLY EOS',name,rec['generated_tokens'],flush=True)
  return rec

def candidate(label,cfg,repeats=1,warmup=False,smoke=True):
 done=ROOT/'raw'/f'{label}-done.json'
 if done.exists():return json.loads(done.read_text())
 recs=[]
 try:
  with Session(label,cfg) as s:
   if smoke:
    r=s.request(8000,64,'smoke','smoke')
    assert r['text'].strip() and r['draft_tokens']>0
   if warmup:s.request(63400,256,'warmup','warmup')
   for n in range(repeats):recs.append(s.request(tag=f'run{n+1}'))
  result={'candidate':label,'status':'OK','runs':recs,'median_tg':statistics.median(r['tg_tps'] for r in recs),'median_pp':statistics.median(r['pp_tps'] for r in recs)}
 except Exception as e:
  log=(ROOT/'logs'/f'{label}-engine.log').read_text(errors='replace') if (ROOT/'logs'/f'{label}-engine.log').exists() else ''
  result={'candidate':label,'status':'UNSUPPORTED_BY_CURRENT_UPSTREAM' if any(x in log for x in ['does not support','needs --','requires --']) else 'FAIL','error':repr(e),'runs':recs}
 c.save(done,result);print('DONE',label,result['status'],result.get('median_tg'),flush=True);return result

if __name__=='__main__':
 phase=sys.argv[1] if len(sys.argv)>1 else 'phase1'
 if phase=='phase1':
  candidate('T2-auto',config('T2-auto','split'),3,True)
  candidate('T1-arena',config('T1-arena'),3,True)
  candidate('T0-control',config('T0-control','resident1'),1,False)
 else:raise SystemExit('Unknown phase')
