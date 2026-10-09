#!/usr/bin/env python3
"""Exact scoped routed-edge obstruction for nonlinear matching conjugacies.

Complete weighted monomial alignment forces F*A_T^-1*P*A_U^-1 to be
F times a monomial. This excludes one smaller uniform C child with
monomial/diagonal wrappers, not general matching or multi-child circuits.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from random import Random
import time

import conditioned_frame_review as g

TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC / 'configs/transfers/coherent-matching-routing.json'
ALPHA, BETA = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))


def scale(value, coefficient):
    return value[0] * coefficient, value[1] * coefficient


def monomial(table, weights):
    size = len(table)
    if sorted(table) != list(range(size)) or any(w == g.ZERO for w in weights):
        raise ValueError('A complete invertible weighted monomial is required')
    matrix = [[g.ZERO] * size for _ in range(size)]
    for source, target in enumerate(table):
        matrix[target][source] = weights[source]
    return matrix


def inverse_monomial(table, weights):
    size = len(table)
    inverse, scalars = [0] * size, [None] * size
    for source, target in enumerate(table):
        inverse[target] = source
        scalars[target] = g.power(weights[source], -1)
    return monomial(inverse, scalars)


def matching_frame(matching, inverse=False):
    first, second = (g.conjugate(ALPHA), g.conjugate(BETA)) if inverse else (ALPHA, BETA)
    size = len(matching)
    return [[g.add(first if row == column else g.ZERO,
                   g.multiply(second, matching[row][column]))
             for column in range(size)] for row in range(size)]


def full_matrix(h):
    alpha = g.power(ALPHA, h)
    return [[g.multiply(alpha, g.power(g.IMAGINARY, -(a ^ b).bit_count()))
             for b in range(1 << h)] for a in range(1 << h)]


def is_affine(table, h):
    offset = table[0]
    columns = [table[1 << j] ^ offset for j in range(h)]
    for address in range(1 << h):
        image = offset
        for j in range(h):
            if address >> j & 1:
                image ^= columns[j]
        if image != table[address]:
            return False
    return True


def apply_columns(values, matrix, h, columns):
    local_size = 1 << h
    data = list(values)
    for column in range(columns):
        out = [g.ZERO] * len(data)
        shift = h * column
        for address, value in enumerate(data):
            if value == g.ZERO:
                continue
            old = (address >> shift) & (local_size - 1)
            base = address ^ (old << shift)
            for new in range(local_size):
                if matrix[new][old] != g.ZERO:
                    index = base | (new << shift)
                    out[index] = g.add(out[index], g.multiply(matrix[new][old], value))
        data = out
    return data


def probe(case):
    started = time.monotonic()
    h, columns, weighted, reverse, seed = [case[k] for k in ('h', 'columns', 'weighted', 'inverse_conjugacy', 'seed')]
    size = 1 << h
    randoms = Random(seed)
    pairs = list(range(size))
    randoms.shuffle(pairs)
    match = [0] * size
    for a, b in zip(pairs[::2], pairs[1::2]):
        match[a], match[b] = b, a
    if any(match[match[a]] != a or match[a] == a for a in range(size)):
        raise ValueError('The source matching is not a fixed-point-free involution')
    table = [a ^ (int(a >> 1 & 1 and a >> 2 & 1)) for a in range(size)]
    if is_affine(table, h):
        raise ValueError('The named Toffoli router unexpectedly became affine')
    phases = [randoms.randrange(4) for _ in range(size)]
    exponents = [randoms.randrange(-2, 3) if weighted else 0 for _ in range(size)]
    weights = [scale(g.power(g.IMAGINARY, phase), Q(2) ** exponent)
               for phase, exponent in zip(phases, exponents)]
    m_u = monomial(match, [g.ONE] * size)
    p, p_inverse = monomial(table, weights), inverse_monomial(table, weights)
    a_u, a_u_inverse = matching_frame(m_u), matching_frame(m_u, True)
    if g.matmul(a_u, a_u) != m_u or g.matmul(a_u, a_u_inverse) != g.identity(size):
        raise ValueError('Literal matching square or inverse identity failed')
    a_t = g.matmul(g.matmul(p, a_u_inverse if reverse else a_u), p_inverse)
    a_t_inverse = g.matmul(g.matmul(p, a_u if reverse else a_u_inverse), p_inverse)
    f = full_matrix(h)
    actual = g.matmul(g.matmul(g.matmul(f, a_t_inverse), p), a_u_inverse)
    expected_monomial = p if reverse else g.matmul(p, m_u)
    expected = g.matmul(f, expected_monomial)
    if actual != expected:
        raise ValueError('The full routed matching-conjugacy identity failed')
    omitted_source = g.matmul(g.matmul(f, a_t_inverse), p)
    if omitted_source == actual:
        raise ValueError('Omitted source-anchor correction did not discriminate')
    count = 1 << (h * columns)
    digest, complete_coefficients = sha256(), 0
    for address in range(count):
        values = [g.ZERO] * count
        values[address] = g.ONE
        current = values
        for local in (a_u_inverse, p, a_t_inverse, f):
            current = apply_columns(current, local, h, columns)
        target, weight = 0, g.ONE
        for column in range(columns):
            local = (address >> (h * column)) & (size - 1)
            if not reverse:
                local = match[local]
            target |= table[local] << (h * column)
            weight = g.multiply(weight, weights[local])
        direct_alpha = g.multiply(weight, g.power(ALPHA, h * columns))
        direct = [g.multiply(direct_alpha, g.power(g.IMAGINARY, -(a ^ target).bit_count()))
                  for a in range(count)]
        if current != direct or any(value == g.ZERO for value in current):
            raise ValueError('Complete grouped literal coefficients or full support failed')
        complete_coefficients += count
        digest.update(str(current).encode())
    for field in range(4):
        values = [(Q((i * 7 + field * 3) % 19 - 9, 8),
                   Q((i * 13 + field * 5) % 23 - 11, 8)) for i in range(count)]
        current = values
        for local in (a_u_inverse, p, a_t_inverse, f):
            current = apply_columns(current, local, h, columns)
        wanted = apply_columns(apply_columns(values, expected_monomial, h, columns), f, h, columns)
        if current != wanted:
            raise ValueError('Complete arbitrary Gaussian dirty field failed')
        returned = current
        for local in (g.adjoint(f), a_t, p_inverse, a_u):
            returned = apply_columns(returned, local, h, columns)
        if returned != values:
            raise ValueError('Literal inverse failed to return complete dirty fields')
        digest.update(str(current).encode())
    # Dropping the aligning router is a genuinely different interface. Two
    # distinct coordinate matchings then admit the old smaller support.
    m0 = monomial([a ^ 1 for a in range(size)], [g.ONE] * size)
    m1 = monomial([a ^ 2 for a in range(size)], [g.ONE] * size)
    unrouted = g.matmul(g.matmul(f, matching_frame(m1, True)), matching_frame(m0, True))
    unrouted_support = [sum(value != g.ZERO for value in row) for row in unrouted]
    if set(unrouted_support) != {1 << (h - 2)}:
        raise ValueError('The independent unaligned two-coordinate control failed')
    return dict(h=h, columns=columns, weighted=weighted, inverse_conjugacy=reverse,
                seed=seed, source_matching=match, nonlinear_route=table,
                route_weight_binary_exponents=exponents, route_weight_phase_exponents=phases,
                complete_grouped_input_columns=count, complete_literal_coefficients=complete_coefficients,
                arbitrary_dirty_gaussian_fields=4, complete_support_per_row_and_column=count,
                minimum_single_uniform_child_selected_width=h,
                nonzero_diagonal_wrappers_cannot_reduce_support=True,
                omitted_source_anchor_detected=True,
                unaligned_control_support_per_row=unrouted_support[0],
                output_sha256=digest.hexdigest(), seconds=time.monotonic()-started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or (args.output and args.output.exists()):
        raise ValueError('Positive workers and a fresh output path are required')
    config = json.loads(CONFIG.read_text())
    helper = Path(g.__file__).resolve()
    if sha256(helper.read_bytes()).hexdigest() != config['independent_gaussian_helper_sha256']:
        raise ValueError('Frozen independent Gaussian helper changed')
    pins = {str(p.relative_to(TOPIC)): sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__).resolve(), CONFIG, helper)}
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    source_config_sha256=pins, producer_imports=False, scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    cases = config['cases'][:1] if args.small else config['cases']
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest() != value for p, value in pins.items()):
        raise ValueError('Source changed during immutable attempt')
    summary = dict(status='EXACT NONLINEAR WEIGHTED CONJUGACY ROUTE BOUNDARY PASS',
                   cases=rows, seconds=time.monotonic()-started, scope=config['scope'],
                   complete_native_primitive=False, new_exponent=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k: summary[k] for k in ('status', 'seconds', 'scope')}))


if __name__ == '__main__':
    main()
