#!/usr/bin/env python3
"""Exact directional and nonlinear cover-matching signed-zeta boundaries.

This is a finite native-interface discriminator, not a faster zeta supplier.
Monomial routes and every scalar/dirty endpoint remain explicit obligations.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time


def full_matrix(h):
    size = 1 << h
    return [
        [(-1 if j.bit_count() % 2 else 1) if j & ~i == 0 else 0
         for j in range(size)]
        for i in range(size)
    ]


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def right_matching(matrix, pairs):
    """Literal right multiplication by the directed two-word involution."""
    out = [row[:] for row in matrix]
    for low, high in pairs:
        for row in range(len(matrix)):
            out[row][low] = matrix[row][low] + matrix[row][high]
            out[row][high] = -matrix[row][high]
    return out


def left_matching(matrix, pairs):
    out = [row[:] for row in matrix]
    for low, high in pairs:
        out[high] = [a-b for a, b in zip(matrix[low], matrix[high])]
    return out


def right_full(matrix, h):
    out = matrix
    for bit in range(h):
        pairs = tuple((a, a | (1 << bit))
                      for a in range(1 << h) if not a >> bit & 1)
        out = right_matching(out, pairs)
    return out


def matrix_key(matrix):
    # These finite products have entries in [-4,4]; explicit failure retains
    # the bound rather than silently reducing a coefficient modulo a byte.
    values = [value for row in matrix for value in row]
    if any(abs(value) > 4 for value in values):
        raise ValueError('The exact matrix-key coefficient bound was exceeded')
    return bytes(value+4 for value in values)


def digest(matrix):
    return sha256(json.dumps(matrix, separators=(',', ':')).encode()).hexdigest()


def support(matrix):
    row_degrees = [sum(bool(value) for value in row) for row in matrix]
    col_degrees = [sum(bool(row[column]) for row in matrix)
                   for column in range(len(matrix))]
    maximum = max(row_degrees + col_degrees)
    return dict(max_row=max(row_degrees), max_column=max(col_degrees),
                minimum_total_child_width=(maximum-1).bit_length(),
                row_histogram=dict(sorted(Counter(row_degrees).items())),
                column_histogram=dict(sorted(Counter(col_degrees).items())))


def components(matrix):
    """Connected components of the bipartite nonzero graph, with no gauge."""
    size = len(matrix)
    adjacency = [[] for _ in range(2*size)]
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value:
                adjacency[i].append(size+j)
                adjacency[size+j].append(i)
    remaining = set(range(2*size)); result = []
    while remaining:
        stack = [min(remaining)]; remaining.remove(stack[0]); vertices = []
        while stack:
            current = stack.pop(); vertices.append(current)
            for other in adjacency[current]:
                if other in remaining:
                    remaining.remove(other); stack.append(other)
        result.append((sum(v < size for v in vertices),
                       sum(v >= size for v in vertices)))
    return sorted(result)


def directed_pairs(h, direction, functional):
    if (direction & functional).bit_count() % 2 != 1:
        raise ValueError('The orientation must change along its direction')
    return tuple((a, a ^ direction) for a in range(1 << h)
                 if (a & functional).bit_count() % 2 == 0)


def cover_matchings(h):
    size = 1 << h
    def visit(unused, pairs):
        if not unused:
            yield tuple(sorted(pairs)); return
        first = min(unused)
        for bit in range(h):
            other = first ^ (1 << bit)
            if other in unused:
                low, high = sorted((first, other), key=int.bit_count)
                yield from visit(unused - {first, other}, pairs + [(low, high)])
    return list(visit(set(range(size)), []))


def apply_matrix(matrix, records, h, columns):
    """Column-major h-bit fields; the order is not a free native transpose."""
    out = list(records); size = 1 << h
    for column in range(columns):
        shift = column*h; mask = (size-1) << shift
        stage = list(out)
        for base in range(len(out)):
            if base & mask:
                continue
            values = [out[base | (j << shift)] for j in range(size)]
            for i, row in enumerate(matrix):
                stage[base | (i << shift)] = tuple(
                    sum(value*values[j][part] for j, value in enumerate(row))
                    for part in (0, 1))
        out = stage
    return out


def physical_word(initial, pairs, h, columns=1, negative=None):
    """One arbitrary dirty helper, all 12 shears at the actual matching frame.

    Source frames are (T_M,I,I). The first virtual source is T_M*x_raw.
    Sink frames are (T_full,T_full*T_M,T_full); raw sign/exchange yields
    T_full on all three original labeled banks, including arbitrary dirty.
    """
    size = 1 << h; T = left_matching(identity(size), pairs)
    F = full_matrix(h); B = right_matching(F, pairs)
    data = [list(bank) for bank in initial]
    for role in (1, 2):
        data[role] = apply_matrix(T, data[role], h, columns)
    def add(target, source, coefficient):
        data[target] = [tuple(a+coefficient*b for a, b in zip(x, y))
                        for x, y in zip(data[target], data[source])]
    # Each four-shear commutator restores the arbitrary current helper.
    for source, target, coefficient in ((0, 1, 1), (1, 0, -1), (0, 1, 1)):
        add(2, source, 1); add(target, 2, coefficient)
        add(2, source, -1); add(target, 2, -coefficient)
    for role, transition in ((0, B), (1, F), (2, B)):
        if negative == 'omit final dirty return' and role == 2:
            continue
        if negative == 'replace full target transition by matching' and role == 1:
            transition = T
        data[role] = apply_matrix(transition, data[role], h, columns)
    data[0] = [tuple(-a for a in value) for value in data[0]]
    data[0], data[1] = data[1], data[0]
    return data


def physical_check(pairs, h, columns=1):
    size = 1 << (h*columns); F = full_matrix(h); output_digest = sha256()
    for role in range(3):
        for address in range(size):
            initial = [[(int(bank == role and a == address), 0)
                        for a in range(size)] for bank in range(3)]
            wanted = [apply_matrix(F, bank, h, columns) for bank in initial]
            actual = physical_word(initial, pairs, h, columns)
            if actual != wanted:
                raise AssertionError('Canonical source/sink/dirty column failed')
            output_digest.update(str(actual).encode())
    for grid in (0, 3):
        # Numerators on a shared 2^-grid Gaussian grid; all banks are dirty.
        initial = [[((a*7+bank*13+grid)%23-11,
                     (a*11+bank*5+grid*3)%29-14) for a in range(size)]
                   for bank in range(3)]
        wanted = [apply_matrix(F, bank, h, columns) for bank in initial]
        if physical_word(initial, pairs, h, columns) != wanted:
            raise AssertionError('Complete arbitrary Gaussian dirty field failed')
        output_digest.update(str(wanted).encode())
    controls = {}
    for name in ('omit final dirty return', 'replace full target transition by matching'):
        controls[name] = physical_word(initial, pairs, h, columns, name) != wanted
    if not all(controls.values()):
        raise AssertionError('A complete physical negative control failed to discriminate')
    return dict(all_physical_columns=3*size, full_gaussian_fields=2,
                gaussian_grid_bits=[0, 3], columns=columns,
                output_sha256=output_digest.hexdigest(), negative_controls=controls)


def linear_component(h):
    started = time.monotonic(); size = 1 << h; F = full_matrix(h)
    counts = Counter(); witnesses = {}; involutions = 0
    for direction in range(1, size):
        for functional in range(1, size):
            if (direction & functional).bit_count() % 2 != 1:
                continue
            pairs = directed_pairs(h, direction, functional)
            T = left_matching(identity(size), pairs)
            if left_matching(T, pairs) != identity(size):
                raise AssertionError('Directed source is not an exact involution')
            B = right_matching(F, pairs); profile = support(B)
            ordinary = direction.bit_count() == 1 and functional == direction
            category = ('coordinate' if ordinary else
                        'noncoordinate_direction' if direction.bit_count() > 1
                        else 'noncoordinate_orientation')
            counts[category] += 1; involutions += 1
            expected_width = h-1 if ordinary else h
            if profile['minimum_total_child_width'] != expected_width:
                raise AssertionError('The complete directional support criterion failed')
            if category == 'noncoordinate_direction':
                expected_origin = (size if direction.bit_count() % 2 == 0 else
                                   size - (size >> direction.bit_count()))
                if sum(bool(row[0]) for row in B) != expected_origin:
                    raise AssertionError('Noncoordinate origin support formula failed')
            if category == 'noncoordinate_orientation':
                row = size-1-direction
                if sum(bool(value) for value in B[row]) != 3*size//4:
                    raise AssertionError('Noncoordinate orientation row formula failed')
            witnesses.setdefault(category, dict(direction=direction, functional=functional,
                                                 profile=profile, matrix_sha256=digest(B)))
    return dict(status='PASS SIGNED ZETA LINEAR BOUNDARY SCREEN', h=h,
                oriented_line_count=involutions, categories=dict(counts), witnesses=witnesses,
                support_model='Invertible monomial/diagonal wrappers and Z/T children; summed child widths bound both row and column branching.',
                whole_native_supplier=False, seconds=time.monotonic()-started)


def cover_component(h):
    started = time.monotonic(); size = 1 << h; F = full_matrix(h)
    matches = cover_matchings(h)
    expected_count = {3: 9, 4: 272}[h]
    if len(matches) != expected_count:
        raise AssertionError('The complete cover-perfect-matching enumeration differs')
    child = [left_matching(identity(size), pairs) for pairs in matches]
    single_lookup = {matrix_key(matrix): (index,) for index, matrix in enumerate(child)}
    two_lookup = {}
    if h == 4:
        for left, matrix in enumerate(child):
            for right, pairs in enumerate(matches):
                two_lookup.setdefault(matrix_key(right_matching(matrix, pairs)), (left, right))
    remainder_lookup = single_lookup if h == 3 else two_lookup
    complementary_lookup = two_lookup if h == 4 else {
        matrix_key(right_matching(matrix, pairs)): (left, right)
        for left, matrix in enumerate(child) for right, pairs in enumerate(matches)}
    factorizable = []; unresolved = []; records = []; pair_compatibility = []
    cleanup_histogram = Counter(); graph_histogram = Counter(); all_physical = 0
    for index, pairs in enumerate(matches):
        B = right_matching(F, pairs); profile = support(B)
        if profile['minimum_total_child_width'] != h-1:
            raise AssertionError('A cover matching lost its exact half-sector branching bound')
        word = None
        if h == 3:
            word = complementary_lookup.get(matrix_key(B))
        else:
            for right, last in enumerate(matches):
                prefix = two_lookup.get(matrix_key(right_matching(B, last)))
                if prefix is not None:
                    word = prefix + (right,); break
        if word is None:
            unresolved.append(index)
        else:
            literal = identity(size)
            for gate in word:
                literal = right_matching(literal, matches[gate])
            if literal != B:
                raise AssertionError('Retained complementary child word is not exact')
            factorizable.append(index)
        reflected = right_full(B, h)  # F*T_M*F, not T_M unless actually commuting.
        reflected_profile = support(reflected)
        cleanup_histogram[reflected_profile['minimum_total_child_width']] += 1
        graph_histogram[str(components(B))] += 1
        physical = physical_check(pairs, h); all_physical += physical['all_physical_columns']
        records.append(dict(matching_index=index, pairs=pairs,
                            complement_word_indices=word,
                            complement_sha256=digest(B), complement_profile=profile,
                            reflected_cleanup_profile=reflected_profile,
                            reflected_cleanup_sha256=digest(reflected),
                            physical_word=physical))
        for source, source_pairs in enumerate(matches):
            relative = right_matching(B, source_pairs)
            short_word = remainder_lookup.get(matrix_key(relative))
            if short_word is not None:
                pair_compatibility.append((index, source, short_word))
    if len(set(matches)) != expected_count:
        raise AssertionError('The enumeration contains duplicate matching inputs')
    noncoordinate = next((record for record in records
                          if len({low ^ high for low, high in record['pairs']}) > 1), None)
    if noncoordinate is None:
        raise AssertionError('Nonlinear matching control absent')
    # Explicit two-column physical replay; these are all columns, not origins.
    two_column = physical_check(matches[noncoordinate['matching_index']], h, 2) if h == 3 else None
    return dict(status='PASS COVER MATCHING SIGNED ZETA BOUNDARIES', h=h,
                matching_count=len(matches), one_child_matrices=len(single_lookup),
                two_child_product_count=len(complementary_lookup),
                complements_factored_into_h_minus_one_cover_children=len(factorizable),
                unresolved_within_cover_only_factor_model=unresolved,
                reflected_cleanup_width_lower_histogram=dict(sorted(cleanup_histogram.items())),
                complement_bipartite_component_histogram=dict(graph_histogram),
                ordered_short_side_pairs=len(pair_compatibility),
                ordered_short_side_pair_witness=next((item for item in pair_compatibility
                                                      if item[0] == noncoordinate['matching_index']), None),
                all_matching_physical_columns=all_physical,
                optimistic_common_matching_dirty_word_rank=3*h, common_matching_payload_stock=3,
                common_matching_capacity=3*h, optimistic_common_matching_deficit=0,
                common_matching_ledger='Two width1 entrances, two complements whose summed widths are at least h-1 each, one fullwidth h call. Retained h-1 factor words attain equality; unresolved factors are not assigned that cost. All 12 scalar shears, final sign/exchange, nonlinear routers and arbitrary dirty restoration are paid obligations.',
                noncoordinate_witness=noncoordinate, two_column_control=two_column,
                records=records,
                scope='Complete finite cover matching and restricted factor enumeration. Complement factorization alone does not make F*T_M*F a width1 cleanup. The explicit common-frame dirty word has capacity equality, not a contracting native recurrence.',
                native_matching_routers_verified=False, seconds=time.monotonic()-started)


def probe(task):
    kind, h = task
    return linear_component(h) if kind == 'linear' else cover_component(h)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__); source_hash = sha256(source.read_bytes()).hexdigest()
    cases = [('linear', 3), ('linear', 4), ('cover', 3), ('cover', 4)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, cases=cases, seed=None, stdlib_only=True,
                    source_sha256={source.name: source_hash},
                    hypothesis='Nonlinear cover-matching T1 anchors may retain h-1 complementary words despite the linear-direction obstruction; bind reflected cleanup and a complete arbitrary-dirty canonical control before proposing a wider supplier.',
                    resource_preflight=dict(maximum_matching_count=272,
                                            maximum_two_child_candidates=73984,
                                            aggregate_memory_bytes_upper=512*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(probe, case): case for case in cases}
        for future in as_completed(futures):
            result = future.result(); results.append(result)
            print(json.dumps({key: result[key] for key in result
                              if key in ('status', 'h', 'matching_count',
                                         'complements_factored_into_h_minus_one_cover_children',
                                         'reflected_cleanup_width_lower_histogram', 'seconds')}), flush=True)
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('Effective source changed during signed-zeta matching experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
