#!/usr/bin/env python3
"""Bounded odd full-pair placement cohort after exact small controls."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import gc
import json
import os
from pathlib import Path
import resource
import sys
import time

import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers
import finite_odd_pair_positions as odd

CONFIG={}


def identity(h,positions):
    positions=list(positions);positions[-1]=0
    value=dict(h=h,base=2,positions=positions,construction='odd_orphan_full_pair',
        reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
    return value,sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def candidates(anchor,prior):
    rows=[];seen=set();grounds=[49,51,47,53,45,43]
    def append(h,positions,kind):
        value,key=identity(h,positions)
        if key in seen:return
        seen.add(key);rows.append(dict(value,candidate_id=key,neighborhood=kind,
            changed=[dict(field='odd_ground_full_pair_placement',h=h,pattern=kind)]))
    for h in grounds:
        k=(h-1)//2
        for position in (k-1,0,k//2):append(h,[position]*h,'odd-uniform-priority-'+str(position))
    for position in range(26):
        for h in grounds:
            if position<(h-1)//2:append(h,[position]*h,'odd-uniform-'+str(position))
    for delta in (0,-2,2,-4,4,-6,6):
        for start in (0,2,4,6):
            for h in grounds:
                k=(h-1)//2;positions=[0]*h
                for offset in range(k+delta):positions[(start+offset)%(h-1)]=k-1
                append(h,positions,'odd-late-window-'+str(start)+'-'+str(k+delta))
    assert len(rows)==len(seen)
    CONFIG.update(grounds=grounds,planned_candidates=len(rows),construction='Odd local even-sized full pairs; orphan+special pair moves among unaffected global pairs',
        canonicalization='The special common-point position is unused and always normalized to0',
        scalar_discriminator='h49 precompile459804; h51 precompile521514; small h7/h11 exact frame/physical/dirty controls run035200')
    return rows,[]


def evaluate(job):
    cap=job['worker_address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    odd.install_reference(job['reference']);started=time.monotonic();cpu=time.process_time()
    row=odd.case(job['h'],job['positions'],job['base'],True,False)
    row.update(candidate_id=job['candidate_id'],pid=os.getpid(),phase=job['phase'],local_cache=False,
        original=row['logical'],checked=row['compiled'],
        phase_seconds={'complete_exact_odd_graph_compile_and_histogram':time.monotonic()-started},
        cpu_seconds=time.process_time()-cpu,process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        verification_scope='Exact full odd formal/scalar/physical/positive-frame/target/matching/histogram checks; independent promotion and final analytic transfer separate',
        odd_constructor_sha256=sha256(Path(odd.__file__).read_bytes()).hexdigest(),
        cohort_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    gc.collect();return row


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:value=dict(value,odd_pair_configuration=CONFIG)
    real_write_json(path,value)


def main():
    ap=argparse.ArgumentParser(add_help=False);ap.add_argument('--control',type=Path,required=True)
    args,remaining=ap.parse_known_args();control=json.loads(args.control.read_text())
    assert control['status'].startswith('Terminal') and len(control['rows'])==4
    assert control['source_sha256']==sha256(Path(odd.__file__).read_bytes()).hexdigest()
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        constructor_sha256=control['source_sha256'],control_sha256=sha256(args.control.read_bytes()).hexdigest(),
        process_lifetime='One candidate per fresh process',original_deadline='2026-10-08T08:25:21Z',extended_deadline='2026-10-08T10:00:00Z')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1);queue.write_json=write_json
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
