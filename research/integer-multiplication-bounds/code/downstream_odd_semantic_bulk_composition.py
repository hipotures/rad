#!/usr/bin/env python3
"""Thin exact odd-ground bit composition using frozen semantic/bulk helpers.

An absent independent finite review is explicitly prospective. This
adapter changes no finite graph, complex circuit, or analytic estimate.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time

from downstream_gaussian import network_counts, require
from downstream_parameter_optimum import as_strings, saving_enclosure
from downstream_promoted_complex_composition import parse_counts
from downstream_semantic_bulk_assembly import witness


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_review(candidate, review, reference, candidate_bytes):
    require(review['status'] == 'PASS' and review['completed_utc'], 'Independent odd promotion is not terminal')
    require(review['reference_commit'] == reference and
            review['candidate_file_sha256'] == hashlib.sha256(candidate_bytes).hexdigest(),
            'Independent odd promotion input differs')
    full = review['full']
    require(full['h'] == candidate['h'] and full['compiled_roles'] == candidate['compiled_roles'] and
            full['candidate_id'] == candidate['candidate_id'] and
            full['compiled_sha256'] == candidate['checked']['compiled_sha256'],
            'Independent odd finite identity differs')
    require(full['matches_immutable_producer_identity_and_compilation'], 'Odd producer identity not independently matched')
    for group, fields in {
        'logical': ('all_additions_disjoint', 'all_global_coefficients_exact', 'all_source_spans_have_common_point'),
        'physical': ('cancellation_free_over_any_scalar_field', 'every_gate_output_exact', 'every_physical_target_exact'),
        'rational_frames': ('all_input_frames_original_lines', 'all_output_frames_exact',
                            'every_designated_target_orthogonal', 'forward_and_reverse_complement_nesting'),
        'controller_plan': ('all_links_same_source_and_acyclic', 'all_retained_labels_nested_by_equations'),
    }.items():
        require(all(full[group][key] for key in fields), 'Independent odd finite premise missing '+group)
    plan = full['controller_plan'];logical = full['logical'];r = full['compiled_roles']
    require(r == plan['independently_counted_roles'] == logical['additions'] + logical['outputs'] - plan['selected_links'],
            'Independent odd physical role count differs')
    matching = full['stage_matching']
    require(matching['intersection_one'] and matching['explicit_inverse_and_bijection'] and
            matching['rational_form_nondegenerate'] and matching['h'] == candidate['h'] and
            matching['triples'] == candidate['h'] * (candidate['h'] - 1) * (candidate['h'] - 2) // 6 and
            matching['image_sha256'] == candidate['stage_matching']['image_sha256'],
            'Independent odd stage matching differs')
    basis = exchanges = 0;dirty_directions = set()
    for small in review['small_controls']:
        for check in small['complete_invocation_dirty_basis_including_centers']:
            require(check['exact_linear_map'], 'Odd small dirty matrix failed')
            basis += check['input_basis_vectors']
            dirty_directions.add((small['h'], check['inverse']))
        for check in small.get('complete_shared_three_stage_exchange', []):
            require(check['complete_bank_exchange'] and check['arbitrary_auxiliary_banks_restored'],
                    'Odd full small exchange failed')
            exchanges += 1
    require({(7, False), (7, True), (11, False), (11, True)} <= dirty_directions and
            basis > 0 and exchanges >= 2, 'Odd complete small controls absent')
    return dict(status='INDEPENDENT FINITE PROMOTION PASS', h=full['h'], roles=r,
                candidate_id=full['candidate_id'], compiled_sha256=full['compiled_sha256'],
                dirty_basis_probes=basis, full_exchange_controls=exchanges)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--expected-candidate-id', required=True)
    p.add_argument('--candidate-review', type=Path)
    p.add_argument('--previous-semantic-bulk', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'Use a fresh output path')
    started = time.monotonic();source_dir = Path(__file__).parent
    old = json.loads(a.previous_semantic_bulk.read_text())
    for name, expected in old['source_sha256'].items():
        require(sha(source_dir / name) == expected, 'Frozen accepted source changed '+name)
    candidate_bytes = a.candidate.read_bytes();candidate = json.loads(candidate_bytes)
    require(candidate['candidate_id'] == a.expected_candidate_id, 'Unexpected odd finite candidate')
    h, R = candidate['h'], candidate['compiled_roles']
    require(h >= 11 and h % 2 == 1 and h != 9, 'Odd rational matching scope differs')
    reference = old['original_reference']['commit']
    identity = dict(h=h, base=candidate['base'], positions=candidate['positions'],
                    construction='odd_orphan_full_pair', reference_commit=reference)
    require(hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            == candidate['candidate_id'], 'Odd candidate canonical identity differs')
    for key in ('all_scalar_coefficients_exact', 'forward_frames_nested', 'reverse_complement_frames_nested'):
        require(candidate['checked'][key], 'Producer odd finite prerequisite missing '+key)
    n = network_counts(h, R);histogram = candidate['residual_rank_histogram']
    for key in ('h', 'm', 'N', 'W', 'L', 'D', 's'):
        require(histogram[key] == n[key], 'Actual odd physical histogram disagrees '+key)
    require(n['L'] == 3 * n['v']**2 * h**2, 'Bit center count must be h, not h+1')
    require(as_strings(saving_enclosure(n['eta'], n['m'])) == candidate['supported_uniform_shrink_saving'],
            'Producer odd primitive enclosure changed')
    matching = candidate['stage_matching']
    require(matching['triples'] == matching['distinct_images'] == n['v'] and
            matching['all_intersections_one'] and matching['explicit_inverse_verified'] and
            matching['ambient_rational_form_nondegenerate'], 'Producer odd constructive stage matching absent')
    audit = dict(status='FINITE INDEPENDENT PROMOTION PENDING', h=h, roles=R,
                 candidate_id=candidate['candidate_id'], compiled_sha256=candidate['checked']['compiled_sha256'])
    if a.candidate_review:
        audit = finite_review(candidate, json.loads(a.candidate_review.read_text()), reference, candidate_bytes)
    regressions = []
    for row in old['witnesses']:
        actual = witness(parse_counts(row['bit_counts']), parse_counts(row['complex_counts']),
                         row['mode'], row['prefix'], Q(row['previous_accepted_kappa']))
        for group in ('parameters', 'recurrence', 'margins', 'constraint_slacks', 'cutoff_log2_b'):
            require(as_strings(actual[group]) == row[group], 'Frozen semantic/bulk regression differs '+group)
        regressions.append(dict(mode=row['mode'], prefix=row['prefix'], kappa=row['parameters']['kappa'], unchanged=True))
    previous = max(Q(row['parameters']['kappa']) for row in old['witnesses'])
    nc = parse_counts(old['witnesses'][0]['complex_counts'])
    require(nc['h'] == 28 and nc['R'] == 97586 and nc['L'] == 3 * nc['v']**2 * 28 * 29,
            'This candidate composition retains the accepted original h28 complex input')
    rows = [witness(n, nc, mode, prefix, previous)
            for mode in ('conservative', 'tight') for prefix in ('original', 'balanced')]
    status = ('PASS EXACT ODD COMPOSITION; INDEPENDENT ASSEMBLY REVIEW REQUIRED' if a.candidate_review else
              'PASS PROSPECTIVE ODD ARITHMETIC; INDEPENDENT FINITE PROMOTION REQUIRED')
    for row in rows:
        row['status'] = status
    inputs = [a.candidate, a.previous_semantic_bulk] + ([a.candidate_review] if a.candidate_review else [])
    hashes = dict(old['source_sha256']);hashes[Path(__file__).name] = sha(Path(__file__))
    result = dict(status=status, campaign='20261007T222521Z', campaign_start='2026-10-07T22:25:21Z',
                  campaign_original_deadline='2026-10-08T08:25:21Z', campaign_deadline='2026-10-08T10:00:00Z',
                  generated_at=datetime.now(timezone.utc).isoformat(), original_reference=old['original_reference'],
                  compact_reference=old['compact_reference'], source_sha256=hashes,
                  input_files={str(path):dict(bytes=path.stat().st_size, sha256=sha(path)) for path in inputs},
                  odd_bit_finite_audit=audit, promoted_complex_audit=old['promoted_complex_audit'],
                  previous_accepted_kappa=previous, unchanged_regressions=regressions, witnesses=rows,
                  explicit_center_counts=dict(bit=h, bit_loss='3*v_bit^2*h_bit^2', complex=29,
                                              complex_loss='3*v_complex^2*h_complex*(h_complex+1)'),
                  scope='Fresh odd finite input with unchanged semantic/bulk proofs and original accepted complex h28; no graph replay or promotion from producer arithmetic alone',
                  elapsed_seconds=time.monotonic() - started)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True) + '\n')
    for row in rows:
        print(status, row['mode'], row['prefix'], row['parameters']['kappa'], row['cutoff_log2_b']['common'], flush=True)


if __name__ == '__main__':
    main()
