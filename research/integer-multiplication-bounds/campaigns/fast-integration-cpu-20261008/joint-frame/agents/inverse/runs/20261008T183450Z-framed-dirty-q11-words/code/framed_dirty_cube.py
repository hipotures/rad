#!/usr/bin/env python3
"""Actual partial-swap arrays for the explicit four-mixer frame schedule.

The q=5 control represents EVERY source/target/dirty basis column exactly.
It is a small contract fixture, not the 23/25-axis public producer. The mixer
is deliberately not self-inverse, and its three distinct center terminals
require paid copy transforms. No upstream implementation is imported.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import time


def matrix_multiply(a, b, p):
    n = len(a)
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(n)) % p
                       for j in range(n)) for i in range(n))


def transpose(a):
    return tuple(zip(*a))


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def inverse(a, p):
    n = len(a)
    rows = [list(row)+list(unit) for row, unit in zip(a, identity(n))]
    for k in range(n):
        pivot = next(i for i in range(k, n) if rows[i][k] % p)
        rows[k], rows[pivot] = rows[pivot], rows[k]
        scale = pow(rows[k][k], -1, p)
        rows[k] = [x*scale % p for x in rows[k]]
        for i in range(n):
            if i != k:
                scale = rows[i][k]
                rows[i] = [(x-scale*y) % p for x, y in zip(rows[i], rows[k])]
    return tuple(tuple(row[n:]) for row in rows)


def projector(columns, p):
    gram = tuple(tuple((int(i == j)-pow(9, -1, p)) % p for j in range(3)) for i in range(3))
    b = transpose(columns)
    btg = matrix_multiply_rect(transpose(b), gram, p)
    middle = inverse(matrix_multiply_rect(btg, b, p), p)
    result = matrix_multiply_rect(matrix_multiply_rect(b, middle, p), btg, p)
    assert matrix_multiply(result, result, p) == result
    return result


def matrix_multiply_rect(a, b, p):
    return tuple(tuple(sum(x*y for x, y in zip(row, col)) % p
                       for col in zip(*b)) for row in a)


def partial_swap(project, p):
    return tuple(tuple(((int(i == j)-project[i][j]) if (a//3 == b//3) else project[i][j]) % p
                       for b in range(6) for j in [b % 3])
                 for a in range(6) for i in [a % 3])


def fixture(p, full_basis, output):
    started = time.time()
    t = partial_swap(projector(((1, 1, 1),), p), p)
    full = partial_swap(identity(3), p)
    e = matrix_multiply(full, t, p)
    centers = []
    for c in range(3):
        columns = []
        for j in range(3):
            if j == c:
                continue
            column = [0]*3
            column[c], column[j] = pow(2, -1, p), 1
            columns.append(tuple(column))
        center = partial_swap(projector(tuple(columns), p), p)
        assert matrix_multiply(center, t, p) == matrix_multiply(t, center, p)
        centers.append(center)
    size = p**6

    @lru_cache(None)
    def permutation(matrix):
        assert matrix_multiply(matrix, matrix, p) == identity(6)
        indices = []
        for a in range(size):
            digits, z = [], a
            for _ in range(6):
                digits.append(z % p)
                z //= p
            transformed = [sum(x*y for x, y in zip(row, digits)) % p for row in matrix]
            target, power = 0, 1
            for digit in transformed:
                target += digit*power
                power *= p
            indices.append(target)
        assert len(set(indices)) == size
        return tuple(indices)

    def move(row, matrix):
        return [row[i] for i in permutation(matrix)]

    if full_basis:
        initial = [[1 << (r*size+a) for a in range(size)] for r in range(5)]
    else:
        initial = [[((r*size+a+1)*0x9E3779B97F4A7C15) & ((1 << 64)-1)
                    for a in range(size)] for r in range(5)]
    # Source carrier is role2. Copy into roles3/4, then swap2/3 by three
    # actual XORs: J*M*V=I, but M != M^-1 on arbitrary dirty inputs.
    mixer = [(3, 2), (4, 2), (2, 3), (3, 2), (2, 3)]

    def word(source, target, mode):
        rows = list(initial)

        def xor(a, b):
            rows[a] = [x ^ y for x, y in zip(rows[a], rows[b])]

        for a, b in mixer:
            xor(a, b)
        for r in range(2, 5):
            xor(target, r)
        for a, b in reversed(mixer):
            xor(a, b)
        rows[2] = move(rows[2], t)
        xor(2, source)
        rows[3], rows[4] = move(rows[3], t), move(rows[4], t)
        for a, b in mixer:
            xor(a, b)
        for r, center in zip(range(2, 5), centers):
            rows[r] = move(rows[r], matrix_multiply(center, t, p))
            copied = list(rows[r])
            if mode != "omit-center-transform":
                copied = move(copied, center)
            rows[target] = [x ^ y for x, y in zip(rows[target], copied)]
            del copied
        rows[target] = move(rows[target], e)
        if mode != "omit-cleanup":
            for r, center in zip(range(2, 5), centers):
                rows[r] = move(rows[r], matrix_multiply(full, center, p))
        for a, b in (mixer if mode == "wrong-last-inverse" else reversed(mixer)):
            xor(a, b)
        rows[source] = move(rows[source], e)
        xor(2, source)
        mismatches = 0
        first = None
        for r, row in enumerate(rows):
            main = initial[r]
            indices = permutation(e if r in (source, target) else full)
            source_indices = permutation(full)
            for a, got in enumerate(row):
                expected = main[indices[a]]
                if r == target:
                    expected ^= initial[source][source_indices[a]]
                if got != expected:
                    mismatches += 1
                    if first is None:
                        first = {"physical_role": r, "address": a,
                                 "first_differing_basis_column": (got ^ expected).bit_length()-1 if full_basis else None}
        return {"source_role": source, "target_role": target, "mode": mode,
                "status": "PASS_EXACT_PHYSICAL_ARRAY" if not mismatches else "PHYSICAL_ARRAY_MISMATCH",
                "mismatched_records": mismatches, "first_mismatch": first}

    results = [word(0, 1, "complete"), word(1, 0, "complete"),
               word(0, 1, "omit-center-transform"), word(0, 1, "omit-cleanup"),
               word(0, 1, "wrong-last-inverse")]
    assert all(r["status"] == "PASS_EXACT_PHYSICAL_ARRAY" for r in results[:2])
    assert all(r["status"] == "PHYSICAL_ARRAY_MISMATCH" for r in results[2:])
    result = {"status": "PASS_POSITIVES_AND_PREDECLARED_PHYSICAL_NEGATIVES",
              "address_prime": p, "local_dimension": 3, "addresses_per_role": size,
              "original_roles": 5, "arbitrary_dirty_roles": 3,
              "all_basis_columns": 5*size if full_basis else None,
              "full_source_target_dirty_basis": full_basis, "all_addresses_checked": True,
              "sampled_words": None if full_basis else "Distinct deterministic64-bit words at every physical address/role",
              "source_frame": "S_triple", "target_and_dirty_source_frame": "I",
              "expected_source_output": "S_triple_perp*x",
              "expected_target_output": "S_full*x+S_triple_perp*y",
              "expected_dirty_output": "S_full*d",
              "mixer_XORs": 5, "wrapped_scalar_XORs": 28,
              "charged_auxiliary_residual_rank": 15, "permutation_tables": permutation.cache_info().currsize,
              "controls": results, "workers": 1, "native_threads": 1,
              "wall_seconds": time.time()-started,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope": "Actual finite partial-swap address permutations and raw XOR payloads for a non-self-inverse3-center contract fixture. Opposite shear uses data-role exchange. Literal public23/25-axis words and the reverse-transposed owned-port compiler are separate obligations."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "prime": p,
                      "addresses": size, "basis": full_basis, "seconds": result["wall_seconds"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prime", type=int, choices=(5, 7, 11), default=5)
    parser.add_argument("--full-basis", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    assert not args.full_basis or args.prime == 5, "bounded exact basis fixture; larger address controls use frozen words"
    fixture(args.prime, args.full_basis, args.output)


if __name__ == "__main__":
    main()
