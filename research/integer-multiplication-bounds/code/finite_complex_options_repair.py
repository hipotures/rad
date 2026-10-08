#!/usr/bin/env python3
"""Fresh no-symmetry continuation of individually bounded complex option attempts."""
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
import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers
import finite_complex_clone_nosym as options

CONFIG={};PARENTS={};EXCLUDED_CONFIGURATIONS=set();GROUNDS=[28,26,30,24,32,34,36]


def candidates(anchor, prior):
    rows=[]
    for limit in (2,4,8,12):
        for policy in ('wide','narrow','seeded'):
            for seed in (0,104729):
                for h in GROUNDS:
                    path=PARENTS[h]
                    if (h,limit,policy,seed) in EXCLUDED_CONFIGURATIONS:continue
                    definition=dict(h=h,option_limit=limit,frame_policy=policy,seed=seed,milp_seconds=6.0,
                        baseline_candidate_path=str(path),baseline_candidate_sha256=sha256(path.read_bytes()).hexdigest(),
                        option_source_sha256=sha256(Path(options.__file__).read_bytes()).hexdigest(),
                        evaluator_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                        reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2',
                        mechanism='multiple-binary-first-consumer-and-provider-options-with-exact-feasible-compatibility-MILP')
                    key=sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                    rows.append(dict(definition,candidate_id=key,neighborhood='complex-multi-provider-first-frame',
                        changed=[dict(ground=h,option_limit=limit,frame_policy=policy,seed=seed)]))
    assert len({row['candidate_id'] for row in rows})==len(rows)
    return rows,sorted(job['candidate_id'] for job in prior['candidate_definitions'])


def evaluate(job):
    cap=job['worker_address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    at=time.monotonic();cpu=time.process_time();path=Path(job['baseline_candidate_path'])
    assert sha256(path.read_bytes()).hexdigest()==job['baseline_candidate_sha256']
    assert sha256(Path(options.__file__).read_bytes()).hexdigest()==job['option_source_sha256']
    parent=json.loads(path.read_text())
    baseline=dict(logical=dict(circuit_sha256=parent['original_logical_sha256']),
        compiled_roles=parent['baseline_roles'],checked=dict(compiled_sha256=parent['original_compiled_sha256']))
    preparation=time.monotonic()-at
    row=options.case(job['h'],baseline,job['option_limit'],job['frame_policy'],job['seed'],job['milp_seconds'])
    row.update(candidate_id=job['candidate_id'],pid=os.getpid(),phase=job['phase'],elapsed_seconds=time.monotonic()-at,
        cpu_seconds=time.process_time()-cpu,phase_seconds=dict(pinned_original_identity_preparation=preparation,
            complete_new_multi_option_complex_witness=time.monotonic()-at-preparation),
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        baseline_candidate_path=str(path),baseline_candidate_sha256=job['baseline_candidate_sha256'],
        parent_delayed_roles=parent['compiled_roles'],additional_role_saving_over_parent=parent['compiled_roles']-row['compiled_roles'],
        original_coefficient_policy='Reuse pinned complete parent evidence; no original verify call; all new graph nodes and coefficients checked once',
        option_source_sha256=job['option_source_sha256'],evaluator_source_sha256=job['evaluator_source_sha256'])
    return row


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:
        value=dict(value,complex_option_configuration=CONFIG,
            scientific_boundary='Every new logical/physical/binary-Gram/phase/target/G/E check unchanged; exact dirty/stage promotion is separate')
        real_write_json(path,value)
        real_write_json(path.with_name('checkpoint.json'),dict(status='Initializing exact complex option cohort',
            dispatcher_pid=os.getpid(),planned_candidates=len(value['candidate_definitions']),
            submitted_candidates=0,completed_candidates=0,failed_candidates=0,active_capacity=0))
        return
    real_write_json(path,value)


def main():
    ap=argparse.ArgumentParser(add_help=False);ap.add_argument('--parent-run',type=Path,required=True)
    ap.add_argument('--small-control',type=Path,required=True);ap.add_argument('--prior-attempt',type=Path,required=True);args,remaining=ap.parse_known_args()
    for path in (args.prior_attempt/'cases').glob('*.json'):
        if '.error.' in path.name:continue
        previous=json.loads(path.read_text());choice=previous['complex_option_configuration']
        EXCLUDED_CONFIGURATIONS.add((previous['h'],choice['limit'],choice['policy'],choice['seed']))
    control=json.loads(args.small_control.read_text())
    assert control['status']=='Terminal exact offered-job identity and native no-symmetry complex witness PASS'
    assert control['new_option_source_sha256']==sha256(Path(options.__file__).read_bytes()).hexdigest()
    small=next(row for row in control['rows'] if row['h']==8)
    assert small['compiled_roles']==806 and small['complete_dirty_scalar_matrix']['forward_identity_shear_and_inverse_exact']
    assert small['complete_shared_three_stage'][0]['all_data_coordinates_and_shared_auxiliary_roles_exact']
    for path in (args.parent_run/'cases').glob('*.json'):
        if '.error.' in path.name:continue
        row=json.loads(path.read_text())
        if row['h'] in GROUNDS:PARENTS[row['h']]=path
    assert set(PARENTS)==set(GROUNDS)
    CONFIG.update(grounds=GROUNDS,native_mip_detect_symmetry=False,completed_predecessor_configurations_excluded=len(EXCLUDED_CONFIGURATIONS),options=[2,4,8,12],frame_policies=['wide','narrow','seeded'],seeds=[0,104729],
        small_control_path=str(args.small_control),small_control_sha256=sha256(args.small_control.read_bytes()).hexdigest(),
        historical_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z',
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_complex_clone_nosym.py','finite_complex_clone_options.py','finite_complex_delayed_clones.py','finite_complex_controller_reuse.py',
             'downstream_complex_circuit.py','review_complex_controller.py','frame_reuse.py','finite_clone_recovered_witness.py')})
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json;queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
