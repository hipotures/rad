#!/usr/bin/env python3
"""Several exact rational-envelope clone choices with a bounded native solver.

Offer multiple complete output chains and unused providers for each old sum.
The all-size delayed-frame proof applies to every offered choice separately.
An integer-audited compatibility subset supplies two links per new clone.
Every strict new subset receives the complete changed coefficient, physical,
forward/complement/target, rank histogram and guard checks. Exact old clone
lists are retained on ties; their pinned physical evidence is then reused.
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

import finite_clone_descendant_frame as witness
import finite_complex_clone_nosym as options
from finite_clone_batch import serialized
from finite_clone_chain_bridge import bridge_compatible
from finite_clone_recovered_witness import compiled_hash, recovered_plan
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse


def logical_identity(circuit):
    digest=sha256()
    for node in sorted(circuit.active):
        digest.update(json.dumps((node,circuit.args[node],circuit.provenance[node]),separators=(',',':')).encode()+b'\n')
    for (common,target),node in sorted(circuit.outputs.items()):
        digest.update(json.dumps((common,target,node),separators=(',',':')).encode()+b'\n')
    return digest.hexdigest()


def deserialize(row):
    result=dict(row)
    result['selected']=frozenset((kind,tuple(owner) if isinstance(owner,list) else owner)
                                for kind,owner in result['selected'])
    return result


def case(h,base,positions,limit=4,policy='wide',seed=0,time_limit=6.0,frozen=None,parent=None,dirty=False):
    at=time.monotonic();phases={};original=witness.build(h,base,positions)
    original_identity=logical_identity(original)
    if frozen:
        assert original_identity==frozen.get('logical',frozen.get('original'))['circuit_sha256']
        assert (h,base,positions)==(frozen['h'],frozen['base'],frozen['positions'])
    old_frames,_=labels(original,True);old_plan=frame_reuse.optimize_chains(original,old_frames,'rank')
    old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
    if frozen:
        assert old_code['roles']==frozen['compiled_roles']
        assert compiled_hash(old_code)==frozen.get('checked',frozen.get('compiled'))['compiled_sha256']
    phases['pinned_original_identity_and_controller_reconstruction']=time.monotonic()-at;start=time.monotonic()
    old_jobs,old_diagnostic=witness.opportunities(original,old_frames,old_plan)
    old_chosen,_=bridge_compatible(old_jobs)
    preferred=[deserialize(job) for job in parent['chosen']] if parent else old_chosen
    audited,rejected=bridge_compatible(preferred)
    assert not rejected and len(audited)==len(preferred)
    # Parent choices are offered first as an exact feasible lower bound.
    # Their full literal identity is kept if no strict count gain is found.
    jobs,diagnostic=options.opportunities(original,old_frames,old_plan,limit,policy,seed)
    definitions=set();offered=[]
    for job in [*preferred,*jobs]:
        key=json.dumps(serialized(job),sort_keys=True,separators=(',',':'))
        if key not in definitions:definitions.add(key);offered.append(job)
    phases['multiple_provider_and_chain_opportunities']=time.monotonic()-start;start=time.monotonic()
    chosen,_=options.select(offered,time_limit);selection=dict(options.LAST_SELECTION)
    if len(chosen)<=len(preferred):chosen=preferred
    assert len(chosen)>=len(preferred)
    phases['exact_feasible_no_symmetry_MILP']=time.monotonic()-start;start=time.monotonic()
    identical=bool(parent and len(chosen)==len(preferred))
    if identical:
        assert [serialized(job) for job in chosen]==parent['chosen']
        row=dict(parent,physical_witness_reused=True,strict_selection_gain=0)
        assert row['compiled_roles']==old_code['roles']-len(preferred)
        row['checked']=parent['final']['checked']
        phases['changed_graph_verification']=0.0
    else:
        view=witness.DelayedCloneView(original,old_frames,chosen)
        frames=witness.descendant_frames(original,old_frames,view,chosen)
        plan=recovered_plan(original,old_plan,view,frames,chosen)
        code=frame_reuse.compile_reuse(view,frames,plan)
        logical=view.verify();checked=frame_reuse.check(view,frames,code)
        targets=target_check(view,frames,True)
        assert old_code['roles']-code['roles']==len(chosen)
        row=dict(h=h,base=base,positions=positions,
            baseline=dict(roles=old_code['roles'],compiled_sha256=compiled_hash(old_code),
                          circuit_sha256=original_identity,links=len(old_plan[2])),
            chosen=[serialized(job) for job in chosen],
            final=dict(logical=logical,roles=code['roles'],links=len(plan[2]),checked=checked,
                       targets=targets,chains=plan[4]),
            compiled_roles=code['roles'],checked=checked,
            role_saving=len(chosen),strict_selection_gain=len(chosen)-len(preferred),
            physical_witness_reused=False,
            frame_scope='Original positive support envelopes; each selected clone inherits its actual complete-chain first consumer frame')
        if dirty:row['complete_small_controls']=witness.small_controls(view,frames,code)
        if h>=40:
            from finite_residual_rank_histogram import histogram
            from downstream_parameter_optimum import as_strings,saving_enclosure
            ranks=histogram(h,view,frames,code);v=len(view.inputs)
            G=3*v*v*(4*(view.additions+code['roles']-v)+20*v)
            E=64*(ranks['W']+ranks['m']+1)**3;depth=2*G*ranks['W']**2+4*ranks['s']+4*ranks['W']+4
            assert depth<E
            row.update(exact_counts=as_strings(ranks),residual_rank_histogram=as_strings(ranks),
                literal_scalar_guard=as_strings(dict(G=G,E=E,depth=depth,slack=E-depth)),
                uniform_shrink_saving=as_strings(saving_enclosure(Fraction(ranks['D'],ranks['W']*ranks['m']),ranks['m'])))
        phases['changed_graph_verification']=time.monotonic()-start
    row.update(bit_option_configuration=dict(limit=limit,policy=policy,seed=seed,time_limit_seconds=time_limit),
        option_diagnostic=dict(diagnostic,rational_positive_envelopes=True),
        old_one_option_diagnostic=old_diagnostic,old_one_option_greedy_clones=len(old_chosen),
        preferred_feasible_clones=len(preferred),selection=selection,phase_seconds=phases,
        option_selector_source_sha256=sha256(Path(options.__file__).read_bytes()).hexdigest(),
        evaluator_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-at,process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        original_coefficient_policy='Pinned original constructor/compile identities, no old coefficient replay; every strict new clone graph is fully checked once',
        scientific_scope='Several rational positive-envelope first-consumer/provider options; exact capacity/formal-child feasibility; all strict changed maps/frames/targets/ranks/guard; numerical optimality excluded')
    frame_reuse.included.cache_clear();witness.GroupUnion.support_in.cache_clear()
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True)
    parser.add_argument('--h',type=int,nargs='+',default=[8,12])
    parser.add_argument('--limit',type=int,default=4)
    parser.add_argument('--policy',choices=['wide','narrow','seeded'],default='wide')
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--time-limit',type=float,default=6)
    parser.add_argument('--dirty-ground',type=int,default=12)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists();witness.install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',rows=[],source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_complex_clone_nosym.py','finite_clone_descendant_frame.py','finite_clone_recovered_witness.py','fast_frame_envelope.py')},
        started_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        positions=[0]*(h//2-1)+[h//2-2]*(h//2+1)
        row=case(h,2,positions,args.limit,args.policy,args.seed,args.time_limit,dirty=h==args.dirty_ground)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],clones=len(row['chosen']),
            gain=row['strict_selection_gain'],offered=row['selection']['offered_options'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact multiple-option rational clone witness PASS',
        elapsed_seconds=time.monotonic()-at,completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
