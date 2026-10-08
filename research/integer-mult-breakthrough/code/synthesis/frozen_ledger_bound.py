#!/usr/bin/env python3
"""Rigorous favorable bound for a frozen native ledger and full scalar sinks.

This derives a necessary condition from retained child distributions. It is
not an integer-multiplication theorem and does not constrain a changed data,
boundary, exterior or recurrence architecture.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from global_incidence import dirty_word, incidence_rows, side_rows
from run_discriminators import log_interval


@lru_cache(None)
def logs(t):
    return log_interval(Q(575, t))


def relaxed_rows(r23=0, r25=0):
    if r23 < 0 or r25 < 0:
        raise ValueError('Negative role count')
    a, b, m = 23, 25, 575
    n = comb(a, 3) * comb(b, 3)
    w = 2 * n + comb(b, 3) * r23 + comb(a, 3) * r25
    rows = Counter({1:19*n, 21:2*n, 17:2*n, 481:2*n})
    loss = 0
    for h, r, copies in [(a, r23, comb(b, 3)), (b, r25, comb(a, 3))]:
        # An arbitrary internal profile of mass hR+h(h-1), max child h,
        # has moment >= that of R+h-1 full-rank children for positive saving.
        rows[h] += copies * (2*r+h-1)
        rows[m-2*h] += copies*r
        rows[1] += 2*n
        rows[h-2] += 2*n
        loss += copies*h*(h-1)
    if sum(t*c for t,c in rows.items()) != m*w-n+loss:
        raise ValueError('Changed rank mass in relaxation')
    return m,w,rows


def bound_moment(saving, r23=0, r25=0):
    if not Q(0) <= saving <= Q(1, 500):
        raise ValueError('Saving outside enclosure range')
    m,w,rows = relaxed_rows(r23,r25)
    low,high = Q(),Q()
    for t,n in rows.items():
        lo,hi = logs(t)
        x,y = saving*lo,saving*hi
        weight = Q(t*n,m*w)
        low += weight*(1+x+x*x/2+x**3/6)
        high += weight*(1+y+y*y/(2*(1-y/3)))
    return low,high


def characteristic_bracket():
    scale=10**12
    lo,hi=0,2*10**9
    while hi-lo>1:
        mid=(lo+hi)//2
        lower,upper=bound_moment(Q(mid,scale))
        if upper<1:
            lo=mid
        elif lower>1:
            hi=mid
        else:
            raise ValueError('Moment enclosure cannot resolve bracket grid')
    lower_moment=bound_moment(Q(lo,scale))
    upper_moment=bound_moment(Q(hi,scale))
    if not lower_moment[1]<1<upper_moment[0]:
        raise ValueError('The strict bracket did not verify')
    return dict(binary_saving_lower=str(Q(lo,scale)), binary_saving_upper=str(Q(hi,scale)),
                lower_endpoint_moment_upper=str(lower_moment[1]),
                upper_endpoint_moment_lower=str(upper_moment[0]),
                conditional_kappa_ceiling=str(Q(hi,scale)/(1+Q(hi,scale))))


def full_scalar_center_replay(h, separate_sides):
    old=dirty_word(h,separate_sides)
    v=comb(h,3)
    sinks=3*v if separate_sides else v
    insert=v+sinks
    remap=lambda slot:slot+h if slot>=insert else slot
    old_word=[(remap(a),remap(b)) for a,b in old['cnot_word']]
    compute_len=(6 if separate_sides else 3)*v
    use_len=(9 if separate_sides else 3)*v
    additional_uses=[(insert+c,remap(insert+c)) for c in range(h)]
    first=compute_len+use_len
    second=2*compute_len+2*use_len
    word=(old_word[:first]+additional_uses+old_word[first:second]+
          additional_uses+old_word[second:])
    roles=old['roles']+h
    states=[1<<j for j in range(roles)]
    initial=list(states)
    for a,b in word:
        if a==b:
            raise ValueError('Invalid inserted center CNOT')
        states[a]^=states[b]
    _,sides,summed=side_rows(h)
    _,totals,_=incidence_rows(h)
    wanted=([r for _,r in sides] if separate_sides else summed)+totals
    for j,row in enumerate(wanted):
        if states[v+j]!=initial[v+j]^row:
            raise ValueError('Full center/source map mismatch')
    for j in list(range(v))+list(range(insert+h,roles)):
        if states[j]!=initial[j]:
            raise ValueError('Full-map source or dirty scratch not restored')
    count=(33 if separate_sides else 13)*v+2*h
    if len(word)!=count:
        raise ValueError('Center sink operations not paid')
    # Removing either center echo leaves independent dirty total coordinates.
    corrupted=list(word)
    del corrupted[first]
    trial=list(initial)
    for a,b in corrupted:
        trial[a]^=trial[b]
    if trial==states:
        raise ValueError('Missing center echo is not detected')
    return dict(h=h, separate_sides=separate_sides, roles=roles, paid_cnots=count,
                ordinary_sinks=sinks, center_sinks=h, independent_dirty_scratch=old['roles']-v-sinks,
                all_source_sink_dirty_columns_exact=True, missing_center_echo_rejected=True,
                scope='The separate-side case includes all ordinary sides and point totals in the historical scalar source/sink map. The summed case changes ordinary boundary outputs. Both remain auxiliary scalar CNOT certificates without physical framed words.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    sources=[Path(__file__),Path(__file__).with_name('global_incidence.py'),Path(__file__).with_name('run_discriminators.py')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=1,
                  random_seed=None,source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    result=dict(status='EXACT FROZEN-LEDGER CEILING AND FULL SCALAR CENTER MAP PASS',
                root_bracket=characteristic_bracket(),
                forbidden_binary_target=str(Q(1,999)),
                forbidden_target_lower_moment=str(bound_moment(Q(1,999))[0]),
                complete_center_maps=[full_scalar_center_replay(h,separate) for h in [6,7,23,25] for separate in [False,True]],
                root_scope='An exact favorable lower bound on the retained 23x25 native child ledger even when every bank role is relaxed to zero. For each positive saving, adding a role increases unnormalized moment-minus-capacity by a strictly positive coefficient. A changed data/boundary/exterior architecture is outside the bound.',
                proof_status='Rational interval certificate plus accompanying dimension-specific analytic proof; no formal verification',
                elapsed_seconds=time.monotonic()-start)
    if Q(result['forbidden_target_lower_moment'])<=1:
        raise ValueError('Claimed target exclusion was not proved')
    (args.output/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','root_bracket','elapsed_seconds']}),flush=True)


if __name__=='__main__':
    main()
