#!/usr/bin/env python3
"""Exact small controls for the proposed reflected joined-block lemma."""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import resource
import time


def add(row,column,value):
    if value:
        value=row.get(column,Q(0))+value
        if value:row[column]=value
        elif column in row:del row[column]


def line(h,triple,reflected=True):
    u=[Q(int(i in triple)) for i in range(h)]
    v=[Q(int(i in triple),2)-Q(1,6) for i in range(h)]
    if reflected:
        u=[x-Q(6,h) for x in u]
        v=[Q(int(i in triple),2)+Q(h-18,6*h) for i in range(h)]
    assert sum(a*b for a,b in zip(u,v))==1
    return u,v


def projection(u,v):
    return [[a*b for b in v] for a in u]


def profile(matrix):
    """Independent exact row-rightmost elimination; column clearing is inert below."""
    rows=[dict(row) for row in matrix];pivots=[]
    for i,row in enumerate(rows):
        if not row:continue
        pivot=max(row);value=row[pivot];pivots.append((i,pivot))
        for following in rows[i+1:]:
            if pivot in following:
                factor=following[pivot]/value
                for column,entry in row.items():add(following,column,-factor*entry)
                assert pivot not in following
    assert len({c for _,c in pivots})==len(pivots)
    return pivots


def matrix(h,PA,PB,PC):
    rows=[]
    for i in range(h):
        for j in range(h):
            for k in range(h):
                row={i*h*h+j*h+k:Q(1)}
                for ip in range(h):
                    for kp in range(h):
                        add(row,ip*h*h+j*h+kp,-PB[i][ip]*PA[k][kp])
                for jp in range(h):
                    for kp in range(h):
                        add(row,i*h*h+jp*h+kp,-PB[j][jp]*PC[k][kp])
                rows.append(row)
    return rows


def inner_complement(h,PB,PC):
    rows=[]
    for j in range(h):
        for k in range(h):
            row={j*h+k:Q(1)}
            for jp in range(h):
                for kp in range(h):add(row,jp*h+kp,-PB[j][jp]*PC[k][kp])
            rows.append(row)
    return rows


def concentrated(h,PA,PB,PC,uB,vB,spike_row=0):
    S=[[Q(i==j) for j in range(h)] for i in range(h)]
    R=[[Q(i==j) for j in range(h)] for i in range(h)]
    for i in range(1,h):S[i][0]=-uB[i]/uB[0]
    for j in range(h-1):R[h-1][j]=-vB[j]/vB[h-1]
    su=[sum(S[i][j]*uB[j] for j in range(h)) for i in range(h)]
    vr=[sum(vB[i]*R[i][j] for i in range(h)) for j in range(h)]
    assert su==[uB[0]]+[Q(0)]*(h-1)
    assert vr==[Q(0)]*(h-1)+[vB[h-1]]
    D=[[sum(S[i][k]*R[k][j] for k in range(h)) for j in range(h)] for i in range(h)]
    assert all(D[i][j]==0 for i in range(h) for j in range(i+1,h))
    assert all(D[i][i]==1 for i in range(h))
    B=inner_complement(h,PB,PC);n=h*h;c=uB[0]*vB[h-1];rows=[]
    for i in range(h):
        for j in range(h):
            for k in range(h):
                row={}
                for ip in range(h):
                    if D[i][ip]:
                        for col,value in B[j*h+k].items():add(row,ip*n+col,D[i][ip]*value)
                if i==spike_row:
                    for kp in range(h):add(row,(h-1)*n+j*h+kp,-c*PA[k][kp])
                rows.append(row)
    return rows


def diagonal_runs(pivots):
    out=[];start=previous=None
    for row,col in pivots:
        if row!=col:continue
        if start is not None and row==previous+1:previous=row;continue
        if start is not None:out.append((start,previous-start+1))
        start=previous=row
    if start is not None:out.append((start,previous-start+1))
    return out


def check(h,A,C,B):
    assert len(set(A)&set(C))==1
    uA,vA=line(h,A);uC,vC=line(h,C);uB,vB=line(h,B)
    assert all(uB) and all(vB) and all(uC) and all(vC)
    assert sum(a*c for a,c in zip(vA,uC))==0
    assert sum(c*a for c,a in zip(vC,uA))==0
    PA,PB,PC=projection(uA,vA),projection(uB,vB),projection(uC,vC)
    local=profile(inner_complement(h,PB,PC));n=h*h
    expected=[(0,n-1)]+[(i,i) for i in range(1,n-1)]
    assert local==expected
    full=profile(matrix(h,PA,PB,PC));other=profile(concentrated(h,PA,PB,PC,uB,vB))
    assert full==other and len(full)==h**3-2*h
    mapping=dict(full);forced=[]
    for i in range(1,h-1):
        for r,c in local:assert mapping[i*n+r]==i*n+c
        start=i*n+1
        assert mapping.get(start-1)!=start-1 and mapping.get(start+n-2)!=start+n-2
        forced.append((start,n-2))
    runs=diagonal_runs(full)
    assert all(run in runs for run in forced)
    diagonal=sum(length for _,length in runs)
    t=h**3-4*h;g=4*h+1;mass=(h-2)*(n-2)
    assert diagonal>=t and len(runs)<=g
    assert diagonal-mass>=t-mass and len(runs)-(h-2)<=g-(h-2)
    return dict(h=h,triples=[A,C,B],exact_rank=len(full),canonical_profile=full,
                canonical_profile_sha256=sha256(json.dumps(full).encode()).hexdigest(),
                lower_concentration_profile_invariant=True,
                interior_local_profiles_exact=True,forced_maximal_diagonal_runs=forced,
                full_diagonal_runs=runs,diagonal_pivots=diagonal,
                remaining_diagonal_lower=t-mass,remaining_run_upper=g-(h-2))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists(),'Use a fresh output path'
    started=time.monotonic()
    cases=[(5,[0,1,2],[0,3,4],[2,3,4]),
           (5,[2,3,4],[0,1,4],[0,2,3]),
           (7,[0,1,2],[0,3,4],[4,5,6]),
           (7,[4,5,6],[0,1,6],[0,3,6])]
    rows=[check(*case) for case in cases]
    h=5;A,C,B=cases[0][1:]
    uA,vA=line(h,A);uC,vC=line(h,C);uB,vB=line(h,B)
    bad=dict(profile(concentrated(h,projection(uA,vA),projection(uB,vB),
                                  projection(uC,vC),uB,vB,spike_row=1)))
    n=h*h
    assert any(bad.get(n+i)!=n+i for i in range(1,n-1))
    us,vs=line(h,[2,3,4],False);uc,vc=line(h,[0,1,2],False)
    sparse=profile(inner_complement(h,projection(us,vs),projection(uc,vc)))
    assert sparse!=[(0,n-1)]+[(i,i) for i in range(1,n-1)]
    result=dict(status='PASS EXACT JOINED INTERIOR-BLOCK CONTROLS; ALL-SIZE REVIEW REQUIRED',
                campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_original_deadline='2026-10-08T08:25:21Z',campaign_deadline='2026-10-08T10:00:00Z',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),cases=rows,
                spike_inside_interior_discriminated=True,dense_first_coordinate_prerequisite_discriminated=True,
                elapsed_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Independent small exact canonical profiles and proof-only lower concentration; no finite graph replay, runtime basis transformation or promoted multiplication bound')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],len(rows),'cases',result['elapsed_seconds'],'seconds',flush=True)


if __name__=='__main__':main()
