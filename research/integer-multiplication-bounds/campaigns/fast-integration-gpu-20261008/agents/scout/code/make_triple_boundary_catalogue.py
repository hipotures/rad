#!/usr/bin/env python3
"""Generate bridge-coupled boundary trees outside completed swap catalogues."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import sys

from gpu_boundary_single_swap_valid_full_family import base, catalogue, restriction_tree, signature


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--count', type=int, required=True)
    ap.add_argument('--previous-catalogue', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert 0 < args.count <= 128 and not args.output.exists()
    parent = base.upstream.baseline()
    previous = json.loads(args.previous_catalogue.read_text())
    forbidden = {signature(parent)} | {entry[2] for entry in catalogue(parent)}
    for row in previous['records']:
        actual = parent.copy()
        for r, a, b in row['swaps']:
            actual[r, a], actual[r, b] = actual[r, b], actual[r, a]
        assert actual.tolist() == row['permutations']
        forbidden.add(signature(actual))
    rng = random.Random(args.seed)
    seen = set()
    records = []
    attempts = 0
    rejected = {'existing_endpoint': 0, 'non_tree': 0, 'same_row': 0}
    while len(records) < args.count:
        attempts += 1
        assert attempts <= 300000
        first_row = rng.randrange(22)
        last_row = rng.randrange(3, 25)
        bridge_row = rng.choice((0, 1, 23, 24))
        if len({first_row, last_row, bridge_row}) != 3:
            rejected['same_row'] += 1
            continue
        first_other = rng.choice([i for i in range(2, 23) if i != 22 or first_row < 2])
        last_other = rng.choice([i for i in range(21) if i != 0 or last_row >= 23])
        bridge = (bridge_row, 1, 22) if bridge_row < 2 else (bridge_row, 0, 21)
        swaps = [(first_row, 1, first_other), (last_row, last_other, 21), bridge]
        actual = parent.copy()
        for r, a, b in swaps:
            actual[r, a], actual[r, b] = actual[r, b], actual[r, a]
        key = signature(actual)
        if key in forbidden or key in seen:
            rejected['existing_endpoint'] += 1
            continue
        if not restriction_tree(actual, 0) or not restriction_tree(actual, 528):
            rejected['non_tree'] += 1
            continue
        assert all(actual[i, 0] == i for i in range(23))
        assert all(actual[i, 22] == i - 2 for i in range(2, 25))
        seen.add(key)
        records.append({'index': len(records), 'swaps': swaps, 'permutations': actual.tolist(),
                        'endpoint_sha256': hashlib.sha256(json.dumps(key, separators=(',', ':')).encode()).hexdigest()})
    result = {'format': 'controlled-multiswap-endpoints-v1',
              'utc': datetime.now(timezone.utc).isoformat(), 'seed': args.seed, 'python': sys.version,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'parent_permutation_sha256': hashlib.sha256(parent.astype('<i4').tobytes()).hexdigest(),
              'previous_catalogue': str(args.previous_catalogue),
              'previous_catalogue_sha256': hashlib.sha256(args.previous_catalogue.read_bytes()).hexdigest(),
              'old_single_swap_endpoints_excluded': 1 + len(catalogue(parent)),
              'all_previous_endpoints_excluded': len(forbidden),
              'attempts': attempts, 'rejection_counts': rejected, 'records': records,
              'scope': 'Three row-disjoint transpositions: separate boundary changes plus a bridge that changes both endpoint restrictions. Both actual 47-edge restrictions are trees. Baseline, all previous single-swap and the supplied two-swap endpoint signatures are excluded. GPU discovery, not a paid physical-network certificate.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(',', ':')) + '\n')
    assert args.output.stat().st_size < 1024 * 1024
    print(json.dumps({'output': str(args.output), 'records': len(records), 'attempts': attempts,
                      'rejections': rejected, 'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
