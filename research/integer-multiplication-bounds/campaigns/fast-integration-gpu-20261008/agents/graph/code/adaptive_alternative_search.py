#!/usr/bin/env python3
"""Refill seven CPU slots with provider-mapped, moment-scored producers.

Completed immutable rows from an active input cohort may be used immediately.
The previous queue's log controls the concurrency ramp, so its final tasks
need not finish before mathematically distinct work begins.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from alternative_producer_clones import evaluate
from producer_search import digest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,nargs='+',required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--previous-log',type=Path)
    p.add_argument('--previous-total',type=int,default=336);p.add_argument('--previous-workers',type=int,default=6)
    p.add_argument('--slots',type=int,default=7);p.add_argument('--rounds',type=int,default=6)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists()and 1<=a.slots<=10
    for name in('builds','inputs','raw'):(a.work/name).mkdir(parents=True,exist_ok=False)
    native=Path(__file__).with_name('moment_match_rank_node.cpp');matcher=a.work/'builds'/'matcher'
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(matcher)],check=True)
    documents=[];seen=set();inputs=[]
    for path in a.input:
        data=json.loads(path.read_text());inputs.append(dict(path=str(path),sha256=digest(path),status=data.get('status')))
        for doc in data['rows']if'rows'in data else[data]:
            row=doc.get('producer')
            if not row or doc.get('status')=='failed' or row['h']>35:continue
            key=row['dag_sha256']
            if key in seen:continue
            seen.add(key);documents.append(doc)
    documents.sort(key=lambda doc:(0 if doc['producer']['h']in(23,25)else 1,doc['producer']['h'],doc['producer']['R']))
    tasks=[];manifest=[]
    for index,doc in enumerate(documents):
        path=a.work/'inputs'/f"parent-{doc['producer']['h']}-{index:04d}.json"
        path.write_text(json.dumps(dict(producer=doc['producer'],case_id=doc.get('case_id'),initial_full_witness_path=doc.get('full_witness_path')),indent=2,sort_keys=True)+'\n')
        manifest.append(dict(path=str(path),sha256=digest(path),h=doc['producer']['h'],R=doc['producer']['R'],dag_sha256=doc['producer']['dag_sha256']))
        for policy,limit in(('mapped-moment',128),('mapped-scarce',128),('mapped-moment',512)):
            tasks.append((path,a.work,matcher,limit,a.rounds,policy))
    (a.work/'inputs'/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    result=dict(status='running',command=sys.argv,slots=a.slots,rounds=a.rounds,inputs=inputs,
                parents=len(documents),total_cases=len(tasks),rows=[],started_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256={p.name:digest(p)for p in(Path(__file__),native,Path(__file__).with_name('alternative_producer_clones.py'))})
    def available():
        if not a.previous_log:return a.slots
        completed=sum('"case_id"'in line for line in a.previous_log.read_text().splitlines())
        active=min(a.previous_workers,max(0,a.previous_total-completed))
        return max(0,a.slots-active)
    next_task=0;active={};last_status=0
    with ProcessPoolExecutor(max_workers=a.slots)as pool:
        while next_task<len(tasks)or active:
            cap=available()
            while len(active)<cap and next_task<len(tasks):
                task=tasks[next_task];future=pool.submit(evaluate,task);active[future]=task;next_task+=1
            done,_=wait(active,timeout=1,return_when=FIRST_COMPLETED)if active else(set(),set())
            if not active:time.sleep(.25)
            for future in done:
                task=active.pop(future);row=future.result()
                compact={k:row.get(k)for k in('case_id','status','initial_roles','role_saving','seconds','error')}
                compact['producer']=row.get('producer');compact['full_witness_path']=str(a.work/'raw'/f"{row['case_id']}.json")
                result['rows'].append(compact)
                a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
                print(json.dumps(dict(completed=len(result['rows']),total=len(tasks),active=len(active),allowed=cap,
                                      h=row.get('producer',{}).get('h'),R=row.get('producer',{}).get('R'),
                                      role_saving=row.get('role_saving'),status=row['status'],case_id=row['case_id'],error=row.get('error'))),flush=True)
            if time.monotonic()-last_status>60:
                print(json.dumps(dict(status='live queue',completed=len(result['rows']),total=len(tasks),active=len(active),allowed=cap)),flush=True);last_status=time.monotonic()
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
