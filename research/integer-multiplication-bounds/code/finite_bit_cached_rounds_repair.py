#!/usr/bin/env python3
"""Fresh pinned-JSON h53/h54 three-round choices, two probes per allocation.

Every changed witness receives the frozen full coefficient/frame/target/rank
checks. Only the complete parent's immutable allocation is reused. Each
chunk is one CPU worker; admission counters count chunks, not inner probes.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import time

import finite_bit_rounds_cached as witness
from finite_bit_rounds_cohort import read, write


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def evaluate(job):
    cap=job['address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    witness.first.witness.install_reference(job['reference'])
    path=Path(job['input_path']);assert sha256(path.read_bytes()).hexdigest()==job['input_sha256']
    parent=read(path);start=time.monotonic();results=[]
    if job['kind']=='new-h54-parent':
        setting=job['parent_setting']
        parent=witness.first.case(parent['h'],parent['base'],parent['positions'],
            setting['limit'],setting['policy'],setting['seed'],6.0,frozen=parent)
        parent.update(candidate_id=digest(dict(job['definition'],stage='new-multi-option-parent')))
        parent_path=Path(job['run_dir'])/'cases'/(parent['candidate_id']+'.json')
        parent.update(input_path=str(path),input_sha256=job['input_sha256'],
            input_kind='ordinary-compiled',pid=os.getpid(),scientific_stage='new-multi-option-parent')
        write(parent_path,parent);results.append(parent)
        path=parent_path
    for setting in job['probes']:
        before=time.monotonic()
        row=witness.case(parent,3,setting['limit'],setting['policy'],setting['seed'],6.0)
        if row['pinned_parent_physical_evidence_reused']:
            assert row['role_saving']==0
            row={**parent,**row};row['checked']=parent['checked']
        definition=dict(job['definition'],stage='successive-round-probe',setting=setting,
            actual_parent_sha256=sha256(path.read_bytes()).hexdigest())
        row.update(candidate_id=digest(definition),definition=definition,input_path=str(path),
            input_sha256=definition['actual_parent_sha256'],pid=os.getpid(),
            scientific_stage='successive-round-probe',probe_elapsed_seconds=time.monotonic()-before)
        write(Path(job['run_dir'])/'cases'/(row['candidate_id']+'.json'),row);results.append(row)
    return dict(chunk_id=job['chunk_id'],h=parent['h'],pid=os.getpid(),
        roles=[r['compiled_roles'] for r in results],case_ids=[r['candidate_id'] for r in results],
        elapsed_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference',required=True);p.add_argument('--parent',type=Path,action='append',required=True)
    p.add_argument('--h54-parent',type=Path,required=True);p.add_argument('--cache-control',type=Path,required=True)
    p.add_argument('--predecessor',type=Path,required=True);p.add_argument('--reserve-file',type=Path,required=True)
    p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--minutes',type=float,default=30)
    p.add_argument('--max-workers',type=int,default=16);p.add_argument('--address-space-gib',type=int,default=8)
    a=p.parse_args();assert a.max_workers==16
    control=read(a.cache_control)
    assert control['status']=='Terminal exact cold/warm parent-allocation identity PASS'
    assert control['source_sha256']==sha256(Path(witness.__file__).read_bytes()).hexdigest()
    a.run_dir.mkdir(parents=True,exist_ok=False);(a.run_dir/'cases').mkdir()
    source=sha256(Path(__file__).read_bytes()).hexdigest();jobs=[]
    def job(path,kind,limit,policy,index):
        r=read(path);assert r['h']==(54 if kind=='pinned-h54-parent' else 53)
        definition=dict(input_path=str(path),input_sha256=sha256(path.read_bytes()).hexdigest(),
            kind=kind,parent_setting=dict(limit=limit,policy=policy,seed=737),
            probes=[dict(limit=limit,policy=policy,seed=737+index*104729),
                    dict(limit=limit,policy='seeded' if policy!='seeded' else 'wide',seed=104773+index*104729)],
            rounds=3,time_limit=6.0,dispatcher_source_sha256=source,
            cache_source_sha256=control['source_sha256'],
            evaluator_source_sha256=control['frozen_evaluator_source_sha256'])
        return dict(definition,definition=definition,chunk_id=digest(definition),
            reference=a.reference,run_dir=str(a.run_dir),address_space_gib=a.address_space_gib)
    for index,policy in enumerate(('wide','narrow','seeded')):
        for limit in (4,8):jobs.append(job(a.h54_parent,'pinned-h54-parent',limit,policy,index+10))
    for path in a.parent:
        for index,policy in enumerate(('wide','narrow','seeded')):
            for limit in (4,8,20):jobs.append(job(path,'pinned-multi-option-parent',limit,policy,index))
    assert len({j['chunk_id'] for j in jobs})==len(jobs)
    identities=[(j['input_sha256'],s['limit'],s['policy'],s['seed']) for j in jobs for s in j['probes']]
    assert len(set(identities))==len(identities)
    protocol=dict(status='Started',started_utc=datetime.now(timezone.utc).isoformat(),dispatcher_pid=os.getpid(),
        source_sha256=source,cache_control_sha256=sha256(a.cache_control.read_bytes()).hexdigest(),
        jobs=jobs,max_workers=16,address_space_gib=a.address_space_gib,
        memory_scope='At most six h54 workers; other h53 witnesses measured about5.3GiB each; aggregate96GiB',
        hypotheses='Three actual inherited-frame rounds from exact saved h54/h53 parent JSON; h54 original25595-role improvement reused without scientific replay',
        scope='One-entry exact parent allocation cache; immutable parent identities checked on each probe; every strict changed physical graph completely verified; no original coefficient replay',
        historical_original_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z')
    write(a.run_dir/'protocol.json',protocol);start=time.monotonic();pending={};done_rows=[];errors=[];index=0;capacity=0
    def checkpoint(status):
        write(a.run_dir/'checkpoint.json',dict(status=status,dispatcher_pid=os.getpid(),
            planned_candidates=len(jobs),submitted_candidates=index,completed_candidates=len(done_rows),
            failed_candidates=len(errors),active_capacity=capacity,admission_units='one process-local chunk',
            scientific_case_count=sum(len(r['case_ids']) for r in done_rows),
            elapsed_seconds=time.monotonic()-start))
    checkpoint('Initializing')
    with ProcessPoolExecutor(max_workers=16,max_tasks_per_child=1) as pool:
        while pending or index<len(jobs):
            old=read(a.predecessor/'checkpoint.json')
            previous=0 if old['status'].startswith('Terminal') else max(0,old['submitted_candidates']-old['completed_candidates']-old.get('failed_candidates',0))
            reserved=read(a.reserve_file)['reserved_workers'];assert 0<=reserved<=16
            capacity=max(0,16-reserved-previous)
            while len(pending)<capacity and index<len(jobs) and time.monotonic()-start<a.minutes*60:
                j=jobs[index];index+=1;pending[pool.submit(evaluate,j)]=j
            checkpoint('Running')
            if not pending and (index==len(jobs) or time.monotonic()-start>=a.minutes*60):break
            finished,_=wait(pending,timeout=5,return_when=FIRST_COMPLETED)
            for f in finished:
                j=pending.pop(f)
                try:
                    r=f.result();done_rows.append(r);write(a.run_dir/'chunks'/(j['chunk_id']+'.json'),r)
                    print(json.dumps(r),flush=True)
                except Exception as e:
                    r=dict(chunk_id=j['chunk_id'],exception_type=type(e).__name__,message=str(e),traceback=__import__('traceback').format_exc(),
                        completed_utc=datetime.now(timezone.utc).isoformat());errors.append(r)
                    write(a.run_dir/'chunks'/(j['chunk_id']+'.error.json'),r);print(json.dumps(r),flush=True)
    status='Terminal PASS' if len(done_rows)==len(jobs) and not errors else 'Terminal PARTIAL; all attempts retained'
    summary=dict(status=status,completed_candidates=len(done_rows),submitted_candidates=index,failed_candidates=len(errors),
        planned_candidates=len(jobs),admission_units='one process-local chunk',scientific_case_count=sum(len(r['case_ids']) for r in done_rows),
        elapsed_seconds=time.monotonic()-start,chunks=done_rows,errors=errors,
        maximum_worker_rss_kib=max((r['peak_rss_kib'] for r in done_rows),default=0))
    write(a.run_dir/'summary.json',summary);write(a.run_dir/'checkpoint.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('chunks','errors')}),flush=True)


if __name__=='__main__':main()
