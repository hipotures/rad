#!/usr/bin/env python3
"""Paid alternating-complement scan adapter with existing complete guards.

The conditional native route is bit SWAP, one literal eight-rotation mask
plus current-address exceptional repair, and bit SWAP back. It realizes
P(a)=a XOR((a&1)(2^f-2)) before the natural scan. Four complete Gaussian
fields use the accepted literal seven-tape polynomial scan. Finite array
routes are exact oracles, not measured native tape routing times.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import time

import selected_polynomial_scan_tapes as poly
import native_gl_review as route


PINS = {'selected_polynomial_scan_tapes.py': '0dcd1ada09c55f74b5001d14d4ffcf89a8ef0589363535f37758cd071fb385c6',
        'selected_fiber_scan_tapes.py': '5565695705b0525861a136dd0ef74e6e0b28802916f080cdc3df015b2ee62e7a',
        'native_gl_review.py': '1ae606d030f1f71ebe2d2497399601f1cdc6e59aa4e3209527533ecf57432d19'}


def swap_bits(value, a, b):
    if ((value >> a) ^ (value >> b)) & 1:
        value ^= (1 << a) | (1 << b)
    return value


def spec(f, k, rho):
    poly.require(f >= 2 and k >= 1 and 0 <= rho < k, 'Two action bits and positive complete chunks required')
    band = f + 4
    target, companion, width = k, band * k, f * k
    pivot, borrowed = rho, (3 * band - 1) * k + rho
    selected = tuple(rho + j * k for j in range(f))
    used = tuple(sorted({pivot, borrowed} | set(range(target, target + width)) |
                        set(range(companion, companion + width))))
    poly.require(target + width <= companion and companion + width <= borrowed,
                 'Pivot/control, target and complete companion ranges are disjoint and ordered')
    poly.require((borrowed // k) == 3 * band - 1, 'The borrowed bit belongs to an existing terminal complete guard chunk')
    return {'f': f, 'k': k, 'rho': rho, 'address_chunks': 3 * f + 12,
            'address_bits': (3 * f + 12) * k, 'target_start': target, 'companion_start': companion,
            'range_width': width, 'active': f - 1, 'pivot_bit': pivot, 'borrowed_guard_bit': borrowed,
            'selected_positions': selected, 'relevant_positions': used,
            'compact_selected': tuple(used.index(bit) for bit in selected)}


def get_range(value, start, width):
    return value >> start & ((1 << width) - 1)


def put_range(value, changed, start, width):
    mask = ((1 << width) - 1) << start
    return (value & ~mask) | (changed << start)


def active_mask(value, s):
    control = value >> s['borrowed_guard_bit'] & 1
    return control * sum(1 << (s['rho'] + j * s['k']) for j in range(s['active']))


def rotate_address(value, s, event, undo=False):
    changed, direction, parity = event
    target, companion = s['target_start'], s['companion_start']
    width, k, rho = s['range_width'], s['k'], s['rho']
    mask = active_mask(value, s)
    here, other = (target, companion) if changed == 0 else (companion, target)
    other_value = get_range(value, other, width)
    offset = sum(1 << (rho + j * k) for j in range(s['active'])
                 if mask >> (rho + j * k) & 1 and (other_value >> (rho + j * k) & 1) == parity)
    changed_value = (get_range(value, here, width) + (-direction if undo else direction) * offset) % (1 << width)
    return put_range(value, changed_value, here, width)


def correction_address(value, s, undo=False):
    target, companion, width = s['target_start'], s['companion_start'], s['range_width']
    mask = active_mask(value, s)
    y, z = get_range(value, target, width), get_range(value, companion, width)
    k, f, rho = s['k'], s['active'] + 1, s['rho']
    if not undo:
        _, y, z = route.repair(mask, y, z, k, f, rho)
    elif route.bad(y, z, k, f, rho):
        # Forward repair is T*S^-1 on the invariant exceptional set.
        # Its actual inverse is S*T, not another forward repair.
        y ^= mask
        _, y, z = route.rotations(mask, y, z, k, f, rho)
    return put_range(put_range(value, y, target, width), z, companion, width)


def literal_address(value, s, undo=False, omit_repair=False, omit_last_swap=False):
    value = swap_bits(value, s['pivot_bit'], s['borrowed_guard_bit'])
    if undo and not omit_repair:
        value = correction_address(value, s, True)
    events = reversed(route.ROTATIONS) if undo else route.ROTATIONS
    for event in events:
        value = rotate_address(value, s, event, undo)
    if not undo and not omit_repair:
        value = correction_address(value, s)
    if not omit_last_swap:
        value = swap_bits(value, s['pivot_bit'], s['borrowed_guard_bit'])
    return value


def expected_address(value, s):
    return value ^ (sum(1 << bit for bit in s['selected_positions'][1:])
                    if value >> s['pivot_bit'] & 1 else 0)


def expand(value, positions):
    return sum(((value >> bit) & 1) << position for bit, position in enumerate(positions))


def compact(value, positions):
    return sum(((value >> position) & 1) << bit for bit, position in enumerate(positions))


def literal_payload(values, s, undo=False):
    """Each actual rotation/repair is replayed as a complete finite permutation."""
    positions = s['relevant_positions']

    def do(function):
        nonlocal values
        values = route.route(values, lambda index: compact(function(expand(index, positions)), positions))

    do(lambda address: swap_bits(address, s['pivot_bit'], s['borrowed_guard_bit']))
    if undo:
        do(lambda address: correction_address(address, s, True))
    for event in reversed(route.ROTATIONS) if undo else route.ROTATIONS:
        do(lambda address, event=event: rotate_address(address, s, event, undo))
    if not undo:
        do(lambda address: correction_address(address, s))
    do(lambda address: swap_bits(address, s['pivot_bit'], s['borrowed_guard_bit']))
    return values


def decode(cells, header, word):
    return poly.decode(cells, header, word, 4)


def order_reference(rows, selected, inverse=False, grouped=False):
    f, cube, groups = len(selected), 1 << len(selected), {}
    for address, row in enumerate(rows):
        a = compact(address, selected)
        key = address & ~sum(1 << bit for bit in selected)
        groups.setdefault(key, {})[a] = (address, row)
    output = [None] * len(rows)
    order = list(range(0, cube, 2)) + list(range(cube - 1, 0, -2)) if grouped else [
        a ^ ((cube - 2) if a & 1 else 0) for a in range(cube)]
    for group in groups.values():
        previous = [0] * 8
        for a in order:
            address, row = group[a]
            current = [x - y if inverse else x + y for x, y in zip(row, previous)]
            output[address] = current
            previous = row if inverse else current
    return output


def payload_probe(task):
    f, k, rho = task
    s = spec(f, k, rho)
    n, count = len(s['relevant_positions']), 1 << len(s['relevant_positions'])
    grid, word = 5, 5 + f + 3
    original = [[7 if field == 0 else (11 * index + 7 * field) % 31 - 15 for field in range(8)]
                for index in range(count)]
    before = literal_payload(original, s)
    expected_q = route.route(original, lambda index: compact(expected_address(expand(index, s['relevant_positions']), s), s['relevant_positions']))
    poly.require(before == expected_q and literal_payload(before, s, True) == original,
                 'All actual eight rotations, repair, bit swaps and their chronological inverse restore complete dirty payloads')
    mask = bytes([poly.START] + [poly.base.SELECTED if bit in s['compact_selected'] else poly.base.SPECTATOR
                                for bit in range(n)] + [poly.END])
    scanned, scan_stats = poly.scan(poly.encode(before, n, word), mask)
    actual = literal_payload(decode(scanned, n, word), s, True)
    expected = order_reference(original, s['compact_selected'])
    poly.require(actual == expected, 'The complete route-scan-route endpoint must be the alternating high-flux order')
    restore_before = literal_payload(actual, s)
    restored, inverse_stats = poly.scan(poly.encode(restore_before, n, word), mask, inverse=True)
    poly.require(literal_payload(decode(restored, n, word), s, True) == original,
                 'Full inverse scan and literal inverse routing restore every Gaussian component')
    witness = no_last = None
    for value in range(count):
        physical = expand(value, s['relevant_positions'])
        wanted = expected_address(physical, s)
        poly.require(literal_address(physical, s) == wanted and literal_address(wanted, s, True) == physical,
                     'Complete relevant address cube and literal inverse agree')
        if witness is None and literal_address(physical, s, omit_repair=True) != wanted:
            witness = {'before': physical, 'actual': literal_address(physical, s, omit_repair=True), 'expected': wanted}
        if no_last is None and literal_address(physical, s, omit_last_swap=True) != wanted:
            no_last = {'before': physical, 'actual': literal_address(physical, s, omit_last_swap=True), 'expected': wanted}
    poly.require(no_last is not None, 'Omitted swap restoration must discriminate in every complete cube')
    grouped = order_reference(original, s['compact_selected'], grouped=True)
    poly.require(grouped != expected, 'Grouped evens-first order must not be misidentified with the alternating high-flux order')
    return {'kind': 'complete_relevant_cube_and_Gaussian_pipeline', 'spec': s,
            'complete_relevant_addresses': count, 'Gaussian_fields': 4,
            'signed_component_values': 8 * count, 'literal_rotations_per_forward_pipeline': 16,
            'current_address_repairs_per_forward_pipeline': 2, 'fixed_two_digit_swaps': 4,
            'remaining_address_planes': 'Untouched identity factor by the exact read/write set; not materialized in this finite quotient',
            'omitted_repair_witness': witness, 'small_cube_needs_repair': witness is not None, 'omitted_last_swap_witness': no_last,
            'grouped_order_negative_rejected': True, 'natural_scan': scan_stats, 'inverse_scan': inverse_stats,
            'fractional_grid_bits': grid, 'reserved_component_width': word,
            'routing_is_finite_array_oracle_not_measured_tape_time': True}


def complete_address_probe(unused):
    f, k, rho = 4, 6, 1
    s = spec(f, k, rho)
    rng = random.Random(190941)
    mask = sum(1 << bit for bit in s['selected_positions'][1:])
    safe, exceptions, witness = 0, 0, None
    for index in range(4096):
        value = rng.randrange(1 << s['address_bits'])
        if index % 2 == 0:
            for start in (s['target_start'], s['companion_start']):
                for j in range(s['active']):
                    position = start + rho + j * k + 1
                    guards = 31 << position
                    value = (value & ~guards) | (rng.randrange(10, 22) << position)
        swapped = swap_bits(value, s['pivot_bit'], s['borrowed_guard_bit'])
        y, z = get_range(swapped, s['target_start'], s['range_width']), get_range(swapped, s['companion_start'], s['range_width'])
        bad = route.bad(y, z, k, s['active'] + 1, rho)
        safe += not bad
        exceptions += bad
        expected = value ^ (mask if value >> s['pivot_bit'] & 1 else 0)
        actual = literal_address(value, s)
        poly.require(actual == expected and literal_address(actual, s, True) == value,
                     'Full K-bit addresses and all unselected planes/guards must restore exactly')
        if not bad:
            poly.require(literal_address(value, s, omit_repair=True) == expected, 'Carry-free generalized mask word must already be exact')
        elif witness is None and literal_address(value, s, omit_repair=True) != expected:
            witness = {'before': value, 'uncorrected': literal_address(value, s, omit_repair=True), 'corrected': expected}
    poly.require(safe and exceptions and witness is not None, 'Both complete carry-free and repaired regimes must be tested')
    return {'kind': 'full_address_guard_lift', 'spec': s, 'seed': 190941,
            'complete_address_samples': 4096, 'safe_samples': safe, 'exception_samples': exceptions,
            'omitted_repair_witness': witness, 'fixed_guard_stock_no_new_address_bits': True}


def dispatch(task):
    return payload_probe(task) if task is not None else complete_address_probe(None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    poly.require(args.workers > 0, 'Positive workers required')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
    own = Path(__file__).resolve()
    paths = [own, Path(poly.__file__).resolve(), Path(poly.base.__file__).resolve(), Path(route.__file__).resolve()]
    before = {path.name: sha256(path.read_bytes()).hexdigest() for path in paths}
    poly.require(all(before[name] == digest for name, digest in PINS.items()), 'Every effective accepted helper must remain pinned')
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    tasks = [(2, 1, 0), None] if args.bounded else [(2, 1, 0), (3, 1, 0), (2, 2, 1), None]
    if args.workers == 1:
        rows = [dispatch(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(dispatch, tasks))
    poly.require(any(row.get('omitted_repair_witness') is not None for row in rows),
                 'At least one complete carry/repair case must reject omission; one-active-bit small cubes can already be exact')
    poly.require(all(sha256(path.read_bytes()).hexdigest() == before[path.name] for path in paths), 'All source bytes stay unchanged')
    result = {'status': 'PASS exact alternating high-flux selected scan adapter',
              'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.monotonic() - tick, 'workers': args.workers, 'bounded': args.bounded,
              'source_sha256': before, 'cases': rows,
              'scope': 'Literal finite packed address/payload word plus actual natural scan; routing-time bill conditional, no fast supplier or kappa'}
    if args.output:
        (args.output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'cases'}, sort_keys=True))


if __name__ == '__main__':
    main()
