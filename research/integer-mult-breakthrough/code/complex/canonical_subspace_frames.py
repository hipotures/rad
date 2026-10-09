#!/usr/bin/env python3
"""Actual Gaussian representatives of L_E, with pinned line/full endpoints.

frame_spec(E,n) is a scalable literal gate specification. frame_matrix(E,n)
and compile_nested(E,F,n) are exact bounded coefficient adapters, retaining
all affine maps and quadratic fourth-root gauges. They are not a native tape
compiler. The test enumerates degenerate subspaces as well as ordinary ones.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter


UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conj(a):
    return a[0], -a[1]


def phase(a, exponent):
    return mul(a, UNITS[exponent % 4])


def alpha_numerator(r):
    value = (1, 0)
    for _ in range(r):
        value = mul(value, (1, 1))
    return value


def dot(a, b):
    return (a & b).bit_count() % 2


def basis(rows):
    pivots = {}
    for value in rows:
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            new_bit = value.bit_length() - 1
            for bit in pivots:
                if pivots[bit] >> new_bit & 1:
                    pivots[bit] ^= value
            pivots[new_bit] = value
    return tuple(pivots[bit] for bit in sorted(pivots))


def embed(value, columns):
    result = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            result ^= column
    return result


def perpendicular(E, n):
    E = basis(E)
    pivots = {row.bit_length() - 1: row for row in E}
    vectors = []
    for bit in range(n):
        if bit in pivots:
            continue
        value = 1 << bit
        for pivot, row in pivots.items():
            if dot(value, row):
                value ^= 1 << pivot
        vectors.append(value)
    result = basis(vectors)
    if any(dot(a, b) for a in result for b in E):
        raise AssertionError('Nullspace construction failed')
    return result


def complete_basis(E, n):
    columns = list(E)
    for bit in range(n):
        if len(basis(columns + [1 << bit])) > len(columns):
            columns.append(1 << bit)
    if len(columns) != n:
        raise AssertionError('Address routing is incomplete')
    return tuple(columns)


def frame_spec(E, n):
    """Return one deterministic ACTUAL operator for every binary subspace.

    D=diag(i^weight). Generic operator is D^-1 P Htilde_r P^-1 D^-1.
    Htilde_r=alpha^r*Hadamard_r, equivalently S*C^r*S. Endpoint overrides
    are literal operators, never abstract free gauge identifications.
    """
    if n < 1 or any(type(x) is not int or not 0 <= x < 1 << n for x in E):
        raise ValueError('Invalid address dimension or subspace')
    E = basis(E); r = len(E)
    common = dict(n=n, subspace=E, rank=r, gaussian_grid_bits=r)
    if r == 0:
        return common | dict(anchor='identity', word=[])
    if r == n:
        return common | dict(anchor='full-C', word=[('C_full', n)])
    if r == 1 and E[0].bit_count() % 2:
        return common | dict(anchor='odd-line-C', line=E[0], word=[('C_line', E[0])])
    complement = perpendicular(E, n)
    if len(complement) == 1 and complement[0].bit_count() % 2:
        return common | dict(anchor='odd-kernel-C', line=complement[0],
                             word=[('C_line_inverse', complement[0]), ('C_full', n)])
    columns = complete_basis(E, n)
    return common | dict(anchor='generic-dyadic-H', routing_columns=columns,
                         word=[('quadratic_phase', -1, 'weight-all-bits'),
                               ('linear_route_inverse', columns),
                               ('H_tilde', r), ('linear_route', columns),
                               ('quadratic_phase', -1, 'weight-all-bits')])


def frame_matrix(E, n):
    """Integer coefficient matrix on grid 2^-dim(E); bounded n<=5."""
    if n > 5:
        raise ValueError('Use frame_spec for scalable operators; matrix audit is bounded at n5')
    spec = frame_spec(E, n); r = spec['rank']; size = 1 << n
    num = alpha_numerator(r)
    if spec['anchor'] == 'generic-dyadic-H':
        columns = spec['routing_columns']
        coordinates = {embed(value, columns): value for value in range(size)}
    result = [[(0, 0)] * size for _ in range(size)]
    for x in range(size):
        for y in range(size):
            kind = spec['anchor']
            if kind == 'identity':
                result[x][y] = (1, 0) if x == y else (0, 0)
            elif kind == 'full-C':
                result[x][y] = phase(num, -(x ^ y).bit_count())
            elif kind == 'odd-line-C':
                result[x][y] = (1, 1) if x == y else (1, -1) if x == y ^ spec['line'] else (0, 0)
            elif kind == 'odd-kernel-C':
                delta = x ^ y; label = spec['line']
                numerator = add(mul((1, -1), phase(alpha_numerator(n), -delta.bit_count())),
                                mul((1, 1), phase(alpha_numerator(n), -(delta ^ label).bit_count())))
                if any(value % 4 for value in numerator):
                    raise AssertionError('Odd kernel grid reduction failed')
                result[x][y] = numerator[0] // 4, numerator[1] // 4
            else:
                a, b = coordinates[x], coordinates[y]
                if a >> r == b >> r:
                    result[x][y] = phase(num, -x.bit_count() - y.bit_count()
                                         + 2 * dot(a & ((1 << r) - 1), b & ((1 << r) - 1)))
    return dict(spec=spec, numerator=result, denominator_bits=r)


def expected_lagrangian(E, n):
    return basis(perpendicular(E, n) + tuple(x | (x << n) for x in basis(E)))


def pauli_labels(frame):
    A = frame['numerator']; n = frame['spec']['n']; size = len(A)
    den = 1 << (2 * frame['denominator_bits'])
    labels = []
    for bit in range(n):
        image = [[(0, 0)] * size for _ in range(size)]
        for x in range(size):
            for y in range(size):
                value = (0, 0)
                for k in range(size):
                    term = mul(conj(A[k][x]), A[k][y])
                    value = add(value, phase(term, 2 if k >> bit & 1 else 0))
                image[x][y] = value
        support = [x for x in range(size) if image[x][0] != (0, 0)]
        if len(support) != 1:
            raise AssertionError('A frame is not a Clifford operator')
        xmask = support[0]
        phases = [j for j in range(4) if image[xmask][0] == (UNITS[j][0] * den, UNITS[j][1] * den)]
        if len(phases) != 1:
            raise AssertionError('Clifford Pauli global unit is not a fourth root')
        exponent = phases[0]; zmask = 0
        for j in range(n):
            if image[xmask ^ (1 << j)][1 << j] != image[xmask][0]:
                zmask |= 1 << j
        for x in range(size):
            for y in range(size):
                wanted = phase((den, 0), exponent + 2 * dot(zmask, y)) if x == y ^ xmask else (0, 0)
                if image[x][y] != wanted:
                    raise AssertionError('Literal Pauli image label/phase failed')
        labels.append(zmask | (xmask << n))
    return basis(labels)


def solve(rows, target):
    n = len(rows)
    work = [row | ((target >> j & 1) << n) for j, row in enumerate(rows)]
    for bit in range(n):
        pivot = next((j for j in range(bit, n) if work[j] >> bit & 1), None)
        if pivot is None:
            raise ValueError('Normal-form coupling is singular')
        work[bit], work[pivot] = work[pivot], work[bit]
        for j in range(n):
            if j != bit and work[j] >> bit & 1:
                work[j] ^= work[bit]
    return sum((work[j] >> n & 1) << j for j in range(n))


def quadratic_fit(values):
    n = (len(values) - 1).bit_length(); constant = values[0]
    linear = [(values[1 << j] - constant) % 4 for j in range(n)]
    cross = []
    for i in range(n):
        for j in range(i + 1, n):
            c = (values[(1 << i) | (1 << j)] - constant - linear[i] - linear[j]) % 4
            if c not in (0, 2):
                raise AssertionError('Normal-form gauge is not quadratic')
            if c:
                cross.append((i, j, c))
    for x, value in enumerate(values):
        wanted = (constant + sum(c for j, c in enumerate(linear) if x >> j & 1)
                  + sum(c for i, j, c in cross if x >> i & 1 and x >> j & 1)) % 4
        if value != wanted:
            raise AssertionError('A quadratic gauge does not describe every address')
    return dict(constant=constant, linear=linear, cross=cross)


def relative_matrix(E_frame, F_frame):
    A = E_frame['numerator']; B = F_frame['numerator']; size = len(A)
    e = E_frame['denominator_bits']; f = F_frame['denominator_bits']; delta = f - e
    if delta < 0:
        raise ValueError('This adapter requires nested increasing subspaces')
    divisor = 1 << (2 * e)
    result = [[(0, 0)] * size for _ in range(size)]
    for x in range(size):
        for y in range(size):
            value = (0, 0)
            for k in range(size):
                value = add(value, mul(B[x][k], conj(A[y][k])))
            if any(z % divisor for z in value):
                raise AssertionError('Nested relative operator has the wrong exact grid')
            result[x][y] = value[0] // divisor, value[1] // divisor
    return result, delta


def compile_matrix(A, n, rank):
    """Coefficient-based one-child normal form; no abstract free phases."""
    size = 1 << n; num = alpha_numerator(rank)
    def unit(x, y):
        matches = [j for j in range(4) if A[x][y] == phase(num, j)]
        if len(matches) != 1:
            raise AssertionError('Wrong child amplitude or nonunit normal-form gauge')
        return matches[0]
    support = [x for x in range(size) if A[x][0] != (0, 0)]
    if len(support) != 1 << rank:
        raise AssertionError('Relative mixing rank differs from the nested distance')
    offset = min(support)
    outputs = list(basis(x ^ offset for x in support))
    row_support = [y for y in range(size) if A[offset][y] != (0, 0)]
    inputs = list(complete_basis(basis(y ^ row_support[0] for y in row_support), n))
    for j in range(rank, n):
        outputs.append(min(x for x in range(size) if A[x][inputs[j]] != (0, 0)) ^ offset)
    if len(basis(outputs)) != n:
        raise AssertionError('Output spectator routing is incomplete')
    coupling = []
    for i in range(rank):
        row = 0
        for j in range(rank):
            exponent = (unit(offset ^ outputs[i], inputs[j]) + unit(offset, 0)
                        - unit(offset ^ outputs[i], 0) - unit(offset, inputs[j])) % 4
            if exponent not in (0, 2):
                raise AssertionError('Active bilinear coefficient is not binary')
            row |= (exponent // 2) << j
        coupling.append(row)
    inputs = [embed(solve(coupling, 1 << j), inputs[:rank]) for j in range(rank)] + inputs[rank:]
    out_address = [offset ^ embed(x, outputs) for x in range(size)]
    in_address = [embed(y, inputs) for y in range(size)]
    row_phase = [0] * size; col_phase = [0] * size
    for block in range(1 << (n - rank)):
        base = block << rank
        origin = unit(out_address[base], in_address[base])
        for a in range(1 << rank):
            row_phase[base + a] = (unit(out_address[base + a], in_address[base])
                                   + a.bit_count() - origin) % 4
        for b in range(1 << rank):
            col_phase[base + b] = (unit(out_address[base], in_address[base + b]) + b.bit_count()) % 4
    row_quadratic = quadratic_fit(row_phase); col_quadratic = quadratic_fit(col_phase)
    for x in range(size):
        for y in range(size):
            wanted = phase(num, row_phase[x] + col_phase[y]
                           - ((x ^ y) & ((1 << rank) - 1)).bit_count()) if x >> rank == y >> rank else (0, 0)
            if A[out_address[x]][in_address[y]] != wanted:
                raise AssertionError('Literal one-child normal form lost a matrix coefficient')
    return dict(selected_rank_per_column=rank, one_bulk_child_calls=int(rank > 0),
                output_affine_offset=offset, output_columns=outputs, input_columns=inputs,
                output_phase_exponents=row_phase, input_phase_exponents=col_phase,
                output_quadratic=row_quadratic, input_quadratic=col_quadratic,
                exact_matrix_entries_checked=size * size)


def compile_nested(E, F, n):
    E = basis(E); F = basis(F)
    if len(basis(E + F)) != len(F):
        raise ValueError('Nested interface requires E contained in F')
    A, delta = relative_matrix(frame_matrix(E, n), frame_matrix(F, n))
    return compile_matrix(A, n, delta)


def all_subspaces(n):
    seen = {()}; queue = [()]
    for E in queue:
        for x in range(1, 1 << n):
            candidate = basis(E + (x,))
            if candidate not in seen:
                seen.add(candidate); queue.append(candidate)
    return sorted(seen)


def probe(n):
    start = perf_counter(); spaces = all_subspaces(n)
    frames = {E: frame_matrix(E, n) for E in spaces}
    for E, frame in frames.items():
        if pauli_labels(frame) != expected_lagrangian(E, n):
            raise AssertionError(('Actual frame does not represent L_E', n, E))
    digest = sha256(); count = entries = degenerate = 0
    for E in spaces:
        for F in spaces:
            if len(basis(E + F)) != len(F):
                continue
            A, delta = relative_matrix(frames[E], frames[F])
            nf = compile_matrix(A, n, delta)
            count += 1; entries += nf['exact_matrix_entries_checked']
            degenerate += len(basis(E + perpendicular(E, n))) < n or len(basis(F + perpendicular(F, n))) < n
            digest.update(json.dumps([E, F, nf], separators=(',', ':')).encode())
    # Even-norm line C_T is a graph frame and cannot replace the vertical L_E.
    E = (3,); candidate = frames[E]['numerator']
    wrong = [[(1, 1) if x == y else (1, -1) if x == y ^ 3 else (0, 0)
              for y in range(1 << n)] for x in range(1 << n)]
    if candidate == wrong:
        raise AssertionError('Even-line false C_T shortcut was not rejected')
    sample = compile_nested((3,), (3, 4), n)
    return dict(n=n, subspaces=len(spaces), actual_inverse_Z_frames_checked=len(spaces),
                nested_interfaces=count, degenerate_endpoint_interfaces=degenerate,
                literal_normal_form_entries=entries, interface_sha256=digest.hexdigest(),
                even_line_C_shortcut_rejected=True, degenerate_sample=sample,
                seconds=perf_counter() - start)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--bounded', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError('Use one to four workers')
    args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__); source_hash = sha256(source.read_bytes()).hexdigest()
    started_utc = datetime.now(timezone.utc).isoformat(); start = perf_counter()
    sizes = (3,) if args.bounded else (3, 4)
    protocol = dict(started_utc=started_utc, workers=args.workers, native_threads_each=1,
                    source_sha256=source_hash, dependencies='Python standard library only',
                    cases=sizes, seeds=None,
                    hypothesis='One fixed actual Gaussian F_E realizes every L_E and nested transitions have exactly one dim-difference child with paid affine/quadratic wrappers.')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(probe, sizes))
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('Effective frame source changed during execution')
    certificate = dict(status='PASS EXACT CANONICAL SUBSPACE FRAMES', started_utc=started_utc,
                       completed_utc=datetime.now(timezone.utc).isoformat(),
                       elapsed_seconds=perf_counter() - start, cases=results,
                       scope='Scalable literal frame definitions and exhaustive finite coefficient/phase controls. Native fixed-tape normal-form synthesis, complete side/master chronology, helper volume and exponent remain separate.')
    (args.output / 'certificate.json').write_text(json.dumps(certificate, indent=2) + '\n')
    print(json.dumps({k: certificate[k] for k in ('status', 'started_utc', 'completed_utc', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
