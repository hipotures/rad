#!/usr/bin/env python3
"""Rebuild the complete PR36 complex moment, with exact outward bounds.

Finite characteristic arithmetic only. This does not verify the scalar DAG,
phase implementation, physical tape interface or an all-size exponent.
The distribution is transcribed from icekylinx's PR36 copied-center notes
at 11817ccacb564bb7f98789c20dc11d3fece207e3 (Apache-2.0), using its
original carrier histogram. OpenAI Codex assisted this independent checker.
"""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def copied_histogram(row):
    h, R, hist = row['h'], row['R'], row['histogram']
    require(row['v'] == comb(h, 3), 'incorrect triple count')
    require(h % 2 == 0 and len(hist) == h+1, 'invalid dimension/histogram')
    require(all(type(n) is int and n >= 0 for n in hist), 'invalid multiplicity')
    loss = h*(h-1)
    require(row['loss'] == loss, 'incorrect selected center loss')
    require(sum(r*n for r, n in enumerate(hist)) == h*R+2*loss,
            'original local rank mass mismatch')
    require(hist[h] >= h, 'missing retained-center cleanup')
    copied = list(hist)
    copied[1] += h
    copied[h] -= h
    require(sum(r*n for r, n in enumerate(copied)) == h*R+loss,
            'copied local rank mass mismatch')
    return copied


def profile(row):
    h, v, R, loss = (row[k] for k in ('h', 'v', 'R', 'loss'))
    hist = copied_histogram(row)
    m, N, B = h*h, v*v, v*R
    W, L = 2*N+2*B, 2*v*loss
    children = Counter({m-h:2*B, (h-1)**2:2*N})
    for r, n in enumerate(hist):
        if r and n:
            children[r] += 2*v*n
    children[h-1] += 4*N
    children[1] += N
    s = sum(t*n for t,n in children.items())
    require(all(0 < t < m and n > 0 for t,n in children.items()), 'invalid child')
    require(s == W*m-N+L, 'complete rank accounting mismatch')
    return dict(m=m, N=N, B=B, W=W, L=L, total_rank=s, deficit=N-L,
                maxchild=max(children), child_multiplicities=dict(sorted(children.items())))


def log_interval(x, terms=48):
    require(x >= 1 and isinstance(x, Q), 'log argument must be rational >=1')
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def small(y):
        z = (y-1)/(y+1)
        lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
        tail = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
        return lo, lo+tail

    l2,u2 = small(Q(2))
    lx,ux = small(x)
    return k*l2+lx, k*u2+ux


def exp_interval(lo, hi, terms=12):
    require(0 <= lo <= hi, 'exp interval must be nonnegative')
    fact = 1
    low, high = Q(1), Q(1)
    for j in range(1,terms+1):
        fact *= j
        low += lo**j/fact
        high += hi**j/fact
    ratio = hi/Q(terms+2)
    require(ratio < 1, 'invalid exponential tail ratio')
    first_tail = hi**(terms+1)/(fact*(terms+1))
    return low, high+first_tail/(1-ratio)


def moment_interval(p, saving, terms=48):
    lo, hi = Q(0), Q(0)
    m,W = p['m'], p['W']
    for t,n in p['child_multiplicities'].items():
        l,u = log_interval(Q(m,int(t)), terms)
        el,eu = exp_interval(saving*l,saving*u)
        weight = Q(n*int(t),W*m)
        lo += weight*el
        hi += weight*eu
    # Round only outward, to keep retained certificates compact. Internal
    # rational sums are exact; this grid contributes <2^-192 per endpoint.
    grid=1<<192
    return Q(lo.numerator*grid//lo.denominator,grid), Q(
        -(-hi.numerator*grid//hi.denominator),grid)


def decimal_moment(p, saving):
    m,W = Decimal(p['m']),Decimal(p['W'])
    return sum((Decimal(n)*Decimal(t)/m/W *
                (saving*(m/Decimal(t)).ln()).exp()
                for t,n in p['child_multiplicities'].items()), Decimal(0))


def numerical_root(p):
    with localcontext() as ctx:
        ctx.prec = 60
        lo, hi = Decimal(0), Decimal('0.01')
        for _ in range(160):
            mid = (lo+hi)/2
            if decimal_moment(p,mid) < 1:
                lo = mid
            else:
                hi = mid
        return str((lo+hi)/2)


def rational_root_bracket(p, digits=12):
    scale=10**digits
    estimate = Q(numerical_root(p))
    low = estimate.numerator*scale//estimate.denominator
    lo,hi = Q(low,scale),Q(low+1,scale)
    il = moment_interval(p,lo)
    ih = moment_interval(p,hi)
    require(il[1] < 1 and ih[0] > 1, 'root bracket not rigorously separated')
    return dict(lower=lo, upper=hi, lower_moment_upper=il[1],
                upper_moment_lower=ih[0])


def serializable(value):
    if isinstance(value,Q):
        return str(value)
    if isinstance(value,dict):
        return {str(k):serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [serializable(v) for v in value]
    return value


def result(row, input_path):
    p=profile(row)
    saving=Q(717,10**7)
    target=Q(20,189981)
    saved = moment_interval(p,saving)
    needed = moment_interval(p,target)
    bracket=rational_root_bracket(p)
    require(saved[1]<1, 'published saving failed exact replay')
    require(needed[0]>1, 'frozen profile is not excluded at target')
    return dict(scope='Exact finite characteristic arithmetic; no physical or asymptotic claim',
                upstream_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',
                input_sha256=sha256(Path(input_path).read_bytes()).hexdigest(),
                profile=p,saved_saving=saving,saved_moment_interval=saved,
                required_saving=target,required_moment_interval=needed,
                actual_root_bracket=bracket,
                slack_ratio_upper=(bracket['upper']-saving)/saving,
                needed_component_gain_lower=target/bracket['upper']-1,
                root_to_balanced_kappa_ceiling=Q(19,20)*bracket['upper']/
                    (1+Q(19,20)*bracket['upper']))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    require(not args.output.exists(), 'output must be new')
    row=json.loads(args.input.read_text())
    answer=result(row,args.input)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(serializable(answer),indent=2)+'\n')
    print('Exact frozen root bracket:',answer['actual_root_bracket']['lower'],
          answer['actual_root_bracket']['upper'])
    print('Published saving replays; target saving is rigorously excluded.')


if __name__=='__main__':
    main()
