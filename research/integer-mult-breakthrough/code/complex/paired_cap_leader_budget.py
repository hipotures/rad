#!/usr/bin/env python3
"""Actual-center capacity at a reported comparator and stronger savings.

The reported kappa is a comparison input, not independently adopted evidence.
The relation b>kappa/(1-kappa) applies only to the inherited balanced assembly
even when beta tends to zero; beta=1/20 is also charged explicitly.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import paired_cap_side_budget as side


REPORTED_KAPPA = Q(6558894, 10 ** 10)


def probe(p):
    cap = side.raw_cap_profile(p)
    minimum = REPORTED_KAPPA / (1 - REPORTED_KAPPA)
    tests = [('necessary lower boundary as beta tends to zero', minimum),
             ('explicit approximate complex comparator', Q(65632, 10 ** 8)),
             ('necessary lower boundary at beta=1/20', minimum * Q(20, 19)),
             ('larger component target', Q(7, 10000))]
    rows = []
    for split in (False, True):
        fixed = side.fixed_profile(p, split)
        rows.append({'target_clock': fixed['target_clock'],
                     'center_roles': fixed['center']['roles'],
                     'copied_center_loss': fixed['center']['copied_loss'],
                     'fixed_first_moment_deficit': fixed['deficit'],
                     'complete_fixed_profile_without_side_roles': dict(fixed['fixed_child_profile']),
                     'tests': [{'comparison': name,
                                'budget': side.budget(fixed, b),
                                'stock_models': side.floor_evidence(fixed, cap, b)}
                               for name, b in tests]})
    return {'p': p, 'h': 2 * p, 'v': 32 * side.comb(p, 5),
            'retained_cap_stock_model': side.characteristic.serializable(cap), 'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker is required')
    paths = [Path(__file__).resolve(), Path(side.__file__).resolve(), Path(side.baseline.__file__).resolve(),
             Path(side.baseline.scalar.__file__).resolve(), Path(side.characteristic.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    ps = (9,) if args.bounded else (9, 12)
    if args.workers == 1:
        rows = [probe(p) for p in ps]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(ps))) as pool:
            rows = list(pool.map(probe, ps))
    if any(p.read_bytes() != b for p, b in frozen.items()):
        raise AssertionError('Effective frozen actual-center/exact-moment closure changed')
    result = {'status': 'PASS exact actual-center comparator-level side budgets',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {p.name: sha256(b).hexdigest() for p, b in frozen.items()},
              'reported_comparison_kappa': str(REPORTED_KAPPA),
              'comparison_provenance': 'Coordinator-provided reported decimal, used only as a necessary assembly comparison; upstream exponent and verifier not adopted here',
              'assembly_scope': 'Inherited a<(1-beta)b and kappa<a/(1+a) only; strict lower boundaries are not certified achievable b or a. Changed transfers need their own inequalities.',
              'cases': rows,
              'scope': 'Exact optimistic side-budget sensitivity with actual copied-center profiles. No attained cap formation, global chronology, native supplier or improved exponent.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'pair_counts': [r['p'] for r in rows]}), flush=True)


if __name__ == '__main__':
    main()
