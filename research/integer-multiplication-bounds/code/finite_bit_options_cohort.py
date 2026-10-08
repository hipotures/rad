#!/usr/bin/env python3
"""Thin bounded dispatcher for distinct rational multi-option clone witnesses."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import statistics
import time

import finite_bit_clone_options as witness
from finite_clone_batch import serialized


def read(path):
    # Shared reservations have legacy non-atomic writers. A short partial
    # JSON write is retried; it never creates a new allocation on its own.
    for attempt in range(20):
        try:return json.loads(path.read_text())
        except json.JSONDecodeError:
            if attempt==19:raise
            time.sleep(0.01)


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.writing')
    temporary.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    os.replace(temporary,path)


def evaluate(job):
    cap=job['worker_address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    witness.witness.install_reference(job['reference']);at=time.monotonic();cpu=time.process_time()
    path=Path(job['input_path']);assert sha256(path.read_bytes()).hexdigest()==job['input_sha256']
    document=read(path);parent=document['rows'][0] if 'rows' in document else document
    if 'chosen' in parent:
        frozen_path=Path(parent['baseline_path'])
        assert sha256(frozen_path.read_bytes()).hexdigest()==parent['baseline_input_sha256']
        frozen=read(frozen_path)
        raw=parent['chosen'];normalized=[serialized(witness.deserialize(row)) for row in raw]
        assert json.dumps(raw,sort_keys=True)==json.dumps(normalized,sort_keys=True)
        parent=dict(parent,chosen=normalized)
    else:frozen=parent;parent=None
    h=frozen['h'];base=frozen['base'];positions=frozen['positions']
    row=witness.case(h,base,positions,job['limit'],job['policy'],job['seed'],job['time_limit'],frozen,parent)
    row.update(candidate_id=job['candidate_id'],input_path=str(path),input_sha256=job['input_sha256'],
        pid=os.getpid(),elapsed_seconds=time.monotonic()-at,cpu_seconds=time.process_time()-cpu,
        parent_candidate_id=job['parent_candidate_id'],input_kind=job['input_kind'],
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True);parser.add_argument('--input',type=Path,action='append',required=True)
    parser.add_argument('--small-control',type=Path,required=True)
    parser.add_argument('--predecessor',type=Path,required=True)
    parser.add_argument('--reserve-file',type=Path,required=True)
    parser.add_argument('--max-workers',type=int,default=16)
    parser.add_argument('--worker-address-space-gib',type=int,default=6)
    parser.add_argument('--minutes',type=float,default=30)
    parser.add_argument('--limits',type=int,nargs='+',default=[2,4,8])
    parser.add_argument('--policies',nargs='+',choices=['wide','narrow','seeded'],default=['wide','narrow','seeded'])
    parser.add_argument('--seeds',type=int,nargs='+',default=[0,104729])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args();assert args.max_workers==16
    control=read(args.small_control)
    assert control['status']=='Terminal exact multiple-option rational clone witness PASS'
    assert control['source_sha256']==sha256(Path(witness.__file__).read_bytes()).hexdigest()
    small=next(row for row in control['rows'] if row['h']==12)
    assert small['strict_selection_gain']==61 and small['complete_small_controls']['complete_center_dirty_bases'][0]['exact_linear_map']
    args.run_dir.mkdir(parents=True,exist_ok=False);(args.run_dir/'cases').mkdir()
    parents=[]
    for path in args.input:
        document=read(path);row=document['rows'][0] if 'rows' in document else document
        parents.append(dict(path=str(path),sha256=sha256(path.read_bytes()).hexdigest(),h=row['h'],
            parent_candidate_id=row['candidate_id'],input_kind='delayed-clone' if 'chosen' in row else 'ordinary-compiled'))
    assert len({p['sha256'] for p in parents})==len(parents)
    jobs=[]
    for limit in args.limits:
        for policy in args.policies:
            for seed in args.seeds:
                for parent in parents:
                    definition=dict(input_path=parent['path'],input_sha256=parent['sha256'],h=parent['h'],
                        parent_candidate_id=parent['parent_candidate_id'],input_kind=parent['input_kind'],
                        limit=limit,policy=policy,seed=seed,time_limit=6.0,
                        evaluator_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
                        dispatcher_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
                    key=sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                    jobs.append(dict(definition,candidate_id=key,reference=args.reference,
                        worker_address_space_gib=args.worker_address_space_gib))
    assert len(jobs)==len({job['candidate_id'] for job in jobs})
    protocol=dict(status='Started',started_utc=datetime.now(timezone.utc).isoformat(),dispatcher_pid=os.getpid(),
        candidate_definitions=jobs,small_control_sha256=sha256(args.small_control.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),parents=parents,
        max_workers=args.max_workers,worker_address_space_gib=args.worker_address_space_gib,minutes=args.minutes,
        hypothesis='Multiple chain/provider choices enlarge the exact feasible clone set; each retained literal old plan remains a lower bound',
        scope='Pinned original constructor/compile identities; every strict new physical graph checked once; exact old clone lists retained on ties; numerical bounds excluded',
        active_campaign_deadline='2026-10-08T10:00:00Z',historical_original_deadline='2026-10-08T08:25:21Z')
    write(args.run_dir/'protocol.json',protocol)
    checkpoint=dict(status='Initializing',dispatcher_pid=os.getpid(),planned_candidates=len(jobs),
        submitted_candidates=0,completed_candidates=0,failed_candidates=0,active_capacity=0)
    write(args.run_dir/'checkpoint.json',checkpoint)
    start=time.monotonic();deadline=start+args.minutes*60;results=[];errors=[];pending={};index=0;changes=[];last_capacity=None
    def state(capacity):
        write(args.run_dir/'checkpoint.json',dict(checkpoint,status='Running',active_capacity=capacity,
            submitted_candidates=index,completed_candidates=len(results),failed_candidates=len(errors),
            elapsed_seconds=time.monotonic()-start,
            best_by_ground={str(h):min(r['compiled_roles'] for r in results if r['h']==h) for h in sorted({r['h'] for r in results})}))
    with ProcessPoolExecutor(max_workers=args.max_workers,max_tasks_per_child=1) as pool:
        while pending or index<len(jobs):
            reserved=read(args.reserve_file)['reserved_workers'];assert 0<=reserved<args.max_workers
            predecessor=read(args.predecessor/'summary.json') if (args.predecessor/'summary.json').exists() else read(args.predecessor/'checkpoint.json')
            old=0 if predecessor['status'].startswith('Terminal') else int(predecessor.get('active_capacity',args.max_workers))
            capacity=max(0,args.max_workers-reserved-old)
            if capacity!=last_capacity:
                changes.append(dict(utc=datetime.now(timezone.utc).isoformat(),capacity=capacity,reserved=reserved,predecessor=old));last_capacity=capacity
                print(json.dumps(changes[-1]),flush=True)
            while len(pending)<capacity and index<len(jobs) and time.monotonic()<deadline:
                job=jobs[index];index+=1;pending[pool.submit(evaluate,job)]=job
            state(capacity)
            if not pending and (index==len(jobs) or time.monotonic()>=deadline):break
            done,_=wait(pending,timeout=5,return_when=FIRST_COMPLETED)
            for future in done:
                job=pending.pop(future)
                try:
                    row=future.result();write(args.run_dir/'cases'/(job['candidate_id']+'.json'),row);results.append(row)
                    print(json.dumps(dict(candidate=job['candidate_id'][:12],h=row['h'],roles=row['compiled_roles'],
                        gain=row['strict_selection_gain'],reused=row['physical_witness_reused'],seconds=row['elapsed_seconds'])),flush=True)
                except Exception as error:
                    record=dict(candidate_id=job['candidate_id'],exception_type=type(error).__name__,message=str(error),
                        completed_utc=datetime.now(timezone.utc).isoformat());errors.append(record)
                    write(args.run_dir/'cases'/(job['candidate_id']+'.error.json'),record);print(json.dumps(record),flush=True)
    elapsed=time.monotonic()-start;best={}
    for row in results:
        if row['h'] not in best or row['compiled_roles']<best[row['h']]['roles']:
            path=args.run_dir/'cases'/(row['candidate_id']+'.json')
            best[row['h']]=dict(roles=row['compiled_roles'],candidate_id=row['candidate_id'],
                case_path=str(path),case_sha256=sha256(path.read_bytes()).hexdigest(),
                compiled_sha256=row['checked']['compiled_sha256'],strict_selection_gain=row['strict_selection_gain'])
    terminal='Terminal PASS' if len(results)==len(jobs) and not errors else 'Terminal PARTIAL; original attempts retained'
    summary=dict(status=terminal,elapsed_seconds=elapsed,completed_candidates=len(results),planned_candidates=len(jobs),
        submitted_candidates=index,errors=errors,unsubmitted_ids=[job['candidate_id'] for job in jobs[index:]],
        best_by_ground=best,verified_candidates_per_hour=3600*len(results)/elapsed,capacity_changes=changes,
        strict_changed_candidates=sum(not row['physical_witness_reused'] for row in results),
        strict_gains=sum(row['strict_selection_gain']>0 for row in results),
        phase_mean_seconds={name:statistics.mean(row['phase_seconds'][name] for row in results) for name in
            results[0]['phase_seconds']} if results else {},
        maximum_worker_rss_kib=max((row['process_lifetime_peak_rss_kib'] for row in results),default=0))
    write(args.run_dir/'summary.json',summary);write(args.run_dir/'checkpoint.json',summary)
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
