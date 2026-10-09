#!/usr/bin/env python3
"""Small literal K/source/center/cap splice with retained dirty kernel data.

One k3 source cube and one proper j2 parity block are completed on h7.
The independent tree uses four extra helpers. The shared version mixes and
unmixes four existing center helpers at a cap before their full center use.
Both pay a complete rank-three copied-side read, all seven full center copies,
K/source cleanup and the complete original target/kernel fields. This is a
local component and a priced formation control, not a global side supplier.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import canonical_subspace_frames as frames
import scalable_subspace_interfaces as interfaces
import paired_five_cube_discriminator as paired


UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


class Stream:
    def __init__(self, bits, records):
        self.bits, self.records = bits, tuple(tuple(row) for row in records)
        self.normalize()

    def normalize(self):
        combined = 0
        for row in self.records:
            for value in row:
                combined |= abs(value)
        if not combined:
            self.bits = 0
        elif self.bits:
            shift = min(self.bits, (combined & -combined).bit_length() - 1)
            if shift:
                self.bits -= shift
                self.records = tuple(tuple(value >> shift for value in row) for row in self.records)
        return self

    def same(self, other):
        grid = max(self.bits, other.bits)
        return all(tuple(x << (grid - self.bits) for x in a) ==
                   tuple(x << (grid - other.bits) for x in b)
                   for a, b in zip(self.records, other.records))

    def scaled(self, c):
        c = Q(c)
        if c.denominator & (c.denominator - 1):
            raise AssertionError('The literal splice left Gaussian dyadics')
        return Stream(self.bits + c.denominator.bit_length() - 1,
                      [[c.numerator * x for x in row] for row in self.records])

    def plus(self, other, c=1):
        product = other.scaled(c)
        grid = max(self.bits, product.bits)
        return Stream(grid, [[(x << (grid - self.bits)) + (y << (grid - product.bits))
                              for x, y in zip(a, b)]
                             for a, b in zip(self.records, product.records)])


def unit_row(row, exponent):
    a, b = UNITS[exponent % 4]
    return tuple(value for field in range(4)
                 for value in (a * row[2 * field] - b * row[2 * field + 1],
                               a * row[2 * field + 1] + b * row[2 * field]))


def apply_word(stream, word, h):
    values = stream
    size = 1 << h
    for gate in word:
        kind = gate[0]
        if kind in ('D', 'Q'):
            q = interfaces.parse_quadratic(gate[1]) if kind == 'Q' else None
            values = Stream(values.bits, [unit_row(row, q.evaluate(x) if q else gate[1] * x.bit_count())
                                          for x, row in enumerate(values.records)])
        elif kind in ('P', 'NOT'):
            rows = [None] * size
            for x, row in enumerate(values.records):
                y = interfaces.embed(x, gate[1]) if kind == 'P' else x ^ gate[1]
                rows[y] = row
            values = Stream(values.bits, rows)
        elif kind in ('H', 'C'):
            mask = (1 << gate[1]) if kind == 'H' else gate[1]
            sign = gate[2]
            rows = [None] * size
            for x in range(size):
                y = x ^ mask
                if x > y:
                    continue
                left, right = values.records[x], values.records[y]
                a, b = [], []
                for field in range(4):
                    u, v, U, V = left[2 * field], left[2 * field + 1], right[2 * field], right[2 * field + 1]
                    if kind == 'C':
                        a.extend((u + U - sign * v + sign * V,
                                  v + V + sign * u - sign * U))
                        b.extend((u + U + sign * v - sign * V,
                                  v + V - sign * u + sign * U))
                    else:
                        # H_tilde=(1+sign*i)/2 times the real Hadamard.
                        a.extend((u + U - sign * (v + V), v + V + sign * (u + U)))
                        b.extend((u - U - sign * (v - V), v - V + sign * (u - U)))
                rows[x], rows[y] = a, b
            values = Stream(values.bits + 1, rows)
        else:
            raise AssertionError(('Unknown literal Gaussian gate', gate))
    return values


def build(shared):
    h, k, n = 7, 3, 8
    source_labels = [paired.cube_label(u, k) for u in range(n)]
    side_targets = [sum(1 << (2 * i + ((t >> i) & 1)) for i in range(2)) | (1 << 6)
                    for t in (0, 3)]
    target_labels = source_labels + side_targets
    G, R = n + len(target_labels), 2 * n + len(target_labels)
    side_sources = (0, 4, 3, 7)
    side_roles = [G + u for u in side_sources] if shared else list(range(R + 7, R + 11))
    roots = [side_roles[0], side_roles[2]]
    roles = R + 7 + (0 if shared else 4)
    full = frames.basis(1 << i for i in range(h))
    current = [frames.basis((S,)) for S in source_labels] + [()] * (roles - n)
    initial = list(current)
    events = []
    cap = frames.basis(source_labels[u] for u in side_sources)
    if len(cap) != 3 or any((a & T).bit_count() & 1 for a in cap for T in side_targets):
        raise AssertionError('The actual copied-side channel cap is wrong')

    def move(role, E, stage):
        E = frames.basis(E)
        if E != current[role]:
            events.append({'kind': 'frame', 'role': role, 'from': list(current[role]),
                           'to': list(E), 'stage': stage})
            current[role] = E

    def gate(kind, target, source, coefficient, stage):
        coefficient = Q(coefficient)
        if kind == 'add' and current[target] != current[source]:
            raise AssertionError('A scalar splice gate lacks identical actual frames')
        events.append({'kind': kind, 'target': target, 'source': source,
                       'coefficient': str(coefficient), 'stage': stage})

    def copy_read(root, targets, sign, stage):
        if any(current[target] for target, c in targets if Q(c)):
            raise AssertionError('The copied read lacks a common identity target cut')
        events.append({'kind': 'copy', 'root': root, 'root_subspace': list(current[root]),
                       'decoder': [(t, str(c)) for t, c in targets], 'sign': sign, 'stage': stage})

    def center_mix(sign, stage):
        for u, S in enumerate(source_labels):
            gate('add', R, G + u, sign, stage)
            for point in range(6):
                if S >> point & 1:
                    gate('add', R + 1 + point, G + u, sign, stage)

    def center_read(sign, stage):
        copy_read(R, [(n + t, Q(-1, 2)) for t in range(len(target_labels))], sign, stage)
        for point in range(6):
            copy_read(R + 1 + point,
                      [(n + t, Q(1, 2)) for t, T in enumerate(target_labels) if T >> point & 1], sign, stage)

    def tree(sign, stage):
        for a in range(0, 4, 2):
            gate('add', side_roles[a], side_roles[a + 1], sign, stage)

    C = [('add', 1, 0, Q(-1)), ('scale', 1, 1, Q(1, 2)),
         ('scale', 0, 0, Q(2)), ('add', 0, 1, Q(2)),
         ('add', 0, 1, Q(1)), ('add', 1, 0, Q(-1)),
         ('add', 0, 1, Q(1)), ('scale', 1, 1, Q(-1))]
    C_inverse = paired.inverse_word(C)
    if [paired.apply(C, [Q(i == j) for i in range(2)]) for j in range(2)] != [[Q(-1, 2), Q(1)], [Q(1, 2), Q(1)]]:
        raise AssertionError('The live row and its retained kernel completion changed')

    def complete(inverse, stage):
        for kind, target, source, coefficient in (C_inverse if inverse else C):
            gate(kind, roots[target], roots[source], coefficient, stage)

    center_mix(1, 'early center M'); center_read(-1, 'early center old read'); center_mix(-1, 'early center undo')
    tree(1, 'early side tree'); complete(False, 'early side completion')
    copy_read(roots[0], [(n + 8, 1), (n + 9, -1)], -1, 'early side old read')
    complete(True, 'early side inverse'); tree(-1, 'early side tree undo')
    for u, S in enumerate(source_labels):
        move(G + u, (S,), 'V before K'); gate('add', G + u, u, 1, 'V before K')
    if not shared:
        for role, u in zip(side_roles, side_sources):
            move(role, (source_labels[u],), 'V before K'); gate('add', role, u, 1, 'V before K')
    groups = [[paired.selector(a, k, p) for a in range(4)] for p in (0, 1)]
    for group in groups:
        U = frames.basis(source_labels[u] for u in group)
        for u in group:
            move(u, U, 'K entrance')
        for kind, a, b, c in paired.parity_word(k):
            gate(kind, group[a], group[b], c, 'K forward')
    for a in range(0, 4, 2):
        E = frames.basis(source_labels[side_sources[t]] for t in (a, a + 1))
        for t in (a, a + 1):
            move(side_roles[t], E, 'late side bucket')
        gate('add', side_roles[a], side_roles[a + 1], 1, 'late side tree')
    for role in side_roles:
        move(role, cap, 'late side cap')
    complete(False, 'late side completion')
    copy_read(roots[0], [(n + 8, 1), (n + 9, -1)], 1, 'paid cap copy read')
    complete(True, 'late side inverse'); tree(-1, 'late side tree undo')
    # Every kernel is restored before these same helpers are reused by the
    # full center mixer. They still contain z+x until final source cleanup.
    for role in set(list(range(G, G + n)) + side_roles):
        move(role, full, 'helpers full after side inverse')
    for role in range(R, R + 7):
        move(role, full, 'center roots direct full')
    center_mix(1, 'late full center M'); center_read(1, 'paid full center read'); center_mix(-1, 'late full center undo')
    for group in groups:
        for u in group:
            target = u ^ 4
            sink = frames.perpendicular((target_labels[target],), h)
            move(u, sink, 'K target continuation'); move(n + target, sink, 'K target continuation')
            gate('add', n + target, u, 1, 'literal K data contribution')
            move(u, full, 'original source full')
    for group in groups:
        for kind, a, b, c in paired.inverse_word(paired.parity_word(k)):
            gate(kind, group[a], group[b], c, 'K inverse at full')
    for u in range(n):
        gate('add', G + u, u, -1, 'uninject after K inverse')
    if not shared:
        for role, u in zip(side_roles, side_sources):
            gate('add', role, u, -1, 'uninject after K inverse')
    for t in (8, 9):
        move(n + t, frames.perpendicular((target_labels[t],), h), 'outside target final kernel')
    return events, {'h': h, 'k': k, 'j': 2, 'source_labels': source_labels,
                    'target_labels': target_labels, 'n': n, 'roles': roles,
                    'center_source_helpers': n, 'center_total_and_singleton_roots': 7,
                    'extra_side_source_helpers': 0 if shared else 4,
                    'side_helpers': side_roles, 'retained_kernel_role': roots[1],
                    'shared_after_inverse_cleanup': shared, 'side_cap': cap,
                    'initial_frames': initial, 'final_frames': current}


def scalar_matrix(events, roles):
    rows = [[Q(i == j) for j in range(roles)] for i in range(roles)]
    for event in events:
        if event['kind'] in ('add', 'scale'):
            i, j, c = event['target'], event['source'], Q(event['coefficient'])
            rows[i] = [a + c * b for a, b in zip(rows[i], rows[j])] if event['kind'] == 'add' else [c * x for x in rows[i]]
        elif event['kind'] == 'copy':
            for target, c in event['decoder']:
                rows[target] = [a + event['sign'] * Q(c) * b for a, b in zip(rows[target], rows[event['root']])]
    return rows


def execute(events, initial, h, normal_cache, reverse=False, negative=None):
    values = list(initial)
    for event in (reversed(events) if reverse else events):
        kind, stage = event['kind'], event['stage']
        if negative == 'missing_K_inverse' and stage == 'K inverse at full':
            continue
        if negative == 'missing_side_old' and stage == 'early side old read':
            continue
        if negative == 'missing_side_unmix' and stage == 'late side inverse':
            continue
        if kind == 'frame':
            E, F = tuple(event['from']), tuple(event['to'])
            if reverse:
                E, F = F, E
            values[event['role']] = apply_word(values[event['role']], normal_cache[E, F]['word'], h)
        elif kind in ('add', 'scale'):
            i, j, c = event['target'], event['source'], Q(event['coefficient'])
            if reverse:
                c = -c if kind == 'add' else 1 / c
            values[i] = values[i].plus(values[j], c) if kind == 'add' else values[i].scaled(c)
        else:
            E = tuple(event['root_subspace'])
            scratch = apply_word(values[event['root']], normal_cache[E, ()]['word'], h)
            sign = event['sign'] * (-1 if reverse else 1)
            for target, coefficient in event['decoder']:
                values[target] = values[target].plus(scratch, sign * Q(coefficient))
            del scratch  # Semantic complete-copy disposal; tape erasure stays paid.
    return values


def probe(shared):
    events, meta = build(shared)
    h, roles, n = meta['h'], meta['roles'], meta['n']
    expected_matrix = [[Q(i == j) for j in range(roles)] for i in range(roles)]
    for u in range(n):
        expected_matrix[n + u][u] += 1
    if scalar_matrix(events, roles) != expected_matrix:
        raise AssertionError('Complete retained source/target/dirty scalar columns differ from identity embedding')
    cache, profile = {}, Counter()
    for event in events:
        edges = [(tuple(event['from']), tuple(event['to']))] if event['kind'] == 'frame' else [(tuple(event['root_subspace']), ())] if event['kind'] == 'copy' else []
        for E, F in edges:
            rank = 2 * len(frames.basis(E + F)) - len(E) - len(F)
            if rank:
                profile[rank] += 1
            for A, B in ((E, F), (F, E)):
                if (A, B) not in cache:
                    normal = interfaces.compile_interface(A, B, h)
                    original = interfaces.inverse_word(interfaces.literal_word(A, h)) + interfaces.literal_word(B, h)
                    paulis = interfaces.assert_complete_tableau(normal, original)
                    cache[A, B] = {'normal': normal, 'word': interfaces.compiled_word(normal), 'Pauli_images': paulis}
    if any(width >= 3 * h for width in profile):
        raise AssertionError('A complete stream call became an improper master child')
    virtual = [Stream(4, [[(17 * role + 7 * address + 3 * component) % 37 - 18
                          for component in range(8)] for address in range(1 << h)])
               for role in range(roles)]
    initial = [apply_word(row, interfaces.literal_word(E, h), h)
               for row, E in zip(virtual, meta['initial_frames'])]
    desired_virtual = list(virtual)
    for u in range(n):
        desired_virtual[n + u] = desired_virtual[n + u].plus(virtual[u])
    desired = [apply_word(row, interfaces.literal_word(E, h), h)
               for row, E in zip(desired_virtual, meta['final_frames'])]
    actual = execute(events, initial, h, cache)
    if not all(a.same(b) for a, b in zip(actual, desired)):
        raise AssertionError('Literal four-field current-K/center/side physical splice failed')
    restored = execute(events, actual, h, cache, reverse=True)
    if not all(a.same(b) for a, b in zip(restored, initial)):
        raise AssertionError('Literal complete physical splice inverse failed')
    negatives = {}
    for name in ('missing_K_inverse', 'missing_side_old', 'missing_side_unmix'):
        wrong = execute(events, initial, h, cache, negative=name)
        if all(a.same(b) for a, b in zip(wrong, desired)):
            raise AssertionError(('An unpaid current-source/kernel response omission passed', name))
        negatives[name] = True
    complete_rank = sum(width * count for width, count in profile.items())
    expected_rank = h * roles - (n + len(meta['target_labels'])) + 7 * h + 3
    if complete_rank != expected_rank:
        raise AssertionError('A shared helper, full root/copy, cap copy or data endpoint was omitted')
    return {'kind': 'shared after inverse' if shared else 'independent source-tree control',
            'metadata': meta, 'complete_scalar_column_entries_checked': roles * roles,
            'literal_complete_four_field_real_imag_components_forward_and_reverse': 2 * 8 * roles * (1 << h),
            'unique_actual_interface_normal_forms': len(cache),
            'actual_Pauli_generator_images_checked': sum(row['Pauli_images'] for row in cache.values()),
            'complete_forward_child_profile': dict(profile), 'complete_forward_rank': complete_rank,
            'ambient_role_capacity_one_core': h * roles,
            'local_endpoint_discount': n + len(meta['target_labels']),
            'complete_center_copy_extra_rank': 7 * h,
            'complete_side_copy_extra_rank': 3,
            'native_workstream_copy_disposal_conditional': True,
            'side_copy_frame_has_radical': len(meta['side_cap']) - len(frames.basis(
                sum(((a & b).bit_count() & 1) << j for j, b in enumerate(meta['side_cap']))
                for a in meta['side_cap'])),
            'side_copy_uses_general_actual_frame_inverse_not_nonzero_Gram_assumption': True,
            'all_kernel_and_current_source_dirty_columns_retained': True,
            'source_injections_before_K_and_subtractions_after_K_inverse': True,
            'negative_controls': negatives, 'events': events,
            'actual_normal_forms': [row['normal'] for row in cache.values()],
            'scope': 'Complete finite k3 partial identity component, actual common frames and dense full fields. No full paired universe, whole canonical three-core master, fast cap formation or kappa. Sharing saves four ambient roles/rank together; paid side-copy rank remains.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker required')
    paths = [Path(__file__).resolve(), Path(frames.__file__).resolve(), Path(interfaces.__file__).resolve(), Path(paired.__file__).resolve()]
    frozen = {path: path.read_bytes() for path in paths}
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    tasks = [True] if args.bounded else [False, True]
    if args.workers == 1:
        rows = [probe(shared) for shared in tasks]
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(tasks))) as pool:
            rows = list(pool.map(probe, tasks))
    if any(path.read_bytes() != contents for path, contents in frozen.items()):
        raise AssertionError('Actual current-source/splice closure changed')
    result = {'status': 'PASS literal mixed-source K/center/cap splice with paid copies',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'workers': args.workers,
              'source_sha256': {path.name: sha256(contents).hexdigest() for path, contents in frozen.items()},
              'cases': rows, 'scope': 'Finite component with explicit extra stock/copies. Global cap repeated use/routing/precision/master transfer and kappa unverified'}
    result = paired_serializable(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'roles_and_rank': [(row['metadata']['roles'], row['complete_forward_rank']) for row in rows]}), flush=True)


def paired_serializable(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(key): paired_serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [paired_serializable(item) for item in value]
    return value


if __name__ == '__main__':
    main()
