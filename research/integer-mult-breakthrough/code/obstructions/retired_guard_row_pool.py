#!/usr/bin/env python3
"""Exact retired-guard row lifecycle, with explicit C reference children.

Reference indexing and C kernels are finite oracles, not native tape bills.
K=1 controls complete small volumes; native guard hypotheses are analytical.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def kernels(data: list, rows: int, e: int, positions: list[int], inverse=False):
    out = list(data)
    n = 1 << e
    for bit in positions:
        for row in range(rows):
            for x in range(n):
                if x & (1 << bit):
                    continue
                lo, hi = row * n + x, row * n + (x | (1 << bit))
                a, b = out[lo], out[hi]
                sr, si = a[0] + b[0], a[1] + b[1]
                dr, di = a[0] - b[0], a[1] - b[1]
                sign = -1 if inverse else 1
                out[lo] = (sr - sign * di, si + sign * dr)
                out[hi] = (sr + sign * di, si - sign * dr)
    return out


def project(x: int, positions: list[int]) -> int:
    return sum(((x >> bit) & 1) << j for j, bit in enumerate(positions))


def lifecycle(data: list, rows: int, e: int, h: int, roles: int,
              trace: list, inverse=False, depth=0):
    if e < 4 * h:
        return kernels(data, rows, e, list(range(e)), inverse)
    g, u = e // (2 * h) - 1, e % (2 * h)
    active = [slot * (g + 1) + j for slot in range(2 * h) for j in range(g)]
    guards = [slot * (g + 1) + g for slot in range(2 * h)]
    guards += list(range(2 * h * (g + 1), e))
    child_e, guard_bits = len(active), len(guards)
    assert guard_bits == 2 * h + u and 0 < child_e < e
    # Every inactive guard chunk becomes part of the row pool. No new axis.
    row_before = rows * (1 << guard_bits)
    row_padded = ((row_before + roles - 1) // roles) * roles
    row_child = row_padded // roles
    parent_n, child_n = 1 << e, 1 << child_e
    assert row_before * child_n == rows * parent_n
    assert (row_padded - row_before) < roles
    before = list(data) if inverse else kernels(data, rows, e, guards)
    packed = [(0, 0)] * (row_padded * child_n)
    positions = []
    for row in range(rows):
        for x in range(parent_n):
            new_row = row * (1 << guard_bits) + project(x, guards)
            index = new_row * child_n + project(x, active)
            packed[index] = before[row * parent_n + x]
            positions.append(index)
    assert len(set(positions)) == rows * parent_n
    trace.append({'depth': depth, 'active_parent': e, 'active_child': child_e,
                  'rows_before_retirement': rows, 'retired_complete_chunks': guard_bits,
                  'rows_before_padding': row_before, 'rows_padded': row_padded,
                  'rows_per_role': row_child, 'volume_before': rows * parent_n,
                  'volume_padded': row_padded * child_n,
                  'padding_bound_pass': (row_padded-row_before)*(1 << guard_bits) < roles*row_before})
    role_results = []
    for role in range(roles):
        values = [value for row in range(row_child)
                  for value in packed[(roles * row + role) * child_n:
                                      (roles * row + role + 1) * child_n]]
        role_results.append(lifecycle(values, row_child, child_e, h, roles,
                                      trace, inverse, depth + 1))
    for role, values in enumerate(role_results):
        for row in range(row_child):
            packed[(roles * row + role) * child_n:
                   (roles * row + role + 1) * child_n] = values[row * child_n:(row + 1) * child_n]
    assert all(value == (0, 0) for value in packed[row_before * child_n:])
    restored = [packed[index] for index in positions]
    # Inverse enters child first and undoes the retired guard transform last.
    return kernels(restored, rows, e, guards, True) if inverse else restored


def probe(case):
    e, roles, rows = case
    h = 2
    n = rows * (1 << e)
    traces, digests = [], []
    for field in range(4):
        data = [(((11*j+field)%29)-14, ((17*j+5*field)%31)-15) for j in range(n)]
        trace = []
        out = lifecycle(data, rows, e, h, roles, trace)
        expected = kernels(data, rows, e, list(range(e)))
        assert out == expected
        reverse_trace = []
        back = lifecycle(out, rows, e, h, roles, reverse_trace, inverse=True)
        assert back == [(a << (2*e), b << (2*e)) for a, b in data]
        assert trace == reverse_trace
        traces = trace
        digests.append(hashlib.sha256(json.dumps(out).encode()).hexdigest())
    # Retirement controlled by a guard value is not a commuting operation.
    def bad_route(v):
        result = [(0, 0)] * 4
        for x, value in enumerate(v):
            result[x ^ ((x & 1) << 1)] = value
        return result
    witness = [(1, 0), (0, 0), (0, 0), (0, 0)]
    assert kernels(bad_route(witness), 1, 2, [0]) != bad_route(kernels(witness, 1, 2, [0]))
    return {'case': {'e': e, 'roles': roles, 'initial_rows': rows, 'K': 1},
            'complete_records_each_field': n, 'fields': 4,
            'full_C_reference_agrees': True, 'true_inverse_agrees': True,
            'zero_padding_returns_zero': True, 'unsafe_guard_control_rejected': True,
            'integer_common_denominator_power_forward': e,
            'integer_common_denominator_power_after_inverse': 2*e,
            'trace': traces, 'field_sha256': digests,
            'scope': 'Exact row allocation with explicit full C reference children; no scalar network or native time'}


def integer_pool_controls():
    result = []
    for h, roles, K in [(2, 3, 6), (3, 17, 6), (4, 257, 8)]:
        row_count, e, steps = 1, 96, []
        while e >= 4*h:
            guards = 2*h + e % (2*h)
            before = row_count << (guards*K)
            padded = ((before+roles-1)//roles)*roles
            assert padded-before < roles
            assert (padded-before)*(1 << (2*h*K)) < roles*before
            row_count = padded//roles
            child_e = e-guards
            assert child_e < e
            steps.append({'e': e, 'child_e': child_e, 'retired_guard_chunks': guards,
                          'complete_row_count': row_count, 'padding_rows': padded-before})
            e = child_e
        result.append({'h': h, 'roles': roles, 'K': K, 'steps': steps})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = Path(__file__)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    cases = [(8, 3, 1), (9, 5, 2)] if args.bounded else [(8, 3, 1), (9, 5, 2), (10, 3, 3), (12, 5, 1)]
    protocol = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'workers': args.workers, 'source_sha256': digest, 'cases': cases,
                'seeds': None, 'scope': 'K1 complete operator controls plus native-K exact integer row ledger; C children are explicit reference oracles'}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, cases))
    summary = {'status': 'PASS RETIRED GUARD ROW LIFECYCLE', 'protocol': protocol,
               'cases': rows, 'large_integer_pool_controls': integer_pool_controls(),
               'source_unchanged': hashlib.sha256(source.read_bytes()).hexdigest() == digest,
               'scope': 'Exact finite row/zero/payload lifecycle only; complete canonical scalar network and strict paid moment remain required'}
    assert summary['source_unchanged']
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({'status': summary['status'], 'cases': len(rows),
                      'complete_records_four_fields': 4*sum(x['complete_records_each_field'] for x in rows)}))


if __name__ == '__main__':
    main()
