#!/usr/bin/env python3
"""Independent rational envelope projector and bounded-minor review.

No native profiler is imported. Exact Gram projectors are built from a separate
integer/rational basis, then compared with the fixed-I+J low-rank formulas.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
from math import comb,lcm,factorial
import argparse,json,random,time

def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def mm(A,B):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*B)] for r in A]
def trans(A):return list(map(list,zip(*A)))
def add(A,B,s=1):return [[a+s*b for a,b in zip(r,t)] for r,t in zip(A,B)]
def rank(A):
    M=[r[:] for r in A];out=0
    for j in range(len(M[0])):
        k=next((i for i in range(out,len(M)) if M[i][j]),None)
        if k is None:continue
        M[out],M[k]=M[k],M[out];p=M[out][j]
        for i in range(out+1,len(M)):
            if M[i][j]:f=M[i][j]/p;M[i]=[a-f*b for a,b in zip(M[i],M[out])]
        out+=1
        if out==len(M):break
    return out
def envelope(h,C,O):
    c=len(C);s=3-c;n=len(O);assert c in (1,2) and n
    basis=[[Q(i==j)+Q(i in C,s) for j in O] for i in range(h)]
    G=[[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
    gram=[[Q(i==j)+Q(c-1,s*s) for j in range(n)] for i in range(n)]
    gram_inv=[[Q(i==j)-Q(c-1,s*s+(c-1)*n) for j in range(n)] for i in range(n)]
    assert mm(mm(trans(basis),G),basis)==gram and mm(gram,gram_inv)==eye(n)
    P=mm(mm(mm(basis,gram_inv),trans(basis)),G)
    # Conjugate by I+J via row/column sums, independently of supplier formula.
    sums=[sum(P[i][j] for i in range(h)) for j in range(h)]
    A=[[P[i][j]+sums[j] for j in range(h)] for i in range(h)]
    Pp=[[x-sum(row)/Q(h+1) for x in row] for row in A]
    den=3*(h+1)*(s*s+(c-1)*n)
    formula=[]
    for i in range(h):
        row=[]
        for j in range(h):
            oi,oj=int(i in O),int(j in O);wi=3+int(i in C);zj=3*(h+1)*int(j in C)-10
            num=s*oi*zj+3*(h+1)*s*wi*oj+n*wi*zj-3*(h+1)*(c-1)*oi*oj
            row.append(Q(i==j and oi)+Q(num,den))
        formula.append(row)
    assert Pp==formula
    delta=[[Q(i==j and i in O) for j in range(h)] for i in range(h)]
    assert rank(add(Pp,delta,-1))<=2
    return Pp,delta

def bound(h):
    Z=3*h-7;B0=(4*h-2)*Z+27*(h+1);D=3*(h+1)*(h-1)**2;B=2*(h-1)*B0
    values={r:sum(comb(h,j)*factorial(j)*B**j*D**(r-j) for j in range(r+1)) for r in (2,3,4)}
    ps=[2**61-1,2**31-1,2**19-1]
    assert values[2]<ps[0] and values[4]<ps[0]*ps[1]*ps[2]
    # LL provides independent primality checks for the three Mersenne primes.
    checks=[]
    for exponent in (61,31,19):
        p=2**exponent-1;x=4
        for _ in range(exponent-2):x=(x*x-2)%p
        assert x==0;checks.append(dict(exponent=exponent,prime=p,Lucas_Lehmer_residue=x))
    actual_max=0
    for c in (1,2):
        s=3-c
        for n in range(1,h-c+1):
            d=s*s+(c-1)*n;assert d<=h-1
            for oi in (0,1):
                for oj in (0,1):
                    for ci in (0,1):
                        for cj in (0,1):
                            if ci and oi or cj and oj:continue
                            wi=3+ci;zj=3*(h+1)*cj-10
                            num=s*oi*zj+3*(h+1)*s*wi*oj+n*wi*zj-3*(h+1)*(c-1)*oi*oj
                            actual_max=max(actual_max,abs(num));assert abs(num)<=B0
    return dict(h=h,Z=Z,B0=B0,D=D,B=B,max_envelope_correction_numerator=actual_max,
                minor_bounds=values,primality=checks,prime_product=ps[0]*ps[1]*ps[2],
                max_constituent_denominator=3*(h+1)*(h-1),
                exact_zero_and_nonzero_by_CRT=True)

def run(h,seed,samples):
    rng=random.Random(seed);cases=[];start=time.monotonic()
    for c in (1,2):
        for sample in range(samples):
            C=sorted(rng.sample(range(h),c));available=[i for i in range(h) if i not in C];rng.shuffle(available)
            cut=rng.randrange(1,len(available));O1=sorted(available[:cut]);O2=sorted(available[:rng.randrange(cut+1,len(available)+1)])
            P1,D1=envelope(h,C,O1);P2,D2=envelope(h,C,O2)
            correction=add(add(P2,P1,-1),add(D2,D1,-1),-1)
            actual_rank=rank(correction);assert actual_rank<=2
            cases.append(dict(core=C,outside_source=O1,outside_target=O2,
                              same_core_difference_correction_rank=actual_rank,
                              matrix_sha256=sha256(json.dumps(P2,default=str,separators=(',',':')).encode()).hexdigest()))
    return dict(status='PASS INDEPENDENT RATIONAL FIXED PROJECTOR FORMULA AND MINOR BOUNDS',h=h,seed=seed,samples=samples,cases=cases,
                bounds=bound(h),elapsed_seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='General algebraic formula/CRT-bound component and sampled rational same-core rank controls; complete transition multiset is independently checked separately')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--h',type=int,required=True);ap.add_argument('--seed',type=int,required=True);ap.add_argument('--samples',type=int,default=4);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    result=run(args.h,args.seed,args.samples);assert not args.output.exists();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','h','elapsed_seconds')}),flush=True)
if __name__=='__main__':main()
