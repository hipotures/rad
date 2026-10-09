#!/usr/bin/env python3
"""Exact paid Fourier conjugation and its scoped two-type recursion boundary.

Htilde=S C S is a scaled Walsh transform. Htilde D_G Htilde^-1 is exact
XOR by immutable mask G. Replacing each C by its two Z/Z^T factorization
uses four complete same-volume Z_f calls. At e=3f+12+u the unchanged
large-width controller cannot absorb even that single four-child word.
This is a failed construction/upper-bound ledger, not a general lower bound.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import time


def require(value, message):
    if not value:
        raise AssertionError(message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def inverse(a):
    norm = a[0] * a[0] + a[1] * a[1]
    require(norm != 0, 'A nonzero Gaussian scalar is required')
    return a[0] / norm, -a[1] / norm


def power(a, k):
    if k < 0:
        return power(inverse(a), -k)
    value = F(1), F(0)
    for _ in range(k):
        value = mul(value, a)
    return value


I, ALPHA, BETA = (F(0), F(1)), (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
ZERO, ONE = (F(0), F(0)), (F(1), F(0))


def scale(values, scalar):
    return [mul(value, scalar) for value in values]


def chirp(values, scalar):
    return [mul(value, power(scalar, index.bit_count())) for index, value in enumerate(values)]


def c_tensor(values, f, undo=False, omit_inverse_unit=False):
    values = list(values)
    a, b = (BETA, ALPHA) if undo else (ALPHA, BETA)
    for axis in range(f):
        for low in range(len(values)):
            if not (low >> axis & 1):
                high = low ^ (1 << axis)
                x, y = values[low], values[high]
                values[low] = add(mul(a, x), mul(b, y))
                values[high] = add(mul(b, x), mul(a, y))
    if undo and omit_inverse_unit:
        # Correct C^-1=(-i)^f Z C Z. Omitting the global unit multiplies
        # the actual inverse by i^f; it is not a free inverse child.
        values = scale(values, power(I, f))
    return values


def zeta(values, f, transpose=False, undo=False):
    values = list(values)
    for axis in reversed(range(f)) if undo else range(f):
        for low in range(len(values)):
            if not (low >> axis & 1):
                high = low ^ (1 << axis)
                destination, source = (low, high) if transpose else (high, low)
                other = values[source]
                values[destination] = add(values[destination], scale([other], (F(-1) if undo else F(1), F(0)))[0])
    return values


def c_via_zeta(values, f, undo=False, omit_one_factor=False):
    if not undo:
        values = chirp(values, inverse(I))
        values = zeta(values, f, transpose=True)
        values = [mul(value, (F((-2) ** index.bit_count()), F(0))) for index, value in enumerate(values)]
        if not omit_one_factor:
            values = zeta(values, f)
        values = scale(values, power(ALPHA, f))
        return chirp(values, inverse(I))
    values = chirp(values, I)
    values = scale(values, power(ALPHA, -f))
    values = zeta(values, f, undo=True)
    values = [mul(value, (F(1, (-2) ** index.bit_count()), F(0))) for index, value in enumerate(values)]
    if not omit_one_factor:
        values = zeta(values, f, transpose=True, undo=True)
    return chirp(values, I)


def htilde(values, f, undo=False, via_zeta=False, negative=None):
    scalar = inverse(I) if undo else I
    values = chirp(values, scalar)
    if via_zeta:
        values = c_via_zeta(values, f, undo, omit_one_factor=negative == 'omit_z_factor')
    else:
        values = c_tensor(values, f, undo, omit_inverse_unit=negative == 'omit_inverse_unit')
    return chirp(values, scalar)


def phase_xor(values, f, mask, via_zeta=False, negative=None):
    values = htilde(values, f, undo=True, via_zeta=via_zeta, negative=negative)
    values = [scale([value], (F(-1 if (mask & index).bit_count() & 1 else 1), F(0)))[0]
              for index, value in enumerate(values)]
    return htilde(values, f, via_zeta=via_zeta)


def probe(f):
    n = 1 << f
    entries = 0
    negative_unit = negative_factor = None
    for source in range(n):
        column = [ONE if index == source else ZERO for index in range(n)]
        require(c_via_zeta(column, f) == c_tensor(column, f), 'The complete paid C factorization must be exact')
        require(c_via_zeta(column, f, True) == c_tensor(column, f, True), 'Its literal inverse normalization must be exact')
        for mask in range(n):
            wanted = [column[index ^ mask] for index in range(n)]
            require(phase_xor(column, f, mask) == wanted and phase_xor(column, f, mask, via_zeta=True) == wanted,
                    'Every exact coefficient of every mask XOR must match both paid words')
            entries += n
            if negative_unit is None and f % 4:
                wrong = phase_xor(column, f, mask, negative='omit_inverse_unit')
                if wrong != wanted:
                    negative_unit = {'source': source, 'mask': mask}
            if negative_factor is None:
                wrong = phase_xor(column, f, mask, via_zeta=True, negative='omit_z_factor')
                if wrong != wanted:
                    negative_factor = {'source': source, 'mask': mask}
    require(negative_factor is not None and (f % 4 == 0 or negative_unit is not None),
            'Omitted paid factors and nontrivial global units must have exact counterexamples')
    fields = 0
    # Immutable three-bit controls, two guard bits and one restored companion
    # bit are complete row parameters; all four Gaussian fields are transported.
    for control in range(8):
        mask = ((control * 5) ^ (control >> 1) ^ (3 if control & 3 == 3 else 0)) % n
        for guard in range(4):
            for companion in range(2):
                for field in range(4):
                    values = [(F((index + 3 * control + guard + 7 * field) % 19 - 9, 8),
                               F((3 * index + control + 5 * companion + field) % 17 - 8, 4))
                              for index in range(n)]
                    wanted = [values[index ^ mask] for index in range(n)]
                    actual = phase_xor(values, f, mask, via_zeta=True)
                    require(actual == wanted and phase_xor(actual, f, mask, via_zeta=True) == values,
                            'All complete Gaussian fields and arbitrary spectator/companion fibers must restore')
                    fields += n
    return {'f': f, 'complete_mask_column_coefficients': entries,
            'complete_Gaussian_field_values': fields, 'control_bits': 3,
            'guard_bits': 2, 'restored_companion_bits': 1, 'Gaussian_fields': 4,
            'C_calls_per_conjugation': 2, 'Z_or_transpose_inverse_calls': 4,
            'omitted_global_inverse_unit_witness': negative_unit,
            'omitted_paid_z_factor_witness': negative_factor}


def budget_controls():
    rows = []
    for f in (15, 32, 64, 1024):
        for u in (0, 1, 2):
            e = 3 * f + 12 + u
            require(4 * f > e, 'The all-power large-width moment must exceed one')
            for p in (F(1, 2), F(9, 10), F(999, 1000)):
                # 4(f/e)^p>1 is exact after raising by its denominator.
                require(4 ** p.denominator * f ** p.numerator > e ** p.numerator,
                        'The actual four-child moment must fail exactly')
                wrong_two_child_passes = 2 ** p.denominator * f ** p.numerator < e ** p.numerator
                rows.append({'f': f, 'u': u, 'e': e, 'p': str(p), 'four_child_power_moment_exceeds_one': True,
                             'incorrect_two_child_bill_can_pass': wrong_two_child_passes})
    require(any(row['incorrect_two_child_bill_can_pass'] for row in rows), 'Omitting two full calls must produce a misleading pass')
    return {'cases': rows, 'uniform_p0to1_proof': 'For x=f/e<1 and p<=1,4*x^p>=4*x>1 whenever f>12+u',
            'two_type_cycle_mass': 'Z_E to 2 C_f to 4 Z_f: product4(f/E)^p; positive type weights cannot repair it',
            'scope': 'Only unchanged same-volume e=3f+12+u Fourier replacement; fused/shared/changed-volume architectures remain open'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.workers > 0, 'Positive workers required')
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
    own = Path(__file__).resolve()
    digest = sha256(own.read_bytes()).hexdigest()
    start, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    tasks = [1, 2] if args.bounded else [1, 2, 3, 4]
    if args.workers == 1:
        cases = [probe(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(probe, tasks))
    require(sha256(own.read_bytes()).hexdigest() == digest, 'Source stays unchanged')
    result = {'status': 'PASS exact paid phase XOR and scoped coupled-moment obstruction',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.monotonic() - tick, 'workers': args.workers, 'bounded': args.bounded,
              'source_sha256': digest, 'cases': cases, 'budget_controls': budget_controls(),
              'scope': 'Exact local Gaussian algebra and stated same-volume recursion ledger; no native router, circuit lower bound or kappa'}
    if args.output:
        (args.output / 'certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ('cases', 'budget_controls')}, sort_keys=True))


if __name__ == '__main__':
    main()
