"""Owned, bounded fresh sessions; immutable inputs and provenance."""
from pathlib import Path
import json,datetime,time,signal,subprocess,psutil
import lab
from q4_multigpu import Q4Session
C=Path(__file__).resolve().parents[1];R=C.parents[1];V=R/'campaigns/q4-residency-v2-20261005T202441Z'
def load(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,indent=2,default=lambda v:v.item() if hasattr(v,'item') else v.tolist())+'\n')
def guard():
 d=load(C/'deadline.json');assert time.time()<d['experiment_cutoff_epoch'],'Stop new experiments; consolidate before absolute deadline';lab.deadline=lambda:d['deadline_epoch']
def status(state,**kw):
 s=load(C/'STATUS.json');s.update(state=state,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**kw);save(C/'STATUS.json',s);(C/'STATUS.md').write_text('# Q4 conditional admission\n\n```json\n'+json.dumps(s,indent=2)+'\n```\n')
class Session(Q4Session):
 def __enter__(self):
  guard();self.variant=self.cfg['build_variant']
  try:
   result=super().__enter__();self.budgeted=True
   natives=[p for p in psutil.Process(self.proc.pid).children(recursive=True) if Path(p.exe()).resolve()==Path(self.cfg['exe']).resolve()];assert len(natives)==1
   p=natives[0];env=p.environ();expected=self.cfg['env'];observed={k:v for k,v in env.items() if k.startswith('STRATA_') or k=='CUDA_VISIBLE_DEVICES'};assert set(observed)<=set(expected)|{'STRATA_RESEARCH_OUTPUT_IDS'} and all(observed.get(k)==v for k,v in expected.items())
   assert p.cmdline()[p.cmdline().index('--layer-split')+1]=='24'
   save(self.path/'raw/native-process.json',{'pid':p.pid,'create_time':p.create_time(),'exe':p.exe(),'command':p.cmdline(),'environment':observed})
   ref=load(V/'raw/control'/self.profile/'rep1/raw/resource-check.json');actual=load(self.path/'raw/resource-check.json');assert all(actual[k]==ref[k] for k in ('primary_slots','helper_or_stage1_slots')),(actual,ref)
   return result
  except BaseException:self.__exit__();raise
def point(task,profile='32k',kind='diagnostic',variant='reason-v1',rep=1):
 guard();path=C/('traces' if kind=='diagnostic' else 'raw')/variant/profile/(task if kind=='diagnostic' else f'rep{rep}')
 if (path/'results.json').exists():return load(path/'results.json')
 assert not path.exists(),'Preserve unfinished point; explicit versioned repair required'
 cfg=load(C/'configs'/f'{variant}-{profile}.json')
 if kind=='diagnostic':cfg['env'].update(STRATA_Q4_EARLY_DIAGNOSTIC='1',STRATA_Q4_EARLY_LOG=str(path/'events'))
 status('RUNNING',phase='A/B data collection',running={'task':task,'profile':profile,'variant':variant,'kind':kind},next_exact_action='fresh server; fixed64-output warmup; one serial request; cleanup')
 with Session(C,cfg,path,profile,port=18144) as s:
  warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID' and warm['actual_output_tokens']==64
  rec=s.request(task,'run',kind);assert rec['state']!='FAILED' and rec.get('actual_engine_input_verified') and rec['reuse']==0,rec
  result={'warmup':warm,'runs':[rec],'headline':kind=='measured','event_prefix':str(path/'events-request2') if kind=='diagnostic' else None};save(path/'results.json',result)
 print('COMPLETED',variant,task,rec.get('actual_output_tokens'),rec.get('TG'),flush=True);return result
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('action',choices=['old-replay','episodes']);args=p.parse_args()
 signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Owned driver timeout/interruption')))
 save(C/'logs/data-driver-pid.json',{'pid':__import__('os').getpid(),'create_time':psutil.Process().create_time(),'timeout_s':3600,'command':__import__('sys').argv})
 if args.action=='old-replay':point('32k-run1')
 else:
  for task in load(C/'datasets/tasks.json')['episodes']:point(task['id'])
 status('DATA_COMPLETE',running=None,next_exact_action='validate reason labels/causality, freeze dev/cal gates before holdout')
if __name__=='__main__':main()
