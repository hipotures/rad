#!/usr/bin/env python3
"""New complex delayed-clone grounds with exact binary phase verification."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import sys
import time
from unittest.mock import patch

import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers
import finite_complex_delayed_clones as witness
from finite_clone_recovered_witness import compiled_hash
import frame_reuse

BASELINES=[];CONFIG={}
GROUNDS=[10,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42]


def candidates(anchor,prior):
    rows=[]
    for h in GROUNDS:
        definition=dict(h=h,clone_strategy='binary-nonalternating-delayed-first-consumer-plus-feasible-MILP',
            witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
            evaluator_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
            reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
        key=sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        rows.append(dict(definition,candidate_id=key,neighborhood='new-complex-delayed-ground',
            changed=[dict(field='ground-and-delayed-binary-clones',h=h)]))
    return rows,[]


def evaluate(job):
    cap=job['worker_address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    at=time.monotonic();cpu=time.process_time();saved=None;source=None
    for path in BASELINES:
        value=json.loads(path.read_text())
        for row in value['rows']:
            if row['h']==job['h']:saved=row;source=path;break
        if saved:break
    original=None
    if saved is None:
        original=witness.TripleSideCircuit(job['h']);frames,_=witness.binary.labels(original)
        with patch.object(frame_reuse,'included',witness.binary.admissible):
            plan=frame_reuse.optimize_chains(original,frames,'rank');code=frame_reuse.compile_reuse(original,frames,plan)
        saved=dict(logical=dict(circuit_sha256=witness.logical_identity(original)),
            compiled_roles=code['roles'],checked=dict(compiled_sha256=compiled_hash(code)))
        # This is only an unverified baseline identity. The complete changed
        # view includes every original active node and verifies all maps once.
    preparation=time.monotonic()-at
    if original is None:row=witness.case(job['h'],saved,False,False)
    else:
        with patch.object(witness,'TripleSideCircuit',lambda h:original):row=witness.case(job['h'],saved,False,False)
    row.update(candidate_id=job['candidate_id'],pid=os.getpid(),phase=job['phase'],elapsed_seconds=time.monotonic()-at,
        cpu_seconds=time.process_time()-cpu,phase_seconds=dict(baseline_identity_preparation=preparation,
            complete_changed_complex_witness=time.monotonic()-at-preparation),
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        original_coefficient_evidence_reused_by_pinned_identity=source is not None,
        accepted_original_certificate_path=str(source) if source else None,
        accepted_original_certificate_sha256=sha256(source.read_bytes()).hexdigest() if source else None,
        new_ground_whole_changed_verification=source is None,
        witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
        evaluator_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    return row


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:value=dict(value,complex_clone_configuration=CONFIG)
    real_write_json(path,value)


def main():
    global BASELINES
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--baseline',type=Path,action='append',required=True);ap.add_argument('--small-control',type=Path,required=True)
    args,remaining=ap.parse_known_args();BASELINES=args.baseline
    control=json.loads(args.small_control.read_text())
    assert control['status']=='Terminal full finite nonalternating complex delayed-clone witness PASS'
    assert control['source_sha256']==sha256(Path(witness.__file__).read_bytes()).hexdigest()
    small=next(row for row in control['rows'] if row['h']==8)
    assert small['role_saving']==12 and small['complete_dirty_scalar_matrix']['forward_identity_shear_and_inverse_exact']
    assert small['complete_shared_three_stage'][0]['all_data_coordinates_and_shared_auxiliary_roles_exact']
    CONFIG.update(grounds=GROUNDS,small_control_sha256=sha256(args.small_control.read_bytes()).hexdigest(),
        witness_source_sha256=control['source_sha256'],historical_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z',
        baseline_policy='Accepted originals reuse pinned coefficient evidence; new grounds verify the complete changed graph once',
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_complex_controller_reuse.py','downstream_complex_circuit.py','downstream_complex_certificate.py',
             'finite_clone_compatibility_milp.py','review_complex_controller.py','frame_reuse.py')})
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json;queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
