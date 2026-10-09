#!/usr/bin/env python3
"""Exact integer reduction and dyadic completion of five-subset center banks.

The finite certificate checks actual integral row/column operations, a complete
inverse, and the scalar center/null separation. It does not price physical
source/sink basis changes or establish an all-size rank recurrence.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from time import perf_counter


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col) if x and y)
             for col in columns] for row in a]


def smith(a):
    """Return D=U A V, V inverse, and replayable unimodular operations.

    The Euclidean pivot loop also checks divisibility of the remaining block.
    No integer factorization or approximate arithmetic is used.
    """
    a = [row[:] for row in a]
    m, n = len(a), len(a[0])
    u, v, winv = identity(m), identity(n), identity(n)
    operations = []

    def row_add(i, j, factor):
        a[i] = [x + factor * y for x, y in zip(a[i], a[j])]
        u[i] = [x + factor * y for x, y in zip(u[i], u[j])]
        operations.append(["row_add", i, j, factor])

    def row_swap(i, j):
        a[i], a[j] = a[j], a[i]
        u[i], u[j] = u[j], u[i]
        operations.append(["row_swap", i, j])

    def col_add(i, j, factor):
        for matrix in (a, v):
            for row in matrix:
                row[i] += factor * row[j]
        # If V <- V T, V^-1 <- T^-1 V^-1.
        winv[j] = [x - factor * y for x, y in zip(winv[j], winv[i])]
        operations.append(["col_add", i, j, factor])

    def col_swap(i, j):
        for matrix in (a, v):
            for row in matrix:
                row[i], row[j] = row[j], row[i]
        winv[i], winv[j] = winv[j], winv[i]
        operations.append(["col_swap", i, j])

    rank = 0
    for k in range(min(m, n)):
        nonzero = [(abs(a[i][j]), i, j)
                   for i in range(k, m) for j in range(k, n) if a[i][j]]
        if not nonzero:
            break
        _, i, j = min(nonzero)
        if i != k:
            row_swap(i, k)
        if j != k:
            col_swap(j, k)
        while True:
            i = next((i for i in range(k + 1, m) if a[i][k]), None)
            if i is not None:
                row_add(i, k, -(a[i][k] // a[k][k]))
                if a[i][k]:
                    row_swap(i, k)
                continue
            j = next((j for j in range(k + 1, n) if a[k][j]), None)
            if j is not None:
                col_add(j, k, -(a[k][j] // a[k][k]))
                if a[k][j]:
                    col_swap(j, k)
                continue
            bad = next(((i, j) for i in range(k + 1, m)
                        for j in range(k + 1, n) if a[i][j] % a[k][k]), None)
            if bad is None:
                break
            row_add(k, bad[0], 1)
        if a[k][k] < 0:
            a[k] = [-x for x in a[k]]
            u[k] = [-x for x in u[k]]
            operations.append(["row_negate", k])
        rank += 1
    diagonal = [a[i][i] for i in range(rank)]
    assert all(a[i][j] == (a[i][i] if i == j else 0)
               for i in range(m) for j in range(n))
    assert all(y % x == 0 for x, y in zip(diagonal, diagonal[1:]))
    return a, u, v, winv, operations


def replay(a, operations):
    result = [row[:] for row in a]
    for kind, *args in operations:
        if kind == "row_add":
            i, j, factor = args
            result[i] = [x + factor * y for x, y in zip(result[i], result[j])]
        elif kind == "col_add":
            i, j, factor = args
            for row in result:
                row[i] += factor * row[j]
        elif kind == "row_swap":
            i, j = args
            result[i], result[j] = result[j], result[i]
        elif kind == "col_swap":
            i, j = args
            for row in result:
                row[i], row[j] = row[j], row[i]
        elif kind == "row_negate":
            i, = args
            result[i] = [-x for x in result[i]]
        else:
            raise ValueError("Unknown operation: " + kind)
    return result


def dyadic(value):
    denominator = Fraction(value).denominator
    return denominator & (denominator - 1) == 0


def center_bank(h, mixed):
    sources = list(combinations(range(h), 5))
    pairs = list(combinations(range(h), 2))
    replaced = {(0, 1), (0, 2)} if mixed else set()
    bank = [[int(set(pair) <= set(source)) for source in sources]
            for pair in pairs]
    for i, pair in enumerate(pairs):
        if pair in replaced:
            bank[i] = [1 - x for x in bank[i]]
    return sources, pairs, replaced, bank


def central_decoder(h, target, pairs, replaced):
    """Coefficients against the actual mixed center bank, with no free T.

    Gi=sum_j Pij/4. For the two-replacement bank,
    T=(sum retained P-sum replaced D)/8 and Pij=T-Dij.
    """
    s = set(target)
    alpha = {pair: Fraction(int(set(pair) <= s), 4)
             - Fraction(3 * sum(i in s for i in pair), 32) for pair in pairs}
    if not replaced:
        return [alpha[pair] + Fraction(3, 80) for pair in pairs]
    gamma = Fraction(3, 8) + sum(alpha[pair] for pair in replaced)
    return [(-alpha[pair] - gamma / 8) if pair in replaced
            else alpha[pair] + gamma / 8 for pair in pairs]


def run(h, mixed):
    started = perf_counter()
    sources, pairs, replaced, bank = center_bank(h, mixed)
    q, volume = len(pairs), len(sources)
    reduced, u, v, winv, operations = smith(bank)
    diagonal = [reduced[i][i] for i in range(q)]
    assert all(diagonal), "Full center rank is required for this completion"
    assert replay(bank, operations) == reduced
    assert multiply(multiply(u, bank), v) == reduced
    assert multiply(v, winv) == identity(volume)
    assert multiply(winv, v) == identity(volume)
    completion = bank + winv[q:]
    # B V = diag(U^-1 D, I); B^-1 = V diag(D^-1 U, I).
    inner = [[Fraction(u[i][j], diagonal[i]) if i < q and j < q
              else Fraction(int(i == j and i >= q))
              for j in range(volume)] for i in range(volume)]
    inverse = multiply(v, inner)
    assert multiply(completion, inverse) == identity(volume)
    assert multiply(inverse, completion) == identity(volume)
    dyadic_inverse = all(dyadic(x) for row in inverse for x in row)
    assert dyadic_inverse == all(dyadic(Fraction(1, x)) for x in diagonal)
    # Complete scalar K and center-null right inverse check; the final
    # coordinates of B form a complement, not an assumed physical frame.
    decoder = [central_decoder(h, s, pairs, replaced) for s in sources]
    central = multiply(decoder, bank)
    for i, source in enumerate(sources):
        for j, target in enumerate(sources):
            t = len(set(source) & set(target))
            assert central[i][j] == Fraction((t - 1) * (t - 3), 8)
    null_columns = [row[q:] for row in inverse]
    assert not any(x for row in multiply(bank, null_columns) for x in row)
    # For side I-K, every center-null column is unchanged.
    assert not any(x for row in multiply(central, null_columns) for x in row)
    inverse_denominators = Counter(str(Fraction(x).denominator)
                                   for row in inverse for x in row)
    matrix_hash = lambda matrix: sha256(json.dumps(matrix, separators=(",", ":"),
                                                    default=str).encode()).hexdigest()
    return dict(status="EXACT FINITE CENTER/NULL COMPLETION", h=h,
        bank="two-D mixed pair features" if mixed else "original pair incidence",
        volume=volume, center_rank=q, null_dimension=volume-q,
        replaced_pairs=[list(p) for p in sorted(replaced)],
        smith_diagonal=diagonal, invariant_counts=dict(Counter(map(str, diagonal))),
        inverse_is_gaussian_dyadic=dyadic_inverse,
        inverse_denominator_counts=dict(inverse_denominators),
        max_inverse_numerator_bits=max(abs(Fraction(x).numerator).bit_length()
                                       for row in inverse for x in row),
        completion_nonzeros=sum(bool(x) for row in completion for x in row),
        inverse_nonzeros=sum(bool(x) for row in inverse for x in row),
        reduction_operations=operations,
        matrix_sha256={"bank":matrix_hash(bank),"completion":matrix_hash(completion),
                       "inverse":matrix_hash(inverse)},
        checked=dict(unimodular_replay=True,full_left_right_inverse=True,
                     all_center_kernel_entries=volume**2,
                     all_null_columns_annihilated=volume-q),
        elapsed_seconds=perf_counter()-started,
        scope="Finite exact scalar basis existence. Complete arbitrary-dirty physical basis changes, phase chronology, paid circuit size, all-size constructive basis and multiplication exponent remain open.")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--h", type=int, required=True)
    p.add_argument("--mixed", action="store_true")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.h < 7 or a.h > 12:
        raise ValueError("This initial exact discriminator is bounded to 7<=h<=12")
    if a.output.exists():
        raise FileExistsError("Use a fresh output")
    result = run(a.h, a.mixed)
    result["source_sha256"] = sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k:v for k,v in result.items()
                      if k not in ("reduction_operations", "smith_diagonal")}))


if __name__ == "__main__":
    main()
