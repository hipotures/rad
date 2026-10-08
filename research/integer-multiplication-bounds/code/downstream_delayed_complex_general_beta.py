#!/usr/bin/env python3
"""Thin general-beta composition of the independently promoted R88377 complex.

The accepted R485680 generic bit input and full old parameter interface are
unchanged. New physical complex counts and literal logical-G/E are read
from the independent changed-witness certificate, not renamed by roles.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import require
from downstream_general_beta_semantic_bulk import general_witness
from downstream_parameter_optimum import as_strings, saving_enclosure
from downstream_promoted_complex_composition import parse_counts


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def check_changed_complex(peer, source_dir):
    require(peer['status'] ==
            'PASS independent binary delayed-clone theorem and complete changed h28 witness',
            'Independent changed binary complex theorem/full-witness acceptance absent')
    for name, digest in peer['source_sha256'].items():
        require(sha(source_dir/name) == digest, 'Independent complex source differs '+name)
    theorem = peer['binary_interval_theorem']
    require(theorem['admitted_nested_interval_predicate_is_transitive'] and
            peer['new_cloner_and_selector_not_imported'] and
            peer['original_accepted_physical_program_not_replayed'],
            'Independent interval theorem/changed graph audit scope differs')
    small = peer['small'];dirty = small['complete_dirty_basis'];exchange = small['complete_shared_exchange']
    require(small['h'] == 8 and dirty['complete_basis_dimension'] == 939 and
            dirty['forward_identity_shear_and_inverse_exact'] and
            dirty['includes_both_data_banks_all_side_and_central_scratch'] and
            exchange['all_data_outputs_exact'] and exchange['all_dirty_banks_restored_exactly'] and
            exchange['middle_chronology_reversed_and_inverted'],
            'Complete changed h8 dirty/shared chronology control absent')
    full = peer['full'];h = full['h'];roles = full['actual_plan']['exact_roles']
    require((h, roles) == (28, 88377), 'This adapter pins the promoted complex R88377')
    v = comb(h, 3);m = h**3;N = v**3
    W = 2*N+2*v*v*(roles+h+1);L = 3*v*v*h*(h+1);D = 2*N-2*L;s = W*m-D
    n = dict(h=h, v=v, m=m, N=N, R=roles, W=W, L=L, D=D, s=s, eta=Q(D, W*m))
    require({k: n[k] for k in full['counts']} == full['counts'] and D > 0,
            'Actual changed complex counts differ from complete physical formula')
    logical = full['complete_changed_logical'];physical = full['physical'];plan = full['actual_plan']
    c = logical['additions'];links = plan['links']
    require(c+v == logical['logical_frames'] and c+2*v-links == roles and
            full['clones'] == c-91034 and links == plan['separate_gate_capacities'] and
            plan['all_equal_source_nondegenerate_nonalternating_intervals_exact'] and
            full['all_actual_source_gates_sinks_and_reverse_complements_admitted'] and
            full['exact_closed_forward_role_rank'] == h*roles,
            'Actual changed logical/plan/frame rank identity differs')
    for key in ('all_changed_formal_coefficients_and_zeros_exact',
                'all_formal_edges_admitted_by_independent_gram',
                'all_original_input_lines_and_actual_enlarged_frames_valid'):
        require(logical[key], 'Independent changed logical witness failed '+key)
    for key in ('all_copy_outputs_source_lines_and_target_kernels_valid',
                'all_nonzero_forward_reverse_residuals_have_norm_one_witness',
                'all_scalar_coefficients_exact_without_modular_cancellation'):
        require(physical[key], 'Independent complete physical complex witness failed '+key)
    require(full['compiled_sha256'] == physical['compiled_sha256'] and
            full['matching']['exact_orthogonal_involution'] and
            full['matching']['all_join_residuals_have_coordinate_norm_one_witness'] and
            full['matching']['triples'] == v and
            full['matching']['joined_residual_dimension'] == m-2*h,
            'Changed physical identity or shared-bank matching differs')
    G = 3*v*v*(4*(c+v)+4*v+4);E = 64*(W+m+1)**3
    depth = 2*G*W*W+4*s+4*W+4;guard = full['guard']
    require(G == guard['actual_grouped_scalar_gates'] and E == guard['additive_E'] and
            depth == guard['exact_operation_depth_bound'] and
            E-depth == guard['slack'] > 0,
            'Actual added-clone scalar gates were not charged by literal E')
    saving = saving_enclosure(n['eta'], m)
    require(saving['chosen_saving'] < Q(full['saving']['lower']) and
            Q(full['saving']['explicit_strict_saving']) < Q(full['saving']['lower']) and
            full['saving']['producer_explicit_saving_independently_accepted'],
            'Independent longer complex logs do not cover this strict primitive')
    return n, G, dict(
        status='INDEPENDENT CHANGED BINARY COMPLEX FINITE/SCALAR/GUARD PASS',
        candidate_id=peer['candidate_id'], compiled_sha256=physical['compiled_sha256'],
        h=h, roles=roles, clones=full['clones'], links=links,
        actual_logical_additions=c, actual_grouped_scalar_gates=G,
        exact_literal_depth=depth, exact_guard_slack=E-depth,
        counts=n, complete_changed_h8_dirty_basis=939,
        actual_frames='Inherited first-consumer binary frames; no rational-envelope substitution',
        old_six_W_condition=G < 6*W,
        whole_rank_complex_calls_used=False,
        all_size_interval_theorem=theorem,
        independent_source_sha256=peer['source_sha256'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--previous-assembly', type=Path, required=True)
    ap.add_argument('--previous-final-review', type=Path, required=True)
    ap.add_argument('--changed-complex-review', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args();require(not args.output.exists(), 'Use a fresh output path')
    t0 = time.monotonic();source_dir = Path(__file__).parent
    old = json.loads(args.previous_assembly.read_text())
    final = json.loads(args.previous_final_review.read_text())
    peer = json.loads(args.changed_complex_review.read_text())
    for name, digest in old['source_sha256'].items():
        require(sha(source_dir/name) == digest, 'Frozen old producer source differs '+name)
    for name, digest in final['reviewer_source_sha256'].items():
        require(sha(source_dir/name) == digest, 'Accepted final checker source differs '+name)
    require(final['status'] == 'PASS independent complete generic-basis general-beta conditional assembly' and
            final['fixed_general_stopping_and_deeper_row_interfaces_reviewed'] and
            final['input_sha256'][str(args.previous_assembly.resolve())] == sha(args.previous_assembly),
            'Previous complete generic/general-beta witness is not independently accepted')
    previous = max(Q(row['kappa']) for row in final['rows'])
    require(previous == max(Q(row['parameters']['kappa']) for row in old['witnesses']),
            'Accepted complete previous kappa differs')
    n = parse_counts(old['witnesses'][0]['bit_counts'])
    primitive = old['generic_characteristic_certificate']['witness']
    require(final['unchanged_finite_identity'] == old['odd_bit_finite_audit'] and
            Q(final['exact_primitive_audit']['chosen_saving']) == Q(primitive['saving']),
            'Promoted generic bit identity/primitive differs')
    regressions = []
    for row in old['witnesses']:
        nc = parse_counts(row['complex_counts'])
        regenerated = general_witness(n, nc, row['mode'], row['prefix'],
                                      Q(row['previous_accepted_kappa']), primitive,
                                      row['semantic_guard']['scalar_gates'])
        for key in ('parameters', 'recurrence', 'margins', 'constraint_slacks',
                    'cutoff_log2_b', 'stopped_leaf_certificate', 'compact_row_padding'):
            require(as_strings(regenerated[key]) == row[key],
                    'Accepted general-beta predecessor regression differs '+key)
        regressions.append(dict(complex_input=row['complex_input'], mode=row['mode'],
                                prefix=row['prefix'], kappa=row['parameters']['kappa'], unchanged=True))
    nc, G, audit = check_changed_complex(peer, source_dir)
    rows = []
    for mode in ('conservative', 'tight'):
        for prefix in ('original', 'balanced'):
            row = general_witness(n, nc, mode, prefix, previous, primitive, G)
            row['complex_input'] = 'delayed88377'
            row['native_bit_primitive'] = old['witnesses'][0]['native_bit_primitive']
            row['uniform_complex_transfer'] = 'Original complete individual-rank complex children; no whole-rank grouping'
            rows.append(row)
    hashes = dict(old['source_sha256']);hashes[Path(__file__).name] = sha(Path(__file__))
    result = dict(
        status='PASS STRICT CONDITIONAL DELAYED-COMPLEX GENERAL-BETA ASSEMBLY; INDEPENDENT FINAL REVIEW REQUIRED',
        campaign_start='2026-10-07T22:25:21Z', campaign_original_deadline='2026-10-08T08:25:21Z',
        campaign_deadline='2026-10-08T10:00:00Z', generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=hashes,
        input_files={str(p): dict(bytes=p.stat().st_size, sha256=sha(p)) for p in
                     (args.previous_assembly, args.previous_final_review, args.changed_complex_review)},
        previous_accepted_kappa=previous,
        previous_complete_review_sha256=sha(args.previous_final_review),
        accepted_general_beta_regressions=regressions,
        odd_bit_finite_audit=old['odd_bit_finite_audit'],
        generic_characteristic_certificate=old['generic_characteristic_certificate'],
        changed_complex_finite_audit=audit,
        changed_complex_independent_review_sha256=sha(args.changed_complex_review),
        unchanged_generic_root_inputs_sha256=old['root_generic_inputs_sha256'],
        witnesses=rows, elapsed_seconds=time.monotonic()-t0,
        scope='New independently promoted binary R88377 complex graph and actual logical-G/E; retained complete uniform complex transfer, generic R485680 bit basis and general-beta inequalities. Whole-rank complex children are not used. Giant bit basis/table/prime and strict absorption remain separately eventual.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
    for row in rows:
        print(result['status'], row['mode'], row['prefix'], row['parameters']['kappa'],
              row['cutoff_log2_b']['common'], flush=True)


if __name__ == '__main__':
    main()
