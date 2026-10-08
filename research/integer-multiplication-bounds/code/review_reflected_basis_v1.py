#!/usr/bin/env python3
"""Exact all-ones reflection, canonical batches and independent saving.

This constructs the new rational address frames from Q=I-2J/h. It does
not change the scalar circuit or import a producer characteristic. All
profile and common-frame controls use exact rational or modular algebra.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import random
import resource
import sys
import time

from review_axis_batching import increasing_runs, phi
from review_parameter_audit import log_integer
from review_pivot_batching import (diagonal_runs, identity, multiply,
                                  sparse_profile, stringify, transpose)
from review_pivot_extension import independent_counts, line_projector


def reflection(h):
    return [[F(int(i==j))-F(2,h) for j in range(h)] for i in range(h)]


def line(h, triple):
    u = [F(int(i in triple))-F(6,h) for i in range(h)]
    dual = [F(int(i in triple),2)+F(h-18,6*h) for i in range(h)]
    assert sum(a*b for a,b in zip(u,dual)) == 1
    return u, dual, [[a*b for b in dual] for a in u]


def all_ground_controls():
    cases=[];triples_checked=0;matrix_checks=0
    for h in (4,5,7,8,10,12,19,51):
        R=reflection(h)
        H=[[F(int(i==j))-F(1,9) for j in range(h)] for i in range(h)]
        assert multiply(R,R)==identity(h)
        assert multiply(multiply(transpose(R),H),R)==H
        count=0
        for triple in combinations(range(h),3):
            u,v,P=line(h,triple)
            assert all(u) and all(v)
            assert u[0] and v[-1]
            if count<3:
                original=line_projector(h,triple)
                assert multiply(multiply(R,original),R)==P
                matrix_checks+=1
            count+=1
        cases.append(dict(h=h,all_triples=count,metric_entries=h*h,
                          exact_involution_and_metric_isometry=True,
                          every_first_source_and_last_dual_nonzero=True))
        triples_checked+=count
    u6,_,P6=line(6,(0,1,2))
    assert u6[0]==0 and sparse_profile([[F(int(i==j))-P6[i][j]
                                       for j in range(6)] for i in range(6)])[0][0]!=0
    _,v18,P18=line(18,(0,1,2))
    assert v18[-1]==0
    p18=sparse_profile([[F(int(i==j))-P18[i][j] for j in range(18)] for i in range(18)])
    assert p18[0][1]!=17
    return dict(cases=cases,all_triples=triples_checked,
                exact_projector_conjugations=matrix_checks,
                excluded_h6_source_zero=True,excluded_h18_dual_zero=True,
                metric_nondegenerate_scope='h != 9; promoted uniform coefficient scope h>18')


def middle_profile(h,triple):
    _,_,P=line(h,triple);s=h*h
    base=[[F(int(i==j))-P[i][j] for j in range(h)] for i in range(h)]
    expected0=[(0,h-1)]+[(i,i) for i in range(1,h-1)]
    assert sparse_profile(base)==expected0
    A=[[F(0)]*(h*s) for _ in range(h*s)]
    for i in range(h):
        for j in range(h):
            if base[i][j]:
                for k in range(s):A[i*s+k][j*s+k]=base[i][j]
    pivots=sparse_profile(A)
    assert pivots==[(i*s+k,j*s+k) for i,j in expected0 for k in range(s)]
    groups=increasing_runs(pivots,h**3)
    assert sorted(r for _,_,r in groups)==[s,(h-2)*s]
    assert sum(r for _,_,r in groups)==(h-1)*s
    return dict(h=h,triple=triple,groups=groups,full_rank=(h-1)*s,
                canonical_profile_sha256=sha256(json.dumps(pivots).encode()).hexdigest())


def data_profile(h,first,second,third):
    Pa,Pb,Pc=[line(h,t)[2] for t in (first,second,third)]
    s=h*h
    prefix=[[F(int(a==i and b==j))-Pa[a][i]*Pb[b][j]
             for i in range(h) for j in range(h)]
            for a in range(h) for b in range(h)]
    base=[[F(int(i==j))-Pc[i][j] for j in range(h)] for i in range(h)]
    p0=sparse_profile(base);p1=sparse_profile(prefix)
    assert p0==[(0,h-1)]+[(i,i) for i in range(1,h-1)]
    assert p1==[(0,s-1)]+[(i,i) for i in range(1,s-1)]
    A=[[base[a][i]*prefix[b][j] for i in range(h) for j in range(s)]
       for a in range(h) for b in range(s)]
    pivots=sparse_profile(A)
    assert pivots==[(a*s+b,i*s+j) for a,i in p0 for b,j in p1]
    groups=increasing_runs(pivots,h**3)
    assert sorted(r for _,_,r in groups)==sorted([1,s-2]*(h-1))
    assert len(pivots)==(h-1)*(s-1)
    return dict(h=h,triples=[first,second,third],full_rank=len(pivots),
                increasing_groups=groups,uniform_suffix_run=s-2,
                canonical_profile_sha256=sha256(json.dumps(pivots).encode()).hexdigest())


def joined_profile(h,first,second,matched):
    assert len(set(first)&set(matched))==1
    (ua,va,Pa),(ub,vb,Pb),(uc,vc,Pc)=[line(h,t) for t in (first,second,matched)]
    assert sum(a*b for a,b in zip(va,uc))==0
    assert multiply(Pa,Pc)==[[F(0)]*h for _ in range(h)]
    A=[[F(int(a==i and b==j and c==k))-
        (Pb[a][i]*Pa[c][k] if b==j else 0)-
        (Pb[b][j]*Pc[c][k] if a==i else 0)
        for i in range(h) for j in range(h) for k in range(h)]
       for a in range(h) for b in range(h) for c in range(h)]
    block=h*h;holes=[i*block for i in range(h)]
    for i in range(h):
        vector=[ub[j]*uc[k] for j in range(h) for k in range(h)]
        assert vector[0]
        assert all(sum(row[i*block+j]*vector[j] for j in range(block))==0 for row in A)
    pivots=sparse_profile(A)
    assert len(pivots)==h**3-2*h
    assert not set(holes)&{j for _,j in pivots}
    groups=increasing_runs(pivots,h**3)
    assert max(r for _,_,r in groups)<=block-1
    diag=diagonal_runs(pivots,h**3)
    assert sum(diag)>=h**3-4*h and len(diag)<=4*h+1
    return dict(h=h,triples=[first,second,matched],full_rank=len(pivots),
                exact_dense_kernel_relations=h,forbidden_columns=holes,
                maximum_increasing_run=max(r for _,_,r in groups),
                maximum_run_bound=block-1,diagonal_pivots=sum(diag),diagonal_runs=len(diag),
                canonical_profile_sha256=sha256(json.dumps(pivots).encode()).hexdigest())


def scalar_field_matrix(M,q):
    return [[int(F(x).numerator*pow(F(x).denominator,-1,q)%q) for x in row] for row in M]


def common_frame_controls(seed):
    rng=random.Random(seed);n=3;q=5
    R=reflection(n)
    def conjugate(M):return scalar_field_matrix(multiply(multiply(R,M),R),q)
    eye=identity(n);zero=[[F(0)]*n for _ in range(n)]
    P=[[F(int(i==j==0)) for j in range(n)] for i in range(n)]
    minusP=[[-x for x in row] for row in P]
    IminusP=[[a-b for a,b in zip(x,y)] for x,y in zip(eye,P)]
    def diff(A,B):return [[a-b for a,b in zip(x,y)] for x,y in zip(A,B)]
    addresses=[(prefix,)+a for prefix in range(2) for a in product(range(q),repeat=2*n)]
    outputs=0;negatives=0
    for _ in range(2):
        arrays=[{a:rng.randrange(2) for a in addresses} for _ in range(2)]
        gates=[[[F(rng.randrange(-2,3)) for _ in range(n)] for _ in range(n)] for _ in range(3)]
        expected=[phi(arrays[1],scalar_field_matrix(eye,q),q),
                  phi(arrays[0],scalar_field_matrix(eye,q),q)]
        def execute(wrong=False):
            current=[conjugate(minusP),conjugate(zero)]
            values=[a.copy() for a in arrays]
            for k,G in enumerate(gates):
                target=[conjugate(G),conjugate(G)]
                if wrong and k==1:target[1]=scalar_field_matrix(G,q)
                for role in range(2):
                    values[role]=phi(values[role],diff(target[role],current[role]),q)
                    current[role]=target[role]
                role=k%2
                values[role]={a:values[role][a]^values[1-role][a] for a in addresses}
            for role,sink in enumerate((eye,IminusP)):
                values[role]=phi(values[role],diff(conjugate(sink),current[role]),q)
            return values
        assert execute()==expected
        outputs+=2*len(addresses)
        if execute(True)!=expected:negatives+=1
    assert negatives
    return dict(arbitrary_dirty_array_probes=2,complete_output_entries=outputs,
                modular_address_alphabet=q,spectator_prefixes=2,
                exact_reflected_source_gate_sink_pipeline=True,
                omitted_one_conjugation_discriminated=negatives)


def characteristic(h,roles,data):
    n=independent_counts(h,roles);v,m=n['v'],n['m']
    grid=2**256
    def lower(r):
        lo=log_integer(r,64)[0]
        return F(lo.numerator*grid//lo.denominator,grid)
    rmid=h*h*(h-2);midcopies=(roles+h)*v*v
    middle=midcopies*(rmid*lower(rmid)+h*h*lower(h*h))
    joined=(roles+h)*v*v*(m-4*h)*(lower(m-4*h)-log_integer(4*h+1,64)[1])
    data_rank=2*n['N']*(h-1)*(h*h-1) if data else 0
    data_moment=2*n['N']*(h-1)*(h*h-2)*lower(h*h-2) if data else F(0)
    middle_rank=midcopies*(h-1)*h*h;joined_rank=(roles+h)*v*v*(m-2*h)
    assert middle_rank+joined_rank+data_rank<=n['s']
    lm=log_integer(m,64)[1];first=n['s']*lm-middle-joined-data_moment
    def gap(a):
        assert 0<=a*lm<1
        return n['D']-a*first-a*a*n['s']*lm*lm/(2*(1-a*lm))
    lo,hi=F(0),F(1,10**7)
    assert gap(lo)>0>gap(hi)
    for _ in range(96):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    saving=F(lo.numerator*10**24//lo.denominator,10**24)
    assert gap(saving)>0
    return dict(variant='reflected-middle-joined-tensor-data' if data else 'reflected-middle-joined',
                counts=n,explicit_saving=saving,strict_characteristic_gap=gap(saving),
                middle_moment_lower=middle,joined_moment_lower=joined,data_moment_lower=data_moment,
                middle_rank=middle_rank,joined_rank=joined_rank,data_rank=data_rank,
                maximum_middle_child=rmid,maximum_data_child=h*h-2 if data else 0,
                maximum_joined_child=h*h-1,uniform_middle_groups=[rmid,h*h],
                uniform_data_groups=[h*h-2,1] if data else [])


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--uncapped-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--seed',type=int,default=659)
    args=ap.parse_args();assert not args.output.exists()
    start=time.monotonic()
    f=json.loads(args.finite_review.read_text());old=json.loads(args.uncapped_review.read_text())
    assert f['status']=='PASS independent explicit clone finite witness'
    assert old['status']=='PASS independent uncapped middle construction and explicit witnesses'
    assert old['clone_acceptance']['candidate_id']==f['candidate_id']
    h,roles=f['full']['h'],f['full']['roles'];assert (h,roles)==(51,500703)
    ground=all_ground_controls()
    middle=[middle_profile(h,t) for h,t in ((5,(0,1,2)),(8,(3,6,7)))]
    data=[data_profile(h,a,b,c) for h,a,b,c in
          ((4,(0,1,2),(1,2,3),(0,2,3)),(5,(2,3,4),(0,1,3),(0,2,4)))]
    joined=[joined_profile(h,a,b,c) for h,a,b,c in
            ((5,(0,1,2),(0,3,4),(2,3,4)),(5,(2,3,4),(0,1,3),(0,1,2)))]
    pipeline=common_frame_controls(args.seed)
    rows=[characteristic(h,roles,flag) for flag in (False,True)]
    assert rows[1]['explicit_saving']>rows[0]['explicit_saving']
    for row in rows:
        oldvariant='tensor-data' if row['data_rank'] else 'two-family'
        predecessor=next(F(r['supplied_saving']) for r in old['rows']
                         if r['side_roles']==roles and r['variant']==oldvariant)
        assert row['explicit_saving']>predecessor
        row['uncapped_predecessor_saving']=predecessor
    names=('review_reflected_basis.py','review_axis_batching.py','review_pivot_batching.py',
           'review_pivot_extension.py','review_parameter_audit.py')
    result=dict(status='PASS independent rational reflection basis and grouped characteristics',
                generated_utc=datetime.now(timezone.utc).isoformat(),seed=args.seed,
                input_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in
                              (args.finite_review,args.uncapped_review)},
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                finite_candidate_id=f['candidate_id'],finite_compiled_sha256=f['full']['compiled_sha256'],
                ground_reflection=ground,middle_profiles=middle,data_profiles=data,
                joined_profiles=joined,whole_common_frame_controls=pipeline,rows=rows,
                new_address_table=True,no_runtime_basis_adapter=True,
                retained_uncapped_row_degree=2600,separate_complex_scalar_guard_unchanged=True,
                scope='A new fixed H-orthogonal image of every rational frame; scalar DAG and roles unchanged. New finite factor table and fixed odd-prime exclusions are eventual setup, not numerically materialized.',
                wall_seconds=time.monotonic()-start,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS',row['variant'],row['explicit_saving'],flush=True)


if __name__=='__main__':main()
