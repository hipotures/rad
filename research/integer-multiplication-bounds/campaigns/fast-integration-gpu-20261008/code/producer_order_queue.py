#!/usr/bin/env python3
"""Replenished, bounded producer/order/threshold experiments using pinned code."""
import argparse,datetime,hashlib,json,multiprocessing,sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed

def main():
 p=argparse.ArgumentParser();p.add_argument('--code',required=True);p.add_argument('--source',required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--configs',type=Path,required=True);p.add_argument('--workers',type=int,required=True);a=p.parse_args()
 sys.path.insert(0,a.code)
 from producer_search import initialize
 from point_order_search import evaluate
 configs=json.loads(a.configs.read_text());done=[];a.work.mkdir(parents=True,exist_ok=True)
 result=dict(status='running',command=sys.argv,config_sha256=hashlib.sha256(a.configs.read_bytes()).hexdigest(),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),configurations=configs,rows=[])
 with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('fork'),initializer=initialize,initargs=(a.source,a.work,a.work/'builds/moment_match_positive')) as pool:
  pending={};it=iter(configs)
  while True:
   try:allowed=int((a.work/'allowed-slots.json').read_text())
   except (OSError,ValueError):allowed=a.workers
   while len(pending)<max(1,min(a.workers,allowed)):
    cfg=next(it,None)
    if cfg is None:break
    pending[pool.submit(evaluate,cfg)]=cfg
   if not pending:break
   future=next(as_completed(pending));pending.pop(future);row=future.result();done.append(row);result['rows']=done
   (a.work/'results.json').write_text(json.dumps(result,indent=2)+'\n')
   print(json.dumps({k:row.get(k)for k in ('case_id','status','R','seconds','pid')}),flush=True)
 result.update(status='complete',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(a.work/'results.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
