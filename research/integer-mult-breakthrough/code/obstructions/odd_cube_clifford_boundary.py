#!/usr/bin/env python3
"""Exact odd-cube reflection and single-Clifford boundary discriminator.

This is an independent integer kernel calculation. It supplies no native
bank word, physical frame chronology, scalar cost, or multiplier exponent.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time


def low_walsh_sum(k, radius, distance):
    """Integer numerator of the low-degree Walsh projector kernel."""
    return sum(
        (-1) ** overlap * comb(distance, overlap)
        * comb(k - distance, degree - overlap)
        for degree in range(radius + 1)
        for overlap in range(max(0, degree - (k - distance)),
                             min(distance, degree) + 1)
    )


def walsh(values):
    values = list(values)
    if not values or len(values) & (len(values) - 1):
        raise ValueError('The Walsh vector must have positive power-of-two size')
    step = 1
    while step < len(values):
        for start in range(0, len(values), 2 * step):
            for i in range(start, start + step):
                a, b = values[i], values[i + step]
                values[i], values[i + step] = a + b, a - b
        step *= 2
    return values


def gram_rows(kernel):
    return [sum(a * kernel[z ^ shift] for z, a in enumerate(kernel))
            for shift in range(len(kernel))]


def conjugated_z_row(kernel):
    return [sum((-a if z & 1 else a) * kernel[z ^ shift]
                for z, a in enumerate(kernel))
            for shift in range(len(kernel))]


def fraction_string(numerator, denominator):
    value = Fraction(numerator, denominator)
    return str(value.numerator) if value.denominator == 1 else str(value)


def check_kernel(kernel, denominator, expected_signs):
    spectrum = walsh(kernel)
    if spectrum != [denominator * sign for sign in expected_signs]:
        raise AssertionError('The independently constructed Walsh signature differs')
    gram = gram_rows(kernel)
    if gram != [denominator * denominator] + [0] * (len(kernel) - 1):
        raise AssertionError('Complete circulant Gram rows do not give the identity')
    conjugated = conjugated_z_row(kernel)
    nonzero = [(i, value) for i, value in enumerate(conjugated) if value]
    pauli_row = len(nonzero) == 1 and abs(nonzero[0][1]) == denominator ** 2
    corrupted = list(kernel)
    corrupted[0] += 1
    if gram_rows(corrupted) == gram:
        raise AssertionError('A changed kernel coefficient escaped the Gram control')
    return {
        'dimension': len(kernel),
        'complete_gram_shifts': len(gram),
        'walsh_negative_eigenvalues': expected_signs.count(-1),
        'walsh_positive_eigenvalues': expected_signs.count(1),
        'conjugated_z0_nonzero_row_entries': len(nonzero),
        'conjugated_z0_row_is_pauli': pauli_row,
        'first_nonzero_conjugated_entries': [
            {'column': i, 'value': fraction_string(value, denominator ** 2)}
            for i, value in nonzero[:8]
        ],
        'changed_kernel_coefficient_rejected': True,
    }


def probe(k):
    if k < 3 or not k & 1:
        raise ValueError('An odd cube dimension at least three is required')
    radius = (k - 1) // 2
    denominator = 1 << (k - 1)
    radial = [denominator * (distance == 0)
              - low_walsh_sum(k, radius, distance)
              for distance in range(k + 1)]
    if any(radial[distance] for distance in range(0, k + 1, 2)):
        raise AssertionError('Odd-cube reflection must reverse the parity sectors')
    kernel = [radial[z.bit_count()] for z in range(1 << k)]
    signature = [-1 if z.bit_count() <= radius else 1
                 for z in range(1 << k)]
    full = check_kernel(kernel, denominator, signature)
    q_kernel = [radial[z.bit_count() + 1 - (z.bit_count() % 2)]
                for z in range(1 << (k - 1))]
    q_signature = [-1 if z.bit_count() <= radius else 1
                   for z in range(1 << (k - 1))]
    parity = check_kernel(q_kernel, denominator, q_signature)
    if full['conjugated_z0_row_is_pauli'] != (k == 3):
        raise AssertionError('The selected Pauli boundary did not match its proof')
    if parity['conjugated_z0_row_is_pauli'] != (k == 3):
        raise AssertionError('The parity-bank Pauli boundary did not match its proof')
    # Check every source/target entry against the specified parity encodings.
    opposite_entries = 0
    for u in range(1 << (k - 1)):
        source = u | ((u.bit_count() & 1) << (k - 1))
        for v in range(1 << (k - 1)):
            target = v | (((v.bit_count() & 1) ^ 1) << (k - 1))
            if kernel[source ^ target] != q_kernel[u ^ v]:
                raise AssertionError('The opposite-parity encoding changed an entry')
            opposite_entries += 1
    magnitudes = sorted({abs(Fraction(x, denominator)) for x in radial if x})
    return {
        'cube_dimension': k,
        'walsh_radius': radius,
        'common_kernel_denominator': denominator,
        'radial_kernel': [fraction_string(x, denominator) for x in radial],
        'nonzero_kernel_magnitudes': [str(x) for x in magnitudes],
        'full_reflection': full,
        'parity_bank_reflection': parity,
        'opposite_parity_entries_checked': opposite_entries,
        'single_clifford_rejected': k >= 5,
        'legitimate_paid_scalar_bank_word_excluded': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('At least one worker is required')
    cases = [3, 5] if args.bounded else [3, 5, 7, 9]
    started = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    if args.workers == 1:
        rows = list(map(probe, cases))
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(cases))) as pool:
            rows = list(pool.map(probe, cases))
    result = {
        'status': 'PASS',
        'started_utc': started,
        'finished_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.perf_counter() - clock,
        'workers_requested': args.workers,
        'bounded': args.bounded,
        'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'arithmetic': 'Exact integers and rational output; no sampled columns',
        'scope': 'Complete finite circulant kernels and one Pauli conjugation witness; no native supplier or exponent',
        'cases': rows,
    }
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / 'certificate.json').write_text(encoded, encoding='utf-8')
    print(encoded, end='')


if __name__ == '__main__':
    main()
