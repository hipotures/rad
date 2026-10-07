"""Exercise the isolated wrapper without treating extra development checks as headline repeats."""
import subprocess,psutil,time,hashlib,datetime
from common import *
python=str(C.parents[1]/'src/control/.venv/bin/python')
records=[]
no_gpu()
for task,arm in [('math-rational','REPLAY_CURRENT'),('math-rational','ORACLE_FULL'),('math-rational','ORACLE_IN_LEARNED_VICTIM')]:
 elapsed=time.monotonic()-load(C/'clock.json')['start_monotonic'];assert elapsed+500<12000,'Do not start reproduction measurement after the original study funnel'
 # One preflight plus this one wrapper check is two unchanged attempts, below the campaign maximum three.
 count=sum(load(p)['task']==task and load(p)['arm']==arm for p in (C/'raw').glob('*/episode.json'))+sum(r.get('task')==task and r.get('arm')==arm for r in records)
 assert count<3,'Unchanged development point repetition cap'
 label='reproducer-'+task+'-'+arm;log=C/'tests'/(label+'.log');cmd=[python,str(C/'scripts/reproduce.py'),'--task',task,'--arm',arm];progress(5,'Test isolated reproducer '+task+' '+arm,task=task,arm=arm,owned_pid=None);ledger('Reproducer test START',command=cmd,matching_prior_attempts=count)
 begin=time.monotonic()
 with Heartbeat(label,5):
  with log.open('x') as out:result=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=700)
 text=log.read_text();line=next(l for l in text.splitlines() if l.startswith('REPRODUCTION_DIRECTORY '));dest=pathlib.Path(line.split(' ',1)[1]);assert dest.parent==C.parent and dest.name.startswith('golden-swap-phase1-reproduction-');ep=load(dest/'raw'/('reproduction-'+task+'-'+arm)/'episode.json');assert result.returncode==0 and ep['valid'],(result.returncode,ep.get('error'));no_gpu()
 record={'command':cmd,'task':task,'arm':arm,'state':'PASS','directory':str(dest),'episode':str(dest/'raw'/('reproduction-'+task+'-'+arm)/'episode.json'),'outer_wall_s':time.monotonic()-begin,'root_campaign_elapsed_s':time.monotonic()-load(C/'clock.json')['start_monotonic'],'checkpoint_sha256':load(dest/'models/selection.json')['checkpoint_sha256'],'binary_sha256':load(dest/'builds/runtime-identity.json')['binary_sha256'],'matching_point_attempts_in_this_study':count+1,'classification':'Development reproduction check, not a headline reserved request; parent study clock remains unchanged.'};records.append(record);save(C/'tests/reproduction-checks.json',{'state':'PASS' if len(records)==3 else 'IN_PROGRESS','checks':records});ledger('Reproducer test COMPLETE',**record)
cmd=[python,str(C/'scripts/reproduce.py'),'--prepare-only']
with (C/'tests/reproducer-prepare-only.log').open('x') as out:subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,check=True,timeout=60)
records.append({'command':cmd,'state':'PASS','classification':'Prepare-only wrapper smoke, no model request'})
save(C/'tests/reproduction-checks.json',{'state':'PASS','checks':records,'dataset_generation':'Original smoke and all12 regeneration commands executed; scripts/dataset.py and data/*-manifest.json','model_fit_evaluation':'Original two-model development fit, export and dev/cal/reserved evaluation executed; logs/train*.log, model identities and prediction metrics','supported_replay_arms':'All three wrapper commands above actually replayed a development tape, and all36 reserved mode points validated. No unsupported point is represented as a successful benchmark.'});progress(5,'All isolated reproduction commands PASS',task=None,arm=None,owned_pid=None)
