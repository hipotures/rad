"""Wait for identified CPU evaluator, then build, validate, and preflight serially."""
import subprocess,os,time,psutil,sys
from common import *
pid=2380679
try:created=psutil.Process(pid).create_time()
except psutil.NoSuchProcess:created=None
wait_start=time.monotonic()
while created is not None:
 try:
  p=psutil.Process(pid)
  if abs(p.create_time()-created)>.1 or p.status()==psutil.STATUS_ZOMBIE:break
 except psutil.NoSuchProcess:break
 assert time.monotonic()-wait_start<1200,'CPU evaluation sequencing timeout'
 progress(2,'HEARTBEAT waiting for reserved CPU evaluation before build',owned_cpu_pid=pid);time.sleep(25)
assert (C/'results/reserved-prediction-metrics.json').exists(),'Reserved CPU evaluation failed'
no_gpu();python=str(C.parents[1]/'src/control/.venv/bin/python')
subprocess.run([python,str(C/'scripts/summarize_prediction.py')],check=True,timeout=60)
progress(2,'STEP 2 END: datasets, two models, matched controls and frozen reserved evaluation complete',selected_policy=load(C/'models/selection.json')['policy'],status='STEP_2_COMPLETE',owned_cpu_pid=None)
progress(3,'STEP 3 START: isolated binary build, safety and development replay preflight',status='STEP_3_ACTIVE')
for label,cmd,timeout in [('build-runtime',[python,str(C/'scripts/build_runtime.py')],1900),('safety',[python,str(C/'scripts/safety.py')],900),('live-identity-check',[python,str(C/'scripts/live.py'),'check'],60)]:
 if len(sys.argv)>1 and sys.argv[1]=='preflight' and label in ['build-runtime','safety']:continue
 ledger('Integration stage START',stage=label,command=cmd)
 with Heartbeat(label,3):
  with (C/'logs'/('stage3-'+label+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=timeout)
 ledger('Integration stage COMPLETE',stage=label)
assert load(C/'tests/safety-summary.json')['native_test_exit_code']==0,'Relevant native tests failed; inspect before preflight'
attempts=[]
for task,arm in [('math-rational','REPLAY_CURRENT'),('math-rational','ORACLE_FULL'),('math-rational','ORACLE_IN_LEARNED_VICTIM'),('math-sensor','REPLAY_CURRENT')]:
 label='preflight-'+task+'-'+arm;cmd=[python,str(C/'scripts/live.py'),'point','--task',task,'--arm',arm,'--label',label];ledger('Development preflight command',command=cmd)
 with (C/'logs'/(label+'.log')).open('x') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=600)
 result=load(C/'raw'/label/'episode.json');assert result['valid'];attempts.append({'task':task,'arm':arm,'label':label,'valid':True,'operating_s':result['total_operating_s']});save(C/'phase-a/preflight-summary.json',attempts)
progress(3,'STEP 3 END: exact binary, safety, three-mode development fidelity and short-input QSA validated',status='STEP_3_COMPLETE',owned_pid=None)
