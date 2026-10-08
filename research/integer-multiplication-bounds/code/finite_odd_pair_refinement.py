#!/usr/bin/env python3
"""Distinct odd full-pair endpoint/multiorphan refinement of a terminal best."""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers
from finite_odd_pair_cohort import identity,evaluate

SEED=109;TARGET=420;CONFIG={}


def candidates(anchor,prior):
    h=anchor['h'];start=anchor['positions'];k=(h-1)//2
    assert h%2 and anchor['base']==2 and start[-1]==0
    excluded={r['candidate_id'] for r in prior['candidate_definitions']};excluded.add(anchor['candidate_id'])
    rows=[];seen=set()
    def append(positions,kind):
        value,key=identity(h,positions)
        if key in excluded or key in seen or len(rows)>=TARGET:return
        seen.add(key);rows.append(dict(value,candidate_id=key,neighborhood=kind,
            changed=[dict(common=i,old=a,new=b) for i,(a,b) in enumerate(zip(start,value['positions'])) if a!=b]))
    for common in range(h-1):
        old=start[common]
        for value in ([1,2] if old==0 else [old-1,old-2] if old==k-1 else [old-1,old+1]):
            positions=list(start);positions[common]=value;append(positions,'odd-individual-near')
    for pair in range(k):
        for value in (0,1,k-2,k-1):
            positions=list(start);positions[2*pair:2*pair+2]=[value,value];append(positions,'odd-paired-near')
    late=[i for i,value in enumerate(start[:-1]) if value];left,right=min(late),max(late)
    for first in range(max(0,left-3),left+4):
        for last in range(right-3,min(h-1,right+4)):
            for value in (k-1,k-2):
                positions=[0]*h;positions[first:last+1]=[value]*(last-first+1);append(positions,'odd-endpoint-window')
    rng=random.Random(SEED);attempts=0
    endpoints=sorted(set(range(max(0,left-3),min(h-1,left+4)))|set(range(max(0,right-3),min(h-1,right+4))))
    while len(rows)<TARGET:
        attempts+=1;assert attempts<20000
        positions=list(start);count=rng.choice([2,2,3,3,4,6])
        pool=endpoints if rng.random()<.6 else list(range(h-1))
        for common in rng.sample(pool,min(count,len(pool))):
            old=positions[common]
            positions[common]=rng.choice([0,1,k-2,k-1,max(0,old-1),min(k-1,old+1)])
        append(positions,'odd-seeded-multiorphan')
    assert len(rows)==len(seen)==TARGET and not seen&excluded
    CONFIG.update(planned_candidates=TARGET,seed=SEED,neighborhood_counts=dict(Counter(r['neighborhood'] for r in rows)),
        semantic_exclusion='All309 predecessor full-pair candidates excluded by normalized exact identity',
        normalization='Special common-point position unused; final position fixed0')
    return rows,sorted(excluded)


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:value=dict(value,odd_pair_refinement=CONFIG)
    real_write_json(path,value)


def main():
    global SEED,TARGET
    ap=argparse.ArgumentParser(add_help=False);ap.add_argument('--seed',type=int,default=109)
    ap.add_argument('--target-cases',type=int,default=420);args,remaining=ap.parse_known_args()
    SEED=args.seed;TARGET=args.target_cases;assert 300<=TARGET<=500
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        frozen_evaluator_sha256=sha256(Path(__file__).with_name('finite_odd_pair_cohort.py').read_bytes()).hexdigest(),
        constructor_sha256=sha256(Path(__file__).with_name('finite_odd_pair_positions.py').read_bytes()).hexdigest(),
        process_lifetime='One candidate per fresh process',original_deadline='2026-10-08T08:25:21Z',extended_deadline='2026-10-08T10:00:00Z')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json;queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
