#!/usr/bin/env python3
"""Exact excluded binary residuals and decaying-family parameter controls."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

from review_complex_frames import space, residual, gram, rank, dot


def boundary(h, old, new):
    U, V = space(old, h), space(new, h)
    assert rank(U+V) == len(V)
    R = residual(U, V)
    assert rank(gram(R)) == len(R) and all(dot(x, x) == 0 for x in R)
    return dict(h=h, child=list(old), parent=list(new),
                residual_dimension=len(R), exact_gram_rank=rank(gram(R)),
                alternating=True, orthonormal_basis_impossible=True)


def scoped_controls():
    checked = 0
    branches = {'guard': 0, 'prefix': 0}
    examples = []
    for a in (Q(1, 8), Q(1, 32), Q(1, 2**30)):
        for b in (2*a, 4*a/(1+a), 5*a):
            assert 0 < a < b < 1
            tau = 1-a
            U = a*a/(1+max(4*a*a/b, a+a*a))
            for j in range(1, 201):
                c = (a/tau)*Q(j, 201)
                q = min(a*c, a-tau*c)
                assert q > 0
                # Limiting constraints from guard, prefix and CRT margins.
                eps = 1/(1+max(4*q/b, c+q, q/a))
                score = eps*q
                assert score <= U
                if c != a:
                    assert score < U
                checked += 1
            assert 4*(a*a/b) == 4*a*a/b
            eps = 1/(1+max(4*a*a/b, a+a*a))
            assert eps*a*a == U
            assert a*(1-eps) >= U and 1-eps*(1+a) >= U
            # Choosing r just below 1-eps and delta sufficiently small leaves
            # inverse/scalar margins above U; r=(1-eps)/2 already suffices.
            r = (1-eps)/2
            assert r > U and 1-eps-r > 0
            branch = 'guard' if 4*a*a/b >= a+a*a else 'prefix'
            branches[branch] += 1
            examples.append(dict(a=str(a), b=str(b), ceiling=str(U), active=branch))
    return dict(exact_sampled_inequality_controls=checked,
                guard_prefix_crossover='b=4a/(1+a)', cases_by_active_ceiling=branches,
                examples=examples,
                scope='Finite controls supplement the piecewise all-size monotonic proof; no general algorithmic ceiling')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    result = dict(source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  excluded_cases=[boundary(6, ('line', 0b111000), ('kernel', 0b000111)),
                                  boundary(9, ('pair', 0b000000011, 0b111111000), ('kernel', 0b000000111))],
                  decaying_model=scoped_controls())
    assert result['excluded_cases'][0]['residual_dimension'] == 4
    assert result['excluded_cases'][1]['residual_dimension'] == 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS two exact alternating exclusions and',
          result['decaying_model']['exact_sampled_inequality_controls'], 'decaying model controls')


if __name__ == '__main__':
    main()
