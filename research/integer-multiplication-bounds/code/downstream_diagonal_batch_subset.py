#!/usr/bin/env python3
"""Exact characteristic screen for a conservative middle-bank batch subset.

This is a prospective recurrence certificate, conditional on the actual
physical endpoint and tape batching proofs. It promotes no theorem.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import log_integer_bounds, network_counts
from downstream_parameter_optimum import as_strings, rational_decimal_lower


def subset(h, roles):
    n = network_counts(h, roles)
    factor = (roles + h) * n['v'] * h * h
    removed = factor * n['v'] * (h - 1)
    assert 0 < removed < n['s']
    histogram = Counter({1: n['s'] - removed})
    frequencies = []
    for a in range(h - 2):
        frequency = comb(h - a - 1, 2)
        frequencies.append(dict(minimum_index=a, triples=frequency, runs=[a, h - a - 2, 1]))
        for r in (a, h - a - 2, 1):
            if r:
                histogram[r] += factor * frequency
    assert sum(row['triples'] for row in frequencies) == n['v']
    assert sum(r * count for r, count in histogram.items()) == n['s']
    assert 1 <= max(histogram) < n['m']
    ml, mh = log_integer_bounds(n['m'])
    linear = n['W'] * n['m'] * mh
    quadratic = Q(0)
    for r, count in histogram.items():
        rl, rh = log_integer_bounds(r)
        linear -= count * r * rl
        quadratic += Q(count * r, 2) * rh * rh
    assert linear > 0 and quadratic > 0
    gap = lambda a: n['D'] - a * linear - a * a * quadratic
    lo, hi = Q(0), Q(1, 100000000)
    assert gap(lo) > 0 and gap(hi) < 0
    for _ in range(80):
        mid = (lo + hi) / 2
        if gap(mid) > 0:
            lo = mid
        else:
            hi = mid
    saving = Q(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24)
    assert saving > 0 and gap(saving) > 0
    return dict(h=h, roles=roles, counts=n, final_middle_subset_factor=factor,
                removed_single_pivots=removed, frequencies=frequencies,
                batch_histogram={str(r):count for r,count in sorted(histogram.items())},
                rank_sum=n['s'], batch_calls=sum(histogram.values()),
                log_m_interval=[ml,mh], taylor_linear_coefficient=linear,
                taylor_quadratic_coefficient=quadratic, saving=saving,
                saving_decimal_lower=rational_decimal_lower(saving, 18),
                strict_taylor_gap=gap(saving), root_bracket=[lo,hi])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h', type=int, required=True)
    ap.add_argument('--roles', type=int, required=True)
    ap.add_argument('--finite-review', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists(), 'Use a fresh output path'
    started = time.monotonic()
    review = json.loads(a.finite_review.read_text())
    assert review['status'] == 'PASS' and review['full']['h'] == a.h
    assert review['full'].get('compiled_roles', review['full'].get('roles')) == a.roles
    row = subset(a.h, a.roles)
    value = dict(status='PASS PROSPECTIVE CONSERVATIVE DIAGONAL-BATCH CHARACTERISTIC',
                 generated_utc=datetime.now(timezone.utc).isoformat(),
                 source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                 finite_input=dict(path=str(a.finite_review), bytes=a.finite_review.stat().st_size,
                                   sha256=sha256(a.finite_review.read_bytes()).hexdigest()),
                 witness=row, elapsed_seconds=time.monotonic() - started,
                 scope='Only the final middle auxiliary endpoints I tensor I tensor (I-P_t) are batched; every other old pivot remains individual. Physical endpoint, grouping, arbitrary-width tail, row-reservation and guard transfers must be reviewed before use.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(as_strings(value), indent=2, sort_keys=True) + '\n')
    print(value['status'], row['saving'], row['saving_decimal_lower'], flush=True)


if __name__ == '__main__':
    main()
