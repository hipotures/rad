#!/usr/bin/env python3
"""Exact aligned-tape binary-counter controls for repeated quadratic phases.

The counters use individual symbol lists and explicitly charged aligned
head moves. The independent comparison recomputes each address phase.
This checks the proposed diagonal scan, not a full frame adapter.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import time


def control(banks, width, selected, linear):
    assert len(selected) % 2 == 0 and len(set(selected)) == len(selected)
    mate = {}
    for a, b in zip(selected[::2], selected[1::2]):
        mate[a] = b
        mate[b] = a
    tape = [[0] * width for _ in range(banks)]
    heads = [0] * banks
    phase = weight = flips = head_moves = 0
    rows = 1 << (banks * width)
    digest = sha256()

    def move(column):
        nonlocal head_moves
        for a in range(banks):
            head_moves += abs(heads[a] - column)
            heads[a] = column

    for address in range(rows):
        actual = phase, weight
        values = [(address >> (a * width)) & ((1 << width) - 1)
                  for a in range(banks)]
        expected_q = 0
        for a, b in zip(selected[::2], selected[1::2]):
            expected_q ^= (values[a] & values[b]).bit_count() & 1
        for a in selected:
            if linear[a]:
                expected_q ^= values[a].bit_count() & 1
        expected_weight = sum(values[a].bit_count() for a in selected) % 4
        assert actual == (expected_q, expected_weight)
        assert all(sum(tape[a][j] << j for j in range(width)) == values[a]
                   for a in range(banks))
        digest.update(bytes(actual))
        if address + 1 == rows:
            continue
        stop = False
        for a in range(banks):
            for j in range(width):
                move(j)
                old = tape[a][heads[a]]
                if a in mate:
                    phase ^= linear[a] ^ tape[mate[a]][heads[mate[a]]]
                    weight = (weight + (1 if old == 0 else -1)) % 4
                tape[a][heads[a]] ^= 1
                flips += 1
                if old == 0:
                    stop = True
                    break
            move(0)
            if stop:
                break
        assert stop
    assert flips < 2 * rows
    assert head_moves <= 4 * banks * rows
    return {'banks': banks, 'bits_per_bank': width,
            'selected_banks': selected, 'linear_coefficients': linear,
            'complete_addresses': rows, 'charged_symbol_flips': flips,
            'charged_counter_head_moves': head_moves,
            'head_move_bound': 4 * banks * rows,
            'initialization_symbols': banks * width,
            'phase_sequence_sha256': digest.hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists()
    started = time.monotonic()
    rng = random.Random(209)
    rows = []
    configs = [(2, f, [0, 1]) for f in range(1, 9)]
    configs += [(4, f, [0, 1, 2, 3]) for f in range(1, 5)]
    configs += [(6, f, [0, 2, 3, 5]) for f in range(1, 4)]
    configs += [(5, f, [1, 3]) for f in range(1, 4)]
    for banks, width, selected in configs:
        linear = [rng.randrange(2) for _ in range(banks)]
        rows.append(control(banks, width, selected, linear))
    result = {'status': 'PASS exact aligned-counter phase scan; adapter/network separate',
              'seed': 209, 'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'cases': rows, 'complete_addresses': sum(x['complete_addresses'] for x in rows),
              'elapsed_seconds': time.monotonic() - started}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}), flush=True)


if __name__ == '__main__':
    main()
