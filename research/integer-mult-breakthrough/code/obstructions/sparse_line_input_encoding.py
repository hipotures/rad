#!/usr/bin/env python3
"""Exact sparse-transversal line preparation and its input-volume boundary.

Copying in a declared orbit-major layout is separate from a native layout
conversion. Arbitrary dense inputs and dirty auxiliary banks are not supplied
by this restricted interface. No new multiplication exponent is claimed.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time


def multiply(x, y):
    a, b = x
    c, d = y
    return a * c - b * d, a * d + b * c


def rotate(x, exponent):
    a, b = x
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def kernel(values, mask, inverse=False):
    out = list(values)
    alpha, beta = ((1, -1), (1, 1)) if inverse else ((1, 1), (1, -1))
    for address in range(len(out)):
        partner = address ^ mask
        if address < partner:
            x, y = values[address], values[partner]
            ax, by = multiply(alpha, x), multiply(beta, y)
            bx, ay = multiply(beta, x), multiply(alpha, y)
            out[address] = ax[0] + by[0], ax[1] + by[1]
            out[partner] = bx[0] + ay[0], bx[1] + ay[1]
    return out


def line(values, label, h, columns, inverse=False):
    out = list(values)
    for column in range(columns):
        mask = sum(((label >> row) & 1) << (row * columns + column)
                   for row in range(h))
        out = kernel(out, mask, inverse)
    return out


def full(values, bits):
    out = list(values)
    for bit in range(bits):
        out = kernel(out, 1 << bit)
    return out


def copy_formula(values, label, h, columns, omit_phase=False):
    """Numerators on denominator 2**columns; retain the declared layout cost."""
    pivot = (label & -label).bit_length() - 1
    factor = (1, 0)
    for unused in range(columns):
        factor = multiply(factor, (1, 1))
    out = []
    for address in range(len(values)):
        representative = address
        selected_weight = 0
        for column in range(columns):
            if (address >> (pivot * columns + column)) & 1:
                selected_weight += 1
                representative ^= sum(((label >> row) & 1) << (row * columns + column)
                                      for row in range(h))
        value = multiply(factor, values[representative])
        out.append(value if omit_phase else rotate(value, -selected_weight))
    return out


def probe(case):
    started = time.monotonic()
    h, columns, label = case
    if not 0 < label < 1 << h:
        raise ValueError('A nonzero label inside the ambient cube is required')
    size = 1 << (h * columns)
    pivot = (label & -label).bit_length() - 1
    pivot_mask = ((1 << columns) - 1) << (pivot * columns)
    representatives = [a for a in range(size) if not a & pivot_mask]
    digest = sha256()
    fields = []
    for representative in representatives:
        fields.append([(int(a == representative), 0) for a in range(size)])
    for seed in range(3):
        fields.append([((a * 7 + seed * 3) % 19 - 9, (a * 11 + seed * 5) % 23 - 11)
                       if a in representatives else (0, 0) for a in range(size)])
    for values in fields:
        prepared = copy_formula(values, label, h, columns)
        if prepared != line(values, label, h, columns):
            raise AssertionError('The complete Gaussian copy/phase formula failed')
        returned = line(prepared, label, h, columns, True)
        if returned != [(a << (2 * columns), b << (2 * columns)) for a, b in values]:
            raise AssertionError('The restricted encoding inverse changed its input')
        physical = full(returned, h * columns)
        expected = [(a << (2 * columns), b << (2 * columns))
                    for a, b in full(values, h * columns)]
        if physical != expected:
            raise AssertionError('The partial frame with restricted preencoding is not full C')
        digest.update(str(prepared).encode())
    phase_control = copy_formula(fields[-1], label, h, columns, True) != line(fields[-1], label, h, columns)
    outside = pivot_mask & -pivot_mask
    dense_input = [(int(a == outside), 0) for a in range(size)]
    domain_control = copy_formula(dense_input, label, h, columns) != line(dense_input, label, h, columns)
    if not phase_control or not domain_control:
        raise AssertionError('A phase or out-of-domain input control did not discriminate')
    return dict(status='PASS RESTRICTED SPARSE ENCODING', h=h, columns=columns,
                label=label, complete_sparse_basis_columns=len(representatives),
                complete_basis_coefficients=size * len(representatives),
                arbitrary_gaussian_fields=3, address_volume=size,
                arbitrary_input_records=len(representatives),
                input_density=str(Fraction(len(representatives), size)),
                exact_expansion_factor=1 << columns,
                common_unreduced_denominator_bits=columns,
                reduced_coefficient_denominator_bits=(columns + 1) // 2,
                negative_controls=dict(omitted_address_phase=phase_control,
                                       unsupported_dense_input=domain_control),
                output_sha256=digest.hexdigest(), seconds=time.monotonic() - started,
                scope='Exact restricted source preparation and partial/full endpoint. Orbit-major copying can avoid arithmetic butterflies only after its actual layout/fanout is paid; no arbitrary-dirty native supplier.')


def density_budget():
    rows = []
    for radix_bits, exponent in ((3, 6), (5, 8), (9, 10)):
        n = radix_bits * (1 << exponent) - 1
        q = (n + radix_bits - 1) // radix_bits
        minimum = (4 * n + radix_bits - 1) // radix_bits
        volume = 1 << (minimum - 1).bit_length()
        if not Fraction(4 * n, radix_bits) <= volume < Fraction(8 * n, radix_bits):
            raise AssertionError('The sampled original assembly box is invalid')
        if not Fraction(q, volume) > Fraction(1, 8):
            raise AssertionError('The inherited digit input density bound failed')
        if not all(q > volume // (1 << f) for f in (3, 4, 8, 16)):
            raise AssertionError('A high-dimensional transversal unexpectedly fits all digits')
        rows.append(dict(input_bits=n, radix_bits=radix_bits, digits=q,
                         original_box=volume, density=str(Fraction(q, volume)),
                         f_at_least_three_cannot_fit_without_repacking=True))
    growth = []
    # Finite illustrations use epsilon=1/8. The report proves the limit for
    # every fixed epsilon>0; these samples do not substitute a new epsilon
    # into the inherited assembly or certify that limit by enumeration.
    for degree in (1, 4, 10):
        first = next(k for k in range(1, 17) if (1 << k) // 4 - 3 > degree * 8 * k)
        growth.append(dict(polynomial_degree=degree, log2_precision=8 * first,
                           dimension=1 << first, selected_columns=(1 << first) // 4,
                           log2_volume_overhead_lower_bound=(1 << first) // 4 - 3,
                           log2_polynomial_budget=degree * 8 * first,
                           exact_overhead_exceeds_budget=True))
    return dict(status='PASS INPUT DENSITY AND DECLARED GROWTH CONTROLS',
                original_assembly_samples=rows, illustrative_growth=growth,
                general_density_bound='q/T>1/8 and transversal records<=T/2^f',
                repacking_lower_bound='new_volume/original_T>2^(f-3)',
                asymptotic_scope='If f=Theta(p^epsilon) with fixed epsilon>0, 2^(f-3)/p^C tends to infinity for every fixed C. Numerical illustrations use epsilon=1/8 only.',
                exclusions='Only the full f-direction sparse-transversal preparation model; different encodings, bounded f, structured suppliers and arithmetic fusion remain open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or (args.output and args.output.exists()):
        raise ValueError('Positive workers and a fresh optional output are required')
    source = Path(__file__).resolve()
    digest = sha256(source.read_bytes()).hexdigest()
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                    workers=args.workers, seed=None, source_sha256=digest,
                    source=str(source), primary_source_id='original-assembly',
                    primary_source_role='Read-only mathematical density/size contract, not runtime input',
                    scope='Restricted finite encoding and explicitly scoped volume obstruction')
    cases = [(3, 1, 7)] if args.bounded else [(3, 1, 7), (4, 2, 7), (3, 3, 7), (6, 1, 21)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, cases))
    summary = dict(status='PASS SPARSE PREPARATION AND VOLUME BOUNDARY',
                   cases=rows, density=density_budget(),
                   complete_native_supplier=False, new_multiplier_exponent=False)
    if sha256(source.read_bytes()).hexdigest() != digest:
        raise ValueError('Source changed during exact verification')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(status=summary['status'], cases=len(rows),
                         complete_sparse_basis_columns=sum(r['complete_sparse_basis_columns'] for r in rows))))


if __name__ == '__main__':
    main()
