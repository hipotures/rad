#!/usr/bin/env python3
"""Fine prefix/window search using the frozen exact singleton evaluator.

The first direct-label cohort shows a broad optimum near half early singleton
positions. These candidates examine its boundary and sharing asymmetries;
every previous completed or planned candidate identity is excluded.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

import finite_singleton_successor as direct


def structured(anchor, prior):
    h, base, starting = anchor['h'], anchor['base'], anchor['positions']
    excluded = {job['candidate_id'] for job in prior['candidate_definitions']}
    excluded.add(direct.queue.identity(h, base, starting)[1])
    for protocol in [prior, *[json.loads((path/'protocol.json').read_text())
                             for path in direct.EXTRA_RUNS]]:
        excluded.update(job['candidate_id'] for job in protocol['candidate_definitions'])
        if 'baseline_positions' in protocol:
            excluded.add(direct.queue.identity(h, base, protocol['baseline_positions'])[1])

    positives = [position for position in starting if position > 0]
    late = Counter(positives).most_common(1)[0][0]
    seen, rows = set(), []

    def append(positions, kind):
        assert len(positions) == h and all(0 <= p < h//2 for p in positions)
        value, key = direct.queue.identity(h, base, positions)
        if key in excluded or key in seen or len(rows) >= direct.TARGET:
            return
        seen.add(key)
        changed = [dict(common=c, old=old, new=new) for c, (old, new)
                   in enumerate(zip(starting, positions)) if old != new]
        assert changed
        rows.append(dict(value, candidate_id=key, neighborhood=kind, changed=changed))

    low, high = max(1, h//2-9), min(h-2, h//2+11)
    sizes = sorted(range(low, high+1), key=lambda size: (abs(size-h//2), size))
    for early in [0, 1, 2]:
        for late_choice in [late, max(1, late-1)]:
            for size in sizes:
                positions = [late_choice]*h
                positions[-2:] = starting[-2:]
                positions[:size] = [early]*size
                append(positions, 'fine-prefix')

    for size in [h//2-3, h//2-1, h//2+1, h//2+3, h//2+5]:
        for tail in [[0, 0], [late, min(h//2-1, late+1)], [late, late],
                     [0, min(h//2-1, late+1)]]:
            positions = [0]*size+[late]*(h-size)
            positions[-2:] = tail
            append(positions, 'prefix-tail')

    for length in [h//2-5, h//2-1, h//2+1, h//2+3, h//2+5]:
        for start in range(2, h-length+1, 2):
            positions = [late]*h
            positions[-2:] = starting[-2:]
            positions[start:start+length] = [0]*length
            append(positions, 'early-window')

    for length in [h//2-1, h//2+1, h//2+3]:
        for start in range(2, h, 2):
            positions = [late]*h
            positions[-2:] = starting[-2:]
            for offset in range(length):
                positions[(start+offset) % h] = 0
            append(positions, 'cyclic-early-window')

    pairs = list(range(h//2))
    orders = [pairs[::2]+pairs[1::2], pairs[1::2]+pairs[::2],
              list(reversed(pairs)), pairs[1:]+pairs[:1]]
    for order in orders:
        for size in range(max(1, h//4-4), min(h//2, h//4+5)+1):
            positions = [late]*h
            positions[-2:] = starting[-2:]
            for pair in order[:size]:
                positions[2*pair:2*pair+2] = [0, 0]
            append(positions, 'paired-early-pattern')

    rng = random.Random(direct.SEED)
    attempts = 0
    while len(rows) < direct.TARGET:
        attempts += 1
        assert attempts < 20000
        positions = list(starting)
        for common in rng.sample(range(h), rng.choice([2, 3, 4, 6, 8, 10])):
            choices = [0, 1, 2, max(1, late-1), late, min(h//2-1, late+1)]
            positions[common] = rng.choice(choices)
        if positions != starting:
            append(positions, 'structured-seeded-refinement')

    assert len(rows) == len(seen) == direct.TARGET and not seen.intersection(excluded)
    direct.CONFIGURATION.update(neighborhood_counts=dict(Counter(row['neighborhood'] for row in rows)),
        structured_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        prefix_size_range=[low, high], late_position=late,
        hypothesis='Optimize early/late common-point boundary and nonprefix global-sharing layouts; exact physical roles determine ranking.')
    return rows, sorted(excluded)


if __name__ == '__main__':
    direct.successor = structured
    if '--target-cases' not in sys.argv:
        sys.argv.extend(['--target-cases', '450'])
    direct.main()
