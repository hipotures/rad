#!/usr/bin/env python3
"""Fresh terminal, full-bank sharing and exchange checks for the complex DAG.

The earlier circuit source and completed results are immutable inputs.
This checker adds explicit terminal witnesses, Cartesian stage matching,
new grouped-gate guard bounds and an actual three-stage dirty exchange.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path
import time

from downstream_complex_circuit import TripleSideCircuit, masks, mixer
from downstream_gaussian import check_sources, require
from downstream_parameter_optimum import as_strings, saving_enclosure


def terminal_checks(circuit):
    full=(1<<circuit.h)-1
    kinds=Counter();dimensions=Counter()
    for node in circuit.active:
        frame=circuit.frame(node);kind=frame[0]
        if kind=='coordinate':
            available=full^frame[1];dimension=circuit.h-frame[1].bit_count()
            unit=available&-available
            require(unit and not unit&frame[1], 'Coordinate terminal complement failed')
        elif kind=='pair':
            pair,vertices=frame[1:]
            require(vertices.bit_count()<=circuit.h-3, 'A used helper includes a forbidden full total')
            available=full^(pair|vertices);unit=available&-available
            dimension=circuit.h-vertices.bit_count()
            require(unit and not unit&(pair|vertices), 'Pair terminal complement failed')
        elif kind=='line':
            available=full^frame[1];unit=available&-available;dimension=circuit.h-1
            require(unit and not unit&frame[1], 'Line terminal complement failed')
        else:
            require(kind=='kernel','Unknown terminal frame')
            unit=frame[1];dimension=1
        require(unit.bit_count()%2==1 and dimension>0, 'Terminal norm-one/dimension check failed')
        kinds[kind]+=1;dimensions[dimension]+=1
    return dict(nodes=len(circuit.active),frame_kind_counts=dict(kinds),
                complement_dimension_counts=dict(sorted(dimensions.items())),
                every_terminal_complement_nondegenerate_nonalternating=True,
                pair_helper_bound_explicitly_checked=True)


def stage_matching(circuit):
    positions={t:i for i,t in enumerate(circuit.inputs)}
    pi=[];intersections=Counter();units=[]
    full=(1<<circuit.h)-1
    for i,t in enumerate(circuit.inputs):
        other=tuple(sorted(j^1 for j in t));j=positions[other];pi.append(j)
        intersection=len(set(t)&set(other))
        require(intersection in (0,2), 'Partner flip lost binary orthogonality')
        union=masks(t)|masks(other);available=full^union;unit=available&-available
        require(unit and unit.bit_count()==1 and not unit&union, 'Join residual lost its norm-one unit')
        intersections[intersection]+=1;units.append(unit)
    require(len(set(pi))==len(pi) and all(pi[pi[i]]==i for i in range(len(pi))),
            'Partner matching is not a bijective involution')
    # Exact scalar products for a tensor coordinate unit with this middle
    # coordinate are zero both against E and the defining line of H.
    for i,j in enumerate(pi):
        require((units[i]&masks(circuit.inputs[i])).bit_count()%2==0
                and (units[i]&masks(circuit.inputs[j])).bit_count()%2==0,
                'Tensor join unit is not in H intersection E-perp')
    v=len(pi)
    pair_checks=0
    if circuit.h<=12:
        matching={(a,b):(b,pi[a]) for a in range(v) for b in range(v)}
        require(len(set(matching.values()))==v*v, 'Full small invocation matching collided')
        pair_checks=v*v
    return pi,dict(triples=v,distinct_images=len(set(pi)),involution=True,
                   even_intersection_counts=dict(intersections),
                   middle_norm_one_join_witnesses=v,
                   small_cartesian_invocation_pairs_enumerated=pair_checks,
                   all_size_invocation_matching='(A,B) -> (B,pi(A)); Cartesian bijection from the exact pi permutation',
                   dim_E=circuit.h,dim_H=circuit.h**3-circuit.h,
                   join_residual_dimension=circuit.h**3-2*circuit.h,
                   rank_removed_per_identified_role=circuit.h**3)


def invoke(circuit, code, x, y, bank, inverse=False):
    roles=code['roles'];h=circuit.h
    def action(kind,sign):
        if kind=='mix':
            mixer(bank,code,inverse=(sign<0))
        elif kind=='inject':
            for i,t in enumerate(circuit.inputs):
                value=bank[code['outputs']['D',t]]-bank[code['outputs']['E',t]]
                require(value%2==0,'Exchange side coefficient requires a dyadic half')
                y[i]+=sign*(value//2)
        elif kind=='copy':
            for i,t in enumerate(circuit.inputs):bank[code['sources'][t]]+=sign*x[i]
        elif kind=='gather':
            for i,t in enumerate(circuit.inputs):
                for j in t:bank[roles+j]+=sign*x[i]
                bank[roles+h]+=sign*x[i]
        else:
            require(kind=='scatter','Unknown scalar action')
            for i,t in enumerate(circuit.inputs):
                value=sum(bank[roles+j] for j in t)-bank[roles+h]
                require(value%2==0,'Exchange central coefficient requires a dyadic half')
                y[i]+=sign*(value//2)
    schedule=[('mix',1),('inject',-1),('mix',-1),('scatter',-1),
              ('copy',1),('gather',1),('scatter',1),('mix',1),
              ('inject',1),('mix',-1),('gather',-1),('copy',-1)]
    if inverse:schedule=[(kind,-sign) for kind,sign in reversed(schedule)]
    for kind,sign in schedule:action(kind,sign)


def global_exchange(circuit, code, pi, seeds):
    v=len(circuit.inputs);n=v**3;size=code['roles']+circuit.h+1
    pool=tuple(range(-32,34,2));cases=[]
    for seed in seeds:
        def payload(i):return pool[(i*17+seed*13)%len(pool)]
        x=[payload(i) for i in range(n)]
        y=[payload(n+i) for i in range(n)];original_x=x[:];original_y=y[:]
        shared=[[payload(2*n+row*size+j) for j in range(size)] for row in range(v*v)]
        middle=[[payload(2*n+v*v*size+row*size+j) for j in range(size)] for row in range(v*v)]
        invocations=0
        for stage in range(3):
            for a in range(v):
                for b in range(v):
                    if stage==0:indices=[i*v*v+a*v+b for i in range(v)];bank=shared[a*v+b]
                    elif stage==1:indices=[a*v*v+i*v+b for i in range(v)];bank=middle[a*v+b]
                    else:indices=[a*v*v+b*v+i for i in range(v)];bank=shared[pi[b]*v+a]
                    if stage==1:source=[y[i] for i in indices];target=[x[i] for i in indices]
                    else:source=[x[i] for i in indices];target=[y[i] for i in indices]
                    invoke(circuit,code,source,target,bank,inverse=(stage==1))
                    output=x if stage==1 else y
                    for i,value in zip(indices,target):output[i]=value
                    invocations+=1
        require(x==[-z for z in original_y] and y==original_x,'Signed three-stage bank exchange failed')
        for row,bank in enumerate(shared):
            require(all(value==payload(2*n+row*size+j) for j,value in enumerate(bank)),
                    'Shared first/third full bank did not restore arbitrary dirty values')
        for row,bank in enumerate(middle):
            require(all(value==payload(2*n+v*v*size+row*size+j) for j,value in enumerate(bank)),
                    'Middle full bank did not restore arbitrary dirty values')
        cases.append(dict(seed=seed,invocations=invocations,data_coordinates_per_bank=n,
                          dirty_scratch_coordinates=2*v*v*size,
                          all_data_coordinates_and_shared_auxiliary_roles_exact=True,
                          stage2='Actual reversed and inverted chronological schedule'))
    return cases


def case(h,exchange_seeds):
    start=time.monotonic();circuit=TripleSideCircuit(h)
    logical=circuit.verify();frames=circuit.verify_frames();code=circuit.compile()
    terminal=terminal_checks(circuit);pi,matching=stage_matching(circuit)
    v,m,n=comb(h,3),h**3,comb(h,3)**3;r=code['roles']
    loss=3*v*v*(h+1)*h;w=2*n+2*v*v*(r+h+1);deficit=2*n-2*loss;s=w*m-deficit
    unshared_w=2*n+3*v*v*(r+h+1);unshared_s=unshared_w*m-deficit
    require(unshared_w-w==v*v*(r+h+1), 'Shared role difference changed')
    require(unshared_s-s==(unshared_w-w)*m, 'Identified role did not remove exactly m rank')
    gates=3*v*v*(4*r+4)
    require(gates<6*w,'New grouped scalar gate bound failed')
    e=64*(w+m+1)**3;b=s+e
    require(12*w**3+4*s+4*w+4<e,'Retained additive guard constant no longer covers coefficient operations')
    counts=dict(h=h,v=v,m=m,N=n,R=r,W=w,L=loss,D=deficit,s=s,eta=Q(deficit,w*m))
    guard=dict(grouped_scalar_gates=gates,strict_six_W_slack=6*w-gates,
               additive_guard_E=e,guard_B=b,
               strict_operation_depth_slack=e-(12*w**3+4*s+4*w+4),
               stopped_depth_branching_premise=bool(2<=s<m**5))
    if deficit>0:require(2<=s<m**5,'Positive finite phase circuit lacks the stopped guard premise')
    exchange=global_exchange(circuit,code,pi,exchange_seeds) if exchange_seeds else []
    return dict(h=h,status='PASS full finite terminal/sharing/guard certificate; independent analytic transfer review remains separate',
                logical=logical,frames=frames,terminal=terminal,matching=matching,
                shared_complex_counts=counts,unshared_W=unshared_w,unshared_s=unshared_s,
                guard=guard,full_dirty_three_stage_exchange=exchange,
                saving_enclosure=saving_enclosure(counts['eta'],m) if deficit>0 else None,
                elapsed_seconds=time.monotonic()-start)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,50])
    ap.add_argument('--global-exchange-h8',action='store_true')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    start=time.monotonic();source=Path(__file__)
    names=['downstream_complex_certificate.py','downstream_complex_circuit.py',
           'downstream_gaussian.py','downstream_parameter_optimum.py']
    result=dict(campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_deadline='2026-10-08T08:25:21Z',provenance=check_sources(args.upstream),
                source_sha256={name:hashlib.sha256((source.parent/name).read_bytes()).hexdigest() for name in names},cases=[])
    for h in args.h:
        print('Starting terminal/shared complex check h',h,flush=True)
        row=case(h,[5] if h==8 and args.global_exchange_h8 else [])
        result['cases'].append(row);result['elapsed_seconds']=time.monotonic()-start
        result['generated_at']=datetime.now(timezone.utc).isoformat()
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
        print('PASS terminal/shared complex h',h,'roles',row['shared_complex_counts']['R'],flush=True)


if __name__=='__main__':main()
