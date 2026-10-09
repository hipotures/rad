#!/usr/bin/env python3
"""Complete Gaussian fibers after selected-action-only compaction.

Controls and every unselected guard coordinate stay fixed. This is an
independent finite address/operator checker and all-size shape model.
Its Python address indexing is a permutation oracle, not native routing.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from math import comb
from pathlib import Path
from random import Random
import time


SEED = 202610090741
ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
C = (Fraction(1, 2), Fraction(-1, 2))
INVERSE_C = (Fraction(1), Fraction(1))


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def power(c, exponent):
    value = ONE
    for _ in range(exponent):
        value = times(value, c)
    return value


def selected_position(slot, column, f, K):
    return (slot * f + column) * K + K - 1


def active_columns(address, h, f, K):
    return [column for column in range(f)
            if all(not address & (1 << selected_position(slot, column, f, K))
                   for slot in range(1, h))]


def compact(address, h, f, K, inverse=False, move_guard_negative=False):
    """Slot zero is action; higher slots are unchanged complete controls."""
    active = active_columns(address, h, f, K)
    active_set = set(active)
    order = active + [column for column in range(f) if column not in active_set]
    values = [bool(address & (1 << selected_position(0, column, f, K)))
              for column in range(f)]
    result = address
    for new, old in enumerate(order):
        target, source = (old, new) if inverse else (new, old)
        bit = 1 << selected_position(0, target, f, K)
        result = (result & ~bit) | (int(values[source]) * bit)
    if move_guard_negative and K > 1:
        # This forbidden crop is an observable full-cube error, even
        # though every selected bit and all activity counts can agree.
        result &= ~(1 << ((f - 1) * K))
    return result, len(active)


def accumulate(column, address, value):
    column[address] = plus(column.get(address, ZERO), value)
    if column[address] == ZERO:
        del column[address]


def direct_column(address, h, f, K, inverse=False):
    result = {address: ONE}
    coefficient = (-C[0], -C[1]) if inverse else C
    chronology = reversed(range(f)) if inverse else range(f)
    for column in chronology:
        bit = 1 << selected_position(0, column, f, K)
        for label, value in list(result.items()):
            if column in active_columns(label, h, f, K) and not label & bit:
                accumulate(result, label ^ bit, times(coefficient, value))
    return result


def tail_weight(address, width, K):
    return sum(bool(address & (1 << (column * K + K - 1))) for column in range(width))


def fiber_column(address, h, f, K, inverse=False, omit_gauges=False):
    transported, width = compact(address, h, f, K)
    entrance = ONE if omit_gauges else power(INVERSE_C, tail_weight(transported, width, K))
    result = {transported: entrance}
    sign = (-1, 0) if inverse else (1, 0)
    chronology = reversed(range(width)) if inverse else range(width)
    for column in chronology:
        bit = 1 << (column * K + K - 1)
        for label, value in list(result.items()):
            if not label & bit:
                accumulate(result, label ^ bit, times(sign, value))
    out = {}
    for label, value in result.items():
        if not omit_gauges:
            value = times(power(C, tail_weight(label, width, K)), value)
        recovered, count = compact(label, h, f, K, inverse=True)
        if count != width:
            raise AssertionError('a tail child altered its fixed activity controls')
        accumulate(out, recovered, value)
    return out


def direct_payload(payload, h, f, K, inverse=False):
    result = [list(fields) for fields in payload]
    coefficient = (-C[0], -C[1]) if inverse else C
    chronology = reversed(range(f)) if inverse else range(f)
    for column in chronology:
        bit = 1 << selected_position(0, column, f, K)
        for address in range(len(result)):
            if column in active_columns(address, h, f, K) and not address & bit:
                other = address ^ bit
                result[other] = [plus(a, times(coefficient, b))
                                 for a, b in zip(result[other], result[address])]
    return result


def fiber_payload(payload, h, f, K, fibers, inverse=False):
    M = len(payload)
    transported = [None] * M
    for address, fields in enumerate(payload):
        new, unused = compact(address, h, f, K)
        if transported[new] is not None:
            raise AssertionError('selected-action compaction is noninjective')
        transported[new] = list(fields)
    out = [None] * M
    for width, prefix in fibers:
        count = 1 << (width * K)
        start = prefix << (width * K)
        block = [[times(power(INVERSE_C, tail_weight(start + tail, width, K)), value)
                  for value in transported[start + tail]] for tail in range(count)]
        chronology = reversed(range(width)) if inverse else range(width)
        sign = (-1, 0) if inverse else (1, 0)
        for column in chronology:
            bit = 1 << (column * K + K - 1)
            for tail in range(count):
                if not tail & bit:
                    block[tail ^ bit] = [plus(a, times(sign, b))
                                        for a, b in zip(block[tail ^ bit], block[tail])]
        for tail, fields in enumerate(block):
            address = start + tail
            old, same_width = compact(address, h, f, K, inverse=True)
            if same_width != width or out[old] is not None:
                raise AssertionError('a whole tail fiber overlapped or left its prefix')
            out[old] = [times(power(C, tail_weight(address, width, K)), value) for value in fields]
    if any(fields is None for fields in out):
        raise AssertionError('a complete dirty Gaussian payload region was omitted')
    return out


def probe(task):
    h, f, K = task
    M = 1 << (h * f * K)
    action_mask = sum(1 << selected_position(0, j, f, K) for j in range(f))
    fibers = {}
    image = set()
    populations = [0] * (f + 1)
    for address in range(M):
        encoded, width = compact(address, h, f, K)
        recovered, count = compact(encoded, h, f, K, inverse=True)
        if recovered != address or count != width:
            raise AssertionError('the full selected-action compaction inverse failed')
        if (encoded ^ address) & ~action_mask:
            raise AssertionError('an immutable control or guard coordinate changed')
        image.add(encoded)
        fibers.setdefault((width, encoded >> (width * K)), []).append(encoded)
        populations[width] += 1
    if image != set(range(M)):
        raise AssertionError('the complete address volume is not preserved')
    prefix_ranges = []
    for (width, prefix), addresses in fibers.items():
        size = 1 << (width * K)
        start = prefix << (width * K)
        if set(addresses) != set(range(start, start + size)) or len(addresses) != size:
            raise AssertionError('a child fiber is not one complete aligned wK cube')
        prefix_ranges.append((start, start + size))
    frontier = 0
    for start, end in sorted(prefix_ranges):
        if start != frontier:
            raise AssertionError('disjoint complete cylinders did not partition the full stream')
        frontier = end
    if frontier != M:
        raise AssertionError('the disjoint cylinder partition ends early')
    for width, population in enumerate(populations):
        expected = comb(f, width) * 2 ** (f * (h * (K - 1) + 1)) * (2 ** (h - 1) - 1) ** (f - width)
        if population != expected:
            raise AssertionError('full-volume activity population has the wrong binomial law')
    nonzeros = 0
    for address in range(M):
        for inverse in (False, True):
            actual = fiber_column(address, h, f, K, inverse)
            expected = direct_column(address, h, f, K, inverse)
            if actual != expected:
                raise AssertionError('a complete forward/inverse physical basis column differs')
            nonzeros += len(actual)
    rng = Random(SEED + h * 10000 + f * 100 + K)
    payload = [[(Fraction(rng.randrange(-16, 17), 8), Fraction(rng.randrange(-16, 17), 8))
                for _ in range(4)] for _ in range(M)]
    actual = fiber_payload(payload, h, f, K, fibers)
    if actual != direct_payload(payload, h, f, K):
        raise AssertionError('the complete arbitrary Gaussian forward payload failed')
    if fiber_payload(actual, h, f, K, fibers, inverse=True) != payload:
        raise AssertionError('the actual Gaussian inverse did not restore every dirty field')
    if fiber_column(0, h, f, K, omit_gauges=True) == direct_column(0, h, f, K):
        raise AssertionError('omitted nonunit Gaussian weight gauges negative did not reject')
    guard_negative = None
    if K > 1:
        original = 1 << ((f - 1) * K)
        cropped, unused = compact(original, h, f, K, move_guard_negative=True)
        if cropped == compact(original, h, f, K)[0]:
            raise AssertionError('cropped unmoved guard negative did not reject')
        guard_negative = True
    return dict(h=h, columns=f, chunk_bits=K, complete_address_bits=h * f * K,
                complete_records=M, inverse_address_checks=M,
                selected_action_bits=f, all_other_address_bits_fixed=True,
                disjoint_complete_K_cylinders=len(fibers), full_cube_partition_checked=True,
                activity_populations=populations, child_widths=list(range(f + 1)),
                physical_basis_columns=2 * M, physical_nonzero_entries=nonzeros,
                full_arbitrary_Gaussian_fields=4 * M, payload_grid_bits=3,
                coefficient='(1-i)/2', actual_inverse_gauge='1+i',
                negative_controls=dict(omitted_weight_gauges=True, cropped_guard=guard_negative),
                native_initial_compaction=False, benes_or_producer_imports=False,
                no_added_address_axis=True, generic_non_power_of_two_shape_allowed=True,
                scope='Independent complete selected-action compaction shape and literal Gaussian operator. Native switch-network routing, guards and recursive supplier remain separate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    source = Path(__file__)
    source_sha = sha256(source.read_bytes()).hexdigest()
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(3, 2, 1), (3, 3, 1)] if args.bounded else [(3, 2, 1), (3, 3, 1), (3, 2, 2), (4, 1, 2)]
    if args.workers == 1:
        cases = list(map(probe, tasks))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    if sha256(source.read_bytes()).hexdigest() != source_sha:
        raise AssertionError('selected-action source changed during execution')
    result = dict(status='PASS COMPLETE SELECTED-ACTION GAUSSIAN CYLINDERS',
                  started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=source_sha, workers=args.workers, bounded=args.bounded,
                  cases=cases, seconds=time.monotonic() - started,
                  scope='Exact finite complete Gaussian operator and all-size cylinder shape, no paid native address permutation, Z supplier or kappa.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
                          full_addresses=sum(c['complete_records'] for c in cases),
                          physical_columns=sum(c['physical_basis_columns'] for c in cases),
                          Gaussian_fields=sum(c['full_arbitrary_Gaussian_fields'] for c in cases),
                          seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
