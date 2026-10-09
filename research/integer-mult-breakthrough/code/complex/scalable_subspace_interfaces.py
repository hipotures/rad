#!/usr/bin/env python3
"""Compact actual-frame interfaces from Clifford tableaux and quadratic sums.

The producer of canonical F_E words is imported as a pinned read-only library.
No address matrix is used by compile_interface. Matrices are bounded test
oracles only. Complete fixed-tape payload routing remains a separate charge.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
from time import perf_counter

import canonical_subspace_frames as reference


REFERENCE_SHA = 'ddb0255a0668d43dd61c5183f3a0de56015f02b6acc462c4b8ad5b3f8173598b'
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def dot(a, b):
    return (a & b).bit_count() & 1


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def basis(rows):
    return reference.basis(rows)


def embed(value, columns):
    return reference.embed(value, columns)


def solve_affine(rows, right, variables):
    """Solve row-dot-variable=right, returning offset and nullspace columns."""
    work = [row | (((right >> j) & 1) << variables)
            for j, row in enumerate(rows)]
    rank = 0
    pivots = []
    for bit in range(variables):
        pivot = next((j for j in range(rank, len(work)) if work[j] >> bit & 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for j in range(len(work)):
            if j != rank and work[j] >> bit & 1:
                work[j] ^= work[rank]
        pivots.append(bit)
        rank += 1
    if any(row & ((1 << variables) - 1) == 0 and row >> variables & 1
           for row in work[rank:]):
        raise ValueError('Inconsistent affine system')
    offset = sum(((work[j] >> variables) & 1) << bit
                 for j, bit in enumerate(pivots))
    null = []
    for free in range(variables):
        if free in pivots:
            continue
        value = 1 << free
        for j, bit in enumerate(pivots):
            value |= ((work[j] >> free) & 1) << bit
        null.append(value)
    return offset, tuple(null)


def coordinates(vector, columns, ambient):
    rows = [sum(((column >> bit) & 1) << j for j, column in enumerate(columns))
            for bit in range(ambient)]
    offset, null = solve_affine(rows, vector, len(columns))
    if null:
        raise ValueError('Coordinates are not unique')
    return offset


def inverse_columns(columns):
    n = len(columns)
    return tuple(coordinates(1 << j, columns, n) for j in range(n))


def multiply_gaussian(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def alpha_numerator(rank):
    value = (1, 0)
    for _ in range(rank):
        value = multiply_gaussian(value, (1, 1))
    return value


def pauli_product(a, b):
    """i^p X^x Z^z convention, with exact product phase."""
    x, z, p = a
    X, Z, P = b
    return x ^ X, z ^ Z, (p + P + 2 * dot(z, X)) % 4


def pauli_combination(generators, mask):
    result = (0, 0, 0)
    for j in bits(mask):
        result = pauli_product(result, generators[j])
    return result


def literal_word(E, n):
    """Expand canonical anchors to phase, binary route, Htilde and C gates."""
    spec = reference.frame_spec(E, n)
    word = []
    for item in spec['word']:
        kind = item[0]
        if kind == 'quadratic_phase':
            word.append(('D', item[1]))
        elif kind == 'linear_route':
            word.append(('P', tuple(item[1])))
        elif kind == 'linear_route_inverse':
            word.append(('P', inverse_columns(item[1])))
        elif kind == 'H_tilde':
            word.extend(('H', j, 1) for j in range(item[1]))
        elif kind == 'C_full':
            word.extend(('C', 1 << j, 1) for j in range(n))
        elif kind == 'C_line':
            word.append(('C', item[1], 1))
        elif kind == 'C_line_inverse':
            word.append(('C', item[1], -1))
        else:
            raise ValueError(('Unknown actual frame gate', item))
    return word


def inverse_word(word):
    result = []
    for gate in reversed(word):
        if gate[0] == 'D':
            result.append(('D', -gate[1]))
        elif gate[0] == 'P':
            result.append(('P', inverse_columns(gate[1])))
        else:
            result.append((gate[0], gate[1], -gate[2]))
    return result


def conjugate_pauli(value, gate, n):
    x, z, p = value
    if gate[0] == 'D':
        p += gate[1] * x.bit_count()
        z ^= x
    elif gate[0] == 'P':
        columns = gate[1]
        x = embed(x, columns)
        z = sum(dot(z, c) << j for j, c in enumerate(inverse_columns(columns)))
    elif gate[0] == 'H':
        bit = 1 << gate[1]
        a, b = bool(x & bit), bool(z & bit)
        p += 2 * a * b
        if a != b:
            x ^= bit
            z ^= bit
    elif gate[0] == 'C':
        if dot(z, gate[1]):
            x ^= gate[1]
            p -= gate[2]
    elif gate[0] == 'Q':
        q = parse_quadratic(gate[1])
        p += q.evaluate(x) - q.constant
        correction = sum((coefficient & 1) << j for j, coefficient in enumerate(q.linear)) & x
        for j in bits(x):
            correction ^= q.cross[j]
        z ^= correction
    elif gate[0] == 'NOT':
        p += 2 * dot(z, gate[1])
    else:
        raise ValueError(('Unknown gate', gate))
    return x, z, p % 4


def tableau(word, n):
    X = [(1 << j, 0, 0) for j in range(n)]
    Z = [(0, 1 << j, 0) for j in range(n)]
    for gate in word:
        X = [conjugate_pauli(p, gate, n) for p in X]
        Z = [conjugate_pauli(p, gate, n) for p in Z]
    return X, Z


class Quadratic:
    """Z4 polynomial: constant + linear + twice square-free pair products."""
    def __init__(self, n=0):
        self.constant = 0
        self.linear = [0] * n
        self.cross = [0] * n

    def new_variable(self):
        j = len(self.linear)
        self.linear.append(0)
        self.cross.append(0)
        return 1 << j

    def pair(self, i, j):
        if i == j:
            self.linear[i] = (self.linear[i] + 2) % 4
        else:
            self.cross[i] ^= 1 << j
            self.cross[j] ^= 1 << i

    def parity(self, mask, coefficient, offset=0):
        if offset:
            self.constant = (self.constant + coefficient) % 4
            coefficient = -coefficient
        coefficient %= 4
        positions = list(bits(mask))
        for i in positions:
            self.linear[i] = (self.linear[i] + coefficient) % 4
        if coefficient & 1:
            for j, i in enumerate(positions):
                for other in positions[j + 1:]:
                    self.pair(i, other)

    def two_parities(self, left, right, left_offset=0, right_offset=0):
        self.constant = (self.constant + 2 * left_offset * right_offset) % 4
        if left_offset:
            self.parity(right, 2)
        if right_offset:
            self.parity(left, 2)
        for i in bits(left):
            for j in bits(right):
                self.pair(i, j)

    def evaluate(self, value):
        total = self.constant + sum(self.linear[j] for j in bits(value))
        for j in bits(value):
            total += 2 * ((self.cross[j] & value & ((1 << j) - 1)).bit_count())
        return total % 4

    def substitute(self, offset, columns):
        result = Quadratic(len(columns))
        result.constant = self.constant
        forms = [sum(((column >> j) & 1) << i for i, column in enumerate(columns))
                 for j in range(len(self.linear))]
        for j, coefficient in enumerate(self.linear):
            result.parity(forms[j], coefficient, offset >> j & 1)
        for j, neighbors in enumerate(self.cross):
            for i in bits(neighbors & ((1 << j) - 1)):
                result.two_parities(forms[i], forms[j], offset >> i & 1, offset >> j & 1)
        return result

    def erase(self, j):
        for other in bits(self.cross[j]):
            self.cross[other] &= ~(1 << j)
        self.linear[j] = 0
        self.cross[j] = 0

    def gauss_sum(self):
        """Exact sum of i^q, by odd singleton and alternating-pair elimination."""
        q = self.substitute(0, [1 << j for j in range(len(self.linear))])
        active = (1 << len(q.linear)) - 1
        factor = (1, 0)
        while active:
            odd = next((j for j in bits(active) if q.linear[j] & 1), None)
            if odd is not None:
                coefficient = q.linear[odd]
                neighbors = q.cross[odd]
                q.erase(odd)
                active ^= 1 << odd
                q.parity(neighbors, -coefficient)
                factor = multiply_gaussian(factor, (1, 1 if coefficient == 1 else -1))
                continue
            first = next((j for j in bits(active) if q.cross[j]), None)
            if first is not None:
                second = next(bits(q.cross[first]))
                a, b = q.linear[first] // 2, q.linear[second] // 2
                left = q.cross[first] & ~(1 << second)
                right = q.cross[second] & ~(1 << first)
                q.erase(first)
                q.erase(second)
                active &= ~((1 << first) | (1 << second))
                q.two_parities(left, right, a, b)
                factor = (2 * factor[0], 2 * factor[1])
                continue
            if any(q.linear[j] for j in bits(active)):
                return (0, 0)
            multiplier = 1 << active.bit_count()
            factor = (multiplier * factor[0], multiplier * factor[1])
            break
        return multiply_gaussian(factor, UNITS[q.constant])


def path_sum_at_zero(word, n, output):
    """Evaluate one actual column coefficient, retaining every global phase."""
    address = [0] * n
    q = Quadratic()
    child_factors = 0
    for gate in word:
        if gate[0] == 'D':
            for expression in address:
                q.parity(expression, gate[1])
        elif gate[0] == 'P':
            routed = [0] * n
            for j, column in enumerate(gate[1]):
                for i in bits(column):
                    routed[i] ^= address[j]
            address = routed
        elif gate[0] == 'H':
            variable = q.new_variable()
            bit = gate[1]
            q.two_parities(address[bit], variable)
            address[bit] = variable
            if gate[2] == -1:
                q.constant = (q.constant - 1) % 4
            child_factors += 1
        elif gate[0] == 'C':
            variable = q.new_variable()
            for j in bits(gate[1]):
                address[j] ^= variable
            q.parity(variable, -gate[2])
            if gate[2] == -1:
                q.constant = (q.constant - 1) % 4
            child_factors += 1
        else:
            raise ValueError(('Unknown path-sum gate', gate))
    offset, null = solve_affine(address, output, len(q.linear))
    gauss = q.substitute(offset, null).gauss_sum()
    numerator = multiply_gaussian(alpha_numerator(child_factors), gauss)
    return numerator, child_factors, len(null)


def fit_quadratic(function, n):
    q = Quadratic(n)
    q.constant = function(0) % 4
    for j in range(n):
        q.linear[j] = (function(1 << j) - q.constant) % 4
    for j in range(n):
        for i in range(j):
            coefficient = (function((1 << i) | (1 << j)) - q.constant
                           - q.linear[i] - q.linear[j]) % 4
            if coefficient not in (0, 2):
                raise AssertionError('Wrapper has a nonquadratic pair coefficient')
            if coefficient:
                q.pair(i, j)
    return q


def serialize_quadratic(q):
    return dict(constant=q.constant, linear=q.linear,
                cross=[[i, j, 2] for j, neighbors in enumerate(q.cross)
                       for i in bits(neighbors & ((1 << j) - 1))])


def parse_quadratic(data):
    q = Quadratic(len(data['linear']))
    q.constant = data['constant']
    q.linear = list(data['linear'])
    for i, j, coefficient in data['cross']:
        if coefficient != 2:
            raise ValueError('Only even cross coefficients are admissible')
        q.pair(i, j)
    return q


def compile_interface(E, F, n):
    """Scalable exact U=F_F F_E^-1, with exactly one distance-rank C child.

    The result is compact affine input/output routing, two Z4 quadratics,
    and a selected rank. Internal compilation uses O(n)-variable quadratic
    sums and binary elimination, never an array indexed by all addresses.
    """
    E, F = basis(E), basis(F)
    # This is the Grassmann distance for the actual L_E representatives.
    # Nested pairs give the absolute dimension difference, in either
    # direction; nonnested pairs retain their larger, fully paid width.
    rank = 2 * len(basis(E + F)) - len(E) - len(F)
    word = inverse_word(literal_word(E, n)) + literal_word(F, n)
    X, Z = tableau(word, n)
    source = basis(value[0] for value in Z)
    if len(source) != rank:
        raise AssertionError(('Tableau mixing rank differs from Grassmann distance', E, F, n))
    rows = [sum(((value[0] >> j) & 1) << k for k, value in enumerate(Z))
            for j in range(n)]
    _, pure_masks = solve_affine(rows, 0, n)
    pure = [pauli_combination(Z, mask) for mask in pure_masks]
    if any(x or p & 1 for x, z, p in pure):
        raise AssertionError('Pure-Z stabilizer is not an even character')
    offset, null = solve_affine([value[1] for value in pure],
                               sum((value[2] // 2) << j for j, value in enumerate(pure)), n)
    if basis(null) != source:
        raise AssertionError('Affine support and translation span differ')
    numerator, path_rank, free_variables = path_sum_at_zero(word, n, offset)
    if path_rank < rank:
        raise AssertionError('Path-sum normalization has too few factors')
    target = alpha_numerator(rank)
    units = [p for p in range(4) if numerator == tuple(v << (path_rank - rank)
             for v in multiply_gaussian(target, UNITS[p]))]
    if len(units) != 1:
        raise AssertionError(('Actual global coefficient is not the selected C amplitude', numerator, rank, path_rank))
    global_phase = units[0]
    support_generators = []
    for vector in source:
        coefficients, _ = solve_affine(rows, vector, n)
        support_generators.append(pauli_combination(Z, coefficients))
    support_coordinate_rows = [sum(((v >> j) & 1) << k for k, v in enumerate(source))
                               for j in range(n)]
    def unit(x, y):
        shift, character, exponent = pauli_combination(X, y)
        a, extra = solve_affine(support_coordinate_rows, x ^ offset ^ shift, rank)
        if extra:
            raise AssertionError('Support coordinate is not unique')
        sx, sz, sp = pauli_combination(support_generators, a)
        return (global_phase + sp + 2 * dot(sz, offset) + exponent
                + 2 * dot(character, x ^ shift)) % 4
    quotient_constraints = [sum(dot(row, value[0]) << j for j, value in enumerate(X))
                            for row in reference.perpendicular(source, n)]
    _, active_inputs = solve_affine(quotient_constraints, 0, n)
    if len(active_inputs) != rank:
        raise AssertionError('Input support has the wrong dimension')
    inputs = list(reference.complete_basis(basis(active_inputs), n))
    coupling = []
    for vector in source:
        row = 0
        for j, y in enumerate(inputs[:rank]):
            exponent = (unit(offset ^ vector, y) + unit(offset, 0)
                        - unit(offset ^ vector, 0) - unit(offset, y)) % 4
            if exponent not in (0, 2):
                raise AssertionError('Input/output coupling is not binary')
            row |= (exponent // 2) << j
        coupling.append(row)
    corrected = []
    for j in range(rank):
        coeff, null = solve_affine(coupling, 1 << j, rank)
        if null:
            raise AssertionError('Active bilinear coupling is singular')
        corrected.append(embed(coeff, inputs[:rank]))
    inputs = corrected + inputs[rank:]
    outputs = list(source) + [pauli_combination(X, y)[0] for y in inputs[rank:]]
    if len(basis(outputs)) != n:
        raise AssertionError('Spectator routing is singular')
    active_mask = (1 << rank) - 1
    def row_phase(value):
        spectator = value & ~active_mask
        y = embed(spectator, inputs)
        origin = unit(offset ^ embed(spectator, outputs), y)
        return (unit(offset ^ embed(value, outputs), y)
                + (value & active_mask).bit_count() - origin) % 4
    def column_phase(value):
        spectator = value & ~active_mask
        return (unit(offset ^ embed(spectator, outputs), embed(value, inputs))
                + (value & active_mask).bit_count()) % 4
    row_q = fit_quadratic(row_phase, n)
    column_q = fit_quadratic(column_phase, n)
    return dict(n=n, source_subspace=list(E), target_subspace=list(F),
                selected_rank_per_column=rank, one_bulk_child_calls=int(rank > 0),
                output_affine_offset=offset, output_columns=outputs, input_columns=inputs,
                output_quadratic=serialize_quadratic(row_q),
                input_quadratic=serialize_quadratic(column_q),
                global_unit_exponent=global_phase,
                compilation=dict(path_variables=path_rank,
                                 summed_free_variables=free_variables,
                                 binary_elimination_only=True,
                                 full_address_arrays_allocated=False))


def reconstructed_entry(normal, x, y):
    """Exact numerator on grid 2^-rank, including every unit wrapper."""
    n, rank = normal['n'], normal['selected_rank_per_column']
    a = coordinates(x ^ normal['output_affine_offset'], normal['output_columns'], n)
    b = coordinates(y, normal['input_columns'], n)
    if a >> rank != b >> rank:
        return (0, 0)
    phase = (parse_quadratic(normal['output_quadratic']).evaluate(a)
             + parse_quadratic(normal['input_quadratic']).evaluate(b)
             - ((a ^ b) & ((1 << rank) - 1)).bit_count()) % 4
    return multiply_gaussian(alpha_numerator(rank), UNITS[phase])


def compiled_word(normal):
    """Exact temporal wrappers around one selected-bit C tensor block."""
    rank = normal['selected_rank_per_column']
    return ([('P', inverse_columns(normal['input_columns'])),
             ('Q', normal['input_quadratic'])]
            + [('C', 1 << j, 1) for j in range(rank)]
            + [('Q', normal['output_quadratic']),
               ('P', tuple(normal['output_columns'])),
               ('NOT', normal['output_affine_offset'])])


def assert_complete_tableau(normal, original_word):
    """All Pauli images plus one nonzero coefficient fix the whole operator.

    Both words are unitary; agreement on all X/Z generator images leaves
    only a global scalar. The exact path-sum coefficient already retained
    by the compiler is the value at (output-offset, input-zero), where the
    compiled coefficient has the stated sum of quadratic constants.
    """
    n = normal['n']
    original = tableau(original_word, n)
    reconstructed = tableau(compiled_word(normal), n)
    if original != reconstructed:
        raise AssertionError('One-child word differs on a complete Pauli generator')
    constant = (normal['input_quadratic']['constant']
                + normal['output_quadratic']['constant']) % 4
    if constant != normal['global_unit_exponent']:
        raise AssertionError('Compiled word omitted the actual global amplitude unit')
    return 2 * n


def check_gauss(seed=614713, count=256):
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randrange(0, 9)
        q = Quadratic(n)
        q.constant = rng.randrange(4)
        q.linear = [rng.randrange(4) for _ in range(n)]
        for j in range(n):
            for i in range(j):
                if rng.randrange(2):
                    q.pair(i, j)
        actual = q.gauss_sum()
        expected = [0, 0]
        for value in range(1 << n):
            term = UNITS[q.evaluate(value)]
            expected[0] += term[0]
            expected[1] += term[1]
        if actual != tuple(expected):
            raise AssertionError(('Quadratic elimination failed', seed, n, actual, expected))
    return count


def matrix_probe(n):
    spaces = reference.all_subspaces(n)
    frames = {E: reference.frame_matrix(E, n) for E in spaces}
    entries = cases = 0
    digest = sha256()
    for E in spaces:
        for F in spaces:
            normal = compile_interface(E, F, n)
            rank = normal['selected_rank_per_column']
            divisor = 1 << (len(E) + len(F) - rank)
            expected = [[(0, 0)] * (1 << n) for _ in range(1 << n)]
            A, B = frames[E]['numerator'], frames[F]['numerator']
            for x in range(1 << n):
                for y in range(1 << n):
                    value = (0, 0)
                    for k in range(1 << n):
                        term = multiply_gaussian(B[x][k], (A[y][k][0], -A[y][k][1]))
                        value = (value[0] + term[0], value[1] + term[1])
                    if any(coefficient % divisor for coefficient in value):
                        raise AssertionError('Relative matrix has a non-dyadic selected grid')
                    expected[x][y] = value[0] // divisor, value[1] // divisor
            for x in range(1 << n):
                for y in range(1 << n):
                    if reconstructed_entry(normal, x, y) != expected[x][y]:
                        raise AssertionError(('Compiled coefficient failed', n, E, F, x, y, normal))
            entries += (1 << n) ** 2
            cases += 1
            digest.update(json.dumps(normal, sort_keys=True, separators=(',', ':')).encode())
    # The global unit and the affine support are physical, rather than gauges
    # that may be omitted at a mixer.
    sample = compile_interface((7,), basis((7, 8)), max(4, n))
    corrupted = json.loads(json.dumps(sample))
    corrupted['input_quadratic']['constant'] = (corrupted['input_quadratic']['constant'] + 1) % 4
    if all(reconstructed_entry(sample, x, 0) == reconstructed_entry(corrupted, x, 0)
           for x in range(1 << sample['n'])):
        raise AssertionError('Omitted global-unit negative was not rejected')
    original_word = inverse_word(literal_word((7,), sample['n'])) + literal_word(basis((7, 8)), sample['n'])
    assert_complete_tableau(sample, original_word)
    wrong_offset = json.loads(json.dumps(sample))
    wrong_offset['output_affine_offset'] ^= 1
    try:
        assert_complete_tableau(wrong_offset, original_word)
    except AssertionError:
        pass
    else:
        raise AssertionError('Wrong affine routing negative was not rejected')
    return dict(kind='complete coefficient replay', n=n, subspaces=len(spaces),
                interfaces=cases, exact_entries=entries, normal_forms_sha256=digest.hexdigest(),
                wrong_global_unit_rejected=True, wrong_affine_routing_rejected=True)


def large_probe(case):
    n, seed = case
    rng = random.Random(seed)
    counts = []
    digest = sha256()
    for attempt in range(6):
        dims = [(0, n), (1, n - 1), (n // 3, 2 * n // 3),
                (n // 2, n // 2 + 1), (n, n - 1), (1, 1)][attempt]
        if attempt == 1:
            line = (1 << min(n, 5)) - 1
            E, F = (line,), reference.perpendicular((line,), n)
            if dot(line, line):
                # Odd line is not nested in its own perpendicular. Use an
                # independent odd hyperplane that actually contains it.
                other = 1 << (n - 1)
                F = reference.perpendicular((other,), n)
        else:
            columns = []
            needed = n if attempt == 3 else max(dims)
            while len(columns) < needed:
                value = rng.randrange(1, 1 << n)
                if len(basis(columns + [value])) > len(columns):
                    columns.append(value)
            if attempt == 3:
                E, F = basis(columns[:dims[0]]), basis(columns[-dims[1]:])
            elif attempt == 5:
                left = rng.randrange(1, 1 << n)
                right = rng.randrange(1, 1 << n)
                while left == right:
                    right = rng.randrange(1, 1 << n)
                E, F = (left,), (right,)
            else:
                E, F = basis(columns[:dims[0]]), basis(columns[:dims[1]])
        normal = compile_interface(E, F, n)
        word = inverse_word(literal_word(E, n)) + literal_word(F, n)
        assert_complete_tableau(normal, word)
        X, Z = tableau(word, n)
        out_q = parse_quadratic(normal['output_quadratic'])
        in_q = parse_quadratic(normal['input_quadratic'])
        rank = normal['selected_rank_per_column']
        for _ in range(40):
            a, b = rng.randrange(1 << n), rng.randrange(1 << n)
            if a >> rank != b >> rank:
                b = (b & ((1 << rank) - 1)) | (a & ~((1 << rank) - 1))
            x = normal['output_affine_offset'] ^ embed(a, normal['output_columns'])
            y = embed(b, normal['input_columns'])
            expected_unit = (out_q.evaluate(a) + in_q.evaluate(b)
                             - ((a ^ b) & ((1 << rank) - 1)).bit_count()) % 4
            # Exact global coefficient plus independent Pauli conjugation
            # relates arbitrary entries to the column-zero quadratic.
            shift, character, exponent = pauli_combination(X, y)
            x0 = x ^ shift
            a0 = coordinates(x0 ^ normal['output_affine_offset'], normal['output_columns'], n)
            if a0 >> rank:
                raise AssertionError('Tableau image changed a spectator fiber')
            actual_unit = (out_q.evaluate(a0) + in_q.evaluate(0) - a0.bit_count()
                           + exponent + 2 * dot(character, x0)) % 4
            if actual_unit != expected_unit:
                raise AssertionError('Large compact phase control failed')
        counts.append(rank)
        digest.update(json.dumps(normal, sort_keys=True, separators=(',', ':')).encode())
    return dict(kind='seeded exact algebraic controls', n=n, seed=seed,
                interfaces=len(counts), selected_ranks=counts,
                random_phase_relations_each=40,
                complete_Pauli_generators_per_interface=2*n,
                exact_global_coefficient_each=True,
                normal_forms_sha256=digest.hexdigest(),
                full_address_matrix_enumerated=False)


def run_case(case):
    if isinstance(case, int):
        return matrix_probe(case)
    return large_probe(case)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError('Use one to four workers')
    reference_file = Path(reference.__file__)
    if sha256(reference_file.read_bytes()).hexdigest() != REFERENCE_SHA:
        raise AssertionError('Actual frame reference does not match pinned source')
    started_utc = datetime.now(timezone.utc).isoformat()
    source = Path(__file__)
    protocol = dict(started_utc=started_utc, workers=args.workers, native_threads_each=1,
                    source_sha256=sha256(source.read_bytes()).hexdigest(),
                    actual_frame_source_sha256=REFERENCE_SHA,
                    dependencies='Python standard library only',
                    scope='Compact polynomial algebraic compiler; no native fixed-tape payload bound or exponent.')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    start = perf_counter()
    gauss_controls = check_gauss(count=64 if args.bounded else 256)
    cases = [3] if args.bounded else [3, 4, (16, 81421), (32, 91421), (64, 101421)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(run_case, cases))
    certificate = dict(status='PASS COMPACT ACTUAL-FRAME INTERFACES', protocol=protocol,
                       completed_utc=datetime.now(timezone.utc).isoformat(),
                       elapsed_seconds=perf_counter() - start,
                       exhaustive_small_quadratic_sums=gauss_controls, cases=results,
                       scientific_scope='Finite exact matrix replay and seeded large algebraic controls support the explicit all-size symbolic algorithm. Native complete-stream movement, precision guards, recursive stock and exponent remain separate.')
    if sha256(source.read_bytes()).hexdigest() != protocol['source_sha256']:
        raise AssertionError('Compiler source changed during execution')
    if sha256(reference_file.read_bytes()).hexdigest() != protocol['actual_frame_source_sha256']:
        raise AssertionError('Imported actual frame source changed during execution')
    if args.output:
        (args.output / 'certificate.json').write_text(json.dumps(certificate, indent=2) + '\n')
    print(json.dumps(certificate, indent=2), flush=True)


if __name__ == '__main__':
    main()
