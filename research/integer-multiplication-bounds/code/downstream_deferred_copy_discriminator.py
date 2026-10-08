#!/usr/bin/env python3
"""Deferred first input copy: exact scalar positive, old-frame negative.

The scalar test uses arbitrary dirty side banks shared across stages1/3.
The rank lower bound is scoped to retaining their old full-frame return
and the prescribed final data-kernel frame at a single cleanup gate.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
from random import Random
import time


def mv(A,x):
    return [sum((a*v for a,v in zip(row,x)),0) for row in A]


def f2mv(A,x):
    ans=[]
    for row in A:
        value=0
        for a,v in zip(row,x):
            if a%2:value^=v
        ans.append(value)
    return ans


def gf2_inverse(A):
    n=len(A);rows=[[x%2 for x in row]+[int(i==j) for j in range(n)] for i,row in enumerate(A)]
    for j in range(n):
        p=next(i for i in range(j,n) if rows[i][j]);rows[j],rows[p]=rows[p],rows[j]
        for i in range(n):
            if i!=j and rows[i][j]:rows[i]=[a^b for a,b in zip(rows[i],rows[j])]
    return [r[n:] for r in rows]


def scalar_probe(values,wrong=False):
    d=3;c=4;A=values[:d];B=values[d:2*d];Z0=values[2*d:2*d+c];Z1=values[2*d+c:]
    L=[[1,0,0,0],[1,1,0,0],[0,1,1,0],[1,0,1,1]];inv=gf2_inverse(L);V=[[int(i==j) for j in range(d)] for i in range(c)]
    J=inv[:d]
    assert all(f2mv(J,f2mv(L,f2mv(V,[int(i==j) for i in range(d)])))==[int(i==j) for i in range(d)] for j in range(d))
    def invocation(a,b,z,restore):
        z=f2mv(L,z);b=[x^y for x,y in zip(b,f2mv(J,z))];z=f2mv(inv,z)
        z=[x^y for x,y in zip(z,f2mv(V,a))]
        z=f2mv(L,z);b=[x^y for x,y in zip(b,f2mv(J,z))];z=f2mv(inv,z)
        if restore:z=[x^y for x,y in zip(z,f2mv(V,a))]
        return a,b,z
    A,B,Z0=invocation(A,B,Z0,False)
    B,A,Z1=invocation(B,A,Z1,True)
    A,B,Z0=invocation(A,B,Z0,True)
    Z0=[x^y for x,y in zip(Z0,f2mv(V,A if wrong else B))]
    return A+B+Z0+Z1


def rank(A):
    A=[list(map(Q,row)) for row in A];r=0
    for j in range(len(A[0])):
        p=next((i for i in range(r,len(A)) if A[i][j]),None)
        if p is None:continue
        A[r],A[p]=A[p],A[r];v=A[r][j];A[r]=[x/v for x in A[r]]
        for i in range(r+1,len(A)):
            c=A[i][j];A[i]=[x-c*y for x,y in zip(A[i],A[r])]
        r+=1
        if r==len(A):break
    return r


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();start=time.monotonic();w=14;failures=0
    rng=Random(202610080845)
    probes=[[1<<i for i in range(w)]]+[[rng.randrange(1<<20) for _ in range(w)] for _ in range(128)]
    for x in probes:
        expected=x[3:6]+x[:3]+x[6:]
        assert scalar_probe(x)==expected
        failures+=scalar_probe(x,True)!=expected
    assert failures>0
    I=[[Q(i==j) for j in range(3)] for i in range(3)];K=[[Q(i==j and i!=0) for j in range(3)] for i in range(3)]
    candidates=[[[Q(0)]*3 for _ in range(3)],I,K,
                [[Q(i==j and i==0) for j in range(3)] for i in range(3)]]
    rows=[]
    for M in candidates:
        x=rank([[a-b for a,b in zip(r,s)] for r,s in zip(I,M)])
        y=rank([[a-b for a,b in zip(r,s)] for r,s in zip(K,M)])
        assert 2*x+2*y>=2
        rows.append(dict(full_to_cleanup_rank=x,kernel_to_cleanup_rank=y,total=2*x+2*y))
    budgets=[]
    for h in (49,51,53,56):
        v=comb(h,3);N=v**3;D=N-6*v*v*h*h
        assert D>0 and 2*N>D
        budgets.append(dict(h=h,N=N,old_available_deficit=D,additional_old_frame_cleanup_rank_lower=2*N,
                            strict_excess=2*N-D))
    result=dict(status='PASS SCALAR DEFERRED RESTORATION; SCOPED OLD-CLEANUP-FRAME NEGATIVE',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        complete_scalar_dirty_basis=w,additional_word_probes=128,
        stages1_and3_use_same_dirty_bank=True,both_side_banks_restored=True,
        wrong_final_source_discriminating_probes=failures,local_rank_triangle_controls=rows,
        large_ground_budgets=budgets,
        exact_rank_inequality='2rank(I-M)+2rank(K-M)>=2rank(I-K)=2 per old full helper/kernel data pair',
        scope='Scalar restoration succeeds. Retaining old late full helper chart and prescribed final data kernel at one common cleanup gate adds at least2N rank and destroys old deficit. Source-specific late cleanup charts or changed restoration contracts are not excluded.',
        elapsed_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],result['complete_scalar_dirty_basis'],failures,flush=True)


if __name__=='__main__':main()
