#!/usr/bin/env python3
"""Exact direct-envelope successor to the completed singleton neighborhood.

This reuses the thin dispatcher and unchanged frozen evaluator, substitutes
the exactly equal direct envelope constructor, and supplies fresh seeded
multi-coordinate candidates. Every older planned candidate ID is excluded.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
from unittest.mock import patch

import finite_singleton_neighborhood as queue
from singleton_sensitivity import evaluate as frozen_evaluate

DIRECT_HASH = 'b95dc6a90713db358f2fe73cdf6feb4d8621d141ed51355ee86b49a388d5b021'
EXTRA_RUNS = []
SEED = 109
TARGET = 420
CONFIGURATION = {}


def evaluate_direct(job):
    import frame_envelope
    import fast_frame_envelope
    assert sha256(Path(fast_frame_envelope.__file__).read_bytes()).hexdigest() == DIRECT_HASH
    with patch.object(frame_envelope, 'labels', fast_frame_envelope.labels):
        row = frozen_evaluate(job)
    row['envelope_constructor'] = dict(source='fast_frame_envelope.py', sha256=DIRECT_HASH,
        control='All454388 Space fields and full unchanged compiler/target checks matched old constructor on h50 best; direct formula independently matches realizable E(C,V)')
    return row


def successor(anchor, prior):
    h, base, starting = anchor['h'], anchor['base'], anchor['positions']
    excluded = {job['candidate_id'] for job in prior['candidate_definitions']}
    excluded.add(queue.identity(h,base,starting)[1])
    if 'baseline_positions' in prior:
        excluded.add(queue.identity(h,base,prior['baseline_positions'])[1])
    for path in EXTRA_RUNS:
        value = json.loads((path/'protocol.json').read_text())
        excluded.update(job['candidate_id'] for job in value['candidate_definitions'])
        if 'baseline_positions' in value:
            excluded.add(queue.identity(h,base,value['baseline_positions'])[1])
    seen, rows = set(), []

    def append(positions,kind):
        assert len(positions)==h and all(0<=p<h//2 for p in positions)
        value,key = queue.identity(h,base,positions)
        if key in excluded or key in seen or len(rows)>=TARGET:
            return
        changed = [dict(common=c,old=old,new=new) for c,(old,new)
                   in enumerate(zip(starting,positions)) if old!=new]
        assert changed
        seen.add(key)
        rows.append(dict(value,candidate_id=key,neighborhood=kind,changed=changed))

    for common in range(h):
        old=starting[common]
        choices=[old-1,old+1] if 0<old<h//2-1 else ([1,2] if old==0 else [old-1,old-2])
        for new in choices:
            positions=list(starting);positions[common]=new
            append(positions,'individual-near-successor')
    for new in [0,1,2]:
        for common in range(h):
            positions=list(starting);positions[common]=new
            append(positions,'individual-early-successor')
    for new in [0,1]:
        for pair in range(h//2):
            positions=list(starting);positions[2*pair:2*pair+2]=[new,new]
            append(positions,'paired-early-successor')
    for size in [2,3,4,6,8,12,16,20,24,32,40,h]:
        if size<=h:
            positions=list(starting);positions[:size]=[0]*size
            append(positions,'early-prefix-successor')
    for common in sorted(set([0,1,2,3,h//4,h//4+1,h//2,h//2+1,h-2,h-1])):
        positions=list(starting);positions[common]=h//4
        append(positions,'middle-gap-successor')
    rng=random.Random(SEED)
    attempts=0
    while len(rows)<TARGET:
        attempts+=1;assert attempts<10000
        size=rng.choice([2,2,3,3,4,6,8])
        selected=rng.sample(range(h),size)
        positions=list(starting)
        for common in selected:
            positions[common]=rng.choice([0,0,1,2,max(0,starting[common]-1),min(h//2-1,starting[common]+1)])
        if positions!=starting:
            append(positions,'seeded-multiple-successor')
    assert len(rows)==len(seen)==TARGET and not seen.intersection(excluded)
    CONFIGURATION['neighborhood_counts']=dict(Counter(row['neighborhood'] for row in rows))
    return rows,sorted(excluded)


def predecessor_workers(path,maximum):
    if (path/'summary.json').exists():
        assert json.loads((path/'summary.json').read_text())['status'].startswith('Terminal')
        return 0
    checkpoint=json.loads((path/'checkpoint.json').read_text())
    settings=json.loads((path/'protocol.json').read_text())['settings']
    capacity=checkpoint.get('active_capacity',settings.get('workers',settings.get('max_workers',maximum)))
    remaining=checkpoint['planned_candidates']-checkpoint['completed_candidates']
    assert remaining>=0
    return max(1,min(int(capacity),remaining,maximum))


real_write_json=queue.write_json


def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:
        value=dict(value,successor_configuration=CONFIGURATION)
    real_write_json(path,value)


def main():
    global EXTRA_RUNS,SEED,TARGET
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--exclude-run',type=Path,action='append',default=[])
    ap.add_argument('--seed',type=int,default=109)
    ap.add_argument('--target-cases',type=int,default=420)
    args,remaining=ap.parse_known_args()
    EXTRA_RUNS=args.exclude_run;SEED=args.seed;TARGET=args.target_cases
    assert 300<=TARGET<=500
    direct=Path(__file__).with_name('fast_frame_envelope.py')
    assert sha256(direct.read_bytes()).hexdigest()==DIRECT_HASH
    CONFIGURATION.update(seed=SEED,target_cases=TARGET,direct_envelope_sha256=DIRECT_HASH,
        wrapper_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        exclude_protocols=[dict(path=str(path/'protocol.json'),sha256=sha256((path/'protocol.json').read_bytes()).hexdigest())
                           for path in EXTRA_RUNS],
        constructor_control_runs=['20261008T005237Z-direct-envelope-small','20261008T005626Z-direct-envelope-full'],
        scientific_boundary='Frozen exact evaluator and every verifier unchanged; only identical Space generation and fresh candidate definitions differ')
    queue.neighborhood=successor
    queue.predecessor_workers=predecessor_workers
    queue.evaluate=evaluate_direct
    queue.write_json=write_json
    sys.argv=[sys.argv[0],*remaining]
    queue.main()


if __name__=='__main__':
    main()
