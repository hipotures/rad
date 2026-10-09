#!/usr/bin/env python3
"""Exact spectral ranks and all-cap channel census for odd paired cubes.

The spectral formula is an algebraic theorem, not a physical role bound.
The materialization interpretation assumes distinct retained cap channels.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time


def probe(k):
    if k < 3 or not k & 1:
        raise ValueError('Odd cube dimension at least three required')
    r = (k - 1) // 2
    ranks = []
    for j in range(k):
        rank = 0
        for a in range(j + 1):
            upper, remaining = r - a, k - j
            partial = sum((-1) ** b * comb(remaining, b)
                          for b in range(min(remaining, upper) + 1)) if upper >= 0 else 0
            closed = ((-1) ** upper * comb(remaining - 1, upper)
                      if 0 <= upper < remaining else 0)
            if partial != closed:
                raise AssertionError('Alternating binomial spectrum formula failed')
            active = max(0, j - r) <= a <= min(j, r)
            if bool(partial) != active:
                raise AssertionError('Spectral support interval failed')
            if active:
                rank += comb(j, a)
        if j and rank % 2:
            raise AssertionError('The two equivalent parity blocks must have equal integer ranks')
        ranks.append(rank)
    count = sum(comb(k, j) * rank for j, rank in enumerate(ranks))
    multinomial = sum(comb(k, a) * comb(k - a, b)
                      for a in range(r + 1) for b in range(r + 1))
    tail = sum(comb(k, a) * 2 ** (k - a) for a in range(r + 1, k + 1))
    if count != multinomial or count != 3 ** k - 2 * tail:
        raise AssertionError('Complete cap census differs from its independent color-count identity')
    tail_bound = 1 << (2 * k - r - 1)
    if tail > tail_bound:
        raise AssertionError('Exact weighted-tail bound failed')
    return {'cube_dimension': k, 'spectral_row_ranks': ranks,
            'independent_cap_channels': count, 'raw_channels': 3 ** k - 2 ** k,
            'source_banks': 2 ** k, 'channel_ratio': str(Q(count, 2 ** k)),
            'excluded_color_tail': tail, 'exact_tail_upper_bound': tail_bound,
            'all_cap_count_lower_bound': 3 ** k - 2 * tail_bound,
            'count_requires_distinct_retained_cap_classes': True,
            'not_a_general_physical_role_lower_bound': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    cases = [3, 5, 7] if args.bounded else [3, 5, 7, 9, 11, 13]
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    if args.workers == 1:
        rows = list(map(probe, cases))
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(cases))) as pool:
            rows = list(pool.map(probe, cases))
    result = {'status': 'PASS EXACT CAP-CHANNEL SPECTRAL CENSUS',
              'started_utc': start, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds': time.perf_counter() - timer,
              'workers_requested': args.workers, 'bounded': args.bounded,
              'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'cases': rows,
              'scope': 'Exact spectral and channel counts; no native circuit or multiplier exponent'}
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'certificate.json').write_text(encoded, encoding='utf-8')
    print(encoded, end='')


if __name__ == '__main__':
    main()
