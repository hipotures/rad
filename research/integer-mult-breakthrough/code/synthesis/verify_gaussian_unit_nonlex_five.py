#!/usr/bin/env python3
"""Bounded reusable replay of four scoped Gaussian-dyadic scan negatives."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import gaussian_unit_nonlex_scan_five as G


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError('Positive workers required')
    if args.output and args.output.exists():
        raise FileExistsError('A fresh optional output file is required')
    sources = [Path(module.__file__).resolve() for module in (G, G.S, G.S.R)]
    sources.append(Path(__file__).resolve())
    hashes = {str(path.relative_to(Path(__file__).resolve().parents[2])):
              sha256(path.read_bytes()).hexdigest() for path in sources}
    started = datetime.now(timezone.utc).isoformat()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(G.probe, G.tasks()))
    if len(rows) != 4 or any(row['witness'] is not None
                            or row['normalized_left_assignments'] != 4**7
                            for row in rows):
        raise AssertionError('A scoped negative is incomplete or now has a field witness')
    control = G.controls()
    # Independently enumerate a small kernel's normalized unit vectors.
    constraints = ((1, 2, 0, 1), (0, 1, 3, 2))
    direct = {(1, a, b, c) for a in range(1, 5) for b in range(1, 5) for c in range(1, 5)
              if all(sum(x*y for x, y in zip(row, (1, a, b, c))) % 5 == 0
                     for row in constraints)}
    produced = set(G.normalized_vectors(constraints, G.kernel(constraints, 4), 4))
    if not direct or produced != direct:
        raise AssertionError('The full normalized-kernel parameterization missed a unit vector')
    if hashes != {str(path.relative_to(Path(__file__).resolve().parents[2])):
                  sha256(path.read_bytes()).hexdigest() for path in sources}:
        raise AssertionError('The effective source closure changed')
    receipt = {'status': 'PASS FOUR GAUSSIAN-DYADIC NONLEX SCAN CONTROLS',
               'started_utc': started, 'workers': args.workers, 'standard_library_only': True,
               'source_closure': hashes, 'complete_negative_cases': 4,
               'normalized_left_assignments': sum(row['normalized_left_assignments'] for row in rows),
               'full_kernel_enumeration_control_size': len(direct), 'controls': control,
               'written_determinant_ring_scope_separate': True,
               'no_arbitrary_complex_or_other_topology_or_native_or_exponent_claim': True}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({key: receipt[key] for key in ('status', 'complete_negative_cases',
                                                   'normalized_left_assignments')}, sort_keys=True))


if __name__ == '__main__':
    main()
