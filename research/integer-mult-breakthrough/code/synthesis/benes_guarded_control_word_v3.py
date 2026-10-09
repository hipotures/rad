#!/usr/bin/env python3
"""Canonical same-column Benes masks with literal restored-slot routing.

Version two correctly implemented a changed within-band matching. This fresh
version reconstructs BOTH canonical control label orders and classifies each
canonical action column. The earlier sources and completed evidence stay fixed.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import time

TOPIC = Path(__file__).resolve().parents[2]
WORD = TOPIC / 'code/synthesis/benes_guarded_control_word.py'
WORD_SHA = 'b3f85a39a2c737dd91ba9888b6fe94c2b6da79a3e386c75ba8cddd9dfd169242'
if sha256(WORD.read_bytes()).hexdigest() != WORD_SHA:
    raise ValueError('The retained literal version-two word changed')
SPEC = importlib.util.spec_from_file_location('benes_literal_v2', WORD)
w = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)
b = w.b


def canonical_route(y, z, f, orders, pattern=(0, 0)):
    """Inputs are placed band coordinates; masks use canonical column labels."""
    if len(pattern) != 2 or any(bit not in (0, 1) for bit in pattern):
        raise ValueError('A fixed binary pattern for the two immutable controls is required')
    canonical_y = b.permute_bits(y, orders[1])
    canonical_z = b.permute_bits(z, orders[2])
    full = (1 << f) - 1
    active = (~((canonical_y ^ (full if pattern[0] else 0)) |
                (canonical_z ^ (full if pattern[1] else 0)))) & full
    compact = b.stable_compaction(active, f)
    inverse_action = b.inverse_permutation(orders[0])
    route = [inverse_action[compact[label]] for label in orders[0]]
    return active, compact, b.benes(route)


def canonical_stage(slots, f, K, stage_index, expected_distance, orders,
                    pattern=(0, 0), literal=True, wrong_decode=False, omit_repair=False):
    before_controls = slots[1:]
    positions = w.active_positions(f, K)
    permutation = b.alignment(f, expected_distance)
    inverse = b.inverse_permutation(permutation)
    x, y, z = w.linear_pair(slots, permutation, f, K, literal, omit_repair)
    decoded_y = w.extract_selected(y, positions)
    if not wrong_decode:
        decoded_y = b.permute_bits(decoded_y, permutation)
    decoded_z = w.extract_selected(z, positions)
    unused_active, unused_compact, stages = canonical_route(decoded_y, decoded_z, f, orders, pattern)
    distance, mask = stages[stage_index]
    if distance != expected_distance:
        raise AssertionError('Data-dependent masks changed the fixed Benes stage skeleton')
    half, g = f // 2, f // 4
    aligned_mask = sum(((mask >> inverse[j]) & 1) << j for j in range(half))
    quarter_width = (g + 1) * K
    quarter_mask = (1 << quarter_width) - 1
    quarters = [(x >> (j * quarter_width)) & quarter_mask for j in range(4)]
    local_positions = tuple(j * K + K - 1 for j in range(g))
    for target, donor, companion, which in w.QUARTER_EVENTS:
        if len({target, donor, companion}) != 3:
            raise AssertionError('A mask reads its target or borrowed full quarter')
        switch = (aligned_mask >> (which * g)) & ((1 << g) - 1)
        mask_word = w.scatter_selected(w.extract_selected(quarters[donor], local_positions) & switch,
                                      local_positions)
        companion_before = quarters[companion]
        if literal:
            quarters[target], quarters[companion] = w.packed_xor(mask_word, quarters[target],
                                                               quarters[companion], quarter_width,
                                                               K, omit_repair)
        else:
            quarters[target] ^= mask_word
        if not omit_repair and quarters[companion] != companion_before:
            raise AssertionError('A complete borrowed quarter failed to restore')
    x = sum(value << (j * quarter_width) for j, value in enumerate(quarters))
    result = w.linear_pair((x, y, z), inverse, f, K, literal, omit_repair)
    if not omit_repair and result[1:] != before_controls:
        raise AssertionError('A canonical mask stage changed an immutable control band')
    return result


def compact_address(address, f, K, inverse=False, pattern=(0, 0), literal=True,
                    wrong_decode=False, omit_repair=False):
    w.validate_shape(f, K)
    unused_swaps, orders = w.stock_layout(f)
    placed = w.apply_stock(address, f, K)
    width = (f + 4) * K
    mask = (1 << width) - 1
    slots = tuple((placed >> (role * width)) & mask for role in range(3))
    positions = w.active_positions(f, K)
    y, z = [w.extract_selected(value, positions) for value in slots[1:]]
    unused_active, unused_compact, stages = canonical_route(y, z, f, orders, pattern)
    chronology = list(enumerate(stages))
    if inverse:
        chronology.reverse()
    for index, (distance, unused_mask) in chronology:
        slots = canonical_stage(slots, f, K, index, distance, orders, pattern,
                                literal, wrong_decode, omit_repair)
    placed = sum(value << (role * width) for role, value in enumerate(slots))
    return w.apply_stock(placed, f, K, inverse=True)


def reference_compact(address, f, K, pattern=(0, 0)):
    x, y, z = [w.selected_canonical(address, f, K, role) for role in range(3)]
    full = (1 << f) - 1
    active = (~((y ^ (full if pattern[0] else 0)) |
                (z ^ (full if pattern[1] else 0)))) & full
    compact = b.stable_compaction(active, f)
    wanted = b.permute_bits(x, compact)
    positions = tuple(j * K + K - 1 for j in range(f))
    mask = sum(1 << p for p in positions)
    return (address & ~mask) | w.scatter_selected(wanted, positions)


def probe(task):
    f, K, seed, exhaustive = task
    started = time.monotonic()
    rng = random.Random(seed)
    n = (3 * f + 12) * K
    cases, decode_witness, repair_witness, label_witness = 0, None, None, None
    patterns = ((0, 0), (0, 1), (1, 0), (1, 1))
    for pattern in patterns:
        if exhaustive:
            values = ((x, y, z) for y in range(1 << f) for z in range(1 << f)
                      for x in range(1 << f))
        else:
            values = (tuple(rng.getrandbits(f) for unused in range(3)) for unused in range(64))
        for x, y, z in values:
            original = w.canonical_embed((x, y, z), f, K, rng.getrandbits(n - 3 * f))
            actual = compact_address(original, f, K, pattern=pattern)
            expected = reference_compact(original, f, K, pattern)
            if actual != expected or compact_address(actual, f, K, inverse=True, pattern=pattern) != original:
                raise AssertionError('The literal canonical pairing word or inverse failed')
            if decode_witness is None:
                wrong = compact_address(original, f, K, pattern=pattern, literal=False, wrong_decode=True)
                if wrong != expected:
                    decode_witness = dict(original=original, wrong=wrong, expected=expected, pattern=pattern)
            if repair_witness is None and cases < 32:
                wrong = compact_address(original, f, K, pattern=pattern, omit_repair=True)
                if wrong != expected:
                    repair_witness = dict(original=original, wrong=wrong, expected=expected, pattern=pattern)
            if label_witness is None:
                wrong = w.compact_address(original, f, K, pattern=pattern, literal=False)
                if wrong != expected:
                    label_witness = dict(original=original, wrong=wrong, expected=expected, pattern=pattern)
            cases += 1
    if any(witness is None for witness in (decode_witness, repair_witness, label_witness)):
        raise AssertionError('A canonical-pairing, transformed-control or repair negative did not fail')
    swaps, orders = w.stock_layout(f)
    return dict(status='PASS CANONICAL GUARDED BENES V3', f=f, K=K, seed=seed,
                selected_cube_exhaustive_each_fixed_pattern=exhaustive,
                fixed_patterns=patterns, complete_address_samples=cases,
                complete_address_bits=n, stock_swaps=len(swaps),
                label_orders=[list(order) for order in orders],
                stage_count=2 * (f.bit_length() - 1) - 1,
                packed_xor_words_per_stage=18, literal_rotations_per_stage=144,
                negative_controls=dict(omitted_decoding=decode_witness,
                                       omitted_exceptional_correction=repair_witness,
                                       omitted_canonical_control_label_reconstruction=label_witness),
                scope='Literal corrected canonical address word; no measured native tape time, Gaussian child or fast-supplier theorem',
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
               str(WORD.relative_to(TOPIC)): WORD_SHA,
               str(w.BASE.relative_to(TOPIC)): w.BASE_SHA}
    tasks = [(4, 1, 20261009111, True), (4, 2, 20261009112, True),
             (8, 6, 20261009113, False), (16, 6, 20261009114, False)]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=closure,
                    tasks=tasks, workers=args.workers, native_threads_each=1, stdlib_only=True,
                    resource_preflight=dict(aggregate_memory_bytes_upper=1 << 30),
                    repair='Reconstruct both stock control label orders before canonical same-column activity classification',
                    scope='Exact finite full-slot permutation chronology; native fees and recursive zeta supply remain conditional')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = []
        for row in pool.map(probe, tasks):
            rows.append(row)
            print(json.dumps({key: row[key] for key in ('status', 'f', 'K', 'complete_address_samples', 'seconds')}), flush=True)
    for name, digest in closure.items():
        if sha256((TOPIC / name).read_bytes()).hexdigest() != digest:
            raise AssertionError('An effective corrected-word source changed during the run')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=rows), indent=2) + '\n')


if __name__ == '__main__':
    main()
