#!/usr/bin/env python3
"""Independent exact-factor and dyadic packed-convolution Gaussian check.

This is a bounded functional experiment, not a Turing-machine runtime
benchmark. All algebra uses Fraction; transcendental comparison uses
mpmath==1.3.0. Signed input convolution is reduced to unsigned integer
products with guard bits, rather than trusting floating point FFTs.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import ceil, isqrt
from pathlib import Path
import time

import mpmath as mp


def round_ratio(n, d):
    """Nearest integer, ties upward, including negative numerators."""
    return (2*n+d)//(2*d)


def rational_mpf(x):
    return mp.mpf(x.numerator)/x.denominator


def packed_convolution(a, b, width):
    """Signed a times nonnegative b, through two unsigned products."""
    assert all(x >= 0 for x in b)
    mask = (1 << width)-1
    ap = sum(max(x, 0) << (width*i) for i, x in enumerate(a))
    an = sum(max(-x, 0) << (width*i) for i, x in enumerate(a))
    bp = sum(x << (width*i) for i, x in enumerate(b))
    plus, minus = ap*bp, an*bp
    return [((plus >> (width*i)) & mask)-((minus >> (width*i)) & mask)
            for i in range(len(a)+len(b)-1)]


def beta(j, s, t):
    x = Q(t*j, s)
    return x-round_ratio(x.numerator, x.denominator)


def factors(mode, s, t, alpha, k0):
    rho, kappa = Q(t, s), Q(s, t)
    j0 = (s*k0)//t
    if mode == 'S':
        gamma = Q(j0)-kappa*k0
        scale = Q(1, alpha*alpha)
        def u(h):
            return scale*((1-kappa)*h*h+2*gamma*h+gamma*gamma)
        def v(q):
            return scale*((kappa*kappa-kappa)*q*q-2*gamma*kappa*q)
        def kernel(d):
            return scale*kappa*d*d
        def full(h, q):
            return scale*(gamma+h-kappa*q)**2
    else:
        gamma = rho*j0-k0
        scale = Q(alpha*alpha)
        def u(h):
            z = scale*((rho*rho-rho)*h*h+2*gamma*rho*h+gamma*gamma)
            return z-scale*beta(j0+h, s, t)**2
        def v(q):
            return scale*((1-rho)*q*q-2*gamma*q)
        def kernel(d):
            return scale*rho*d*d
        def full(h, q):
            return scale*((gamma+rho*h-q)**2-beta(j0+h, s, t)**2)
    return j0, u, v, kernel, full


def one_block(mode, s, t, alpha, p, k0, x, audit_all=True):
    # Integer upper square-root keeps the experiment's windows deterministic.
    sqrtp = isqrt(p)+(isqrt(p)**2 < p)
    B = sqrtp*alpha if mode == 'S' else max(1, ceil(Q(sqrtp, alpha)))
    count = min(B, t-k0)
    radius = sqrtp*alpha+2 if mode == 'S' else ceil(Q(sqrtp, alpha))+2
    j0, u, v, kernel, full = factors(mode, s, t, alpha, k0)
    lo = -radius
    hi = ceil(Q(s*(count-1), t))+radius+1
    input_h = list(range(lo, hi+1))
    output_v = list(range(count))
    for h in input_h:
        for q in output_v:
            assert u(h)+v(q)+kernel(h-q) == full(h, q)
    assert all(kernel(d) >= 0 for d in range(-hi, count-lo))
    max_growth = max([Q(0)]+[-u(h) for h in input_h]+[-v(q) for q in output_v])
    # pi<4 and log(2)>1/2, so this dominates all dyadic growth exponents.
    sigma = ceil(8*max_growth)+8
    length = len(input_h)
    guard = (length-1).bit_length()+3
    P = 2*sigma+p+8*(length-1).bit_length()+48
    mp.mp.prec = P+128
    scaleP = mp.mpf(2)**P
    def quantize(exponent, normalize=False):
        z = -mp.pi*rational_mpf(exponent)
        if normalize:
            z -= sigma*mp.log(2)
        return int(mp.floor(mp.exp(z)*scaleP+mp.mpf('0.5')))
    uq = [quantize(u(h), True) for h in input_h]
    vq = [quantize(v(q), True) for q in output_v]
    kq = [quantize(kernel(d)) for d in range(-hi, count-lo)]
    assert max(uq+vq+kq) <= 1 << P
    ar = [round_ratio(z*x[(j0+h)%s][0], 1 << p) for z, h in zip(uq, input_h)]
    ai = [round_ratio(z*x[(j0+h)%s][1], 1 << p) for z, h in zip(uq, input_h)]
    width = 2*P+guard
    cr = packed_convolution(ar, kq, width)
    ci = packed_convolution(ai, kq, width)
    if audit_all:
        for q in output_v:
            index = q+hi-lo
            assert cr[index] == sum(ar[i]*kq[q+hi-lo-i] for i in range(length))
            assert ci[index] == sum(ai[i]*kq[q+hi-lo-i] for i in range(length))
    denominator = (1 << (3*P-2*sigma-p))*(2*alpha if mode == 'S' else 1)
    computed = [(round_ratio(cr[q+hi-lo]*vq[q], denominator),
                 round_ratio(ci[q+hi-lo]*vq[q], denominator)) for q in output_v]
    worst = mp.mpf(0)
    direct_round_disagreement = 0
    for q, (yr, yi) in zip(output_v, computed):
        target = sum(mp.exp(-mp.pi*rational_mpf(full(h, q)))*
                     mp.mpc(*x[(j0+h)%s])
                     for h in input_h)
        if mode == 'S':
            target /= 2*alpha
        error = abs(mp.mpc(yr, yi)-target)
        worst = max(worst, error)
        expected = (int(mp.floor(target.real+mp.mpf('0.5'))),
                    int(mp.floor(target.imag+mp.mpf('0.5'))))
        direct_round_disagreement += expected != (yr, yi)
    # T mode applies T D. Subtract original input at selected q_j for N-I.
    selected = []
    if mode != 'S':
        for j in range(s):
            k = round_ratio(t*j, s)
            if k0 <= k < k0+count:
                yr, yi = computed[k-k0]
                selected.append((j, yr-x[j][0], yi-x[j][1]))
    packed_bits = width*max(len(ar), len(kq))
    return dict(mode=mode, output_start=k0, output_count=count,
                input_window_count=length, block_size=B, radius=radius,
                normalized_diagonals=2, kernel_normalized=False,
                sigma=sigma, work_precision=P, packed_operand_bits=packed_bits,
                factor_identities_checked=length*count,
                periodic_input_indices_used=any(not 0 <= j0+h < s for h in input_h),
                exact_signed_convolution_checked=audit_all,
                direct_rounded_disagreements=direct_round_disagreement,
                maximum_scaled_truncated_error=mp.nstr(worst, 12),
                selected_E_values=selected,
                output_digest=sha256(json.dumps(computed).encode()).hexdigest())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--p', type=int, default=128)
    ap.add_argument('--s', type=int, default=127)
    ap.add_argument('--t', type=int, default=151)
    ap.add_argument('--alphas', type=int, nargs='+', default=[2, 10])
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    assert 1 < Q(args.t, args.s) < 2
    begin = time.monotonic()
    unit = 1 << args.p
    # Signed real and imaginary inputs with unit-disk norm and cancellation.
    x = [(unit//2*(-1 if j%2 else 1), unit//2*(-1 if j%3 else 1))
         for j in range(args.s)]
    records = []
    for a in args.alphas:
        assert 2 <= a and a*a < args.p
        sqrtp = isqrt(args.p)+(isqrt(args.p)**2 < args.p)
        for mode in ['S', 'TD']:
            B = sqrtp*a if mode == 'S' else max(1, ceil(Q(sqrtp, a)))
            starts = sorted(set([0, min(B, args.t-1), ((args.t-1)//B)*B]))
            for k0 in starts:
                row = one_block(mode, args.s, args.t, a, args.p, k0, x)
                row['alpha'] = a
                records.append(row)
    result = dict(s=args.s, t=args.t, p=args.p, input_pattern='signed half-unit real/imaginary',
                  work_precision_rule='2 sigma+p+8 ceil(log2 input-window)+48',
                  records=records, wall_seconds=time.monotonic()-begin,
                  scope='Bounded algebra, signed integer convolution, periodic indexing, and rounding check; no asymptotic runtime measurement or general theorem.')
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
