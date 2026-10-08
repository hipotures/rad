#!/usr/bin/env python3
"""Independent exact controls and minor bounds for L_h=I-4J/[3(h+3)].

The campaign's geometry worker discovered this family by entry-root search.
This review imports no native profiler, matching code, or supplier formula.
It derives projectors from Gram bases and compares them with a low-rank
expression, then bounds every membership category with integer arithmetic.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb, factorial
from pathlib import Path


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def transpose(a):
    return list(map(list, zip(*a)))


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def conjugate(p, h):
    t = Q(-4, 3*(h+3))
    left = [[Q(i == j)+t for j in range(h)] for i in range(h)]
    right = [[Q(i == j)-t/(1+h*t) for j in range(h)] for i in range(h)]
    assert mm(left, right) == eye(h)
    return mm(mm(left, p), right)


def envelope(h, core, outside):
    c, n = len(core), len(outside)
    s = 3-c
    basis = [[Q(i == j)+Q(i in core, s) for j in outside] for i in range(h)]
    gram = [[Q(i == j)+Q(c-1, s*s) for j in range(n)] for i in range(n)]
    inv = [[Q(i == j)-Q(c-1, s*s+(c-1)*n) for j in range(n)] for i in range(n)]
    g = [[Q(i == j)-Q(1, 9) for j in range(h)] for i in range(h)]
    assert mm(mm(transpose(basis), g), basis) == gram
    assert mm(gram, inv) == eye(n)
    actual = conjugate(mm(mm(mm(basis, inv), transpose(basis)), g), h)
    d = s*s+(c-1)*n
    formula = []
    for i in range(h):
        row = []
        for j in range(h):
            oi, oj = int(i in outside), int(j in outside)
            wi, zj = (h+3)*int(i in core)-4, int(j in core)+1
            z = s*(h+3)*oi*zj+s*wi*oj+n*wi*zj-(h+3)*(c-1)*oi*oj
            row.append(Q(i == j and oi)+Q(z, (h+3)*d))
        formula.append(row)
    assert actual == formula
    return dict(core=core, outside=outside, denominator=(h+3)*d,
                matrix_sha256=sha256(json.dumps(actual, default=str).encode()).hexdigest())


def source_and_centers(h):
    t = Q(-4, 3*(h+3))
    triple = {0, 1, 2}
    p = [Q(i in triple)-Q(4, h+3) for i in range(h)]
    nu = [Q(int(i in triple)+1, 2) for i in range(h)]
    assert all(p) and all(nu) and sum(x*y for x, y in zip(p, nu)) == 1
    original = [[Q(i in triple)*Q(3*int(j in triple)-1, 6) for j in range(h)] for i in range(h)]
    assert conjugate(original, h) == [[x*y for y in nu] for x in p]
    for center in range(h):
        pc = [Q(i == center)-Q(2, h+3) for i in range(h)]
        nc = [-Q(h-1, 4)-Q(h-9, 4)*int(i == center) for i in range(h)]
        assert all(pc) and all(nc) and sum(x*y for x, y in zip(pc, nc)) == 1
        po = [Q(i == center)+Q(2, h-9) for i in range(h)]
        no = [Q(h-9, 12)-Q(h-9, 4)*int(i == center) for i in range(h)]
        # Scalar Sherman-Morrison conjugation, separately from envelope code.
        assert pc == [x+t*sum(po) for x in po]
        assert nc == [x-t*sum(no)/(1+h*t) for x in no]
    return dict(t=str(t), source_coordinate_products={
        'inside': str(Q(h-1, h+3)), 'outside': str(Q(-2, h+3))},
        centers_checked=h, every_coordinate_nonzero=True)


def bounds(h):
    single = 0
    for c in (1, 2):
        s = 3-c
        for n in range(1, h-c+1):
            assert s*s+(c-1)*n <= h-1
            for ci, oi in ((1, 0), (0, 1), (0, 0)):
                for cj, oj in ((1, 0), (0, 1), (0, 0)):
                    wi, zj = (h+3)*ci-4, cj+1
                    z = s*(h+3)*oi*zj+s*wi*oj+n*wi*zj-(h+3)*(c-1)*oi*oj
                    single = max(single, abs(z))
    single = max(single, 2*(h-1))  # Source-line outer-product numerator.
    dmax = (h+3)*(h-1)**2
    bmax = 2*(h-1)*single
    minor = {r: sum(comb(h,j)*factorial(j)*bmax**j*dmax**(r-j)
                    for j in range(r+1)) for r in (2, 3, 4)}
    primes = [2**61-1, 2**31-1, 2**19-1]
    for exponent, p in zip((61, 31, 19), primes):
        x = 4
        for _ in range(exponent-2):
            x = (x*x-2) % p
        assert x == 0
    assert (h+3)*(h-1) < min(primes)
    assert minor[2] < primes[0] and minor[4] < primes[0]*primes[1]*primes[2]
    return dict(single_numerator_bound=single, common_denominator_upper=dmax,
                difference_numerator_bound=bmax, minor_numerator_bounds=minor,
                primes=primes, prime_product=primes[0]*primes[1]*primes[2],
                maximum_constituent_denominator=(h+3)*(h-1),
                crt_bound_pass=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    rows = []
    for h in (23, 25):
        controls = [envelope(h, list(range(c)), list(range(c, c+n)))
                    for c in (1, 2) for n in (1, 3)]
        rows.append(dict(h=h, bounds=bounds(h), source_and_centers=source_and_centers(h),
                         gram_projector_controls=controls))
    result = dict(status='PASS independent exact specialized basis and bounded-minor component',
                  rows=rows, source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  scope='General formula/CRT bound with bounded Gram controls. Actual full transition profiles, matching, complete source-pair nonvanishing and compiler checks remain separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps([dict(h=r['h'], maximum_minor_bits=r['bounds']['minor_numerator_bounds'][4].bit_length()) for r in rows]))


if __name__ == '__main__':
    main()
