#!/usr/bin/env python3
"""Bounded actual-role clone cohort over distinct frozen odd-ground witnesses.

Each input candidate was already checked by the unchanged position evaluator.
This experiment changes its DAG by a deterministic compatible clone batch,
reconstructs its exact baseline hash and checks the entire changed program.
It never describes the recovered feasible chain witness as an optimal flow.
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
import finite_clone_recovered_witness as witness

BASELINES = []; CONFIG = {}; TARGET = 210; CONTROL = None


def candidates(anchor, prior):
    existing = {}; grounds = (49,51,53)
    for root in BASELINES:
        for path in sorted((root/'cases').glob('*.json')):
            if path.name.endswith('.error.json'): continue
            row = json.loads(path.read_text())
            if row.get('h') not in grounds: continue
            assert row['base'] == 2 and row['positions'][-1] == 0
            existing.setdefault(row['candidate_id'], (row,path))
    ordered = {h:sorted((pair for pair in existing.values() if pair[0]['h']==h),
                         key=lambda pair:(pair[0]['compiled_roles'],pair[0]['candidate_id'])) for h in grounds}
    rows = []; seen = set(); control_inputs = set(CONTROL.get('candidate_input_sha256',[]) if isinstance(CONTROL.get('candidate_input_sha256'),list) else [CONTROL.get('candidate_input_sha256')])
    # Round-robin comparable grounds; actual supported savings are retained
    # separately from raw role count in every resulting certificate.
    for index in range(max(map(len,ordered.values()))):
        for h in grounds:
            if index >= len(ordered[h]) or len(rows) >= TARGET: continue
            old,path = ordered[h][index]; digest = sha256(path.read_bytes()).hexdigest()
            if digest in control_inputs: continue
            definition = dict(h=h,base=2,positions=old['positions'],baseline_candidate_id=old['candidate_id'],
                baseline_input_sha256=digest,clone_strategy='unused-P-plus-unused-earlier-Q-capacity-disjoint',
                witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
                reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
            key = sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            assert key not in seen;seen.add(key)
            rows.append(dict(definition,baseline_path=str(path),candidate_id=key,
                neighborhood='unused-controller-compatible-clones',
                changed=[dict(field='explicit-DAG-clones-and-feasible-controller-plan',baseline=old['candidate_id'])]))
    assert len(rows) == TARGET
    CONFIG.update(target=TARGET,grounds=grounds,per_ground=dict(Counter(row['h'] for row in rows)),
        prior_distinct_baselines=len(existing),excluded_control_sha256=sorted(x for x in control_inputs if x),
        scientific_question='Do explicit unused-controller clones improve actual roles across competitive odd-ground DAGs?',
        ranking='Raw roles are only comparable within one ground; every case also retains exact supported uniform saving')
    return rows, []


def evaluate(job):
    cap = job['worker_address_space_gib']*1024**3
    resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    witness.install_reference(job['reference']); at=time.monotonic(); cpu=time.process_time()
    path=Path(job['baseline_path']); assert sha256(path.read_bytes()).hexdigest()==job['baseline_input_sha256']
    baseline=json.loads(path.read_text())
    assert baseline['candidate_id']==job['baseline_candidate_id']
    row=witness.case(job['h'],job['base'],job['positions'],frozen=baseline,compare_frames=False,dirty=False)
    code=row.get('duplicated',row['baseline'])
    if 'duplicated' in row:
        ranks=row['exact_counts'];saving=row['uniform_shrink_saving']
    else:
        ranks=baseline['residual_rank_histogram'];saving=baseline['supported_uniform_shrink_saving']
    row['witness_phase_seconds']=row['phase_seconds']
    row.update(candidate_id=job['candidate_id'],baseline_candidate_id=baseline['candidate_id'],
        baseline_input_sha256=job['baseline_input_sha256'],baseline_path=str(path),
        compiled_roles=code['roles'],checked=code['checked'],pid=os.getpid(),phase=job['phase'],
        residual_rank_histogram=ranks,supported_uniform_shrink_saving=saving,
        cpu_seconds=time.process_time()-cpu,elapsed_seconds=time.monotonic()-at,
        phase_seconds={'complete_baseline_and_changed_clone_witness':time.monotonic()-at},
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        verification_scope='Entire changed logical/scalar/forward/reverse/target/rank witness; mapped frame identity controlled independently; dirty/stage promotion remains separate',
        clone_witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
        cohort_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    return row


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:
        value=dict(value,recovered_clone_configuration=CONFIG)
    real_write_json(path,value)


def main():
    global BASELINES, TARGET, CONTROL
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--baseline-run',action='append',type=Path,required=True)
    ap.add_argument('--clone-control',type=Path,required=True)
    ap.add_argument('--target-cases',type=int,default=210)
    args,remaining=ap.parse_known_args();BASELINES=args.baseline_run;TARGET=args.target_cases
    assert 100<=TARGET<=450
    CONTROL=json.loads(args.clone_control.read_text())
    assert CONTROL['status']=='Terminal exact recovered clone witness PASS'
    assert CONTROL['source_sha256']==sha256(Path(witness.__file__).read_bytes()).hexdigest()
    assert CONTROL['rows'][0]['h']==51 and CONTROL['rows'][0]['frame_identity_control']
    assert CONTROL['rows'][0]['role_saving']>0
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        witness_source_sha256=CONTROL['source_sha256'],control_sha256=sha256(args.clone_control.read_bytes()).hexdigest(),
        candidate_generation_sha256=sha256(Path(__file__).with_name('finite_clone_unused_capacity.py').read_bytes()).hexdigest(),
        process_lifetime='One graph per fresh process',historical_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json;queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
