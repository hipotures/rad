"""Experimental Q4 capture/replay only; fixed warmup, owned fresh server and finite deadlines."""
from pathlib import Path
import argparse,json,time,datetime,hashlib,signal,psutil,os
import lab
from q4_multigpu import Q4Session
C=Path(__file__).resolve().parents[1];R=C.parents[1]
def load(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,indent=2)+'\n')
def guard():
 d=load(C/'deadline.json');assert time.monotonic()<d['experiment_cutoff_monotonic'],'New experiments forbidden after absolute cutoff';lab.deadline=lambda:d['deadline_epoch']
def status(state,**kw):
 s=load(C/'STATUS.json');s.update(state=state,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw);save(C/'STATUS.json',s);(C/'STATUS.md').write_text('# Q4 live oracle\n\n```json\n'+json.dumps(s,indent=2)+'\n```\n')
def config(profile,variant='replay-v1'):
 cfg=load(C/'configs'/f'control-{profile}.json')
 if variant!='control':
  i=load(C/'git'/f'{variant}-identity.json');cfg.update(exe=i['exe'],cwd=i['source'],source_sha=i['source_sha'],Strata_HEAD=i['source_sha'],binary_sha256=i['binary_sha256'],build_variant=variant)
 return cfg
class Session(Q4Session):
 def __enter__(self):
  guard()
  try:
   result=super().__enter__();self.budgeted=True
   p=[p for p in psutil.Process(self.proc.pid).children(recursive=True) if Path(p.exe()).resolve()==Path(self.cfg['exe']).resolve()];assert len(p)==1
   env={k:v for k,v in p[0].environ().items() if k.startswith('STRATA_') or k=='CUDA_VISIBLE_DEVICES'}
   assert all(env.get(k)==v for k,v in self.cfg['env'].items())
   save(self.path/'raw/native-process.json',{'pid':p[0].pid,'created':p[0].create_time(),'executable':p[0].exe(),'command':p[0].cmdline(),'environment':env,'cpu_affinity':p[0].cpu_affinity(),'system_load':os.getloadavg()})
   return result
  except BaseException:self.__exit__();raise

def point(profile,mode,label,payload,variant='replay-v1',tape=None,oracle='off',strategy='deadline',horizon=64,direct=False,check=False):
 guard();path=C/'raw'/label;assert not path.exists(),'Immutable attempt already exists';cfg=config(profile,variant)
 if mode in ['record','replay']:
  tape=Path(tape).resolve() if tape else C/'tapes'/f'{label}.bin'
  cfg['env'].update(STRATA_Q4_TAPE=str(tape),STRATA_Q4_TAPE_MODE=mode,STRATA_Q4_TAPE_REQUEST='2',STRATA_Q4_TAPE_OBSERVATIONS=str(path/'raw/observations.bin'))
 if variant.startswith('oracle'):
  cfg['env'].update(STRATA_Q4_ORACLE_SUBSTRATE='1',STRATA_Q4_ORACLE_LOG=str(path/'raw/oracle'),STRATA_Q4_ORACLE_MODE=oracle,STRATA_Q4_ORACLE_STRATEGY=strategy,STRATA_Q4_ORACLE_HORIZON=str(horizon))
  if direct:cfg['env']['STRATA_Q4_ORACLE_DIRECT']='1'
  if check:cfg['env']['STRATA_Q4_ORACLE_CHECK']='1'
 cfg['headline_instrumentation']='Common buffered fixed-work tape and routing observations; cost measured against natural mode'
 cfg['variant_overrides']={'experiment_mode':mode,'oracle':oracle,'strategy':strategy,'horizon':horizon if oracle=='short' else 'full','direct':direct,'actual_fixed_work_tape':str(tape) if tape else None,'normal_serving':False}
 save(C/'configs'/f'{label}.json',cfg);status('PHASE_C_LIVE_REPLAY' if mode=='replay' and variant.startswith('oracle') else 'PHASE_A_FIDELITY',error=None,running={'mode':mode,'profile':profile,'label':label},next_exact_action='fixed warmup64, one capture/replay request, owned cleanup')
 with Session(C,cfg,path,profile,port=18146) as s:
  warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID' and warm['actual_output_tokens']==64
  r=s.request(payload,'run','measured');save(path/'results.json',{'warmup':warm,'runs':[r],'mode':mode,'tape':str(tape) if tape else None,'headline':False})
  assert r['state']=='VALID' and r.get('actual_engine_input_verified'),r
  if mode in ['record','replay']:
   assert 'Q4_TAPE_END' in (path/'raw/run-engine.log').read_text(),'Missing native full tape completion'
 print('POINT_COMPLETE',label,r.get('PP'),r.get('TG'),r.get('wall_s'),flush=True)
 return r

def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['natural','record','replay']);a.add_argument('--profile',default='32k',choices=['32k','128k','256k']);a.add_argument('--label',required=True);a.add_argument('--payload',default='32k-run1');a.add_argument('--variant',default='replay-v1');a.add_argument('--tape');a.add_argument('--oracle',choices=['off','full','short'],default='off');a.add_argument('--strategy',choices=['deadline','reuse'],default='deadline');a.add_argument('--horizon',type=int,choices=[1,4,16,64],default=64);a.add_argument('--direct',action='store_true');a.add_argument('--check',action='store_true');v=a.parse_args()
 signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Finite owned timeout')))
 save(C/'logs'/f'{v.label}-driver-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'command':__import__('sys').argv,'absolute_deadline':load(C/'deadline.json')['deadline_utc']})
 try:point(v.profile,v.mode,v.label,v.payload,v.variant,v.tape,v.oracle,v.strategy,v.horizon,v.direct,v.check)
 except BaseException as e:status('REPAIR_REQUIRED',running=None,error=repr(e),next_exact_action='preserve failure; inspect minimal assumption; version repair');raise
if __name__=='__main__':main()
