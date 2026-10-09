#!/usr/bin/env python3
"""Synchronized quotient roots and paid rank-one singleton read copies.

This complete finite formation component lifts pure direct source fanout.
Every extra persistent quotient root and complete owned copy is retained.
Higher-overlap aggregates, full side/master integration and native copy
time/erasure are not supplied by this component.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import singleton_fanout_release_probe as geometry

TOPIC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOPIC / 'code/complex'))
import scalable_subspace_interfaces as interface

PINS = {
    'singleton_fanout_release_probe.py': 'fec8292dd3fad1c1e008b543bfefc448d51648068ebdb32ea123959a27ff5746',
    'scalable_subspace_interfaces.py': '3da400b0b157cc28b546113e63a150e4b1672c71a5f2c74e724ac8fc3d1f4851',
    'canonical_subspace_frames.py': 'ddb0255a0668d43dd61c5183f3a0de56015f02b6acc462c4b8ad5b3f8173598b'}


def normalize(values, grid):
    while grid and all(not x & 1 for row in values for x in row):
        values = [tuple(x // 2 for x in row) for row in values]
        grid -= 1
    return tuple(values), grid


def plus(left, right, sign=1):
    p = max(left[1], right[1])
    a, b = p - left[1], p - right[1]
    return normalize([tuple((x << a) + sign * (y << b) for x, y in zip(u, v))
                      for u, v in zip(left[0], right[0])], p)


def phase(row, exponent):
    exponent %= 4
    result = []
    for j in range(0, len(row), 2):
        a, b = row[j:j + 2]
        result.extend(((a, b), (-b, a), (-a, -b), (b, -a))[exponent])
    return tuple(result)


def embed(x, columns):
    value = 0
    for j, column in enumerate(columns):
        if x >> j & 1:
            value ^= column
    return value


@lru_cache(None)
def local_map(columns, h):
    return tuple(embed(x, columns) for x in range(1 << h))


@lru_cache(None)
def quadratic_values(serialized, h):
    q = interface.parse_quadratic(json.loads(serialized))
    return tuple(q.evaluate(x) for x in range(1 << h))


def apply_word(bank, word, h, columns):
    values, grid = bank
    if not any(x for row in values for x in row):
        return bank
    mask = (1 << h) - 1
    for gate in word:
        for column in range(columns):
            shift = h * column
            kind = gate[0]
            if kind in ('D', 'Q'):
                q = quadratic_values(json.dumps(gate[1], sort_keys=True), h) if kind == 'Q' else None
                values = tuple(phase(row, q[(a >> shift) & mask] if q is not None
                                     else gate[1] * ((a >> shift) & mask).bit_count())
                               for a, row in enumerate(values))
            elif kind in ('P', 'NOT'):
                out = [None] * len(values)
                mapping = local_map(tuple(gate[1]), h) if kind == 'P' else None
                for a, row in enumerate(values):
                    b = ((a & ~(mask << shift)) | (mapping[(a >> shift) & mask] << shift)
                         if mapping is not None else a ^ (gate[1] << shift))
                    out[b] = row
                values = tuple(out)
            else:
                bit = (1 << gate[1] if kind == 'H' else gate[1]) << shift
                sign = gate[2]
                out = [None] * len(values)
                for a, u in enumerate(values):
                    b = a ^ bit
                    if a > b:
                        continue
                    v, first, second = values[b], [], []
                    for j in range(0, len(u), 2):
                        x, y, z, w = u[j], u[j + 1], v[j], v[j + 1]
                        if kind == 'H':
                            first.extend((x + z - sign * (y + w), y + w + sign * (x + z)))
                            second.extend((x - z - sign * (y - w), y - w + sign * (x - z)))
                        elif kind == 'C':
                            first.extend((x - sign * y + z + sign * w, y + sign * x + w - sign * z))
                            second.extend((x + sign * y + z - sign * w, y - sign * x + w + sign * z))
                        else:
                            raise ValueError(('Unknown literal Gaussian gate', gate))
                    out[a], out[b] = tuple(first), tuple(second)
                values, grid = normalize(out, grid + 1)
    return normalize(values, grid)


@lru_cache(None)
def literal(E, h, inverse=False):
    word = interface.literal_word(E, h)
    return interface.inverse_word(word) if inverse else word


@lru_cache(None)
def normal(E, F, h):
    result = interface.compile_interface(E, F, h)
    actual = literal(E, h, True) + literal(F, h)
    interface.assert_complete_tableau(result, actual)
    return result


def schedule(k):
    if k < 1 or k % 2 != 1:
        raise ValueError('Positive odd source cube weight required')
    h, n, q = 2 * k, 1 << k, k + 1
    labels = [geometry.label(code, k) for code in range(n)]
    buckets = [(j, bit, tuple(code for code in range(n) if code >> j & 1 == bit),
                interface.basis(labels[code] for code in range(n) if code >> j & 1 == bit))
               for j in range(k) for bit in (0, 1)]
    G, R, A, roles = n, 2 * n, 2 * n + q, 2 * n + q + 2 * k
    current = [(value,) for value in labels] + [()] * (roles - n)
    initial, events, histogram = list(current), [], Counter()
    full = interface.basis(1 << j for j in range(h))

    def move(role, E, stage):
        E = interface.basis(E)
        if current[role] != E:
            nf = normal(current[role], E, h)
            histogram[nf['selected_rank_per_column']] += 1
            events.append({'kind': 'frame', 'role': role, 'from': list(current[role]),
                           'to': list(E), 'stage': stage})
            current[role] = E

    def add(target, source, sign, stage):
        if current[target] != current[source]:
            raise AssertionError('Quotient scalar operands lack the same actual canonical representative')
        events.append({'kind': 'add', 'target': target, 'source': source,
                       'sign': sign, 'stage': stage})

    def negate(role, stage):
        events.append({'kind': 'negate', 'role': role, 'stage': stage})

    def gather(sign, stage):
        for source in range(n):
            add(R, G + source, sign, stage)
            for j in range(k):
                if source >> j & 1:
                    add(R + j + 1, G + source, sign, stage)

    def read(sign, late):
        for a, (j, bit, codes, E) in enumerate(buckets):
            root = R + j + 1
            if not bit:
                negate(root, 'prepare complementary half'); add(root, R, 1, 'prepare complementary half')
            if late:
                move(A + a, E, 'aggregate entrance before paid read')
            nf = normal(current[root], current[A + a], h)
            if nf['selected_rank_per_column'] != int(late):
                raise AssertionError('A singleton copy has an omitted or unexpected child')
            if late:
                histogram[1] += 1
            events.append({'kind': 'copy-read', 'root': root, 'target': A + a,
                           'from': list(current[root]), 'to': list(current[A + a]),
                           'sign': sign, 'late': late, 'complete_owned_copy': True})
            if not bit:
                add(root, R, -1, 'undo complementary half'); negate(root, 'undo complementary half')

    gather(1, 'early helper response'); read(-1, False); gather(-1, 'undo early helper response')
    for source, value in enumerate(labels):
        move(G + source, (value,), 'original source injection'); add(G + source, source, 1, 'original source injection')
    E = ()
    for source, value in enumerate(labels):
        E = interface.basis(E + (value,))
        for root in range(R, A):
            move(root, E, 'synchronized quotient growth')
        move(G + source, E, 'source meets synchronized quotient')
        add(R, G + source, 1, 'late quotient incidence')
        for j in range(k):
            if source >> j & 1:
                add(R + j + 1, G + source, 1, 'late quotient incidence')
        move(G + source, full, 'helper retirement after its quotient writes')
    if len(E) != k + 1:
        raise AssertionError('The source cube quotient span is incomplete')
    read(1, True)
    for root in range(R, A):
        move(root, full, 'quotient roots to common cleanup endpoint')
    gather(-1, 'undo full quotient incidence')
    for source in range(n):
        move(source, full, 'unchanged original source to cleanup endpoint')
        add(G + source, source, -1, 'exact original source uninject')
    baseline = sum(len(F) - len(E) for E, F in zip(initial, current))
    rank = sum(r * count for r, count in histogram.items())
    if rank != baseline + 2 * k:
        raise AssertionError('An extra quotient root or paid singleton copy was omitted')
    return {'k': k, 'h': h, 'n': n, 'q': q, 'G': G, 'R': R, 'A': A, 'roles': roles,
            'labels': labels, 'buckets': buckets, 'initial': initial, 'final': current,
            'events': events, 'histogram': dict(histogram), 'rank': rank,
            'endpoint_baseline_rank': baseline, 'paid_copy_extra_rank': 2 * k}


def execute(spec, data, columns, reverse=False, negative=None):
    values = list(data)
    h = spec['h']
    current = list(spec['final'] if reverse else spec['initial'])
    events = reversed(spec['events']) if reverse else spec['events']
    max_grid, max_magnitude_bits, copied_values = 0, 0, 0
    corrupted = False
    for event in events:
        kind = event['kind']
        if kind == 'frame':
            E, F = tuple(event['from']), tuple(event['to'])
            if reverse:
                E, F = F, E
            role = event['role']
            if current[role] != E:
                raise AssertionError('A quotient frame event skips its actual continuation')
            values[role] = apply_word(values[role], interface.compiled_word(normal(E, F, h)), h, columns)
            current[role] = F
        elif kind == 'negate':
            role = event['role']
            values[role] = (tuple(tuple(-x for x in row) for row in values[role][0]), values[role][1])
        elif kind == 'add':
            i, j = event['target'], event['source']
            if current[i] != current[j]:
                raise AssertionError('A chronological quotient scalar gate has unequal actual operators')
            sign = event['sign'] * (-1 if reverse else 1)
            values[i] = plus(values[i], values[j], sign)
        else:
            root, target = event['root'], event['target']
            E, F = tuple(event['from']), tuple(event['to'])
            if current[root] != E or current[target] != F:
                raise AssertionError('The copy interface differs from actual source/recipient frames')
            if negative == 'omit old dirty read' and not event['late']:
                continue
            scratch = (tuple(tuple(row) for row in values[root][0]), values[root][1])
            copied_values += len(scratch[0]) * len(scratch[0][0])
            nf = normal(E, F, h)
            if negative == 'missing late copy transform' and event['late']:
                pass
            else:
                if negative in ('wrong global phase', 'wrong affine offset') and event['late'] and not corrupted:
                    nf = deepcopy(nf)
                    if negative == 'wrong global phase':
                        nf['input_quadratic']['constant'] = (nf['input_quadratic']['constant'] + 1) % 4
                    else:
                        nf['output_affine_offset'] ^= 1
                    corrupted = True
                scratch = apply_word(scratch, interface.compiled_word(nf), h, columns)
            if negative == 'cropped copied fields':
                scratch = (tuple(tuple(row[:2]) + (0,) * (len(row) - 2) for row in scratch[0]), scratch[1])
            values[target] = plus(values[target], scratch, event['sign'] * (-1 if reverse else 1))
            del scratch  # Semantic disposal; native complete-buffer erase remains conditional.
        max_grid = max(max_grid, *(bank[1] for bank in values))
        max_magnitude_bits = max(max_magnitude_bits, *(max((abs(x).bit_length() for row in bank[0] for x in row), default=0) - bank[1]
                                                     for bank in values))
    if current != list(spec['initial'] if reverse else spec['final']):
        raise AssertionError('The complete persistent endpoint frames are wrong')
    return values, {'finite_observed_max_bank_fractional_bits': max_grid,
                    'finite_observed_component_magnitude_bits': max_magnitude_bits,
                    'copied_complete_signed_components': copied_values,
                    'native_copy_erase_not_implemented': True}


def expected(spec, data, columns):
    virtual = [apply_word(bank, literal(tuple(E), spec['h'], True), spec['h'], columns)
               for bank, E in zip(data, spec['initial'])]
    output = list(virtual)
    for a, row in enumerate(spec['buckets']):
        for source in row[2]:
            output[spec['A'] + a] = plus(output[spec['A'] + a], virtual[source])
    return [apply_word(bank, literal(tuple(E), spec['h']), spec['h'], columns)
            for bank, E in zip(output, spec['final'])]


def scalar_audit(spec):
    n = spec['roles']
    identity = [[int(i == j) for j in range(n)] for i in range(n)]
    rows = [row[:] for row in identity]
    maximum = 1
    for event in spec['events']:
        if event['kind'] in ('add', 'copy-read'):
            i, j = event['target'], event.get('source', event.get('root'))
            rows[i] = [a + event['sign'] * b for a, b in zip(rows[i], rows[j])]
        elif event['kind'] == 'negate':
            rows[event['role']] = [-x for x in rows[event['role']]]
        maximum = max(maximum, *(sum(abs(x) for x in row) for row in rows))
    desired = [row[:] for row in identity]
    for a, row in enumerate(spec['buckets']):
        for source in row[2]:
            desired[spec['A'] + a][source] += 1
    if rows != desired:
        raise AssertionError('An independent scalar source/helper/root/aggregate column is wrong')
    return {'complete_independent_scalar_matrix_entries': n * n,
            'virtual_scalar_prefix_L1': maximum, 'virtual_scalar_grid_bits': 0,
            'physical_child_internal_prefix_guard_not_in_this_scalar_audit': True}


def probe(task):
    k, columns, part, bounded = task
    started = time.monotonic()
    spec = schedule(k)
    scalar = scalar_audit(spec)
    size, roles = 1 << (spec['h'] * columns), spec['roles']
    checked, digest = 0, sha256()
    if part != 'fields':
        choices = [(role, address) for role in range(roles) for address in range(size)]
        if part != 'all':
            choices = choices[part::4]
            if bounded:
                choices = choices[:8]
        for role, address in choices:
            data = [(tuple((int(i == role and a == address), 0) for a in range(size)), 0)
                    for i in range(roles)]
            actual, unused = execute(spec, data, columns)
            if actual != expected(spec, data, columns):
                raise AssertionError('A complete physical persistent-input basis column failed')
            restored, unused = execute(spec, actual, columns, True)
            if restored != data:
                raise AssertionError('The actual reverse word failed a physical column')
            digest.update(repr(actual).encode()); checked += 1
    data = [normalize([tuple(((17 * i + 13 * a + 7 * c) % 47 - 23) for c in range(8))
                       for a in range(size)], i % 4) for i in range(roles)]
    actual, counters = execute(spec, data, columns)
    wanted = expected(spec, data, columns)
    if actual != wanted or execute(spec, actual, columns, True)[0] != data:
        raise AssertionError('The complete four-field Gaussian dirty endpoint or inverse failed')
    negatives = {}
    for negative in ('omit old dirty read', 'missing late copy transform', 'cropped copied fields',
                     'wrong global phase', 'wrong affine offset'):
        if execute(spec, data, columns, negative=negative)[0] == wanted:
            raise AssertionError(('A paid-copy/old-response corruption was accepted', negative))
        negatives[negative] = True
    return {'k': k, 'h': spec['h'], 'columns': columns, 'part': part,
            'source_roles': spec['n'], 'source_helpers': spec['n'],
            'extra_quotient_roots': spec['q'], 'aggregate_target_roots': 2 * k,
            'all_persistent_roles': roles, 'child_histogram_per_column': spec['histogram'],
            'paid_rank_per_column': spec['rank'], 'endpoint_baseline_rank': spec['endpoint_baseline_rank'],
            'paid_relative_copy_extra_rank': spec['paid_copy_extra_rank'],
            'explicit_complete_physical_basis_columns': checked,
            'basis_coverage': 'Complete all columns' if part == 'all' else
                              'A disjoint fourth of all columns' if isinstance(part, int) and not bounded else
                              'Bounded selected columns' if isinstance(part, int) else 'Full Gaussian fields only',
            'complete_four_Gaussian_fields': True, 'full_field_signed_values_forward': 8 * roles * size,
            'inverse_and_all_dirty_helpers_and_quotient_roots_restored': True,
            'finite_counters': counters, 'scalar_audit': scalar, 'negative_controls': negatives,
            'output_sha256': digest.hexdigest(), 'seconds': time.monotonic() - started,
            'actual_representatives_include_degenerate_cube_and_bucket_frames': True,
            'native_owned_copy_and_erase_not_implemented': True,
            'higher_J_side_formation_and_whole_master_not_supplied': True}


def profile(k):
    spec = schedule(k)
    scalar = scalar_audit(spec)
    normals = []
    for event in spec['events']:
        if event['kind'] == 'copy-read' and event['late']:
            normals.append(normal(tuple(event['from']), tuple(event['to']), spec['h']))
    return {'k': k, 'h': spec['h'], 'source_roles': spec['n'],
            'persistent_source_helpers': spec['n'], 'extra_persistent_quotient_roots': spec['q'],
            'existing_singleton_aggregate_roots': 2 * k,
            'all_persistent_roles': spec['roles'], 'child_histogram_per_column': spec['histogram'],
            'endpoint_baseline_rank': spec['endpoint_baseline_rank'], 'rank': spec['rank'],
            'extra_paid_singleton_copy_rank': 2 * k, 'scalar_audit': scalar,
            'every_late_copy_complete_normal_form': normals,
            'physical_Gaussian_arrays_not_replayed_for_this_profile': True,
            'all_higher_J_aggregates_unpaid': True,
            'native_scratch_copy_read_erase_conditional': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or (args.output and args.output.exists()):
        raise ValueError('Positive workers and a fresh optional output file required')
    paths = [Path(__file__).resolve(), Path(geometry.__file__).resolve(),
             Path(interface.__file__).resolve(), Path(interface.reference.__file__).resolve()]
    original = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    if any(original[name] != pin for name, pin in PINS.items()):
        raise AssertionError('An immutable geometry/frame compiler input changed')
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    tasks = [(1, 1, 'all', args.bounded), (3, 1, 0, args.bounded)] if args.bounded else [
        (1, 1, 'all', False), *[(3, 1, part, False) for part in range(4)], (3, 2, 'fields', False)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, tasks))
    result = {'status': 'PASS synchronized singleton quotient copies',
              'started_utc': started, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.monotonic() - tick, 'workers': args.workers, 'bounded': args.bounded,
              'source_sha256': original, 'cases': rows, 'k5_complete_scalar_and_frame_profile': profile(5),
              'dependencies': 'Python standard library and three pinned in-repository sources',
              'scope': 'Complete finite singleton-formation operator; all extra persistent roots and paid rank-one owned copies retained. Higher-J/global side/master/native copy and exponent remain open.'}
    if original != {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}:
        raise AssertionError('A source changed during the immutable experiment')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('cases', 'k5_complete_scalar_and_frame_profile')}, sort_keys=True))


if __name__ == '__main__':
    main()
