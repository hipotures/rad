"""Frozen adjacent blocks; fixed deadline coverage, serial fresh servers."""
import argparse,datetime,statistics
from common import *
import live
v=argparse.ArgumentParser();v.add_argument('kind',choices=['main','independent']);args=v.parse_args()
tasks={x['task_id']:x for x in load(P0/'benchmark-manifest.json')['tasks']};ind=load(C/'inputs/independent-task-manifest.json');tasks[ind['task_id']]=ind
order=load(C/'run-order.json')[args.kind];done=[];clock=load(C/'clock.json');cutoff=datetime.datetime.fromisoformat(clock['major_work_cutoff_utc']).timestamp()
for start in range(0,len(order),3):
 block=order[start:start+3];samples=[x['total_operating_s'] for x in done];estimate=max(samples[-9:],default=180)+20
 if time.time()+3*estimate>cutoff:
  ledger('Deadline coverage stopped before next block',kind=args.kind,next_block=block,remaining=len(order)-start,estimated_block_s=3*estimate);break
 for entry in block:
  progress(4,'START frozen live block',task=entry['task'],arm=entry['arm'],block=entry['block'],version=load(C/'configs/runtime-identity.json')['source_sha'],completed=len(done),remaining=len(order)-len(done),eta_range_s=[(len(order)-len(done))*min(samples),(len(order)-len(done))*max(samples)] if samples else None,next_action='Complete all three adjacent arms')
  result=live.point(tasks[entry['task']],entry['arm'],entry['label'],4,wait_profile=1);result.update(block=entry['block'],kind=args.kind);save(C/'raw'/entry['label']/'episode.json',result);done.append(result)
  save(C/'results'/(args.kind+'-execution.json'),[{'task':x['task'],'arm':x['arm'],'label':x['label'],'block':x['block'],'valid':x['valid'],'total_operating_s':x['total_operating_s']} for x in done])
 samples=[x['total_operating_s'] for x in done];left=len(order)-len(done)
 progress(4,'Complete adjacent block',task=block[0]['task'],block=block[0]['block'],arm='ALL',completed=len(done),remaining=left,eta_range_s=[left*min(samples),left*max(samples)],next_action='Next predeclared block; retain all outcomes')
print('MATRIX COMPLETE',args.kind,len(done),len(order),flush=True)
