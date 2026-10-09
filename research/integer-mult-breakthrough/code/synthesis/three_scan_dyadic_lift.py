#!/usr/bin/env python3
"""Literal exact dyadic lift of a finite three-prefix Z2 discovery.

Three scans are sufficient in this local one-bank model. The two-scan
fixed-label lower bound is elsewhere. This supplies no faster all-size scan
factorization, recursive supplier, tape allocation or multiplier exponent.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random

import ordered_scan_products as S


def word():
    result=[]
    for diagonal in ((1,1,Q(1,2),Q(1,2)),(1,-1,2,-2),(1,-1,-1,1),(1,1,-1,-1)):
        for i,coefficient in enumerate(diagonal):
            if coefficient!=1:
                result.append(('scale',i,Q(coefficient)))
        if diagonal!=(1,1,-1,-1):
            result.extend(('add',i,i-1,Q(1)) for i in range(1,4))
    return tuple(result)


def apply(gates,values,invert=False):
    values=list(values)
    for gate in reversed(gates) if invert else gates:
        if gate[0]=='scale':
            unused,target,coefficient=gate
            coefficient=1/coefficient if invert else coefficient
            values[target]=tuple(coefficient*x for x in values[target])
        else:
            unused,target,source,coefficient=gate
            coefficient=-coefficient if invert else coefficient
            values[target]=tuple(a+coefficient*b for a,b in zip(values[target],values[source]))
    return tuple(values)


def matrix(gates,invert=False):
    columns=[]
    for source in range(4):
        column=apply(gates,tuple((Q(i==source),) for i in range(4)),invert)
        columns.append(tuple(x[0] for x in column))
    return tuple(zip(*columns))


def prefix_guard(gates,invert=False):
    rows=tuple(tuple(Q(i==j) for j in range(4)) for i in range(4))
    maximum_l1=Q(1)
    maximum_grid=0
    for gate in reversed(gates) if invert else gates:
        rows=apply((gate,),rows,invert)
        maximum_l1=max(maximum_l1,max(sum(abs(x) for x in row) for row in rows))
        for row in rows:
            for x in row:
                if x.denominator&(x.denominator-1):
                    raise AssertionError('The common Gaussian dyadic grid was lost')
                maximum_grid=max(maximum_grid,x.denominator.bit_length()-1)
    return dict(complete_linear_prefix_maximum_l1=[maximum_l1.numerator,maximum_l1.denominator],
                maximum_fractional_bits=maximum_grid,
                arithmetic_temporary_or_native_record_buffers_not_included=True)


def probe():
    gates=word()
    target=S.zeta(2)
    forward=matrix(gates)
    inverse=matrix(gates,True)
    if forward!=target or inverse!=S.zeta(2,True):
        raise AssertionError('The complete literal Z2 or inverse operator failed')
    rng=random.Random(20261009201)
    fields=0
    for grid in (0,1,4,9):
        for unused in range(12):
            initial=tuple((Q(rng.randrange(-29,30),1<<grid),Q(rng.randrange(-31,32),1<<grid)) for unused in range(4))
            wanted=tuple(tuple(sum(Q(target[i][j])*initial[j][part] for j in range(4)) for part in (0,1)) for i in range(4))
            actual=apply(gates,initial)
            if actual!=wanted or apply(gates,actual,True)!=initial:
                raise AssertionError('A complete Gaussian field or literal inverse failed')
            fields+=1
    wrong_final=tuple(gate for gate in gates[:-2])
    if matrix(wrong_final)==target:
        raise AssertionError('Missing final output signs passed')
    wrong_middle=list(gates)
    for i,gate in enumerate(wrong_middle):
        if gate[0]=='scale' and gate[1]==2 and gate[2]==2:
            wrong_middle[i]=('scale',2,Q(-1))
        if gate[0]=='scale' and gate[1]==3 and gate[2]==-2:
            wrong_middle[i]=('scale',3,Q(1))
    if matrix(tuple(wrong_middle))==target:
        raise AssertionError('The failed finite-field sign lift passed exact characteristic-zero replay')
    adds=sum(gate[0]=='add' for gate in gates)
    scales=sum(gate[0]=='scale' for gate in gates)
    if (adds,scales)!=(9,9):
        raise AssertionError('The complete elementary gate ledger changed')
    return dict(status='PASS EXACT THREE-PREFIX DYADIC Z2 LIFT',
                word=[list(gate[:-1])+[[gate[-1].numerator,gate[-1].denominator]] for gate in gates],
                complete_basis_columns=4,complete_inverse_columns=4,full_gaussian_fields=fields,
                gaussian_grid_bits=[0,1,4,9],seed=20261009201,
                whole_prefix_calls=3,elementary_adds=adds,explicit_scales=scales,
                nonunit_power_two_scales=sum(gate[0]=='scale' and abs(gate[-1])!=1 for gate in gates),
                forward_guard=prefix_guard(gates),inverse_guard=prefix_guard(gates,True),
                negative_controls=['omitted_final_output_signs','incorrect_finite_sign_lift'],
                native_tape_or_all_size_supplier_or_exponent_claim=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('A fresh optional output is required')
    sources=(Path(__file__).resolve(),Path(S.__file__).resolve(),Path(S.R.__file__).resolve())
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    receipt=probe()
    if hashes!={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise AssertionError('The source closure changed')
    receipt.update(source_closure=hashes,verified_utc=datetime.now(timezone.utc).isoformat(),stdlib_only=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(status=receipt['status'],whole_prefix_calls=3,elementary_adds=9,explicit_scales=9,
                         forward_guard=receipt['forward_guard'],inverse_guard=receipt['inverse_guard']),sort_keys=True))


if __name__=='__main__':
    main()
