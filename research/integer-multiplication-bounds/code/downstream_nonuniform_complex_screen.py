#!/usr/bin/env python3
"""Exact screen of grouped nonalternating complex boundary calls.

This is a numerical characteristic under a NEW, PENDING child interface.
It does not certify fixed-tape concatenation, numerical precision or a
complete multiplication bound. Only accepted finite complex inputs enter.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_gaussian import require
from downstream_general_beta_semantic_bulk import complex_counts
from downstream_parameter_optimum import as_strings, rational_decimal_lower
from downstream_rotated_batch_characteristic import log_bounds


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def screen(h, roles):
    n = complex_counts(h, roles)
    m, v = n['m'], n['v']
    J = (roles+h+1)*v*v
    ranks = dict(middle=m-h*h, joined=m-2*h,
                 data=(h*h-1)*(h-1))
    copies = dict(middle=J, joined=J, data=2*n['N'])
    family_ranks = {name: ranks[name]*copies[name] for name in ranks}
    credited = sum(family_ranks.values())
    require(all(1 < r < m for r in ranks.values()) and credited < n['s'],
            'Proposed disjoint grouped family rank accounting failed')
    lm = log_bounds(m)[1]
    logs = {name: log_bounds(r) for name, r in ranks.items()}
    moment = {name: family_ranks[name]*logs[name][0] for name in ranks}
    linear = n['s']*lm-sum(moment.values())
    quadratic = Q(n['s'], 2)*lm*lm

    def gap(b):
        require(0 <= b*lm < 1, 'Positive-exp remainder domain failed')
        return n['D']-b*linear-b*b*quadratic/(1-b*lm)

    lo, hi = Q(0), Q(1, 10**4)
    require(linear > 0 and gap(lo) > 0 > gap(hi),
            'Pending complex strict root bracket failed')
    for _ in range(100):
        mid = (lo+hi)/2
        if gap(mid) > 0:
            lo = mid
        else:
            hi = mid
    b = Q(lo.numerator*10**24//lo.denominator, 10**24)
    require(gap(b) > 0, 'Pending complex screen is not strict')
    maximum = max(ranks.values())
    depth = 1
    while m**depth <= 2*maximum**depth:
        depth += 1
    require(m**depth > 2*maximum**depth and n['W'] < 2**41,
            'Exact pending complex depth/role stock failed')
    exponent = 23000
    require(Q(41*depth)*(2+Q(1, 25)) < exponent,
            'Pending complete complex row degree arithmetic failed')
    return dict(
        h=h, roles=roles, counts=n, family_multiplicities=copies,
        grouped_children=ranks, family_rank_sums=family_ranks,
        total_grouped_rank=credited,
        all_other_individual_pivots=n['s']-credited,
        rank_log_moment_lower=moment,
        chosen_saving=b, saving_decimal_lower=rational_decimal_lower(b, 18),
        strict_positive_normalization_gap=gap(b),
        taylor_linear_coefficient=linear,
        taylor_quadratic_coefficient=quadratic,
        maximum_child=maximum, depth_per_ceil_log2e=depth,
        sufficient_complex_row_degree=exponent,
        complex_row_degree_rational_slack=exponent-Q(41*depth)*(2+Q(1, 25)),
        existing_generic_bit_row_degree=66000,
        existing_bit_row_degree_also_covers_complex=66000 > exponent,
        root_bracket=[lo, hi],
        exact_log_method='Outward exact 24-term intervals on common dyadic 2^256 grid',
        proposed_child='One C^(r*f) for the complete nonalternating residual, replacing r separate C^f calls',
        pending='Fixed-tape whole-field concatenation, numerical guard/precision and recursive full-volume transfer are not certified by this arithmetic screen')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--accepted-assembly', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    t0 = time.monotonic()
    old = json.loads(args.accepted_assembly.read_text())
    source_dir = Path(__file__).parent
    for name, digest in old['source_sha256'].items():
        require(sha(source_dir/name) == digest, 'Pinned prior source differs '+name)
    require(old['controller_complex_audit']['status'] ==
            'INDEPENDENT COMPLEX CONTROLLER FINITE/SCALAR/GUARD PASS',
            'Accepted complex finite input audit absent')
    rows = [screen(28, r) for r in (97586, 92309)]
    for row in rows:
        prior = next(r for r in old['witnesses'] if
                     r['complex_counts']['R'] == row['roles'] and
                     r['mode'] == 'tight' and r['prefix'] == 'balanced')
        require(as_strings(row['counts']) == prior['complex_counts'],
                'Proposed screen uses different finite counts')
        row['old_uniform_complex_saving'] = Q(prior['parameters']['a_complex'])
        row['conditional_primitive_ratio'] = row['chosen_saving']/row['old_uniform_complex_saving']
        row['current_generic_bit_saving'] = Q(prior['parameters']['a_bit'])
        row['would_make_generic_bit_limiting'] = row['chosen_saving'] > row['current_generic_bit_saving']
        row['old_literal_guard_unchanged_only_if_transfer_proves_it'] = prior['semantic_guard']
    files = [Path(__file__), source_dir/'downstream_rotated_batch_characteristic.py',
             source_dir/'downstream_general_beta_semantic_bulk.py',
             source_dir/'downstream_parameter_optimum.py', source_dir/'downstream_gaussian.py']
    result = dict(
        status='PASS EXACT NUMERICAL SCREEN; NONUNIFORM COMPLEX CHILD TRANSFER PENDING',
        campaign_start='2026-10-07T22:25:21Z',
        campaign_original_deadline='2026-10-08T08:25:21Z',
        campaign_deadline='2026-10-08T10:00:00Z',
        generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256={p.name: sha(p) for p in files},
        input_file=dict(path=str(args.accepted_assembly), bytes=args.accepted_assembly.stat().st_size,
                        sha256=sha(args.accepted_assembly)),
        rows=rows, elapsed_seconds=time.monotonic()-t0,
        exact_inequality='D-b*(s*ln(m)_U-M_L)-b^2*s*ln(m)_U^2/[2*(1-b*ln(m)_U)]>0',
        scope='Only characteristic arithmetic for accepted complex role/count inputs. This result neither establishes a new complex implementation nor promotes a multiplication kappa.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
    for row in rows:
        print(result['status'], row['roles'], row['chosen_saving'],
              row['saving_decimal_lower'], row['depth_per_ceil_log2e'], flush=True)


if __name__ == '__main__':
    main()
