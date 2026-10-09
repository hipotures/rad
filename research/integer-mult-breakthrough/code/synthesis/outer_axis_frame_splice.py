#!/usr/bin/env python3
"""Exact Gaussian interfaces between two odd-label tensor-axis components.

This checks actual convolution operators and their paid affine/chirp normal
forms. It does not compose the virtual center maps into an identity, supply
a complete auxiliary chronology, or inherit an earlier master histogram.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

from lagrangian_graph_completion import basis, image, solve

ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))
ALPHA = (Q(1, 2), Q(1, 2))
BETA = (Q(1, 2), Q(-1, 2))
UNITS = (ONE, (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1)))


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def div(a, b):
    norm = b[0] * b[0] + b[1] * b[1]
    if not norm:
        raise ValueError('Division by a zero Gaussian coefficient')
    z = mul(a, (b[0], -b[1]))
    return z[0] / norm, z[1] / norm


def power(a, n):
    z = ONE
    for _ in range(n):
        z = mul(z, a)
    return z


def dot(a, b):
    return (a & b).bit_count() % 2


def apply_line(values, direction, inverse=False):
    out = list(values)
    lo, hi = (BETA, ALPHA) if inverse else (ALPHA, BETA)
    for a in range(len(out)):
        b = a ^ direction
        if a >= b:
            continue
        x, y = out[a], out[b]
        out[a], out[b] = add(mul(lo, x), mul(hi, y)), add(mul(hi, x), mul(lo, y))
    return out


def convolution_frame(n, directions, inverse=False, initial=None):
    # C_direction=alpha*I+beta*X_direction; every inverse is beta*I+alpha*X.
    out = [ONE] + [ZERO] * ((1 << n) - 1) if initial is None else list(initial)
    for direction in directions:
        out = apply_line(out, direction, inverse)
    return out


def tensor_direction(s, t, h):
    return sum(((s >> i) & 1) * ((t >> j) & 1) << (i * h + j)
               for i in range(h) for j in range(h))


def perp(rows, n):
    # Bounded checker only; the proof uses exact nullspace elimination.
    return basis((a for a in range(1 << n) if all(dot(a, b) == 0 for b in rows)), n)


def unit_id(z):
    if z not in UNITS:
        raise ValueError('An alleged paid fourth-root chirp is not a Gaussian unit')
    return UNITS.index(z)


def normal_form(kernel, V, n, check_all_matrix=True):
    """One C_rank child, affine XOR routing and explicit fourth-root scans.

    The support V must be nondegenerate, but it may be alternating. Different
    input/output dot-dual coordinates avoid an orthonormal-basis assumption.
    """
    r = len(V)
    support = [a for a, z in enumerate(kernel) if z != ZERO]
    if not support:
        raise ValueError('An invertible relative frame has empty kernel')
    offset = support[0]
    expected_support = sorted(offset ^ image(V, a) for a in range(1 << r))
    if support != expected_support:
        raise ValueError('Actual Gaussian convolution lacks the declared affine support')
    gram = tuple(sum(dot(a, b) << i for i, a in enumerate(V)) for b in V)
    dual = tuple(image(V, solve(gram, 1 << j)) for j in range(r))
    if any(dot(a, b) != int(i == j) for i, a in enumerate(V) for j, b in enumerate(dual)):
        raise ValueError('Input and output address columns are not dot-dual')
    spectator = perp(V, n)
    if len(spectator) != n - r or len(basis(V + spectator, n)) != n:
        raise ValueError('Spectator routing lost the complete address cube')
    child = convolution_frame(r, tuple(1 << j for j in range(r)))
    row = [div(kernel[offset ^ image(V, a)], child[a]) for a in range(1 << r)]
    col = [div(kernel[offset ^ image(dual, b)], mul(row[0], child[b]))
           for b in range(1 << r)]
    row_ids, col_ids = [unit_id(z) for z in row], [unit_id(z) for z in col]
    for a in range(1 << r):
        for b in range(1 << r):
            actual = kernel[offset ^ image(V, a) ^ image(dual, b)]
            rebuilt = mul(mul(row[a], child[a ^ b]), col[b])
            if actual != rebuilt:
                raise ValueError('One-child affine/chirp normal form is incorrect')
    entries = 0
    digest = sha256()
    if check_all_matrix:
        out_columns, in_columns = V + spectator, dual + spectator
        out_coords = [solve(out_columns, a ^ offset) for a in range(1 << n)]
        in_coords = [solve(in_columns, b) for b in range(1 << n)]
        low = (1 << r) - 1
        for a in range(1 << n):
            aa = out_coords[a]
            for b in range(1 << n):
                bb = in_coords[b]
                rebuilt = (mul(mul(row[aa & low], child[(aa ^ bb) & low]), col[bb & low])
                           if aa >> r == bb >> r else ZERO)
                if kernel[a ^ b] != rebuilt:
                    raise ValueError('Spectator/affine normal form failed on a physical matrix entry')
                entries += 1
            digest.update(json.dumps([[str(z[0]), str(z[1])] for z in
                                      (kernel[a ^ b] for b in range(1 << n))],
                                     separators=(',', ':')).encode())
    return dict(child_width=r, physical_address_bits=n, affine_output_xor=offset,
                output_columns=V + spectator, input_columns=dual + spectator,
                output_fourth_root_exponents=row_ids, input_fourth_root_exponents=col_ids,
                child_entries_checked=1 << (2 * r), all_physical_matrix_entries_checked=entries,
                full_matrix_sha256=digest.hexdigest() if check_all_matrix else None,
                alternating_support=all(dot(a, a) == 0 for a in V),
                native_obligations=['Paid input/output GF2 address routing',
                                    'Paid affine XOR of every selected column',
                                    'Paid per-column fourth-root row/column chirps',
                                    'Preserve all spectator coordinates and payload fields'])


def probe(case):
    h, s, t = case
    start = time.monotonic()
    if not (s.bit_count() % 2 == t.bit_count() % 2 == 1):
        raise ValueError('Odd outer and inner labels required')
    n = h * h
    full = tuple(1 << j for j in range(n))
    Es = tuple(tensor_direction(s, 1 << j, h) for j in range(h))
    Et = tuple(tensor_direction(1 << i, t, h) for i in range(h))
    u = tensor_direction(s, t, h)
    if any(dot(a, b) != int(i == j) for i, a in enumerate(Es) for j, b in enumerate(Es)):
        raise ValueError('Outer label subspace is not an isometric h-bit embedding')
    if any(dot(a, b) != int(i == j) for i, a in enumerate(Et) for j, b in enumerate(Et)):
        raise ValueError('Second-axis label subspace is not an isometric h-bit embedding')
    # A first-axis source ends C_Es. Its second-axis source starts Phi_t*C_u.
    # A first-axis sink ends C_Es*C_u^-1. Its second-axis sink starts Phi_t.
    # Therefore the exact relative operator on BOTH broad families is M.
    phi = convolution_frame(n, Et, True, convolution_frame(n, full))
    source = convolution_frame(n, Es, True, apply_line(phi, u))
    sink = apply_line(convolution_frame(n, Es, True, phi), u)
    if source != sink:
        raise ValueError('Two broad source/sink relative Gaussian operators differ')
    V = perp(Es + Et, n)
    if len(V) != (h - 1) ** 2:
        raise ValueError('The two-axis residual rank is incorrect')
    residual = normal_form(source, V, n)
    complement = normal_form(phi, perp(Et, n), n, False)
    # Independently recover the polar map I+P+Q+R from the Z4 spectral phase.
    def phase(z):
        return (z.bit_count() - sum(dot(z, a) for a in Es)
                - sum(dot(z, a) for a in Et) + dot(z, u)) % 4
    polar = []
    for j in range(n):
        e = 1 << j
        column = e
        for a in Es + Et + (u,):
            if dot(e, a):
                column ^= a
        for i in range(n):
            value = (phase(e ^ (1 << i)) - phase(e) - phase(1 << i)) % 4
            if value != 2 * dot(column, 1 << i):
                raise ValueError('Gaussian spectral phase has the wrong polar matrix')
        polar.append(column)
    if basis(polar, n) != V:
        raise ValueError('The actual relative polar image is not the joint complement')
    # Losing the single line term changes the complete physical kernel.
    wrong = convolution_frame(n, Es, True, phi)
    if wrong == source:
        raise ValueError('Omitted line inverse/correction was not discriminating')
    return dict(status='EXACT TWO-AXIS GAUSSIAN INTERFACE PASS', h=h,
                first_label=s, second_label=t, first_label_weight=s.bit_count(),
                second_label_weight=t.bit_count(), active_line=u,
                first_axis_columns=Es, second_axis_columns=Et,
                broad_source_sink_operators_equal=True,
                relative_phase_formula='wt(z)-sum_j parity(s*z_col_j)-sum_i parity(t*z_row_i)+parity(s^T*z*t) mod4',
                relative_polar_rank=len(V), broad_interface=residual,
                spectator_prepost_interface=complement,
                omitted_line_correction_detected=True, seconds=time.monotonic() - start,
                scope='Actual finite Gaussian convolution and one-child affine/chirp routing on every physical address coefficient. The virtual two-axis center composition, arbitrary-dirty whole word, master child multiplicities, fixed-tape implementation and exponent remain open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('Positive worker count required')
    args.output.mkdir(parents=True, exist_ok=False)
    sources = (Path(__file__), Path(__file__).with_name('lagrangian_graph_completion.py'))
    hashes = {p: sha256(p.read_bytes()).hexdigest() for p in sources}
    cases = [(3, 1, 1), (3, 1, 7), (3, 7, 1), (3, 7, 7)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, cases=cases, seed=None,
                    source_sha256={p.name: value for p, value in hashes.items()},
                    question='Does the exact two-axis splice have rank (h-1)^2 with all phase and spectator obligations retained?')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    receipts = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(probe, case): case for case in cases}
        for future in as_completed(futures):
            result = future.result(); receipts.append(result)
            print(json.dumps({key: result[key] for key in ('status', 'h', 'first_label', 'second_label', 'seconds')}
                             | {'relative_rank': result['relative_polar_rank'],
                                'affine_offset': result['broad_interface']['affine_output_xor']}), flush=True)
    if any(sha256(p.read_bytes()).hexdigest() != value for p, value in hashes.items()):
        raise ValueError('An effective source changed during the experiment')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=receipts), indent=2) + '\n')


if __name__ == '__main__':
    main()
