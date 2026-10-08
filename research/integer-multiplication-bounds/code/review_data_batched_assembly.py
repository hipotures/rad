#!/usr/bin/env python3
"""Independent final assembly for the reviewed third data-edge family.

Only the kernel-hole variant is promoted here. The common assembly
inequalities use the frozen independent two-family checker after its
native-certificate representation is normalized and checked explicitly.
No producer is imported, and the new bit moment is recomputed independently.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import resource
import time

from review_batched_bulk_assembly import audit_row
from review_parameter_audit import log_integer
from review_packed_unrolling import finite_counts
from review_semantic_bulk_assembly import require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def audit_primitive(p):
    n = finite_counts(p['counts'])
    h, roles = p['h'], p['roles']
    require(h == 51 and roles == 502265 and p['variant'] == 'kernel-holes',
            'Unexpected third-family finite identity or proof variant')
    v, m = comb(h, 3), h**3
    copies = (roles+h)*v*v
    middle_rank = copies*h*h*(h-1)
    joined_rank = copies*(m-2*h)
    d = h*h+h-1
    data_copies = 2*n['N']
    data_rank = data_copies*(m-d)
    t, g = m-2*d, 2*d+1
    require(p['data_edge_count'] == data_copies and p['data_edge_rank'] == m-d and
            p['data_rank_defect'] == d and p['data_old_rank'] == data_rank and
            p['data_minimum_diagonal_pivots'] == t and
            p['data_maximum_run_pieces'] == g and p['maximum_child_rank'] == h*h-1 and
            p['previous_join_and_middle_rank'] == joined_rank+middle_rank and
            p['other_unchanged_rank'] == n['s']-data_rank-joined_rank-middle_rank > 0,
            'Disjoint physical family rank/count inputs differ')
    logs = {k: log_integer(k, 80) for k in range(1, h+1)}
    middle = Q(0)
    frequency = 0
    for first in range(h-2):
        count = comb(h-first-1, 2)
        frequency += count
        for length in (first, h-first-2):
            if length:
                middle += count*length*logs[length][0]
    require(frequency == v, 'Triple-minimum frequency partition differs')
    middle *= (roles+h)*v*h*h
    joined = copies*(m-4*h)*(log_integer(m-4*h, 80)[0]-log_integer(4*h+1, 80)[1])
    data = data_copies*t*(log_integer(t, 80)[0]-log_integer(g, 80)[1])
    lm = log_integer(m, 80)[1]
    linear = n['W']*m*lm-middle-joined-data
    quadratic = Q(n['s'], 2)*lm*lm
    saved_linear, saved_quadratic = (Q(p[k]) for k in
        ('taylor_linear_coefficient', 'taylor_quadratic_coefficient'))
    saving = Q(p['saving'])
    require(saving == Q(5385522401708297, 10**24), 'Unexpected declared data saving')
    require(saved_linear >= linear > 0 and saved_quadratic >= quadratic > 0,
            'Longer independent logs do not support the declared Taylor bounds')
    gap = n['D']-saving*saved_linear-saving*saving*saved_quadratic
    independent_gap = n['D']-saving*linear-saving*saving*quadratic
    require(gap == Q(p['strict_taylor_gap']) > 0 and independent_gap >= gap,
            'Third-family strict characteristic fails')
    return dict(chosen_saving=str(saving), logarithm_terms=80, exact_total_rank=n['s'],
                data_copies=data_copies, data_edge_rank=m-d, data_minimum_diagonal=t,
                data_maximum_runs=g, maximum_child_rank=h*h-1,
                independent_taylor_gap=str(independent_gap),
                saved_strict_taylor_gap=str(gap))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('certificate', 'two-family', 'two-family-review', 'primitive', 'data-review', 'output'):
        ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh result path')
    begin = time.monotonic()
    data = json.loads(args.certificate.read_text())
    old = json.loads(args.two_family.read_text())
    old_review = json.loads(args.two_family_review.read_text())
    primitive = json.loads(args.primitive.read_text())
    peer = json.loads(args.data_review.read_text())
    require(old_review['status'].startswith('PASS') and
            old_review['input_sha256'][str(args.two_family)] == digest(args.two_family),
            'Two-family predecessor lacks its independent final review')
    require(data['data_primitive_certificate'] == primitive and
            data['independent_data_review_sha256'] == digest(args.data_review) and
            digest(args.primitive) in peer['inputs'].values(),
            'Third-family primitive or peer input identity differs')
    require(peer['status'].startswith('PASS') and
            peer['physical_family']['disjoint_from_middle_and_joins'] and
            peer['physical_family']['x_edge'] == 'stage3 X in->2' and
            peer['physical_family']['y_edge'] == 'stage3 Y 0->1',
            'New physical data chronology has not passed independent review')
    require(data['odd_bit_finite_audit'] == old['odd_bit_finite_audit'] and
            data['promoted_complex_audit'] == old['promoted_complex_audit'],
            'Accepted finite identities changed')
    for name, expected in data['source_sha256'].items():
        require(digest(Path(__file__).with_name(name)) == expected,
                'Executed producer source changed '+name)
    for path in (args.two_family, args.primitive, args.data_review):
        require(any(record['sha256'] == digest(path) for record in data['input_files'].values()),
                'Producer input hash absent '+path.name)
    p = next(p for p in primitive['witnesses'] if p['variant'] == 'kernel-holes')
    primitive_audit = audit_primitive(p)
    old_best = max(old['witnesses'], key=lambda row: Q(row['parameters']['kappa']))
    require(Q(data['previous_accepted_kappa']) == Q(old_best['parameters']['kappa']),
            'Prior strongest two-family witness differs')
    rows = []
    for row in data['witnesses']:
        if row['batch_variant'] != 'kernel-holes':
            continue
        require(row['bit_counts'] == old_best['bit_counts'] and
                row['complex_counts'] == old_best['complex_counts'],
                'Third-family assembly changed accepted finite counts')
        native = row['native_bit_primitive']
        require(native['certificate_kind'] == 'THREE-FAMILY TAYLOR CHARACTERISTIC' and
                Q(native['chosen_saving']) == Q(p['saving']) and
                Q(native['strict_taylor_gap']) == Q(p['strict_taylor_gap']) and
                native['maximum_child_rank'] == p['maximum_child_rank'] == 2600 and
                Q(native['child_ratio']) == Q(1, 51) and
                native['physical_data_edges'] == 'X stage3 in->2 and Y stage3 0->1, N copies each' and
                native['excluded_zero_data_edge'] == 'Y stage3 in->0',
                'New native data contract differs')
        # Normalize checked representation only; no numeric exponent or
        # inequality is changed before the common independent algebra audit.
        normalized = deepcopy(row)
        normalized['native_bit_primitive'] = dict(
            certificate_kind='BATCHED CHARACTERISTIC', chosen_saving=native['chosen_saving'],
            strict_taylor_gap=native['strict_taylor_gap'], maximum_run=native['maximum_child_rank'])
        checked = audit_row(normalized, old_best, p)
        checked['batch_variant'] = 'kernel-holes'
        checked['reviewed_physical_data_edges'] = native['physical_data_edges']
        rows.append(checked)
    require({(r['mode'], r['prefix']) for r in rows} ==
            set(product(('conservative', 'tight'), ('original', 'balanced'))),
            'Four reviewed third-family rows are missing')
    names = ('review_data_batched_assembly.py', 'review_batched_bulk_assembly.py',
             'review_semantic_bulk_assembly.py', 'review_parameter_audit.py',
             'review_asymmetric_motif.py', 'review_packed_unrolling.py')
    result = dict(status='PASS independent complete three-family kernel-hole assembly',
        campaign='20261007T222521Z', generated_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256={str(p): digest(p) for p in
            (args.certificate, args.two_family, args.two_family_review, args.primitive, args.data_review)},
        reviewer_source_sha256={name: digest(Path(__file__).with_name(name)) for name in names},
        primitive_audit=primitive_audit, rows=rows,
        unchanged_finite_identity=data['odd_bit_finite_audit'],
        unchanged_complex_audit=data['promoted_complex_audit'],
        wall_seconds=time.monotonic()-begin,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Only the new kernel-hole data variant is independently promoted; the capped variant is unpromoted here. Conditional on retained written tape/analytic interfaces, separate eventual fixed-layout/prime/setup thresholds, and full multiplication assumptions.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    for row in rows:
        print('PASS', row['mode'], row['prefix'], row['kappa'], flush=True)


if __name__ == '__main__':
    main()
