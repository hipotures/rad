#!/usr/bin/env python3
"""Exact source-ridge endpoint reflection and arbitrary-dirty echo controls.

This proves finite geometric identities and tests a literal finite array echo.
It does not identify the public compiler's source arrays with these ridges or
authorize an uncharged physical frame shrink.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import time

from review_positive_physical_profiles import mm


def transpose(a):
    return [list(row) for row in zip(*a)]


def matrix_vector(a, x):
    return [sum(v * w for v, w in zip(row, x)) for row in a]


def difference(a, b):
    return [[x-y for x, y in zip(row, other)] for row, other in zip(a, b)]


def geometry(h, beta, c, a, b):
    identity = [[Q(i == j) for j in range(h)] for i in range(h)]
    H0 = [[Q(i == j)-Q(1, 9) for j in range(h)] for i in range(h)]
    L = [[Q(i == j)-beta for j in range(h)] for i in range(h)]
    eta = beta / (1-h*beta)
    inverse_L = [[Q(i == j)+eta for j in range(h)] for i in range(h)]
    assert mm(L, inverse_L) == identity
    HLi = mm(H0, inverse_L)

    def gram_projector(columns, norms):
        B = transpose(columns)
        G = mm(mm(transpose(B), H0), B)
        assert G == [[Q(norms[i] if i == j else 0)
                      for j in range(len(norms))] for i in range(len(norms))]
        inverse_G = [[Q(1, norms[i]) if i == j else Q(0)
                      for j in range(len(norms))] for i in range(len(norms))]
        return mm(mm(mm(mm(L, B), inverse_G), transpose(B)), HLi)

    common_columns = [[Q(int(j == c)+2*int(j == i)) for j in range(h)]
                      for i in range(h) if i != c]
    kernel_columns = [[Q(int(j == c)+2*int(j == i)) for j in range(h)]
                      for i in range(h) if i not in (c, a, b)]
    kernel_columns.append([Q(int(j == a)-int(j == b)) for j in range(h)])
    Gamma = gram_projector(common_columns, [4]*(h-1))
    K = gram_projector(kernel_columns, [4]*(h-3)+[2])
    T = (c, a, b)
    w = matrix_vector(L, [Q(i in T) for i in range(h)])
    d = [sum(HLi[i][j] for i in T)/2 for j in range(h)]
    source = [[x*y for y in d] for x in w]
    assert sum(x*y for x, y in zip(w, d)) == 1
    assert difference(Gamma, K) == source
    assert mm(Gamma, Gamma) == Gamma and mm(K, K) == K
    assert mm(Gamma, K) == K and mm(K, Gamma) == K
    assert sum(Gamma[i][i] for i in range(h)) == h-1
    assert sum(K[i][i] for i in range(h)) == h-2
    DG = difference(identity, [[2*x for x in row] for row in Gamma])
    DK = difference(identity, [[2*x for x in row] for row in K])
    reflection = difference(identity, [[2*x for x in row] for row in source])
    assert mm(DK, DG) == reflection and mm(DG, DK) == reflection
    source_count = surviving_count = 0
    intersection_counts = [0]*4
    Tset = set(T)
    for U in combinations(range(h), 3):
        k = len(set(U) & Tset)
        dU = [sum(HLi[i][j] for i in U)/2 for j in range(h)]
        wU = matrix_vector(L, [Q(i in U) for i in range(h)])
        forward = sum(x*y for x, y in zip(dU, w))
        reverse = sum(x*y for x, y in zip(d, wU))
        assert forward == reverse == Q(k-1, 2)
        coefficient = (int(c in U)-int(c in U and a in U)
                       -int(c in U and b in U)+int(set(U) == Tset))
        surviving = c in U and a not in U and b not in U
        assert coefficient == int(surviving)
        if surviving:
            assert forward == reverse == 0
            surviving_count += 1
        intersection_counts[k] += 1
        source_count += 1
    # An arbitrary dirty array is not invariant. Its indicator at d*x=1
    # distinguishes the two reflected addresses of the excluded source T.
    assert matrix_vector(DG, w) == [-x for x in w]
    assert matrix_vector(DK, w) == w
    assert sum(x*y for x, y in zip(d, matrix_vector(DG, w))) == -1
    assert sum(x*y for x, y in zip(d, matrix_vector(DK, w))) == 1
    return dict(h=h, beta=str(beta), target=list(T), source_triples_checked=source_count,
                surviving_source_ridges=surviving_count,
                all_intersection_counts=intersection_counts,
                explicit_Gram_projector_identity=True,
                both_orientation_covector_identity=True,
                complete_scalar_coefficient_cancellation=True,
                arbitrary_dirty_reflection_counterexample=True), DG, DK, HLi


def finite_array_echo():
    h, prime = 5, 5
    _, DG, DK, HLi = geometry(h, Q(0), 0, 1, 2)
    addresses = list(product(range(prime), repeat=h))
    lookup = {x: i for i, x in enumerate(addresses)}

    def residue(x):
        return x.numerator * pow(x.denominator, -1, prime) % prime

    def address_permutation(matrix):
        matrix = [[residue(x) for x in row] for row in matrix]
        permutation = [lookup[tuple(sum(a*b for a, b in zip(row, x)) % prime
                                    for row in matrix)] for x in addresses]
        assert sorted(permutation) == list(range(len(addresses)))
        assert all(permutation[permutation[i]] == i for i in range(len(addresses)))
        return permutation

    gamma, kernel = map(address_permutation, (DG, DK))
    dU = [residue(sum(HLi[i][j] for i in (0, 3, 4))/2) for j in range(h)]
    dT = [residue(sum(HLi[i][j] for i in (0, 1, 2))/2) for j in range(h)]
    ridge_values = (0, 1, 1, 0, 1)
    signal = [ridge_values[sum(a*b for a, b in zip(dU, x)) % prime]
              for x in addresses]
    dirty = [int(sum(a*b for a, b in zip(dT, x)) % prime == 1)
             for x in addresses]
    output = [(i*17+i//5) & 1 for i in range(len(addresses))]

    def pull(array, permutation):
        return [array[i] for i in permutation]

    def xor(a, b):
        return [x ^ y for x, y in zip(a, b)]

    def section(q, y, permutation):
        q = pull(q, permutation)
        y = xor(y, q)
        q = pull(q, permutation)  # Literal inverse of the same operator.
        q = xor(q, signal)
        return q, y

    assert pull(signal, gamma) == pull(signal, kernel)
    expected = xor(output, pull(signal, kernel))
    for permutation in (gamma, kernel):
        q, y = section(dirty, output, permutation)
        q, y = section(q, y, permutation)
        assert q == dirty and y == expected
    # Mixing operators between echo halves leaves excluded-source dirty data.
    q, y = section(dirty, output, gamma)
    q, y = section(q, y, kernel)
    assert q == dirty and y != expected
    return dict(h=h, address_prime=prime, addresses=len(addresses),
                actual_invertible_address_permutations=True,
                consistent_Gamma_and_K_echoes_agree_on_signal=True,
                arbitrary_dirty_restoration_in_consistent_echoes=True,
                inconsistent_echo_halves_dirty_counterexample=True,
                dirty_residue_addresses=sum(a != b for a, b in zip(y, expected)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    start = time.monotonic()
    rows = []
    for h, betas in [(23, [Q(-1), Q(1, 15), Q(169, 261)]),
                     (25, [Q(-1), Q(7, 207), Q(1, 2)])]:
        for beta in betas:
            for target in [(0, 1, 2), (h-3, h-2, h-1), (h//2, 0, h-1)]:
                row, _, _, _ = geometry(h, beta, *target)
                rows.append(row)
                print(json.dumps(dict(completed=len(rows), h=h, beta=str(beta))), flush=True)
    result = dict(status='PASS EXACT SOURCE-RIDGE REFLECTION AND ARRAY-ECHO CONTROLS',
                  classification='DISCOVERY: ENDPOINT TRANSFER NOT ACCEPTED',
                  rows=rows, finite_array_echo=finite_array_echo(),
                  elapsed_seconds=time.monotonic()-start,
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Exact explicit-Gram projectors, all finite source triples, '
                        'both covector orientations, scalar cancellation and a literal '
                        'finite arbitrary-dirty array echo. The public physical source '
                        'array/interface representation, changed terminal word and '
                        'all transition costs remain unverified. The two reflection '
                        'operators do not agree on arbitrary dirty arrays; each echo '
                        'must use its actual unchanged operator in both halves.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
