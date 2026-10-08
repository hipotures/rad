#!/usr/bin/env python3
"""Exact rational Gram controls for final partial-output aggregation.

This does not claim a better bit circuit. Under the unchanged controller
flow, converting one-user partial outputs into one-user combiner inputs
creates no new multiuser controller candidates. The span calculation is
retained for a possible future compiler using data/output pivots.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_gaussian import check_sources,require
from downstream_parameter_optimum import as_strings


def determinant(a):
    a=[row[:] for row in a];value=Q(1)
    for col in range(len(a)):
        pivot=next((i for i in range(col,len(a)) if a[i][col]),None)
        if pivot is None:return Q(0)
        if pivot!=col:a[col],a[pivot]=a[pivot],a[col];value=-value
        p=a[col][col];value*=p
        for i in range(col+1,len(a)):
            factor=a[i][col]/p
            for j in range(col+1,len(a)):a[i][j]-=factor*a[col][j]
            a[i][col]=0
    return value


def case(h,k):
    require(h>=6 and 1<=k<=3,'Unsupported helper-union control')
    n=h-3;vectors=[]
    for j in range(1,n):
        a=[Q(0)]*h;a[3+j]=1;a[3]=-1;vectors.append(a)
    for j in range(1,k):
        a=[Q(0)]*h;a[j]=1;a[0]=-1;vectors.append(a)
    aggregate=[Q(0)]*h
    for j in range(k):aggregate[j]=Q(1,k)
    for j in range(3,h):aggregate[j]=Q(2,n)
    vectors.append(aggregate)
    def inner(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))-sum(a)*sum(b)/9
    target=[Q(1)]*3+[Q(0)]*(h-3)
    require(all(inner(a,target)==0 for a in vectors),'Aggregated span is not target-orthogonal')
    gram=[[inner(a,b) for b in vectors] for a in vectors]
    g=Q(4,n)+Q(1,k)-1
    for j in range(len(vectors)-1):require(gram[-1][j]==0,'Aggregate/deviation split failed')
    require(gram[-1][-1]==g,'Aggregate scalar Gram formula failed')
    det=determinant(gram);predicted=4*k-n*(k-1)
    require(det==predicted,'Exact helper-union determinant identity failed')
    # All triple generators in these k common-point families lie in the
    # displayed relation-defined space. Both their rational norm and
    # physical target orthogonality are independently checked.
    generators=0
    for point in range(k):
        for a in range(3,h):
            for b in range(a+1,h):
                v=[Q(0)]*h;v[point]=v[a]=v[b]=1
                require(sum(v[3:])==2*sum(v[:3]),'Source relation changed')
                require(inner(v,target)==0 and inner(v,v)==2,'Source triple Gram control failed')
                generators+=1
    return dict(h=h,helpers=k,outside_vertices=n,span_dimension=n+k-1,
                positive_deviation_dimension=n+k-2,aggregate_norm=g,
                exact_gram_determinant=det,nondegenerate=bool(det),
                signature_if_nondegenerate=('positive definite' if g>0 else 'one negative direction') if det else None,
                source_generators_checked=generators,
                singular_expected_negative_control=bool((k==2 and h==11) or (k==3 and h==9)))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,9,10,11,12,50])
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    start=time.monotonic();source=Path(__file__)
    rows=[case(h,k) for h in args.h for k in (1,2,3)]
    for row in rows:require(row['nondegenerate'] != row['singular_expected_negative_control'],
                            'Unexpected singularity outside declared control')
    result=dict(campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_deadline='2026-10-08T08:25:21Z',generated_at=datetime.now(timezone.utc).isoformat(),
                provenance=check_sources(args.upstream),
                source_sha256={source.name:hashlib.sha256(source.read_bytes()).hexdigest()},cases=rows,
                controller_flow_negative=dict(old_partial_users=1,new_partial_users=1,
                                              added_combiner_users=[1,1],new_multiuser_candidates=0,
                                              baseline_addition_delta='2v',baseline_output_delta='-2v',
                                              baseline_physical_role_delta=0),
                elapsed_seconds=time.monotonic()-start,
                status='PASS span formulas and expected singular controls; bounded negative for unchanged controller compiler',
                scope='No full new compiler, broader physical-role reuse theorem or multiplication improvement claimed')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print('PASS rational helper-union cases',len(rows),'source triple controls',sum(r['source_generators_checked'] for r in rows),flush=True)


if __name__=='__main__':main()
