#!/usr/bin/env python3
"""Exact independent Fourier/product check for equal main axes, one wide suffix.

The formal phase zeta satisfies zeta^r=-1. Ring coefficients are rational
polynomials in zeta, so twists and wrap signs are checked without floating point.
These are arithmetic/interface controls; arbitrary line gathers in this checker
are not asserted to be free fixed-tape operations.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path
from random import Random
from time import perf_counter


def add(a, b, scale=Fraction(1)):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, Fraction())+scale*value
        if not out[key]:
            del out[key]
    return out


def multiply_monomial(a, power, r):
    out = {}
    for (y, z), value in a.items():
        q, new_y = divmod(y+power, r)
        key = (new_y, z)
        out[key] = out.get(key, Fraction())+((-1)**q)*value
    return {k:v for k,v in out.items() if v}


def scale(a, numerator, denominator=1):
    return {k:v*Fraction(numerator, denominator) for k,v in a.items() if v}


def product(a, b, r):
    out = {}
    for (y, z), value in a.items():
        for (v, w), other in b.items():
            yq, yn = divmod(y+v, r)
            zq, zn = divmod(z+w, r)
            key = (yn, zn)
            out[key] = out.get(key, Fraction())+value*other*((-1)**(yq+zq))
    return {k:v for k,v in out.items() if v}


def forward(line, r):
    n = len(line)
    if n == 1:
        return line
    first = []
    second = []
    for k in range(n//2):
        first.append(scale(add(line[k], line[k+n//2]), 1, 2))
        second.append(multiply_monomial(scale(add(line[k], line[k+n//2], -1), 1, 2),
                                         -(2*r//n)*k, r))
    return forward(first, r)+forward(second, r)


def backward(line, r):
    n = len(line)
    if n == 1:
        return line
    first = backward(line[:n//2], r)
    second = backward(line[n//2:], r)
    left = []
    right = []
    for k in range(n//2):
        twisted = multiply_monomial(second[k], (2*r//n)*k, r)
        left.append(scale(add(first[k], twisted), 1, 2))
        right.append(scale(add(first[k], twisted, -1), 1, 2))
    return left+right


def named_addresses(shape):
    return list(itertools.product(*(range(t) for t in shape)))


def axis_pass(data, shape, axis, r, inverse=False):
    output = dict(data)
    spectator_shape = shape[:axis]+shape[axis+1:]
    for spectators in itertools.product(*(range(t) for t in spectator_shape)):
        keys = [spectators[:axis]+(j,)+spectators[axis:] for j in range(shape[axis])]
        transformed = (backward if inverse else forward)([data[k] for k in keys], r)
        for key, value in zip(keys, transformed):
            output[key] = value
    return output


def twist(scalar, main_shape, r):
    return {address: {(k, k):scalar.get(address+(k,), Fraction())
                      for k in range(r) if scalar.get(address+(k,), Fraction())}
            for address in named_addresses(main_shape)}


def direct_cyclic(f, g, shape):
    out = {address:Fraction() for address in named_addresses(shape)}
    volume = math.prod(shape)
    for a, x in f.items():
        for b, y in g.items():
            target = tuple((u+v)%t for u,v,t in zip(a,b,shape))
            out[target] += x*y/volume
    return out


def check_case(case):
    ell, h, dimension, seed = case
    started = perf_counter()
    rng = Random(seed)
    t = 2**ell
    r = 2**(ell+h)
    main = (t,)*(dimension-1)
    shape = main+(r,)
    addresses = named_addresses(shape)
    sparse = min(5, len(addresses))
    f = {a:Fraction(rng.randrange(-4, 5), 8) for a in rng.sample(addresses, sparse)}
    g = {a:Fraction(rng.randrange(-4, 5), 8) for a in rng.sample(addresses, sparse)}
    # Explicit end/suffix terms force a last-axis cyclic wrap and test r/t>2.
    f[(0,)*(dimension-1)+(r-1,)] = Fraction(1, 4)
    g[(0,)*(dimension-1)+(1,)] = Fraction(1, 8)
    tf = twist(f, main, r)
    tg = twist(g, main, r)
    for axis in range(dimension-1):
        tf = axis_pass(tf, main, axis, r)
        tg = axis_pass(tg, main, axis, r)
    # Independent direct character formula checks frequency significance.
    direct_entries = 0
    for frequency in named_addresses(main):
        expected = {}
        for source, value in twist(f, main, r).items():
            power = -sum((2*r//t)*a*b for a,b in zip(frequency,source))
            expected = add(expected, multiply_monomial(value, power, r))
        expected = scale(expected, 1, math.prod(main))
        stored = tuple(int(f"{j:0{ell}b}"[::-1], 2) for j in frequency)
        assert tf[stored] == expected
        direct_entries += len(expected)
    multiplied = {a:scale(product(tf[a], tg[a], r), 1, r) for a in named_addresses(main)}
    for axis in reversed(range(dimension-1)):
        multiplied = axis_pass(multiplied, main, axis, r, inverse=True)
    multiplied = {a:scale(value, math.prod(main)) for a,value in multiplied.items()}
    expected_scalar = direct_cyclic(f, g, shape)
    expected_ring = twist(expected_scalar, main, r)
    assert multiplied == expected_ring
    # Untwisting removes zeta^k from exactly the coefficient at y^k.
    actual_scalar = {a+(k,):value.get((k,k), Fraction())
                     for a,value in multiplied.items() for k in range(r)}
    assert actual_scalar == expected_scalar
    assert all(y == z for value in multiplied.values() for y,z in value)
    # Direct character cancellation, including roots whose exponent exceeds2.
    for frequency in range(1, t):
        total = {}
        for j in range(t):
            total = add(total, multiply_monomial({(0,0):Fraction(1)}, (2*r//t)*j*frequency, r))
        assert not total
    # Omitting the coefficient twist turns this explicit cyclic wrap negative.
    negative = product({(r-1,0):Fraction(1)}, {(1,0):Fraction(1)}, r)
    assert negative == {(0,0):Fraction(-1)}
    return {"ell": ell, "h": h, "dimension": dimension,
            "main_axis": t, "polynomial_axis": r, "root_step": 2*r//t,
            "scalar_records": len(addresses), "formal_fourier_terms_checked": direct_entries,
            "cyclic_coefficients_checked": len(expected_scalar),
            "normalization": f"1/{math.prod(shape)}", "seed": seed,
            "seconds": perf_counter()-started,
            "negative_without_twist": "last-axis wrap has the wrong sign"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("at most four allocated CPU slots")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    cases = []
    for dimension in (2, 3, 4):
        for ell in (1, 2, 3):
            for h in range(ell):
                if 2**((dimension-1)*ell+ell+h) <= 2048:
                    cases.append((ell,h,dimension,202610082000+len(cases)))
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(check_case, cases))
    result = {"status": "exact generalized Fourier and product alignment passed",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "workers": args.workers, "rows": rows,
              "totals": {"cases": len(rows),
                         "scalar_records": sum(x["scalar_records"] for x in rows),
                         "formal_fourier_terms_checked": sum(x["formal_fourier_terms_checked"] for x in rows)},
              "limitations": ["finite arithmetic check, not an all-size tape execution",
                               "native main layer/row reservations remain a conditional transfer",
                               "no Gaussian or multiplication exponent claim"]}
    (out/"certificate.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "totals": result["totals"]}))


if __name__ == "__main__":
    main()
