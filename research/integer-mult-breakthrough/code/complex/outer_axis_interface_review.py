#!/usr/bin/env python3
"""Independent integer-Fourier review of the odd-label two-axis splice.

No synthesis producer is imported. Exact integer FWHT kernels bind the small
operators; orthogonal quadratic Gauss elimination checks the closed unit at
larger dimensions. Per-column ranks are distinct from bulk tensor dimensions.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter


UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def sub(x, y):
    return x[0] - y[0], x[1] - y[1]


def mul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def phase(x, exponent):
    return mul(x, UNITS[exponent % 4])


def dot(x, y):
    return (x & y).bit_count() % 2


def embed(x, columns):
    value = 0
    for j, column in enumerate(columns):
        if x >> j & 1:
            value ^= column
    return value


def basis(vectors):
    pivots = {}
    for value in vectors:
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


def perpendicular(label, h):
    if not 0 < label < 1 << h or label.bit_count() % 2 != 1:
        raise ValueError('Both labels must have odd norm')
    anchor = (label & -label).bit_length() - 1
    return tuple((1 << j) ^ ((1 << anchor) if label >> j & 1 else 0)
                 for j in range(h) if j != anchor)


def tensor(s, t, h):
    return sum(((s >> i) & 1) * t << (i * h) for i in range(h))


def solve(rows, target):
    n = len(rows)
    work = [row | ((target >> i & 1) << n) for i, row in enumerate(rows)]
    for bit in range(n):
        pivot = next((i for i in range(bit, n) if work[i] >> bit & 1), None)
        if pivot is None:
            raise ValueError('A required GF2 routing matrix is singular')
        work[bit], work[pivot] = work[pivot], work[bit]
        for i in range(n):
            if i != bit and work[i] >> bit & 1:
                work[i] ^= work[bit]
    return sum((work[i] >> n & 1) << i for i in range(n))


def alpha_numerator(rank):
    result = (1, 0)
    for _ in range(rank):
        result = mul(result, (1, 1))
    return result


def gauss_weight(columns):
    """Sum i^weight(v) over a nondegenerate binary subspace, without enumeration.

    Split odd one-dimensional lines when possible. A remaining alternating
    form splits into nondegenerate two-dimensional planes. Every basis change
    is literal XOR on the original bit vectors, so quadratic values are
    obtained independently from their exact weights.
    """
    work = list(columns)
    result = (1, 0)
    blocks = []
    while work:
        odd = next((j for j, x in enumerate(work) if dot(x, x)), None)
        if odd is not None:
            u = work.pop(odd)
            work = [x ^ (u if dot(x, u) else 0) for x in work]
            q = u.bit_count() % 4
            result = mul(result, add((1, 0), UNITS[q]))
            blocks.append(('odd-line', q))
            continue
        u = work.pop()
        partner = next((j for j, x in enumerate(work) if dot(u, x)), None)
        if partner is None:
            raise ValueError('Alternating quadratic block is degenerate')
        v = work.pop(partner)
        work = [x ^ (u if dot(x, v) else 0) ^ (v if dot(x, u) else 0) for x in work]
        plane = (0, 0)
        for x in (0, u, v, u ^ v):
            plane = add(plane, UNITS[x.bit_count() % 4])
        if plane not in ((2, 0), (-2, 0)):
            raise AssertionError('A nondegenerate alternating plane has an invalid Gauss factor')
        result = mul(result, plane)
        blocks.append(('alternating-plane', u.bit_count() % 4, v.bit_count() % 4,
                       1 if plane[0] > 0 else -1))
    return result, blocks


def specification(h, s, t):
    S = perpendicular(s, h)
    T = perpendicular(t, h)
    n = h * h
    Es = tuple(tensor(s, 1 << j, h) for j in range(h))
    Et = tuple(tensor(1 << j, t, h) for j in range(h))
    u = tensor(s, t, h)
    V = tuple(tensor(a, b, h) for a in S for b in T)
    R = basis(Es + Et)
    ell_s = (s.bit_count() - 1) // 2 % 2
    ell_t = (t.bit_count() - 1) // 2 % 2
    ones = (1 << h) - 1
    offset = ((tensor(s, ones ^ t, h) if ell_s else 0)
              ^ (tensor(ones ^ s, t, h) if ell_t else 0))
    unit = ((h - 1) * (ell_s + ell_t) + 2 * ell_s * ell_t) % 4
    return dict(h=h, s=s, t=t, n=n, S=S, T=T, Es=Es, Et=Et, u=u, V=V, R=R,
                ell_s=ell_s, ell_t=ell_t, offset=offset, unit=unit)


def spectral_phase(z, spec, phi=False):
    value = z.bit_count() - sum(dot(z, x) for x in spec['Et'])
    if not phi:
        value += dot(z, spec['u']) - sum(dot(z, x) for x in spec['Es'])
    return value % 4


def algebra_probe(h, s, t):
    spec = specification(h, s, t)
    n = spec['n']; V = spec['V']; R = spec['R']
    r = (h - 1) ** 2
    if len(basis(V)) != r or len(R) != 2 * h - 1 or len(basis(V + R)) != n:
        raise AssertionError('Odd-label direct-sum dimensions failed')
    if any(dot(a, b) for a in V for b in R):
        raise AssertionError('Joint complement and radical are not orthogonal')
    def P(z, directions):
        value = 0
        for x in directions:
            if dot(z, x):
                value ^= x
        return value
    def A(z):
        return z ^ P(z, spec['Es']) ^ P(z, spec['Et']) ^ (spec['u'] if dot(z, spec['u']) else 0)
    columns = tuple(A(1 << j) for j in range(n))
    if basis(columns) != basis(V) or any(A(A(x)) != A(x) for x in (1 << j for j in range(n))):
        raise AssertionError('Polar image/projector identity failed')
    for x in R:
        if spectral_phase(x, spec) != 2 * dot(spec['offset'], x):
            raise AssertionError('Canonical radical character/affine support failed')
    if any(dot(spec['offset'], x) for x in V):
        raise AssertionError('Canonical affine offset is not in the radical')
    for x in V:
        if spectral_phase(x, spec) != x.bit_count() % 4:
            raise AssertionError('Restricted active quadratic lift changed')
    actual_gauss, blocks = gauss_weight(V)
    predicted_gauss = phase(alpha_numerator(r), spec['unit'])
    if actual_gauss != predicted_gauss:
        raise AssertionError(('Closed tensor Gauss unit failed', h, s, t, actual_gauss, predicted_gauss))
    # Omitting C_u changes the polar image by the independent unit line.
    wrong_columns = tuple(x ^ (spec['u'] if dot(1 << j, spec['u']) else 0)
                          for j, x in enumerate(columns))
    if len(basis(wrong_columns)) != r + 1:
        raise AssertionError('Omitted line correction failed to increase relative rank')
    return spec, dict(h=h, s=s, t=t, source_sink_relative_rank=r,
                      radical_dimension=len(R), canonical_affine_offset=spec['offset'],
                      global_i_exponent_per_column=spec['unit'],
                      actual_gauss_numerator=list(actual_gauss), gauss_grid_denominator_bits=r,
                      orthogonal_gauss_blocks=blocks, omitted_line_rank=r + 1,
                      spectator_phi_rank=n - h,
                      spectator_phi_offset=tensor((1 << h) - 1, t, h) if spec['ell_t'] else 0,
                      spectator_phi_global_i_exponent=(h * spec['ell_t']) % 4)


def fwht(values):
    out = list(values)
    stride = 1
    while stride < len(out):
        for start in range(0, len(out), 2 * stride):
            for j in range(start, start + stride):
                left, right = out[j], out[j + stride]
                out[j], out[j + stride] = add(left, right), sub(left, right)
        stride *= 2
    return out


def kernel_probe(spec, phi=False):
    h = spec['h']; n = spec['n']
    # Integer inverse Fourier numerators on the complete grid 2^-n.
    actual = fwht([UNITS[spectral_phase(z, spec, phi)] for z in range(1 << n)])
    if phi:
        V = tuple(tensor(1 << i, b, h) for i in range(h) for b in spec['T'])
        offset = tensor((1 << h) - 1, spec['t'], h) if spec['ell_t'] else 0
        unit = h * spec['ell_t'] % 4
    else:
        V = spec['V']; offset = spec['offset']; unit = spec['unit']
    r = len(V)
    base = phase(alpha_numerator(r), unit)
    expected = {}
    for index in range(1 << r):
        x = embed(index, V)
        value = phase(base, -x.bit_count())
        expected[offset ^ x] = (value[0] << (n - r), value[1] << (n - r))
    if any(z != expected.get(index, (0, 0)) for index, z in enumerate(actual)):
        raise AssertionError('Independent full integer-Fourier kernel differs from its closed form')
    digest = sha256(json.dumps(actual, separators=(',', ':')).encode()).hexdigest()
    # This complete convolution origin determines every physical address
    # column by exact XOR covariance; no giant matrix is serialized.
    entries = 0
    if not phi:
        gram = [sum(dot(a, b) << j for j, b in enumerate(V)) for a in V]
        dual = tuple(embed(solve(gram, 1 << j), V) for j in range(r))
        if any(dot(a, b) != int(i == j) for i, a in enumerate(V) for j, b in enumerate(dual)):
            raise AssertionError('Independent active input/output coordinates are not dot-dual')
        out_values = [embed(a, V) for a in range(1 << r)]
        in_values = [embed(b, dual) for b in range(1 << r)]
        num = alpha_numerator(r)
        for a, da in enumerate(out_values):
            for b, db in enumerate(in_values):
                chirp = (spec['unit'] - (da.bit_count() - a.bit_count())
                         - (db.bit_count() - b.bit_count()))
                coefficient = phase(num, -(a ^ b).bit_count() + chirp)
                coefficient = (coefficient[0] << (n - r), coefficient[1] << (n - r))
                if coefficient != actual[offset ^ da ^ db]:
                    raise AssertionError('Paid one-child dual-coordinate normal form failed')
                entries += 1
        wrong_offset_detected = offset != 0 and any(actual[index] != expected.get(index ^ offset, (0, 0))
                                                  for index in range(1 << n))
        wrong_unit_detected = unit != 0 and any(z != phase(z, -unit) for z in actual)
        if offset and not wrong_offset_detected or unit and not wrong_unit_detected:
            raise AssertionError('Affine or global-unit negative control failed')
    else:
        wrong_offset_detected = wrong_unit_detected = None
    return dict(operator='Phi_t' if phi else 'M', n=n, relative_rank_per_column=r,
                complete_kernel_coefficients=len(actual), explicitly_rebuilt_active_matrix_entries=entries,
                complete_physical_matrix_entries_determined_by_covariance=1 << (2 * n),
                affine_offset=offset, global_i_exponent_per_column=unit,
                kernel_numerators_sha256=digest,
                omitted_offset_detected=wrong_offset_detected,
                omitted_global_unit_detected=wrong_unit_detected)


def worker(case):
    h, s, t, kernels = case
    start = perf_counter()
    spec, result = algebra_probe(h, s, t)
    if kernels:
        result['exact_fourier_kernels'] = [kernel_probe(spec), kernel_probe(spec, True)]
    result['seconds'] = perf_counter() - start
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError('Use one to four workers')
    args.output.mkdir(parents=True, exist_ok=False)
    started_utc = datetime.now(timezone.utc).isoformat(); start = perf_counter()
    cases = [(3, s, t, True) for s in (1, 7) for t in (1, 7)]
    if not args.bounded:
        cases += [(4, 1, 1, True), (4, 1, 7, True), (4, 11, 1, True), (4, 7, 11, True)]
        cases += [(h, s, t, False) for h in (7, 10, 16, 24)
                  for s, t in ((1, 1), (7, 1), (31, 127), (127, 31))]
    source = Path(__file__); source_hash = sha256(source.read_bytes()).hexdigest()
    protocol = dict(started_utc=started_utc, cases=cases, workers=args.workers,
                    native_threads_each=1, source_sha256=source_hash, seeds=None,
                    dependencies='Python standard library only; no producer imports',
                    reference_producer='code/synthesis/outer_axis_frame_splice.py; independently inspected',
                    question='Bind the all-h projection, affine support and closed Gauss unit to exact small Fourier kernels and larger quadratic elimination.')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(worker, cases))
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('Review source changed during execution')
    certificate = dict(status='PASS INDEPENDENT EXACT TWO-AXIS PHASE INTERFACE',
                       started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                       elapsed_seconds=perf_counter() - start, cases=results,
                       scope='All-h algebraic phase and rank argument with exact finite controls. Native routing/chirps/guards, whole arbitrary-dirty master chronology, role stock and multiplier exponent are not certified.')
    (args.output / 'certificate.json').write_text(json.dumps(certificate, indent=2) + '\n')
    print(json.dumps({k: certificate[k] for k in ('status', 'started_utc', 'completed_utc', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
