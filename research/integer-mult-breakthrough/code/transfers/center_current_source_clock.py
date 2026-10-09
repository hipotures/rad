#!/usr/bin/env python3
"""Paid current-source phase clock for a naive direct full-root gather.

The exact local source/target endpoint tests have arbitrary four-field dirty
values. The master ledger is conditional on replacing the old center block
by q full roots and retaining the same source/target/correction/side contract.
This excludes that replacement's unpaid full/kernel/full detour, not all
possible source-sharing architectures.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

import synchronized_center_review as exact


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def c_axes(values, axes, inverse=False):
    out = [list(row) for row in values]
    alpha = (Q(1, 2), Q(-1 if inverse else 1, 2))
    beta = (alpha[0], -alpha[1])
    for bit in axes:
        for address in range(len(out)):
            if address >> bit & 1:
                continue
            partner = address | (1 << bit)
            low, high = out[address], out[partner]
            out[address] = [add(multiply(alpha, a), multiply(beta, b)) for a, b in zip(low, high)]
            out[partner] = [add(multiply(beta, a), multiply(alpha, b)) for a, b in zip(low, high)]
    return out


def schedule(width, direct=False):
    cap = min(5, width - 1)
    if direct:
        return [('C', list(range(1, width)), False),
                ('C', [width - 1], True), ('add', None, None),
                ('C', [width - 1], False)]
    return [('C', list(range(1, cap)), False),
            ('C', list(range(cap, width - 1)), False),
            ('add', None, None), ('C', [width - 1], False)]


def execute(word, source, target, reverse=False, omit=None):
    source, target = [list(row) for row in source], [list(row) for row in target]
    events = list(enumerate(word))
    if reverse:
        events.reverse()
    for index, (kind, axes, inverse) in events:
        if index == omit:
            continue
        if kind == 'C':
            source = c_axes(source, axes, not inverse if reverse else inverse)
        else:
            sign = -1 if reverse else 1
            target = [[add(a, (sign * b[0], sign * b[1])) for a, b in zip(left, right)]
                      for left, right in zip(target, source)]
    return source, target


def physical_case(width):
    size = 1 << width
    x = [[(Q((11 * address + 3 * field) % 29 - 14, 8),
           Q((7 * address + 5 * field) % 31 - 15, 16))
          for field in range(4)] for address in range(size)]
    y = [[(Q((13 * address + 2 * field) % 37 - 18, 16),
           Q((5 * address + 7 * field) % 41 - 20, 8))
          for field in range(4)] for address in range(size)]
    initial_x, initial_y = c_axes(x, [0]), c_axes(y, range(width - 1))
    y_plus_x = [[add(a, b) for a, b in zip(left, right)] for left, right in zip(y, x)]
    expected = c_axes(x, range(width)), c_axes(y_plus_x, range(width - 1))
    words = [schedule(width), schedule(width, True)]
    for word in words:
        actual = execute(word, initial_x, initial_y)
        require(actual == expected, 'Literal current-source read or full endpoint corrupted')
        require(execute(word, *actual, reverse=True) == (initial_x, initial_y),
                'True chronological inverse did not restore arbitrary dirty fields')
    for omission in (1, 3):
        require(execute(words[1], initial_x, initial_y, omit=omission) != expected,
                'An unpaid source phase detour omission was accepted')
    # Enumerate every independent physical input column, in addition to all
    # arbitrary Gaussian fields above. Gaussian linearity transports i columns.
    columns = 0
    for role in range(2):
        for address in range(size):
            inputs = [[[ (Q(0), Q(0)) for field in range(4)] for unused in range(size)]
                      for unused_role in range(2)]
            inputs[role][address][0] = (Q(1), Q(0))
            require(execute(words[0], *inputs) == execute(words[1], *inputs),
                    'Complete physical source/target columns disagree')
            columns += 1
    original = [len(axes) for kind, axes, inverse in words[0] if kind == 'C' and axes]
    changed = [len(axes) for kind, axes, inverse in words[1] if kind == 'C' and axes]
    require(sum(changed) - sum(original) == 2, 'The source detour lost rank')
    return {'h': width, 'original_source_clock': original,
            'direct_full_gather_source_clock': changed, 'extra_rank_per_source': 2,
            'complete_physical_input_columns': columns,
            'arbitrary_Gaussian_component_values_forward_and_inverse': 4 * 2 * size * 8,
            'omitted_kernel_descent_and_full_return_rejected': True,
            'scope': 'Literal local source-clock and target shear, not a complete center/master operator'}


def conditional_profile(pair_count, omit_detour=False):
    h, v, q = 2 * pair_count, 32 * comb(pair_count, 5), 2 * pair_count * (pair_count - 1)
    calls = Counter({h: 6 * q, h - 1: 3 * v, 5: 3 * v, h - 6: 3 * v, 2: 2 * v})
    if not omit_detour:
        calls[1] += 6 * v
    R_side = 0
    for overlap in range(max(0, 10 - pair_count), 5):
        roles = comb(pair_count, 5) * comb(5, overlap) * (1 << overlap)
        cap, bucket = (6 if overlap == 0 else 5), 6 - overlap
        for width in (bucket, cap - bucket, h - cap):
            if width:
                calls[width] += 3 * roles
        R_side += roles
    W, m = 2 * v + q + R_side, 3 * h
    deficit = m * W - exact.rank(calls)
    expected = (2 * v if omit_detour else -4 * v) - 3 * q * h
    require(deficit == expected, 'Changed center/source/master rank telescope failed')
    return {'h': h, 'v': v, 'q': q, 'm': m, 'W': W, 'side_roles': R_side,
            'center_roles': q, 'child_multiplicities': dict(calls), 'deficit': deficit,
            'source_detour_paid': not omit_detour}


def ledger_case(pair_count):
    paid, fake = conditional_profile(pair_count), conditional_profile(pair_count, True)
    require(paid['deficit'] < 0, 'Naive full-source gather unexpectedly improved the first moment')
    paid_moment, fake_moment = exact.moment(paid, Q(1, 1000)), exact.moment(fake, Q(1, 1000))
    require(paid_moment[0] > 1, 'Proper children failed their first-moment exclusion')
    if pair_count == 12:
        require(fake_moment[1] < 1, 'The unpaid source detour negative no longer fakes improvement')
    return {'pair_count': pair_count, 'paid_profile': paid, 'unpaid_negative_profile': fake,
            'paid_moment_at_b_1e_minus3': [str(x) for x in paid_moment],
            'unpaid_negative_moment_at_b_1e_minus3': [str(x) for x in fake_moment],
            'scope': 'Conditional unchanged three-core/data/cap ledger with q direct full roots. No universal source-copy lower bound.'}


def run(task):
    return physical_case(task[1]) if task[0] == 'physical' else ledger_case(task[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'At least one worker required')
    source_paths = [Path(__file__).resolve(), Path(exact.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in source_paths}
    tasks = [('physical', 3), ('ledger', 12)] if args.bounded else (
        [('physical', h) for h in (3, 4, 5, 6)] + [('ledger', p) for p in (9, 12)])
    start, clock = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    if args.workers == 1:
        rows = [run(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(run, tasks))
    require(all(p.read_bytes() == value for p, value in frozen.items()), 'Frozen source closure changed')
    result = {'status': 'PASS paid current-source clock and scoped direct-gather exclusion',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - clock, 'workers': args.workers,
              'source_sha256': {p.name: sha256(value).hexdigest() for p, value in frozen.items()},
              'cases': rows,
              'scope': 'Exact local Gaussian phase/current-source controls and conditional naive-gather master obstruction. Joint/interleaved source-sharing, changed output adapters and a different master are outside.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds']}), flush=True)


if __name__ == '__main__':
    main()
