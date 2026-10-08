#!/usr/bin/env python3
"""Distinct delayed-frame clone hypotheses on saved competitive bit graphs.

Only the positive small discriminator is prerequisite for this exploratory
cohort. Every changed large graph receives the full existing finite checks;
independent promotion and the new frame-transfer proof remain separate.
"""
from __future__ import annotations
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import sys
import time

import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers
import finite_clone_descendant_frame as witness

BASELINES=[];CONFIG={};TARGET=300;EXCLUDED_HASHES=set()


def candidates(anchor,prior):
    existing={};grounds=(49,50,51,52,53)
    for root in BASELINES:
        for path in sorted((root/'cases').glob('*.json')):
            if path.name.endswith('.error.json'):continue
            row=json.loads(path.read_text())
            if row.get('h') not in grounds or row.get('base')!=2:continue
            if row['h']%2:assert row['positions'][-1]==0
            existing.setdefault(row['candidate_id'],(row,path))
    ordered={h:sorted((pair for pair in existing.values() if pair[0]['h']==h),
        key=lambda pair:(pair[0]['compiled_roles'],pair[0]['candidate_id'])) for h in grounds}
    rows=[];seen=set()
    for index in range(max(map(len,ordered.values()))):
        for h in grounds:
            if index>=len(ordered[h]) or len(rows)>=TARGET:continue
            baseline,path=ordered[h][index];digest=sha256(path.read_bytes()).hexdigest()
            if digest in EXCLUDED_HASHES:continue
            definition=dict(h=h,base=2,positions=baseline['positions'],baseline_candidate_id=baseline['candidate_id'],
                baseline_input_sha256=digest,clone_strategy='delayed-first-use-envelope-plus-unused-P-Q-capacities',
                witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
                reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
            key=sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            assert key not in seen;seen.add(key)
            rows.append(dict(definition,baseline_path=str(path),candidate_id=key,
                neighborhood='delayed-first-use-positive-envelope-clones',changed=[dict(field='explicit-clone-placement-and-frame',baseline=baseline['candidate_id'])]))
    assert len(rows)==TARGET
    CONFIG.update(target=TARGET,grounds=grounds,per_ground=dict(Counter(row['h'] for row in rows)),
        distinct_baselines_available=len(existing),excluded_baseline_sha256=sorted(EXCLUDED_HASHES),
        scientific_question='Does delayed first-use frame cloning improve supported bit saving across nearby competitive grounds?',
        ranking='Compare physical roles within a ground; exact uniform saving and changed residual rank histogram retained separately')
    return rows,[]


def evaluate(job):
    cap=job['worker_address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    witness.install_reference(job['reference']);at=time.monotonic();cpu=time.process_time()
    path=Path(job['baseline_path']);assert sha256(path.read_bytes()).hexdigest()==job['baseline_input_sha256']
    frozen=json.loads(path.read_text());assert frozen['candidate_id']==job['baseline_candidate_id']
    if 'logical' not in frozen:frozen={**frozen,'logical':frozen['original']}
    if 'checked' not in frozen:frozen={**frozen,'checked':frozen['compiled']}
    row=witness.case(job['h'],job['base'],job['positions'],frozen=frozen,dirty=False)
    row.update(candidate_id=job['candidate_id'],baseline_candidate_id=frozen['candidate_id'],baseline_path=str(path),
        baseline_input_sha256=job['baseline_input_sha256'],compiled_roles=row['final']['roles'],checked=row['final']['checked'],
        residual_rank_histogram=row['exact_counts'],supported_uniform_shrink_saving=row['uniform_shrink_saving'],
        pid=os.getpid(),phase=job['phase'],elapsed_seconds=time.monotonic()-at,cpu_seconds=time.process_time()-cpu,
        phase_seconds={'complete_baseline_and_delayed_clone_witness':time.monotonic()-at},
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
        cohort_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        verification_scope='Complete changed scalar/positive-frame/physical-target/rank witness; clones inherit actual first-use frames, independent promotion separate')
    return row


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:value=dict(value,delayed_clone_configuration=CONFIG)
    real_write_json(path,value)


def main():
    global BASELINES,TARGET,EXCLUDED_HASHES
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--baseline-run',type=Path,action='append',required=True)
    ap.add_argument('--small-control',type=Path,required=True);ap.add_argument('--exclude-baseline',type=Path,action='append',default=[])
    ap.add_argument('--target-cases',type=int,default=300)
    args,remaining=ap.parse_known_args();BASELINES=args.baseline_run;TARGET=args.target_cases
    assert 100<=TARGET<=450
    control=json.loads(args.small_control.read_text())
    assert control['status']=='Terminal exact descendant-frame clone witness PASS'
    assert control['source_sha256']==sha256(Path(witness.__file__).read_bytes()).hexdigest()
    small=next(row for row in control['rows'] if row['h']==12)
    assert small['role_saving']==130 and small['complete_small_controls']['complete_center_dirty_bases'][0]['exact_linear_map']
    EXCLUDED_HASHES={sha256(path.read_bytes()).hexdigest() for path in args.exclude_baseline}
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),witness_source_sha256=control['source_sha256'],
        small_control_sha256=sha256(args.small_control.read_bytes()).hexdigest(),
        process_lifetime='One full changed graph per fresh process',historical_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z',
        scientific_boundary='New delayed-frame family is exploratory until independent all-size and full changed-candidate promotion')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json;queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
