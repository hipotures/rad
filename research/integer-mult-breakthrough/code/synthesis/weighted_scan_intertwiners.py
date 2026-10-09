#!/usr/bin/env python3
"""Exact simultaneous weighted-scan channels across a missing Fourier block.

L_D consists of arbitrary diagonal entries and strict lower/upper entries
u_i+v_j. It is a finite sum of weighted contiguous scans, not arbitrary
products of scans, global permutations, nonlinear routes or a native word.
Solve X in L_D and C_f X in L_D over Q(i); no dyadic inverse is assumed.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
from random import Random
import time


ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def add(x,y): return x[0]+y[0],x[1]+y[1]
def neg(x): return -x[0],-x[1]
def multiply(x,y): return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def divide(x,y):
    n=y[0]*y[0]+y[1]*y[1]
    if not n: raise ValueError('zero Gaussian pivot')
    return (x[0]*y[0]+x[1]*y[1])/n,(x[1]*y[0]-x[0]*y[1])/n


def sparse_echelon(rows):
    """Exact forward elimination; normalized pivots retain all free columns."""
    pivots={}
    for original in rows:
        row={j:(Q(z[0]),Q(z[1])) for j,z in enumerate(original) if z!=(0,0)}
        for p,old in sorted(pivots.items()):
            c=row.pop(p,ZERO)
            if c==ZERO: continue
            for j,z in old.items():
                if j==p: continue
                value=add(row.get(j,ZERO),neg(multiply(c,z)))
                if value==ZERO: row.pop(j,None)
                else: row[j]=value
        if row:
            pivot=min(row);c=row[pivot]
            row={j:divide(z,c) for j,z in row.items()}
            if row[pivot]!=ONE: raise AssertionError('pivot normalization failed')
            pivots[pivot]=row
    return pivots


def nullspace(rows,variables):
    pivots=sparse_echelon(rows)
    free=[j for j in range(variables) if j not in pivots]
    vectors=[]
    for column in free:
        vector=[ZERO]*variables;vector[column]=ONE
        for p,row in sorted(pivots.items(),reverse=True):
            value=ZERO
            for j,z in row.items():
                if j!=p: value=add(value,multiply(z,vector[j]))
            vector[p]=neg(value)
        for equation in rows:
            value=ZERO
            for a,b in zip(equation,vector): value=add(value,multiply(a,b))
            if value!=ZERO: raise AssertionError('exact null vector fails an original constraint')
        vectors.append(vector)
    if len(pivots)+len(vectors)!=variables: raise AssertionError('rank/nullity mismatch')
    return pivots,vectors


def gaussian_integer_vector(vector):
    denominator=1
    for z in vector:
        for component in z: denominator=lcm(denominator,component.denominator)
    integers=[tuple(int(v*denominator) for v in z) for z in vector]
    common=0
    for z in integers:
        for v in z: common=gcd(common,abs(v))
    if common: integers=[tuple(v//common for v in z) for z in integers]
    return integers


def scan_basis(D):
    """Independent integer basis, with one additive gauge fixed per triangle."""
    basis=[];labels=[]
    def append(label,entries):
        M=[[(0,0)]*D for _ in range(D)]
        for i,j in entries: M[i][j]=(1,0)
        basis.append(M);labels.append(label)
    for i in range(D): append(('diagonal',i),[(i,i)])
    for i in range(1,D): append(('lower_row',i),[(i,j) for j in range(i)])
    for j in range(1,D-1): append(('lower_column',j),[(i,j) for i in range(j+1,D)])
    for i in range(D-1): append(('upper_row',i),[(i,j) for j in range(i+1,D)])
    for j in range(1,D-1): append(('upper_column',j),[(i,j) for i in range(j)])
    if len(basis)!=5*D-6: raise AssertionError('weighted scan space dimension wrong')
    return basis,labels


def scan_constraints(M):
    D=len(M);out=[]
    for j in range(1,D-1):
        for i in range(j+2,D):
            out.append(add(add(M[i][j],neg(M[i][0])),add(neg(M[j+1][j]),M[j+1][0])))
        for i in range(j-1):
            out.append(add(add(M[i][j],neg(M[i][D-1])),add(neg(M[j-1][j]),M[j-1][D-1])))
    if len(out)!=(D-2)*(D-3): raise AssertionError('weighted scan codimension wrong')
    return out


def F_numerators(f):
    D=1<<f;values=[]
    for d in range(f+1):
        z=(1,0)
        for _ in range(f-d): z=multiply(z,(1,1))
        for _ in range(d): z=multiply(z,(1,-1))
        values.append(z)
    return [[values[(x^y).bit_count()] for x in range(D)] for y in range(D)]


def product(A,B):
    D=len(A);out=[]
    for row in A:
        values=[]
        for j in range(len(B[0])):
            value=(0,0)
            for a,b in zip(row,B):
                if a!=(0,0) and b[j]!=(0,0): value=add(value,multiply(a,b[j]))
            values.append(value)
        out.append(values)
    return out


def matrix_combination(matrices,coefficients):
    D=len(matrices[0]);out=[[(0,0)]*D for _ in range(D)]
    for M,c in zip(matrices,coefficients):
        if c==(0,0): continue
        for i,row in enumerate(M):
            for j,z in enumerate(row):
                if z!=(0,0): out[i][j]=add(out[i][j],multiply(c,z))
    return out


def rank(M): return len(sparse_echelon(M))


def quotient_matrix(M):
    return [[add(add(M[i][j],neg(M[i][0])),add(neg(M[0][j]),M[0][0]))
             for j in range(1,len(M))] for i in range(1,len(M))]


def digest(value): return sha256(json.dumps(value,separators=(',',':')).encode()).hexdigest()


def probe(f):
    started=time.monotonic();D=1<<f;basis,labels=scan_basis(D);F=F_numerators(f)
    if any(any(z!=(0,0) for z in scan_constraints(M)) for M in basis):
        raise AssertionError('an authored scan basis element fails the class definition')
    if rank([[z for row in M for z in row] for M in basis])!=len(basis):
        raise AssertionError('the scan basis is not exactly independent')
    images=[product(F,M) for M in basis]
    constraints=[scan_constraints(M) for M in images]
    equations=list(map(list,zip(*constraints)))
    pivots,vectors=nullspace(equations,len(basis))
    integer_vectors=[gaussian_integer_vector(vector) for vector in vectors]
    channels=[matrix_combination(basis,vector) for vector in integer_vectors]
    for X in channels:
        if any(z!=(0,0) for z in scan_constraints(X)) or any(z!=(0,0) for z in scan_constraints(product(F,X))):
            raise AssertionError('cleared exact scan intertwiner left either scan class')
    quotients=[quotient_matrix(X) for X in channels]
    common_right_rank=rank([row for M in quotients for row in M])
    common_left_rank=rank([[M[i][j] for i in range(D-1)] for M in quotients for j in range(D-1)])
    rng=Random(202610090416+f)
    samples=list(channels)
    for _ in range(6):
        samples.append(matrix_combination(channels,[(rng.randrange(-2,3),rng.randrange(-1,2)) for _ in channels]))
    ranks=[rank(X) for X in samples]
    maximum=max(ranks);best=samples[ranks.index(maximum)]
    # Every L_D crossing block has rank <=2. F's crossing block is invertible.
    # F X=Y then bounds each half of X's columns by rank(X_LU)+rank(Y_LU)<=4,
    # so rank X<=8. This is an all-size necessary bound for this one-sum space.
    if maximum>min(D,8): raise AssertionError('cross-cut analytic scalar-rank bound failed')
    W=6;stack_lower=0
    for _ in range(3):
        stack=[]
        for _bank in range(W):
            stack.extend(matrix_combination(channels,[(rng.randrange(-2,3),rng.randrange(-1,2)) for _ in channels]))
        stack_lower=max(stack_lower,rank(stack))
    # X = u*1^T+1*v^T+Z, with rows(Z) in one common right space R.
    # On ker(1^T,R), a vertical W-stack has image dimension <=W.
    stack_upper=min(D,1+common_right_rank+W,W*min(D,8))
    if stack_lower>stack_upper: raise AssertionError('shared quotient channel bound failed')
    perturb=[[(0,0)]*D for _ in range(D)];perturb[D-1][1]=(1,0)
    if not any(z!=(0,0) for z in scan_constraints(perturb)):
        raise AssertionError('out-of-class triangle perturbation negative did not reject')
    if f>=4 and not any(z!=(0,0) for z in scan_constraints(F)):
        raise AssertionError('identity channel incorrectly transports the full Fourier matrix')
    return dict(status='PASS EXACT WEIGHTED SCAN INTERTWINER SPACE',selected_columns=f,address_dimension=D,
                scan_class_dimension=len(basis),scan_class_basis=labels,constraint_equations=len(equations),
                exact_constraint_rank=len(pivots),exact_intertwiner_dimension=len(vectors),
                independent_free_columns=[j for j in range(len(basis)) if j not in pivots],
                cleared_integer_basis_sha256=digest(integer_vectors),
                exact_basis_matrices_verified=len(channels),common_quotient_right_rank=common_right_rank,
                common_quotient_left_rank=common_left_rank,scalar_channel_rank_upper=min(D,8),
                largest_tested_exact_scalar_rank=maximum,largest_channel_matrix_sha256=digest(best),
                six_bank_stacked_column_rank_lower=stack_lower,six_bank_stacked_column_rank_upper=stack_upper,
                six_bank_column_capacity_excluded=stack_upper<D,seed=202610090416+f,
                sampled_combination_count=6,stacked_trials=3,
                negative_controls={'out_of_class_triangle':'REJECTED','full_F_identity_transport':('REJECTED' if f>=4 else 'NOT A REQUIRED EXCLUSION')},
                proof_scope='Entire Q(i)-linear space X in L_D and C_f X in L_D. This is a weighted scan sum, not arbitrary products, routes or all streaming algorithms. No dyadic inverse/native operator supplied.',
                precision_scope='Cleared integer basis is exact; arbitrary Q(i) elimination is analysis and is not an executable division word.',
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--columns',type=int,nargs='+',default=[2,3,4,5])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    if any(f<2 or f>5 for f in args.columns): raise ValueError('preflight supports f2..5 only')
    source=Path(__file__);source_hash=sha256(source.read_bytes()).hexdigest()
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  selected_columns=args.columns,source_sha256={source.name:source_hash},stdlib_only=True,
                  hypothesis='Exact simultaneous weighted prefix/suffix scan space may supply native-linear pre/post channels or reveal complete input-capacity loss.',
                  resource_preflight=dict(maximum_address_dimension=1<<max(args.columns),maximum_variables=5*(1<<max(args.columns))-6,
                                          expected_aggregate_memory_bytes_upper=512*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(probe,f):f for f in args.columns}
        for future in as_completed(futures):
            result=future.result();results.append(result)
            print(json.dumps({k:result[k] for k in ('status','selected_columns','exact_intertwiner_dimension','largest_tested_exact_scalar_rank','common_quotient_right_rank','six_bank_stacked_column_rank_upper','six_bank_column_capacity_excluded','seconds')}),flush=True)
    if sha256(source.read_bytes()).hexdigest()!=source_hash: raise AssertionError('effective source changed during exact scan search')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__': main()
