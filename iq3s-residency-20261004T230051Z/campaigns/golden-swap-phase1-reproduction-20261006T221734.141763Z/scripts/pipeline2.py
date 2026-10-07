"""Sequential CPU preparation; observed live handle is awaited before compilation."""
import subprocess,os,time
from common import *
# A verified current handle, not a stale lock or intent.
import sys
sys.path.append(str(C.parents[1]/'src/control/.venv/lib/python3.13/site-packages'))
# /proc start ticks provide process identity without requiring psutil in the analysis venv.
pid=2370858;stat=pathlib.Path('/proc')/str(pid)/'stat';expected=stat.read_text().split()[21] if stat.exists() else None
while stat.exists():
 current=stat.read_text().split();
 if current[21]!=expected or current[2]=='Z':break
 progress(2,'HEARTBEAT waiting for confirmed live CPU evaluator',owned_cpu_pid=pid,eta='unknown');time.sleep(25)
# A clean expected metrics file proves the completed evaluation, not merely process exit.
assert (C/'results/development-calibration-prediction-metrics.json').exists(),'Trainer/evaluator stopped without complete diagnostics'
python=str(C/'.venv/bin/python');env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2')
resume_stage=sys.argv[1] if len(sys.argv)>1 else None
def run(label,cmd,timeout=1200,extra=None):
 global resume_stage
 if label=='learning-curves' and (C/'results/learning-curves.json').exists():return
 if resume_stage and label!=resume_stage:return
 resume_stage=None
 progress(2,label+' START',owned_cpu_pid=None);ledger('CPU stage START',stage=label,command=cmd)
 e=env.copy();e.update(extra or {})
 with Heartbeat(label,2):
  logpath=C/'logs'/(label+'.log');version=1
  while logpath.exists():version+=1;logpath=C/'logs'/(label+'-attempt'+str(version)+'.log')
  with logpath.open('x') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=e,check=True,timeout=timeout)
 ledger('CPU stage COMPLETE',stage=label);progress(2,label+' COMPLETE')
run('compile-offline',[python,str(C/'scripts/compile_offline.py')],600)
run('scorer-parity',[python,str(C/'scripts/test_scorer.py')],120)
run('policy-fixture',[str(C/'builds/policy-fixture')],60)
run('full-reference-regression',[str(C/'builds/information-fixture')],240,{'STRATA_Q4_TAPE':str(P0/'raw/math-rational/tape.bin'),'STRATA_Q4_TAPE_MODE':'replay'})
run('learning-curves',[python,str(C/'scripts/diagnostics.py')],300)
run('offline-smoke',[python,str(C/'scripts/offline_campaign.py'),'smoke'],600)
run('offline-competition',[python,str(C/'scripts/offline_campaign.py'),'competition'],2400)
frozen=load(C/'models/selection.json');assert frozen['promising'],'No model meets the frozen offline promise gate: investigate before integration/live matrix'
run('offline-reserved',[python,str(C/'scripts/offline_campaign.py'),'reserved'],900)
run('prediction-reserved',[python,str(C/'scripts/train.py'),'--evaluate-reserved'],1200)
progress(2,'STEP 2 END: frozen finalist and reserved evaluation complete',selected_policy=frozen['policy'],threshold=frozen['threshold'],owned_cpu_pid=None,status='STEP_2_COMPLETE')
