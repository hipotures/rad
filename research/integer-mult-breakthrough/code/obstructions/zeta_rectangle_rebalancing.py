#!/usr/bin/env python3
"""Exact rectangle rebalancing and arbitrary-dirty zeta shear controls.

This is an arithmetic circuit experiment. Its wire bill is not native tape
time, and it does not certify a multiplication exponent.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import time


@lru_cache(None)
def optimal_wires(remaining: int, row_power: int, column_power: int) -> int:
    """Exact Bellman optimum over the two literal one-axis partitions."""
    if not remaining:
        return (1 << row_power) + (1 << column_power)
    unchanged = optimal_wires(remaining - 1, row_power, column_power)
    return unchanged + min(
        optimal_wires(remaining - 1, row_power + 1, column_power),
        optimal_wires(remaining - 1, row_power, column_power + 1),
    )


def balanced_wire_formula(h: int) -> int:
    return sum(
        math.comb(h, t) * ((1 << (t // 2)) + (1 << ((t + 1) // 2)))
        for t in range(h + 1)
    )


def rectangles(h: int) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Partition disjointness, then complement rows to obtain subset zeta."""
    leaves = [((0,), (0,))]
    for axis in range(h):
        bit = 1 << axis
        next_leaves = []
        for rows, cols in leaves:
            if len(rows) <= len(cols):
                next_leaves.append((rows + tuple(x | bit for x in rows), cols))
                next_leaves.append((rows, tuple(x | bit for x in cols)))
            else:
                next_leaves.append((rows, cols + tuple(x | bit for x in cols)))
                next_leaves.append((tuple(x | bit for x in rows), cols))
        leaves = next_leaves
    mask = (1 << h) - 1
    return [(tuple(x ^ mask for x in rows), cols) for rows, cols in leaves]


def source_sums(x: list[int], boxes: list) -> list[int]:
    return [sum(x[j] for j in cols) for _, cols in boxes]


def sink_sums(c: list[int], boxes: list, dimension: int) -> list[int]:
    result = [0] * dimension
    for value, (rows, _) in zip(c, boxes):
        for i in rows:
            result[i] += value
    return result


def zeta_reference(x: list[int]) -> list[int]:
    return [sum(value for j, value in enumerate(x) if j & i == j)
            for i in range(len(x))]


def word(x: list[int], y: list[int], c: list[int], boxes: list,
         inverse: bool = False, omit_old_dirty_cut: bool = False) -> tuple[list, list, list]:
    """Four additive stages; true reverse order for the inverse."""
    x, y, c = list(x), list(y), list(c)
    stages = [('sink', -1), ('source', 1), ('sink', 1), ('source', -1)]
    if inverse:
        stages = [(kind, -sign) for kind, sign in reversed(stages)]
    for index, (kind, sign) in enumerate(stages):
        if omit_old_dirty_cut and index == 0:
            continue
        if kind == 'source':
            sums = source_sums(x, boxes)
            c = [a + sign * b for a, b in zip(c, sums)]
        else:
            sums = sink_sums(c, boxes, len(y))
            y = [a + sign * b for a, b in zip(y, sums)]
    return x, y, c


def probe(h: int) -> dict:
    started = time.perf_counter()
    n = 1 << h
    boxes = rectangles(h)
    assert len(boxes) == n
    matrix = [[0] * n for _ in range(n)]
    for rows, cols in boxes:
        for i in rows:
            for j in cols:
                matrix[i][j] += 1
    assert all(matrix[i][j] == int(j & i == j)
               for i in range(n) for j in range(n))
    wires = sum(len(rows) + len(cols) for rows, cols in boxes)
    assert wires == balanced_wire_formula(h) == optimal_wires(h, 0, 0)
    zero = [0] * n
    for bank in range(3):
        for column in range(n):
            inputs = [zero.copy() for _ in range(3)]
            inputs[bank][column] = 1
            x, y, c = inputs
            out = word(x, y, c, boxes)
            expected = (x, [a + b for a, b in zip(y, zeta_reference(x))], c)
            assert out == expected
            assert word(*out, boxes, inverse=True) == (x, y, c)
    fields = []
    for field in range(4):
        x = [((17 * j + 11 * field) % 31) - 15 for j in range(n)]
        y = [((13 * j + 7 * field) % 29) - 14 for j in range(n)]
        c = [((19 * j + 5 * field) % 37) - 18 for j in range(n)]
        out = word(x, y, c, boxes)
        assert out == (x, [a + b for a, b in zip(y, zeta_reference(x))], c)
        assert word(*out, boxes, inverse=True) == (x, y, c)
        fields.append(out)
    dirty = [1] * n
    assert word(zero, zero, dirty, boxes, omit_old_dirty_cut=True) != (zero, zero, dirty)
    # An all-positive upper corner receives all n original coefficients.
    assert zeta_reference([1] * n)[-1] == n
    return {
        'h': h, 'dimension': n, 'rectangles': len(boxes), 'depth_two_wires': wires,
        'dirty_word_wire_uses': 2 * wires, 'complete_linear_columns': 3 * n,
        'payload_fields': 4, 'old_dirty_cut_required': True,
        'source_bank_preserved': True, 'dirty_bank_restored': True,
        'triangular_diagonal_proves_full_rank': all(matrix[i][i] == 1 for i in range(n)),
        'balanced_policy_is_bellman_optimal': True,
        'field_output_sha256': hashlib.sha256(json.dumps(fields).encode()).hexdigest(),
        'seconds': time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = Path(__file__)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    protocol = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'workers': args.workers, 'source_sha256': source_hash,
                'dimensions': [3, 4] if args.bounded else [3, 4, 5, 6],
                'seeds': None, 'scope': 'Exact arithmetic rectangle and dirty shear only; no native time or exponent'}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, protocol['dimensions']))
    recurrence = []
    values = [2, 5]
    for _ in range(2, 49):
        values.append(2 * values[-1] + values[-2])
    for h in range(49):
        exact = balanced_wire_formula(h)
        assert exact == values[h]
        recurrence.append({'h': h, 'wires': exact, 'labels': 1 << h})
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    summary = {'status': 'PASS EXACT REBALANCED ZETA ARITHMETIC AND DIRTY WORD',
               'protocol': protocol, 'cases': rows, 'wire_recurrence': recurrence,
               'source_unchanged': True,
               'scope': 'Two literal partitions only. Complete full-rank shear uses one dirty channel per label; arithmetic wire improvement is not a native exponent.'}
    if args.output:
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'status': summary['status'], 'cases': len(rows),
                      'depth_two_wires': [row['depth_two_wires'] for row in rows]}))


if __name__ == '__main__':
    main()
