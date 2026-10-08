#!/usr/bin/env python3
"""Distinct refined full-pair windows across the three competitive odd grounds.

The evaluator, constructor, exact frames and role histogram are frozen.
This thin dispatcher tests whether the new near-end placement at h51 also
improves h49/h53, with strict exclusion of both completed/live predecessors.
"""
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
from finite_odd_pair_cohort import identity, evaluate

EXCLUDE = []; ANCHORS = {}; CONFIG = {}; TARGET = 360; SEED = 110


def candidates(anchor, prior):
    assert anchor['h'] == 51 and anchor['base'] == 2
    excluded = {row['candidate_id'] for row in prior['candidate_definitions']}
    excluded.add(anchor['candidate_id'])
    for run in EXCLUDE:
        protocol = json.loads((run/'protocol.json').read_text())
        excluded.update(row['candidate_id'] for row in protocol['candidate_definitions'])
    anchors = {**ANCHORS, 51: anchor}; grounds = [49, 51, 53]
    rows = []; seen = set()
    def append(h, positions, kind):
        value, key = identity(h, positions)
        if key in excluded or key in seen or len(rows) >= TARGET: return
        seen.add(key)
        rows.append(dict(value, candidate_id=key, neighborhood=kind,
                         changed=[dict(field='refined_odd_ground_window', h=h, pattern=kind)]))
    # Round-robin grounds avoid an entire ground awaiting late admission.
    for delta in (0, 1, -1, 2, -2, 3, -3):
        for begin in (6, 8, 4, 10, 2, 0, 7, 5, 9, 3, 1):
            for back in (1, 2, 0, 3):
                for h in grounds:
                    k = (h-1)//2; length = k+delta
                    positions = [0]*h
                    if begin+length > h-1: continue
                    positions[begin:begin+length] = [k-1-back]*length
                    append(h, positions, 'odd-cross-ground-window')
    rng = random.Random(SEED); attempts = 0
    while len(rows) < TARGET:
        attempts += 1; assert attempts < 30000
        h = grounds[(attempts-1) % len(grounds)]; k = (h-1)//2
        positions = list(anchors[h]['positions'])
        nonzero = [i for i, value in enumerate(positions[:-1]) if value]
        left, right = min(nonzero), max(nonzero)
        endpoints = sorted(set(range(max(0,left-4), min(h-1,left+5))) |
                           set(range(max(0,right-4), min(h-1,right+5))))
        for common in rng.sample(endpoints, rng.choice((2, 3, 4, 6))):
            positions[common] = rng.choice((0, 1, k-1, k-2, k-3))
        append(h, positions, 'odd-cross-ground-multiorphan')
    assert len(rows) == len(seen) == TARGET and not seen & excluded
    CONFIG.update(seed=SEED, grounds=grounds, target=TARGET,
                  neighborhoods=dict(Counter(row['neighborhood'] for row in rows)),
                  per_ground=dict(Counter(row['h'] for row in rows)),
                  excluded_count=len(excluded),
                  scientific_question='Does the h51 near-end full-pair/window improvement transfer to h49/h53 under actual physical roles?',
                  aliases='Final special-point position always0; unchanged base2 and construction identity')
    return rows, sorted(excluded)


original_write = queue.write_json
def write_json(path, value):
    if path.name == 'protocol.json' and 'candidate_definitions' in value:
        value = dict(value, odd_window_transfer=CONFIG)
    original_write(path, value)


def main():
    global EXCLUDE, ANCHORS, TARGET, SEED
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--exclude-run', action='append', type=Path, default=[])
    ap.add_argument('--ground-anchor', action='append', type=Path, default=[])
    ap.add_argument('--target-cases', type=int, default=360); ap.add_argument('--seed', type=int, default=110)
    args, remaining = ap.parse_known_args(); EXCLUDE=args.exclude_run; TARGET=args.target_cases; SEED=args.seed
    assert 200 <= TARGET <= 500
    ANCHORS = {json.loads(path.read_text())['h']: json.loads(path.read_text()) for path in args.ground_anchor}
    assert set(ANCHORS) == {49, 53}
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  frozen_evaluator_sha256=sha256(Path(__file__).with_name('finite_odd_pair_cohort.py').read_bytes()).hexdigest(),
                  frozen_constructor_sha256=sha256(Path(__file__).with_name('finite_odd_pair_positions.py').read_bytes()).hexdigest(),
                  exclusion_protocol_sha256={str(path):sha256((path/'protocol.json').read_bytes()).hexdigest() for path in EXCLUDE},
                  other_anchor_sha256={str(path):sha256(path.read_bytes()).hexdigest() for path in args.ground_anchor},
                  process_lifetime='One candidate per fresh process',
                  historical_deadline='2026-10-08T08:25:21Z', active_deadline='2026-10-08T10:00:00Z')
    queue.neighborhood=candidates; queue.evaluate=evaluate; queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json; queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining]; queue.main()


if __name__ == '__main__': main()
