#!/usr/bin/env python3
"""Successive clone discriminator reconstructed from a complete saved parent."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

import finite_bit_clone_options as first
import finite_complex_clone_nosym as selector
from finite_clone_batch import serialized
from finite_clone_recovered_witness import recovered_plan,compiled_hash
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse


def case(parent,rounds=2,limit=4,policy='wide',seed=0,time_limit=6.0,dirty=False):
    at=time.monotonic();h=parent['h'];original=first.witness.build(h,parent['base'],parent['positions'])
    assert first.logical_identity(original)==parent['baseline']['circuit_sha256']
    old_frames,_=labels(original,True);old_plan=frame_reuse.optimize_chains(original,old_frames,'rank')
    old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
    assert old_code['roles']==parent['baseline']['roles'] and compiled_hash(old_code)==parent['baseline']['compiled_sha256']
    initial=[first.deserialize(job) for job in parent['chosen']]
    current=first.witness.DelayedCloneView(original,old_frames,initial)
    frames=first.witness.descendant_frames(original,old_frames,current,initial)
    plan=recovered_plan(original,old_plan,current,frames,initial)
    code=frame_reuse.compile_reuse(current,frames,plan)
    assert code['roles']==parent['compiled_roles'] and compiled_hash(code)==parent['checked']['compiled_sha256']
    assert first.logical_identity(current)==parent['final']['logical']['circuit_sha256']
    preparation=time.monotonic()-at;records=[]
    previous_clones=set(current.clones.values())
    previous_parent_copies={current.original_mapping[job['node']] for job in initial}
    total=0
    for iteration in range(rounds):
        start=time.monotonic();jobs,diagnostic=selector.opportunities(current,frames,plan,limit,policy,seed+iteration*1000003)
        chosen,_=selector.select(jobs,time_limit);old_roles=code['roles']
        providers={job['predecessor_gates'][1] for job in chosen}
        touches_previous_parent=sum(bool(set(job['original_children']) & previous_parent_copies) for job in chosen)
        touches_previous_clone=sum(bool(set(job['original_children']) & previous_clones) for job in chosen)
        record=dict(round=iteration+1,chosen=[serialized(job) for job in chosen],diagnostic=diagnostic,
            selection=selector.LAST_SELECTION,old_roles=old_roles,
            old_compiled_sha256=compiled_hash(code),old_logical_sha256=first.logical_identity(current),
            borrowed_previous_clone_providers=len(providers & previous_clones),
            chosen_parents_with_previous_cloned_original_child=touches_previous_parent,
            chosen_parents_with_previous_clone_child=touches_previous_clone)
        if not chosen:
            record.update(new_roles=old_roles,seconds=time.monotonic()-start);records.append(record);break
        view=first.witness.DelayedCloneView(current,frames,chosen)
        next_frames=first.witness.descendant_frames(current,frames,view,chosen)
        next_plan=recovered_plan(current,plan,view,next_frames,chosen)
        next_code=frame_reuse.compile_reuse(view,next_frames,next_plan)
        assert old_roles-next_code['roles']==len(chosen)
        assert len(next_plan[2])-len(plan[2])==2*len(chosen)
        previous_clones={view.original_mapping[node] for node in previous_clones}|set(view.clones.values())
        previous_parent_copies={view.original_mapping[node] for node in previous_parent_copies}|{view.original_mapping[job['node']] for job in chosen}
        record.update(new_roles=next_code['roles'],new_compiled_sha256=compiled_hash(next_code),
            new_logical_sha256=first.logical_identity(view),seconds=time.monotonic()-start)
        records.append(record);total+=len(chosen);current,frames,plan,code=view,next_frames,next_plan,next_code
    assert parent['compiled_roles']-code['roles']==total
    if not total:
        return dict(h=h,compiled_roles=code['roles'],parent_roles=parent['compiled_roles'],
            role_saving=0,rounds=records,pinned_parent_physical_evidence_reused=True,
            parent_compiled_sha256=parent['checked']['compiled_sha256'],elapsed_seconds=time.monotonic()-at)
    start=time.monotonic();logical=current.verify();checked=frame_reuse.check(current,frames,code)
    targets=target_check(current,frames,True)
    row=dict(h=h,base=parent['base'],positions=parent['positions'],compiled_roles=code['roles'],
        parent_roles=parent['compiled_roles'],role_saving=total,rounds=records,
        final=dict(logical=logical,checked=checked,roles=code['roles'],links=len(plan[2]),targets=targets),
        checked=checked,pinned_parent_physical_evidence_reused=False,
        pinned_parent_identity_reconstruction_seconds=preparation,
        final_changed_verification_seconds=time.monotonic()-start,
        frame_scope='Original and all prior enlarged first-consumer frames retained literally; later round clones inherit actual first consumer frame')
    if dirty:row['complete_small_controls']=first.witness.small_controls(current,frames,code)
    if h>=40:
        from finite_residual_rank_histogram import histogram
        from downstream_parameter_optimum import as_strings,saving_enclosure
        ranks=histogram(h,current,frames,code);v=len(current.inputs)
        G=3*v*v*(4*(current.additions+code['roles']-v)+20*v)
        E=64*(ranks['W']+ranks['m']+1)**3;depth=2*G*ranks['W']**2+4*ranks['s']+4*ranks['W']+4
        assert depth<E
        row.update(exact_counts=as_strings(ranks),residual_rank_histogram=as_strings(ranks),
            literal_scalar_guard=as_strings(dict(G=G,E=E,depth=depth,slack=E-depth)),
            uniform_shrink_saving=as_strings(saving_enclosure(Fraction(ranks['D'],ranks['W']*ranks['m']),ranks['m'])))
    row.update(elapsed_seconds=time.monotonic()-at,process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear();first.witness.GroupUnion.support_in.cache_clear()
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True);parser.add_argument('--parent',type=Path,required=True)
    parser.add_argument('--h',type=int);parser.add_argument('--rounds',type=int,default=2)
    parser.add_argument('--limit',type=int,default=4);parser.add_argument('--policy',choices=['wide','narrow','seeded'],default='wide')
    parser.add_argument('--seed',type=int,default=0);parser.add_argument('--time-limit',type=float,default=6)
    parser.add_argument('--dirty',action='store_true');parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists();first.witness.install_reference(args.reference)
    document=json.loads(args.parent.read_text())
    parent=next(row for row in document['rows'] if args.h is None or row['h']==args.h) if 'rows' in document else document
    definition=dict(parent_path=str(args.parent),parent_sha256=sha256(args.parent.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rounds=args.rounds,limit=args.limit,
        policy=args.policy,seed=args.seed,time_limit=args.time_limit)
    key=sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    at=time.monotonic();row=case(parent,args.rounds,args.limit,args.policy,args.seed,args.time_limit,args.dirty)
    row.update(candidate_id=key,parent_sha256=definition['parent_sha256'],parent_path=str(args.parent))
    value=dict(status='Terminal exact parent-reconstructed successive clone witness PASS',candidate_id=key,
        definition=definition,rows=[row],elapsed_seconds=time.monotonic()-at,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_bit_clone_options.py','finite_complex_clone_nosym.py','finite_clone_descendant_frame.py','finite_clone_recovered_witness.py')})
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(candidate_id=key,h=row['h'],roles=row['compiled_roles'],gain=row['role_saving'],
        round_clones=[len(r['chosen']) for r in row['rounds']],seconds=row['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
