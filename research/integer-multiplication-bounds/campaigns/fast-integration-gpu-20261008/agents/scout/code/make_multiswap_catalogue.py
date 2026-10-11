#!/usr/bin/env python3
"""Generate finite distinct two-swap endpoint trees outside the old catalogue."""
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
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert 0 < args.count <= 128 and not args.output.exists()
    rng = random.Random(args.seed)
    parent = base.upstream.baseline()
    forbidden = {signature(parent)} | {entry[2] for entry in catalogue(parent)}
    seen = set()
    records = []
    attempts = 0
    rejected = {'existing_endpoint': 0, 'non_tree': 0, 'same_row': 0}
    while len(records) < args.count:
        attempts += 1
        assert attempts <= 300000
        first_row = rng.randrange(22)
        last_row = rng.randrange(3, 25)
        if first_row == last_row:
            rejected['same_row'] += 1
            continue
        first_other = rng.choice([i for i in range(2, 23) if i != 22 or first_row < 2])
        last_other = rng.choice([i for i in range(21) if i != 0 or last_row >= 23])
        swaps = [(first_row, 1, first_other), (last_row, last_other, 21)]
        actual = parent.copy()
        for row, left, right in swaps:
            actual[row, left], actual[row, right] = actual[row, right], actual[row, left]
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
    result = {'format': 'controlled-multiswap-endpoints-v1', 'utc': datetime.now(timezone.utc).isoformat(),
              'seed': args.seed, 'python': sys.version, 'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'parent_permutation_sha256': hashlib.sha256(parent.astype('<i4').tobytes()).hexdigest(),
              'old_single_swap_endpoints_excluded': len(forbidden), 'attempts': attempts,
              'rejection_counts': rejected, 'records': records,
              'scope': 'Exactly two row-disjoint transpositions, one affecting each controlled boundary; both actual47-edge restrictions are trees. Complete old single-swap endpoint signatures are excluded. Finite GPU discovery, not a physical-network certificate.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(',', ':')) + '\n')
    assert args.output.stat().st_size < 1024 * 1024
    print(json.dumps({'output': str(args.output), 'records': len(records), 'attempts': attempts,
                      'rejections': rejected, 'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
