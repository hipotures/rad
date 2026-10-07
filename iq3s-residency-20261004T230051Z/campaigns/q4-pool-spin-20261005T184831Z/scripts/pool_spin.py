"""Bounded same-binary CPU-pool experiment. No runtime code changes."""
import argparse, copy, datetime, hashlib, json, os, pathlib, signal, subprocess, time
import psutil
import lab
from lab import load, save, owned_stop
from q4_multigpu import Q4Session, manual

C=pathlib.Path(__file__).resolve().parents[1]
POLICIES=['100us','500us','2000us','default20ms']

def status(state, **kw):
 old=load(C/'STATUS.json');old.update(state=state,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw);save(C/'STATUS.json',old)
 (C/'STATUS.md').write_text('# Q4 CPU-pool comparison\n\n```json\n'+json.dumps(old,indent=2)+'\n```\n')

def verify_model(cfg, full=False):
 m=load(cfg['model_manifest'])
 for s in m['shards']:
  st=pathlib.Path(s['path']).stat();assert st.st_size==s['bytes'] and st.st_mtime_ns==s['mtime_ns'],s['path']
 for p,x in m['files'].items():
  path=pathlib.Path(p);assert path.stat().st_size==x['bytes'],p
  if full:assert hashlib.sha256(path.read_bytes()).hexdigest()==x['sha256'],p
 assert hashlib.sha256(pathlib.Path(cfg['exe']).resolve().read_bytes()).hexdigest()==cfg['binary_sha256']
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['cwd'],text=True).strip()==cfg['source_sha']
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=cfg['cwd'],text=True).strip()
 assert cfg['gpu']==[0,1] and cfg['layer_split']=='24'
 assert cfg['args'][cfg['args'].index('--pcie-frac')+1]=='.28'

class PoolSession(Q4Session):
 def __enter__(self):
  verify_model(self.cfg)
  result=super().__enter__()
  try:
   engine=[p for p in psutil.Process(self.proc.pid).children(recursive=True) if pathlib.Path(p.exe()).resolve()==pathlib.Path(self.cfg['exe']).resolve()]
   assert len(engine)==1
   env=engine[0].environ();expected=self.cfg['env'].get('STRATA_POOL_SPIN_US')
   assert env.get('STRATA_POOL_SPIN_US')==expected,(env.get('STRATA_POOL_SPIN_US'),expected)
   saved={k:v for k,v in env.items() if k.startswith('STRATA_') or k=='CUDA_VISIBLE_DEVICES'}
   save(self.path/'raw/actual-engine-environment.json',{'environment':saved,'pool_override_present':'STRATA_POOL_SPIN_US' in env,'effective_spin_us':int(expected) if expected else 20000,'source_default_ms':20})
   resource=load(self.path/'raw/resource-check.json');assert resource['split_K']==24
   key=C/'analysis'/f'resource-reference-{self.profile}.json'
   fields=['primary_slots','helper_or_stage1_slots','cache_MiB_primary','cache_MiB_total','initial_resident_count','split_K']
   if key.exists():
    ref=load(key);assert {k:resource[k] for k in fields}==ref,'CACHE_CAPACITY_MISMATCH'
   else:save(key,{k:resource[k] for k in fields})
   return result
  except BaseException:self.__exit__();raise

def matrix():
 d=load(C/'deadline.json');lab.deadline=lambda:d['deadline_epoch']
 def stop_signal(*_):raise KeyboardInterrupt('Owned driver stop requested')
 signal.signal(signal.SIGTERM,stop_signal);signal.signal(signal.SIGINT,stop_signal)
 try:
  for point in load(C/'protocol.json')['order']:
   policy,profile,rep=point['policy'],point['profile'],point['replicate'];path=C/'raw'/policy/profile/f'rep{rep}'
   if (path/'results.json').exists():continue
   if time.time()>d['no_new_sessions_after_epoch']:raise RuntimeError('REPORTING_CUTOFF: no new server starts')
   status('RUNNING',current=point,next_exact_action='fresh start, identical64-output warmup, one4096 measured request')
   cfg=load(C/'configs'/f'{policy}-{profile}.json')
   with PoolSession(C,cfg,path,profile,port=18135) as s:
    s.budgeted=True
    warm=s.request('warmup','warmup','warmup')
    assert warm['state']=='VALID' and warm['actual_output_tokens']==64,'Warmup invalid: preserve/diagnose'
    r=s.request(f'{profile}-run{rep}','measured','measured')
    r.update(spin_policy=policy,replicate=rep)
    save(path/'raw/measured.json',r)
    if r['state']!='VALID':raise RuntimeError('Measured request invalid; preserved; diagnose before versioned repair')
    save(path/'results.json',[r])
   count=len(list((C/'raw').glob('*/*/rep*/results.json')))
   status('RUNNING',current=None,valid_measured_requests=count,next_exact_action='next predeclared paired fresh-start point')
   print('PROGRESS',count,'/24',policy,profile,rep,'TG',r['TG'],'wall',r['wall_s'],flush=True)
  status('MATRIX_COMPLETE',current=None,pending=['parity/analysis','policy selection','report/launchers','cleanup/audit'])
 except BaseException as e:
  status('NEEDS_DIAGNOSIS',error=repr(e),next_exact_action='inspect preserved failure; no blind retry')
  raise

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['matrix','start','stop']);ap.add_argument('--profile',choices=['32k','128k']);ap.add_argument('--host',default='0.0.0.0');ap.add_argument('--port',type=int,default=8080);ap.add_argument('--check',action='store_true');a=ap.parse_args()
 if a.action=='matrix':matrix()
 elif a.action=='stop':
  p=C/'owned-process.json'
  if p.exists():r=load(p);owned_stop(r['pid'],r['create_time'])
 else:
  cfg=load(C/'launchers'/f'{a.profile}.json');verify_model(cfg)
  if a.check:
   cfg.update(host=a.host,port=a.port);print('RESOLVED_CONFIG',json.dumps(cfg,indent=2));print('CHECK PASS; no inference started')
  else:
   # Reuse preserved foreground serving and monitor recording; validate actual
   # engine environment and cache capacities in the new campaign subclass.
   import q4_multigpu
   q4_multigpu.Q4Session=PoolSession
   manual(C,a.profile,a.host,a.port)

if __name__=='__main__':main()
