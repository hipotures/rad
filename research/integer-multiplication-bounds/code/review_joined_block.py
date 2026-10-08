#!/usr/bin/env python3
"""Independent reflected joined-block profiles and Jensen remainder.

Use proof-only lower factors to expose interior diagonal blocks; compare
both actual canonical profiles. Scalar/frame/table setup is unchanged.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys
import time

from review_parameter_audit import log_integer
from review_pivot_batching import identity, multiply, sparse_profile, stringify
from review_pivot_extension import independent_counts
from review_reflected_basis import line


def diagonal_groups(pivots):
    groups=[];previous=None
    for i,j in pivots:
        if i!=j:
            previous=None
            continue
        if previous is not None and i==previous+1:
            start,length=groups[-1];groups[-1]=(start,length+1)
        else:
            groups.append((i,1))
        previous=i
    return groups


def full_case(h,first,second,matched):
    assert len(set(first)&set(matched))==1
    (ua,va,Pa),(ub,vb,Pb),(uc,vc,Pc)=[line(h,t) for t in (first,second,matched)]
    assert sum(a*b for a,b in zip(va,uc))==0
    s=h*h;m=h*s
    B=[[Q(int(b==j and c==k))-Pb[b][j]*Pc[c][k]
        for j in range(h) for k in range(h)] for b in range(h) for c in range(h)]
    T=[[Pa[c][k] if b==j else Q(0)
        for j in range(h) for k in range(h)] for b in range(h) for c in range(h)]
    local=sparse_profile(B)
    assert local==[(0,s-1)]+[(i,i) for i in range(1,s-1)]
    A=[[Q(int(a==i))*B[x][y]-Pb[a][i]*T[x][y]
        for i in range(h) for y in range(s)] for a in range(h) for x in range(s)]
    S,R=identity(h),identity(h)
    for i in range(1,h):S[i][0]=-ub[i]/ub[0]
    for j in range(h-1):R[-1][j]=-vb[j]/vb[-1]
    assert all(x==0 for x in [sum(S[i][j]*ub[j] for j in range(h)) for i in range(1,h)])
    assert all(sum(vb[i]*R[i][j] for i in range(h))==0 for j in range(h-1))
    D=multiply(S,R)
    assert all(D[i][j]==0 for i in range(h) for j in range(i+1,h))
    assert all(D[i][i]==1 for i in range(h))
    # Apply the sparse tensor row/column operations directly to every
    # full matrix entry, independently of the expected block formula.
    changed=[row.copy() for row in A]
    for i in range(1,h):
        for x in range(s):
            changed[i*s+x]=[a-ub[i]/ub[0]*b for a,b in zip(changed[i*s+x],A[x])]
    before_right=[row.copy() for row in changed]
    for j in range(h-1):
        for y in range(s):
            for x in range(m):
                changed[x][j*s+y]-=vb[j]/vb[-1]*before_right[x][(h-1)*s+y]
    coefficient=ub[0]*vb[-1]
    expected=[[D[a][i]*B[x][y]-(coefficient*T[x][y] if a==0 and i==h-1 else 0)
               for i in range(h) for y in range(s)] for a in range(h) for x in range(s)]
    assert changed==expected
    raw_profile=sparse_profile(A);profile=sparse_profile(changed)
    assert profile==raw_profile and len(profile)==m-2*h
    mapping=dict(profile)
    for i in range(1,h-1):
        assert mapping[i*s]==i*s+s-1
        assert all(mapping[i*s+j]==i*s+j for j in range(1,s-1))
        assert mapping.get(i*s+s-1)!=i*s+s-1
    groups=diagonal_groups(profile)
    known={(i*s+1,s-2) for i in range(1,h-1)}
    assert known<=set(groups)
    remaining=[pair for pair in groups if pair not in known]
    t=m-4*h-(h-2)*(s-2);g=4*h+1-(h-2)
    assert t==2*(h-2)*(h+1) and g==3*(h+1)
    assert sum(r for _,r in groups)>=m-4*h and len(groups)<=4*h+1
    assert sum(r for _,r in remaining)>=t and len(remaining)<=g
    assert not {i*s for i in range(h)}&{j for _,j in profile}
    assert max(r for _,r in groups)<=s-1
    assert mapping[0]!=s-1  # The first outer block is not another untouched B.
    return dict(h=h,triples=[first,second,matched],dimension=m,
                exact_lower_tensor_transform_entries=m*m,
                original_and_transformed_canonical_profile_equal=True,
                canonical_rank=len(profile),known_maximal_diagonal_runs=sorted(known),
                remaining_diagonal_pivots=sum(r for _,r in remaining),
                remaining_diagonal_runs=len(remaining),
                remainder_lower_pivots=t,remainder_upper_runs=g,
                all_spaced_kernel_holes_absent=True,
                first_outer_block_not_uniform_negative=True,
                canonical_profile_sha256=sha256(json.dumps(profile).encode()).hexdigest())


def characteristic(h,roles):
    n=independent_counts(h,roles);v,m=n['v'],n['m'];s=h*h
    grid=2**256
    def lower(r):
        lo=log_integer(r,64)[0]
        return Q(lo.numerator*grid//lo.denominator,grid)
    lm=log_integer(m,64)[1]
    middle=(roles+h)*v*v*(s*(h-2)*lower(s*(h-2))+s*lower(s))
    J=(roles+h)*v*v
    known=(h-2)*(s-2)
    remainder=m-4*h-known;groups=3*h+3
    joined_block=J*known*lower(s-2)
    joined_remainder=J*remainder*(lower(remainder)-log_integer(groups,64)[1])
    joined=joined_block+joined_remainder
    oldjoined=J*(m-4*h)*(lower(m-4*h)-log_integer(4*h+1,64)[1])
    assert remainder==2*(h-2)*(h+1)>groups and joined>oldjoined
    data=2*n['N']*(h-1)*(s-2)*lower(s-2)
    first=n['s']*lm-middle-joined-data
    assert first>0
    def gap(a):
        assert 0<=a*lm<1
        return n['D']-a*first-a*a*n['s']*lm*lm/(2*(1-a*lm))
    lo,hi=Q(0),Q(1,10**7)
    assert gap(lo)>0>gap(hi)
    for _ in range(96):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    a=Q(lo.numerator*10**24//lo.denominator,10**24)
    assert gap(a)>0
    return dict(counts=n,explicit_saving=a,strict_independent_characteristic_gap=gap(a),
                middle_moment_lower=middle,joined_block_moment_lower=joined_block,
                joined_remainder_moment_lower=joined_remainder,joined_moment_lower=joined,
                old_joined_jensen_moment_lower=oldjoined,data_moment_lower=data,
                joined_known_diagonal_pivots=known,joined_known_diagonal_runs=h-2,
                joined_remainder_lower_pivots=remainder,joined_remainder_upper_runs=groups,
                maximum_child=s*(h-2),first_moment_upper=first)


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reflection-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    start=time.monotonic();f=json.loads(args.reflection_review.read_text())
    assert f['status']=='PASS independent rational reflection basis and grouped characteristics'
    for name,digest in f['source_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    n=f['rows'][0]['counts'];h,roles=n['h'],n['side_roles']
    assert (h,roles)==(51,500703)
    cases=[full_case(h,a,b,c) for h,a,b,c in
           ((5,(0,2,4),(1,2,3),(0,1,3)),
            (5,(1,3,4),(0,2,4),(0,1,2)),
            (7,(0,2,6),(1,3,5),(2,3,4)))]
    row=characteristic(h,roles)
    old=Q(f['rows'][1]['explicit_saving'])
    assert row['explicit_saving']>old
    names=('review_joined_block.py','review_reflected_basis.py','review_parameter_audit.py',
           'review_pivot_batching.py','review_pivot_extension.py')
    result=dict(status='PASS independent reflected joined interior blocks and remainder characteristic',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                input_sha256={str(args.reflection_review):sha256(args.reflection_review.read_bytes()).hexdigest()},
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                finite_candidate_id=f['finite_candidate_id'],finite_compiled_sha256=f['finite_compiled_sha256'],
                full_profile_cases=cases,row=row,reflected_predecessor_saving=old,
                same_actual_fixed_address_table=True,new_runtime_adapter=False,
                retained_uncapped_row_degree=2600,
                scope='Sharpened lower bound on moments of actual existing canonical joined groups. Proof-only lower factors expose their interior profiles; no fixed table, role, frame, scalar or tape change.',
                wall_seconds=time.monotonic()-start,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],row['explicit_saving'],flush=True)


if __name__=='__main__':main()
