#!/usr/bin/env python3
"""Exact channel screen for additive weighted scans in two address orders.

Bit reversal and Gray-code permutations can have high rank across a fixed
cut. Their fixed-tape implementation is NOT supplied or assumed free.
Full-rank channels still require a dyadic inverse and paid complete layout.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

import weighted_scan_intertwiners as s


BASE_SHA='0e6e1e3af2da37a0ada5eb599ec568f7125479dd88717148335a7c484f4e12ac'


def order_table(f,kind):
    D=1<<f
    if kind=='bit_reverse':
        table=[int(format(a,f'0{f}b')[::-1],2) for a in range(D)]
    elif kind=='gray': table=[a^(a>>1) for a in range(D)]
    else: raise ValueError('unknown retained address order')
    if sorted(table)!=list(range(D)): raise AssertionError('address order is not bijective')
    return table


def conjugate(M,table):
    D=len(table);out=[[(0,0)]*D for _ in range(D)]
    for i in range(D):
        for j in range(D): out[table[i]][table[j]]=M[i][j]
    return out


def flatten(M): return [z for row in M for z in row]


def independent_basis(matrices):
    pivots={};chosen=[]
    for index,M in enumerate(matrices):
        row={j:(Q(z[0]),Q(z[1])) for j,z in enumerate(flatten(M)) if z!=(0,0)}
        for p,R in sorted(pivots.items()):
            factor=row.pop(p,s.ZERO)
            if factor==s.ZERO: continue
            for j,z in R.items():
                if j==p: continue
                value=s.add(row.get(j,s.ZERO),s.neg(s.multiply(factor,z)))
                if value==s.ZERO: row.pop(j,None)
                else: row[j]=value
        if row:
            p=min(row);factor=row[p]
            pivots[p]={j:s.divide(z,factor) for j,z in row.items()}
            chosen.append(index)
    return [matrices[j] for j in chosen],chosen,pivots


def member(M,pivots):
    row={j:(Q(z[0]),Q(z[1])) for j,z in enumerate(flatten(M)) if z!=(0,0)}
    for p,R in sorted(pivots.items()):
        factor=row.pop(p,s.ZERO)
        if factor==s.ZERO: continue
        for j,z in R.items():
            if j==p: continue
            value=s.add(row.get(j,s.ZERO),s.neg(s.multiply(factor,z)))
            if value==s.ZERO: row.pop(j,None)
            else: row[j]=value
    return not row


def determinant(M):
    A=[[(Q(z[0]),Q(z[1])) for z in row] for row in M];D=len(A);det=s.ONE
    for j in range(D):
        pivot=next((i for i in range(j,D) if A[i][j]!=s.ZERO),None)
        if pivot is None: return s.ZERO
        if pivot!=j: A[j],A[pivot]=A[pivot],A[j];det=s.neg(det)
        p=A[j][j];det=s.multiply(det,p)
        for i in range(j+1,D):
            if A[i][j]==s.ZERO: continue
            factor=s.divide(A[i][j],p);A[i][j]=s.ZERO
            for k in range(j+1,D): A[i][k]=s.add(A[i][k],s.neg(s.multiply(factor,A[j][k])))
    return det


def probe(task):
    f,kind=task;started=time.monotonic();D=1<<f;table=order_table(f,kind)
    if sha256(Path(s.__file__).read_bytes()).hexdigest()!=BASE_SHA:
        raise AssertionError('pinned exact arithmetic source changed')
    original,labels=s.scan_basis(D)
    all_basis=original+[conjugate(M,table) for M in original]
    basis,chosen,class_pivots=independent_basis(all_basis);k=len(basis)
    F=s.F_numerators(f);images=[s.product(F,M) for M in basis]
    vectors=[flatten(M) for M in images]+[[s.neg(z) for z in flatten(M)] for M in basis]
    equations=list(map(list,zip(*vectors)))
    pivots,null=s.nullspace(equations,2*k)
    # Y is uniquely F X and the scan-space basis is independent, so nullspace
    # projection to X is injective. No right-only auxiliary solution omitted.
    if any(all(z==s.ZERO for z in vector[:k]) for vector in null):
        raise AssertionError('right-only null vector contradicts independent output basis')
    coefficients=[s.gaussian_integer_vector(vector[:k]) for vector in null]
    channels=[s.matrix_combination(basis,vector) for vector in coefficients]
    for X in channels:
        if not member(X,class_pivots) or not member(s.product(F,X),class_pivots):
            raise AssertionError('cleared exact channel leaves either two-order scan space')
    quotients=[s.quotient_matrix(X) for X in channels]
    common_right=s.rank([row for M in quotients for row in M])
    common_left=s.rank([[M[i][j] for i in range(D-1)] for M in quotients for j in range(D-1)])
    rng=Random(202610090444+f+(101 if kind=='gray' else 0))
    samples=list(channels)
    for _ in range(4):
        samples.append(s.matrix_combination(channels,[(rng.randrange(-2,3),rng.randrange(-1,2)) for _ in channels]))
    ranks=[s.rank(X) for X in samples];best=samples[ranks.index(max(ranks))]
    stack_rank=0
    for _ in range(2):
        stack=[]
        for _bank in range(6):
            stack.extend(s.matrix_combination(channels,[(rng.randrange(-2,3),rng.randrange(-1,2)) for _ in channels]))
        stack_rank=max(stack_rank,s.rank(stack))
    upper=min(D,7+common_right)
    if stack_rank>upper: raise AssertionError('complete shared-channel stack upper bound failed')
    det=determinant(best) if max(ranks)==D else s.ZERO
    if any(z.denominator!=1 for z in det): raise AssertionError('Gaussian integer matrix has a noninteger determinant')
    norm=int(det[0]*det[0]+det[1]*det[1]);odd=norm
    while odd and odd%2==0: odd//=2
    dyadic_unit=norm!=0 and odd==1
    # The class deliberately admits a high fixed-cut-rank permutation;
    # omission of P produces the already-excluded one-order problem.
    P=[[(int(i==table[j]),0) for j in range(D)] for i in range(D)]
    lower_cross=s.rank([row[:D//2] for row in P[D//2:]])
    if kind=='bit_reverse' and lower_cross!=D//4:
        raise AssertionError('bit reversal crossing rank disagrees with its exact D/4 count')
    return dict(status='PASS EXACT TWO-ORDER SCAN CHANNEL SCREEN',selected_columns=f,address_dimension=D,
                second_order=kind,explicit_order_table=table,order_fixed_cut_rank=lower_cross,
                scan_sum_dimension=k,chosen_generator_indices=chosen,exact_constraint_rank=len(pivots),
                exact_channel_dimension=len(null),complete_channels_verified=len(channels),
                cleared_channel_coefficients_sha256=s.digest(coefficients),
                common_quotient_left_rank=common_left,common_quotient_right_rank=common_right,
                largest_tested_exact_scalar_rank=max(ranks),best_exact_matrix_sha256=s.digest(best),
                best_scalar_determinant=[str(z) for z in det],best_scalar_determinant_norm=str(norm),
                best_scalar_gaussian_dyadic_invertible=dyadic_unit,
                six_bank_input_column_rank_lower=stack_rank,six_bank_input_column_rank_upper=upper,
                complete_six_bank_capacity_excluded=upper<D,
                seed=202610090444+f+(101 if kind=='gray' else 0),sampled_combinations=4,stack_trials=2,
                order_native_compiler_supplied=False,inverse_native_word_supplied=False,
                precision_scope='Null vectors cleared to primitive Gaussian integers; odd determinant factors cannot be discarded or divided by in a native Gaussian-dyadic word.',
                scope='Complete Q(i) space X and F X in L+P L P^-1 at the declared finite dimensions. Necessary operator capacity only; two-order routing, inverses, all guards/layout and distinct-label joint core remain unpaid.',
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(s.__file__)];hashes={p.name:sha256(p.read_bytes()).hexdigest() for p in sources}
    tasks=[(f,kind) for f in (3,4) for kind in ('bit_reverse','gray')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,tasks=tasks,
                  source_sha256=hashes,stdlib_only=True,
                  hypothesis='Two additive weighted-scan orderings may lift shared source-column capacity; a positive must still pay high-rank order routing and exact dyadic inverse/native closure.',
                  resource_preflight=dict(maximum_address_dimension=16,maximum_raw_variables=296,
                                          expected_aggregate_memory_bytes_upper=512*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(probe,task):task for task in tasks}
        for future in as_completed(futures):
            result=future.result();results.append(result)
            print(json.dumps({k:result[k] for k in ('status','selected_columns','second_order','exact_channel_dimension','largest_tested_exact_scalar_rank','six_bank_input_column_rank_lower','six_bank_input_column_rank_upper','best_scalar_gaussian_dyadic_invertible','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=hashes[p.name] for p in sources):
        raise AssertionError('an effective source changed during two-order channel search')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__': main()
