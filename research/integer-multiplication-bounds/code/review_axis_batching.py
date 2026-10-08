#!/usr/bin/env python3
"""Independent global tensor-axis batching discriminator and characteristic.

The frame basis changes once, before the fixed address program is built.
No runtime gather or producer characteristic function is used. The finite
scalar network and separate complex arithmetic table are unchanged.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import resource
import sys
import time

from review_parameter_audit import log_integer
from review_pivot_batching import sparse_profile, diagonal_runs, stringify
from review_pivot_extension import independent_counts, line_projector
from review_pivot_forbidden import joined


def cycle_index(h, index):
    a, remainder = divmod(index, h*h)
    b, c = divmod(remainder, h)
    return (c*h+a)*h+b


def conjugate(A, new_index):
    n = len(A)
    assert sorted(new_index) == list(range(n))
    answer = [[Q(0)]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            answer[new_index[i]][new_index[j]] = A[i][j]
    return answer


def increasing_runs(pivots, cap):
    groups = []
    for i, j in pivots:
        if groups and groups[-1][0]+groups[-1][2] == i and groups[-1][1]+groups[-1][2] == j and groups[-1][2] < cap:
            a, b, r = groups[-1]
            groups[-1] = a, b, r+1
        else:
            groups.append((i, j, 1))
    assert sum(r for _, _, r in groups) == len(pivots)
    return groups


def middle_case(h, triple):
    s = h*h
    P = line_projector(h, triple)
    base = [[Q(int(i == j))-P[i][j] for j in range(h)] for i in range(h)]
    base_profile = sparse_profile(base)
    assert len(base_profile) == h-1
    n = h*s
    matrix = [[Q(0)]*n for _ in range(n)]
    for i in range(h):
        for j in range(h):
            if base[i][j]:
                for k in range(s):
                    matrix[i*s+k][j*s+k] = base[i][j]
    expected = [(i*s+k,j*s+k) for i,j in base_profile for k in range(s)]
    actual = sparse_profile(matrix)
    assert actual == expected
    groups = increasing_runs(actual,s)
    assert len(groups) == h-1 and all(r == s for _,_,r in groups)
    assert any(i != j and r == s for i,j,r in groups)
    return dict(h=h,triple=triple,dimension=n,exact_rank=(h-1)*s,
                lifted_base_profile_exact=True,all_middle_pivots_batched=True,
                child_groups=len(groups),every_child_rank=s,
                includes_contiguous_offdiagonal_block=True,
                groups=groups,profile_sha256=sha256(json.dumps(actual,separators=(',', ':')).encode()).hexdigest())


def joined_case(h,first,second,matched):
    assert len(set(first)&set(matched)) == 1
    old = joined(h,first,second,matched)
    permutation = [cycle_index(h,i) for i in range(h**3)]
    A = conjugate(old,permutation)
    # The old K=t_second tensor t_matched tensor F is now
    # F tensor t_second tensor t_matched. Use K rather than E holes.
    offset=h*min(second)+min(matched)
    holes=[i*h*h+offset for i in range(h)]
    for i in range(h):
        support=[(i*h+j)*h+k for j in second for k in matched]
        assert all(sum(row[j] for j in support)==0 for row in A)
    pivots=sparse_profile(A)
    assert len(pivots)==h**3-2*h and not set(holes)&{j for _,j in pivots}
    diag=diagonal_runs(pivots,h**3-1)
    groups=increasing_runs(pivots,h**3-1)
    assert sum(diag)>=h**3-4*h and len(diag)<=4*h+1
    assert max(r for _,_,r in groups)<=h*h-1
    # The tensor metric is invariant under this simultaneous permutation.
    factors=[divmod(i,h*h) for i in range(h**3)]
    entries=0
    for i,(a,bc) in enumerate(factors):
        b,c=divmod(bc,h)
        for j,(x,yz) in enumerate(factors):
            y,z=divmod(yz,h)
            before=(Q(int(a==x))-Q(1,9))*(Q(int(b==y))-Q(1,9))*(Q(int(c==z))-Q(1,9))
            after=(Q(int(c==z))-Q(1,9))*(Q(int(a==x))-Q(1,9))*(Q(int(b==y))-Q(1,9))
            assert before==after
            entries+=1
    return dict(h=h,triples=[first,second,matched],permutation='(3,1,2)',
                exact_rank=len(pivots),metric_entries=entries,
                all_conjugated_K_kernel_holes_absent=True,
                forbidden_columns=holes,diagonal_pivots=sum(diag),diagonal_runs=len(diag),
                maximum_increasing_run=max(r for _,_,r in groups),maximum_run_bound=h*h-1,
                profile_sha256=sha256(json.dumps(pivots,separators=(',', ':')).encode()).hexdigest())


def data_case(h, first, second, third):
    """A global cycle gives (I-P3) tensor (I-P12), with lower factors."""
    s=h*h
    Pa,Pb,Pc=[line_projector(h,t) for t in (first,second,third)]
    prefix=[[Q(int(a==i and b==j))-Pa[a][i]*Pb[b][j]
             for i in range(h) for j in range(h)] for a in range(h) for b in range(h)]
    base=[[Q(int(i==j))-Pc[i][j] for j in range(h)] for i in range(h)]
    p0,p1=sparse_profile(base),sparse_profile(prefix)
    k=h*min(first)+min(second)
    assert p1==[(i,s-1 if i==k else i) for i in range(s-1)]
    rows=[[base[a][i]*prefix[b][j] for i in range(h) for j in range(s)]
          for a in range(h) for b in range(s)]
    pivots=sparse_profile(rows)
    expected=[(a*s+b,i*s+j) for a,i in p0 for b,j in p1]
    assert pivots==expected and len(pivots)==(h-1)*(s-1)
    groups=increasing_runs(pivots,s)
    assert max(r for _,_,r in groups)<=s-2
    actual=sorted(r for _,_,r in groups)
    expected_runs=sorted([r for r in (k,s-k-2,1) if r]*(h-1))
    assert actual==expected_runs
    return dict(h=h,triples=[first,second,third],exact_rank=len(pivots),
                exact_tensor_profile=True,prefix_minimum=k,
                increasing_run_lengths=actual,maximum_run_bound=s-2,
                offdiagonal_base_blocks_included=True,
                profile_sha256=sha256(json.dumps(pivots,separators=(',', ':')).encode()).hexdigest())


def matdiff(A,B):
    return [[a-b for a,b in zip(x,y)] for x,y in zip(A,B)]


def phi(array,M,q):
    answer={}
    n=len(M)
    for address,payload in array.items():
        prefix,H,D=address[0],address[1:1+n],address[1+n:]
        new=tuple((H[i]+sum(M[i][j]*D[j] for j in range(n)))%q for i in range(n))
        key=(prefix,)+new+D
        assert key not in answer
        answer[key]=payload
    assert len(answer)==len(array)
    return answer


def whole_frame_controls(seed):
    rng=random.Random(seed);n,q=3,3
    zero=[[0]*n for _ in range(n)]
    eye=[[int(i==j) for j in range(n)] for i in range(n)]
    P=[[int(i==j==0) for j in range(n)] for i in range(n)]
    cycle=[1,2,0]
    permute=lambda M:[[int(v) for v in row] for row in conjugate(M,cycle)]
    sources=[matdiff(zero,P),zero]
    sinks=[eye,matdiff(eye,P)]
    addresses=[(prefix,)+entry for prefix in range(2) for entry in product(range(q),repeat=2*n)]
    checked=bad=0
    for _ in range(8):
        arrays=[{a:rng.randrange(2) for a in addresses} for _ in range(2)]
        gates=[[[rng.randrange(-2,3) for _ in range(n)] for _ in range(n)] for _ in range(3)]
        expected=[phi(arrays[1],eye,q),phi(arrays[0],eye,q)]
        def execute(changed,wrong=False):
            current=[permute(M) if changed else M for M in sources]
            value=[a.copy() for a in arrays]
            for index,G in enumerate(gates):
                target=[permute(G) if changed else G for _ in range(2)]
                if wrong and index==1:target[1]=G
                for role in range(2):
                    value[role]=phi(value[role],matdiff(target[role],current[role]),q)
                    current[role]=target[role]
                target_role=index%2
                value[target_role]={a:value[target_role][a]^value[1-target_role][a] for a in addresses}
            for role in range(2):
                sink=permute(sinks[role]) if changed else sinks[role]
                value[role]=phi(value[role],matdiff(sink,current[role]),q)
            return value
        assert execute(False)==execute(True)==expected
        checked+=2*len(addresses)
        if execute(True,True)!=expected:bad+=1
    assert bad>0
    return dict(arbitrary_dirty_array_probes=8,complete_output_payload_entries=checked,
                spectator_prefixes=2,consistent_source_gate_sink_conjugation_exact=True,
                missed_incidence_conjugation_discriminated=bad,
                unchanged_external_shear_and_role_swap=True)


def characteristic(n,data):
    h,m,R,v=[n[k] for k in ('h','m','side_roles','v')]
    middle_rank=(R+h)*v*v*h*h*(h-1)
    middle=middle_rank*log_integer(h*h,64)[0]
    count=(R+h)*v*v
    t,g=m-4*h,4*h+1
    join=count*t*(log_integer(t,64)[0]-log_integer(g,64)[1])
    joined_rank=count*(m-2*h)
    data_moment=Q(0);data_rank=0;extra={}
    if data:
        r3=(h*h-1)*(h-1);d3=m-r3;t3=m-2*d3
        g3=2*d3+1+(r3+h*h-1)//(h*h)
        if data=='exact':
            # Use a shared denominator before adding thousands of logs.
            # Flooring a certified lower interval preserves its direction.
            grid=2**256;cache={}
            def loglower(r):
                if r not in cache:
                    lower=log_integer(r,64)[0]
                    cache[r]=Q(lower.numerator*grid//lower.denominator,grid)
                return cache[r]
            total=Q(0);rank_check=0
            from math import comb
            for a in range(h-2):
                for b in range(h-2):
                    frequency=comb(h-a-1,2)*comb(h-b-1,2)
                    k=h*a+b
                    lengths=[r for r in (k,h*h-k-2,1) if r]
                    total+=frequency*sum(r*loglower(r) for r in lengths)
                    rank_check+=frequency*sum(lengths)
            assert rank_check==v*v*(h*h-1)
            data_moment=2*v*(h-1)*total
            extra.update(exact_tensor_middle_suffix_profile=True,
                         logarithm_common_grid=grid,distinct_data_logarithms=len(cache))
        else:
            assert data=='capped'
            data_moment=2*n['N']*t3*(log_integer(t3,64)[0]-log_integer(g3,64)[1])
        data_rank=2*n['N']*r3
        extra.update(data_rank_per_edge=r3,data_defect=d3,data_edge_count=2*n['N'],
                     data_diagonal=t3,data_capped_run_bound=g3,
                     old_third_axis_hole_bound_not_transferred=True)
    unchanged=n['s']-middle_rank-joined_rank-data_rank
    assert unchanged>=0
    lm=log_integer(m,64)[1]
    M=middle+join+data_moment
    first=n['s']*lm-M
    assert first>0
    def gap(a):
        assert 0<=a*lm<1
        return n['D']-a*first-a*a*n['s']*lm*lm/(2*(1-a*lm))
    lo,hi=Q(0),Q(1,10**7)
    assert gap(lo)>0 and gap(hi)<0
    for _ in range(96):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    a=Q(lo.numerator*10**24//lo.denominator,10**24)
    assert gap(a)>0 and a>Q(5385522401708297,10**24)
    return dict(variant='axis-middle-joined-data-'+data if data else 'axis-middle-joined',
                saving=a,strict_normalized_characteristic_gap=gap(a),
                counts=n,middle_old_rank=middle_rank,middle_child_rank=h*h,
                middle_child_count=middle_rank//(h*h),middle_moment_lower=middle,
                joined_old_rank=joined_rank,joined_edge_count=count,
                joined_diagonal=t,joined_run_bound=g,joined_moment_lower=join,
                data_old_rank=data_rank,data_moment_lower=data_moment,
                unchanged_rank=unchanged,first_moment_upper=first,
                total_rank_conserved=True,global_maximum_run=h*h,
                child_shrink='r*floor(e/m)<=e/h<e',
                row_depth='ceil(log_h(e))',**extra)


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--seed',type=int,default=643)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    started=time.monotonic();f=json.loads(args.finite_review.read_text())
    assert f['status']=='PASS' and f['full']['matches_immutable_producer_identity_and_compilation']
    n=independent_counts(f['full']['h'],f['full']['compiled_roles'])
    cases=[middle_case(h,triple) for h,triple in
           [(6,(0,1,2)),(6,(1,3,5)),(6,(3,4,5)),
            (8,(0,1,2)),(8,(3,6,7)),(8,(5,6,7))]]
    joined_cases=[joined_case(*c) for c in
                  [(6,(0,1,2),(3,4,5),(2,3,4)),
                   (8,(3,6,7),(0,2,6),(0,1,3))]]
    frames=whole_frame_controls(args.seed)
    data_cases=[data_case(*c) for c in
                [(6,(0,1,2),(3,4,5),(1,3,5)),
                 (8,(3,6,7),(0,2,6),(2,4,7))]]
    rows=[characteristic(n,data) for data in (False,'capped','exact')]
    assert rows[2]['saving']>rows[1]['saving']>rows[0]['saving']
    names=('review_axis_batching.py','review_pivot_batching.py','review_pivot_forbidden.py',
           'review_pivot_extension.py','review_parameter_audit.py')
    result=dict(status='PASS independent global-axis batching construction',
                generated_utc=datetime.now(timezone.utc).isoformat(),seed=args.seed,
                finite_candidate_id=f['full']['candidate_id'],
                finite_compiled_sha256=f['full']['compiled_sha256'],
                finite_review_sha256=sha256(args.finite_review.read_bytes()).hexdigest(),
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                axis_choice='(3,1,2), one simultaneous conjugation of every rational bit frame',
                middle_profiles=cases,joined_profiles=joined_cases,data_profiles=data_cases,
                whole_common_frame_controls=frames,rows=rows,
                new_prime_scope='A new fixed odd q may be required for the new canonical triangular-factor table; frame determinants unchanged',
                complex_guard_scope='Separate complex h28 scalar network and factors are unchanged',
                limitations=['No giant h51 factor table or explicit new global prime is materialized',
                             'No fixed-factor shared alphabet constant is inserted into a numerical cutoff',
                             'Full physical/rational and eventual setup transfer is a separately written mathematical argument',
                             'No integer multiplication kappa is inferred without fresh full composition'],
                wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    for row in rows:print('PASS',row['variant'],row['saving'],'new fixed axis, maximumrun',n['h']**2,flush=True)


if __name__=='__main__':main()
