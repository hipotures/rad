#!/usr/bin/env python3
"""Align OLD-row role splits with complete fresh guard cubes.

Finite Gaussian children and vector indexing are reference oracles. The
script does not supply a canonical scalar network or native tape runtime.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from retired_guard_row_pool import kernels, project


def lifecycle(data, rows, e, h, roles, trace, inverse=False, depth=0):
    if e < 4*h:
        return kernels(data, rows, e, list(range(e)), inverse)
    g, u = e//(2*h)-1, e%(2*h)
    active = [slot*(g+1)+j for slot in range(2*h) for j in range(g)]
    guards = [slot*(g+1)+g for slot in range(2*h)]
    guards += list(range(2*h*(g+1), e))
    q, child_e = len(guards), len(active)
    G, n, child_n = 1 << q, 1 << e, 1 << child_e
    old_padded = ((rows+roles-1)//roles)*roles
    quotient = old_padded//roles
    child_rows = quotient*G
    assert G*child_n == n and 0 < child_e < e
    assert old_padded-rows < roles and child_rows >= G
    before = list(data) if inverse else kernels(data, rows, e, guards)
    packed = [(0, 0)]*(old_padded*G*child_n)
    positions = []
    for row in range(rows):
        for x in range(n):
            index = (row*G+project(x, guards))*child_n+project(x, active)
            packed[index] = before[row*n+x]
            positions.append(index)
    assert len(set(positions)) == rows*n
    record = {'depth': depth, 'e': e, 'child_e': child_e,
              'old_rows': rows, 'old_rows_padded': old_padded,
              'fresh_guard_cube': G, 'fresh_guard_chunks': q,
              'rows_per_role': child_rows,
              'full_guard_cube_independent_of_role': True,
              'root_fixed_padding_only': depth == 0,
              'all_nonroot_old_rows_at_least_16': depth == 0 or rows >= 16}
    assert record['all_nonroot_old_rows_at_least_16']
    trace.append(record)
    results = []
    for role in range(roles):
        # Role depends on OLD row alone, never on a fresh guard coordinate.
        values = [value for k in range(quotient)
                  for value in packed[(roles*k+role)*G*child_n:
                                      (roles*k+role+1)*G*child_n]]
        assert len(values) == quotient*G*child_n
        results.append(lifecycle(values, child_rows, child_e, h, roles,
                                 trace, inverse, depth+1))
    for role, values in enumerate(results):
        for k in range(quotient):
            packed[(roles*k+role)*G*child_n:(roles*k+role+1)*G*child_n] = \
                values[k*G*child_n:(k+1)*G*child_n]
    assert all(value == (0, 0) for value in packed[rows*G*child_n:])
    restored = [packed[index] for index in positions]
    return kernels(restored, rows, e, guards, True) if inverse else restored


def rehydration_probe(h=2, g=1):
    active_count, guard_count = 2*h*g, 2*h
    e = active_count+guard_count
    labels = list(range(e))
    swaps = []
    for j in range(guard_count):
        label, destination = active_count+j, (j+1)*(g+1)-1
        origin = labels.index(label)
        if origin != destination:
            labels[origin], labels[destination] = labels[destination], labels[origin]
            swaps.append((origin, destination))
    assert len(swaps) <= 2*h
    guard_positions = [(j+1)*(g+1)-1 for j in range(2*h)]
    assert [labels[p] for p in guard_positions] == list(range(active_count, e))
    new_active = [p for p in range(e) if p not in guard_positions]
    n = 1 << e
    permutation = [sum(((x >> labels[p]) & 1) << p for p in range(e)) for x in range(n)]
    assert len(set(permutation)) == n
    for field in range(4):
        data = [(((7*j+field)%19)-9, ((13*j+field)%23)-11) for j in range(n)]
        moved = [(0, 0)]*n
        for old, new in enumerate(permutation):
            moved[new] = data[old]
        applied = kernels(moved, 1, e, new_active)
        restored = [applied[new] for new in permutation]
        assert restored == kernels(data, 1, e, list(range(active_count)))
    return {'h': h, 'g': g, 'whole_chunk_swaps': swaps,
            'all_physical_addresses': n, 'fields': 4,
            'active_coordinate_order_may_change': True,
            'exact_conjugated_C_tensor_agrees': True,
            'scope': 'Literal K1 reference rehydration only; a complete network must bind all frames to the new active order'}


def probe(case):
    e, roles, rows = case
    n = rows*(1 << e)
    trace, hashes = [], []
    for field in range(4):
        data = [(((11*j+field)%29)-14, ((17*j+field)%31)-15) for j in range(n)]
        trace = []
        out = lifecycle(data, rows, e, 2, roles, trace)
        assert out == kernels(data, rows, e, list(range(e)))
        reversed_trace = []
        back = lifecycle(out, rows, e, 2, roles, reversed_trace, True)
        assert back == [(a << (2*e), b << (2*e)) for a, b in data]
        assert trace == reversed_trace
        hashes.append(hashlib.sha256(json.dumps(out).encode()).hexdigest())
    return {'e': e, 'roles': roles, 'old_rows': rows, 'K': 1, 'fields': 4,
            'complete_records_each_field': n, 'field_sha256': hashes, 'trace': trace,
            'zero_padding_returns_zero': True, 'full_C_and_true_inverse_agree': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = Path(__file__)
    helper = source.with_name('retired_guard_row_pool.py')
    pins = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in [source, helper]}
    cases = [(8, 3, 1), (9, 5, 2)] if args.bounded else [(8, 3, 1), (9, 5, 2), (10, 3, 3), (12, 5, 1)]
    protocol = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'workers': args.workers, 'source_sha256': pins, 'cases': cases,
                'seeds': None, 'scope': 'Aligned complete row/guard cubes with exact C reference children, not a native scalar network'}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(probe, cases))
    geometry = [rehydration_probe(2, 1)]
    if not args.bounded:
        geometry += [rehydration_probe(2, 2), rehydration_probe(3, 1)]
    after = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in [source, helper]}
    assert after == pins
    summary = {'status': 'PASS ALIGNED ROW POOL AND COMPLETE GUARD CUBES',
               'protocol': protocol, 'cases': results, 'rehydration': geometry,
               'source_unchanged': True,
               'scope': 'Exact finite corrected allocation and active-order conjugation; canonical network/native precision and paid moment remain unsupplied'}
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({'status': summary['status'], 'cases': len(results),
                      'complete_records_four_fields': 4*sum(q['complete_records_each_field'] for q in results)}))


if __name__ == '__main__':
    main()
