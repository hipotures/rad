#!/usr/bin/env python3
"""Compose separately promoted bit and even-ground complex compact inputs.

The executed fixed-input compact certificate is an immutable regression.
This adapter verifies the independent finite records and recomputes the
counts, seven margins, guard and strengthened real-logarithm cutoff. It
does not replay either large finite graph or establish a proof by itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path
import subprocess
import time

from downstream_compact_control_assembly import COMPACT_REVISION, compose, upstream_regression
from downstream_gaussian import ceil_q, check_sources, require
from downstream_parameter_optimum import as_strings, rational_decimal_lower, saving_enclosure
from downstream_promoted_complex_composition import parse_counts, promoted


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def complex_promotion(candidate, review, calibration, source_dir):
    h = candidate['h']
    require(h >= 8 and h % 2 == 0, 'Shared binary complex proof requires even h>=8')
    logical, matching = candidate['logical'], candidate['matching']
    terminal, guard = candidate['terminal'], candidate['guard']
    row = next(r for r in review['rows'] if r['h'] == h)
    audit = row['frames']
    require(logical['all_disjoint_formal_additions'] and logical['all_output_coefficients_and_zeros_exact'],
            'Producer complex coefficient prerequisites missing')
    require(candidate['frames']['all_frames_nondegenerate_nested'] and
            candidate['frames']['every_nonzero_residual_has_explicit_norm_one_witness'],
            'Producer binary-frame prerequisite missing')
    require(terminal['every_terminal_complement_nondegenerate_nonalternating'] and
            terminal['pair_helper_bound_explicitly_checked'], 'Producer terminal prerequisite missing')
    require(audit['source_lines_and_exact_target_kernels'] and audit['reverse_complements_isometric'],
            'Independent complex endpoint/orientation audit missing')
    require(audit['exact_output_nonzero_coefficients'] == logical['nonzero_side_coefficients'],
            'Independent complex scalar coefficient count differs')
    require(audit['independent_logical_frames'] == terminal['nodes'] == logical['inputs']+logical['active_additions'],
            'Independent logical frame count differs')
    require(audit['analytic_complement_witnesses'] == audit['unique_frames'] > 0 and
            audit['analytic_nonzero_residual_witnesses'] > 0 and
            audit['forward_and_reverse_physical_transitions'] > 0,
            'Independent residual/complement/full physical timeline evidence missing')
    for name, expected in review['source_sha256'].items():
        require(sha(source_dir/name) == expected, 'Independently executed complex source changed '+name)
    v, m, N = comb(h,3), h**3, comb(h,3)**3
    R = logical['active_additions']+2*v
    require(logical['inputs'] == v and logical['designated_outputs'] == 2*v and
            R == logical['baseline_physical_roles'] == row['roles'],
            'Independently reconstructed complex roles differ')
    W = 2*N+2*v*v*(R+h+1)
    L = 3*v*v*h*(h+1)
    D = 2*N-2*L
    s = W*m-D
    n = dict(h=h,v=v,m=m,N=N,R=R,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    require(D > 0 and n == parse_counts(candidate['shared_complex_counts']),
            'Shared complex role/rank/count formulas disagree')
    require(candidate['unshared_W'] == W+v*v*(R+h+1) and
            candidate['unshared_s'] == s+v*v*(R+h+1)*m,
            'Complex sharing did not remove exactly m rank per identified role')
    independent_matching = row['even_stage_matching']
    require(matching['involution'] and matching['distinct_images'] == matching['triples'] == v and
            matching['middle_norm_one_join_witnesses'] == v and
            independent_matching['images'] == v and
            independent_matching['involutive_binary_orthogonal_matching'] and
            independent_matching['every_join_has_middle_coordinate_norm_one_witness'],
            'Independent complex stage matching/join evidence missing')
    require(matching['even_intersection_counts'] == independent_matching['intersection_histogram'] and
            sum(matching['even_intersection_counts'].values()) == v,
            'Producer/independent matching intersections differ')
    require(matching['dim_E'] == h and matching['dim_H'] == m-h and
            matching['join_residual_dimension'] == m-2*h and
            matching['rank_removed_per_identified_role'] == m,
            'Complex joining dimensions differ')
    gates = 3*v*v*(4*R+4)
    E = 64*(W+m+1)**3
    require(guard['grouped_scalar_gates'] == gates < 6*W and
            guard['strict_six_W_slack'] == 6*W-gates and
            guard['additive_guard_E'] == E and guard['guard_B'] == s+E and
            guard['strict_operation_depth_slack'] == E-(12*W**3+4*s+4*W+4) > 0 and
            guard['stopped_depth_branching_premise'] and 2 <= s < m**5,
            'Independent algebraic grouped-gate/stopped guard check failed')
    require(candidate['saving_enclosure'] == as_strings(saving_enclosure(n['eta'],m)),
            'Producer primitive logarithm enclosure changed')
    # The h8 complete matrix is the accepted all-even construction's finite
    # scalar calibration, rather than a redundant h28 dense matrix replay.
    small = next(r for r in calibration['rows'] if r['h'] == 8)
    matrix = small['complete_dirty_matrix']
    require(matrix['includes_both_data_banks_all_side_and_central_scratch'] and
            matrix['forward_identity_shear_and_inverse_exact'] and matrix['complete_basis_dimension'] == 1019,
            'Accepted complete dirty scalar calibration absent')
    for name, expected in calibration['source_sha256'].items():
        require(sha(source_dir/name) == expected, 'Accepted complex calibration source changed '+name)
    return n, dict(h=h,roles=R,circuit_sha256=logical['circuit_sha256'],
                   exact_output_nonzero_coefficients=audit['exact_output_nonzero_coefficients'],
                   logical_frames=audit['independent_logical_frames'],
                   unique_residual_norm_one_witnesses=audit['analytic_nonzero_residual_witnesses'],
                   terminal_complement_norm_one_witnesses=audit['analytic_complement_witnesses'],
                   forward_and_reverse_physical_transitions=audit['forward_and_reverse_physical_transitions'],
                   matching_images=v,complete_dirty_h8_basis_dimension=1019,
                   independent_role_rank_guard_and_log_formulas=True)


def strengthened_real_log_cutoff(row):
    eps, c = Q(row['parameters']['epsilon']), Q(row['parameters']['c'])
    k = ceil_q(1/(eps*c))
    L0 = row['cutoff_log2_b']['compact_controls']
    require(L0 == 64*k*k+1 and L0 >= 2*k, 'Executed compact cutoff changed')
    exact_slack = 2**(L0//k)-(32*L0+192)
    require(exact_slack > 0, 'Strengthened real-logarithm compact cutoff failed')
    # For real L=log2 b>=L0, 2^(L/k)/(32L+192) is increasing:
    # its logarithmic derivative is >=1/(2k)-1/L>0. Thus
    # K>=b^(epsilon*c)/4 >=8L+48. Also ceil(log2 p)<=L+4,
    # so G+4ceil(log2 p)+10=8ceil(log2 p)+16<=8L+48.
    return dict(status='PASS strengthened real-L comparison without changing the cutoff',
                L0=L0,k=k,denominator_slope=32,denominator_constant=192,
                exact_integer_slack=exact_slack,
                K_lower_bound='8*log2(b_input)+48',
                required_bound='8*ceil(log2(p))+16',
                real_log_ceiling='ceil(log2(p)) <= log2(b_input)+4, p=6*b_input')


def regress_fixed(previous, source_dir):
    for name, expected in previous['source_sha256'].items():
        require(sha(source_dir/name) == expected, 'Executed fixed compact source changed '+name)
    checks = []
    for row in previous['witnesses']:
        actual = compose(parse_counts(row['bit_counts']),parse_counts(row['complex_counts']),row['mode'],
                         Q(row['previous_accepted_kappa']))
        for group in ('parameters','recurrence','margins','constraint_slacks','cutoff_log2_b'):
            require(as_strings(actual[group]) == row[group], 'Fixed compact regression failed '+group)
        require(actual['minimum_margin'] == Q(row['minimum_margin']) and
                actual['scoped_model_upper'] == Q(row['scoped_model_upper']),
                'Fixed compact exact minimum/ceiling differs')
        checks.append(dict(mode=row['mode'],kappa=row['parameters']['kappa'],
                           unchanged_parameters_margins_slacks_cutoffs=True,
                           strengthened_cutoff=strengthened_real_log_cutoff(row)))
    return checks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original-upstream',type=Path,required=True)
    ap.add_argument('--compact-upstream',type=Path,required=True)
    ap.add_argument('--bit-candidate',type=Path,required=True)
    ap.add_argument('--bit-review',type=Path,required=True)
    ap.add_argument('--complex-candidate',type=Path,required=True)
    ap.add_argument('--complex-review',type=Path,required=True)
    ap.add_argument('--complex-calibration',type=Path,required=True)
    ap.add_argument('--previous-compact',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    require(not args.output.exists(), 'Use a fresh output path')
    started = time.monotonic()
    source_dir = Path(__file__).parent
    reference = check_sources(args.original_upstream)
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.compact_upstream,text=True).strip() == COMPACT_REVISION,
            'Wrong separately pinned compact input')
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=args.compact_upstream,text=True),
            'Compact input is no longer pristine')
    previous = json.loads(args.previous_compact.read_text())
    require(previous['original_reference']['commit'] == reference['commit'] and
            previous['compact_reference']['commit'] == COMPACT_REVISION,
            'Fixed compact input provenance differs')
    regressions = regress_fixed(previous,source_dir)
    bit_bytes = args.bit_candidate.read_bytes()
    n, bit_audit = promoted(json.loads(bit_bytes),json.loads(args.bit_review.read_text()),reference['commit'],bit_bytes)
    complex_bytes = args.complex_candidate.read_bytes()
    nc, complex_audit = complex_promotion(json.loads(complex_bytes),json.loads(args.complex_review.read_text()),
                                        json.loads(args.complex_calibration.read_text()),source_dir)
    old_kappa = max(Q(r['parameters']['kappa']) for r in previous['witnesses'])
    witnesses = [compose(n,nc,mode,Q(previous['witnesses'][0]['previous_accepted_kappa']))
                 for mode in ('conservative','tight')]
    for row in witnesses:
        row['strengthened_real_log_compact_cutoff'] = strengthened_real_log_cutoff(row)
        row['status'] = 'PASS exact separately promoted finite compact arithmetic; compact transfer review remains a separate dependency'
    tight = witnesses[1]
    require(tight['parameters']['kappa'] >= old_kappa, 'Fresh promoted inputs weakened the fixed compact witness')
    compact_certificate = args.compact_upstream/'certificates/compact-control-layer.json'
    regression = upstream_regression(json.loads(compact_certificate.read_text()))
    names = ['downstream_generic_compact_composition.py','downstream_compact_control_assembly.py',
             'downstream_promoted_complex_composition.py','downstream_complex_assembly.py',
             'downstream_complex_certificate.py','downstream_complex_circuit.py',
             'downstream_gaussian.py','downstream_parameter_optimum.py','review_complex_frames.py']
    inputs = [args.bit_candidate,args.bit_review,args.complex_candidate,args.complex_review,
              args.complex_calibration,args.previous_compact,compact_certificate]
    result = dict(status='PASS exact generic compact composition with independently promoted finite inputs',
                  campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                  campaign_deadline='2026-10-08T08:25:21Z',generated_at=datetime.now(timezone.utc).isoformat(),
                  original_reference=reference,compact_reference=previous['compact_reference'],
                  source_sha256={name:sha(source_dir/name) for name in names},
                  input_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in inputs},
                  promoted_bit_audit=bit_audit,promoted_complex_audit=complex_audit,
                  fixed_compact_regressions=regressions,upstream_compact_regression=regression,
                  witnesses=witnesses,previous_fixed_kappa=old_kappa,
                  strict_or_equal_kappa_ratio=tight['parameters']['kappa']/old_kappa,
                  ratio_decimal_lower=rational_decimal_lower(tight['parameters']['kappa']/old_kappa,15),
                  elapsed_seconds=time.monotonic()-started,
                  scope='Separately promoted finite inputs plus inherited phase inverse and new compact transfer; strengthened real-L cutoff; no formal proof, universal optimum or novelty claim')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print('PASS generic compact bit roles',bit_audit['roles'],'complex h',nc['h'],'roles',nc['R'],
          'kappa',tight['parameters']['kappa'],'common cutoff',tight['cutoff_log2_b']['common'],flush=True)


if __name__ == '__main__':
    main()
