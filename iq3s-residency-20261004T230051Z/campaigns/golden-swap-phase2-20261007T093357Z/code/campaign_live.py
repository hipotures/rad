"""Frozen serial owned OFF/ON, main and independent replay; conservative deadline funnel."""
import argparse,statistics,time,datetime
from common import *
import live

def run(order,tasks,kind):
 completed=[];clock=load(C/'clock.json');stop=datetime.datetime.fromisoformat(clock['stop_substantial_utc'].replace('Z','+00:00')).timestamp()
 for idx,x in enumerate(order):
  remaining=len(order)-idx;durations=[r['total_operating_s'] for r in completed];projection=(max(durations[-8:],default=155)+15)*(4 if kind in ['main','independent'] else 1)
  if time.time()+projection>stop:ledger('Deadline funnel stops before next bounded block',kind=kind,remaining=remaining,projection_s=projection);break
  label=x['label'];p=C/'raw'/label
  assert not p.exists(),'No unchanged attempt rerun or overwrite'
  progress(4,'START '+kind+' '+label,task=x['task'],arm=x['arm'],block=x.get('block'),version=load(C/'configs/runtime-identity.json')['source_sha'],completed=len(completed),remaining=remaining,eta_range_s=[remaining*min(durations),remaining*max(durations)] if durations else None,next_action='Complete adjacent frozen block')
  r=live.point(tasks[x['task']],x['arm'],label,4);r.update(block=x.get('block'),kind=kind);save(p/'episode.json',r);completed.append(r)
  save(C/'results'/f'{kind}-execution.json',[{'task':r['task'],'arm':r['arm'],'label':r['label'],'block':r.get('block'),'valid':r['valid'],'total_operating_s':r['total_operating_s']} for r in completed])
  if (idx+1)%4==0:
   left=len(order)-idx-1;progress(4,f'{kind} block complete',completed=len(completed),remaining=left,version=load(C/'configs/runtime-identity.json')['source_sha'],eta_range_s=[left*min(d['total_operating_s'] for d in completed),left*max(d['total_operating_s'] for d in completed)],next_action='Next fixed block; preserve slow observations')
 return completed
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('kind',choices=['development','main','independent']);v=a.parse_args();tasks={t['task_id']:t for t in load(P0/'benchmark-manifest.json')['tasks']}
 if v.kind=='development':
  order=[{'task':'math-rational','arm':a,'label':'dev-math-rational-'+label,'block':b} for a,label,b in [('LOGISTIC_OFF','OFF1',1),('ORACLE_IN_LOGISTIC_TC','ON2',1),('ORACLE_IN_LOGISTIC_TC','ON3',2),('LOGISTIC_OFF','OFF2',2)]]
  save(C/'configs/development-run-order.json',{'order':order,'unpaired_smoke':'smoke-math-rational-LOGISTIC_TC is first ON attempt; total ON3/OFF2, no fourth run','method':'Two matched OFF/ON pairs, reversed order in second'})
 elif v.kind=='main':order=load(C/'run-order.json')['main']
 else:order=load(C/'run-order.json')['independent'];t=load(C/'inputs/independent-task-manifest.json');tasks[t['task_id']]=t
 run(order,tasks,v.kind)
