#!/usr/bin/env python3
"""Pinned complete composition of reviewed whole-rank complex children.

The native generic bit characteristic is unchanged. The phase branching
characteristic is independently reconstructed from physical families;
paid bit adapters, mixed directions, exact tails, leading completed rows
and the PRODUCT row stock enter through the accepted complete transfer.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from downstream_delayed_complex_general_beta import check_changed_complex
from downstream_gaussian import require
from downstream_general_beta_semantic_bulk import general_witness
from downstream_parameter_optimum import as_strings, rational_decimal_lower
from downstream_promoted_complex_composition import parse_counts
from downstream_rotated_batch_characteristic import log_bounds
from downstream_whole_complex_parameters import whole_witness


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def check_sources(obj, source_dir, single_name=None):
    for key in ('source_sha256', 'reviewer_source_sha256', 'dependency_sha256'):
        value = obj.get(key, {})
        if isinstance(value, str):
            require(single_name is not None and key == 'source_sha256',
                    'A single source hash needs its exact filename')
            value = {single_name: value}
        for name, digest in value.items():
            require(sha(source_dir/name) == digest, 'Pinned source differs '+name)


def check_input_hashes(obj):
    for key in ('inputs', 'input_sha256'):
        for name, digest in obj.get(key, {}).items():
            path = Path(name)
            require(path.is_file() and sha(path) == digest,
                    'Pinned proof/certificate input differs '+name)


def phase_characteristic(nc, peer, primitive):
    require(peer['status'] ==
            'PASS independent exact b_phase=10^-6 on accepted changed h28',
            'Accepted whole-rank characteristic absent')
    require({k: nc[k] for k in peer['counts']} == peer['counts'],
            'Whole-rank characteristic uses different physical counts')
    h, m, v = nc['h'], nc['m'], nc['v']
    J = (nc['R']+h+1)*v*v
    ranks = dict(middle=m-h*h, joined=m-2*h, data=(h*h-1)*(h-1))
    copies = dict(middle=J, joined=J, data=2*nc['N'])
    credited = sum(copies[k]*ranks[k] for k in ranks)
    other = nc['s']-credited
    histogram = {'1': other, **{str(ranks[k]): copies[k] for k in ranks}}
    require(ranks == peer['grouped_ranks'] and copies == peer['family_multiplicities'] and
            credited == peer['total_grouped_rank'] and
            other == peer['all_other_individual_pivots'] > 0 and
            histogram == peer['child_histogram'] and
            sum(int(r)*count for r, count in histogram.items()) == nc['s'],
            'Disjoint whole-rank family/histogram accounting differs')
    b = Q(1, 10**6)
    coarse_linear = nc['s']*10-Q(99, 10)*credited
    coarse_quadratic = Q(nc['s'], 2)*100
    coarse_gap = nc['D']-b*coarse_linear-b*b*coarse_quadratic/(1-10*b)
    require(b == Q(peer['saving']) and coarse_linear == Q(peer['normalized_linear_upper']) and
            coarse_quadratic == Q(peer['normalized_quadratic_upper']) and
            coarse_gap == Q(peer['strict_normalized_gap']) > 0,
            'Independent coarse logarithm/Taylor witness differs')
    # These outward intervals come from our separate 24-term/grid source.
    lm = log_bounds(m)
    logs = {name: log_bounds(rank) for name, rank in ranks.items()}
    require(lm[1] < 10 and all(pair[0] > Q(99, 10) for pair in logs.values()),
            'Coarse logarithm bounds not independently established')
    moment = sum(copies[name]*ranks[name]*logs[name][0] for name in ranks)
    linear = nc['s']*lm[1]-moment
    quadratic = Q(nc['s'], 2)*lm[1]*lm[1]
    fine_gap = nc['D']-b*linear-b*b*quadratic/(1-b*lm[1])
    a = Q(primitive['saving'])
    require(0 < b*lm[1] < 1 and fine_gap >= coarse_gap > 0 and b > 2*a and
            Q(peer['accepted_generic_bit_saving']) >= a and
            Q(peer['phase_above_twice_bit']) > 0,
            'Strict new characteristic or fixed-half leaf feasibility failed')
    maximum = max(ranks.values())
    require(maximum == peer['maximum_child'] == m-2*h and
            peer['exact_half_shrink_power'] == 272 and m**272 > 2*maximum**272,
            'Whole-rank strict variable shrink differs')
    return dict(certificate_kind='STRICT HOMOGENEOUS PHASE BRANCHING; PAID NATIVE BIT OVERHEAD',
                chosen_saving=b, sigma=1-b, counts=nc, grouped_children=ranks,
                family_multiplicities=copies, total_grouped_rank=credited,
                all_other_individual_pivots=other, child_histogram=histogram,
                maximum_child=maximum, depth_per_ceil_log2e=272,
                exact_log_method='Independent outward 24-term intervals, common dyadic 2^256 grid',
                logarithm_intervals={'m': lm, **logs}, rank_log_moment_lower=moment,
                normalized_linear_upper=linear, normalized_quadratic_upper=quadratic,
                strict_primitive_gap=fine_gap, independent_coarse_gap=coarse_gap,
                phase_above_twice_bit=b-2*a, beta_half_leaf_above_bit=b/2-a,
                characteristic='sum(n_r*r^(1-b))<W*m^(1-b)',
                exact_sufficient_inequality='D-b*(s*ln(m)_U-M_L)-b^2*s*ln(m)_U^2/[2*(1-b*ln(m)_U)]>0',
                overhead='Existing native bit exponent tau, complete V/W child volume, plus paid leading-prefix O(V logp)',
                scope='sigma is a homogeneous branching exponent. No standalone phase runtime below paid bit-adapter tau is asserted.')


def check_whole_transfer(nc, G, phase, transfer, controls):
    require(transfer['status'] ==
            'PASS independent complete whole-rank complex transfer qualifications' and
            controls['status'] == 'PASS independent mixed whole-rank complex interface controls',
            'Complete reviewed whole-rank transfer/controls absent')
    rows = transfer['combined_rows']
    require(rows['polynomial_degree'] == 89000 and rows['sufficient_suffix_slope'] == 356000 and
            rows['stock_base_two_coefficient'] == 49*651+41*272 and
            rows['bit_depth'] == 651 and rows['complex_depth'] == 272 and
            rows['complex_maxchild'] == phase['maximum_child'] and
            rows['exact_product'] == 'W_complex^D_complex*W_bit^D_bit' and
            rows['one_initial_leading_prefix'], 'Complete nested product stock differs')
    E = 64*(nc['W']+nc['m']+1)**3
    B = nc['s']+E
    depth = 2*G*nc['W']*nc['W']+8*nc['s']+4*nc['W']+4+32*nc['m']
    expected = dict(h=nc['h'], R=nc['R'], W=nc['W'], s=nc['s'], G=G, E=E, B=B,
                    C0=32*nc['m']*B*B, C1=1, stronger_wrapper_tail_depth=depth,
                    strict_E_slack=E-depth)
    require(expected == transfer['finite_count_and_guard'] and E > depth,
            'Enhanced actual scalar/mixed-wrapper/tail guard differs')
    mixed, grid, layout = controls['mixed'], controls['variable_fixed_grid'], controls['complete_layouts']
    require(mixed['same_completed_grid_and_norm_as_individual_kernels'] and
            mixed['omitted_mixed_wrappers_disagreeing_probes'] > 0 and
            grid['common_encoding_never_rewritten'] and
            grid['omitted_trailing_tail_disagreeing_outputs'] > 0 and
            layout['same_K_rho_complete_prefix_child'] and layout['full_width_child_excluded'] and
            layout['main_and_tail_fields_never_moved'],
            'Mixed/tail/fixed-grid/complete-field discriminating controls missing')
    return dict(status='INDEPENDENT COMPLETE WHOLE-RANK TRANSFER ACCEPTED',
                mixed_directions='(-i)^(f*n_minus) Z_minus C^(r*f) Z_minus, paid aligned scans',
                child_field='First r complete adjacent fK fields; same rho,K; full V/W volume',
                exact_tail='t<m elementary C1 butterflies, 32m additive depth charged',
                product_row_stock=rows, literal_enhanced_guard=expected,
                fine_grid='No child truncation or encoding rewrite; exact completed reset',
                weighted_tree='Strict homogeneous phase characteristic plus native tau overhead',
                reviewed_controls=dict(mixed_probes=mixed['probes'], fixed_grid_probes=grid['probes'],
                                       complete_layouts=layout['exact_shapes'],
                                       weighted_frontier=controls['weighted_stopped_trees']['frontier_leaf_potential_not_equal_depth']))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('previous-assembly', 'previous-final-review', 'changed-complex-review',
                 'whole-controls', 'whole-characteristic', 'whole-transfer-review',
                 'whole-transfer-report'):
        ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--whole-transfer-report-sha256', required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args();require(not args.output.exists(), 'Use a fresh output path')
    t0 = time.monotonic();source_dir = Path(__file__).parent
    old = json.loads(args.previous_assembly.read_text())
    final = json.loads(args.previous_final_review.read_text())
    peer = json.loads(args.changed_complex_review.read_text())
    controls = json.loads(args.whole_controls.read_text())
    characteristic = json.loads(args.whole_characteristic.read_text())
    transfer = json.loads(args.whole_transfer_review.read_text())
    check_sources(old, source_dir);check_sources(final, source_dir)
    check_sources(controls, source_dir, 'review_whole_complex.py')
    check_sources(characteristic, source_dir, 'review_whole_complex_characteristic.py')
    check_sources(transfer, source_dir, 'review_whole_complex_transfer.py')
    for obj in (final, characteristic, transfer):check_input_hashes(obj)
    require(sha(args.whole_transfer_report) == args.whole_transfer_report_sha256,
            'Frozen full analytic whole-rank transfer report differs')
    require(final['status'] == 'PASS independent complete delayed-complex generic-basis general-beta assembly' and
            final['complete_conditional_assembly'] and not final['whole_rank_complex_children'] and
            final['input_sha256'][str(args.previous_assembly.resolve())] == sha(args.previous_assembly),
            'Previous complete uniform delayed-complex assembly not independently accepted')
    previous = max(Q(row['kappa']) for row in final['rows'])
    require(previous == max(Q(row['parameters']['kappa']) for row in old['witnesses']),
            'Accepted complete previous kappa differs')
    n = parse_counts(old['witnesses'][0]['bit_counts'])
    primitive = old['generic_characteristic_certificate']['witness']
    require(final['unchanged_finite_identity'] == old['odd_bit_finite_audit'] and
            Q(final['exact_primitive_audit']['chosen_saving']) == Q(primitive['saving']),
            'Unchanged accepted generic bit identity differs')
    nc, G, finite_audit = check_changed_complex(peer, source_dir)
    require(final['changed_complex_finite_audit'] == as_strings(finite_audit),
            'Accepted changed complex finite audit differs')
    regressions = []
    for row in old['witnesses']:
        regenerated = general_witness(n, nc, row['mode'], row['prefix'],
                                      Q(row['previous_accepted_kappa']), primitive, G)
        for key in ('parameters', 'recurrence', 'margins', 'constraint_slacks',
                    'cutoff_log2_b', 'stopped_leaf_certificate', 'compact_row_padding'):
            require(as_strings(regenerated[key]) == row[key],
                    'Frozen uniform delayed-complex regression differs '+key)
        regressions.append(dict(mode=row['mode'], prefix=row['prefix'],
                                kappa=row['parameters']['kappa'], unchanged=True))
    phase = phase_characteristic(nc, characteristic, primitive)
    interface = check_whole_transfer(nc, G, phase, transfer, controls)
    rows = []
    for mode in ('conservative', 'tight'):
        for prefix in ('original', 'balanced'):
            row = whole_witness(n, nc, mode, prefix, previous, primitive, phase, G)
            row['complex_input'] = 'delayed88377-whole-rank'
            row['native_bit_primitive'] = old['witnesses'][0]['native_bit_primitive']
            row['whole_complex_transfer'] = interface
            rows.append(row)
    paths = [getattr(args, name.replace('-', '_')) for name in
             ('previous-assembly', 'previous-final-review', 'changed-complex-review',
              'whole-controls', 'whole-characteristic', 'whole-transfer-review', 'whole-transfer-report')]
    hashes = dict(old['source_sha256'])
    for name in (Path(__file__).name, 'downstream_whole_complex_parameters.py',
                 'downstream_rotated_batch_characteristic.py'):
        hashes[name] = sha(source_dir/name)
    result = dict(status='PASS STRICT CONDITIONAL WHOLE-COMPLEX ASSEMBLY; INDEPENDENT FULL REVIEW REQUIRED',
                  campaign_start='2026-10-07T22:25:21Z', campaign_original_deadline='2026-10-08T08:25:21Z',
                  campaign_deadline='2026-10-08T10:00:00Z', generated_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=hashes, input_files={str(p): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in paths},
                  previous_accepted_kappa=previous, accepted_uniform_regressions=regressions,
                  odd_bit_finite_audit=old['odd_bit_finite_audit'],
                  generic_characteristic_certificate=old['generic_characteristic_certificate'],
                  changed_complex_finite_audit=finite_audit, whole_complex_characteristic=phase,
                  accepted_whole_complex_transfer=interface,
                  whole_transfer_report_sha256=args.whole_transfer_report_sha256,
                  unchanged_generic_root_inputs_sha256=old['unchanged_generic_root_inputs_sha256'],
                  witnesses=rows, elapsed_seconds=time.monotonic()-t0,
                  scope='Changed complete contiguous complex recursion on independently promoted R88377. Retained generic R485680 bit basis and bulk/router/precision interfaces. New homogeneous sigma, mixed wrappers, tails and PRODUCT row stock are charged. Fixed giant table/prime/layout and strict absorption remain separately eventual.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
    for row in rows:
        print(result['status'], row['mode'], row['prefix'], row['parameters']['kappa'],
              rational_decimal_lower(row['parameters']['kappa'], 18),
              row['cutoff_log2_b']['common'], flush=True)


if __name__ == '__main__':
    main()
