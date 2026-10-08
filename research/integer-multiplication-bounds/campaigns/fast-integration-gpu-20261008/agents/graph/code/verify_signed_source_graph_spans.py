#!/usr/bin/env python3
"""Independent integer incidence-rank controls for signed source joins.

Direct integer row elimination supplies the expected span dimension; the
candidate normal descriptor supplies neither the expected rank nor input
generators. This checks the new signed graph convention, not all native
projectors or a complete conditional multiplication construction.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import random
import time

import co_signed_source_frames as co
import future_signed_source_frames as future


def integer_rank(rows):
    pivots = {}
    for original in rows:
        row = list(original)
        for pivot, base in sorted(pivots.items()):
            if row[pivot]:
                a, b = row[pivot], base[pivot]
                row = [b * x - a * y for x, y in zip(row, base)]
                divisor = 0
                for value in row:
                    divisor = gcd(divisor, abs(value))
                if divisor > 1:
                    row = [x // divisor for x in row]
        if any(row):
            pivot = next(i for i, x in enumerate(row) if x)
            if row[pivot] < 0:
                row = [-x for x in row]
            pivots[pivot] = row
    return len(pivots)


def check_graph(h, common, specifications):
    pairs = list(combinations(range(h), 2))
    index = {pair: i for i, pair in enumerate(pairs)}
    positive = negative = 0
    rows, source_vectors = [], []
    for a, b, coefficient in specifications:
        assert common not in (a, b) and coefficient in (1, -1)
        bit = 1 << index[tuple(sorted((a, b)))]
        if coefficient == 1:
            positive |= bit
        else:
            negative |= bit
        row = [0] * h
        row[a], row[b] = 1, coefficient
        rows.append(tuple(row))
        vector = [2 * x for x in row]
        vector[common] = sum(row)
        source_vectors.append(tuple(vector))
    expected = integer_rank(rows)
    candidate = future.signed_span(h, common, positive, negative)
    assert candidate[0] == expected
    assert all(co.vector_in(vector, candidate) for vector in source_vectors)
    assert integer_rank(co.basis(candidate)) == expected
    # Equal dimension and all direct generator inclusions prove exact span
    # equality. No descriptor-produced basis is used as the expected rank.
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    pairs = list(combinations(range(1, 5), 2))
    histogram = {}
    for code in range(1, 4 ** len(pairs)):
        specifications = []
        for i, (a, b) in enumerate(pairs):
            state = code >> (2 * i) & 3
            if state & 1:
                specifications.append((a, b, 1))
            if state & 2:
                specifications.append((a, b, -1))
        rank = check_graph(5, 0, specifications)
        histogram[rank] = histogram.get(rank, 0) + 1
    rng = random.Random(202610082256)
    larger = []
    for h in (23, 25):
        for trial in range(32):
            common = rng.randrange(h)
            outside = [i for i in range(h) if i != common]
            specifications = []
            for _ in range(8 + trial):
                a, b = sorted(rng.sample(outside, 2))
                specifications.append((a, b, rng.choice((-1, 1))))
            rank = check_graph(h, common, specifications)
            larger.append(dict(h=h, common=common, trial=trial, rank=rank,
                               signed_generators=len(specifications)))
    receipt = dict(status='PASS independent exact signed source-graph spans',
        exhaustive_four_vertex_signed_graphs=4095, incidence_rank_histogram=histogram,
        full_dimension_controls=larger, expected_rank_method='Independent normalized integer row elimination on directly specified generators',
        descriptor='complemented-signed-one-core-v1; symbols encode orthogonal NORMALS',
        direct_generator_membership=True, exact_span_equality_by_dimension=True,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        generator_source_sha256=sha256(Path(future.__file__).read_bytes()).hexdigest(),
        seconds=time.monotonic()-started, completed_utc=datetime.now(timezone.utc).isoformat(),
        limitations='This checks incidence span and signed-normal conventions. Native rational projectors, NE/CRT certificates, actual scalar and physical words, all DATA/stock/moment/assembly obligations and conditional all-size transfer remain separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(status=receipt['status'], exhaustive=4095, full=64, seconds=receipt['seconds'])), flush=True)


if __name__ == '__main__':
    main()
