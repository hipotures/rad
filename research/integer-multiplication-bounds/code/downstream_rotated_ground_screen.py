#!/usr/bin/env python3
"""Rank saved actual-role ground candidates by the exact rotated characteristic.

No scalar graph, role compiler or frame replay is executed. Producer-only
candidates remain unpromoted; the result nominates independent finite audits.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_gaussian import network_counts, require
from downstream_parameter_optimum import as_strings, rational_decimal_lower
from downstream_rotated_batch_characteristic import rotated


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def checked_counts(saved, h, roles):
    n = network_counts(h, roles)
    for key in ('h', 'm', 'N', 'W', 'L', 'D', 's', 'side_roles'):
        if key in saved:
            require(saved[key] == n[key], 'Saved count differs: ' + key)
    require(saved.get('rank_sum_regression_exact', True), 'Saved rank sum failed')
    require(saved.get('edge_count_regression_exact', True), 'Saved edge count failed')
    return n


def ordinary(path, expected=None, summary=None):
    actual_sha = digest(path)
    require(expected is None or actual_sha == expected, 'Saved case hash differs')
    a = json.loads(path.read_text())
    h, roles = a['h'], a['compiled_roles']
    checks = a['checked']
    for key in ('all_scalar_coefficients_exact', 'forward_frames_nested',
                'reverse_complement_frames_nested'):
        require(checks[key], 'Saved finite check failed: ' + key)
    saved = a.get('residual_rank_histogram')
    if saved is None:
        saved = a.get('compiled', {}).get('residual_rank_histogram', {})
    n = checked_counts(saved, h, roles)
    if summary is not None:
        require(summary['h'] == h and summary['compiled_roles'] == roles,
                'Terminal summary and saved case differ')
        for key, value in summary.get('exact_network_counts', {}).items():
            require(n[key] == value, 'Summary count differs: ' + key)
        require(summary['candidate_id'] == a['candidate_id'], 'Candidate ID differs')
    return dict(h=h, roles=roles, candidate_id=a['candidate_id'],
                compiled_sha256=checks['compiled_sha256'], counts=n,
                source_case=dict(path=str(path), bytes=path.stat().st_size,
                                 sha256=actual_sha),
                input_kind='SAVED FINITE PRODUCER CASE; INDEPENDENT PROMOTION REQUIRED')


def clone(path):
    a = json.loads(path.read_text())
    require(a['status'].endswith('PASS'), 'Saved clone witness is not terminal PASS')
    r = a['rows'][0]
    require(r['frame_identity_control'], 'Saved clone frame control failed')
    saved = r['exact_counts']
    h, roles = saved['h'], saved['side_roles']
    n = checked_counts(saved, h, roles)
    return dict(h=h, roles=roles, candidate_id='clone-certificate:' + digest(path),
                compiled_sha256=None, counts=n,
                source_case=dict(path=str(path), bytes=path.stat().st_size,
                                 sha256=digest(path)),
                input_kind='SAVED STRUCTURAL CLONE PRODUCER; DISTINCT ID AND INDEPENDENT PROMOTION REQUIRED')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--terminal-summary', type=Path, action='append', default=[])
    ap.add_argument('--saved-candidate', type=Path, action='append', default=[])
    ap.add_argument('--clone-certificate', type=Path, action='append', default=[])
    ap.add_argument('--reference-characteristic', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    records = []
    summaries = []
    for path in args.terminal_summary:
        a = json.loads(path.read_text())
        require(a['status'].startswith('Terminal'), 'Summary is still live')
        summaries.append(dict(path=str(path), bytes=path.stat().st_size,
                              sha256=digest(path), status=a['status']))
        for h, row in a['best_per_ground'].items():
            if 43 <= int(h) <= 58:
                records.append(ordinary(Path(row['external_certificate']),
                                        row['external_certificate_sha256'], row))
    records.extend(ordinary(path) for path in args.saved_candidate)
    records.extend(clone(path) for path in args.clone_certificate)
    require(records, 'No eligible saved candidates')
    by_ground = {}
    for row in records:
        require(43 <= row['h'] <= 58, 'Supplemental ground is outside declared screen')
        old = by_ground.get(row['h'])
        if old is None or row['roles'] < old['roles']:
            by_ground[row['h']] = row
    reference = json.loads(args.reference_characteristic.read_text())
    expected = next(r for r in reference['witnesses'] if r['variant'] == 'tensor-data')
    require(as_strings(rotated(expected['h'], expected['roles'], 'tensor-data')) == expected,
            'Historical accepted characteristic regression differs')
    results = []
    for h, record in sorted(by_ground.items()):
        p = rotated(h, record['roles'], 'tensor-data')
        a = p['saving']
        row = dict(record)
        row.update(primitive_saving=a,
                   primitive_saving_decimal_lower=rational_decimal_lower(a, 18),
                   declared_balanced_parameter_supremum=a/(1+a),
                   supremum_decimal_lower=rational_decimal_lower(a/(1+a), 18),
                   strict_taylor_gap=p['strict_taylor_gap'],
                   taylor_linear_coefficient=p['taylor_linear_coefficient'],
                   taylor_quadratic_coefficient=p['taylor_quadratic_coefficient'],
                   maximum_child_rank=h*h,
                   W_upper_binary_exponent=record['counts']['W'].bit_length(),
                   above_historical_reference=a>Q(expected['saving']))
        results.append(row)
    ranking = sorted(results, key=lambda r: r['primitive_saving'], reverse=True)
    source_dir = Path(__file__).parent
    result = dict(status='PASS EXACT SAVED-GROUND SCREEN; NO NEW FINITE PROMOTIONS',
                  campaign='20261007T222521Z',
                  original_start_utc='2026-10-07T22:25:21Z',
                  original_deadline_utc='2026-10-08T08:25:21Z',
                  extended_deadline_utc='2026-10-08T10:00:00Z',
                  generated_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256={p.name:digest(p) for p in (Path(__file__),
                      source_dir/'downstream_rotated_batch_characteristic.py',
                      source_dir/'downstream_gaussian.py')},
                  summary_inputs=summaries,
                  reference_input=dict(path=str(args.reference_characteristic),
                                       sha256=digest(args.reference_characteristic)),
                  reference_saving=Q(expected['saving']),
                  reference_regression_exact=True,
                  selected_ground_count=len(results), loaded_saved_records=len(records),
                  rows=results, ranked_grounds=[r['h'] for r in ranking],
                  best=ranking[0],
                  missing_grounds=[h for h in range(43,59) if h not in by_ground],
                  elapsed_seconds=time.monotonic()-started,
                  scope='Exact tensor-data characteristic applied to saved actual role counts only. Minimum R at fixed h is selected, then cross-ground saving is compared exactly. Independent scalar/frame/timeline promotion, matching/prime scope, full assembly and ground-specific row padding remain required for each new candidate. Displayed a/(1+a) is a declared parameter-family supremum, not a promoted complete witness.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
    for row in ranking:
        print('SAVED CANDIDATE', row['h'], row['roles'], row['primitive_saving'],
              row['primitive_saving_decimal_lower'], flush=True)


if __name__ == '__main__':
    main()
