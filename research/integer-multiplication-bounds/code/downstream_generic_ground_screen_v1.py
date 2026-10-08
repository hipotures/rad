#!/usr/bin/env python3
"""Rank completed actual bit candidates under the generic metric objective.

No graph, optimizer, physical compiler or large frame audit is replayed.
New candidates remain unpromoted. Histograms are audited where present;
older scalar-checked cases without histograms are explicitly weaker input.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_descendant_joined_characteristic import audit_boundary_histogram
from downstream_gaussian import ceil_q, network_counts, require
from downstream_generic_metric_characteristic import generic
from downstream_parameter_optimum import as_strings, rational_decimal_lower
from downstream_rotated_batch_characteristic import log_bounds


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def checked_case(path, expected=None, summary=None):
    raw = path.read_bytes();digest = sha256(raw).hexdigest()
    require(expected is None or digest == expected, 'Saved case hash differs')
    document = json.loads(raw)
    if 'rows' in document:
        require(document['status'].endswith('PASS'), 'Saved structural certificate is not PASS')
        row = document['rows'][0]
    else:
        row = document
    h = row['h'];R = row['compiled_roles'];n = network_counts(h, R)
    checks = row.get('final', row)['checked']
    for key in ('all_scalar_coefficients_exact', 'forward_frames_nested',
                'reverse_complement_frames_nested'):
        require(checks[key], 'Saved complete finite producer check failed '+key)
    hist = row.get('exact_counts') or row.get('residual_rank_histogram')
    if hist:
        for key in ('m', 'N', 'W', 'L', 'D', 's', 'side_roles'):
            require(hist[key] == n[key], 'Saved actual network count differs '+key)
        audit = audit_boundary_histogram(hist, h, R)
        rank_scope = 'COMPLETE ACTUAL CHANGED HISTOGRAM AND BOUNDARY CATEGORIES RECONSTRUCTED'
    else:
        audit = None
        rank_scope = 'OLDER FULL SCALAR/FRAME PRODUCER; ACTUAL INTERNAL RANK HISTOGRAM NOT SAVED'
    if summary is not None:
        require(summary['h'] == h and summary['roles'] == R and
                summary['candidate_id'] == row['candidate_id'],
                'Saved descendant frontier identity differs')
        require(summary['exact_counts'] == hist and
                summary['compiled_sha256'] == checks['compiled_sha256'],
                'Saved descendant complete histogram/compile identity differs')
    return dict(h=h, roles=R, counts=n, candidate_id=row['candidate_id'],
                compiled_sha256=checks['compiled_sha256'],
                source_case=dict(path=str(path), bytes=len(raw), sha256=digest),
                actual_histogram_audit=audit, rank_scope=rank_scope,
                promotion='PRODUCER FINITE CHECKS ONLY; INDEPENDENT SELECTED-WITNESS PROMOTION REQUIRED')


def objective(h, R):
    n = network_counts(h, R);m = n['m'];v = n['v'];J = (R+h)*v*v
    kernels = dict(middle=h*h, joined=2*h, data=h*h+h-1)
    runs = {name: m-2*d for name, d in kernels.items()}
    copies = dict(middle=J, joined=J, data=2*n['N'])
    require(n['D'] > 0 and all(0 < r < m for r in runs.values()),
            'Eligible positive-deficit generic kernels failed')
    moment = {name: copies[name]*r*log_bounds(r)[0] for name, r in runs.items()}
    lm = log_bounds(m)[1]
    linear = n['W']*m*lm-sum(moment.values())
    quadratic = Q(n['s'], 2)*lm*lm
    gap = lambda a: n['D']-a*linear-a*a*quadratic
    lo, hi = Q(0), Q(1, 10**4)
    require(gap(lo) > 0 > gap(hi), 'Saved generic root bracket failed')
    for _ in range(100):
        mid = (lo+hi)/2
        if gap(mid) > 0:
            lo = mid
        else:
            hi = mid
    a = Q(lo.numerator*10**24//lo.denominator, 10**24)
    require(gap(a) > 0, 'Saved generic characteristic is not strict')
    maximum = max(runs.values());depth = 1
    while m**depth <= 2*maximum**depth:
        depth += 1
    bits = n['W'].bit_length()
    stock = ceil_q(Q(bits*depth)*(2+Q(1, 25))/1000)*1000
    require(stock > Q(bits*depth)*(2+Q(1, 25)),
            'Saved generic row degree is not strict')
    return dict(kernel_dimensions=kernels, grouped_runs=runs,
                family_multiplicities=copies,
                family_ranks={name: copies[name]*(m-kernels[name]) for name in runs},
                rank_log_moment_lower=moment,
                chosen_saving=a, saving_decimal_lower=rational_decimal_lower(a, 18),
                strict_taylor_gap=gap(a), taylor_linear_coefficient=linear,
                taylor_quadratic_coefficient=quadratic,
                maximum_child=maximum, binary_halving_depth=depth,
                W_binary_upper_exponent=bits, standalone_bit_row_degree=stock,
                safe_nested_whole_complex_row_degree=stock+23000,
                safe_nested_reservoir_coefficient=4*(stock+23000),
                declared_bit_limited_parameter_upper=a/(1+a),
                parameter_upper_decimal_lower=rational_decimal_lower(a/(1+a), 18))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--descendant-summary', type=Path, required=True)
    ap.add_argument('--ordinary-summary', type=Path, action='append', default=[])
    ap.add_argument('--saved-case', type=Path, action='append', default=[])
    ap.add_argument('--structural-certificate', type=Path, action='append', default=[])
    ap.add_argument('--accepted-generic-characteristic', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args();require(not args.output.exists(), 'Use a fresh output path')
    t0 = time.monotonic();summaries = [];records = []
    saved = json.loads(args.descendant_summary.read_text())
    require(saved['status'].startswith('Terminal') and not saved['errors'],
            'Delayed frontier is not complete without scientific errors')
    summaries.append(dict(path=str(args.descendant_summary), sha256=sha(args.descendant_summary)))
    for row in saved['best_by_ground']:
        path = Path(saved['full_external_results'])/'cases'/(row['candidate_id']+'.json')
        records.append(checked_case(path, row['full_result_sha256'], row))
    for path in args.ordinary_summary:
        saved = json.loads(path.read_text())
        require(saved['status'].startswith('Terminal'), 'Ordinary summary is still live')
        summaries.append(dict(path=str(path), sha256=sha(path), historical_errors_retained=True))
        for row in saved['best_per_ground'].values():
            records.append(checked_case(Path(row['external_certificate']),
                                        row['external_certificate_sha256']))
    records.extend(checked_case(p) for p in args.saved_case)
    records.extend(checked_case(p) for p in args.structural_certificate)
    best_by_ground = {}
    for record in records:
        h = record['h']
        require(21 <= h <= 58, 'Saved ground outside declared screen')
        if h not in best_by_ground or record['roles'] < best_by_ground[h]['roles']:
            best_by_ground[h] = record
    reference = json.loads(args.accepted_generic_characteristic.read_text())
    old = reference['witness']
    require(as_strings(generic(old['h'], old['roles'])) == old,
            'Accepted h51 generic characteristic regression differs')
    rows = []
    for h, record in sorted(best_by_ground.items()):
        p = objective(h, record['roles'])
        audit = record['actual_histogram_audit']
        if audit is not None:
            require(p['family_ranks']['middle'] == audit['final_middle_copies']*audit['final_middle_residual_rank'] and
                    p['family_ranks']['joined'] == audit['joined_copies']*audit['joined_residual_rank'] and
                    p['family_ranks']['data'] == audit['stage3_data_copies']*audit['stage3_data_residual_rank'],
                    'Generic selected families differ from actual boundary histogram')
        rows.append(dict(record, **p,
                         above_current_promoted_h51=Q(p['chosen_saving']) > Q(old['saving'])))
    ranking = sorted(rows, key=lambda r: r['chosen_saving'], reverse=True)
    source_dir = Path(__file__).parent
    result = dict(
        status='PASS EXACT SAVED GENERIC GROUND SCREEN; NO NEW FINITE PROMOTION OR KAPPA',
        campaign_start='2026-10-07T22:25:21Z', campaign_original_deadline='2026-10-08T08:25:21Z',
        campaign_deadline='2026-10-08T10:00:00Z', generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256={p.name: sha(p) for p in (Path(__file__), source_dir/'downstream_generic_metric_characteristic.py',
                       source_dir/'downstream_descendant_joined_characteristic.py',
                       source_dir/'downstream_gaussian.py', source_dir/'downstream_rotated_batch_characteristic.py')},
        summary_inputs=summaries, accepted_reference=dict(path=str(args.accepted_generic_characteristic),
                                                         sha256=sha(args.accepted_generic_characteristic)),
        accepted_reference_regression_exact=True,
        reference_saving=Q(old['saving']), rows=rows,
        loaded_saved_candidates=len(records), selected_grounds=len(rows),
        ranked_grounds=[r['h'] for r in ranking], best=ranking[0],
        elapsed_seconds=time.monotonic()-t0,
        scope='Exact direct negative-exponential characteristic on completed actual role counts. Actual complete rank histogram and boundaries are reconstructed where saved; older missing-histogram input is explicitly distinct. Every new candidate needs its own independent finite/metric-basis/prime/row/interface promotion and complete parameter witness. No repeated graph search or replay is executed. Nested wholeC row stocks use the sum of standalone degrees, not a maximum.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
    for row in ranking:
        print('SAVED GENERIC CANDIDATE', row['h'], row['roles'], row['chosen_saving'],
              row['saving_decimal_lower'], row['rank_scope'], flush=True)


if __name__ == '__main__':
    main()
