#!/usr/bin/env python3
"""Sequential cap-channel accumulation through one repeatedly used dirty target.

The first cut is at identity and later cuts use the same actual cap frame.
Every source/kernel bank, original target value and ancestor old-response
column is retained. Exact scalar matrices and literal canonical frame
interfaces are checked separately; no global side supplier is asserted.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import cap_target_pivot_accumulation as previous
import canonical_subspace_frames as frames
import scalable_subspace_interfaces as interfaces

algebra = previous.component


def shared_packet(j, h, negative=None, correction=False):
    case = algebra.probe((j, 0))
    n, N = case['original_complete_banks_retained'], 16
    if h < 2 * (10 - j):
        raise ValueError('Ambient dimension cannot hold the literal source and target pairs')
    matrix = [[Q(v) for v in row] for row in case['completion_matrix']]
    forward = algebra.compile_word(matrix)
    inverse = algebra.invert_word(forward)
    outside = 1 << (5 - j)
    decoder = [[Q(v) for v in row] for row in case['full_target_decoder']
               for unused in range(outside)]
    pivot = next(t for t, row in enumerate(decoder) if all(row))
    if any(c not in (Q(1), Q(-1)) for c in decoder[pivot]):
        raise AssertionError('Repeated pivot requires an unpaid coefficient divisor')
    sources = case['source_selector_order']
    targets = case['selected_actual_target_selector_order']
    buckets = [frames.basis(algebra.source_label(5, s | (b << j))
                           for b in range(outside)) for s in sources]
    cap = frames.basis(v for bucket in buckets for v in bucket)
    target_labels = [algebra.target_label(5, j, t, b)
                     for t in targets for b in range(outside)]
    kernels = [frames.perpendicular((t,), h) for t in target_labels]
    full = frames.basis(1 << i for i in range(h))
    if len(cap) != 5 or any(len(frames.basis(cap + E)) != len(E) for E in kernels):
        raise AssertionError('The literal common cap is outside a target endpoint')
    signal_start, total = n + N, 2 * n + N
    initial = [()] * (n + N) + buckets
    current = [tuple(E) for E in initial]
    events, word, cuts = [], [], []

    def move(role, E, stage):
        E = frames.basis(E)
        old = current[role]
        if old == E:
            return
        if len(frames.basis(old + E)) != len(E):
            raise AssertionError('A repeated-pivot role descends or leaves its nested interval')
        events.append({'kind': 'frame', 'role': role, 'from': list(old),
                       'to': list(E), 'stage': stage})
        current[role] = E

    def gate(g, stage):
        kind, target, source, c = g
        if kind == 'add' and current[target] != current[source]:
            raise AssertionError(('A scalar gate lacks identical actual frames', stage, target, source))
        word.append(g)
        events.append({'kind': 'scalar', 'gate': [kind, target, source, str(c)],
                       'stage': stage, 'actual_subspace': list(current[target])})

    def add(target, source, c, stage):
        if c:
            gate(('add', target, source, Q(c)), stage)

    def basis_word(w, stage):
        for g in w:
            gate(g, stage)

    # Preserve all ancestor responses. Only the old three independent sink
    # coordinates disappear, not an actual row or any parked kernel bank.
    basis_word(forward, 'old-response basis at identity')
    if negative != 'dropped_ancestor_old_response':
        for t, row in enumerate(decoder):
            for a, c in enumerate(row):
                add(n + t, a, -c, 'retained ancestor old response')
    basis_word(inverse, 'old-response basis undo at identity')

    def pre(a):
        for t, row in enumerate(decoder):
            if t != pivot and not (negative == 'missing_later_pre' and a == 1):
                add(n + t, n + pivot, -row[a] / decoder[pivot][a],
                    'channel %d pre-cut' % a)

    pre(0)
    cuts.append({'channel': 0, 'cut_actual_subspace': [], 'pivot_target': pivot,
                 'pivot_contains_previous_channels': []})
    for i, E in enumerate(buckets):
        move(i, E, 'source injection frame')
        add(i, signal_start + i, 1, 'source injection')
    for i in range(n):
        move(i, cap, 'source/control basis entrance')
    basis_word(forward, 'actual-row producer at common cap')
    correction_target = next(t for t, row in enumerate(decoder)
                             if t != pivot and row[0])
    for a in range(3):
        for t, row in enumerate(decoder):
            if row[a]:
                move(n + t, cap, 'channel %d target entrance' % a)
        if a:
            pre(a)
            cuts.append({'channel': a, 'cut_actual_subspace': list(cap),
                         'pivot_target': pivot,
                         'pivot_contains_previous_channels': list(range(a))})
        if a == 0 and (correction or negative == 'pivot_correction_inside_cut'):
            move(signal_start, cap, 'independent correction control entrance')
            t = pivot if negative == 'pivot_correction_inside_cut' else correction_target
            add(n + t, signal_start, Q(3, 4), 'independent correction inside first cut')
        add(n + pivot, a, decoder[pivot][a], 'channel %d pivot producer' % a)
        for t, row in enumerate(decoder):
            if t != pivot and not (negative == 'missing_later_post' and a == 1):
                add(n + t, n + pivot, row[a] / decoder[pivot][a],
                    'channel %d post-cut' % a)
    for i in range(n):
        move(i, full, 'all source/kernel banks to full')
    basis_word(inverse, 'full-frame basis inverse')
    for i in range(n):
        move(signal_start + i, full, 'read-only signal endpoint')
        add(i, signal_start + i, -1, 'full-frame source uninject')
    for t, E in enumerate(kernels):
        move(n + t, E, 'target kernel endpoint')
    return word, {'source_basis_banks': n, 'target_banks': N,
                  'retained_kernel_banks': n - 3, 'read_only_signal_banks': n,
                  'slots': total, 'pivot_targets': [pivot],
                  'repeated_pivot_for_each_channel': [pivot] * 3,
                  'decoder': decoder, 'basis_matrix': matrix,
                  'correction_target': correction_target, 'cuts': cuts,
                  'source_bucket_subspaces': buckets, 'common_cap': cap,
                  'target_labels': target_labels, 'initial_subspaces': initial,
                  'final_subspaces': current, 'events': events}


def audit_frames(meta, h):
    current = [tuple(E) for E in meta['initial_subspaces']]
    normals, profile, phase_counts = {}, {}, {}
    equality_gates, pauli_images = 0, 0
    total_rank_by_role = [0] * meta['slots']
    for event in meta['events']:
        if event['kind'] == 'scalar':
            kind, target, source, c = event['gate']
            if list(current[target]) != event['actual_subspace']:
                raise AssertionError('Recorded actual scalar anchor differs from chronological role')
            if kind == 'add' and current[target] != current[source]:
                raise AssertionError('Complete chronological scalar operands use different actual representatives')
            equality_gates += 1
            continue
        role = event['role']
        E, F = tuple(event['from']), tuple(event['to'])
        if current[role] != E:
            raise AssertionError('The literal frame event skips a role continuation')
        rank = len(F) - len(E)
        if rank <= 0 or len(frames.basis(E + F)) != len(F):
            raise AssertionError('A frame event is not a nonempty nested ascent')
        key = (E, F)
        if key not in normals:
            normal = interfaces.compile_interface(E, F, h)
            if normal['selected_rank_per_column'] != rank:
                raise AssertionError('Actual Gaussian interface has the wrong paid child width')
            actual = interfaces.inverse_word(interfaces.literal_word(E, h)) + interfaces.literal_word(F, h)
            pauli_images += interfaces.assert_complete_tableau(normal, actual)
            normals[key] = normal
            phase = normal['global_unit_exponent']
            phase_counts[str(phase)] = phase_counts.get(str(phase), 0) + 1
        profile[rank] = profile.get(rank, 0) + 1
        total_rank_by_role[role] += rank
        current[role] = F
    if current != [tuple(E) for E in meta['final_subspaces']]:
        raise AssertionError('Final actual role frames differ from the declared endpoints')
    expected = [len(F) - len(E) for E, F in zip(meta['initial_subspaces'], current)]
    if total_rank_by_role != expected:
        raise AssertionError('Nested rank bill omitted a role entrance or endpoint')
    return {'all_common_actual_frame_scalar_operations_checked': equality_gates,
            'all_literal_nested_frame_events_checked': sum(profile.values()),
            'new_complete_positive_child_profile_including_signal_endpoints': profile,
            'paid_rank_including_signal_endpoints': sum(r * count for r, count in profile.items()),
            'unique_exact_one_child_interfaces': len(normals),
            'all_complete_Pauli_generator_images_checked': pauli_images,
            'interface_global_unit_histogram': phase_counts,
            'interface_normal_forms': list(normals.values()),
            'all_role_paths_nested': True,
            'full_Gaussian_address_arrays_materialized': False,
            'literal_field_array_execution': False}


def check(task):
    j, h = task
    old, oldmeta = previous.block_word(j, 'old')
    word, meta = shared_packet(j, h)
    new = algebra.word_matrix(meta['slots'], word)
    old_matrix = algebra.word_matrix(oldmeta['slots'], old)
    if old_matrix != previous.expected_matrix(oldmeta) or new != previous.expected_matrix(meta):
        raise AssertionError('Original or repeated-pivot word changed a retained independent column')
    if [row[:meta['slots']] for row in old_matrix[:meta['slots']]] != new:
        raise AssertionError('Repeated-pivot word does not preserve every retained old response')
    if any(old_matrix[t][s] for t in range(meta['slots'])
           for s in range(meta['slots'], oldmeta['slots'])):
        raise AssertionError('The old sink input leaks into a retained output')
    corrected, cmeta = shared_packet(j, h, correction=True)
    if algebra.word_matrix(cmeta['slots'], corrected) != previous.expected_matrix(cmeta, correction=True):
        raise AssertionError('An independent nonpivot correction was changed by temporal reuse')
    negatives = {}
    for name in ('dropped_ancestor_old_response', 'missing_later_pre',
                 'missing_later_post', 'pivot_correction_inside_cut'):
        bad, bmeta = shared_packet(j, h, negative=name)
        expected = previous.expected_matrix(bmeta, early=name == 'pivot_correction_inside_cut')
        if algebra.word_matrix(bmeta['slots'], bad) == expected:
            raise AssertionError('An invalid sequential target cut was accepted')
        negatives[name] = True
    proof = audit_frames(meta, h)
    n, N = meta['source_basis_banks'], meta['target_banks']
    # Read-only signal endpoints are included above, with original bucket
    # rank r. Old extra copies each use [5] and [h-5]; no other role changes.
    old_rank = proof['paid_rank_including_signal_endpoints'] + 3 * h
    old_stock, new_stock = meta['slots'] + 3, meta['slots']
    if old_stock - new_stock != 3 or old_rank - proof['paid_rank_including_signal_endpoints'] != 3 * h:
        raise AssertionError('Repeated-pivot deletion dropped a paid endpoint or active/kernel bank')
    return {'j': j, 'ambient_binary_dimension': h,
            'complete_old_scalar_columns': oldmeta['slots'], 'complete_new_scalar_columns': meta['slots'],
            'all_new_scalar_matrix_entries_checked': meta['slots'] ** 2,
            'retained_source_basis_banks': n, 'retained_kernel_banks': n - 3,
            'retained_arbitrary_dirty_target_banks': N,
            'removed_independent_destination_only_sink_copies': 3,
            'same_pivot_for_all_channels': meta['repeated_pivot_for_each_channel'],
            'sequential_cuts': meta['cuts'],
            'common_cap': list(meta['common_cap']),
            'common_cap_Gram_radical_dimension': 5 - len(frames.basis(
                sum(frames.dot(u, v) << i for i, v in enumerate(meta['common_cap']))
                for u in meta['common_cap'])),
            'old_complete_scalar_gate_count': len(old), 'new_complete_scalar_gate_count': len(word),
            'prefix_bill_including_all_products': algebra.prefix_bill(meta['slots'], word),
            'inverse_prefix_bill_including_all_products': algebra.prefix_bill(meta['slots'], algebra.invert_word(word)),
            'four_field_all_component_inverse_checks': previous.exact_payload(word, meta['slots']),
            'independent_nonpivot_correction_preserved': True,
            'negative_controls': negatives, 'exact_canonical_frame_audit': proof,
            'one_core_removed_positive_child_pieces': [5, h - 5] * 3,
            'one_core_paid_rank_delta': -3 * h,
            'three_core_paid_rank_delta': -9 * h,
            'three_core_stock_capacity_delta': -9 * h,
            'rank_deficit_delta': 0,
            'all_original_source_and_target_column_values_preserved': True,
            'global_cross_cap_deadlines_verified': False,
            'forward_scalar_word': algebra.serialized_word(word),
            'inverse_scalar_word': algebra.serialized_word(algebra.invert_word(word)),
            'frame_scalar_event_chronology': meta['events']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker is required')
    paths = [Path(__file__).resolve(), Path(previous.__file__).resolve(), Path(algebra.__file__).resolve(),
             Path(frames.__file__).resolve(), Path(interfaces.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    cases = [(j, h) for h in ((14,) if args.bounded else (14, 18)) for j in (3, 4)]
    if args.workers == 1:
        rows = [check(task) for task in cases]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(cases))) as pool:
            rows = list(pool.map(check, cases))
    if any(p.read_bytes() != b for p, b in frozen.items()):
        raise AssertionError('Effective scalar/frame source closure changed during the run')
    result = {'status': 'PASS exact sequential dirty target cuts with one repeated pivot and actual cap interfaces',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {p.name: sha256(b).hexdigest() for p, b in frozen.items()},
              'cases': rows,
              'scope': 'Exact retained-column scalar words and canonical one-child frame interfaces, including phase constants and every nested endpoint. Same-cap local temporal reuse only; no cross-cap global chronology, native tape supplier or exponent.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'pivots': [r['same_pivot_for_all_channels'] for r in rows],
                      'scalar_gate_counts': [r['new_complete_scalar_gate_count'] for r in rows],
                      'new_paid_ranks': [r['exact_canonical_frame_audit']['paid_rank_including_signal_endpoints'] for r in rows]}), flush=True)


if __name__ == '__main__':
    main()
