#!/usr/bin/env python3
"""Exact rational control for the separately stored side-carrier obstruction.

Projector formulas are the fixed-I+J original-envelope formulas from pinned
PR58/PR48. This program checks the scoped rank decrease; the accompanying
proof supplies its dimension-uniform rank-variation argument. Shared ports
and a changed data/boundary decoder are expressly outside the family.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time


def projector(h,c,cover):
    """Original-envelope projector with one common point and outside cover."""
    core=1<<c;assert core&cover
    outside=cover&~core;n=outside.bit_count();den=12*(h+1)
    result=[]
    for i in range(h):
        row=[]
        for j in range(h):
            oi=(outside>>i)&1;oj=(outside>>j)&1
            wi=3+int(i==c);zj=3*(h+1)*int(j==c)-10
            row.append(F(den*int(i==j)*oi+2*oi*zj+6*(h+1)*wi*oj+n*wi*zj,den))
        result.append(row)
    return result


def multiply(a,b):
    h=len(a)
    return [[sum((a[i][k]*b[k][j] for k in range(h)),F()) for j in range(h)] for i in range(h)]


def subtract(a,b):return [[x-y for x,y in zip(ar,br)] for ar,br in zip(a,b)]


def rank(a):
    a=[row.copy() for row in a];h=len(a);r=0
    for j in range(h):
        pivot=next((i for i in range(r,h) if a[i][j]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r];value=a[r][j]
        for k in range(j,h):a[r][k]/=value
        for i in range(r+1,h):
            factor=a[i][j]
            if factor:
                for k in range(j,h):a[i][k]-=factor*a[r][k]
        r+=1
    return r


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--projector-source',required=True,type=Path)
    args=ap.parse_args();assert __debug__ and not args.output.exists()
    started=time.monotonic();rows=[];cases=[]
    for h in range(4,8):
        cases.extend((h,T,c,'exhaustive-small') for T in combinations(range(h),3) for c in T)
    for h in (23,25):
        cases.extend((h,T,c,'selected-native') for T in [(0,1,2),(0,h//2,h-1)] for c in T)
    for h,T,c,scope in cases:
        all_cover=(1<<h)-1
        excluded=sum(1<<q for q in T if q!=c)
        full=projector(h,c,all_cover);side=projector(h,c,all_cover^excluded)
        difference=subtract(full,side)
        assert rank(full)==h-1 and rank(side)==h-3 and rank(difference)==2
        assert multiply(full,full)==full and multiply(side,side)==side
        assert multiply(full,side)==side and multiply(side,full)==side
        assert multiply(difference,difference)==difference
        witness=next((j,[str(difference[i][j]) for i in range(h)]) for j in range(h) if any(difference[i][j] for i in range(h)))
        # Deliberate negative: reusing the full frame silently pays zero drop,
        # but its projector has the wrong rank and an explicit changed payload.
        assert rank(subtract(full,full))==0 and full!=side
        rows.append(dict(h=h,triple=list(T),common=c,scope=scope,
            common_rank=h-1,required_rank=h-3,drop_rank=2,
            omit_drop_negative_basis_column=witness[0],omit_drop_payload_difference=witness[1]))
    h,k=23,25;v23,v25=comb(h,3),comb(k,3);N=v23*v25
    L=v25*h*(h-1)+v23*k*(k-1)
    D23,D25=6*v23,6*v25
    weighted_D=v25*D23+v23*D25
    extra_mass=2*weighted_D
    assert weighted_D==12*N and extra_mass==24*N
    deficit=N-L;excess=extra_mass-deficit
    assert deficit==1846900 and excess>0
    result=dict(status='EXACT SCOPED RANK-DROP AND NATIVE MASS OBSTRUCTION PASS',
        recorded_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        projector_source=dict(path=str(args.projector_source),sha256=sha256(args.projector_source.read_bytes()).hexdigest()),
        exact_cases=len(rows),exhaustive_small_cases=sum(r['scope']=='exhaustive-small' for r in rows),
        selected_native_cases=sum(r['scope']=='selected-native' for r in rows),cases=rows,
        controller=dict(m=h*k,v23=v23,v25=v25,N=N,L=L,unchanged_deficit=deficit,
            minimum_downward_variation23=D23,minimum_downward_variation25=D25,
            minimum_weighted_downward_variation=weighted_D,minimum_extra_rank_mass=extra_mass,
            minimum_rank_excess_above_mW=excess),
        accepted_negative='Within the explicitly separately stored side-carrier family and unchanged boundary/controller ledger, native moment at exponent zero is already greater than one, and every positive saving increases it.',
        outside_scope=['shared ports','global remixed boundary carriers','changed data geometry or decoder','other recurrence architectures'],
        seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','exact_cases','seconds']}))


if __name__=='__main__':main()
