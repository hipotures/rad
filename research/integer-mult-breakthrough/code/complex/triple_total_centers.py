#!/usr/bin/env python3
"""Integral triple-subset total/star quotient and its declared capacity.

The complete scalar word is unimodular and needs no fractional-bit extension.
Native phase chronology, the auxiliary proxy and center losses remain open.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
from time import perf_counter

from center_basis_scalar_word import apply
from characteristic import moment_interval, rational_root_bracket, serializable


TARGET = Q(20, 189981)


def feature(center, source):
    return 1 if center == 0 else int(center in source)


def word(h):
    if h < 4:
        raise ValueError('The unimodular base uses four labels')
    pivots = [tuple(j for j in range(4) if j != missing) for missing in range(4)]
    pivots += [(0, 1, j) for j in range(4, h)]
    assert len(set(pivots)) == h
    chosen = set(pivots)
    sources = pivots+[source for source in combinations(range(h), 3) if source not in chosen]
    gates = [['add', 0, j, Q(1)] for j in range(1, 4)]
    for j in range(1, 4):
        gates += [['scale', j, Q(-1)], ['add', j, 0, Q(1)]]
    for j in range(4, h):
        gates += [['add', 0, j, Q(1)], ['add', 1, j, Q(1)]]
    for j, source in enumerate(sources[h:], h):
        gates.append(['add', 0, j, Q(1)])
        gates += [['add', center, j, Q(1)] for center in source if center != 0]
    return dict(source_order=sources, center_order=list(range(h)), gates=gates,
                total_center=0, extra_banks=0)


def counts(h):
    v = comb(h, 3)
    additions = 4*v-comb(h-1, 2)-h-3
    return dict(h=h, volume=v, center_rank=h,
        feature_nonzeros=4*v-comb(h-1, 2),
        additions=additions, negations=3, swaps=0,
        expanded_scalar_proxy=additions+3,
        proxy_per_source=Q(additions+3, v),
        additional_fractional_bits=0,
        scope='Exact integral scalar word only; actual complete native auxiliary count is not inferred.')


def scalar_control(h, seed=20261009):
    compiled = word(h)
    sources, gates = compiled['source_order'], compiled['gates']
    v = len(sources)
    counted = Counter(gate[0] for gate in gates)
    expected = counts(h)
    assert counted['add'] == expected['additions'] and counted['scale'] == 3
    originals = [[Q(int(i == j)) for i in range(v)] for j in range(v)]
    rng = random.Random(seed)
    originals += [[Q(rng.randrange(-100, 101), 1 << rng.randrange(6)) for _ in range(v)] for _ in range(4)]
    for original in originals:
        actual = apply(gates, original)
        expected_values = [sum(feature(center, source)*x for source, x in zip(sources, original))
                           for center in range(h)]+original[h:]
        assert actual == expected_values
        assert apply(gates, actual, True) == original
    checked = 0
    for target in sources:
        zero = int(0 in target)
        decoder = [3*zero-1]+[int(center in target)-zero for center in range(1, h)]
        for source in sources:
            value = sum(c*feature(center, source) for center, c in enumerate(decoder))
            assert value == len(set(source) & set(target))-1
            checked += 1
    assert any(apply(list(reversed(gates)), apply(gates, original)) != original for original in originals)
    return dict(h=h, scalar_counts=counts(h), complete_columns=v,
        forward_inverse_scalar_values=2*v*v, arbitrary_dirty_fields=4,
        central_entries=checked, decoder_denominator_bits=1,
        wrong_inverse_rejected=True,
        word_sha256=sha256(json.dumps(serializable(compiled), separators=(',', ':')).encode()).hexdigest())


def profile(h, R, loss):
    v = comb(h, 3)
    N, m = v*v, h*h
    W = 2*N+2*v*R
    children = Counter({m-h: 2*v*R, (h-1)**2: 2*N, h-1: 4*N, 1: N})
    children[1] += 2*v*(h*R+loss)
    assert sum(t*n for t, n in children.items()) == W*m-N+2*v*loss
    return dict(ambient_h=h, source_weight=3, volume=v, N=N, m=m, W=W,
        assumed_auxiliary_roles=R, assumed_center_loss=loss,
        deficit=N-2*v*loss, child_multiplicities=dict(sorted(children.items())),
        scope='Declared two-axis profile only; no actual frame compiler supplies these multiplicities.')


def capacity(h):
    started = perf_counter()
    scalar = counts(h)
    R = scalar['expanded_scalar_proxy']
    # h-1 ordinary singleton stars have rank h-1; total has full rank h.
    analogy = (h-1)**2+h
    rows = []
    for name, loss in [('single-total copied-frame analogy', analogy),
                       ('replace center cost by one full-width traversal', h*h),
                       ('replace center cost by closed full-width release', 2*h*h),
                       ('add closed full-width release to old analogy', analogy+2*h*h)]:
        p = profile(h, R, loss)
        interval = moment_interval(p, TARGET)
        rows.append(dict(center_cost_hypothesis=name, profile=p,
            target=TARGET, target_moment_interval=interval,
            target_status='below1' if interval[1] < 1 else 'above1' if interval[0] > 1 else 'unresolved',
            root_bracket=rational_root_bracket(p) if p['deficit'] > 0 else None))
    return dict(status='CONDITIONAL TRIPLE-TOTAL CAPACITY', h=h,
        scalar_counts=scalar, rows=rows, elapsed_seconds=perf_counter()-started,
        obligations=['Actual address operators must coincide for scalar shears',
                     'All source/sink/dirty continuation and decoder costs are included',
                     'Complete native R is bounded by the declared scalar proxy',
                     'Old center calls are removed when their cost is replaced',
                     'Precision, packed routing, binary component and outer multiplication are separately proved'],
        scope='Exact moments of unattained profiles and exact integral scalar component; no native saving or kappa certificate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, required=True)
    parser.add_argument('--literal', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a fresh attempt path')
    if args.literal:
        if not 4 <= args.h <= 10:
            raise ValueError('Literal full scalar checks use h4..10')
        result = scalar_control(args.h)
    else:
        if args.h not in (44, 48, 52, 56):
            raise ValueError('First capacity discriminator uses h44/48/52/56')
        result = capacity(args.h)
    result['source_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(serializable(result), indent=2)+'\n')
    print(json.dumps({k: serializable(v) for k, v in result.items() if k != 'rows'}), flush=True)


if __name__ == '__main__':
    main()
