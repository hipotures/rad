#!/usr/bin/env python3
"""Actual all-Lagrangian Gaussian frames and one-child relative interfaces.

The canonical L_E anchors and tableau/normal-form algebra are retained from
the pinned scalable compiler. New frame synthesis and Q/affine path sums are
explicit; native time remains the separate paid wrapper contract.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import time

import scalable_subspace_interfaces as exact


COMPILER_SHA = '3da400b0b157cc28b546113e63a150e4b1672c71a5f2c74e724ac8fc3d1f4851'


def symplectic(a, b, n):
    mask = (1 << n)-1
    return exact.dot(a & mask, b >> n) ^ exact.dot(a >> n, b & mask)


def valid_lagrangian(rows, n):
    L = exact.basis(rows)
    if len(L) != n or any(v < 0 or v >= 1 << (2*n) for v in L):
        raise ValueError('expected a full binary Lagrangian, X low and Z high')
    if any(symplectic(a, b, n) for a, b in combinations(L, 2)):
        raise ValueError('frame labels are not isotropic')
    return L


def inverse_word(word):
    inverse = []
    for gate in reversed(word):
        if gate[0] == 'Q':
            q = exact.parse_quadratic(gate[1])
            q.constant = -q.constant % 4
            q.linear = [-c % 4 for c in q.linear]
            inverse.append(('Q', exact.serialize_quadratic(q)))
        elif gate[0] == 'NOT':
            inverse.append(gate)
        else:
            inverse += exact.inverse_word([gate])
    return inverse


def inverse_Z_labels(word, n):
    _, Z = exact.tableau(inverse_word(word), n)
    return exact.basis(x | (z << n) for x, z, p in Z)


def frame_word(rows, n):
    """A polynomial actual representative F satisfying F^-1 Z F=L."""
    L = valid_lagrangian(rows, n)
    mask = (1 << n)-1
    E = exact.basis(v & mask for v in L)
    # Preserve old actual anchors wherever this is an L_E frame.
    if all(all(exact.dot(u, (v & mask) ^ (v >> n)) == 0 for u in E) for v in L):
        word = exact.literal_word(E, n)
        anchor = 'retained-canonical-L_E'
    else:
        r = len(E)
        P = exact.reference.complete_basis(E, n)
        projection_rows = [sum((v >> bit & 1) << j for j, v in enumerate(L)) for bit in range(n)]
        active_columns = []
        for x in E:
            coefficients, _ = exact.solve_affine(projection_rows, x, n)
            lift = exact.embed(coefficients, L)
            z = lift >> n
            routed_z = sum(exact.dot(p, z) << j for j, p in enumerate(P))
            # Pure Z labels span all inactive coordinates; row combinations
            # remove this inactive part without a physical gate.
            active_columns.append(routed_z & ((1 << r)-1))
        if any((active_columns[i] >> j & 1) != (active_columns[j] >> i & 1)
               for i in range(r) for j in range(r)):
            raise AssertionError('active graph is not symmetric')
        q = exact.Quadratic(n)
        for j in range(r):
            q.linear[j] = active_columns[j] >> j & 1
            for i in range(j):
                if active_columns[j] >> i & 1:
                    q.pair(i, j)
        word = [('P', exact.inverse_columns(P)), ('Q', exact.serialize_quadratic(q))]
        word += [('H', j, 1) for j in range(r)]
        anchor = 'general-projection-chirp-Htilde'
    if inverse_Z_labels(word, n) != L:
        raise AssertionError('actual inverse-Z labels do not bind the requested frame')
    return dict(n=n, coordinate_convention='X low n bits, Z high n bits',
                lagrangian_basis=list(L), anchor=anchor, actual_word=word)


def path_sum(word, n, output):
    """Actual coefficient with Q/NOT affine support, on O(n) path variables."""
    address = [0]*n
    shifts = [0]*n
    q = exact.Quadratic()
    factors = 0
    def add_parity(expression, shift, coefficient):
        if shift:
            q.constant = (q.constant+coefficient) % 4
            coefficient = -coefficient
        q.parity(expression, coefficient)
    for gate in word:
        kind = gate[0]
        if kind == 'D':
            for expression, shift in zip(address, shifts):
                add_parity(expression, shift, gate[1])
        elif kind == 'Q':
            data = gate[1]
            q.constant = (q.constant+data['constant']) % 4
            for expression, shift, coefficient in zip(address, shifts, data['linear']):
                add_parity(expression, shift, coefficient)
            for i, j, coefficient in data['cross']:
                if coefficient != 2:
                    raise ValueError('quadratic cross term is not even')
                q.two_parities(address[i], address[j])
                if shifts[j]:
                    q.parity(address[i], 2)
                if shifts[i]:
                    q.parity(address[j], 2)
                if shifts[i] and shifts[j]:
                    q.constant = (q.constant+2) % 4
        elif kind == 'P':
            routed, translated = [0]*n, [0]*n
            for j, column in enumerate(gate[1]):
                for i in exact.bits(column):
                    routed[i] ^= address[j]
                    translated[i] ^= shifts[j]
            address, shifts = routed, translated
        elif kind == 'H':
            variable = q.new_variable()
            bit = gate[1]
            q.two_parities(address[bit], variable)
            if shifts[bit]:
                q.parity(variable, 2)
            address[bit], shifts[bit] = variable, 0
            if gate[2] == -1:
                q.constant = (q.constant-1) % 4
            factors += 1
        elif kind == 'C':
            variable = q.new_variable()
            for j in exact.bits(gate[1]):
                address[j] ^= variable
            q.parity(variable, -gate[2])
            if gate[2] == -1:
                q.constant = (q.constant-1) % 4
            factors += 1
        elif kind == 'NOT':
            for j in exact.bits(gate[1]):
                shifts[j] ^= 1
        else:
            raise ValueError('unsupported actual Clifford word')
    shifted_output = output ^ sum(bit << j for j, bit in enumerate(shifts))
    try:
        offset, null = exact.solve_affine(address, shifted_output, len(q.linear))
    except ValueError:
        return (0, 0), factors, 0
    value = q.substitute(offset, null).gauss_sum()
    return exact.multiply_gaussian(exact.alpha_numerator(factors), value), factors, len(null)


def compile_word(word, n, expected_rank=None):
    """Generic actual-word extension of the pinned one-child normal form."""
    X, Z = exact.tableau(word, n)
    source = exact.basis(value[0] for value in Z)
    rank = len(source)
    if expected_rank is not None and rank != expected_rank:
        raise AssertionError('relative tableau rank differs from Lagrangian distance')
    rows = [sum((value[0] >> j & 1) << k for k, value in enumerate(Z)) for j in range(n)]
    _, pure_masks = exact.solve_affine(rows, 0, n)
    pure = [exact.pauli_combination(Z, mask) for mask in pure_masks]
    if any(x or p & 1 for x, z, p in pure):
        raise AssertionError('pure-Z stabilizer is not an even character')
    offset, null = exact.solve_affine([value[1] for value in pure],
        sum((value[2]//2) << j for j, value in enumerate(pure)), n)
    if exact.basis(null) != source:
        raise AssertionError('affine support has wrong translation span')
    numerator, path_rank, free = path_sum(word, n, offset)
    if path_rank < rank:
        raise AssertionError('path sum has too few Gaussian factors')
    alpha = exact.alpha_numerator(rank)
    units = [p for p in range(4) if numerator == tuple(v << (path_rank-rank)
             for v in exact.multiply_gaussian(alpha, exact.UNITS[p]))]
    if len(units) != 1:
        raise AssertionError('actual dyadic amplitude is not a fourth-root C gauge')
    phase = units[0]
    support_generators = []
    for vector in source:
        coefficients, _ = exact.solve_affine(rows, vector, n)
        support_generators.append(exact.pauli_combination(Z, coefficients))
    support_rows = [sum((v >> j & 1) << k for k, v in enumerate(source)) for j in range(n)]
    def unit(x, y):
        shift, character, exponent = exact.pauli_combination(X, y)
        coordinates, extra = exact.solve_affine(support_rows, x ^ offset ^ shift, rank)
        if extra:
            raise AssertionError('support coordinates not unique')
        sx, sz, sp = exact.pauli_combination(support_generators, coordinates)
        return (phase+sp+2*exact.dot(sz, offset)+exponent+2*exact.dot(character, x ^ shift)) % 4
    quotient = [sum(exact.dot(row, value[0]) << j for j, value in enumerate(X))
                for row in exact.reference.perpendicular(source, n)]
    _, active_inputs = exact.solve_affine(quotient, 0, n)
    if len(active_inputs) != rank:
        raise AssertionError('input support has wrong dimension')
    inputs = list(exact.reference.complete_basis(exact.basis(active_inputs), n))
    coupling = []
    for vector in source:
        row = 0
        for j, y in enumerate(inputs[:rank]):
            exponent = (unit(offset ^ vector, y)+unit(offset, 0)-unit(offset ^ vector, 0)-unit(offset, y)) % 4
            if exponent not in (0, 2):
                raise AssertionError('active coupling is not binary')
            row |= (exponent//2) << j
        coupling.append(row)
    corrected = []
    for j in range(rank):
        coefficients, null = exact.solve_affine(coupling, 1 << j, rank)
        if null:
            raise AssertionError('active coupling singular')
        corrected.append(exact.embed(coefficients, inputs[:rank]))
    inputs = corrected+inputs[rank:]
    outputs = list(source)+[exact.pauli_combination(X, y)[0] for y in inputs[rank:]]
    if len(exact.basis(outputs)) != n:
        raise AssertionError('output spectators do not form a route')
    active_mask = (1 << rank)-1
    def row_phase(value):
        spectator = value & ~active_mask
        y = exact.embed(spectator, inputs)
        origin = unit(offset ^ exact.embed(spectator, outputs), y)
        return (unit(offset ^ exact.embed(value, outputs), y)+(value & active_mask).bit_count()-origin) % 4
    def column_phase(value):
        spectator = value & ~active_mask
        return (unit(offset ^ exact.embed(spectator, outputs), exact.embed(value, inputs))
                +(value & active_mask).bit_count()) % 4
    normal = dict(n=n, selected_rank_per_column=rank, one_bulk_child_calls=int(rank > 0),
        output_affine_offset=offset, output_columns=outputs, input_columns=inputs,
        output_quadratic=exact.serialize_quadratic(exact.fit_quadratic(row_phase, n)),
        input_quadratic=exact.serialize_quadratic(exact.fit_quadratic(column_phase, n)),
        global_unit_exponent=phase,
        compilation=dict(path_variables=path_rank, summed_free_variables=free,
                         binary_elimination_only=True, full_address_arrays_allocated=False))
    exact.assert_complete_tableau(normal, word)
    return normal


def compile_frames(A, B, n):
    left, right = frame_word(A, n), frame_word(B, n)
    # dim(A+B)=2n-dim(A intersect B), so the metric is dim(A+B)-n.
    rank = len(exact.basis(tuple(left['lagrangian_basis'])+tuple(right['lagrangian_basis'])))-n
    word = inverse_word(left['actual_word'])+right['actual_word']
    normal = compile_word(word, n, rank)
    return dict(source_frame=left, target_frame=right, actual_relative_word=word, normal_form=normal)


def all_lagrangians(n):
    spaces = []
    for pivots in combinations(range(2*n), n):
        free = [(i, j) for i, pivot in enumerate(pivots)
                for j in range(pivot+1, 2*n) if j not in pivots]
        for mask in range(1 << len(free)):
            rows = [1 << p for p in pivots]
            for bit, (i, j) in enumerate(free):
                rows[i] |= (mask >> bit & 1) << j
            if not any(symplectic(a, b, n) for a, b in combinations(rows, 2)):
                spaces.append(exact.basis(rows))
    return tuple(sorted(set(spaces)))


def literal_column(word, n, column):
    values = [(0, 0)]*(1 << n)
    values[column] = (1, 0)
    grid = 0
    for gate in word:
        kind = gate[0]
        if kind in ('P', 'NOT'):
            out = [(0, 0)]*len(values)
            for address, value in enumerate(values):
                routed = exact.embed(address, gate[1]) if kind == 'P' else address ^ gate[1]
                out[routed] = value
            values = out
        elif kind in ('D', 'Q'):
            values = [exact.multiply_gaussian(value, exact.UNITS[
                (gate[1]*address.bit_count()) % 4 if kind == 'D'
                else exact.parse_quadratic(gate[1]).evaluate(address)])
                for address, value in enumerate(values)]
        elif kind in ('H', 'C'):
            out = [(0, 0)]*len(values)
            if kind == 'H':
                bit = 1 << gate[1]
                alpha = (1, gate[2])
                for address in range(len(values)):
                    if address & bit:
                        continue
                    A, B = values[address], values[address ^ bit]
                    out[address] = exact.multiply_gaussian((A[0]+B[0], A[1]+B[1]), alpha)
                    out[address ^ bit] = exact.multiply_gaussian((A[0]-B[0], A[1]-B[1]), alpha)
            else:
                for address, value in enumerate(values):
                    stay = exact.multiply_gaussian(value, (1, gate[2]))
                    jump = exact.multiply_gaussian(value, (1, -gate[2]))
                    for target, v in ((address, stay), (address ^ gate[1], jump)):
                        a, b = out[target]
                        out[target] = (a+v[0], b+v[1])
            values, grid = out, grid+1
        else:
            raise ValueError('unknown matrix reference gate')
    return values, grid


def small_probe(n):
    Ls = all_lagrangians(n)
    expected_count = 1
    for j in range(1, n+1):
        expected_count *= (1 << j)+1
    if len(Ls) != expected_count:
        raise AssertionError('full Lagrangian enumeration count wrong')
    frame_entries, Q_frames = 0, 0
    for L in Ls:
        spec = frame_word(L, n)
        Q_frames += spec['anchor'] != 'retained-canonical-L_E'
        for x in range(1 << n):
            values, grid = literal_column(spec['actual_word'], n, x)
            for y in range(1 << n):
                # The new affine-Q Gauss path is checked at column zero.
                if x == 0:
                    if path_sum(spec['actual_word'], n, y)[0] != values[y]:
                        raise AssertionError('Q path sum differs from literal matrix')
                frame_entries += 1
    return dict(kind='complete-frame-labels', n=n, lagrangians=len(Ls),
                new_general_frames=Q_frames, literal_coefficients=frame_entries,
                actual_inverse_Z_frame_labels=True)


def witness_probe():
    n = 3
    fixture = Path(__file__).parents[2]/'fixtures'/'complex'/'noncommuting-four-incidence.json'
    data = json.loads(fixture.read_text())
    terminals = []
    for A in data['incoming_symmetric_matrices']+data['outgoing_symmetric_matrices']:
        terminals.append(tuple(sum(A[i][j] << i for i in range(n)) | (1 << (n+j)) for j in range(n)))
    median = tuple((v >> n) | ((v & ((1 << n)-1)) << n) for v in data['common_lagrangian_basis'])
    widths, entries, normals = [], 0, []
    for L in terminals:
        result = compile_frames(L, median, n)
        normal, word = result['normal_form'], result['actual_relative_word']
        rank = normal['selected_rank_per_column']
        widths.append(rank)
        for x in range(1 << n):
            values, grid = literal_column(word, n, x)
            for y in range(1 << n):
                expected = exact.reconstructed_entry(normal, y, x)
                if grid < rank or values[y] != tuple(v << (grid-rank) for v in expected):
                    raise AssertionError('all-Lagrangian witness relative coefficient differs')
                entries += 1
        normals.append(result)
    if widths != data['charged_incidence_ranks'] or sum(widths) != 5:
        raise AssertionError('actual-frame compiler lost the retained 5-vs6 local gap')
    return dict(kind='retained-four-incidence-gap', selected_ranks=widths,
                total_rank=5, retained_graph_minimum=6,
                all_literal_coefficients=entries, interfaces=normals,
                fixture_sha256=sha256(fixture.read_bytes()).hexdigest(),
                no_new_scalar_chronology=True)


def large_probe(task):
    n, seed = task
    rng = random.Random(seed)
    frames = []
    for _ in range(2):
        # Generate L by an explicit invertible Clifford word; the new factory
        # independently chooses its own actual representative for those labels.
        q = exact.Quadratic(n)
        q.linear = [rng.randrange(4) for _ in range(n)]
        for j in range(n):
            for i in range(j):
                if rng.randrange(2):
                    q.pair(i, j)
        word = [('Q', exact.serialize_quadratic(q))]+[('H', j, 1) for j in range(n) if rng.randrange(2)]
        columns = list(1 << j for j in range(n))
        for _ in range(2*n):
            a, b = rng.sample(range(n), 2)
            columns[b] ^= columns[a]
        word += [('P', columns)]
        frames.append(inverse_Z_labels(word, n))
    result = compile_frames(*frames, n)
    normal = result['normal_form']
    return dict(kind='seeded-large-actual-frames', n=n, seed=seed,
                complete_Pauli_images=2*n, selected_rank=normal['selected_rank_per_column'],
                path_variables=normal['compilation']['path_variables'],
                exact_global_coefficient=True, full_address_arrays=False,
                normal_form_sha256=sha256(json.dumps(normal,sort_keys=True).encode()).hexdigest())


def run_task(task):
    if task == 'witness':
        return witness_probe()
    if isinstance(task, int):
        return small_probe(task)
    return large_probe(task)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive workers required')
    files = [Path(__file__), Path(exact.__file__), Path(exact.reference.__file__)]
    before = {p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if before[Path(exact.__file__).name] != COMPILER_SHA or before[Path(exact.reference.__file__).name] != exact.REFERENCE_SHA:
        raise AssertionError('pinned compact compiler closure changed')
    started = time.monotonic()
    utc = datetime.now(timezone.utc).isoformat()
    tasks = ['witness', 2] if args.bounded else ['witness', 3, (16, 202610090316), (32, 202610090332)]
    if args.workers == 1:
        cases = [run_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(run_task, tasks))
    if before != {p.name:sha256(p.read_bytes()).hexdigest() for p in files}:
        raise AssertionError('effective source changed during run')
    certificate = dict(status='PASS', started_utc=utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                       effective_sources=before, workers=args.workers, bounded=args.bounded,
                       cases=cases, seconds=time.monotonic()-started,
                       scope='Actual all-Lagrangian frame construction and one-distance-child algebraic interfaces. Native wrapper time remains conditional; no whole scalar chronology, stock or exponent.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',cases=len(cases),seconds=certificate['seconds'],scope=certificate['scope'])),flush=True)


if __name__ == '__main__':
    main()
