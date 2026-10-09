#!/usr/bin/env python3
"""Exact fixed-dimensional reversible permutations with a restored dirty bit.

Only NOT, CNOT and Toffoli gates are emitted. Native placement of their data,
borrowed and routing-companion slots is a separate charged contract.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import time


def controlled_word(controls, target, borrowed):
    if len(set(controls + (target, borrowed))) != len(controls) + 2:
        raise ValueError('Controls, target and borrowed bit must be distinct')
    if len(controls) <= 2:
        return [tuple(controls) + (target,)]
    split = (len(controls) + 1) // 2
    left, right = controls[:split], controls[split:]
    a = controlled_word(left, borrowed, target)
    b = controlled_word((borrowed,) + right, target, left[0])
    return a + b + a + b


def adjacent_word(u, v, h):
    difference = u ^ v
    if difference.bit_count() != 1:
        raise ValueError('Adjacent transposition needs one changed data bit')
    target = difference.bit_length() - 1
    controls = tuple(bit for bit in range(h) if bit != target)
    flips = [(bit,) for bit in controls if not (u >> bit) & 1]
    return flips + controlled_word(controls, target, h) + list(reversed(flips))


def transposition_word(u, v, h):
    if u == v:
        return []
    path = [u]
    for bit in range(h):
        if ((u ^ v) >> bit) & 1:
            path.append(path[-1] ^ (1 << bit))
    edges = [adjacent_word(a, b, h) for a, b in zip(path, path[1:])]
    return [gate for edge in edges + list(reversed(edges[:-1])) for gate in edge]


def permutation_word(permutation):
    size = len(permutation)
    h = (size - 1).bit_length()
    if size != 1 << h or sorted(permutation) != list(range(size)):
        raise ValueError('A complete power-of-two address permutation is required')
    seen, word, transpositions = set(), [], 0
    for origin in range(size):
        if origin in seen:
            continue
        cycle, current = [], origin
        while current not in seen:
            cycle.append(current)
            seen.add(current)
            current = permutation[current]
        if current != origin:
            raise AssertionError('Permutation cycles did not close')
        for partner in cycle[1:]:
            word += transposition_word(origin, partner, h)
            transpositions += 1
    return word, transpositions


def execute(address, word):
    for gate in word:
        if all((address >> control) & 1 for control in gate[:-1]):
            address ^= 1 << gate[-1]
    return address


def field_orders(h):
    polynomial = {3: 11, 4: 19, 5: 37}[h]
    size = 1 << h
    powers, value = [], 1
    for unused in range(size - 1):
        powers.append(value)
        value <<= 1
        if value & size:
            value ^= polynomial
    if value != 1 or sorted(powers) != list(range(1, size)):
        raise ValueError('The retained primitive polynomial did not enumerate the field')
    return {'zero-last': powers + [0], 'zero-first': [0] + powers}, polynomial


def payload_fields(size):
    return [[(address * 17 + field * 7 - 31,
              address * 11 - field * 13 + 19) for address in range(size)]
            for field in range(4)]


def probe(h):
    started = time.monotonic()
    orders, polynomial = field_orders(h)
    random_order = list(range(1 << h))
    random.Random(202610090354 + h).shuffle(random_order)
    orders['seeded-arbitrary'] = random_order
    orders['single-transposition'] = list(range(1 << h))
    orders['single-transposition'][0], orders['single-transposition'][-1] = (1 << h) - 1, 0
    rows = []
    for name, permutation in orders.items():
        word, count = permutation_word(permutation)
        size = 1 << (h + 1)
        target = [permutation[a & ((1 << h) - 1)] | (a & (1 << h)) for a in range(size)]
        actual = [execute(a, word) for a in range(size)]
        if actual != target:
            raise AssertionError('Complete borrowed-bit address permutation failed')
        if [execute(a, list(reversed(word))) for a in actual] != list(range(size)):
            raise AssertionError('Literal reverse gates did not restore every address')
        moved, peak_borrowed = 0, 0
        for a in range(size):
            current = a
            for gate in word:
                current = execute(current, [gate])
                moved += bool((current ^ a) & (1 << h))
                peak_borrowed |= current & (1 << h)
        fields = payload_fields(size)
        digest = sha256()
        for values in fields:
            output = [None] * size
            for a, value in enumerate(values):
                output[execute(a, word)] = value
            expected = [None] * size
            for a, value in enumerate(values):
                expected[target[a]] = value
            if output != expected:
                raise AssertionError('Complete four-field payload scatter changed a value')
            digest.update(str(output).encode())
        corrupt = word[:-1]
        if all(execute(a, corrupt) == target[a] for a in range(size)):
            raise AssertionError('An omitted physical gate did not discriminate')
        rows.append(dict(name=name, complete_address_columns=size,
                         complete_payload_records=4 * size, transpositions=count,
                         NOT=sum(len(g) == 1 for g in word),
                         CNOT=sum(len(g) == 2 for g in word),
                         Toffoli=sum(len(g) == 3 for g in word), total_gates=len(word),
                         arbitrary_borrowed_bit_restored=True,
                         temporary_borrowed_bit_changes=moved,
                         omitted_last_gate_detected=True, output_sha256=digest.hexdigest(),
                         word_sha256=sha256(json.dumps(word).encode()).hexdigest()))
    controlled = []
    for k in range(3, h + 1):
        controls = tuple(range(k))
        word = controlled_word(controls, k, k + 1)
        for a in range(1 << (k + 2)):
            expected = a ^ ((1 << k) if a & ((1 << k) - 1) == (1 << k) - 1 else 0)
            if execute(a, word) != expected:
                raise AssertionError('The recursive dirty-bit controlled word failed')
        controlled.append(dict(controls=k, actual_three_bit_gates=len(word),
                               complete_addresses=1 << (k + 2)))
    return dict(status='PASS EXACT DIRTY-BIT PERMUTATION WORDS', h=h,
                primitive_polynomial=polynomial, cases=rows,
                controlled_NOT_words=controlled, seconds=time.monotonic() - started,
                scope='Complete fixed-h Boolean words and payload reference scatter. One restored dirty address bit and native gate slots/companions remain charged; no tape routing time or field-kernel arithmetic theorem.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or (args.output and args.output.exists()):
        raise ValueError('Positive workers and a fresh optional output are required')
    source = Path(__file__).resolve()
    original = sha256(source.read_bytes()).hexdigest()
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    workers=args.workers, source_sha256=original,
                    seeded_permutations='202610090354+h',
                    scope='Exact restored-dirty-bit Boolean word, separate native shape obligations')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, [3] if args.bounded else [3, 4, 5]))
    if sha256(source.read_bytes()).hexdigest() != original:
        raise ValueError('Source changed during exact gate verification')
    summary = dict(status='PASS BORROWED-BIT PERMUTATIONS', cases=rows,
                   gate_set=['NOT', 'CNOT', 'Toffoli'],
                   complete_native_route=False, new_multiplier_exponent=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], dimensions=len(rows),
                         permutations=sum(len(r['cases']) for r in rows))))


if __name__ == '__main__':
    main()
