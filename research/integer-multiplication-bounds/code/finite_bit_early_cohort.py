#!/usr/bin/env python3
"""Task-specific mixed-ground earlier-capacity probe queue; admission ends09:10Z."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import time

import finite_bit_early_selection as witness
from finite_bit_rounds_cohort import read,write


def digest(v):return sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def evaluate(job):
    cap=job['address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    witness.allocation.first.witness.install_reference(job['reference'])
    path=Path(job['input_path']);assert sha256(path.read_bytes()).hexdigest()==job['input_sha256']
    parent=read(path);rows=[];start=time.monotonic()
    for seed in job['seeds']:
        cache=witness.allocation.CACHE
        hit=bool(cache and cache['key']==witness.allocation.parent_key(parent))
        row=witness.case(parent,job['policy'],seed,job['limit'],4)
        definition=dict(job['definition'],seed=seed)
        row.update(candidate_id=digest(definition),definition=definition,input_path=str(path),
            input_sha256=job['input_sha256'],pid=os.getpid(),parent_allocation_cache_reused=hit)
        write(Path(job['run_dir'])/'cases'/(row['candidate_id']+'.json'),row);rows.append(row)
    return dict(chunk_id=job['chunk_id'],h=parent['h'],pid=os.getpid(),
        case_ids=[r['candidate_id']for r in rows],roles=[r['compiled_roles']for r in rows],
        allocation_prepare_seconds=[r['allocation_prepare_seconds']for r in rows],
        final_changed_verification_seconds=[r['final_changed_verification_seconds']for r in rows],
        elapsed_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',required=True)
    p.add_argument('--parent',type=Path,action='append',required=True);p.add_argument('--small-control',type=Path,required=True)
    p.add_argument('--predecessor',type=Path,required=True);p.add_argument('--reserve-file',type=Path,required=True)
    p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--max-workers',type=int,default=16)
    p.add_argument('--address-space-gib',type=int,default=8)
    a=p.parse_args();assert a.max_workers==16
    control=read(a.small_control);assert control['status']=='Terminal exact earlier-selection compound witnesses PASS'
    source_hash=sha256(Path(witness.__file__).read_bytes()).hexdigest();assert control['source_sha256']==source_hash
    assert {r['policy']:r['compiled_roles']for r in control['rows']}=={'late-parent':3576,'early-parent':3589,'scarce-capacity':3571}
    assert all('complete_small_controls'in r for r in control['rows'])
    a.run_dir.mkdir(parents=True,exist_ok=False);(a.run_dir/'cases').mkdir();parents=[]
    for path in a.parent:
        r=read(path);assert r['h']in(53,54)
        parents.append(dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest(),h=r['h'],
            compiled_sha256=r['checked']['compiled_sha256']))
    assert len({r['compiled_sha256']for r in parents})==len(parents)
    jobs=[];dispatcher=sha256(Path(__file__).read_bytes()).hexdigest()
    for policy in witness.POLICIES:
        for limit in (4,8):
            for parent in parents:
                definition=dict(input_path=parent['path'],input_sha256=parent['sha256'],h=parent['h'],
                    policy=policy,limit=limit,max_rounds=4,evaluator_source_sha256=source_hash,
                    dispatcher_source_sha256=dispatcher)
                jobs.append(dict(definition,definition=definition,chunk_id=digest(definition),seeds=[0,104729],
                    reference=a.reference,run_dir=str(a.run_dir),address_space_gib=a.address_space_gib))
    protocol=dict(status='Started',started_utc=datetime.now(timezone.utc).isoformat(),dispatcher_pid=os.getpid(),
        jobs=jobs,parents=parents,source_sha256=dispatcher,evaluator_source_sha256=source_hash,
        small_control_sha256=sha256(a.small_control.read_bytes()).hexdigest(),max_workers=16,
        admission_cutoff='2026-10-08T09:10:00Z',maximum_active_h54=8,
        scientific_scope='Different original first-batch capacity/child allocation; later actual frames retained; exact greedy subsets, no MILP preprocessing; each final changed graph receives full maps/frames/targets/histogram/G/E checks',
        reuse_scope='Only one pinned parent allocation per process; no old scientific coefficient replay; two distinct seeds per chunk')
    write(a.run_dir/'protocol.json',protocol);start=time.monotonic();pending={};completed=[];errors=[];remaining=list(jobs);submitted=0;capacity=0
    cutoff=datetime(2026,10,8,9,10,tzinfo=timezone.utc)
    def checkpoint(status):
        write(a.run_dir/'checkpoint.json',dict(status=status,dispatcher_pid=os.getpid(),
            planned_candidates=len(jobs),submitted_candidates=submitted,completed_candidates=len(completed),
            failed_candidates=len(errors),active_capacity=capacity,admission_units='one process-local chunk',
            elapsed_seconds=time.monotonic()-start,scientific_case_count=2*len(completed)))
    checkpoint('Initializing')
    with ProcessPoolExecutor(max_workers=16,max_tasks_per_child=1)as pool:
        while pending or remaining:
            old=read(a.predecessor/'checkpoint.json');reserved=read(a.reserve_file)['reserved_workers']
            previous=0 if old['status'].startswith('Terminal')else max(0,old['submitted_candidates']-old['completed_candidates']-old.get('failed_candidates',0))
            capacity=max(0,16-reserved-previous)
            while len(pending)<capacity and remaining and datetime.now(timezone.utc)<cutoff:
                active54=sum(j['h']==54 for j in pending.values())
                index=next((i for i,j in enumerate(remaining)if j['h']!=54 or active54<8),None)
                if index is None:break
                job=remaining.pop(index);submitted+=1;pending[pool.submit(evaluate,job)]=job
            checkpoint('Running')
            if not pending and (not remaining or datetime.now(timezone.utc)>=cutoff):break
            done,_=wait(pending,timeout=5,return_when=FIRST_COMPLETED)
            for f in done:
                j=pending.pop(f)
                try:
                    r=f.result();completed.append(r);write(a.run_dir/'chunks'/(j['chunk_id']+'.json'),r);print(json.dumps(r),flush=True)
                except Exception as e:
                    r=dict(chunk_id=j['chunk_id'],exception_type=type(e).__name__,message=str(e),
                        traceback=__import__('traceback').format_exc(),completed_utc=datetime.now(timezone.utc).isoformat())
                    errors.append(r);write(a.run_dir/'chunks'/(j['chunk_id']+'.error.json'),r);print(json.dumps(r),flush=True)
    status='Terminal PASS'if not remaining and not errors else'Terminal PARTIAL; all original attempts retained'
    summary=dict(status=status,completed_candidates=len(completed),submitted_candidates=submitted,
        failed_candidates=len(errors),planned_candidates=len(jobs),scientific_case_count=2*len(completed),
        admission_units='one process-local chunk',elapsed_seconds=time.monotonic()-start,
        chunks=completed,errors=errors,unsubmitted_ids=[j['chunk_id']for j in remaining],
        maximum_worker_rss_kib=max((r['peak_rss_kib']for r in completed),default=0))
    write(a.run_dir/'summary.json',summary);write(a.run_dir/'checkpoint.json',summary)
    print(json.dumps({k:v for k,v in summary.items()if k not in('chunks','errors')}),flush=True)


if __name__=='__main__':main()
