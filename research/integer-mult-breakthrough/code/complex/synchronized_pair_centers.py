#!/usr/bin/env python3
"""One source-copy per port, synchronized center roots and paid full copies.

All center roots follow a common growing actual address frame. One dirty
source helper visits its incident roots there, then retires at full. Complete
copy/transform/read/discard leaves each full root unchanged. The finite toy
executes all four Gaussian fields; paired cases count the exact geometry.
The copied-center native interface and whole master remain conditional.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

import canonical_subspace_frames as frames
import paired_five_cube_discriminator as paired
import scalable_subspace_interfaces as interfaces


def gadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def gmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def gscale(a, c):
    return c * a[0], c * a[1]


def apply_frame(E, h, columns, values, inverse=False):
    spec = frames.frame_matrix(E, h)
    matrix, denominator = spec['numerator'], 1 << spec['denominator_bits']
    result = [list(row) for row in values]
    mask = (1 << h) - 1
    for column in range(columns):
        incoming = [list(row) for row in result]
        for address in range(len(values)):
            output = (address >> (h * column)) & mask
            row = [(Q(0), Q(0)) for unused in range(4)]
            for source in range(1 << h):
                coefficient = matrix[source][output] if inverse else matrix[output][source]
                coefficient = (Q(coefficient[0], denominator), Q(-coefficient[1] if inverse else coefficient[1], denominator))
                if coefficient == (0, 0):
                    continue
                old_address = (address & ~(mask << (h * column))) | (source << (h * column))
                for field in range(4):
                    row[field] = gadd(row[field], gmul(coefficient, incoming[old_address][field]))
            result[address] = row
    return result


def execute(events, initial, h, columns, reverse=False, negative=None):
    values = [[list(row) for row in role] for role in initial]
    sequence = list(reversed(events)) if reverse else events
    full = frames.basis(1 << i for i in range(h))
    copy_records = copy_fields = 0
    for event in sequence:
        kind = event['kind']
        if kind == 'frame':
            old, new = event['from'], event['to']
            if reverse:
                old, new = new, old
            i = event['role']
            values[i] = apply_frame(new, h, columns, apply_frame(old, h, columns, values[i], True))
        elif kind == 'add':
            i, j, c = event['target'], event['source'], Q(event['coefficient'])
            if reverse:
                c = -c
            values[i] = [[gadd(a, gscale(b, c)) for a, b in zip(left, right)]
                         for left, right in zip(values[i], values[j])]
        else:
            sign = Q(event['sign']) * (-1 if reverse else 1)
            if negative == 'missing_old_response' and event['stage'] == 'early old scatter':
                continue
            # Own scratch is a complete copy, not an extra permanent dirty
            # scalar bank and not a spectator crop. Original root is retained.
            scratch = [list(row) for row in values[event['root']]]
            copy_records += len(scratch)
            copy_fields += 4 * len(scratch)
            if event['root_at_full'] and negative != 'missing_copy_transform':
                scratch = apply_frame(full, h, columns, scratch, True)
            if negative == 'cropped_complete_copy':
                scratch = [[row[0]] + [(Q(0), Q(0))] * 3 for row in scratch]
            for target, coefficient in event['decoder']:
                c = sign * Q(coefficient)
                values[target] = [[gadd(a, gscale(b, c)) for a, b in zip(left, right)]
                                  for left, right in zip(values[target], scratch)]
            del scratch
    return values, {'copied_complete_records': copy_records,
                    'copied_Gaussian_fields': copy_fields,
                    'owned_scratch_erased_after_each_read': True}


def toy_word(h=3):
    labels = [1, 7, 2]
    n, q = len(labels), 2
    incidence = [[1, 1, 0], [0, 1, 1]]
    decoder = [[Q(1, 4), Q(3, 8)], [Q(-1, 2), Q(1, 8)], [Q(3, 4), Q(-1, 4)]]
    G, R, total = 2 * n, 3 * n, 3 * n + q
    current = [frames.basis((label,)) for label in labels] + [()] * (2 * n + q)
    initial = list(current)
    events = []

    def move(i, E):
        E = frames.basis(E)
        if current[i] != E:
            events.append({'kind': 'frame', 'role': i, 'from': list(current[i]), 'to': list(E)})
            current[i] = E

    def add(i, j, c):
        if c:
            if current[i] != current[j]:
                raise AssertionError('Synchronized center scalar gate has unequal actual anchors')
            events.append({'kind': 'add', 'target': i, 'source': j, 'coefficient': str(c)})

    def mix(sign):
        for feature in range(q):
            for source in range(n):
                add(R + feature, G + source, sign * incidence[feature][source])

    def read(sign, full, stage):
        for feature in range(q):
            if current[R + feature] != (frames.basis(1 << i for i in range(h)) if full else ()):
                raise AssertionError('Center copy input has the wrong actual background')
            if any(current[n + t] for t in range(n)):
                raise AssertionError('Center copy scatter lacks common identity target cut')
            events.append({'kind': 'copy-transform-read-discard', 'root': R + feature,
                           'root_at_full': full, 'sign': sign, 'stage': stage,
                           'decoder': [(n + t, str(decoder[t][feature])) for t in range(n)]})

    mix(1); read(-1, False, 'early old scatter'); mix(-1)
    for s, label in enumerate(labels):
        move(G + s, (label,)); add(G + s, s, 1)
    E = ()
    full = frames.basis(1 << i for i in range(h))
    for source, label in enumerate(labels):
        E = frames.basis(E + (label,))
        for feature in range(q):
            move(R + feature, E)
        move(G + source, E)
        for feature in range(q):
            add(R + feature, G + source, incidence[feature][source])
        move(G + source, full)
    if E != full:
        raise AssertionError('Toy source labels do not span full')
    read(1, True, 'paid full center scatter')
    mix(-1)
    for source in range(n):
        move(source, full); add(G + source, source, -1)
    for target, label in enumerate(labels):
        move(n + target, frames.perpendicular((label,), h))
    return events, {'h': h, 'labels': labels, 'n': n, 'q': q, 'roles': total,
                    'incidence': incidence, 'decoder': decoder,
                    'initial_subspaces': initial, 'final_subspaces': current}


def expected_toy(meta, virtual, columns):
    n, q, h = (meta[k] for k in ('n', 'q', 'h'))
    values = [[list(row) for row in role] for role in virtual]
    central = [[sum(meta['decoder'][t][a] * meta['incidence'][a][s] for a in range(q))
                for s in range(n)] for t in range(n)]
    for t in range(n):
        for s in range(n):
            c = central[t][s]
            values[n + t] = [[gadd(a, gscale(b, c)) for a, b in zip(left, right)]
                             for left, right in zip(values[n + t], virtual[s])]
    return [apply_frame(E, h, columns, role) for E, role in zip(meta['final_subspaces'], values)]


def literal_toy(columns):
    events, meta = toy_word()
    h, roles = meta['h'], meta['roles']
    size = 1 << (h * columns)
    virtual = [[[(Q((13 * role + 7 * a + 3 * field) % 29 - 14, 8),
                  Q((11 * role + 5 * a + 7 * field) % 31 - 15, 16))
                 for field in range(4)] for a in range(size)] for role in range(roles)]
    initial = [apply_frame(E, h, columns, row) for E, row in zip(meta['initial_subspaces'], virtual)]
    actual, copy = execute(events, initial, h, columns)
    expected = expected_toy(meta, virtual, columns)
    if actual != expected:
        raise AssertionError('Literal synchronized center changed a physical source/sink/dirty field')
    restored, undo_copy = execute(events, actual, h, columns, True)
    if restored != initial:
        raise AssertionError('Literal complete center inverse did not restore every physical input')
    checked = 0
    if columns == 1:
        for role in range(roles):
            for address in range(size):
                x = [[[ (Q(0), Q(0)) for field in range(4)] for a in range(size)] for i in range(roles)]
                x[role][address][0] = (Q(1), Q(0))
                v = [apply_frame(E, h, columns, row, True) for E, row in zip(meta['initial_subspaces'], x)]
                out, unused = execute(events, x, h, columns)
                if out != expected_toy(meta, v, columns):
                    raise AssertionError('A retained independent physical column failed')
                checked += 1
    negatives = {}
    for negative in ('missing_copy_transform', 'cropped_complete_copy', 'missing_old_response'):
        corrupted, unused = execute(events, initial, h, columns, negative=negative)
        if corrupted == expected:
            raise AssertionError('An unpaid copy/old-response omission was accepted')
        negatives[negative] = True
    return {'kind': 'literal complete physical toy', 'h': h, 'selected_columns': columns,
            'address_layout': 'Literal column-major tensor order; native row-bit-major routing is not implemented by this toy',
            'source_labels': meta['labels'], 'persistent_source_copy_helpers': meta['n'],
            'persistent_center_roots': meta['q'], 'all_permanent_roles': roles,
            'complete_role_address_basis_columns': checked,
            'four_field_dense_components_compared_forward_and_reverse': 2 * 8 * size * roles,
            'copied_center_width_per_selected_column': h,
            'literal_C_tensor_factors_on_each_full_copy': h * columns,
            'full_copy_is_not_a_smaller_child_of_standalone_C_h': True,
            'copy_and_reverse_volume': {'forward': copy, 'reverse': undo_copy},
            'all_source_helper_root_dirty_values_restored_under_final_frames': True,
            'negative_controls': negatives,
            'scalar_and_frame_events': events,
            'scope': 'Literal Gaussian operator component, no whole canonical signed-SWAP/master or native copy implementation'}


def geometry(p):
    h = 2 * p
    labels = paired.labels(p, 5)
    v = len(labels)
    centers = [(i, j) for i in range(h) for j in range(i + 1, h) if i // 2 != j // 2]
    q = len(centers)
    histogram = Counter({1: v})
    E, stages = (), []
    scalar_additions = 0
    full = frames.basis(1 << i for i in range(h))
    representative_normals = []
    all_paulis = 0
    for source, label in enumerate(labels):
        F = frames.basis(E + (label,))
        if len(F) > len(E):
            histogram[len(F) - len(E)] += q
            normal = interfaces.compile_interface(E, F, h)
            actual = interfaces.inverse_word(interfaces.literal_word(E, h)) + interfaces.literal_word(F, h)
            all_paulis += interfaces.assert_complete_tableau(normal, actual)
            representative_normals.append(normal)
            stages.append({'first_source_index': source, 'old_dimension': len(E),
                           'new_dimension': len(F), 'new_subspace': list(F),
                           'simultaneously_moved_center_roots': q})
        if len(frames.basis(F + (label,))) != len(F):
            raise AssertionError('Current helper line lies outside the synchronized frame')
        if len(F) > 1:
            histogram[len(F) - 1] += 1
        if h > len(F):
            histogram[h - len(F)] += 1
        pair_count = len(list(combinations([i for i in range(h) if label >> i & 1], 2)))
        if pair_count != 10:
            raise AssertionError('A paired weight-five source does not have ten center writes')
        scalar_additions += pair_count
        E = F
    if E != full or q != 2 * p * (p - 1) or scalar_additions != 10 * v:
        raise AssertionError('The synchronized center stock or source span is incomplete')
    # Every original helper/root makes one monotone ambient traversal.
    # Each read-only full-root copy then pays one additional rank-h call.
    histogram[h] += q
    R = v + q
    loss = q * h
    total = sum(width * count for width, count in histogram.items())
    if total != h * R + loss:
        raise AssertionError('A shared helper, permanent root or full copy endpoint was omitted')
    return {'kind': 'paired synchronized center geometry', 'p': p, 'h': h,
            'original_sources': v, 'pair_center_roots': q,
            'persistent_source_copy_helpers': v, 'all_center_auxiliary_roles': R,
            'old_independent_center_copy_roles': 10 * v,
            'center_role_change': R - 10 * v,
            'copied_full_center_loss': loss,
            'old_pair_star_copied_loss': q * (h - 4),
            'loss_change': 4 * q,
            'complete_one_core_center_child_profile': dict(histogram),
            'complete_one_core_rank': total,
            'all_synchronized_center_sum_additions': scalar_additions,
            'conservative_four_M_and_inverse_passes': 4 * scalar_additions,
            'helper_source_injection_and_subtraction_gates': 2 * v,
            'two_signed_center_scatters': 2 * q * v,
            'full_copy_calls_per_core': q,
            'full_copy_selected_width': h,
            'proper_width_only_relative_to_master_m3h': 3 * h,
            'rank_growth_stages': stages,
            'root_growth_actual_interface_Pauli_images_checked': all_paulis,
            'root_growth_actual_interface_normal_forms': representative_normals,
            'all_helper_lines_and_full_returns_binary_checked': v,
            'individual_full_gaussian_helper_interfaces_replayed': False,
            'common_frame_invariant': 'Every root and current helper use the identical actual F_E at every center write; roots all finish at full before paid copying',
            'temporary_complete_copy_contract': 'Sequential complete role stream, one C_h inverse on the copy, all target reads at identity, copy and erasure charged linearly; original root remains at full. Native contract remains conditional.',
            'own_root_and_source_ancestor_old_responses_retained': True,
            'new_fixed_odd_divisor5_bridge_inherited_unchanged_as_obligation': True,
            'scope': 'Exact paired center geometry and scalar recipe counts, with independently supplied full-copy interface and whole completed-core lift still required'}


def run(task):
    kind, value = task
    return literal_toy(value) if kind == 'toy' else geometry(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    paths = [Path(__file__).resolve(), Path(frames.__file__).resolve(), Path(paired.__file__).resolve(), Path(interfaces.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    tasks = [('toy', 1), ('paired', 7)] if args.bounded else [('toy', 1), ('toy', 2), ('paired', 7), ('paired', 9), ('paired', 12)]
    if args.workers == 1:
        rows = [run(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(run, tasks))
    if any(p.read_bytes() != b for p, b in frozen.items()):
        raise AssertionError('Effective synchronized-center source closure changed')
    result = {'status': 'PASS literal synchronized-center component and exact paired role/profile geometry',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {p.name: sha256(b).hexdigest() for p, b in frozen.items()},
              'cases': rows,
              'scope': 'Fresh center-only component. Full-copy width h is proper only in a larger m3h master. Side aggregation, whole canonical primitive, fixed-tape/precision/copy integration and an exponent are not verified.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'toy_columns': [r['selected_columns'] for r in rows if r['kind'].startswith('literal')],
                      'paired_roles': [(r['p'], r['all_center_auxiliary_roles']) for r in rows if r['kind'].startswith('paired')]}), flush=True)


if __name__ == '__main__':
    main()
