"""Two diagnostic-only traces after primary matrix; reused unfiltered trace."""
from campaign import C,load,save,Session,guard,status
from live_matrix import parse_summary
from pathlib import Path
import json,os,psutil,signal
def run():
 assert load(C/'phase-c/matrix-progress.json')['completed']==18
 signal.signal(signal.SIGTERM,lambda *_:(_ for _ in ()).throw(KeyboardInterrupt('Diagnostic timeout')))
 save(C/'logs/ablations-driver-pid.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'timeout_s':1200})
 for variant in ('reactive-only','conditional'):
  guard();path=C/'diagnostics'/variant/'32k'
  if (path/'results.json').exists():continue
  assert not path.exists(),'Preserve incomplete attempt'
  cfg=load(C/'configs'/f'{variant}-32k.json');cfg['env'].update(STRATA_Q4_EARLY_DIAGNOSTIC='1',STRATA_Q4_EARLY_LOG=str(path/'events'));cfg['headline_instrumentation']='DIAGNOSTIC_ONLY buffered demand/native-change/events and canonical bytes'
  status('DIAGNOSTIC_ABLATIONS',phase='C',running=variant,next_exact_action='One fixed32K4096 diagnostic; no threshold selection or headline speed')
  with Session(C,cfg,path,'32k',port=18144) as s:
   warm=s.request('warmup','warmup','warmup');assert warm['state']=='VALID' and warm['actual_output_tokens']==64
   r=s.request('32k-run1','run','diagnostic');assert r['state']=='VALID' and r['actual_output_tokens']==4096 and r['actual_engine_output_ID_count']==4096
   save(path/'results.json',{'warmup':warm,'runs':[r],'admission':parse_summary(path/'raw/run-engine.log'),'headline':False,'trace':str(path/'events-request2')})
  print('DIAGNOSTIC_ABLATION_COMPLETE',variant,flush=True)
if __name__=='__main__':run()
