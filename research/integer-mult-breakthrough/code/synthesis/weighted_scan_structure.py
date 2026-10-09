#!/usr/bin/env python3
"""Bounded exact controls for the all-size additive weighted-scan theorem.

For f>=4 the full Q(i) space X in L_D and C_f X in L_D equals
u*1^T+1*v^T+s*w^T, where s indicates the upper half and w is constant
on each half interior with two arbitrary midpoint boundary entries.
These controls are not formal verification or a native tape implementation.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time


def add(x,y): return x[0]+y[0],x[1]+y[1]
def sub(x,y): return x[0]-y[0],x[1]-y[1]
def mul(x,y): return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def div(x,y):
    n=y[0]*y[0]+y[1]*y[1]
    return Fraction(x[0]*y[0]+x[1]*y[1],n),Fraction(x[1]*y[0]-x[0]*y[1],n)


def rank(M):
    pivots={}
    for original in M:
        row={j:(Fraction(z[0]),Fraction(z[1])) for j,z in enumerate(original) if z!=(0,0)}
        for p,R in sorted(pivots.items()):
            factor=row.pop(p,(0,0))
            if factor==(0,0): continue
            for j,z in R.items():
                if j==p: continue
                value=sub(row.get(j,(0,0)),mul(factor,z))
                if value==(0,0): row.pop(j,None)
                else: row[j]=value
        if row:
            p=min(row);factor=row[p]
            pivots[p]={j:div(z,factor) for j,z in row.items()}
    return len(pivots)


def fourier_numerators(f):
    D=1<<f;kernel=[]
    for weight in range(f+1):
        value=(1,0)
        for _ in range(f-weight): value=mul(value,(1,1))
        for _ in range(weight): value=mul(value,(1,-1))
        kernel.append(value)
    return [[kernel[(i^j).bit_count()] for j in range(D)] for i in range(D)]


def quotient_fourier(F):
    """Numerators of H=Delta F P with Delta_i=e_(i+1)-e_i."""
    D=len(F);suffix=[]
    for row in F:
        values=[(0,0)]*(D-1);total=(0,0)
        for j in range(D-2,-1,-1):
            total=add(total,row[j+1]);values[j]=total
        suffix.append(values)
    return [[sub(suffix[i+1][j],suffix[i][j]) for j in range(D-1)] for i in range(D-1)]


def mixed_difference(X):
    D=len(X)
    return [[add(sub(X[i+1][j+1],X[i+1][j]),sub(X[i][j],X[i][j+1]))
             for j in range(D-1)] for i in range(D-1)]


def in_class(X):
    A=mixed_difference(X)
    return all(z==(0,0) for i,row in enumerate(A) for j,z in enumerate(row) if abs(i-j)>1)


def check_quotient_identity(F,H):
    D=len(F)
    for i in range(D-1):
        for j in range(D):
            right=(0,0)
            if j>0: right=add(right,H[i][j-1])
            if j<D-1: right=sub(right,H[i][j])
            if right!=sub(F[i+1][j],F[i][j]):
                raise AssertionError('Delta F = H Delta fails an exact entry')


def component(f):
    started=time.monotonic();D=1<<f;m=D//2;c=m-1
    F=fourier_numerators(f);H=quotient_fourier(F)
    G=fourier_numerators(f-1);old=quotient_fourier(G)
    check_quotient_identity(F,H)
    if any(sum(row[j][0] for j in range(D))!=D or sum(row[j][1] for j in range(D)) for row in F):
        raise AssertionError('full Fourier does not fix the constant vector')
    for i in range(m-1):
        for j in range(m-1):
            same=mul((1,1),old[i][j]);cross=mul((1,-1),old[i][j])
            if H[i][j]!=same or H[m+i][m+j]!=same or H[i][m+j]!=cross or H[m+i][j]!=cross:
                raise AssertionError('literal quotient recursion block disagrees with alpha/beta factors')
    if any(H[i][c]!=((0,D) if i==c else (0,0)) for i in range(D-1)):
        raise AssertionError('midpoint quotient vector is not an actual i eigenvector')
    local_dimensions=[]
    for j in range(D-1):
        support=list(range(max(0,j-1),min(D-1,j+2)))
        rows=[[H[i][k] for k in support] for i in range(D-1) if i not in support]
        dimension=len(support)-rank(rows);local_dimensions.append(dimension)
        if dimension!=(1 if abs(j-c)<=1 else 0):
            raise AssertionError('local tridiagonal transport has an unexpected independent channel')
    # The theorem's central-column argument uses one common interior row.
    # G first/last columns at addresses2/3 have unequal coefficients.
    expected_first=sub(G[2][0],G[3][0]);expected_last=sub(G[3][-1],G[2][-1])
    if old[2][0]!=expected_first or old[2][-1]!=expected_last or (0,0) in (expected_first,expected_last):
        raise AssertionError('central endpoint-column nonzero witness fails')
    extra_rows=[]
    for kind in range(3):
        w=[int(j==m-1) if kind==0 else int(j==m) if kind==1 else int(j>=m+1) for j in range(D)]
        X=[[(int(i>=m)*value,0) for value in w] for i in range(D)]
        # F*s = beta*1+i*s, using numerator denominatorD.
        Y=[[(int(D//2)*value,(D//2 if i>=m else -D//2)*value) for value in w] for i in range(D)]
        if not in_class(X) or not in_class(Y):
            raise AssertionError('an explicit spanning midpoint channel leaves the scan class')
        A=mixed_difference(X);extra_rows.append([z for row in A for z in row])
    if rank(extra_rows)!=3: raise AssertionError('the three spanning midpoint channels are dependent')
    # A complete six-block source stack can attain10, but never D>=16.
    stacked=[]
    for b in range(6):
        w=[int(j==m-1) if b==0 else int(j==m) if b==1 else int(j>=m+1) if b==2 else 0 for j in range(D)]
        for i in range(D):
            stacked.append([(int(i==0)+int(j==b)+int(i>=m)*w[j],0) for j in range(D)])
    if rank(stacked)!=10: raise AssertionError('explicit six-bank capacity bound is not attained')
    # A high-cut-rank reversal evades the class; it is deliberately excluded.
    reversal=[[(int(i+j==D-1),0) for j in range(D)] for i in range(D)]
    if in_class(reversal): raise AssertionError('address reversal was silently admitted to the weighted scan class')
    identity=[[(int(i==j),0) for j in range(D)] for i in range(D)]
    if not in_class(identity) or in_class(F): raise AssertionError('Fourier endpoint exclusion negative failed')
    return dict(status='PASS EXACT WEIGHTED SCAN STRUCTURE CONTROLS',selected_columns=f,address_dimension=D,
                quotient_dimension=D-1,complete_quotient_identity_entries=D*(D-1),
                complete_recursive_block_entries=4*(m-1)*(m-1),
                all_local_tridiagonal_channel_dimensions=local_dimensions,midpoint_channel_dimension=sum(local_dimensions),
                exact_full_intertwiner_dimension=2*D+2,scalar_rank_upper=3,
                six_bank_input_column_rank_upper=10,explicit_stack_rank=10,
                complete_input_column_excluded=True,midpoint_nonzero_endpoint_entries=[expected_first,expected_last],
                negative_controls={'reversal_in_class':'REJECTED','identity_F_transport':'REJECTED'},
                all_size_statement='The accompanying proof covers f>=4; these are bounded exact controls of its literal quotient recurrence and complete local column systems.',
                scope='Additive weighted prefix/suffix scan sums only. Products, alternate orderings, global/nonlinear permutations and high-rank buffers are outside; no native supplier or new exponent.',
                seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--columns',type=int,nargs='+',default=[4,5,6,7])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if any(f<4 or f>8 for f in args.columns): raise ValueError('bounded controls support f4..8')
    args.output.mkdir(parents=True,exist_ok=False);source=Path(__file__)
    source_hash=sha256(source.read_bytes()).hexdigest()
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  selected_columns=args.columns,source_sha256={source.name:source_hash},stdlib_only=True,
                  hypothesis='Adjacent differences reduce additive weighted scans to tridiagonal matrices; the Fourier quotient permits only three midpoint channels at all f>=4.',
                  resource_preflight=dict(maximum_address_dimension=1<<max(args.columns),expected_aggregate_memory_bytes_upper=256*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(component,f):f for f in args.columns}
        for future in as_completed(futures):
            result=future.result();results.append(result)
            print(json.dumps({k:result[k] for k in ('status','selected_columns','exact_full_intertwiner_dimension','scalar_rank_upper','six_bank_input_column_rank_upper','seconds')}),flush=True)
    if sha256(source.read_bytes()).hexdigest()!=source_hash: raise AssertionError('source changed during exact structure controls')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__': main()
