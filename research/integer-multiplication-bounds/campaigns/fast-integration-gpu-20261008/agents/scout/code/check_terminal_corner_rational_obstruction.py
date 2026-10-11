#!/usr/bin/env python3
"""Check the exact rational obstruction for one source-to-terminal corner.

This is a scoped lemma, not an impossibility claim for other frames, bases,
ordered corners or joint words. Independent Gram projectors validate the
symbolic primitive-source/center decomposition.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import sys


def determinant2(M):
    return M[5][6] * M[1][2] - M[5][2] * M[1][6]


def primitive_transition(h, beta):
    star = (1 - 9 * beta) / (9 * (1 - h * beta))
    source_in, source_out = {0, 1, 2}, {0, 3, 4}
    center = [F(i == 0) + F(2, h - 9) for i in range(h)]
    center_sum = sum(center)
    lc = [x - beta * center_sum for x in center]
    rc = [x - star * center_sum for x in center]
    result = [[F(i == j) + F(h - 9, 4) * lc[i] * rc[j]
               for j in range(h)] for i in range(h)]
    for support in [source_in, source_out]:
        left = [F(i in support) - 3 * beta for i in range(h)]
        right = [F(i in support) - 3 * star for i in range(h)]
        for i in range(h):
            for j in range(h):
                result[i][j] -= left[i] * right[j] / 2
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    geometry_code = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
    sys.path.insert(0, str(geometry_code))
    from review_positive_physical_profiles import projector
    controls = []
    # Independent dense Gram computations, including the unique h>9 exception.
    for h in [14, 23, 25]:
        symbols = list(range(2, h + 2))
        symbols[0] = 1
        symbols[4] = -symbols[3]
        source_symbols = [int(i in {0, 1, 2}) for i in range(h)]
        for beta in map(F, [0, 1, -1, 2]):
            basis = f'beta:{beta.numerator}:{beta.denominator}'
            terminal = projector(h, 1, symbols, basis)
            source = projector(h, 7, source_symbols, basis)
            actual = [[terminal[i][j] - source[i][j] for j in range(h)] for i in range(h)]
            primitive = primitive_transition(h, beta)
            assert actual == primitive
            polynomial = 2 - 3 * (h - 3) * beta + 9 * (h - 9) * beta * beta
            assert (1 - h * beta) * determinant2(actual) == polynomial / 24
            controls.append({'h': h, 'beta': str(beta), 'matrix_entries': h * h,
                             'minor_times_1_minus_h_beta': str(polynomial / 24),
                             'independent_gram_and_primitive_identity': 'PASS'})
    roots = []
    for h in range(10, 513):
        delta = 9 * ((h - 7) ** 2 + 32)
        root = math.isqrt(delta)
        if root * root == delta:
            values = [F(3 * (h - 3) + sign * root, 18 * (h - 9)) for sign in [-1, 1]]
            assert all(2 - 3 * (h - 3) * x + 9 * (h - 9) * x * x == 0 for x in values)
            roots.append({'h': h, 'roots': list(map(str, values))})
    assert roots == [{'h': 14, 'roots': ['1/15', '2/3']}]
    # The finite enumeration supports, rather than replaces, the factor proof.
    factor_pairs = [(d, 32 // d) for d in range(1, 6)
                    if 32 % d == 0 and (d + 32 // d) % 2 == 0]
    assert factor_pairs == [(2, 16), (4, 8)]
    receipt = {'utc': datetime.now(timezone.utc).isoformat(),
               'status': 'PASS SCOPED SOURCE-TO-MAXIMAL-TERMINAL RATIONAL CORNER OBSTRUCTION',
               'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'independent_gram_source_sha256': hashlib.sha256((geometry_code / 'review_positive_physical_profiles.py').read_bytes()).hexdigest(),
               'primitive_configuration': {'common': 0, 'input_source': [0, 1, 2],
                                           'output_source': [0, 3, 4], 'witness_rows': [5, 1],
                                           'witness_columns': [6, 2]},
               'minor_identity': '(1-h*beta)*det(Q_beta[{5,1},{6,2}])=(2-3*(h-3)*beta+9*(h-9)*beta^2)/24',
               'discriminant': '9*((h-7)^2+32)',
               'all_integer_h_greater_than9_rational_root_cases': roots,
               'factor_argument': 'A rational square root of an integer is integral. With u^2=(h-7)^2+32, (u-h+7)*(u+h-7)=32. The only positive same-parity factor pairs are(2,16),(4,8), yieldingh14 orh9; h9 is excluded.',
               'finite_supporting_dimensions': '10..512', 'controls': controls,
               'scope': 'This excludes exact rational disappearance of this displayed witness minor at h23 andh25 in the homogeneous rank-one I-betaJ family. It does not exclude other rational loci, better ordered profiles, signed frames, common-context policies or other basis families.',
               'attribution': ['Avi Eisenberg (PR62)', 'eumemic (PR57)',
                               'Alejandro Zarzuelo Urdiales (PR61)', 'Inherited authors and independent primitive-frame/rational-basis research.']}
    args.output.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': receipt['status'], 'controls': len(controls),
                      'rational_root_exception': roots}), flush=True)


if __name__ == '__main__':
    main()
