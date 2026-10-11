#!/usr/bin/env python3
"""Independent exact moment checks of supplied PR118/PR120 complex histograms.

No producer, frame, signed-word or all-size theorem is verified here. Inputs are
explicit transcriptions of the pinned source JSON files, not network-derived
certificates. Uses only the Python standard library; no network or shell calls.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from pathlib import Path
from math import factorial
import hashlib
import json

BASE = Path(__file__).resolve().parent
DEN = 2**180
SOURCES = {
    'pr118': ('https://github.com/rohanarun/integer-mult-bounds/blob/'
              'ec862a5af51537495c745d9f2323e8a5736ee265/'
              'research/deferred-replayed-117/complex-profile.json', Q(108566486,10**12)),
    'pr120': ('https://github.com/eumemic/integer-mult-bounds/blob/'
              'bfc5466b028923a1f8655602994ea56c70b5c329/'
              'research/deferred-replayed/complex-profile.json', Q(109140237,10**12)),
}

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def down(x: Q) -> Q:
    return Q((x.numerator*DEN)//x.denominator, DEN)

def up(x: Q) -> Q:
    return Q(-((-x.numerator*DEN)//x.denominator), DEN)

def log_unit(x: Q) -> tuple[Q,Q]:
    require(1 <= x <= 2, 'Logarithm range reduction failed')
    z=(x-1)/(x+1)
    lower=sum((2*z**(2*k+1)/Q(2*k+1) for k in range(40)),Q(0))
    # All omitted terms are nonnegative; every omitted denominator is >=81.
    tail=2*z**81/(81*(1-z*z))
    return down(lower), up(lower+tail)

def log_bounds(x: Q) -> tuple[Q,Q]:
    require(x >= 1, 'Logarithm argument below one')
    k=0
    while x>2:
        x/=2;k+=1
    lo,hi=log_unit(x);l2,h2=log_unit(Q(2))
    return down(lo+k*l2), up(hi+k*h2)

def exp_bounds(lo: Q, hi: Q) -> tuple[Q,Q]:
    require(0 <= lo <= hi < 1, 'Exponential remainder assumptions fail')
    lower=sum((lo**k/Q(factorial(k)) for k in range(10)),Q(0))
    upper=sum((hi**k/Q(factorial(k)) for k in range(10)),Q(0))
    # Starting at degree 10, successive ratios are at most hi/11.
    tail=(hi**10/Q(factorial(10)))/(1-hi/11)
    return down(lower), up(upper+tail)

def check(name: str, url: str, saving: Q) -> dict:
    path=BASE/'sources'/f'{name}-profile-transcription.json'
    raw=path.read_bytes();p=json.loads(raw)
    m,W,N,L,rank=(p[k] for k in ('m','W','N','L','total_rank'))
    hist={int(t):c for t,c in p['child_multiplicities'].items()}
    require(all(type(c) is int and c>0 and 0<t<m for t,c in hist.items()), 'Invalid child')
    require(sum(t*c for t,c in hist.items())==rank==m*W-N+L, 'Rank conservation failed')
    logs={t:log_bounds(Q(m,t)) for t in hist}
    def moment(s: Q) -> tuple[Q,Q]:
        lower=upper=Q(0)
        for t,count in hist.items():
            l,h=logs[t];el,eh=exp_bounds(s*l,s*h);weight=Q(t*count,m*W)
            lower+=weight*el;upper+=weight*eh
        return down(lower),up(upper)
    lo,hi=moment(saving);nextlo,nexthi=moment(saving+Q(1,10**12))
    require(hi<1 and nextlo>1, f'{name}: acceptance or next-grid exclusion failed')
    return dict(source=url,input_sha256=hashlib.sha256(raw).hexdigest(),
                m=m,W=W,rank=rank,deficit=m*W-rank,maxchild=max(hist),
                saving=str(saving),moment_lower=str(lo),moment_upper=str(hi),
                gap_lower=str(1-hi),gap_decimal=float(1-hi),
                next_saving=str(saving+Q(1,10**12)),next_lower=str(nextlo),
                next_excess_lower=str(nextlo-1),next_excess_decimal=float(nextlo-1))

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,help='Optional NEW output file; existing evidence is never overwritten')
    args=ap.parse_args()
    results={name:check(name,*pair) for name,pair in SOURCES.items()}
    bit=Q(1240189553,10**13);k118=Q(6783925373,62500000000000);k120=Q(1363953833,12500000000000)
    b120=SOURCES['pr120'][1]
    report=dict(scope='Supplied histogram arithmetic only. No graph/frame/whole-word/all-size validation.',
                method='40-term range-reduced rational atanh; degree-9 exponential Taylor with geometric tail; outward dyadic 2^-180.',
                profiles=results,
                comparisons=dict(ordinary_bit_saving=str(bit),frozen_bit_optimistic_cap=str(bit/(1+bit)),
                   top_120_over_118_percent=float(100*(k120/k118-1)),
                   top_120_over_117_percent=float(100*(k120/Q(1044939,10**10)-1)),
                   top_120_over_reviewed_main_percent=float(100*(k120/Q(25508460085039,5*10**17)-1)),
                   kappa_headroom_from_120_percent=float(100*(bit/(1+bit)/k120-1)),
                   complex_to_kappa_120_gap_percent=float(100*(b120/k120-1)),
                   required_a_for_2e4=str(Q(1,4999)),
                   required_bit_gain_percent=float(100*(Q(1,4999)/bit-1)),
                   required_b_for_2e4_beta1e6=str(Q(1,4999)/(1-Q(1,10**6))),
                   required_complex_gain_percent=float(100*((Q(1,4999)/(1-Q(1,10**6)))/b120-1))))
    text=json.dumps(report,indent=2)+'\n'
    if args.output:
        with args.output.open('x',encoding='utf-8') as f:f.write(text)
    print(text,end='')

if __name__=='__main__':
    main()
