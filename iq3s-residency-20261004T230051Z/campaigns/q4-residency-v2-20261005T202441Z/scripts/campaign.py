"""Bounded Q4-only sessions; actual native identity, no inherited flags, owned cleanup."""
from pathlib import Path
import argparse, copy, datetime, hashlib, json, os, signal, subprocess, time
import psutil
import lab
from q4_multigpu import Q4Session, option
C=Path(__file__).resolve().parents[1]
R=C.parents[1]
def load(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,indent=2)+'\n')
def status(state,**extra):
 s=load(C/'STATUS.json');s.update(state=state,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra);save(C/'STATUS.json',s)
 (C/'STATUS.md').write_text('# Q4 Residency v2\n\n```json\n'+json.dumps(s,indent=2)+'\n```\n')
def guard():
 d=load(C/'deadline.json')
 if time.time()>=d['experiment_cutoff_epoch']:raise RuntimeError('EXPERIMENT_CUTOFF: consolidate, do not start substantial work')
 lab.deadline=lambda:d['deadline_epoch']
class V2Session(Q4Session):
 def __enter__(self):
  guard()
  try:
   result=super().__enter__();self.budgeted=True
   children=[p for p in psutil.Process(self.proc.pid).children(recursive=True) if Path(p.exe()).resolve()==Path(self.cfg['exe']).resolve()]
   assert len(children)==1
   native=children[0];env=native.environ()
   assert env.get('CUDA_VISIBLE_DEVICES')=='0,1' and env.get('STRATA_POOL_SPIN_US')=='100'
   expected=self.cfg['env'];observed={k:v for k,v in env.items() if k.startswith('STRATA_') or k=='CUDA_VISIBLE_DEVICES'}
   assert all(observed.get(k)==v for k,v in expected.items())
   allowed=set(expected)|{'STRATA_RESEARCH_OUTPUT_IDS'}
   assert set(observed)<=allowed,('Unexpected inherited experiment flags',observed)
   command=native.cmdline();assert command[command.index('--layer-split')+1]=='24'
   save(self.path/'raw/native-process.json',{'pid':native.pid,'create_time':native.create_time(),'executable':native.exe(),'command':command,'effective_environment':observed})
   return result
  except BaseException:self.__exit__();raise
def prepare_episodes():
 src=R/'src/control';sys_path=[str(src),str(src/'tools')]
 import sys
 sys.path[:0]=sys_path
 import strata_tokenizer as ST
 from serve.frontend import ChatTemplate
 from serve.server import Service
 cfg=load(C/'configs/control-32k.json');voc=Path(cfg['tokenizer']);v=load(voc/'vocab.json');tokens=[None]*len(v)
 for token,index in v.items():tokens[index]=token
 svc=Service.__new__(Service);svc.tok=ST.Tokenizer(tokens,(voc/'merges.txt').read_text().split('\n'),load(voc/'token_type.json'));svc.template=ChatTemplate(voc/'chat_template.jinja');svc.effort_end=False
 manifest=load(C/'inputs/manifest.json');names=['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math']
 for name in names:
  source=R/'workloads'/f'{name}.json';p=load(source);p['model']=cfg['model_name']
  ids=svc.encode_prompt(p['messages'],None,{'enable_thinking':False});raw=json.dumps(ids,separators=(',',':')).encode();sha=hashlib.sha256(raw).hexdigest()
  path=C/'inputs'/f'{name}.json';save(path,p);ip=C/'inputs/token-ids'/f'{sha}.json';ip.write_bytes(raw)
  manifest['payloads'][name]={'path':str(path),'payload_sha256':lab.hashjson(p),'messages_sha256':lab.hashjson(p['messages']),'input_ids_sha256':sha,'token_ids_path':str(ip),'actual_input_tokens':len(ids),'source_payload':str(source),'split':name.split('-')[0],'output':p['max_tokens'],'provenance':'Prior independent tasks, now tokenized and traced with Q4. No nonce-derived training episodes.'}
 save(C/'inputs/manifest.json',manifest)
 save(C/'datasets/splits.json',{'development':['dev-code','dev-math'],'calibration':['cal-prose'],'holdout':['hold-code','hold-structured','hold-math'],'unit':'complete independent task/episode; adjacent windows are never a held-out split','coverage_limitation':'Six short task instructions with1024-token budget; no broad document/translation generalization claim','primary_benchmark':'32k/128k/256k repository payloads excluded from predictor training'})
def point(variant,profile,rep=1,diagnostic=False,payload=None):
 guard();cfg=load(C/'configs'/f'{variant}-{profile}.json');payload=payload or f'{profile}-run{rep}'
 path=C/('traces' if diagnostic else 'raw')/variant/profile/(payload if diagnostic else f'rep{rep}')
 if path.exists():
  if (path/'results.json').exists():return load(path/'results.json')
  raise RuntimeError('Existing unfinished attempt; preserve and explicitly repair, never overwrite '+str(path))
 if diagnostic:cfg['env']['STRATA_LAB_TRACE']=str(path/'trace')
 status('RUNNING',phase='A' if diagnostic else 'control',running={'variant':variant,'profile':profile,'payload':payload},next_exact_action='fresh process, fixed64-output warmup, one serial request')
 with V2Session(C,cfg,path,profile,port=18136) as s:
  warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID' and warm['actual_output_tokens']==64
  rec=s.request(payload,'run','diagnostic' if diagnostic else 'measured')
  if not diagnostic:assert rec['state']=='VALID',rec
  else:assert rec['actual_engine_input_verified'] and rec['reuse']==0,rec
  save(path/'results.json',{'runs':[rec],'warmup':warm,'headline':not diagnostic,'trace_prefix':str(path/'trace-request2') if diagnostic else None})
 print('PROGRESS',variant,profile,payload,rec['state'],rec.get('actual_output_tokens'),rec.get('TG'),flush=True)
 return rec
def phase_a():
 prepare_episodes()
 # Missing fresh-start256K control only;32/128 latest pool controls are preserved.
 point('control','256k',1)
 for profile in ['32k','128k','256k']:point('diagnostic',profile,1,True)
 for payload in ['dev-code','dev-math','cal-prose','hold-code','hold-structured','hold-math']:
  point('diagnostic','32k',1,True,payload)
 status('A_TRACES_COLLECTED',phase='A',running=None,next_exact_action='Validate observed-current replay/counters/slots, measure costs and headroom')
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['phase-a','point']);a.add_argument('--variant',default='control');a.add_argument('--profile',choices=['32k','128k','256k'],default='32k');a.add_argument('--rep',type=int,default=1);a.add_argument('--diagnostic',action='store_true');a.add_argument('--payload');args=a.parse_args()
 def stop(*_):raise KeyboardInterrupt('Owned campaign interrupted; preserve evidence')
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 if args.action=='phase-a':phase_a()
 else:point(args.variant,args.profile,args.rep,args.diagnostic,args.payload)
if __name__=='__main__':main()
