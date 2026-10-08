#!/usr/bin/env python3
"""Successive explicit clones using actual inherited first-consumer frames.

Each new gate has a fresh unused provider capacity. Later rounds may use that
capacity for another complete-chain clone. Old frames are retained literally;
canonical support envelopes are never substituted for enlarged clone frames.
Only the final changed graph is replayed, with every round's recovered links
and explicit jobs preserved for independent reconstruction.
"""
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
from finite_clone_recovered_witness import recovered_plan, compiled_hash
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse


def case(h,base,positions,rounds=3,limit=4,policy='wide',seed=0,time_limit=6.0,dirty=False,frozen=None):
    at=time.monotonic();original=first.witness.build(h,base,positions)
    frames,_=labels(original,True);plan=frame_reuse.optimize_chains(original,frames,'rank')
    code=frame_reuse.compile_reuse(original,frames,plan)
    if frozen:
        assert first.logical_identity(original)==frozen.get('logical',frozen.get('original'))['circuit_sha256']
        assert code['roles']==frozen['compiled_roles']
        assert compiled_hash(code)==frozen.get('checked',frozen.get('compiled'))['compiled_sha256']
    baseline=dict(roles=code['roles'],logical_sha256=first.logical_identity(original),compiled_sha256=compiled_hash(code))
    records=[];current=original;initial_clone_nodes=set();total=0
    for iteration in range(rounds):
        start=time.monotonic();jobs,diagnostic=selector.opportunities(current,frames,plan,limit,policy,seed+iteration*1000003)
        chosen,_=selector.select(jobs,time_limit)
        providers={job['predecessor_gates'][1] for job in chosen}
        borrowed_previous_clones=len(providers & initial_clone_nodes)
        old_roles=code['roles'];old_hash=compiled_hash(code)
        if not chosen:
            records.append(dict(round=iteration+1,chosen=[],diagnostic=diagnostic,selection=selector.LAST_SELECTION,
                old_roles=old_roles,new_roles=old_roles,borrowed_previous_clone_providers=0,
                seconds=time.monotonic()-start));break
        view=first.witness.DelayedCloneView(current,frames,chosen)
        enlarged=first.witness.descendant_frames(current,frames,view,chosen)
        next_plan=recovered_plan(current,plan,view,enlarged,chosen)
        next_code=frame_reuse.compile_reuse(view,enlarged,next_plan)
        assert old_roles-next_code['roles']==len(chosen)
        assert len(next_plan[2])-len(plan[2])==2*len(chosen)
        previous_clone_nodes={view.original_mapping[node] for node in initial_clone_nodes}
        current_clone_nodes=set(view.clones.values())
        record=dict(round=iteration+1,chosen=[serialized(job) for job in chosen],
            diagnostic=diagnostic,selection=selector.LAST_SELECTION,
            old_roles=old_roles,new_roles=next_code['roles'],old_compiled_sha256=old_hash,
            new_compiled_sha256=compiled_hash(next_code),
            old_logical_sha256=first.logical_identity(current),new_logical_sha256=first.logical_identity(view),
            borrowed_previous_clone_providers=borrowed_previous_clones,
            actual_enlarged_frame_count=len(current_clone_nodes),
            scalar_role_gain=len(chosen),extra_links=2*len(chosen),seconds=time.monotonic()-start)
        records.append(record);total+=len(chosen)
        initial_clone_nodes=previous_clone_nodes | current_clone_nodes
        current,frames,plan,code=view,enlarged,next_plan,next_code
    start=time.monotonic();logical=current.verify();checked=frame_reuse.check(current,frames,code)
    targets=target_check(current,frames,True)
    assert baseline['roles']-code['roles']==total
    row=dict(h=h,base=base,positions=positions,baseline=baseline,rounds=records,
        compiled_roles=code['roles'],total_clones=total,
        final=dict(logical=logical,checked=checked,roles=code['roles'],links=len(plan[2]),targets=targets),
        final_all_changed_verification_seconds=time.monotonic()-start,
        frame_scope='Every original frame retained literally; each later clone inherits its actual first consumer frame; never replace enlarged frames with canonical support envelopes')
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
    parser.add_argument('--reference',required=True);parser.add_argument('--h',type=int,nargs='+',default=[8,12])
    parser.add_argument('--rounds',type=int,default=3);parser.add_argument('--limit',type=int,default=4)
    parser.add_argument('--policy',choices=['wide','narrow','seeded'],default='wide');parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--time-limit',type=float,default=6);parser.add_argument('--dirty-ground',type=int,default=12)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    assert not args.output.exists();first.witness.install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',rows=[],source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_bit_clone_options.py','finite_complex_clone_nosym.py','finite_clone_descendant_frame.py','finite_clone_recovered_witness.py')},
        started_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        positions=[0]*(h//2-1)+[h//2-2]*(h//2+1)
        row=case(h,2,positions,args.rounds,args.limit,args.policy,args.seed,args.time_limit,h==args.dirty_ground)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],round_clones=[len(r['chosen']) for r in row['rounds']],
            borrowed_previous_clones=[r['borrowed_previous_clone_providers'] for r in row['rounds']],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact successive actual-frame clone witness PASS',
        elapsed_seconds=time.monotonic()-at,completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
