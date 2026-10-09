#!/usr/bin/env python3
"""Literal guarded XOR words for control-preserving Benes compaction.

This is an exact finite address-permutation oracle. Each XOR executes eight
modular rotations and its complete-record exceptional correction. Native tape
time still depends on the separately stated stream/mask/chunk-swap contracts.
The earlier endpoint-only source and its completed run are immutable inputs.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import time

TOPIC = Path(__file__).resolve().parents[2]
BASE = TOPIC / 'code/synthesis/benes_control_fiber_probe.py'
BASE_SHA = '0090d94c72943abc24ac77bf01db254134f5c4d069fce47e53c7747fc470b02f'
if sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('The immutable endpoint-only Benes source changed')
SPEC = importlib.util.spec_from_file_location('benes_endpoint_v1', BASE)
b = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(b)

ROTATIONS = ((0, -1, 0), (1, -1, 0), (0, 1, 0), (1, 1, 0),
             (1, 1, 1), (0, 1, 1), (1, -1, 1), (0, -1, 1))
QUARTER_EVENTS = ((0, 2, 1, 0), (1, 3, 0, 1), (2, 0, 3, 0),
                  (3, 1, 2, 1), (0, 2, 1, 0), (1, 3, 0, 1))


def validate_shape(f, K):
    if not isinstance(f, int) or f < 4 or f & (f - 1):
        raise ValueError('The present network requires a power-of-two f>=4')
    if not isinstance(K, int) or K < 1:
        raise ValueError('A positive complete chunk width is required')


@lru_cache(maxsize=32)
def stock_layout(f):
    """At most 60 full-K swaps place real guards and correct band roles.

    Canonical input has three f-chunk bands followed by twelve guard chunks.
    Within-band labels are tracked, rather than pretending a growing shuffle
    has been paid. The child compaction incorporates the action label order.
    """
    validate_shape(f, 1)
    g = f // 4
    labels = [(role, i) for role in range(3) for i in range(f)]
    labels += [(3, i) for i in range(12)]
    swaps = []
    for role in range(3):
        for q in range(4):
            target = (4 * role + q) * (g + 1) + g
            donor = labels.index((3, 4 * role + q))
            if donor != target:
                labels[target], labels[donor] = labels[donor], labels[target]
                swaps.append((target, donor))
    positions = [[(4 * role + q) * (g + 1) + j
                  for q in range(4) for j in range(g)] for role in range(3)]
    expected = {p: role for role, band in enumerate(positions) for p in band}
    wrong = [p for p, role in expected.items() if labels[p][0] != role]
    if len(wrong) > 48:
        raise AssertionError('The conservative all-size band mismatch bound failed')
    for target in wrong:
        role = expected[target]
        if labels[target][0] == role:
            continue
        donor = next(p for p in wrong
                     if labels[p][0] == role and expected[p] != role)
        labels[target], labels[donor] = labels[donor], labels[target]
        swaps.append((target, donor))
    if len(swaps) > 60 or any(labels[p][0] != role for p, role in expected.items()):
        raise AssertionError('The constant stock placement did not bind all band roles')
    orders = tuple(tuple(labels[p][1] for p in band) for band in positions)
    if any(sorted(order) != list(range(f)) for order in orders):
        raise AssertionError('A complete active band label was lost')
    return tuple(swaps), orders


def swap_chunks(address, first, second, K):
    mask = (1 << K) - 1
    difference = ((address >> (first * K)) ^ (address >> (second * K))) & mask
    return address ^ (difference << (first * K)) ^ (difference << (second * K))


def apply_stock(address, f, K, inverse=False):
    swaps, unused = stock_layout(f)
    for first, second in (reversed(swaps) if inverse else swaps):
        address = swap_chunks(address, first, second, K)
    return address


def extract_selected(slot, positions):
    return sum(((slot >> position) & 1) << i for i, position in enumerate(positions))


def scatter_selected(value, positions):
    return sum(((value >> i) & 1) << position for i, position in enumerate(positions))


def active_positions(f, K):
    g = f // 4
    return tuple((q * (g + 1) + j) * K + K - 1 for q in range(4) for j in range(g))


def rotations(mask, target, companion, width, K, inverse=False):
    positions = range(K - 1, width - K, K)
    modulus = 1 << width
    steps = reversed(ROTATIONS) if inverse else ROTATIONS
    for changed, direction, parity in steps:
        other = companion if changed == 0 else target
        offset = sum(1 << p for p in positions
                     if mask >> p & 1 and (other >> p & 1) == parity)
        sign = -direction if inverse else direction
        if changed == 0:
            target = (target + sign * offset) % modulus
        else:
            companion = (companion + sign * offset) % modulus
    return target, companion


def exceptional(target, companion, width, K):
    guard_mask = (1 << (K - 1)) - 1
    return any(not 10 <= ((value >> (p + 1)) & guard_mask) <= (1 << (K - 1)) - 11
               for value in (target, companion) for p in range(K - 1, width - K, K))


def packed_xor(mask, target, companion, width, K, omit_repair=False):
    if mask < 0 or mask >> width:
        raise ValueError('The XOR mask lies outside its complete slot')
    allowed = sum(1 << p for p in range(K - 1, width - K, K))
    if mask & ~allowed:
        raise ValueError('The XOR mask includes a spectator or terminal guard')
    initial = (target, companion)
    actual = rotations(mask, target, companion, width, K)
    if exceptional(*actual, width, K) and not omit_repair:
        before = rotations(mask, *actual, width, K, inverse=True)
        actual = (before[0] ^ mask, before[1])
    if not omit_repair and actual != (initial[0] ^ mask, initial[1]):
        raise AssertionError('A literal repaired mask word missed its complete endpoint')
    return actual


def linear_pair(slots, permutation, f, K, literal=True, omit_repair=False):
    """Six words act on complete bands; the third complete band is borrowed."""
    slots = list(slots)
    positions = active_positions(f, K)
    width = (f + 4) * K
    inverse = b.inverse_permutation(permutation)
    identity = list(range(f))
    events = ((1, 0, identity), (0, 1, identity), (1, 0, identity),
              (1, 0, permutation), (0, 1, inverse), (1, 0, permutation))
    for source, target, route in events:
        companion = 2
        mask = scatter_selected(b.permute_bits(extract_selected(slots[source], positions), route), positions)
        control_before = slots[source]
        companion_before = slots[companion]
        if literal:
            slots[target], slots[companion] = packed_xor(mask, slots[target], slots[companion],
                                                       width, K, omit_repair)
        else:
            slots[target] ^= mask
        if not omit_repair and (slots[source] != control_before or slots[companion] != companion_before):
            raise AssertionError('A complete linear-pair control or companion changed')
    return tuple(slots)


def desired_route(y, z, f, action_order, pattern=(0, 0)):
    full = (1 << f) - 1
    active = (~((y ^ (full if pattern[0] else 0)) |
                (z ^ (full if pattern[1] else 0)))) & full
    compact = b.stable_compaction(active, f)
    inverse_order = b.inverse_permutation(action_order)
    route = [inverse_order[target] for target in compact]
    return active, route, b.benes(route)


def guarded_stage(slots, f, K, stage_index, expected_distance, action_order,
                  pattern=(0, 0), literal=True, wrong_decode=False, omit_repair=False):
    """Recompute each stage mask from the actual currently immutable controls."""
    original_controls = slots[1:]
    positions = active_positions(f, K)
    permutation = b.alignment(f, expected_distance)
    inverse = b.inverse_permutation(permutation)
    x, y, z = linear_pair(slots, permutation, f, K, literal, omit_repair)
    decoded_y = extract_selected(y, positions)
    if not wrong_decode:
        decoded_y = b.permute_bits(decoded_y, permutation)
    decoded_z = extract_selected(z, positions)
    unused, unused_route, stages = desired_route(decoded_y, decoded_z, f, action_order, pattern)
    distance, mask = stages[stage_index]
    if distance != expected_distance:
        raise AssertionError('Data-dependent routing changed the fixed Benes stage skeleton')
    half, g = f // 2, f // 4
    aligned_mask = sum(((mask >> inverse[j]) & 1) << j for j in range(half))
    quarter_width = (g + 1) * K
    quarter_mask = (1 << quarter_width) - 1
    quarters = [(x >> (j * quarter_width)) & quarter_mask for j in range(4)]
    local_positions = tuple(j * K + K - 1 for j in range(g))
    for target, donor, companion, which in QUARTER_EVENTS:
        if len({target, donor, companion}) != 3:
            raise AssertionError('A switch mask illegally reads its target or companion')
        switch = (aligned_mask >> (which * g)) & ((1 << g) - 1)
        mask_word = scatter_selected(extract_selected(quarters[donor], local_positions) & switch,
                                     local_positions)
        donor_before, companion_before = quarters[donor], quarters[companion]
        if literal:
            quarters[target], quarters[companion] = packed_xor(mask_word, quarters[target],
                                                             quarters[companion], quarter_width,
                                                             K, omit_repair)
        else:
            quarters[target] ^= mask_word
        if not omit_repair and (quarters[donor] != donor_before or quarters[companion] != companion_before):
            raise AssertionError('A donor or borrowed full quarter changed at its endpoint')
    x = sum(value << (j * quarter_width) for j, value in enumerate(quarters))
    result = linear_pair((x, y, z), inverse, f, K, literal, omit_repair)
    if not omit_repair and result[1:] != original_controls:
        raise AssertionError('The complete switch stage did not restore its original controls')
    return result


def compact_address(address, f, K, inverse=False, pattern=(0, 0), literal=True,
                    wrong_decode=False, omit_repair=False):
    validate_shape(f, K)
    unused_swaps, orders = stock_layout(f)
    placed = apply_stock(address, f, K)
    width = (f + 4) * K
    slot_mask = (1 << width) - 1
    slots = tuple((placed >> (role * width)) & slot_mask for role in range(3))
    positions = active_positions(f, K)
    y, z = [extract_selected(value, positions) for value in slots[1:]]
    unused_active, unused_route, stages = desired_route(y, z, f, orders[0], pattern)
    chronology = list(enumerate(stages))
    if inverse:
        chronology.reverse()
    for index, (distance, unused_mask) in chronology:
        slots = guarded_stage(slots, f, K, index, distance, orders[0], pattern,
                              literal, wrong_decode, omit_repair)
    placed = sum(value << (role * width) for role, value in enumerate(slots))
    return apply_stock(placed, f, K, inverse=True)


def selected_canonical(address, f, K, role):
    return extract_selected(address >> (role * f * K), tuple(j * K + K - 1 for j in range(f)))


def canonical_embed(values, f, K, spectator):
    n = (3 * f + 12) * K
    positions = tuple((role * f + j) * K + K - 1 for role in range(3) for j in range(f))
    selected = set(positions)
    address, bit = 0, 0
    for position in range(n):
        if position not in selected:
            address |= ((spectator >> bit) & 1) << position
            bit += 1
    for role, value in enumerate(values):
        address |= scatter_selected(value, positions[role * f:(role + 1) * f])
    return address


def reference_compact(address, f, K, pattern=(0, 0)):
    unused, orders = stock_layout(f)
    canonical = [selected_canonical(address, f, K, role) for role in range(3)]
    oriented = [sum(((canonical[role] >> label) & 1) << i for i, label in enumerate(orders[role]))
                for role in range(3)]
    unused, route, unused_stages = desired_route(oriented[1], oriented[2], f, orders[0], pattern)
    transported = b.permute_bits(oriented[0], route)
    wanted = sum(((transported >> i) & 1) << label for i, label in enumerate(orders[0]))
    positions = tuple(j * K + K - 1 for j in range(f))
    mask = sum(1 << p for p in positions)
    return (address & ~mask) | scatter_selected(wanted, positions)


def endpoint_probe(task):
    f, K, seed, exhaustive = task
    started = time.monotonic()
    rng = random.Random(seed)
    validate_shape(f, K)
    if exhaustive:
        values = ((x, y, z) for y in range(1 << f) for z in range(1 << f)
                  for x in range(1 << f))
    else:
        values = (tuple(rng.getrandbits(f) for unused in range(3)) for unused in range(256))
    n = (3 * f + 12) * K
    cases, decode_witness, repair_witness = 0, None, None
    for x, y, z in values:
        pattern = (cases & 1, (cases >> 1) & 1)
        original = canonical_embed((x, y, z), f, K, rng.getrandbits(n - 3 * f))
        actual = compact_address(original, f, K, pattern=pattern)
        expected = reference_compact(original, f, K, pattern)
        if actual != expected or compact_address(actual, f, K, inverse=True, pattern=pattern) != original:
            raise AssertionError('The literal complete guarded word or true inverse failed')
        if decode_witness is None:
            wrong = compact_address(original, f, K, pattern=pattern, literal=False, wrong_decode=True)
            if wrong != expected:
                decode_witness = dict(original=original, wrong=wrong, expected=expected, pattern=pattern)
        if repair_witness is None and cases < 32:
            wrong = compact_address(original, f, K, pattern=pattern, omit_repair=True)
            if wrong != expected:
                repair_witness = dict(original=original, wrong=wrong, expected=expected, pattern=pattern)
        cases += 1
    if decode_witness is None or repair_witness is None:
        raise AssertionError('A required transformed-control or exceptional-repair negative did not fail')
    swaps, orders = stock_layout(f)
    return dict(status='PASS LITERAL GUARDED BENES WORD', f=f, K=K, seed=seed,
                selected_cube_exhaustive=exhaustive, complete_address_samples=cases,
                complete_address_bits=n, quarter_count=12, active_chunks_each_quarter=f // 4,
                real_guard_chunks_each_quarter=1, stock_full_chunk_swaps=len(swaps),
                action_order=list(orders[0]), stage_count=2 * (f.bit_length() - 1) - 1,
                packed_xor_words_per_stage=18, literal_rotations_per_stage=144,
                native_fixed_tape_time_measured=False, child_operator_verified=False,
                negative_controls=dict(omitted_control_decoding=decode_witness,
                                       omitted_exceptional_correction=repair_witness),
                seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('A positive worker count is required')
    args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve()
    closure = {str(source.relative_to(TOPIC)): sha256(source.read_bytes()).hexdigest(),
               str(BASE.relative_to(TOPIC)): BASE_SHA}
    tasks = [(4, 1, 20261009101, True), (4, 2, 20261009102, True),
             (8, 6, 20261009103, False), (16, 6, 20261009104, False)]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=closure,
                    tasks=tasks, workers=args.workers, native_threads_each=1,
                    stdlib_only=True, resource_preflight=dict(aggregate_memory_bytes_upper=1 << 30),
                    scope='Literal finite rotations, correction, actual control masks and complete guard layout; conditional native stream cost, no fast zeta supplier or exponent')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = []
        for row in pool.map(endpoint_probe, tasks):
            results.append(row)
            print(json.dumps({key: row[key] for key in ('status', 'f', 'K', 'complete_address_samples', 'seconds')}), flush=True)
    for name, digest in closure.items():
        if sha256((TOPIC / name).read_bytes()).hexdigest() != digest:
            raise AssertionError('An effective literal-word source changed during the run')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=results), indent=2) + '\n')


if __name__ == '__main__':
    main()
