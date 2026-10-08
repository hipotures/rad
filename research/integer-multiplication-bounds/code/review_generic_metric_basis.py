#!/usr/bin/env python3
"""Exact simultaneous rational reflections and complementary pivot flags.

No producer characteristic or generic-basis code is imported. The finite
family construction raises deficient flags using explicit linear factors
and preserves full flags using determinant-lemma quadratic factors.
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
from review_pivot_batching import (identity, invert, multiply, sparse_profile,
                                  stringify, transpose)
from review_pivot_extension import independent_counts
from review_reflected_basis import line, scalar_field_matrix
from review_axis_batching import phi


def rref(A):
    rows=[list(map(Q,row)) for row in A]
    if not rows:return rows,[]
    pivots=[];i=0
    for j in range(len(rows[0])):
        p=next((k for k in range(i,len(rows)) if rows[k][j]),None)
        if p is None:continue
        rows[i],rows[p]=rows[p],rows[i]
        c=rows[i][j];rows[i]=[a/c for a in rows[i]]
        for k in range(len(rows)):
            if k!=i and rows[k][j]:
                c=rows[k][j];rows[k]=[a-c*b for a,b in zip(rows[k],rows[i])]
        pivots.append(j);i+=1
        if i==len(rows):break
    return rows,pivots


def rank(A):return len(rref(A)[1])


def null_vector(A):
    rows,pivots=rref(A);n=len(A[0])
    j=next(j for j in range(n) if j not in pivots)
    v=[Q(int(k==j)) for k in range(n)]
    for i,k in enumerate(pivots):v[k]=-rows[i][j]
    assert all(sum(a*b for a,b in zip(row,v))==0 for row in A)
    return v


def matrix_vector(A,v):return [sum(a*b for a,b in zip(row,v)) for row in A]


def row_vector(v,A):return [sum(a*b for a,b in zip(v,col)) for col in zip(*A)]


def minus_identity_product(U,V):
    P=multiply(U,V);n=len(U)
    return [[Q(int(i==j))-P[i][j] for j in range(n)] for i in range(n)]


def dual(G,U):
    GU=multiply(G,U);gram=multiply(transpose(U),GU)
    return multiply(invert(gram),transpose(GU))


def check_dual(G,U,V):
    d=len(V);GU=multiply(G,U);gram=multiply(transpose(U),GU)
    assert multiply(V,U)==identity(d)
    assert multiply(gram,V)==transpose(GU)
    return d


def flag_cache(U,V):
    n=len(U);d=len(V);answer=[]
    for name,A in (('front',U[:d]),('back',[row[n-d:] for row in V])):
        k=rank(A)
        item=dict(name=name,rank=k,matrix=A)
        if k==d:item['inverse']=invert(A)
        else:
            item['left_null']=null_vector(transpose(A))
            item['right_null']=null_vector(A)
        answer.append(item)
    return answer


def simultaneous_reflections(G,pairs,seed):
    """Seeded integer candidates followed by a proven finite tensor grid."""
    n=len(G);rng=random.Random(seed)
    original=[([row.copy() for row in U],[row.copy() for row in V]) for U,V in pairs]
    pairs=[([row.copy() for row in U],[row.copy() for row in V]) for U,V in pairs]
    for U,V in pairs:check_dual(G,U,V)
    T=identity(n);steps=[];initial=None
    while True:
        caches=[flag_cache(U,V) for U,V in pairs]
        ranks=[[x['rank'] for x in cache] for cache in caches]
        if initial is None:initial=ranks
        if all(k==len(V) for row,(_,V) in zip(ranks,pairs) for k in row):break
        # Each deficient flag contributes two nonzero linear factors;
        # each full flag contributes one nonzero quadratic factor.
        degree=2+sum(2 for cache in caches for _ in cache)
        assert degree==2+4*len(pairs)
        attempts=0;selected=None
        candidates=([rng.randrange(-2,3) for _ in range(n)] for _ in range(128))
        for candidate_source in (candidates,product(range(degree+1),repeat=n)):
            for w0 in candidate_source:
                attempts+=1;w=list(map(Q,w0));wg=row_vector(w,G)
                norm=sum(a*b for a,b in zip(w,wg))
                if not norm:continue
                work=[];valid=True
                for (U,V),cache in zip(pairs,caches):
                    d=len(V);a_front=w[:d];b_front=row_vector(wg,U)
                    a_back=matrix_vector(V,w);b_back=wg[n-d:]
                    for item,a,b in zip(cache,(a_front,a_back),(b_front,b_back)):
                        if item['rank']==d:
                            determinant_factor=norm-2*sum(x*y for x,y in
                                zip(b,matrix_vector(item['inverse'],a)))
                            if not determinant_factor:valid=False;break
                        elif not (sum(x*y for x,y in zip(item['left_null'],a)) and
                                  sum(x*y for x,y in zip(b,item['right_null']))):
                            valid=False;break
                    if not valid:break
                    work.append((b_front,a_back))
                if valid:selected=(w,wg,norm,work);break
            if selected is not None:break
        assert selected is not None
        w,wg,norm,work=selected
        factor=2/norm
        changed=[]
        for (U,V),(b_front,a_back) in zip(pairs,work):
            U1=[[a-factor*w[i]*b_front[j] for j,a in enumerate(row)] for i,row in enumerate(U)]
            V1=[[a-factor*a_back[i]*wg[j] for j,a in enumerate(row)] for i,row in enumerate(V)]
            changed.append((U1,V1))
        wt=row_vector(wg,T)
        T=[[a-factor*w[i]*wt[j] for j,a in enumerate(row)] for i,row in enumerate(T)]
        newranks=[[rank(U[:len(V)]),rank([row[n-len(V):] for row in V])] for U,V in changed]
        assert all(k1==min(k0+1,len(V)) for old,new,(_,V) in zip(ranks,newranks,pairs)
                   for k0,k1 in zip(old,new))
        steps.append(dict(integer_direction=[int(x) for x in w],norm=norm,
                          candidates_tested=attempts,product_degree_bound=degree,
                          old_ranks=ranks,new_ranks=newranks))
        pairs=changed
        assert len(steps)<=max(len(V) for _,V in pairs)
    for U,V in pairs:check_dual(G,U,V)
    if n<=12:
        assert multiply(multiply(transpose(T),G),T)==G
        Tinv=invert(T)
        for (U,V),(U0,V0) in zip(pairs,original):
            assert U==multiply(T,U0) and V==multiply(V0,Tinv)
    return pairs,T,dict(dimension=n,kernel_dimensions=[len(V) for _,V in pairs],
                        initial_ranks=initial,final_ranks=ranks,reflection_steps=steps,
                        rounds=len(steps),all_dual_gram_identities_exact=True,
                        full_metric_and_conjugation_checked=n<=12)


def complementary_profile(U,V):
    n=len(U);d=len(V);assert 2*d<n and multiply(V,U)==identity(d)
    assert rank(U[:d])==rank([row[n-d:] for row in V])==d
    A=minus_identity_product(U,V);p=sparse_profile(A)
    assert len(p)==n-d
    assert [i for i,_ in p[:d]]==list(range(d))
    assert {j for _,j in p[:d]}==set(range(n-d,n))
    assert p[d:]==[(i,i) for i in range(d,n-d)]
    return dict(dimension=n,kernel_dimension=d,canonical_rank=len(p),
                first_offdiagonal_pivots=p[:d],one_diagonal_run=[d,n-2*d],
                final_d_rows_zero=True,
                canonical_profile_sha256=sha256(json.dumps(p).encode()).hexdigest())


def abstract_controls(seed):
    results=[]
    for c,(n,diagonal) in enumerate(((5,[1]*5),(7,[1,-1,1,-1,1,-1,1]),
                                   (9,[1]*8+[-2]),(12,[1,-1]*6))):
        G=[[Q(diagonal[i] if i==j else 0) for j in range(n)] for i in range(n)]
        positions=[(1,3),(n-3,n-2),tuple(range(min(4,(n-1)//2)))]
        pairs=[]
        for index in positions:
            U=[[Q(int(i==j)) for j in index] for i in range(n)]
            pairs.append((U,dual(G,U)))
        changed,T,record=simultaneous_reflections(G,pairs,seed+c)
        record['profiles']=[complementary_profile(U,V) for U,V in changed]
        assert any(k<d for row,d in zip(record['initial_ranks'],record['kernel_dimensions']) for k in row)
        record['positive_metric']=all(x>0 for x in diagonal)
        results.append(record)
    # Missing flag assumptions can leave the diagonal profile fragmented.
    U=[[Q(int(i==j)) for j in (2,5)] for i in range(8)]
    V=transpose(U);p=sparse_profile(minus_identity_product(U,V))
    assert p==[(0,0),(1,1),(3,3),(4,4),(6,6),(7,7)]
    assert not any(p[k:k+4]==[(i,i) for i in range(i0,i0+4)]
                   for k in range(len(p)) for i0 in range(5))
    # Flags alone do not supply the projector relation VU=I.
    U,V=changed[0];wrong=[[2*x for x in row] for row in V]
    assert len(sparse_profile(minus_identity_product(U,wrong)))==len(U)
    return results,dict(missing_flags_fragmentation=True,missing_projector_relation_full_rank=True)


def tensor_ground_controls(seed):
    h=5;n=h**3;H=[[Q(int(i==j))-Q(1,9) for j in range(h)] for i in range(h)]
    addresses=list(product(range(h),repeat=3))
    G=[[H[a][i]*H[b][j]*H[c][k] for i,j,k in addresses] for a,b,c in addresses]
    pairs=[];names=[]
    for first,second,matched in (((0,1,2),(1,2,3),(0,3,4)),
                                 ((1,3,4),(0,2,4),(0,1,2))):
        (ua,va,_),(ub,vb,_),(uc,vc,_)=[line(h,t) for t in (first,second,matched)]
        assert sum(a*b for a,b in zip(va,uc))==0
        U=[[ub[a]*Q(int(b==j))*ua[c] for j in range(h)]+
           [Q(int(a==i))*ub[b]*uc[c] for i in range(h)] for a,b,c in addresses]
        V=([[vb[a]*Q(int(b==j))*va[c] for a,b,c in addresses] for j in range(h)]+
           [[Q(int(a==i))*vb[b]*vc[c] for a,b,c in addresses] for i in range(h)])
        pairs.append((U,V));names.append('actual-joined-orthogonal-kernel')
    ub,vb,_=line(h,(0,2,4))
    U=[[ub[a]*Q(int(b*h+c==j)) for j in range(h*h)] for a,b,c in addresses]
    V=[[vb[a]*Q(int(b*h+c==j)) for a,b,c in addresses] for j in range(h*h)]
    pairs.append((U,V));names.append('actual-middle-kernel')
    changed,T,record=simultaneous_reflections(G,pairs,seed)
    record['family_names']=names
    record['profiles']=[complementary_profile(U,V) for U,V in changed]
    assert record['rounds']>0
    return record


def dirty_endpoint_control(seed):
    n=3;G=identity(n);U=[[Q(int(i==1))] for i in range(n)]
    pairs,T,record=simultaneous_reflections(G,[(U,transpose(U))],seed)
    Tinv=invert(T);rng=random.Random(seed);q=5
    while any(x.denominator%q==0 for A in (T,Tinv) for row in A for x in row):
        q=next(k for k in range(q+2,102,2) if all(k%j for j in range(2,k)))
    assert q<=11
    def conjugate(A):return scalar_field_matrix(multiply(multiply(T,A),Tinv),q)
    eye=identity(n);zero=[[Q(0)]*n for _ in range(n)]
    P=multiply(U,transpose(U));minusP=[[-x for x in row] for row in P]
    endpoint=[[x-y for x,y in zip(a,b)] for a,b in zip(eye,P)]
    def diff(A,B):return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]
    addresses=[(prefix,)+a for prefix in range(2) for a in product(range(q),repeat=2*n)]
    arrays=[{a:rng.randrange(2) for a in addresses} for _ in range(2)]
    gates=[[[Q(rng.randrange(-2,3)) for _ in range(n)] for _ in range(n)] for _ in range(3)]
    expected=[phi(arrays[1],scalar_field_matrix(eye,q),q),phi(arrays[0],scalar_field_matrix(eye,q),q)]
    def execute(wrong=False):
        current=[conjugate(minusP),conjugate(zero)];values=[x.copy() for x in arrays]
        for k,G0 in enumerate(gates):
            target=[conjugate(G0),conjugate(G0)]
            if wrong and k==1:target[1]=scalar_field_matrix(G0,q)
            for role in range(2):
                values[role]=phi(values[role],diff(target[role],current[role]),q)
                current[role]=target[role]
            role=k%2;values[role]={a:values[role][a]^values[1-role][a] for a in addresses}
        for role,sink in enumerate((eye,endpoint)):
            values[role]=phi(values[role],diff(conjugate(sink),current[role]),q)
        return values
    assert execute()==expected and execute(True)!=expected
    return dict(complete_output_entries=2*len(addresses),arbitrary_dirty_arrays=2,
                q=q,spectator_prefixes=2,full_source_gate_sink_conjugation=True,
                omitted_one_conjugation_discriminated=True,reflection_record=record)


def characteristic(h,roles):
    c=independent_counts(h,roles);v,m=c['v'],c['m'];grid=2**256
    def lower(x):
        lo=log_integer(x,64)[0];return Q(lo.numerator*grid//lo.denominator,grid)
    dmid=h*h;djoin=2*h;ddata=h*h+h-1
    assert 2*max(dmid,djoin,ddata)<m
    J=(roles+h)*v*v;middle=J*(m-2*dmid)*lower(m-2*dmid)
    joined=J*(m-2*djoin)*lower(m-2*djoin)
    data=2*c['N']*(m-2*ddata)*lower(m-2*ddata)
    ranks=dict(middle=J*(m-dmid),joined=J*(m-djoin),data=2*c['N']*(m-ddata))
    assert sum(ranks.values())<=c['s']
    lm=log_integer(m,64)[1];first=c['s']*lm-middle-joined-data
    assert first>0
    def gap(a):
        assert 0<=a*lm<1
        return c['D']-a*first-a*a*c['s']*lm*lm/(2*(1-a*lm))
    lo,hi=Q(0),Q(1,10**5);assert gap(lo)>0>gap(hi)
    for _ in range(100):
        a=(lo+hi)/2
        if gap(a)>0:lo=a
        else:hi=a
    a=Q(lo.numerator*10**24//lo.denominator,10**24);assert gap(a)>0
    maximum=max(m-2*dmid,m-2*djoin,m-2*ddata)
    assert maximum==m-4*h and m**651>2*maximum**651
    assert c['W']<2**49 and Q(49*651)*(2+Q(1,25))<66000
    return dict(counts=c,kernel_dimensions=dict(middle=dmid,joined=djoin,data=ddata),
                family_ranks=ranks,middle_moment_lower=middle,joined_moment_lower=joined,
                data_moment_lower=data,explicit_saving=a,strict_characteristic_gap=gap(a),
                first_moment_upper=first,maximum_child=maximum,
                grouped_middle=m-2*dmid,grouped_joined=m-2*djoin,grouped_data=m-2*ddata,
                depth_bound_per_ceil_log2e=651,sufficient_row_degree=66000,
                sufficient_reservoir_linear_coefficient=264000,
                old_2600_row_degree_not_asserted=True)


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--seed',type=int,default=683)
    args=ap.parse_args();assert not args.output.exists();start=time.monotonic()
    finite=json.loads(args.finite_review.read_text())
    assert finite['status']=='PASS independent delayed first-consumer-frame clone finite witness'
    c=finite['full'];assert (c['h'],c['roles'])==(51,485680)
    counts=independent_counts(c['h'],c['roles'])
    assert all(c['exact_counts'][k]==counts[k] for k in ('W','m','v','N','L','D','s'))
    row=characteristic(c['h'],c['roles'])
    print('Exact generic-flag characteristic',row['explicit_saving'],flush=True)
    abstract,negative=abstract_controls(args.seed)
    print('Complete positive/indefinite small families PASS',flush=True)
    tensor=tensor_ground_controls(args.seed+10)
    print('Complete actual h5 joined/middle family PASS',flush=True)
    endpoint=dirty_endpoint_control(args.seed+20)
    print('Complete dirty source/gate/sink interface PASS',flush=True)
    names=('review_generic_metric_basis.py','review_reflected_basis.py',
           'review_pivot_batching.py','review_parameter_audit.py','review_pivot_extension.py',
           'review_axis_batching.py')
    result=dict(status='PASS independent finite-family rational reflections and complementary flags',
                generated_utc=datetime.now(timezone.utc).isoformat(),seed=args.seed,
                input_sha256={str(args.finite_review):sha256(args.finite_review.read_bytes()).hexdigest()},
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                finite_candidate_id=finite['candidate_id'],finite_compiled_sha256=c['compiled_sha256'],
                abstract_family_controls=abstract,actual_tensor_family_control=tensor,
                boundary_negatives=negative,dirty_common_frame_control=endpoint,row=row,
                all_h51_ambient_basis_instantiated=False,
                rational_finite_setup_existence='Explicit nonzero product on {0,...,D}^m; degree D<=2+4N and at most max kernel dimension reflections.',
                fixed_table_changed=True,new_runtime_adapter=False,
                scope='Constructive all-size finite-family theorem and complete exact small instantiations. No giant h51 isometry/table/common prime materialized; fixed setup and alphabet constants retain separate eventual qualifications.',
                wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],row['explicit_saving'],flush=True)


if __name__=='__main__':main()
