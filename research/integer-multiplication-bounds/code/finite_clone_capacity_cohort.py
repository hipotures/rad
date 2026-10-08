#!/usr/bin/env python3
"""Capacity-selection refinement of frozen delayed-frame clone witnesses.

Identical explicit job lists reuse their already verified physical witness.
Every strict change receives complete scalar/frame/target/rank checks.
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
from fractions import Fraction

import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers
import finite_clone_capacity_matching as matching
import finite_clone_descendant_frame as witness
from finite_clone_batch import serialized
from finite_clone_recovered_witness import compiled_hash,recovered_plan
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse

PARENT_RUN=None;CONFIG={};TARGET=300


def candidates(anchor,prior):
    rows=[]
    definitions=prior['candidate_definitions']
    for old in definitions[:TARGET]:
        path=PARENT_RUN/'cases'/(old['candidate_id']+'.json')
        assert path.exists(), 'Only completed immutable parent witnesses are admitted'
        digest=sha256(path.read_bytes()).hexdigest()
        definition=dict(h=old['h'],base=old['base'],positions=old['positions'],
            parent_candidate_id=old['candidate_id'],parent_path=str(path),parent_sha256=digest,
            clone_strategy='pseudoforest-capacity-matching-plus-conservative-source-conflicts',
            matching_source_sha256=sha256(Path(matching.__file__).read_bytes()).hexdigest(),
            witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),
            reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
        key=sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        rows.append(dict(definition,candidate_id=key,neighborhood='capacity-compatible-delayed-clones',
            changed=[dict(field='clone-job-selection',parent=old['candidate_id'])]))
    assert len(rows)==TARGET and len({row['candidate_id'] for row in rows})==TARGET
    CONFIG.update(target=TARGET,per_ground=dict(Counter(row['h'] for row in rows)),
        scientific_question='Can exact capacity matchings recover more compatible delayed-clone jobs?',
        unchanged_case_policy='Exact equality of complete explicit job list permits reuse of immutable complete parent physical checks')
    return rows,[]


def evaluate(job):
    cap=job['worker_address_space_gib']*1024**3;resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    witness.install_reference(job['reference']);at=time.monotonic();cpu=time.process_time()
    path=Path(job['parent_path']);assert sha256(path.read_bytes()).hexdigest()==job['parent_sha256']
    parent=json.loads(path.read_text());assert parent['candidate_id']==job['parent_candidate_id']
    old_path=Path(parent['baseline_path']);assert sha256(old_path.read_bytes()).hexdigest()==parent['baseline_input_sha256']
    frozen=json.loads(old_path.read_text())
    logical_frozen=frozen.get('logical',frozen.get('original'))
    compiled_frozen=frozen.get('checked',frozen.get('compiled'))
    original=witness.build(job['h'],job['base'],job['positions']);logical=original.verify();assert logical==logical_frozen
    old_frames,_=labels(original,True);old_plan=frame_reuse.optimize_chains(original,old_frames,'rank')
    old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
    assert old_code['roles']==frozen['compiled_roles'] and compiled_hash(old_code)==compiled_frozen['compiled_sha256']
    construct_seconds=time.monotonic()-at
    jobs,diagnostic=witness.opportunities(original,old_frames,old_plan)
    chosen,rejected=matching.select(jobs)
    serialized_chosen=[serialized(value) for value in chosen]
    selection=matching.LAST_SELECTION
    assert selection['original_greedy_clones']==len(parent['chosen'])
    if len(chosen)==len(parent['chosen']):
        assert serialized_chosen==parent['chosen'], 'Only literal unchanged job lists may reuse physical verification'
        row={**parent,'capacity_selection':selection,'physical_witness_reused':True,
            'reused_physical_sha256':job['parent_sha256'],'strict_selection_gain':0}
        verification_seconds=0.0
    else:
        assert len(chosen)>len(parent['chosen'])
        before=time.monotonic()
        view=witness.DelayedCloneView(original,old_frames,chosen)
        frames=witness.descendant_frames(original,old_frames,view,chosen)
        plan=recovered_plan(original,old_plan,view,frames,chosen)
        code=frame_reuse.compile_reuse(view,frames,plan)
        logical_new=view.verify();checked=frame_reuse.check(view,frames,code);targets=target_check(view,frames,True)
        assert old_code['roles']-code['roles']==len(chosen)
        from finite_residual_rank_histogram import histogram
        from downstream_parameter_optimum import as_strings,saving_enclosure
        ranks=histogram(job['h'],view,frames,code)
        v=len(view.inputs);G=3*v*v*(4*(view.additions+code['roles']-v)+20*v);E=64*(ranks['W']+ranks['m']+1)**3
        depth=2*G*ranks['W']**2+4*ranks['s']+4*ranks['W']+4;assert E>depth
        row=dict(h=job['h'],base=job['base'],positions=job['positions'],baseline=parent['baseline'],
            baseline_candidate_id=parent['baseline_candidate_id'],baseline_path=parent['baseline_path'],
            baseline_input_sha256=parent['baseline_input_sha256'],opportunity_diagnostic=diagnostic,
            chosen=serialized_chosen,conflict_rejected=len(rejected),capacity_selection=selection,
            final=dict(logical=logical_new,roles=code['roles'],links=len(plan[2]),checked=checked,targets=targets,chains=plan[4]),
            exact_counts=as_strings(ranks),literal_scalar_guard=as_strings(dict(G=G,E=E,depth=depth,slack=E-depth)),
            uniform_shrink_saving=as_strings(saving_enclosure(Fraction(ranks['D'],ranks['W']*ranks['m']),ranks['m'])),
            role_saving=len(chosen),strict_selection_gain=len(chosen)-len(parent['chosen']),physical_witness_reused=False,
            frame_scope=parent['frame_scope'])
        verification_seconds=time.monotonic()-before
    row.update(candidate_id=job['candidate_id'],parent_candidate_id=job['parent_candidate_id'],
        parent_path=str(path),parent_sha256=job['parent_sha256'],compiled_roles=row['final']['roles'],checked=row['final']['checked'],
        residual_rank_histogram=row['exact_counts'],supported_uniform_shrink_saving=row['uniform_shrink_saving'],
        pid=os.getpid(),phase=job['phase'],elapsed_seconds=time.monotonic()-at,cpu_seconds=time.process_time()-cpu,
        phase_seconds=dict(baseline_reconstruction=construct_seconds,strict_changed_physical_verification=verification_seconds),
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        matching_source_sha256=sha256(Path(matching.__file__).read_bytes()).hexdigest(),
        cohort_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        verification_scope='Identical explicit job lists reuse exact immutable parent checks; every strict new clone set fully verified, independent promotion separate')
    frame_reuse.included.cache_clear();witness.GroupUnion.support_in.cache_clear();return row


real_write_json=queue.write_json
def write_json(path,value):
    if path.name=='protocol.json' and 'candidate_definitions' in value:value=dict(value,capacity_clone_configuration=CONFIG)
    real_write_json(path,value)


def main():
    global PARENT_RUN,TARGET
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--parent-run',type=Path,required=True);ap.add_argument('--small-control',type=Path,required=True)
    ap.add_argument('--target-cases',type=int,default=300)
    args,remaining=ap.parse_known_args();PARENT_RUN=args.parent_run;TARGET=args.target_cases
    control=json.loads(args.small_control.read_text())
    assert control['status']=='Terminal exact capacity-selection clone witness PASS'
    assert control['source_sha256']==sha256(Path(matching.__file__).read_bytes()).hexdigest()
    small=next(row for row in control['rows'] if row['h']==12)
    assert small['capacity_selection']['improvement_over_greedy']==4
    assert small['complete_small_controls']['complete_center_dirty_bases'][0]['exact_linear_map']
    CONFIG.update(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        matching_source_sha256=control['source_sha256'],small_control_sha256=sha256(args.small_control.read_bytes()).hexdigest(),
        historical_deadline='2026-10-08T08:25:21Z',active_deadline='2026-10-08T10:00:00Z',
        process_lifetime='One selection hypothesis per fresh process')
    queue.neighborhood=candidates;queue.evaluate=evaluate;queue.predecessor_workers=predecessor_workers
    queue.write_json=write_json;queue.ProcessPoolExecutor=partial(ProcessPoolExecutor,max_tasks_per_child=1)
    sys.argv=[sys.argv[0],*remaining];queue.main()


if __name__=='__main__':main()
