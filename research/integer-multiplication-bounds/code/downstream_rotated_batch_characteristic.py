#!/usr/bin/env python3
"""Exact prospective characteristics after one global (3,1,2) basis choice.

All finite matrices are conjugated before their fixed Bruhat tables are
chosen. No per-edge physical pivot gather is assumed. Three-family rows
are separate optional hypotheses until their tensor factor proof passes.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import log_integer_bounds,network_counts
from downstream_parameter_optimum import as_strings,rational_decimal_lower


@cache
def log_bounds(n):
    """Outward exact dyadic rounding keeps the many-term sum manageable."""
    lo,hi=log_integer_bounds(n);scale=2**256
    lower=Q(lo.numerator*scale//lo.denominator,scale)
    upper=Q(-((-hi.numerator*scale)//hi.denominator),scale)
    assert lower<=lo<=hi<=upper
    return lower,upper


def rotated(h,roles,variant):
    n=network_counts(h,roles);m=n['m'];v=n['v']
    copies=(roles+h)*v*v
    middle_rank=copies*h*h*(h-1)
    joined_rank=copies*(m-2*h)
    assert middle_rank+joined_rank<n['s']
    middle_log_sum=middle_rank*log_bounds(h*h)[0]
    t=m-4*h;g=4*h+1
    joined_log_sum=copies*t*(log_bounds(t)[0]-log_bounds(g)[1])
    assert t>g>0 and joined_log_sum>0
    data_rank=data_log_sum=0
    data_description='Excluded'
    data_histogram={}
    if variant in ('universal-data','tensor-data'):
        r=(h*h-1)*(h-1);data_rank=2*n['N']*r
        assert middle_rank+joined_rank+data_rank<n['s']
        if variant=='universal-data':
            d=m-r;td=m-2*d;gd=2*d+1
            assert td>gd
            data_log_sum=2*n['N']*td*(log_bounds(td)[0]-log_bounds(gd)[1])
            data_description='Universal diagonal-run bound; kernel F tensor protected-line12 gives h^2-spaced holes'
        else:
            # Pi_3 tensor Pi_12. Each of h-1 outer pivots repeats the
            # exact rank-one-complement profile of ambient h^2.
            factor=2*v*(h-1)
            for a in range(h-2):
                for b in range(h-2):
                    k=h*a+b;frequency=factor*comb(h-a-1,2)*comb(h-b-1,2)
                    for length in (k,h*h-k-2,1):
                        if length:
                            data_histogram[length]=data_histogram.get(length,0)+frequency
            assert sum(r*c for r,c in data_histogram.items())==data_rank
            assert max(data_histogram)<=h*h-2
            data_log_sum=sum((count*r*log_bounds(r)[0] for r,count in data_histogram.items()),Q(0))
            data_description='Exact Pi_3 tensor Pi_12 contiguous increasing source/target blocks; every other pivot unchanged'
    else:
        assert variant=='two-family'
    lm=log_bounds(m)[1]
    linear=n['W']*m*lm-middle_log_sum-joined_log_sum-data_log_sum
    quadratic=Q(n['s'],2)*lm*lm
    assert linear>0 and quadratic>0
    gap=lambda a:n['D']-a*linear-a*a*quadratic
    lo,hi=Q(0),Q(1,10000000)
    assert gap(lo)>0 and gap(hi)<0
    for _ in range(96):
        mid=(lo+hi)/2
        if gap(mid)>0:lo=mid
        else:hi=mid
    saving=Q(lo.numerator*10**24//lo.denominator,10**24)
    assert saving>0 and gap(saving)>0
    return dict(variant=variant,h=h,roles=roles,counts=n,
        compiler_basis_order=[3,1,2],middle_old_rank=middle_rank,joined_old_rank=joined_rank,
        data_old_rank=data_rank,other_unchanged_rank=n['s']-middle_rank-joined_rank-data_rank,
        middle_child_rank=h*h,middle_batch_calls=copies*(h-1),middle_rank_log_sum_lower=middle_log_sum,
        joined_rank_log_sum_lower=joined_log_sum,joined_run_bound=g,
        joined_minimum_diagonal=t,joined_maximum_diagonal_run=h*h-1,
        data_rank_log_sum_lower=data_log_sum,data_description=data_description,
        data_batch_histogram={str(r):c for r,c in sorted(data_histogram.items())},
        maximum_child_rank=h*h,child_ratio=Q(1,h),row_depth='ceil(log_h e)',
        taylor_linear_coefficient=linear,taylor_quadratic_coefficient=quadratic,
        saving=saving,saving_decimal_lower=rational_decimal_lower(saving,18),
        strict_taylor_gap=gap(saving),root_bracket=[lo,hi],
        exact_log_method='24-term integer logarithm intervals, outward dyadic256-bit rounding',
        above_two_power_minus_27=saving>Q(1,2**27))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h',type=int,required=True);ap.add_argument('--roles',type=int,required=True)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists(),'Use a fresh output path'
    review=json.loads(a.finite_review.read_text())
    assert review['status']=='PASS' and review['full']['h']==a.h
    assert review['full'].get('compiled_roles',review['full'].get('roles'))==a.roles
    started=time.monotonic();rows=[rotated(a.h,a.roles,v) for v in ('two-family','universal-data','tensor-data')]
    result=dict(status='PASS PROSPECTIVE GLOBAL-AXIS ROTATED CHARACTERISTICS',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        finite_input=dict(path=str(a.finite_review),sha256=sha256(a.finite_review.read_bytes()).hexdigest()),
        witnesses=rows,elapsed_seconds=time.monotonic()-started,
        scope='Global fixed matrix-basis conjugation and independent all-size grouped/tensor factor transfer require review; no arbitrary physical gather, finite role change or complex guard change is assumed')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    for row in rows:print(result['status'],row['variant'],row['saving'],row['saving_decimal_lower'],flush=True)


if __name__=='__main__':main()
