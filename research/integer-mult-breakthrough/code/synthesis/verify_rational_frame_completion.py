#!/usr/bin/env python3
"""Bounded exact constructor, cap obstruction, and paid-chain endpoint controls."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import rational_frame_completion as F
import rational_paid_chain_endpoints as P


def determinant(rows):
    """Independent rational Gaussian determinant for the bounded verifier."""
    n, result = len(rows), Q(1)
    matrix = [list(map(Q, row)) for row in rows]
    for column in range(n):
        source = next((i for i in range(column, n) if matrix[i][column]), None)
        if source is None:
            return Q(0)
        if source != column:
            matrix[source], matrix[column] = matrix[column], matrix[source]
            result = -result
        pivot = matrix[column][column]
        result *= pivot
        for i in range(column + 1, n):
            scale = matrix[i][column] / pivot
            matrix[i] = [a - scale * b for a, b in zip(matrix[i], matrix[column])]
    return result


def inspect(result, G, expected_min, expected_max=None):
    if result['minimal_dimension'] != expected_min:
        raise AssertionError('Exact minimum dimension mismatch')
    if expected_min is None:
        vector = result['obstruction']
        if (not any(vector) or not F.contained([vector], result['lower'], len(G))
                or any(F.pairing(vector, row, G) for row in result['upper'])):
            raise AssertionError('Independent shared-radical obstruction rejected')
        return
    if len(result['completion']) != expected_min or determinant(F.gram(result['completion'], G)) == 0:
        raise AssertionError('Independent minimum-frame determinant rejected')
    if expected_max is not None:
        if (result['maximum_dimension'] != expected_max
                or determinant(F.gram(result['maximum_completion'], G)) == 0):
            raise AssertionError('Independent maximum-frame determinant rejected')


def probe():
    h, G = 12, F.form(12)
    unit = [tuple(Q(i == j) for j in range(h)) for i in range(h)]
    triple = [tuple(Q(3 * i <= j < 3 * i + 3) for j in range(h)) for i in range(3)]
    cap = F.kernel([tuple(Q(3 * (j in (0, 3, 6)) - 1) for j in range(h))], h)
    pair = P.endpoint_frames(triple, cap, G)
    inspect(pair, G, 4, 11)
    w = tuple(Q(j in (0, 3, 6)) + Q(6 * (j == 9)) for j in range(h))
    if determinant(F.gram(triple + [w], G)) != -108:
        raise AssertionError('Explicit four-vector determinant changed')
    joint = F.kernel([tuple(Q(3 * (j in (a, b, c)) - 1) for j in range(h))
                      for a in range(3) for b in range(3, 6) for c in range(6, 9)], h)
    inspect(P.endpoint_frames(triple, joint, G), G, None)
    # A general rational form with radical dimension two checks that the API
    # does not silently apply the Lorentz-specific bound to another form.
    hyperbolic = tuple(tuple(Q((1 if i < 2 else -1) if i == j else 0)
                              for j in range(4)) for i in range(4))
    four_units = [tuple(Q(i == j) for j in range(4)) for i in range(4)]
    isotropic = [(Q(1), Q(0), Q(1), Q(0)), (Q(0), Q(1), Q(0), Q(1))]
    inspect(P.endpoint_frames(isotropic, four_units, hyperbolic), hyperbolic, 4, 4)
    singular = ((Q(1), Q(0), Q(0)), (Q(0), Q(-1), Q(0)), (Q(0), Q(0), Q(0)))
    three_units = [tuple(Q(i == j) for j in range(3)) for i in range(3)]
    inspect(P.endpoint_frames([three_units[0]], three_units, singular), singular, 1, 2)
    inspect(P.endpoint_frames([three_units[2]], three_units, singular), singular, None)
    inspect(P.endpoint_frames([], three_units, singular), singular, 0, 2)
    controls = []
    for name, call in [('outside_cap', lambda: F.complete([unit[0]], [unit[1]], G)),
                       ('nonsymmetric_form', lambda: F.complete([], [], ((Q(1), Q(2)), (Q(0), Q(1))))),
                       ('invalid_chain_dimension', lambda: P.widths(3, (4, 1), (10, 10))),
                       ('zero_exponent', lambda: P.power_interval(2, 0, 10))]:
        try:
            call()
        except ValueError:
            controls.append(name)
        else:
            raise AssertionError('Adverse domain accepted: ' + name)
    minimum_widths = P.widths(4, (2, 1), (11, 11))
    maximum_widths = P.widths(11, (2, 1), (11, 11))
    low = P.moment_interval(minimum_widths, 9, 10, 32)
    high = P.moment_interval(maximum_widths, 9, 10, 32)
    if sum(minimum_widths) != sum(maximum_widths) or not high[1] < low[0]:
        raise AssertionError('Exact concentrating-endpoint moment improvement failed')
    # Verify integer power enclosures independently of the bisection loop.
    for rank in (1, 2, 3, 7, 9, 10, 11):
        a, b = P.power_interval(rank, 9, 10, 32)
        if not a ** 10 <= rank ** 9 <= b ** 10:
            raise AssertionError('Power enclosure failed its defining inequalities')
    return dict(status='PASS RATIONAL COMPLETION AND PAID ENDPOINT CONTROLS',
                exact_completion_cases=6, explicit_Gram_determinant=-108,
                radical_two_generic_control=True, negative_controls=controls,
                minimum_widths=minimum_widths, maximum_widths=maximum_widths,
                exponent='9/10', strict_ideal_moment_improvement_lower=str(low[0] - high[1]),
                local_ring_and_native_fees_not_assumed=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    paths = [Path(__file__).resolve(), Path(F.__file__).resolve(), Path(P.__file__).resolve()]
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in paths}
    receipt = probe()
    if hashes != {path.name: sha256(path.read_bytes()).hexdigest() for path in paths}:
        raise AssertionError('The bounded constructor closure changed')
    receipt['source_closure'] = hashes
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
