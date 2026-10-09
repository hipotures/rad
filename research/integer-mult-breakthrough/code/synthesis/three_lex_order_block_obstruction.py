#!/usr/bin/env python3
"""Exact block controls for three natural/bit-reversal ordered scans.

The analytical proof excludes f>=3 in characteristic zero with arbitrary
nonzero diagonal gauges, including Gaussian scalars. This program binds
the block identities and unit bridge witnesses on four finite widths.
It does not price native routing or exclude arbitrary address orders.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import time

import verify_ordered_scan_products as V

S=V.S


def identity(n):
    return tuple(tuple(int(i==j) for j in range(n)) for i in range(n))


def add(a,b,sign=1):
    return tuple(tuple(x+sign*y for x,y in zip(ar,br)) for ar,br in zip(a,b))


def left_diagonal(matrix,diagonal):
    return tuple(tuple(diagonal[i]*x for x in row) for i,row in enumerate(matrix))


def right_diagonal(matrix,diagonal):
    return tuple(tuple(x*diagonal[j] for j,x in enumerate(row)) for row in matrix)


def upper_right(matrix,m):
    return tuple(tuple(row[m:]) for row in matrix[:m])


def block(matrix,m,row,column):
    return tuple(tuple(line[column*m:(column+1)*m]) for line in matrix[row*m:(row+1)*m])


def reverse(x,f):
    return sum(((x>>b)&1)<<(f-1-b) for b in range(f))


def complete_product(scans,b,c):
    return S.multiply(S.multiply(right_diagonal(scans[0],b),scans[1]),left_diagonal(scans[2],c))


def probe(f):
    started=time.monotonic()
    n,m=1<<f,1<<(f-1)
    I=identity(m)
    natural={kind:S.ordered_scan(tuple(range(n)),kind) for kind in ('prefix','difference')}
    reflected={kind:S.ordered_scan(tuple(reverse(x,f) for x in range(n)),kind) for kind in ('prefix','difference')}
    R=S.ordered_scan(tuple(reverse(x,f-1) for x in range(m)),'prefix')
    D=S.ordered_scan(tuple(reverse(x,f-1) for x in range(m)),'difference')
    H=add(D,I,-1)
    expected_L=(R,add(R,I,-1),R,R)
    expected_D=(I,H,tuple(tuple(-x for x in row) for row in I),I)
    for kind,expected in [('prefix',expected_L),('difference',expected_D)]:
        if tuple(block(reflected[kind],m,i,j) for i in range(2) for j in range(2))!=expected:
            raise AssertionError('An actual bit-reversal scan has the wrong complete blocks')
    b=tuple((-1 if i%2 else 1)*(1<<(i%3)) for i in range(n))
    c=tuple((-1 if i%3 else 1)*(1<<((i+1)%2)) for i in range(n))
    one_reverse=0
    for where in range(3):
        for kinds in product(('prefix','difference'),repeat=3):
            scans=[reflected[kind] if i==where else natural[kind] for i,kind in enumerate(kinds)]
            cross=upper_right(complete_product(scans,b,c),m)
            if len(S.R.rref(cross,m)[1])!=m-1:
                raise AssertionError('Natural triangular factors killed a single reflected upper block')
            one_reverse+=1
    same_order=0
    for bank in (natural,reflected):
        for kinds in product(('prefix','difference'),repeat=3):
            # For bit-reversal order the relevant midpoint cut is pulled back
            # by that axis permutation, not assumed to be the same coordinate.
            result=complete_product([bank[k] for k in kinds],b,c)
            if bank is reflected:
                pi=tuple(reverse(x,f) for x in range(n))
                result=tuple(tuple(result[pi[i]][pi[j]] for j in range(n)) for i in range(n))
            cross=block(result,m,1,0)
            if len(S.R.rref(cross,m)[1])>3:
                raise AssertionError('A three-factor triangular cross-cut exceeds rank three')
            same_order+=1
    target=S.zeta(f)
    pi=tuple(reverse(x,f) for x in range(n))
    if tuple(tuple(target[pi[i]][pi[j]] for j in range(n)) for i in range(n))!=target:
        raise AssertionError('Bit reversal is not the required axis-permutation target symmetry')
    if len(S.R.rref(block(target,m,1,0),m)[1])!=m:
        raise AssertionError('The complete zeta target cross-cut is not full rank')
    consecutive=[]
    for left_kind,right_kind in product(('prefix','difference'),repeat=2):
        second=tuple((-1 if i%2 else 1)*(1<<(i%2)) for i in range(m))
        first=[0]*m
        order=tuple(reverse(x,f-1) for x in range(m))
        first[order[0]]=4
        sign=-1 if left_kind==right_kind else 1
        for i in range(1,m):
            first[order[i]]=sign*second[order[i-1]]
        Q=S.multiply(right_diagonal(reflected[left_kind],tuple(first)+second),reflected[right_kind])
        if any(x for row in upper_right(Q,m) for x in row):
            raise AssertionError('The constructive consecutive upper-zero condition failed')
        if left_kind==right_kind=='prefix':
            expected00=right_diagonal(R,first)
            expected11=left_diagonal(R,second)
            if block(Q,m,0,0)!=expected00 or block(Q,m,1,1)!=expected11:
                raise AssertionError('Consecutive prefix blocks did not reduce to one smaller scan')
        elif left_kind==right_kind=='difference':
            expected00=left_diagonal(D,first)
            expected11=right_diagonal(D,second)
            if block(Q,m,0,0)!=expected00 or block(Q,m,1,1)!=expected11:
                raise AssertionError('Consecutive difference blocks did not reduce to one smaller scan')
        elif left_kind=='prefix':
            if block(Q,m,1,1)!=left_diagonal(I,second):
                raise AssertionError('Consecutive prefix/difference bottom block is not diagonal')
        else:
            if block(Q,m,0,0)!=left_diagonal(I,first):
                raise AssertionError('Consecutive difference/prefix top block is not diagonal')
        consecutive.append(dict(kinds=[left_kind,right_kind],complete_upper_zero=True,
                                diagonal_or_single_smaller_scan_blocks=True))
    separated=[]
    r,column=m//2,m//2-1
    for left_kind,right_kind,middle_kind in product(('prefix','difference'),repeat=3):
        N=natural[middle_kind]
        A,K=block(N,m,0,0),block(N,m,1,0)
        U=right_diagonal(left_diagonal(A,b[:m]),c[:m])
        W=right_diagonal(left_diagonal(K,b[m:]),c[:m])
        Z=right_diagonal(left_diagonal(A,b[m:]),c[m:])
        UH,HV,HWH=S.multiply(U,H),S.multiply(H,Z),S.multiply(S.multiply(H,W),H)
        result=upper_right(complete_product([reflected[left_kind],N,reflected[right_kind]],b,c),m)
        if left_kind=='prefix':result=S.multiply(D,result)
        if right_kind=='prefix':result=S.multiply(result,D)
        if left_kind==right_kind=='prefix':
            expected=add(add(tuple(tuple(-x for x in row) for row in UH),HV,-1),HWH)
            forced_sign=1
        elif left_kind=='prefix':
            expected=add(add(UH,HV,-1),HWH,-1)
            forced_sign=-1
        elif right_kind=='prefix':
            expected=add(add(tuple(tuple(-x for x in row) for row in UH),HV),HWH,-1)
            forced_sign=-1
        else:
            expected=add(add(UH,HV),HWH)
            forced_sign=1
        if result!=expected or UH[r][column]!=0 or HV[r][column]!=0:
            raise AssertionError('The complete separated scan block identity failed')
        if result[r][column]!=forced_sign*W[0][m-1] or not result[r][column]:
            raise AssertionError('The exact nonzero natural bridge witness disappeared')
        corrupt=add(expected,HWH,-forced_sign)
        if corrupt==result or corrupt[r][column]!=0:
            raise AssertionError('Omitting the required natural bridge passed the exact block control')
        separated.append(dict(kinds=[left_kind,middle_kind,right_kind],witness_address=[r,column],
                              exact_nonzero_value=result[r][column],missing_bridge_rejected=True))
    return dict(status='PASS THREE NATURAL/REVERSE BLOCK IDENTITIES',f=f,
                one_reverse_cases=one_reverse,same_order_cases=same_order,
                consecutive=consecutive,separated=separated,
                exact_integer_matrix_controls=True,seconds=time.monotonic()-started,
                scope='Block/control binding of written characteristic-zero proof, no native or general-order claim')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.workers<1:raise ValueError('Positive workers required')
    sources=(Path(__file__).resolve(),Path(V.__file__).resolve(),Path(S.__file__).resolve(),Path(V.T.__file__).resolve(),Path(S.R.__file__).resolve())
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=datetime.now(timezone.utc).isoformat(),source_closure=hashes,
        workers=args.workers,stdlib_only=True,f_tasks=[3,4,5,6],
        scope='Exact finite block identities plus inherited complete two-scan control; written all-size proof is not formal verification'),indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(probe,(3,4,5,6)))
    lower=V.probe()
    if hashes!={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}:raise AssertionError('The source closure changed')
    receipt=dict(status='PASS SELECTED THREE-SCAN CHARACTERISTIC-ZERO BLOCK CONTROLS',rows=rows,
                 inherited_two_scan_complete_cases=lower['f2_complete_cases'],
                 arbitrary_nonzero_gaussian_diagonals_covered_by_written_proof=True,
                 arbitrary_nonlex_order_or_native_supplier_not_excluded=True)
    (args.output/'certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(status=receipt['status'],f_tasks=[r['f'] for r in rows],
                         exact_block_cases=sum(r['one_reverse_cases']+r['same_order_cases']+len(r['consecutive'])+len(r['separated']) for r in rows)),sort_keys=True))


if __name__=='__main__':
    main()
