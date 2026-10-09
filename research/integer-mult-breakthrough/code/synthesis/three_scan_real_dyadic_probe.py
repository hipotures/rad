#!/usr/bin/env python3
"""Small exact GF(3) discriminator for three ordered one-bank scans.

Every invertible real dyadic unit +/-2^k reduces to a nonzero GF(3) value.
An exhaustive negative therefore excludes these units for the chosen orders,
but does not exclude Gaussian phases, odd scalar units, other orders or banks.
Finite positives are separately checked for an exact rational sign lift.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import time

import ordered_scan_products as S


def field_kernel(rows, n):
    rows=[list(int(x)%3 for x in row) for row in rows if any(int(x)%3 for x in row)]
    pivots=[]
    for column in range(n):
        pivot=next((i for i in range(len(pivots),len(rows)) if rows[i][column]),None)
        if pivot is None:
            continue
        r=len(pivots)
        rows[r],rows[pivot]=rows[pivot],rows[r]
        coefficient=rows[r][column]
        rows[r]=[(coefficient*x)%3 for x in rows[r]]
        for i,row in enumerate(rows):
            if i!=r and row[column]:
                coefficient=row[column]
                rows[i]=[(a-coefficient*b)%3 for a,b in zip(row,rows[r])]
        pivots.append(column)
    basis=[]
    for free in range(n):
        if free in pivots:
            continue
        direction=[0]*n
        direction[free]=1
        for i,pivot in enumerate(pivots):
            direction[pivot]=(-rows[i][free])%3
        basis.append(tuple(direction))
    return tuple(basis)


def nonzero_normalized_kernel_vectors(rows,basis,n):
    pivot=next((i for i,row in enumerate(basis) if row[0]),None)
    if pivot is None:
        return
    base=tuple((basis[pivot][0]*x)%3 for x in basis[pivot])
    directions=[tuple((x-direction[0]*y)%3 for x,y in zip(direction,base))
                for i,direction in enumerate(basis) if i!=pivot]
    if 3**len(directions)<=2**(n-1):
        for coefficients in product(range(3),repeat=len(directions)):
            vector=tuple((base[k]+sum(c*d[k] for c,d in zip(coefficients,directions)))%3 for k in range(n))
            if all(vector):
                yield vector
    else:
        for tail in product((1,2),repeat=n-1):
            vector=(1,)+tail
            if all(sum(a*b for a,b in zip(row,vector))%3==0 for row in rows):
                yield vector


def reduced_matrix(tensor,middle):
    return tuple(tuple(sum(c*b for c,b in zip(entry,middle))%3 for entry in row) for row in tensor)


def repair_gauges(matrix,target):
    n=len(matrix)
    if any((matrix[i][j]==0)!=(target[i][j]==0) for i in range(n) for j in range(n)):
        return None
    row_inverse=tuple(matrix[i][0] for i in range(n))
    column_inverse=tuple((matrix[j][j]*row_inverse[j])%3 for j in range(n))
    if any(row_inverse[i]*matrix[i][j]*column_inverse[j]%3!=target[i][j] for i in range(n) for j in range(n)):
        return None
    return row_inverse,column_inverse


def sign_lift(first_tensor,last,b,c,target):
    b=tuple(Q(1 if x==1 else -1) for x in b)
    c=tuple(Q(1 if x==1 else -1) for x in c)
    middle=S.evaluate(first_tensor,b)
    matrix=S.evaluate(S.coefficient_tensor(middle,last),c)
    gauges=S.gauged_zeta(matrix,target)
    if gauges is None:
        return dict(status='NO EXACT RATIONAL SIGN LIFT; FINITE POSITIVE ONLY')
    def unit(x):
        n,d=abs(x.numerator),x.denominator
        return bool(n) and n&(n-1)==0 and d&(d-1)==0
    row,column=gauges
    return dict(status='EXACT COMPLETE RATIONAL SIGN-LIFT FACTORIZATION',
                left_middle=S.R.encoded([b])[0],right_middle=S.R.encoded([c])[0],
                row_inverse=S.R.encoded([tuple(1/x for x in row)])[0],
                column_inverse=S.R.encoded([tuple(1/x for x in column)])[0],
                all_real_dyadic_units=all(unit(x) for x in row+column+b+c),native_not_asserted=True)


def bit_reverse(x,f):
    return sum(((x>>j)&1)<<(f-1-j) for j in range(f))


def probe(task):
    f,orders,kinds=task
    started=time.monotonic()
    n=1<<f
    matrices=[S.ordered_scan(order,kind) for order,kind in zip(orders,kinds)]
    first_tensor=S.coefficient_tensor(matrices[0],matrices[1])
    target=S.zeta(f)
    zero_positions=[(i,j) for i in range(n) for j in range(n) if not target[i][j]]
    left_assignments=right_candidates=0
    kernel_dimensions=Counter()
    found=None
    for tail in product((1,2),repeat=n-1):
        b=(1,)+tail
        left_assignments+=1
        middle=reduced_matrix(first_tensor,b)
        final_tensor=S.coefficient_tensor(middle,matrices[2])
        constraints=[final_tensor[i][j] for i,j in zero_positions]
        basis=field_kernel(constraints,n)
        if any(sum(a*d for a,d in zip(row,direction))%3 for row in constraints for direction in basis):
            raise AssertionError('An exact GF(3) kernel violates the original zero equations')
        kernel_dimensions[len(basis)]+=1
        for c in nonzero_normalized_kernel_vectors(constraints,basis,n):
            right_candidates+=1
            matrix=reduced_matrix(final_tensor,c)
            gauges=repair_gauges(matrix,target)
            if gauges is not None:
                found=dict(left_middle=b,right_middle=c,row_inverse=gauges[0],column_inverse=gauges[1],
                           exact_characteristic_zero_sign_lift=sign_lift(first_tensor,matrices[2],b,c,target))
                break
        if found:
            break
    if not found and left_assignments!=2**(n-1):
        raise AssertionError('A negative finite claim skipped left diagonal assignments')
    return dict(status='FINITE GF3 THREE-SCAN FACTORIZATION FOUND' if found else 'EXACT GF3 EXCLUSION FOR THESE ORDERS',
                f=f,orders=orders,kinds=kinds,normalized_left_assignments=left_assignments,
                nonzero_right_candidates=right_candidates,kernel_dimensions=dict(kernel_dimensions),
                witness=found,seconds=time.monotonic()-started,
                gaussian_diagonal_units_and_unlisted_orders_not_excluded=True)


def controls():
    L,D=S.ordered_scan((0,1),'prefix'),S.ordered_scan((0,1),'difference')
    target=S.zeta(1)
    repaired=S.multiply(S.multiply(L,L),D)
    if repaired!=target:
        raise AssertionError('The exact positive three-scan word failed')
    if S.multiply(S.multiply(L,L),tuple(tuple(abs(x) for x in row) for row in D))==target:
        raise AssertionError('An omitted difference sign passed')
    kernel=field_kernel(((1,1,0),(0,1,1)),3)
    if kernel!=((1,2,1),) or list(nonzero_normalized_kernel_vectors(((1,1,0),(0,1,1)),kernel,3))!=[(1,2,1)]:
        raise AssertionError('The finite-field homogeneous normalization failed')
    if list(nonzero_normalized_kernel_vectors(((1,0,0),),field_kernel(((1,0,0),),3),3)):
        raise AssertionError('A forced-zero scalar was accepted as invertible')
    if repair_gauges(((1,0),(0,1)),target) is not None:
        raise AssertionError('A missing required source response passed the complete operator check')
    return dict(status='PASS GF3 NORMALIZATION AND COMPLETE WORD CONTROLS',
                positive='L L D = Z1 over Q, with all scalar units one',
                negative_controls=['omitted_difference_sign','forced_zero_scalar','missing_source_response'])


def tasks():
    result=[]
    for f in (1,2,3):
        n=1<<f
        orders=tuple(dict.fromkeys((tuple(range(n)),tuple(bit_reverse(x,f) for x in range(n)))))
        for chosen in product(orders,repeat=3):
            for kinds in product(('prefix','difference'),repeat=3):
                result.append((f,chosen,kinds))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.workers<1:
        raise ValueError('Positive workers required')
    sources=(Path(__file__).resolve(),Path(S.__file__).resolve(),Path(S.R.__file__).resolve())
    hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    args.output.mkdir(parents=True,exist_ok=False)
    selected=tasks()
    (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=datetime.now(timezone.utc).isoformat(),source_closure=hashes,
        workers=args.workers,stdlib_only=True,selected_case_count=len(selected),orders=['natural','bit-reversal'],
        diagonal_domain='All nonzero GF3 values; necessary reduction for real dyadic units +/-2^k',
        amplitude_unit_and_gaussian_scope_separate=True,native_or_supplier_or_exponent_claim=False),indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(probe,selected))
    control=controls()
    if hashes!={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}:
        raise AssertionError('The effective source closure changed')
    counts={str(f):dict(Counter(row['status'] for row in rows if row['f']==f)) for f in (1,2,3)}
    receipt=dict(status='PASS SELECTED THREE-SCAN REAL-DYADIC DISCRIMINATOR',counts=counts,controls=control,rows=rows,
                 finite_found_is_not_a_characteristic_zero_lift=True,chosen_order_and_real_unit_scope_only=True)
    (args.output/'certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(status=receipt['status'],counts=counts,cases=len(rows),
                         left_assignments=sum(r['normalized_left_assignments'] for r in rows)),sort_keys=True))


if __name__=='__main__':
    main()
