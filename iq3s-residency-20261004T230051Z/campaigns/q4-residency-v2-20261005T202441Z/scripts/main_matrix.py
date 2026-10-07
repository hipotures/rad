"""Predeclared counterbalanced primary confirmation; screening counts toward max3 attempts."""
from campaign import C,R,point,load,save,status,guard
import time,psutil,json,datetime

def main():
 assert (C/'phase-c/short-correctness.json').exists(),'Correctness evidence precedes speed'
 assert all(not x['head_nonfinite_or_worker_failure'] for x in load(C/'phase-c/short-correctness.json'))
 # Exactly3 attempts per config/profile. Existing original256rep1 is retained
 # as compatible, earlier control; chronology limitation is explicit.
 variants=['control','history-v2','early-v1']
 plan=[]
 for profile in ['32k','128k','256k']:
  for rep in [1,2,3]:
   order=variants[rep-1:]+variants[:rep-1]
   for variant in order:plan.append({'variant':variant,'profile':profile,'rep':rep,'reuse_completed':variant=='control' and profile=='256k' and rep==1})
 save(C/'phase-c/primary-plan.json',{'frozen_before_first_primary_candidate':True,'plan':plan,'protocol':'fresh server per measured attempt; same4096-input/64-output warmup; greedy4096 output; serial; input-runN paired across arms','attempt_limit':3,'context256_control1':'Previously completed phaseA; same config/payload/protocol, not temporally paired. No fourth repeat.'})
 # Add one long32K OFF guard per finalist, outside performance matrix. These
 # are distinct modes with one attempt; do not invent OFF headline medians.
 for variant in ['history-off','early-off']:
  point(variant,'32k',1)
 # Guard requested old arithmetic; compare same exact primary payload.
 for row in plan:
  guard();status('C_PRIMARY_MATRIX',phase='C',running=row,next_exact_action='Complete current4096 request; no concurrent build/training/profile')
  try:
   point(row['variant'],row['profile'],row['rep'])
  except Exception as error:
   path=C/'raw'/row['variant']/row['profile']/f"rep{row['rep']}"
   rec=path/'raw/run.json'
   if rec.exists() and load(rec).get('state') in ['INVALID','INVALID_PROTOCOL']:
    save(path/'results.json',{'runs':[load(rec)],'headline':True,'error':repr(error),'invalid_attempt':True})
    print('INVALID_ATTEMPT_PRESERVED',row,repr(error),flush=True)
   else:
    save(C/'phase-c/primary-failure.json',{'point':row,'error':repr(error),'time':time.time(),'next':'Inspect runtime/safety failure before more candidate inference; original control remains safe'})
    raise
  done=[str(p) for p in (C/'raw').glob('*/*/rep*/results.json')]
  save(C/'phase-c/primary-progress.json',{'completed':done,'current':row,'updated_epoch':time.time()})
 status('C_PRIMARY_COMPLETE',phase='C',running=None,next_exact_action='Analyze paired metrics/progression/diagnostics, bounded independent confirmation and actual launch smoke')
if __name__=='__main__':main()
