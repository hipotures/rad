#!/usr/bin/env python3
"""Necessary capacity of a proposed geodesic dirty side chronology.

This reconstructs every orthogonal side edge and nested binary frame span.
It is a conditional geometric profile for a framed identity shear, not a
canonical C primitive or an attained multiplication exponent. Exact moment
bounds reuse the already published rational characteristic arithmetic.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys
import time

COMPLEX = Path(__file__).resolve().parents[1] / 'complex'
sys.path.insert(0, str(COMPLEX))
import characteristic as arithmetic

TARGET = Q(20, 189981)


def extend(columns, value):
    """Maintain a reduced echelon binary span in descending pivot order."""
    for pivot in columns:
        if value & (1 << (pivot.bit_length() - 1)):
            value ^= pivot
    if not value:
        return False
    position = value.bit_length() - 1
    columns[:] = [x ^ value if x >> position & 1 else x for x in columns]
    columns.append(value)
    columns.sort(reverse=True)
    return True


def case(h):
    start = time.perf_counter()
    labels = [sum(1 << j for j in s) for s in combinations(range(h), 3)]
    v, q = len(labels), h
    assert v == comb(h, 3)
    spans = [[] for _ in labels]
    widths = Counter({})
    dimensions = Counter({})
    edges = 0
    scalar_coefficients = Counter({})
    for source in labels:
        for target_index, target in enumerate(labels):
            t = (source & target).bit_count()
            coefficient = Q(int(source == target)) - Q(t - 1, 2)
            if not coefficient:
                continue
            assert t % 2 == 0 and source != target
            scalar_coefficients[str(coefficient)] += 1
            E = spans[target_index]
            old_rank = len(E)
            extend(E, source)
            rank = len(E)
            assert old_rank <= rank <= old_rank + 1 and 1 <= rank <= h - 1
            assert all((vector & target).bit_count() % 2 == 0 for vector in E)
            # One incoming line, a nested line-to-current-span transition,
            # and the remaining span-to-full transition. Zero ranks vanish.
            widths[1] += 1
            if rank > 1:
                widths[rank - 1] += 1
            widths[h - rank] += 1
            dimensions[rank] += 1
            edges += 1
    assert sum(rank * count for rank, count in widths.items()) == edges * h
    side_widths = dict(sorted(widths.items()))
    # Sources and central helpers contribute their original complete paths.
    widths[1] += v
    widths[h - 1] += 2 * v
    widths[h] += 2 * q
    # Each sink follows nested one-dimensional extensions, then completes
    # to its target perpendicular. The final residual is charged explicitly.
    sink_widths = Counter({})
    for E in spans:
        sink_widths[1] += len(E)
        if len(E) < h - 1:
            sink_widths[h - 1 - len(E)] += 1
    assert sum(rank * count for rank, count in sink_widths.items()) == v * (h - 1)
    widths.update(sink_widths)
    W = 3 * v + edges
    total = sum(rank * count for rank, count in widths.items())
    deficit = 2 * v - 2 * q * h
    assert total == W * h - deficit
    profile = dict(m=h, W=W, total_rank=total, deficit=deficit,
                   maxchild=max(widths), child_multiplicities=dict(sorted(widths.items())))
    interval = arithmetic.moment_interval(profile, TARGET)
    root = arithmetic.rational_root_bracket(profile) if deficit > 0 else None
    # A closed full-materialized-output splice would add at least twice
    # the side rank. Its separate proof is not silently applied to this
    # geodesic word, whose early dirty subtraction uses the zero frame.
    return dict(h=h, source_banks=v, center_features=q, side_helpers=edges,
                physical_stock=W, source_order='Lexicographic three-subsets',
                complete_side_edges=edges, scalar_side_coefficients=dict(scalar_coefficients),
                side_helper_histogram=side_widths,
                side_used_span_dimensions=dict(sorted(dimensions.items())),
                final_neighbor_span_dimensions=dict(Counter(map(len, spans))),
                final_neighbor_spans_sha256=sha256(json.dumps(spans, separators=(',', ':')).encode()).hexdigest(),
                sink_histogram=dict(sorted(sink_widths.items())), profile=profile,
                complex_target=TARGET, target_moment_interval=interval,
                target_status='below1' if interval[1] < 1 else 'above1' if interval[0] > 1 else 'unresolved',
                conditional_root_bracket=root, seconds=time.perf_counter() - start,
                obligations=['Actual consistent L_E representatives and every relative phase unit',
                             'Complete arbitrary-dirty scalar and Gaussian word',
                             'Native same-width child and all live-stock/guard/routing contracts',
                             'A canonical C primitive derived from the framed identity shear, including initial encoding',
                             'Full binary/complex multiplication assembly'],
                scope='Exact consequences of the proposed complete geometric chronology. Every scalar edge is retained, but physical realization and canonical primitive transfer are not certified here.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError('Use a fresh output directory')
    dimensions = [9] if args.bounded else [9, 10, 12, 16]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    worker_processes=args.workers, ambient_dimensions=dimensions,
                    source_sha256={str(p): sha256(p.read_bytes()).hexdigest()
                                   for p in [Path(__file__), COMPLEX / 'characteristic.py']},
                    seeds=None, ordering='Complete deterministic lexicographic source/target enumeration')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(case, dimensions))
    result = dict(status='CONDITIONAL GEODESIC SIDE CAPACITY PROFILE',
                  cases=arithmetic.serializable(rows),
                  scope='No new canonical primitive, native theorem or kappa is claimed.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    for row in result['cases']:
        print(json.dumps({key: row[key] for key in ['h', 'side_helpers', 'physical_stock', 'target_status', 'conditional_root_bracket', 'seconds']}), flush=True)


if __name__ == '__main__':
    main()
