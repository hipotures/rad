"""Six counted attempts; first complete pair is the live smoke, with symmetric gross gate."""
from common import *
import sys,statistics,hashlib
from protocol_rules import perturbation_gate
clock=load(R/'clock.json');rows=[];pairs=[]
for block in load(C/'configs/run-order.json')['blocks']:
 for arm in block['arms']:
  assert time.monotonic()-clock['start_monotonic']<11700,'Reporting reserve; no new request'
  label=f'block{block["block"]}-{arm}';assert not (W/'raw'/label).exists(),'Attempt exists; refuse cosmetic repeat'
  progress(3,'Counted replay START',block=block['block'],task='math-rational',arm=arm,completed_requests=len(rows),planned_requests=6,valid=None,next_action='Startup, identical warmup, full measured replay',eta='unknown')
  cmd=[sys.executable,str(C/'code/live.py'),'--task','math-rational','--arm',arm,'--label',label]
  with (W/'logs'/f'{label}-runner.log').open('x') as log:
   p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   from live import stop_owned
   import psutil,signal
   created=psutil.Process(p.pid).create_time();save(R/'matrix-parent.json',{'pid':p.pid,'create_time':created,'label':label,'command':cmd})
   try:code=p.wait(timeout=440)
   except subprocess.TimeoutExpired:stop_owned(p.pid,created);code=124
  path=W/'raw'/label/'episode.json';result=load(path) if path.exists() else {'label':label,'arm':arm,'valid':False,'error':'No completed episode','exit_code':code}
  result['block']=block['block'];result['exit_code']=code;rows.append(result);save(R/'results/live-attempts.json',rows)
  progress(3,'Counted replay END',block=block['block'],arm=arm,completed_requests=len(rows),planned_requests=6,valid=result['valid'],next_action='Pair guard or next frozen arm')
  if not result['valid'] or code!=0:raise RuntimeError('Preserved failed point; diagnose before another inference')
 members={r['arm']:r for r in rows if r['block']==block['block']};control=members['CONTROL']['run'];trace=members['TRACE']['run']
 pair={'block':block['block'],'decode_change_pct':100*(trace['decode_s']/control['decode_s']-1),'wall_change_pct':100*(trace['wall_s']/control['wall_s']-1)};pairs.append(pair);save(R/'results/paired-blocks.json',pairs);print('PAIR',json.dumps(pair),flush=True)
 if block['block']==1 and max(abs(pair['decode_change_pct']),abs(pair['wall_change_pct']))>10:
  save(R/'results/first-pair-pause.json',{'required':True,'pair':pair,'reason':'Gross symmetric perturbation; evidence retained'});raise RuntimeError('Gross first-pair gate; investigate, no neutralizing repeats')
save(R/'results/perturbation-gate.json',perturbation_gate(pairs));print('SYMMETRIC_GATE',json.dumps(perturbation_gate(pairs)),flush=True)
