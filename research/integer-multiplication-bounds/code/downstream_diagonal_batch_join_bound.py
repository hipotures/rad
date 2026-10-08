#!/usr/bin/env python3
"""Exact Taylor screen combining middle endpoints and joined low-rank edges.

The low-rank diagonal-run theorem and tape transfer are hypotheses here.
No graph, exponent interface, or assembly witness is promoted by this code.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_diagonal_batch_subset import subset
from downstream_gaussian import log_integer_bounds
from downstream_parameter_optimum import as_strings, rational_decimal_lower


def joint(h, roles):
    middle = subset(h, roles)
    n = middle['counts']
    copies = (roles + h) * n['v'] ** 2
    dimension_defect = 2 * h
    minimum_diagonal = n['m'] - 2 * dimension_defect
    maximum_runs = 2 * dimension_defect + 1
    joined_old_rank = copies * (n['m'] - dimension_defect)
    assert middle['removed_single_pivots'] + joined_old_rank < n['s']
    assert minimum_diagonal > maximum_runs > 1
    tl, th = log_integer_bounds(minimum_diagonal)
    gl, gh = log_integer_bounds(maximum_runs)
    log_ratio_lower = tl - gh
    assert log_ratio_lower > 0
    joined_log_sum_lower = copies * minimum_diagonal * log_ratio_lower
    ml, mh = middle['log_m_interval']
    middle_log_sum_lower = n['W'] * n['m'] * mh - middle['taylor_linear_coefficient']
    linear = middle['taylor_linear_coefficient'] - joined_log_sum_lower
    # Every batch rank is at most m, and the full rank sum remains s.
    quadratic = Q(n['s'], 2) * mh * mh
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
    assert gap(saving) > 0
    return dict(h=h, roles=roles, counts=n, minimum_diagonal_pivots_per_join=minimum_diagonal,
                maximum_diagonal_runs_per_join=maximum_runs, join_count=copies,
                joined_rank_defect=dimension_defect, joined_old_rank=joined_old_rank,
                middle_old_rank=middle['removed_single_pivots'],
                other_unchanged_rank=n['s'] - joined_old_rank - middle['removed_single_pivots'],
                middle_rank_log_sum_lower=middle_log_sum_lower,
                joined_rank_log_sum_lower=joined_log_sum_lower,
                log_diagonal_to_runs_lower=log_ratio_lower,
                taylor_linear_coefficient=linear, taylor_quadratic_coefficient=quadratic,
                saving=saving, saving_decimal_lower=rational_decimal_lower(saving, 18),
                strict_taylor_gap=gap(saving), root_bracket=[lo,hi],
                comparison=dict(uniform_subset_saving=middle['saving'],
                                strict_improvement_over_subset=saving > middle['saving'],
                                larger_than_two_power_minus_28=saving > Q(1, 2 ** 28)))


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
    row = joint(a.h, a.roles)
    sources = [Path(__file__), Path(__file__).with_name('downstream_diagonal_batch_subset.py')]
    result = dict(status='PASS PROSPECTIVE JOINT DIAGONAL-BATCH TAYLOR SCREEN',
                  generated_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources},
                  finite_input=dict(path=str(a.finite_review), sha256=sha256(a.finite_review.read_bytes()).hexdigest()),
                  witness=row, elapsed_seconds=time.monotonic() - started,
                  scope='Conditional on independent low-rank pivot-run theorem and physical endpoint multiplicities; only conservative disjoint middle-final and joined families are changed. Row reservations, tape batching, exact original-factor compatibility and recursive exponent transfer remain required.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True) + '\n')
    print(result['status'], row['saving'], row['saving_decimal_lower'], flush=True)


if __name__ == '__main__':
    main()
