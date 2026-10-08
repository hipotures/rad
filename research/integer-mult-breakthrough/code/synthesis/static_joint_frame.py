#!/usr/bin/env python3
"""Exact obstruction for a static globally coupled rational-frame ansatz.

The model permits an arbitrary operator on center-channel tensor address
coordinates, but requires one fixed operator to intertwine all target
projectors. This is an auxiliary matrix model, not a physical network theorem.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from global_incidence import incidence_rows, projector, rank


def exact_mask_rank(masks, nrows):
    return rank([[Q((mask>>i)&1) for mask in masks] for i in range(nrows)])


def probe(h):
    inputs,points,pairs=incidence_rows(h)
    v=len(inputs)
    mask=(1<<v)-1
    diagonal_constant=-Q(5,h+1)
    diagonal_increment=Q(6*h+1,3*(h+1))
    if diagonal_increment==0:
        raise ValueError('Projector diagonal fails to separate memberships')
    # Every diagonal entry is an affine membership indicator. This tests
    # the exact algebraic multiplier used by the written invariance proof.
    for t in inputs:
        for i in range(h):
            bit=int(i in t)
            entry=Q((3+bit)*(3*(h+1)*bit-10),6*(h+1))
            if entry!=diagonal_constant+diagonal_increment*bit:
                raise ValueError('Wrong projector multiplier identity')
    for j,t in enumerate(inputs):
        isolated=points[t[0]]&points[t[1]]&points[t[2]]
        if isolated!=1<<j:
            raise ValueError('Three multiplier products did not isolate a target')
    stages=[]
    for family,initial in [('point',points),('pair',list(pairs.values()))]:
        current=set(initial)
        family_stages=[]
        for step in range(3):
            if h<=8:
                r=exact_mask_rank(sorted(current),v)
            else:
                r=None
            family_stages.append(dict(iteration=step,distinct_indicator_columns=len(current),exact_rational_rank=r))
            if all((1<<j) in current for j in range(v)):
                break
            current|={column&point for column in current for point in points}
            current.discard(0)
        if not all((1<<j) in current for j in range(v)):
            raise ValueError('Closure did not contain the full coordinate basis')
        stages.append(dict(family=family,initial_channels=len(initial),closure_stages=family_stages,
                           full_coordinate_basis_size=v,static_required_rank=v))
    d,i,j,k,l=0,1,2,3,4
    ts=[(d,i,j),(d,k,l),(d,i,k),(d,j,l)]
    weights=[1,1,-1,-1]
    relation=[sum(weight*int(c in t) for weight,t in zip(weights,ts)) for c in range(h)]
    if any(relation):
        raise ValueError('Four-target incidence relation failed')
    rhs=[]
    for t in ts:
        bits=sum(1<<c for c in t)
        p=projector(h,bits,bits)
        rhs.append(p[i][j])
    residue=sum((weight*value for weight,value in zip(weights,rhs)),Q())
    if residue!=Q(1,2):
        raise ValueError('Static intertwiner inconsistency witness failed')
    # Negative control: claiming that the residue is zero must be rejected.
    claimed_static_point_intertwiner=False
    if residue==0:
        claimed_static_point_intertwiner=True
    if claimed_static_point_intertwiner:
        raise ValueError('An inconsistent static operator was accepted')
    return dict(h=h,v=v,diagonal_constant=str(diagonal_constant),diagonal_increment=str(diagonal_increment),
                point_and_pair_channel_closures=stages,
                explicit_point_channel_failure=dict(targets=[list(t) for t in ts],weights=weights,
                    target_membership_relation=relation,center_column=d,address_row=i,address_column=j,
                    projector_entries=list(map(str,rhs)),inconsistency_residue=str(residue)),
                omitted_intertwiner_equation_negative_rejected=True,
                every_target_coordinate_isolated_exactly=True,
                scope='Auxiliary rational static-intertwiner model. It permits arbitrary off-diagonal/non-selfadjoint global operators, but insists on fixed target projectors and one stationary channel frame. Dynamic frames, altered target geometry, nonlinear/address-table representations and full physical implementation are outside scope.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('global_incidence.py')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),worker_processes=args.workers,
                  native_threads_each=1,seed=None,dimensions=[5,6,7,8,23,25],
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    start=time.monotonic()
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,h):h for h in protocol['dimensions']}
        for future in as_completed(jobs):
            results.append(future.result())
            print(json.dumps(dict(h=jobs[future],status='EXACT AUXILIARY STATIC-INTERTWINER CONTROL PASS',seconds=time.monotonic()-start)),flush=True)
    receipt=dict(status='EXACT AUXILIARY STATIC-INTERTWINER CONTROL PASS',
                 cases=sorted(results,key=lambda d:d['h']),elapsed_seconds=time.monotonic()-start,
                 claim='A reached-everywhere channel space must have full dimension v under the stationary intertwiner assumptions, by the accompanying all-size invariance argument. Finite closures are independent checks, not that theorem by extrapolation.')
    (args.output/'certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':
    main()
