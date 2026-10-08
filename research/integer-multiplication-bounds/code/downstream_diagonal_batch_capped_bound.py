#!/usr/bin/env python3
"""Capped joined-run Taylor screen with an explicit h-fold child shrink.

This fresh source preserves the uncapped screen unchanged. It certifies
arithmetic and depth implications; the complete physical/tape transfer is
still an independent obligation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_diagonal_batch_join_bound import joint
from downstream_gaussian import log_integer_bounds
from downstream_parameter_optimum import as_strings, rational_decimal_lower


def ceil_log(e, base):
    assert e > 0 and base > 1
    count, power = 0, 1
    while power < e:
        power *= base
        count += 1
    return count


def depth_controls():
    count = 0
    for h in (6, 8, 50, 51):
        m = h ** 3
        sizes = {m - 1, m, m + 1, 2 * m - 1, m * h * h + 7}
        for j in range(1, 16):
            sizes.update((h ** j - 1, h ** j, h ** j + 1))
        for e in sorted(x for x in sizes if x > 0):
            assert ceil_log(e, h) <= 3 * ceil_log(e, m)
            if e >= m:
                b, t = divmod(e, m)
                assert 0 <= t < m and b >= 1
                for r in (1, h - 2, h, h * h - 1, h * h):
                    assert r * b <= e // h and r * b < e
                    count += 1
    return dict(exact_child_width_and_depth_checks=count,
                child_width_bound='r*floor(e/h^3) <= floor(e/h) for 1<=r<=h^2',
                depth_bound='ceil(log_h e) <= 3*ceil(log_(h^3) e)')


def capped(h, roles):
    old = joint(h, roles)
    n = old['counts']
    minimum_diagonal = n['m'] - 4 * h
    maximum_pieces = 5 * h + 1
    maximum_child_rank = h * h
    # Every original diagonal run is cut into ceil(r/h^2) pieces.
    assert Q(4 * h + 1) + Q(n['m'] - 2 * h, h * h) < maximum_pieces
    tl, _ = log_integer_bounds(minimum_diagonal)
    _, gh = log_integer_bounds(maximum_pieces)
    joined_log_sum_lower = old['join_count'] * minimum_diagonal * (tl - gh)
    _, mh = log_integer_bounds(n['m'])
    linear = n['W'] * n['m'] * mh - old['middle_rank_log_sum_lower'] - joined_log_sum_lower
    quadratic = Q(n['s'], 2) * mh * mh
    assert linear > 0 and quadratic > 0
    gap = lambda a: n['D'] - a * linear - a * a * quadratic
    lo, hi = Q(0), Q(1, 100000000)
    assert gap(lo) > 0 and gap(hi) < 0
    for _ in range(80):
        middle = (lo + hi) / 2
        if gap(middle) > 0:
            lo = middle
        else:
            hi = middle
    saving = Q(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24)
    assert saving > Q(1, 2 ** 28) and gap(saving) > 0
    return dict(h=h, roles=roles, counts=n, minimum_diagonal_pivots_per_join=minimum_diagonal,
                maximum_capped_diagonal_pieces_per_join=maximum_pieces,
                maximum_child_rank=maximum_child_rank, strict_child_ratio=Q(1, h),
                join_count=old['join_count'], middle_old_rank=old['middle_old_rank'],
                joined_old_rank=old['joined_old_rank'], other_unchanged_rank=old['other_unchanged_rank'],
                middle_rank_log_sum_lower=old['middle_rank_log_sum_lower'],
                joined_capped_rank_log_sum_lower=joined_log_sum_lower,
                taylor_linear_coefficient=linear, taylor_quadratic_coefficient=quadratic,
                saving=saving, saving_decimal_lower=rational_decimal_lower(saving, 18),
                strict_taylor_gap=gap(saving), root_bracket=[lo,hi],
                uncapped_comparison=dict(prospective_saving=old['saving'],
                                         uncapped_strictly_larger=old['saving'] > saving),
                depth_controls=depth_controls())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h', type=int, required=True)
    ap.add_argument('--roles', type=int, required=True)
    ap.add_argument('--finite-review', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists(), 'Use a fresh output path'
    review = json.loads(a.finite_review.read_text())
    assert review['status'] == 'PASS' and review['full']['h'] == a.h
    assert review['full'].get('compiled_roles', review['full'].get('roles')) == a.roles
    started = time.monotonic()
    row = capped(a.h, a.roles)
    sources = [Path(__file__), Path(__file__).with_name('downstream_diagonal_batch_join_bound.py'),
               Path(__file__).with_name('downstream_diagonal_batch_subset.py')]
    result = dict(status='PASS PROSPECTIVE CAPPED DIAGONAL-BATCH TAYLOR SCREEN',
                  generated_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources},
                  finite_input=dict(path=str(a.finite_review), sha256=sha256(a.finite_review.read_bytes()).hexdigest()),
                  witness=row, elapsed_seconds=time.monotonic() - started,
                  scope='Conditional on independently verified physical endpoints and low-rank diagonal-run theorem; capped ranks<=h^2 give h-fold shrink. Complete fixed-tape grouping, original-factor compatibility, row reservation and recursive transfer remain unpromoted.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True) + '\n')
    print(result['status'], row['saving'], row['saving_decimal_lower'], flush=True)


if __name__ == '__main__':
    main()
