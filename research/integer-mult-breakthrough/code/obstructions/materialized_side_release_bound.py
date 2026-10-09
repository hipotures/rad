#!/usr/bin/env python3
"""Exact controls for a conditional full-materialized-side release bound.

The model requires a closed full-to-proper-to-full excursion for each scalar
side channel. It does not cover arbitrary joint center/side circuits, direct
geodesic transfers, operator-valued mixtures or a multiplication lower bound.
OpenAI Codex assisted the mathematical discriminator and implementation.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time


def rank(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    if not rows:
        return 0
    assert len({len(row) for row in rows}) == 1
    position = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(position, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[position], rows[pivot] = rows[pivot], rows[position]
        scale = rows[position][column]
        rows[position] = [x / scale for x in rows[position]]
        for i in range(position + 1, len(rows)):
            coefficient = rows[i][column]
            if coefficient:
                rows[i] = [x - coefficient * y for x, y in zip(rows[i], rows[position])]
        position += 1
        if position == len(rows):
            break
    return position


def central(h, k):
    subsets = list(combinations(range(h), k))
    d = (k - 1) // 2
    masks = [sum(1 << j for j in subset) for subset in subsets]
    def entry(a, b):
        t = (a & b).bit_count()
        result = Q(1)
        for j in range(d):
            result *= Q(t - 1 - 2 * j, 2 * (j + 1))
        return result
    return [[entry(a, b) for b in masks] for a in masks]


def assess(h, matrix, name):
    start = time.perf_counter()
    v = len(matrix)
    assert h >= 2 and v and all(len(row) == v for row in matrix)
    q = rank(matrix)
    side = [[Q(int(i == j)) - matrix[i][j] for j in range(v)] for i in range(v)]
    d = rank(side)
    # Identity = K+(I-K), so rank subadditivity gives d >= v-q.
    assert q + d >= v
    center_only_deficit = 2 * v - 2 * q * h
    compressed_side_excess = -center_only_deficit + 2 * d
    necessary_excess = 2 * q * (h - 1)
    assert compressed_side_excess >= necessary_excess >= 0
    # The exact input matrix, not selected entries, determines both ranks.
    return dict(case=name, h=h, v=v, rank_center=q, rank_side=d,
                center_only_deficit=center_only_deficit,
                optimally_compressed_closed_side_excess=compressed_side_excess,
                universal_excess_within_model=necessary_excess,
                matrix_sha256=sha256(json.dumps(matrix, default=str, separators=(',', ':')).encode()).hexdigest(),
                seconds=time.perf_counter() - start)


def case(spec):
    name, h, k = spec
    if k:
        matrix = central(h, k)
    else:
        v = 64
        matrix = [[Q(int(i == j and i < 3)) for j in range(v)] for i in range(v)]
    return assess(h, matrix, name)


def controls():
    receipts = []
    for h in (2, 3, 7):
        for v in (2, 4):
            for q in range(v + 1):
                matrix = [[Q(int(i == j and i < q)) for j in range(v)] for i in range(v)]
                row = assess(h, matrix, 'exact projection')
                assert row['rank_center'] == q and row['rank_side'] == v - q
                assert row['optimally_compressed_closed_side_excess'] == row['universal_excess_within_model']
                receipts.append(row)
    # Losing the identity term changes the problem: zero K and zero "side"
    # do not have ranks summing to the input dimension.
    zero = [[Q(0)] * 4 for _ in range(4)]
    assert rank(zero) + rank(zero) < 4
    nilpotent = [[Q(0), Q(1), Q(0)], [Q(0), Q(0), Q(1)], [Q(0)] * 3]
    result = assess(3, nilpotent, 'nonprojector nilpotent')
    assert result['rank_center'] == 2 and result['rank_side'] == 3
    return dict(tight_projection_cases=len(receipts), nilpotent=result,
                omitted_identity_rejected=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh output directory')
    specs = [('k3-h4', 4, 3), ('k3-h9', 9, 3), ('k5-h8', 8, 5),
             ('center-profitable-projection', 7, 0)]
    if args.bounded:
        specs = [specs[0], specs[-1]]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    worker_processes=args.workers, cases=specs, seed=None,
                    source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    scope=__doc__)
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(case, specs))
    result = dict(status='PASS CONDITIONAL MATERIALIZED-SIDE BOUND CONTROLS',
                  cases=rows, controls=controls(), seconds=time.perf_counter() - start,
                  limitations='Rank and closed-channel premises only; no arbitrary-circuit, Gaussian-phase, tape-time or exponent theorem.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
