#!/usr/bin/env python3
"""Exact rational representatives falsifying a sample-only permutation gain."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path

import numpy as np


def weights(h, beta):
    gamma = (9 * beta - 1) / (3 * (1 - h * beta))
    return (1 - 3 * beta) * (1 + gamma) / 2, -3 * beta * gamma / 2


def profile(permutation, betas, source):
    inverse = [[1 / weights(h, beta)[0 if i in triple else 1] for i in range(h)]
               for h, beta, triple in zip((23, 25), betas, source)]
    rows = [(permutation[i % 25][i // 25], i % 25) for i in range(47)]
    columns = [(permutation[(528 + j) % 25][(528 + j) // 25], (528 + j) % 25)
               for j in range(47)]
    M = [[inverse[0][r] * (r == c) + inverse[1][b] * (b == d) - 1
          for c, d in columns] for r, b in rows]
    pivots = []
    for i in range(47):
        pivot = next((j for j in range(46, -1, -1) if M[i][j]), -1)
        pivots.append(pivot)
        if pivot < 0:
            continue
        for k in range(i + 1, 47):
            if M[k][pivot]:
                factor = M[k][pivot] / M[i][pivot]
                M[k] = [value - factor * entry for value, entry in zip(M[k], M[i])]
    cuts = [0] + [i for i in range(1, 47) if pivots[i] != pivots[i - 1] + 1] + [47]
    return pivots, [b - a for a, b in zip(cuts, cuts[1:])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    triples = [list(combinations(range(h), 3)) for h in (23, 25)]
    names = ['gpu-basis-full-family-20261008T1615-device0',
             'gpu-basis-full-family-20261008T1615-device1',
             'gpu-basis-full-family-followup-20261008T1619-device1']
    records = []
    for name in names:
        root = args.work_root / 'derived/scout' / name
        path = root / 'summary.json'
        summary = json.loads(path.read_text())
        dominant = max(summary['profile_classes_agree_full_rank'], key=lambda item: item['count'])
        arrays = [np.load(root / f'pivots-prime{p}.npy', mmap_mode='r') for p in summary['primes']]
        chosen = None
        for start in range(0, len(arrays[0]), 8192):
            first = arrays[0][start:start + 8192]
            masks = np.sum((first[:, 1:] != first[:, :-1] + 1).astype(np.uint64)
                           * (np.uint64(1) << np.arange(46, dtype=np.uint64)), axis=1)
            matches = (masks == dominant['cut_mask']) & (first == arrays[1][start:start + 8192]).all(axis=1)
            if matches.any():
                chosen = start + int(np.flatnonzero(matches)[0])
                break
        assert chosen is not None
        index = chosen + summary['source_partition_start_inclusive']
        source = [triples[0][index // 2300], triples[1][index % 2300]]
        betas = [Fraction(summary[f'beta{h}']['numerator'],
                          summary[f'beta{h}']['denominator']) for h in (23, 25)]
        pivots, runs = profile(summary['actual_permutation'], betas, source)
        assert pivots == arrays[0][chosen].tolist() == arrays[1][chosen].tolist()
        assert runs == dominant['runs'] and 21 in runs and 15 in runs and 17 not in runs
        records.append({'run': name, 'summary_path': str(path),
                        'summary_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'pair_index': index, 'source_triples': source,
                        'beta23': summary['beta23'], 'beta25': summary['beta25'],
                        'actual_permutation': summary['actual_permutation'],
                        'Q_pivots': pivots, 'Q_runs': runs,
                        'matches_both_saved_field_profiles': True,
                        'modular_agree_dominant_class_count': dominant['count'],
                        'conclusion': 'Exact rational counterexample to a universal21+17 or sample+2ln2 profile at this changed permutation.'})
    result = {'utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PASS THREE EXACT Q FALSIFYING REPRESENTATIVES',
              'audit_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'records': records,
              'scope': 'Three concrete rational matrices; large field histograms remain discovery-only unless separately certified.'}
    assert not args.output.exists()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'representatives': len(records), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
