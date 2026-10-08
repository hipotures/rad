#!/usr/bin/env python3
"""Ground/graph study for exact ranks and prospective rank batching.

The frozen full bit evaluator constructs and checks each new graph once.
A process-local observer captures its unchanged compilation, then extracts
the exact rank histogram. Supported uniform-shrink saving is recorded
separately from the hypothetical one-child batching score.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

import finite_singleton_neighborhood as queue
from finite_singleton_successor import evaluate_direct,predecessor_workers
from finite_residual_rank_histogram import histogram

GROUNDS=list(range(40,60,2));EXTRA=[];CONFIG={}
real_write_json=queue.write_json


def candidates(anchor,prior):
    excluded={anchor['candidate_id']}
    for protocol in [prior,*[json.loads((path/'protocol.json').read_text()) for path in EXTRA]]:
        for row in protocol['candidate_definitions']:
            if row.get('sum_rule_early',0) in (0,1) and row.get('sum_rule_late',0) in (0,1):
                base=2 if row['base']==3 else row['base']
                excluded.add(queue.identity(row['h'],base,row['positions'])[1])
    seen=set();rows=[]
    patterns={}
    for h in GROUNDS:
        half=h//2
        gaps=sorted(set([0,1,2,3,half//2-1,half//2,half//2+1,
            half-7,half-6,half-5,half-4,half-3,half-2,half-1]))
        values=[([gap]*h,'uniform-singleton-'+str(gap)) for gap in gaps if 0<=gap<half]
        for length in (half-1,half+1,half+3):
            for start in (0,2,4,6,8,10):
                positions=[0]*h
                for offset in range(length):positions[(start+offset)%h]=half-2
                values.append((positions,'late-window-'+str(start)+'-'+str(length)))
        patterns[h]=values
    # Round-robin grounds bounds aggregate RAM and samples the whole range
    # early, so a time-limited partial run remains informative.
    for index in range(max(map(len,patterns.values()))):
        for h in GROUNDS:
            if index>=len(patterns[h]):continue
            positions,kind=patterns[h][index]
            value,key=queue.identity(h,2,positions)
            if key in seen or key in excluded:continue
            seen.add(key);rows.append(dict(value,candidate_id=key,neighborhood='residual-rank-'+kind,
                changed=[dict(field='ground_and_position_pattern',h=h,pattern=kind)]))
    assert len(rows)==len(seen) and not seen&excluded
    CONFIG.update(grounds=GROUNDS,planned_candidates=len(rows),semantic_exclusion='Canonical rule0/1 and cutoff2/3 prior identities normalized',
        scientific_scope='New ground40..58 cutoff2 physical graphs; exact supported uniform-shrink saving and independently marked hypothetical rank-batched score')
    return rows,sorted(excluded)


def evaluate(job):
    import frame_reuse
    captured={};original=frame_reuse.compile_reuse
    def observe(circuit,spaces,plan):
        code=original(circuit,spaces,plan)
        captured.update(circuit=circuit,spaces=spaces,code=code)
        return code
    with patch.object(frame_reuse,'compile_reuse',observe):row=evaluate_direct(job)
    assert frame_reuse.compile_reuse is original and captured
    histogram_start=time.monotonic();histogram_cpu=time.process_time()
    ranks=histogram(job['h'],captured['circuit'],captured['spaces'],captured['code'])
    assert ranks['side_roles']==row['compiled_roles']
    from fractions import Fraction
    from downstream_parameter_optimum import saving_enclosure,as_strings
    from reuse_network import triple_matching
    triples,images=triple_matching(job['h'])
    assert len(set(images))==len(triples)
    assert all(len(set(t)&set(triples[j]))==1 for t,j in zip(triples,images))
    row.update(residual_rank_histogram=ranks,
        supported_uniform_shrink_saving=as_strings(saving_enclosure(Fraction(ranks['D'],ranks['W']*ranks['m']),ranks['m'])),
        stage_matching=dict(bijection=True,every_match_intersects_in_one=True,triples=len(triples)),
        histogram_source_sha256=sha256(Path(__file__).with_name('finite_residual_rank_histogram.py').read_bytes()).hexdigest(),
        batch_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        ranking_scope='Raw roles comparable only at fixed ground; final batch rescoring uses supported saving. Rank-batched score remains hypothetical.')
    row['phase_seconds']['residual_histogram_and_matching']=time.monotonic()-histogram_start
    row['elapsed_seconds']+=row['phase_seconds']['residual_histogram_and_matching']
    row['cpu_seconds']+=time.process_time()-histogram_cpu
    return row


def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:
        value=dict(value,residual_ground_configuration=CONFIG)
    real_write_json(path,value)


def main():
    global GROUNDS,EXTRA
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--grounds',type=int,nargs='+',default=GROUNDS)
    ap.add_argument('--exclude-run',type=Path,action='append',default=[])
    args,remaining=ap.parse_known_args();GROUNDS=args.grounds;EXTRA=args.exclude_run
    assert all(h>=40 and h%2==0 for h in GROUNDS) and len(GROUNDS)==len(set(GROUNDS))
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        histogram_source_sha256=sha256(Path(__file__).with_name('finite_residual_rank_histogram.py').read_bytes()).hexdigest(),
        observer_scope='Original compile_reuse called exactly once; returned code untouched; all frozen checks execute before histogram extraction',
        campaign_original_deadline='2026-10-08T08:25:21Z',campaign_user_extended_deadline='2026-10-08T10:00:00Z')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers;queue.write_json=write_json
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
