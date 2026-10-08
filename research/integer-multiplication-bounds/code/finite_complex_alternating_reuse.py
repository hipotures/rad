#!/usr/bin/env python3
"""Exact complex reuse allowing reviewed alternating nondegenerate residuals.

The original nonalternating checker stays frozen. A fresh generic-Gram
checker constructs every actual alternating projector, symplectic basis,
quadratic phase, Arf sign and reverse complement. All changed scalar and
dirty/shared endpoints remain mandatory. Alternating edges use r ordinary
f-axis children and the paid reviewed compact adapters, with 4s extra charge.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time
from unittest.mock import patch

import frame_reuse
import finite_complex_delayed_clones as witness
import finite_complex_clone_options as options
from finite_clone_recovered_witness import compiled_hash,recovered_plan
from review_complex_frames import complement,dot,gram,rank,residual
import review_complex_controller as generic


def xor_selected(basis, coefficient):
    value=0
    for i,vector in enumerate(basis):
        if coefficient>>i&1:value^=vector
    return value


def symplectic(basis):
    pending=list(basis);answer=[]
    while pending:
        a=pending.pop(0);index=next(i for i,b in enumerate(pending) if dot(a,b));b=pending.pop(index)
        pending=[x^(a if dot(x,b) else 0)^(b if dot(x,a) else 0) for x in pending]
        answer.extend((a,b))
    r=len(answer)
    assert r==rank(answer)==rank(gram(answer)) and r%2==0
    assert all(dot(a,b)==int(j==(i^1)) for i,a in enumerate(answer) for j,b in enumerate(answer))
    assert rank(list(basis)+answer)==r
    return tuple(answer)


def multiply(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def unit_phase(value, exponent):
    a,b=value;return ((a,b),(-b,a),(-a,-b),(b,-a))[exponent%4]
def swap_pairs(value,r):return sum(((value>>i)&1)<<(i^1) for i in range(r))


def alternating_record(old,new):
    assert generic.contained(old,new)
    E=tuple(residual(list(generic.geometry(old)[0]),list(generic.geometry(new)[0])))
    r=new.dimension-old.dimension;assert len(E)==rank(E)==rank(gram(E))==r and r>0 and r%2==0
    assert all(not dot(x,x) for x in E)
    B=symplectic(E);linear=tuple((x.bit_count()//2)%2 for x in B)
    arf=sum(linear[i]*linear[i+1] for i in range(0,r,2))%2;columns=[]
    for i in range(new.h):
        coefficient=sum(dot(1<<i,x)<<j for j,x in enumerate(B))
        image=xor_selected(B,swap_pairs(coefficient,r));columns.append(image)
        assert image==new.project(1<<i)^old.project(1<<i)
        assert new.project(image)==image and old.project(image)==0
    assert all(dot(1<<i,columns[j])==dot(1<<j,columns[i]) for i in range(new.h) for j in range(new.h))
    assert all(not dot(1<<i,columns[i]) for i in range(new.h))
    reverse=tuple(residual(complement(list(generic.geometry(new)[0]),new.h),
        complement(list(generic.geometry(old)[0]),new.h)))
    assert len(reverse)==rank(gram(reverse))==r and rank(list(reverse)+list(E))==r
    # Check Q on basis columns and every paired polarization coefficient.
    def quadratic(alpha):return (xor_selected(B,alpha).bit_count()//2)%2
    assert all(quadratic((1<<i)^(1<<j))==((linear[i]+linear[j]+dot(B[i],B[j]))%2)
        for i in range(r) for j in range(i+1,r))
    pair_gauss=1
    for i in range(0,r,2):
        gauss=sum((-1)**(linear[i]*a+linear[i+1]*b+a*b) for a in (0,1) for b in (0,1))
        assert gauss==2*((-1)**(linear[i]*linear[i+1]));pair_gauss*=gauss
    assert pair_gauss==((-1)**arf)*(1<<(r//2))
    entries=0;digest=sha256()
    # This family has only rank2/rank4 strict alternating intervals. The
    # exact general polynomial checks above remain independent of that fact.
    if r<=8:
        values=[quadratic(a) for a in range(1<<r)]
        assert sum((-1)**x for x in values)==pair_gauss
        for a in range(1<<r):
            for b in range(1<<r):
                jb=swap_pairs(b,r);distance=(a^jb).bit_count();coefficient=(1,0)
                for _ in range(r-distance):coefficient=multiply(coefficient,(1,1))
                for _ in range(distance):coefficient=multiply(coefficient,(1,-1))
                actual=unit_phase(coefficient,a.bit_count()+jb.bit_count()-r//2+2*(arf+values[a]+values[b]))
                assert actual==(((-1)**(arf+values[a^b]))*(1<<(r//2)),0)
                digest.update(f'{a},{b}:{actual};'.encode());entries+=1
    return dict(old_tag=old.tag,new_tag=new.tag,residual_rank=r,symplectic_basis=B,
        residual_projector_columns=columns,linear_quadratic_coefficients=linear,arf_sign=arf,
        exact_gauss_sum=pair_gauss,exact_ordinary_child_phase_entries=entries,
        operator_entries_sha256=digest.hexdigest(),reverse_complement_same_residual=True,
        ordinary_children_per_f_axis=r,extra_elementary_coefficient_charges_at_most=8)


def independent_physical(circuit,frames,code):
    actual={node:generic.GramFrame(circuit.h,frame.tag) for node,frame in frames.items()};records={}
    original_unit=generic.unit
    for frame in set(frames.values()):
        other=generic.GramFrame(circuit.h,frame.tag);generic.geometry(other)
        assert other.dimension==frame.dimension and other.characteristic==frame.characteristic
        for i in range(circuit.h):assert other.project(1<<i)==frame.project(1<<i)
    @lru_cache(maxsize=None)
    def checked_interval(old,new):
        if old is None or old.dimension==new.dimension or old.characteristic!=new.characteristic:
            return original_unit(old,new)
        record=alternating_record(old,new);records[old,new]=record;return 0
    with patch.object(generic,'admissible',generic.contained),patch.object(generic,'unit',checked_interval):
        result=generic.physical(circuit,actual,{node:circuit.support[node] for node in circuit.active},code)
    result.pop('all_nonzero_forward_reverse_residuals_have_norm_one_witness')
    result.update(every_actual_nondegenerate_forward_reverse_residual_has_checked_phase_implementation=True,
        alternating_residual_classes=len(records),alternating_residual_certificates=list(records.values()))
    for (_,target),node in circuit.outputs.items():assert actual[node].project(witness.masks(target))==0
    return result


def phase_timeline(circuit,frames,code):
    old=[None]*code['roles'];transitions=Counter();alternating=Counter()
    for node,inputs,outputs in code['gates']:
        new=frames[node]
        for role in set(inputs+outputs):
            previous=old[role];delta=new.dimension-(previous.dimension if previous else 0)
            assert previous is None or witness.binary.contained(previous,new)
            assert delta>=0
            if previous and delta and previous.characteristic==new.characteristic:alternating[delta]+=1
            transitions[delta]+=1;old[role]=new
    for target,role in code['outputs'].items():assert old[role]==frames[circuit.outputs[target]]
    for frame in set(old):
        assert frame is not None;generic.complement_unit(generic.GramFrame(frame.h,frame.tag))
    return dict(physical_forward_transition_histogram=dict(sorted(transitions.items())),
        physical_forward_transitions=sum(transitions.values()),alternating_forward_rank_histogram=dict(sorted(alternating.items())),
        actual_alternating_forward_transitions=sum(alternating.values()),
        reverse_residuals='Same exact projected subspaces under complementary reversal, checked independently',
        fresh_entries_and_terminal_complements_nonalternating=True)


def case(h,baseline,clone_limit=0,policy='wide',seed=0,dirty=False,exchange=False):
    at=time.monotonic();phases={};original=witness.TripleSideCircuit(h)
    assert witness.logical_identity(original)==baseline['logical']['circuit_sha256']
    old_frames,_=witness.binary.labels(original);phases['construct_original_labels']=time.monotonic()-at;start=time.monotonic()
    with patch.object(frame_reuse,'included',witness.binary.contained):
        old_plan=frame_reuse.optimize_chains(original,old_frames,'rank');old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
        phases['all_nondegenerate_controller_flow']=time.monotonic()-start;start=time.monotonic()
        chosen=[];diagnostic={};selection={}
        if clone_limit:
            jobs,diagnostic=options.opportunities(original,old_frames,old_plan,clone_limit,policy,seed)
            chosen,_=options.select(jobs,6.0);selection=options.LAST_SELECTION
            view=witness.ComplexCloneView(original,old_frames,chosen)
            frames={view.original_mapping[node]:old_frames[node] for node in original.active}
            for job in chosen:frames[view.clones[job['node']]]=old_frames[job['clone_frame_owner']]
            plan=recovered_plan(original,old_plan,view,frames,chosen)
        else:view=original;frames=old_frames;plan=old_plan
        code=frame_reuse.compile_reuse(view,frames,plan);checked=frame_reuse.check(view,frames,code)
    phases['clone_compile_and_coefficient_check']=time.monotonic()-start;start=time.monotonic()
    logical=view.verify();physical=witness.binary.physical_replay(view,code);phase=phase_timeline(view,frames,code)
    independent=independent_physical(view,frames,code);phases['logical_physical_and_exact_residual_phases']=time.monotonic()-start
    from review_complex_frames import complete_scalar_matrix
    dirty_result=complete_scalar_matrix(view,code) if dirty else None
    pi,matching=witness.stage_matching(view);stages=witness.global_exchange(view,code,pi,[5]) if exchange else []
    v=comb(h,3);m=h**3;N=v**3;R=code['roles'];W=2*N+2*v*v*(R+h+1)
    L=3*v*v*(h+1)*h;D=2*N-2*L;s=W*m-D
    G=3*v*v*(4*(view.additions+v)+4*v+4);E=64*(W+m+1)**3;depth=2*G*W*W+8*s+4*W+4;assert depth<E
    counts=dict(h=h,v=v,m=m,N=N,R=R,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    row=dict(h=h,compiled_roles=R,accepted_nonalternating_roles=baseline['compiled_roles'],
        saving_over_accepted_nonalternating=baseline['compiled_roles']-R,all_nondegenerate_before_clones_roles=old_code['roles'],
        added_clones=len(chosen),clone_configuration=dict(limit=clone_limit,policy=policy,seed=seed),
        chosen=[witness.serialized(job) for job in chosen],opportunity_diagnostic=diagnostic,selection=selection,
        logical=logical,checked=checked,physical=physical,phase=phase,independent_actual_frames=independent,
        complete_dirty_scalar_matrix=dirty_result,stage_matching=matching,complete_shared_three_stage=stages,
        shared_complex_counts=counts,guard=dict(actual_grouped_scalar_gates=G,additive_E=E,
            exact_operation_depth_bound=depth,slack=E-depth,alternating_extra_charge_at_most=4*s,
            formula='2G W^2+8s+4W+4; actual G, no old six-W shortcut'),
        saving_enclosure=witness.saving_enclosure(counts['eta'],m) if D>0 else None,
        phase_seconds=phases,elapsed_seconds=time.monotonic()-at,
        scientific_scope='All actual nested nondegenerate residuals; reviewed alternating phases use r ordinary f-axis children and paid adapters; complete changed maps/frame/phase/targets/G/E; independent whole transfer pending')
    witness.binary.contained.cache_clear();witness.binary.admissible.cache_clear();witness.binary.basis.cache_clear()
    return witness.as_strings(row)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,12]);ap.add_argument('--clone-limit',type=int,default=0)
    ap.add_argument('--policy',choices=['wide','narrow','seeded'],default='wide');ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--dirty-ground',type=int,default=8);ap.add_argument('--exchange-h8',action='store_true')
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    baseline=json.loads(args.baseline.read_text());assert baseline['source_sha256']==sha256(Path(witness.binary.__file__).read_bytes()).hexdigest()
    saved={row['h']:row for row in baseline['rows']};at=time.monotonic()
    value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=[],
        baseline_input_sha256=sha256(args.baseline.read_bytes()).hexdigest(),
        reviewed_alternating_interface_sha256=sha256(Path(__file__).parent.parent.joinpath('reports/review-alternating-quadratic-phase.md').read_bytes()).hexdigest(),
        started_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        row=case(h,saved[h],args.clone_limit,args.policy,args.seed,h==args.dirty_ground,h==8 and args.exchange_h8)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],saving=row['saving_over_accepted_nonalternating'],
            alternating=row['phase']['actual_alternating_forward_transitions'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal all-nondegenerate alternating-phase complex finite witness PASS',
        elapsed_seconds=time.monotonic()-at,completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
