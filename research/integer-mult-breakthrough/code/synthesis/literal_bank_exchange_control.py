#!/usr/bin/env python3
"""Complete Gaussian operator control with literal or signed-shear exchanges.

Raw exchanges carry both actual Gaussian frame operators and logical rows.
They incur separately recorded data movement, without a common-frame shear
constraint. Identical source/sink basis words nevertheless match original
worldlines at the central copy and retain a crossed-endpoint rank bound.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import global_word_frame_search as f
import pauli_tensor_discriminator as g


def invert(word):
    result = []
    for event in reversed(word):
        if event[0] == 'swap':
            result.append(event)
        elif event[0] == 'add':
            result.append(('add', event[1], event[2], -event[3]))
        elif event[0] == 'scale':
            result.append(('scale', event[1], 1 / event[2]))
        else:
            raise ValueError('Unknown reversible scalar operation')
    return result


def expand_exchanges(word):
    result = []
    for event in word:
        if event[0] == 'swap':
            _, a, b = event
            result += [('add', a, b, Q(1)), ('add', b, a, Q(-1)),
                       ('add', a, b, Q(1)), ('scale', b, Q(-1))]
        else:
            result.append(event)
    return result


def complete_word(m, basis_kind, exchange_kind):
    # This retained prelude exchanges initially differently framed banks,
    # making a missing frame carry observable in the complete operator.
    B = [('swap', 0, 1)] + [('add', 0, j, Q(1)) for j in range(1, m)]
    if basis_kind == 'side':
        B += [('add', j, 0, Q(-1)) for j in range(1, m)]
    elif basis_kind != 'sum':
        raise ValueError('Unknown basis kind')
    Bx = B
    By = [(kind, m + a, m + b, *rest) if kind != 'scale'
          else (kind, m + a, b) for kind, a, b, *rest in B]
    permutation = list(range(1, m)) + [0]
    arrangement = list(range(m))
    target = [permutation.index(i) for i in range(m)]
    P = []
    for i, value in enumerate(target):
        if arrangement[i] != value:
            j = arrangement.index(value)
            arrangement[i], arrangement[j] = arrangement[j], arrangement[i]
            P.append(('swap', m + i, m + j))
    before = Bx + By
    copies = [('add', m + permutation[j], j, Q(1)) for j in range(m)]
    raw = before + P + copies + invert(P) + invert(before)
    return (raw if exchange_kind == 'literal' else expand_exchanges(raw)), raw, permutation


def scalar_columns(word, m, corrupted=False):
    rows = [{j: Q(1)} for j in range(2 * m)]
    corrupt_copy = next(j for j, event in enumerate(word)
                        if event[0] == 'add' and event[1] >= m and event[2] < m)
    for step, event in enumerate(word):
        kind, a, *rest = event
        if kind == 'swap':
            b, = rest
            rows[a], rows[b] = rows[b], rows[a]
        elif kind == 'scale':
            c, = rest
            rows[a] = {j: c * value for j, value in rows[a].items()}
        else:
            b, c = rest
            if corrupted and step == corrupt_copy:
                c = -c
            for j, value in list(rows[b].items()):
                updated = rows[a].get(j, Q()) + c * value
                if updated:
                    rows[a][j] = updated
                else:
                    rows[a].pop(j, None)
    expected = [{j: Q(1)} for j in range(2 * m)]
    for j in range(m):
        expected[m + j][j] = Q(1)
    if (rows != expected) != corrupted:
        raise ValueError('Complete scalar bank-exchange word failed')
    return dict(all_initial_columns=2 * m, source_columns=m, arbitrary_sink_columns=m,
                corruption_detected=corrupted)


def worldline_graph(word, starts, ends):
    vertices = sum(event[0] == 'add' for event in word)
    boundaries = [[] for _ in range(vertices)]
    previous = [None] * len(starts)
    pending = list(starts)
    origins = list(range(len(starts)))
    edge_counts = Counter()
    middle_origins = []
    node = 0
    for event in word:
        kind, a, *rest = event
        if kind == 'swap':
            b, = rest
            previous[a], previous[b] = previous[b], previous[a]
            pending[a], pending[b] = pending[b], pending[a]
            origins[a], origins[b] = origins[b], origins[a]
        elif kind == 'add':
            b, _ = rest
            for role in (a, b):
                if previous[role] is None:
                    boundaries[node].append(pending[role])
                else:
                    edge_counts[tuple(sorted((previous[role], node)))] += 1
                previous[role] = node
            if a >= len(starts) // 2 and b < len(starts) // 2:
                middle_origins.append((origins[b], origins[a]))
            node += 1
    constant = 0
    n = len(starts[0])
    for role, old in enumerate(previous):
        if old is None:
            constant += f.distance(pending[role], ends[role], n)
        else:
            boundaries[old].append(ends[role])
    return tuple((a, b, weight) for (a, b), weight in sorted(edge_counts.items())), boundaries, constant, origins, middle_origins


def chronological_charge(word, starts, ends, frames, assignment):
    current = list(starts)
    histogram = Counter()
    node = 0
    n = len(starts[0])
    for event in word:
        kind, a, *rest = event
        if kind == 'swap':
            b, = rest
            current[a], current[b] = current[b], current[a]
        elif kind == 'add':
            b, _ = rest
            target = frames[assignment[node]]
            for role in (a, b):
                rank = f.distance(current[role], target, n)
                if rank:
                    histogram[rank] += 1
                current[role] = target
            node += 1
    for old, target in zip(current, ends):
        rank = f.distance(old, target, n)
        if rank:
            histogram[rank] += 1
    return dict(sorted(histogram.items()))


def identity(size):
    return [[g.ONE if a == b else g.ZERO for b in range(size)] for a in range(size)]


def adjoint(A):
    return [[(A[b][a][0], -A[b][a][1]) for b in range(len(A))] for a in range(len(A))]


def sum_gaussian(values):
    result = g.ZERO
    for value in values:
        result = g.add(result, value)
    return result


def compose(A, B):
    return [[sum_gaussian(g.mul(A[a][k], B[k][b]) for k in range(len(A))
                         if A[a][k] != g.ZERO and B[k][b] != g.ZERO)
             for b in range(len(A))] for a in range(len(A))]


def c_line(t, n):
    size = 1 << n
    return [[g.ALPHA if a == b else g.BETA if a == b ^ t else g.ZERO
             for b in range(size)] for a in range(size)]


def apply(A, values):
    return [sum_gaussian(g.mul(coefficient, value) for coefficient, value in zip(row, values)
                         if coefficient != g.ZERO and value != g.ZERO) for row in A]


def physical_columns(word, n, m, corrupt_frame_carry=False):
    size = 1 << n
    zero = identity(size)
    full = g.tensor_c(n)
    starts = [c_line(1 << j, n) for j in range(m)] + [zero] * m
    ends = [full] * m + [compose(full, adjoint(c_line(1 << j, n))) for j in range(m)]
    digest = sha256()
    wrong = []
    transition_replays = 0
    for column in range(2 * m * size):
        data = [[g.ONE if role * size + a == column else g.ZERO for a in range(size)]
                for role in range(2 * m)]
        virtual = [apply(adjoint(F), values) for F, values in zip(starts, data)]
        for j in range(m):
            virtual[m + j] = [g.add(a, b) for a, b in zip(virtual[m + j], virtual[j])]
        expected = [apply(F, values) for F, values in zip(ends, virtual)]
        current = list(starts)
        for event in word:
            kind, a, *rest = event
            if kind == 'swap':
                b, = rest
                data[a], data[b] = data[b], data[a]
                if not corrupt_frame_carry:
                    current[a], current[b] = current[b], current[a]
            elif kind == 'scale':
                c, = rest
                data[a] = [g.scale(z, c) for z in data[a]]
            else:
                b, c = rest
                for role in (a, b):
                    # The certified representative uses the common identity
                    # Gaussian operator, not merely an abstract frame label.
                    if current[role] != zero:
                        data[role] = apply(adjoint(current[role]), data[role])
                        transition_replays += 1
                        current[role] = zero
                data[a] = [g.add(z, g.scale(value, c)) for z, value in zip(data[a], data[b])]
        for role, target in enumerate(ends):
            data[role] = apply(compose(target, adjoint(current[role])), data[role])
        if data != expected:
            wrong.append(column)
        digest.update(json.dumps([[g.text_complex(value) for value in values] for values in data],
                                 separators=(',', ':')).encode())
    if bool(wrong) != corrupt_frame_carry:
        raise ValueError('Fixed labeled physical source/sink operator failed')
    return dict(status='CORRUPTION DETECTED' if wrong else 'EXACT COMPLETE GAUSSIAN OPERATOR PASS',
                full_initial_columns=2 * m * size, arbitrary_source_columns=m * size,
                arbitrary_sink_columns=m * size, all_labeled_outputs_exact=not wrong,
                wrong_frame_carry=corrupt_frame_carry, corrupted_columns=len(wrong),
                first_corrupted_column=wrong[0] if wrong else None,
                complete_output_sha256=digest.hexdigest(), transition_replays=transition_replays)


def probe(spec):
    n, m, basis_kind, exchange_kind = spec
    started = time.monotonic()
    word, literal, permutation = complete_word(m, basis_kind, exchange_kind)
    scalar = scalar_columns(word, m)
    corruption = scalar_columns(word, m, True)
    zero = f.le((), n)
    full = f.le(tuple(1 << j for j in range(n)), n)
    starts = [f.le((1 << j,), n) for j in range(m)] + [zero] * m
    ends = [full] * m + [f.le(f.perpendicular((1 << j,), n), n) for j in range(m)]
    edges, boundaries, constant, origins, middle = worldline_graph(word, starts, ends)
    assignment = [0] * len(boundaries)
    unary = [[sum(f.distance(F, zero, n) for F in bound),
              sum(f.distance(F, full, n) for F in bound)] for bound in boundaries]
    binary_distance = lambda a, b: n if a != b else 0
    binary = f.alpha_move(assignment, 1, edges, unary, binary_distance)
    exact_binary = f.energy(binary, edges, unary, binary_distance, constant)
    histogram = chronological_charge(word, starts, ends, [zero, full], binary)
    if sum(rank * count for rank, count in histogram.items()) != exact_binary:
        raise ValueError('Worldline graph and chronological frame replay disagree')
    if exact_binary != 2 * m * n:
        raise ValueError('Identical-basis control changed its capacity baseline')
    # Only literal exchanges have immutable original worldline identities.
    # Each designated central copy joins original source t and original sink
    # t. Their two disjoint paths give 2*n by crossed endpoint triangles,
    # independent of basis coefficient mixing at earlier scalar gates.
    proof = None
    if exchange_kind == 'literal':
        if origins != list(range(2 * m)) or sorted(middle) != [(j, m + j) for j in range(m)]:
            raise ValueError('Original paired worldlines failed to return/match')
        for j in range(m):
            if f.distance(starts[j], ends[m + j], n) + f.distance(starts[m + j], ends[j], n) != 2 * n:
                raise ValueError('Crossed physical endpoint distance failed')
        proof = dict(original_paired_middle_worldlines=middle, original_roles_restored=True,
                     any_common_frame_rank_lower_bound=2 * m * n,
                     scope='All frames in the rank metric, for this identical-basis literal-exchange topology only.')
    operator = physical_columns(word, n, m)
    wrong_frame = physical_columns(word, n, m, True) if exchange_kind == 'literal' else None
    return dict(status='PASS COMPLETE LITERAL/SHEAR EXCHANGE CONTROL', active_bits=n, data_roles=m,
                basis_kind=basis_kind, exchange_kind=exchange_kind, payload_stock=2 * m,
                capacity=2 * m * n, exact_zero_full_rank_optimum=exact_binary,
                zero_full_histogram=histogram, any_frame_literal_lower_bound=proof,
                scalar_columns=scalar, wrong_copy_control=corruption, physical_operator=operator,
                missing_frame_carry_control=wrong_frame, scalar_operation_counts=dict(Counter(e[0] for e in word)),
                paid_raw_exchange_stages=sum(e[0] == 'swap' for e in word),
                raw_exchange_record_pairs=sum(e[0] == 'swap' for e in word) * (1 << n),
                tape_cost_scope='Every raw exchange stage and record pair is retained. Sequential tape scheduling, word precision and head movement are unpaid; no zero-cost native exchange premise.',
                middle_permutation=permutation,
                complete_word=[[e[0], *e[1:3], str(e[3])] if e[0] == 'add'
                               else [e[0], e[1], str(e[2])] if e[0] == 'scale' else list(e) for e in word],
                seconds=time.monotonic() - started,
                scope='Complete finite fixed labeled Gaussian source/sink operator, no initialized ancillas. Raw exchanges carry actual operators and virtual coefficients; rank and data movement are separate. No multiplier recurrence, precision or exponent claim.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    specs = [(3, 3, basis_kind, exchange_kind) for basis_kind in ('sum', 'side')
             for exchange_kind in ('literal', 'signed-shears')]
    paths = [Path(__file__), Path(g.__file__), Path(f.__file__),
             Path(f.__file__).with_name('lagrangian_graph_completion.py'),
             Path(f.__file__).with_name('trimmed_zeta_dirty_probe.py'), f.SIDE_SOURCE]
    hashes = {path: sha256(path.read_bytes()).hexdigest() for path in paths}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, specs=specs,
                    source_sha256={path.name: value for path, value in hashes.items()},
                    hypothesis='A literal raw exchange avoids a common-frame constraint, but its worldline still carries original endpoint obligations.')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    cases = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(probe, spec): spec for spec in specs}
        for future in as_completed(jobs):
            result = future.result()
            cases.append(result)
            print(json.dumps({key: result[key] for key in ('status', 'basis_kind', 'exchange_kind',
                                                          'exact_zero_full_rank_optimum', 'paid_raw_exchange_stages', 'seconds')}), flush=True)
    if any(sha256(path.read_bytes()).hexdigest() != value for path, value in hashes.items()):
        raise ValueError('Effective source changed during exchange experiment')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=cases), indent=2) + '\n')


if __name__ == '__main__':
    main()
