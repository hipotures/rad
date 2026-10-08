#!/usr/bin/env python3
"""Exact nonalternating binary-frame controller reuse for the D/E circuit.

For U subset V nondegenerate over F2, the residual is nonalternating iff
P_V*1 differs from P_U*1. Coordinate, pair, triple-line and triple-kernel
projectors have closed forms. New retained chains are admitted only when
their residual is zero or nonalternating; the established even-ground
phase transfer remains the intended interface. The root compiler is imported
unchanged, under a process-local exact admissibility binding.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime,timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import random
import time
from unittest.mock import patch

import frame_reuse
from downstream_complex_circuit import TripleSideCircuit
from downstream_complex_certificate import terminal_checks,stage_matching,global_exchange
from downstream_parameter_optimum import saving_enclosure,as_strings


def bits(mask):
    while mask:
        bit=mask&-mask;yield bit;mask^=bit


@dataclass(frozen=True)
class BinaryFrame:
    h:int
    tag:tuple

    @property
    def dimension(self):
        kind=self.tag[0]
        return (1 if kind=='line' else self.h-1 if kind=='kernel'
                else self.tag[-1].bit_count())

    @property
    def support(self):
        kind=self.tag[0]
        return ((1<<self.h)-1 if kind=='kernel' else self.tag[1]|self.tag[2]
                if kind=='pair' else self.tag[1])

    def project(self,x):
        kind=self.tag[0]
        if kind=='coordinate':return x&self.tag[1]
        if kind=='line':return self.tag[1] if (x&self.tag[1]).bit_count()%2 else 0
        if kind=='kernel':return x^(self.tag[1] if (x&self.tag[1]).bit_count()%2 else 0)
        assert kind=='pair'
        pair,vertices=self.tag[1:]
        common_parity=(x&pair).bit_count()%2
        outside=(x&vertices)^(vertices if common_parity else 0)
        pair_coefficient=outside.bit_count()%2
        return outside^(pair if pair_coefficient else 0)

    @property
    def characteristic(self):
        return self.project((1<<self.h)-1)

    @property
    def basis(self):
        return basis(self)


@lru_cache(maxsize=300000)
def basis(frame):
    kind=frame.tag[0]
    if kind=='line':return (frame.tag[1],)
    if kind=='coordinate':return tuple(bits(frame.tag[1]))
    if kind=='pair':return tuple(frame.tag[1]|bit for bit in bits(frame.tag[2]))
    assert kind=='kernel'
    target=frame.tag[1];a=target&-target
    return (*bits(((1<<frame.h)-1)^target),*(a|bit for bit in bits(target^a)))


@lru_cache(maxsize=500000)
def contained(a,b):
    assert a.h==b.h
    if a==b:return True
    kind=b.tag[0]
    if kind=='coordinate':return not a.support&~b.tag[1]
    if kind=='kernel':return not a.project(b.tag[1])
    if kind=='line':return a.dimension==1 and a.support==b.tag[1]
    assert kind=='pair'
    pair,vertices=b.tag[1:];first=pair&-pair
    return not (a.support&~(pair|vertices) or a.project(pair) or a.project(vertices|first))


def witness(a,b):
    assert contained(a,b) and a.dimension<b.dimension
    characteristic=a.characteristic^b.characteristic
    assert characteristic,'Residual is alternating'
    coordinate=characteristic&-characteristic
    unit=a.project(coordinate)^b.project(coordinate)
    assert unit.bit_count()%2==1 and not a.project(unit) and b.project(unit)==unit
    return unit


@lru_cache(maxsize=500000)
def admissible(a,b):
    if not contained(a,b):return False
    assert a.dimension<=b.dimension
    if a.dimension==b.dimension:return True
    if a.characteristic==b.characteristic:return False
    witness(a,b)
    return True


def labels(circuit):
    intern={};values={}
    for node in sorted(circuit.active):
        tag=circuit.frame(node);values[node]=intern.setdefault(tag,BinaryFrame(circuit.h,tag))
        frame=values[node]
        assert frame.project(frame.characteristic)==frame.characteristic and frame.characteristic
        if circuit.args[node]:
            for child in circuit.args[node]:assert admissible(values[child],frame)
        else:assert frame.tag==('line',circuit.core[node]) and frame.dimension==1
    return values,dict(unique_binary_frames=len(intern),
        family='Exact coordinate, orthonormal pair, triple-line and triple-perp frames',
        every_original_edge_nondegenerate_nested_nonalternating=True)


def independent(circuit,frames,plan,seed=109):
    from review_complex_frames import rank,gram,residual,complement,dot
    unique=sorted(set(frames.values()),key=lambda frame:frame.tag);checks=0;projectors=0
    for frame in unique:
        B=list(frame.basis);assert len(B)==rank(B)==rank(gram(B))==frame.dimension
        for coordinate in bits((1<<circuit.h)-1):
            image=frame.project(coordinate)
            assert rank(B+[image])==len(B)
            assert all(dot(coordinate^image,v)==0 for v in B)
            projectors+=1
    pairs={(frames[child],frames[node]) for node in circuit.active for child in circuit.args[node] or ()}
    _,descriptions,successor,_,_=plan
    for first,second in successor.items():
        node,old,_=descriptions[first];_,new,_=descriptions[second]
        pairs.add((frames[old],frames[new if new is not None else node]))
    rng=random.Random(seed)
    for _ in range(4096):pairs.add((rng.choice(unique),rng.choice(unique)))
    alternating=0
    for a,b in pairs:
        A,B=list(a.basis),list(b.basis)
        actual=rank(A+B)==len(B)
        assert contained(a,b)==actual
        if actual:
            E=residual(A,B);assert len(E)==rank(gram(E))==b.dimension-a.dimension
            reverse=residual(complement(B,circuit.h),complement(A,circuit.h))
            assert rank(E+reverse)==len(E)==len(reverse)
            nonalternating=not E or any(dot(v,v) for v in E)
            assert admissible(a,b)==nonalternating
            assert (not E or a.characteristic!=b.characteristic)==nonalternating
            alternating+=int(bool(E) and not nonalternating)
        else:assert not admissible(a,b)
        checks+=1
    return dict(exact_binary_frame_grams=len(unique),independent_projector_columns=projectors,
        exact_containment_and_residual_decisions=checks,excluded_alternating_pairs=alternating,
        reverse_complements_same_residual=True,seed=seed)


def physical_replay(circuit,code):
    """Exact disjoint scalar replay permits either argument as result pivot."""
    values=[0]*code['roles'];additions=copies=swaps=0
    for node,inputs,outputs in code['gates']:
        if circuit.args[node] is None:
            assert len(inputs)==1 and values[inputs[0]]==0
            values[inputs[0]]=circuit.support[node]
        else:
            assert len(inputs)==2
            a,b=circuit.args[node];actual=(values[inputs[0]],values[inputs[1]])
            expected=(circuit.support[a],circuit.support[b])
            assert actual==expected or actual==expected[::-1]
            swaps+=int(actual==expected[::-1])
            assert not actual[0]&actual[1]
            values[inputs[0]]=actual[0]|actual[1];additions+=1
        assert values[inputs[0]]==circuit.support[node]
        for role in outputs[1:]:
            assert values[role]==0
            values[role]=values[inputs[0]];copies+=1
    for target,role in code['outputs'].items():
        assert values[role]==circuit.support[circuit.outputs[target]]
    return dict(all_physical_coefficients_exact=True,physical_additions=additions,
        physical_copies=copies,designated_outputs=len(code['outputs']),
        exact_swapped_result_pivots=swaps)


def phase_timeline(circuit,frames,code):
    old=[None]*code['roles'];transitions=Counter();unique=set()
    for node,ins,outs in code['gates']:
        new=frames[node]
        for role in set(ins+outs):
            previous=old[role]
            if previous is None:
                assert new.characteristic
                unit=new.project(new.characteristic&-new.characteristic)
                assert unit.bit_count()%2==1 and new.project(unit)==unit
                difference=new.dimension
            else:
                assert admissible(previous,new)
                difference=new.dimension-previous.dimension
                if difference:unit=witness(previous,new)
            transitions[difference]+=1;unique.add((previous,new));old[role]=new
    for target,role in code['outputs'].items():assert old[role]==frames[circuit.outputs[target]]
    for frame in set(old):
        assert frame is not None
        char=((1<<circuit.h)-1)^frame.characteristic
        assert char,'A terminal complement would be alternating'
        coordinate=char&-char;unit=coordinate^frame.project(coordinate)
        assert unit.bit_count()%2==1 and not frame.project(unit)
    return dict(physical_forward_transition_histogram=dict(sorted(transitions.items())),
        physical_forward_transitions=sum(transitions.values()),unique_physical_transitions=len(unique),
        every_nonzero_physical_residual_has_exact_norm_one_witness=True,
        every_fresh_role_entry_and_terminal_complement_nonalternating=True,
        reverse_residuals='Isometric complements of the checked forward residuals')


def case(h,independent_max,dirty_max,exchange):
    start=time.monotonic();circuit=TripleSideCircuit(h);logical=circuit.verify()
    original_frames=circuit.verify_frames();terminal=terminal_checks(circuit)
    frames,metadata=labels(circuit);marks={}
    at=time.monotonic()
    with patch.object(frame_reuse,'included',admissible):
        plan=frame_reuse.optimize_chains(circuit,frames,'rank')
        marks['flow_seconds']=time.monotonic()-at;at=time.monotonic()
        code=frame_reuse.compile_reuse(circuit,frames,plan)
        checked=frame_reuse.check(circuit,frames,code)
    checked['nondegeneracy']='Exact binary nondegenerate frames; every admitted nonzero residual nonalternating'
    marks['compile_and_unchanged_checker_seconds']=time.monotonic()-at
    physical=physical_replay(circuit,code);phase=phase_timeline(circuit,frames,code)
    independent_result=independent(circuit,frames,plan) if h<=independent_max else None
    from review_complex_frames import complete_scalar_matrix
    dirty=complete_scalar_matrix(circuit,code) if h<=dirty_max else None
    pi,matching=stage_matching(circuit)
    stages=global_exchange(circuit,code,pi,[5]) if h==8 and exchange else []
    v=comb(h,3);m=h**3;N=v**3;R=code['roles'];W=2*N+2*v*v*(R+h+1)
    L=3*v*v*(h+1)*h;D=2*N-2*L;s=W*m-D
    # The logical-node gate count remains fixed after physical reuse. Use
    # its actual value, rather than substituting the smaller R into4R+4.
    grouped_gates=3*v*v*(4*(circuit.additions+v)+4*v+4)
    E=64*(W+m+1)**3;depth=2*grouped_gates*W*W+4*s+4*W+4
    assert depth<E
    if D>0:assert 2<=s<m**5
    counts=dict(h=h,v=v,m=m,N=N,R=R,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    row=dict(h=h,status='Finite nonalternating binary controller-reuse witness PASS; independent global phase/guard transfer review required',
        logical=logical,original_frames=original_frames,terminal=terminal,new_frames=metadata,
        compiled_roles=R,baseline_roles=circuit.additions+len(circuit.outputs),roles_saved=len(plan[2]),
        chains=code['chain_summary'],checked=checked,physical=physical,phase=phase,
        independent=independent_result,complete_dirty_scalar_matrix=dirty,stage_matching=matching,
        complete_shared_three_stage=stages,shared_complex_counts=counts,
        guard=dict(actual_grouped_scalar_gates=grouped_gates,old_six_W_condition=grouped_gates<6*W,
            exact_saved_input_operation_depth_bound=depth,additive_E=E,guard_B=s+E,operation_depth_slack=E-depth,
            correction='Actual fixed node-gate count used after reuse; no false4R+4 substitution'),
        saving_enclosure=saving_enclosure(counts['eta'],m) if D>0 else None,
        phase_seconds=marks,elapsed_seconds=time.monotonic()-start)
    admissible.cache_clear();contained.cache_clear();basis.cache_clear()
    return as_strings(row)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--h',type=int,nargs='+',default=[8,10,12])
    ap.add_argument('--independent-max',type=int,default=12)
    ap.add_argument('--dirty-max',type=int,default=8)
    ap.add_argument('--exchange-h8',action='store_true')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    start=time.monotonic();rows=[]
    for h in args.h:
        row=case(h,args.independent_max,args.dirty_max,args.exchange_h8);rows.append(row)
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],saved=row['roles_saved'],seconds=row['elapsed_seconds'])),flush=True)
    value=dict(status='Terminal finite complex reuse witness PASS; final transfer review separate',rows=rows,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('frame_reuse.py','downstream_complex_circuit.py','downstream_complex_certificate.py','review_complex_frames.py','finite_complex_blocks.py')},
        started_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
        scope='Existing even-ground nonalternating phase family; exact scalar/frame/controller/terminal flags; actual grouped-gate guard recomputed')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
