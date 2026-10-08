#!/usr/bin/env python3
"""Exact binary projector/shear interface and naive recursive-compiler control.

This is a different address-frame representation of the accepted complex
network. It does not certify a faster movement algorithm: naive recursive
basis changes spend more than the entire available child-count deficit.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random
import time

from downstream_gaussian import check_sources,require


def parity(a,b):return (a&b).bit_count()&1


def inverse(rows,n):
    a=[row|(1<<(n+i)) for i,row in enumerate(rows)]
    for col in range(n):
        pivot=next((i for i in range(col,n) if a[i]>>col&1),None)
        if pivot is None:return None
        a[col],a[pivot]=a[pivot],a[col]
        for i in range(n):
            if i!=col and a[i]>>col&1:a[i]^=a[col]
    return [row>>n for row in a]


def independent(vectors):
    pivots={};out=[]
    for vector in vectors:
        reduced=vector
        while reduced:
            p=reduced.bit_length()-1
            if p in pivots:reduced^=pivots[p]
            else:pivots[p]=reduced;out.append(vector);break
    return out


def orthogonal_complement(vectors,n):
    rows=independent(vectors);pivots=[]
    for col in range(n):
        at=len(pivots);pivot=next((i for i in range(at,len(rows)) if rows[i]>>col&1),None)
        if pivot is None:continue
        rows[at],rows[pivot]=rows[pivot],rows[at]
        for i in range(len(rows)):
            if i!=at and rows[i]>>col&1:rows[i]^=rows[at]
        pivots.append(col)
    free=[i for i in range(n) if i not in pivots];basis=[]
    for f in free:
        vector=1<<f
        for i,p in enumerate(pivots):
            if rows[i]>>f&1:vector|=1<<p
        basis.append(vector)
    require(all(parity(a,b)==0 for a in vectors for b in basis),'Complement basis failed')
    return basis


def projection(vectors,n):
    basis=independent(vectors);rank=len(basis)
    if not rank:return [0]*n,[]
    gram=[sum(parity(a,b)<<j for j,b in enumerate(basis)) for a in basis]
    gi=inverse(gram,rank)
    if gi is None:return None,None
    dual=[]
    for row in gi:
        value=0
        for j,b in enumerate(basis):
            if row>>j&1:value^=b
        dual.append(value)
    result=[0]*n
    for a,b in zip(basis,dual):
        for i in range(n):
            if a>>i&1:result[i]^=b
    return result,list(zip(basis,dual))


def apply(rows,value):return sum(parity(row,value)<<i for i,row in enumerate(rows))


def multiply(a,b):
    rows=[]
    for row in a:
        value=0
        while row:
            bit=row&-row;value^=b[bit.bit_length()-1];row^=bit
        rows.append(value)
    return rows


def shear(p):
    n=len(p)
    return [1<<i for i in range(n)]+[row|(1<<(n+i)) for i,row in enumerate(p)]


def controls():
    rng=random.Random(20261008);cases=[];vectors=0;attempts=0
    for n in (4,6,8,10):
        accepted=0
        while accepted<32:
            attempts+=1;matrix=[1<<i for i in range(n)]
            for _ in range(5*n):
                a,b=rng.sample(range(n),2);matrix[a]^=matrix[b]
            columns=[sum((matrix[i]>>j&1)<<i for i in range(n)) for j in range(n)]
            k=rng.randrange(n);ell=rng.randrange(k+1,n+1)
            ub,vb=columns[:k],columns[:ell]
            u,_=projection(ub,n);v,_=projection(vb,n)
            if u is None or v is None:continue
            e_basis=independent([x^apply(u,x) for x in vb])
            e,factors=projection(e_basis,n);require(e is not None,'Nested residual became degenerate')
            require([a^b for a,b in zip(u,v)]==e,'Nested projection difference is not residual projection')
            uc,_=projection(orthogonal_complement(ub,n),n)
            identity=[1<<i for i in range(n)]
            require(uc==[a^b for a,b in zip(identity,u)],'Complement projector is not I+P_U')
            su,sv,se=shear(u),shear(v),shear(e);identity2=[1<<i for i in range(2*n)]
            require(multiply(su,su)==identity2,'Binary shear is not an involution')
            require(multiply(sv,su)==se,'Binary residual shear identity failed')
            require(multiply(shear(uc),su)==shear(identity),'Source/sink full-XOR endpoint identity failed')
            product=identity2
            for a,b in factors:
                dyad=[b if a>>i&1 else 0 for i in range(n)]
                product=multiply(shear(dyad),product)
            require(product==se and len(factors)==ell-k,'Rank-one directional factor count changed')
            for _ in range(16):
                value=rng.randrange(1<<(2*n))
                require(apply(sv,apply(su,value))==apply(se,value),'Joint-address vector control failed')
                vectors+=1
            cases.append(dict(n=n,dim_U=k,dim_V=ell,residual_rank=ell-k,rank_one_children=len(factors)))
            accepted+=1
    # Alternating residuals are allowed in this shear representation.
    a,b=0b0011,0b0110;e,factors=projection([a,b],4)
    require(e is not None and parity(a,a)==parity(b,b)==0 and parity(a,b)==1,
            'Alternating-plane control was not genuinely alternating')
    product=[1<<i for i in range(8)]
    for left,right in factors:
        product=multiply(shear([right if left>>i&1 else 0 for i in range(4)]),product)
    require(product==shear(e),'Alternating-plane dyad factorization failed')
    return dict(status='PASS exact binary projector, shear, endpoint and rank-factor identities',
                seed=20261008,cases=cases,attempts=attempts,joint_address_vector_checks=vectors,
                alternating_plane_rank_two_control=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--complex-certificate',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    start=time.monotonic();source=Path(__file__);cx=json.loads(args.complex_certificate.read_text())
    row=next(r for r in cx['cases'] if r['h']==50);n=row['shared_complex_counts']
    N,W,m,s,D,L=[n[k] for k in ('N','W','m','s','D','L')]
    extra=3*N;child_count=s+extra
    require(child_count>W*m and child_count-W*m==N+2*L,'Naive recursive basis deficit control failed')
    result=dict(campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_deadline='2026-10-08T08:25:21Z',provenance=check_sources(args.upstream),
                source_sha256={source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
                input=dict(path=str(args.complex_certificate),bytes=args.complex_certificate.stat().st_size,
                           sha256=hashlib.sha256(args.complex_certificate.read_bytes()).hexdigest()),
                exact_algebra=controls(),naive_recursive_basis_negative=dict(
                    accepted_rank_children=s,accepted_deficit=D,
                    lower_bound_additional_recursive_basis_children=extra,
                    resulting_children_lower_bound=child_count,critical_W_times_m=W*m,
                    excess_over_critical=N+2*L,
                    scope='Independent per-edge basis-conjugation compiler using one or more new word-XOR child calls at each of at least3N noncoordinate source-line edges; no cancellation/amortization across edges assumed'),
                elapsed_seconds=time.monotonic()-start,generated_at=datetime.now(timezone.utc).isoformat(),
                status='PASS alternate binary address-shear algebra; naive recursive basis compiler fails to give a sublinear movement primitive',
                scope='Conditional finite address identity; no optimized full algorithm, general impossibility or improved kappa claimed')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS binary shear algebra; naive child excess',N+2*L,flush=True)


if __name__=='__main__':main()
