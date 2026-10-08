#!/usr/bin/env python3
"""Independent edge cases for complementary flags and finite-prime setup."""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import resource
import sys
import time

from review_generic_metric_basis import (complementary_profile, dual,
    minus_identity_product, matrix_vector, row_vector)
from review_pivot_batching import exact_factor, identity, multiply, stringify, transpose
from review_reflected_basis import scalar_field_matrix


def varied_orders():
    cases=[];increasing=reverse=0
    for d in range(1,5):
        n=2*d+2
        for p in permutations(range(d)):
            U=[]
            for i in range(n):
                if i<d:U.append([Q(int(i==j)) for j in range(d)])
                elif i<n-d:U.append([Q(0)]*d)
                else:U.append([Q(int(p[i-(n-d)]==j)) for j in range(d)])
            G=identity(n)
            if p[0]%2:G[d][d]=Q(-1)
            V=dual(G,U);record=complementary_profile(U,V)
            A=minus_identity_product(U,V);profile,L,R=exact_factor(A)
            assert profile[:d]==[(i,n-d+p.index(i)) for i in range(d)]
            assert multiply(multiply(L,A),R)==[
                [Q(int((i,j) in profile)) for j in range(n)] for i in range(n)]
            targets=[j for _,j in profile[:d]]
            if targets==sorted(targets):increasing+=1
            if targets==sorted(targets,reverse=True):reverse+=1
            record['bottom_permutation']=list(p)
            record['exact_lower_lower_factors']=True
            cases.append(record)
    assert increasing and reverse and increasing<len(cases) and reverse<len(cases)
    return dict(cases=cases,increasing_top_orders=increasing,decreasing_top_orders=reverse,
                offdiagonal_order_not_assumed=True)


def singular_metric_negative():
    G=identity(3);G[2][2]=Q(0);U=[[Q(int(i==0))] for i in range(3)]
    V=dual(G,U);assert V==[[Q(1),Q(0),Q(0)]]
    controls=0
    for w in product(range(-2,3),repeat=3):
        w=list(map(Q,w));wg=row_vector(w,G);norm=sum(a*b for a,b in zip(w,wg))
        if not norm:continue
        vw=matrix_vector(V,w)
        V1=[[a-2*vw[i]*wg[j]/norm for j,a in enumerate(row)] for i,row in enumerate(V)]
        assert V1[0][-1]==0;controls+=1
    assert controls
    # The last column of every such dual is identically zero because
    # the last column of G is zero, so no desired back flag can exist.
    return dict(reflections_checked=controls,back_flag_always_zero=True,
                ambient_nondegeneracy_essential=True)


def characteristic_two_negative():
    U=[0,1,0];checked=0
    for w in product(range(2),repeat=3):
        norm=sum(x*x for x in w)%2
        if not norm:continue
        R=[[((int(i==j)-2*w[i]*w[j]*pow(norm,-1,2))%2)
            for j in range(3)] for i in range(3)]
        assert R==[[int(i==j) for j in range(3)] for i in range(3)]
        assert [sum(a*b for a,b in zip(row,U))%2 for row in R]==U
        checked+=1
    assert checked
    return dict(nonisotropic_directions_checked=checked,every_reflection_identity=True,
                both_required_flags_stay_zero=True,no_native_binary_extension_claim=True)


def odd_prime_negative():
    U=[[Q(1),Q(0)],[Q(0),Q(1)],[Q(0),Q(0)],[Q(2),Q(0)],[Q(0),Q(3)]]
    V=dual(identity(5),U);A=minus_identity_product(U,V)
    profile,L,R=exact_factor(A)
    assert profile==[(0,3),(1,4),(2,2)]
    assert all(x.denominator%3 for row in A for x in row)
    bad=scalar_field_matrix(A,3)
    bad_profile=[]
    for i,row in enumerate(bad):
        js=[j for j,x in enumerate(row) if x%3]
        if not js:continue
        j=max(js);bad_profile.append((i,j))
        for k in range(i+1,5):
            c=bad[k][j]*pow(row[j],-1,3)%3
            bad[k]=[(a-c*b)%3 for a,b in zip(bad[k],row)]
    assert len(bad_profile)==len(profile) and bad_profile!=profile
    assert any(x.denominator%3==0 for B in (L,R) for row in B for x in row)
    q=7;Lq,Aq,Rq=[scalar_field_matrix(B,q) for B in (L,A,R)]
    product0=multiply(multiply(Lq,Aq),Rq)
    assert [[int(x)%q for x in row] for row in product0]==[
        [int((i,j) in profile) for j in range(5)] for i in range(5)]
    return dict(rational_profile=profile,bad_prime=3,bad_prime_profile=bad_profile,
                rank_retained_at_bad_prime=True,matrix_entry_denominators_all_units_at_bad_prime=True,
                triangular_denominator_not_unit_at_bad_prime=True,good_prime=7,
                full_lower_factor_identity_mod_good_prime=True,
                factor_prime_exclusion_essential=True)


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--generic-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();start=time.monotonic()
    old=json.loads(args.generic_review.read_text())
    assert old['status']=='PASS independent finite-family rational reflections and complementary flags'
    for name,digest in old['source_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    names=('review_generic_flag_boundaries.py','review_generic_metric_basis.py',
           'review_pivot_batching.py','review_reflected_basis.py')
    result=dict(status='PASS independent generic flag boundary controls',
                generated_utc=datetime.now(timezone.utc).isoformat(),
                input_sha256={str(args.generic_review):sha256(args.generic_review.read_bytes()).hexdigest()},
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                arbitrary_top_pivot_order=varied_orders(),
                singular_metric_negative=singular_metric_negative(),
                characteristic_two_negative=characteristic_two_negative(),
                bad_odd_prime_negative=odd_prime_negative(),
                old_generic_primitive_saving=old['row']['explicit_saving'],
                scope='Boundary controls only; no new primitive, graph, table, final assembly or generic all-h51 basis instantiation.',
                wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],len(result['arbitrary_top_pivot_order']['cases']),flush=True)


if __name__=='__main__':main()
