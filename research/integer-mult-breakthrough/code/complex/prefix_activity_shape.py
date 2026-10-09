#!/usr/bin/env python3
"""Complete-K-chunk activity prefix shape and literal operator controls.

This is an exact address permutation, variable-child block shape and full
payload operator model. It does not execute a fast tape permutation or
provide a native zeta supplier. No address chunk or guard bit is added.
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


C = (Fraction(1, 2), Fraction(-1, 2))
C_INVERSE = (Fraction(1), Fraction(1))
ONE = (Fraction(1), Fraction(0))
ZERO = (Fraction(0), Fraction(0))
SEED = 202610090640


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def multiply(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def power(value, exponent):
    result = ONE
    for _ in range(exponent):
        result = multiply(result, value)
    return result


def digit(address, slot, column, f, K):
    return (address >> ((slot * f + column) * K)) & ((1 << K) - 1)


def encode(address, h, f, K, crop_active_target=False):
    prefix, tail = [], []
    selected = 1 << (K - 1)
    for column in range(f):
        controls = [digit(address, slot, column, f, K) for slot in range(h - 1)]
        target = digit(address, h - 1, column, f, K)
        prefix.extend(controls)
        if all(not value & selected for value in controls):
            tail.append(0 if crop_active_target else target)
        else:
            prefix.append(target)
    value = 0
    for chunk in prefix + tail:
        value = (value << K) | chunk
    prefix_value = value >> (len(tail) * K)
    return value, len(tail), prefix_value


def decode(encoded, h, f, K):
    length = h * f
    chunks = [(encoded >> ((length - 1 - index) * K)) & ((1 << K) - 1)
              for index in range(length)]
    selected = 1 << (K - 1)
    old = [0] * length
    active = []
    pointer = 0
    for column in range(f):
        controls = chunks[pointer:pointer + h - 1]
        pointer += h - 1
        for slot, value in enumerate(controls):
            old[slot * f + column] = value
        if all(not value & selected for value in controls):
            active.append(column)
        else:
            old[(h - 1) * f + column] = chunks[pointer]
            pointer += 1
    if pointer != length - len(active):
        raise AssertionError('prefix decoder did not leave exactly the active whole target chunks')
    for column, target in zip(active, chunks[pointer:]):
        old[(h - 1) * f + column] = target
    address = sum(value << (index * K) for index, value in enumerate(old))
    return address, len(active)


def eligible(address, h, f, K, column):
    return all(not digit(address, slot, column, f, K) & (1 << (K - 1))
               for slot in range(h - 1))


def accumulate(values, index, value):
    values[index] = add(values.get(index, ZERO), value)
    if values[index] == ZERO:
        del values[index]


def direct_column(address, h, f, K, inverse=False):
    values = {address: ONE}
    coefficient = (-C[0], -C[1]) if inverse else C
    columns = reversed(range(f)) if inverse else range(f)
    for column in columns:
        target = 1 << (((h - 1) * f + column) * K + K - 1)
        for index, value in list(values.items()):
            if eligible(index, h, f, K, column) and not index & target:
                accumulate(values, index ^ target, multiply(coefficient, value))
    return values


def tail_weight(encoded, active, K):
    return sum(bool(encoded & (1 << (column * K + K - 1))) for column in range(active))


def child_column(address, h, f, K, inverse=False, omit_gauges=False):
    encoded, active, _ = encode(address, h, f, K)
    entrance = ONE if omit_gauges else power(C_INVERSE, tail_weight(encoded, active, K))
    values = {encoded: entrance}
    sign = (-1, 0) if inverse else (1, 0)
    bits = reversed(range(active)) if inverse else range(active)
    for column in bits:
        target = 1 << (column * K + K - 1)
        for index, value in list(values.items()):
            if not index & target:
                accumulate(values, index ^ target, multiply(sign, value))
    physical = {}
    for index, value in values.items():
        if not omit_gauges:
            value = multiply(power(C, tail_weight(index, active, K)), value)
        old, count = decode(index, h, f, K)
        if count != active:
            raise AssertionError('child changed its invariant activity prefix')
        accumulate(physical, old, value)
    return physical


def direct_payload(payload, h, f, K, inverse=False):
    out = [list(fields) for fields in payload]
    coefficient = (-C[0], -C[1]) if inverse else C
    columns = reversed(range(f)) if inverse else range(f)
    for column in columns:
        target = 1 << (((h - 1) * f + column) * K + K - 1)
        for address in range(len(out)):
            if not address & target and eligible(address, h, f, K, column):
                other = address ^ target
                out[other] = [add(a, multiply(coefficient, b))
                              for a, b in zip(out[other], out[address])]
    return out


def child_payload(payload, h, f, K, groups, inverse=False):
    M = len(payload)
    encoded_payload = [None] * M
    for address, fields in enumerate(payload):
        encoded, _, _ = encode(address, h, f, K)
        encoded_payload[encoded] = list(fields)
    out = [None] * M
    for (active, prefix), _ in groups.items():
        size = 1 << (active * K)
        start = prefix << (active * K)
        values = [[multiply(power(C_INVERSE, tail_weight(start + tail, active, K)), value)
                   for value in encoded_payload[start + tail]] for tail in range(size)]
        columns = reversed(range(active)) if inverse else range(active)
        sign = (-1, 0) if inverse else (1, 0)
        for column in columns:
            target = 1 << (column * K + K - 1)
            for tail in range(size):
                if not tail & target:
                    other = tail ^ target
                    values[other] = [add(a, multiply(sign, b)) for a, b in zip(values[other], values[tail])]
        for tail, fields in enumerate(values):
            address = start + tail
            scaled = [multiply(power(C, tail_weight(address, active, K)), value) for value in fields]
            old, count = decode(address, h, f, K)
            if count != active:
                raise AssertionError('payload output left its activity block')
            out[old] = scaled
    if any(value is None for value in out):
        raise AssertionError('complete arbitrary payload stream was cropped')
    return out


def probe(task):
    h, f, K = task
    M = 1 << (h * f * K)
    groups = {}
    images = set()
    records_by_active = [0] * (f + 1)
    for address in range(M):
        encoded, active, prefix = encode(address, h, f, K)
        recovered, other_active = decode(encoded, h, f, K)
        if recovered != address or other_active != active:
            raise AssertionError('whole-K prefix codec did not recover an original address')
        images.add(encoded)
        records_by_active[active] += 1
        groups.setdefault((active, prefix), []).append(encoded)
    if len(images) != M or min(images) != 0 or max(images) != M - 1:
        raise AssertionError('prefix route changes the complete address population')
    for (active, prefix), addresses in groups.items():
        size = 1 << (active * K)
        start = prefix << (active * K)
        if len(addresses) != size or set(addresses) != set(range(start, start + size)):
            raise AssertionError('an activity group is not one complete aligned child cube')
    D = 1 << h
    for active, records_count in enumerate(records_by_active):
        expected_numerator = M * comb(f, active) * 2 ** active * (D - 2) ** (f - active)
        if expected_numerator != records_count * D ** f:
            raise AssertionError('whole-record activity law is not the declared binomial law')
    forward_entries = 0
    inverse_entries = 0
    for address in range(M):
        direct = direct_column(address, h, f, K)
        child = child_column(address, h, f, K)
        if direct != child:
            raise AssertionError('a complete sparse physical forward column differs from child shape')
        direct_inverse = direct_column(address, h, f, K, inverse=True)
        child_inverse = child_column(address, h, f, K, inverse=True)
        if direct_inverse != child_inverse:
            raise AssertionError('a complete sparse physical inverse column differs from child shape')
        forward_entries += len(direct)
        inverse_entries += len(direct_inverse)
    rng = Random(SEED + h * 10000 + f * 100 + K)
    payload = [[(Fraction(rng.randrange(-8, 9), 4), Fraction(rng.randrange(-8, 9), 4))
                for _ in range(4)] for _ in range(M)]
    actual = child_payload(payload, h, f, K, groups)
    expected = direct_payload(payload, h, f, K)
    if actual != expected or child_payload(actual, h, f, K, groups, inverse=True) != payload:
        raise AssertionError('full four-field arbitrary Gaussian payload or true inverse failed')
    if direct_payload(expected, h, f, K, inverse=True) != payload:
        raise AssertionError('direct inverse did not restore all raw fields')
    if direct_column(0, h, f, K) == child_column(0, h, f, K, omit_gauges=True):
        raise AssertionError('omitted nonunit child gauges negative did not reject')
    target_bit = 1 << (((h - 1) * f) * K + K - 1)
    if encode(0, h, f, K, crop_active_target=True)[0] != encode(target_bit, h, f, K, crop_active_target=True)[0]:
        raise AssertionError('cropped active target negative failed to expose noninjectivity')
    guard_negative = None
    if K > 1:
        guard_bit = 1 << (((h - 1) * f) * K)
        cropped, _, _ = encode(guard_bit, h, f, K, crop_active_target=True)
        if decode(cropped, h, f, K)[0] == guard_bit:
            raise AssertionError('cropped complete target guard negative did not reject')
        guard_negative = True
    return dict(h=h, columns=f, chunk_bits=K, selected_width=h * f,
                complete_address_bits=h * f * K, complete_records=M,
                complete_address_inverse_checks=M, native_route_executed=False,
                child_groups=len(groups), child_group_records_by_active=records_by_active,
                child_full_chunk_widths=list(range(f + 1)),
                complete_sparse_forward_basis_columns=M,
                complete_sparse_inverse_basis_columns=M,
                nonzero_forward_matrix_entries=forward_entries,
                nonzero_inverse_matrix_entries=inverse_entries,
                dense_payload_Gaussian_fields=4 * M,
                dense_payload_fractional_grid_bits=2,
                coefficient='(1-i)/2', coefficient_inverse='1+i',
                affine_orienting_route_not_assumed=True,
                all_original_spectator_guard_bits_preserved=True,
                full_cube_volume_unchanged=True,
                negative_controls=dict(omitted_child_gauges=True,
                                       cropped_active_target=True,
                                       cropped_active_guard=guard_negative),
                scope='Full exact shape and physical operator, with whole K chunks and arbitrary Gaussian fields. Python indexing is an oracle; fast fixed-tape routing/group dispatch/guard endpoints/precision recurrence remain unproved.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    source = sha256(Path(__file__).read_bytes()).hexdigest()
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(3, 1, 1), (3, 2, 1)] if args.bounded else [(3, 1, 1), (3, 2, 1), (3, 1, 2), (3, 2, 2)]
    if args.workers == 1:
        cases = list(map(probe, tasks))
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    if sha256(Path(__file__).read_bytes()).hexdigest() != source:
        raise AssertionError('prefix shape source changed during run')
    result = dict(status='PASS EXACT COMPLETE-K ACTIVITY PREFIX SHAPE AND OPERATORS',
                  source_sha256=source, started_utc=started_utc,
                  completed_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                  bounded=args.bounded, cases=cases, seconds=time.monotonic() - started,
                  scope='All-volume literal prefix permutation and child shape, no paid native routing, faster zeta supplier or kappa.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], cases=len(cases),
                          basis_columns=sum(c['complete_sparse_forward_basis_columns'] + c['complete_sparse_inverse_basis_columns'] for c in cases),
                          dense_Gaussian_fields=sum(c['dense_payload_Gaussian_fields'] for c in cases),
                          seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
