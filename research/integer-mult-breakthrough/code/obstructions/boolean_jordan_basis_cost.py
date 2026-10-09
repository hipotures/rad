#!/usr/bin/env python3
"""Exact linear BTK basis discriminator with the full basis-change ledger.

The cited classical basis construction is an input, not our discovery.
We test its exact Boolean zeta conjugation, inverse coefficients and the
specific sequential basis implementation cost. Balanced alternatives remain
open. This is not a native supplier or multiplier exponent certificate.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from math import comb, factorial
import json
from pathlib import Path


PRIMARY_SOURCE = "https://arxiv.org/abs/1001.0280v2"


def chains(n):
    result = [(0, [(1,)])]
    for f in range(n):
        updated = []
        size = 1 << f
        zero = (0,) * size
        for k, vectors in result:
            old = {k + j: vector for j, vector in enumerate(vectors)}
            # Two boundary columns and all interior two-input blocks. The
            # construction is equations (35)-(36) of the pinned source.
            long = []
            for level in range(k, f + 2 - k):
                base = old.get(level, zero)
                shifted = old.get(level - 1, zero)
                long.append(tuple(base) + tuple((level - k) * x for x in shifted))
            updated.append((k, long))
            short = []
            for level in range(k + 1, f + 1 - k):
                base = old[level]
                shifted = old[level - 1]
                short.append(tuple(-x for x in base)
                             + tuple((f - k - level + 1) * x for x in shifted))
            if short:
                updated.append((k + 1, short))
        result = updated
    return result


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def up(vector, n):
    output = [0] * len(vector)
    for x, value in enumerate(vector):
        if value:
            for bit in range(n):
                if not (x >> bit) & 1:
                    output[x | (1 << bit)] += value
    return tuple(output)


def odd_part(value):
    while value % 2 == 0:
        value //= 2
    return value


def exact_case(n):
    family = chains(n)
    columns = [v for _, chain in family for v in chain]
    size = 1 << n
    if len(columns) != size:
        raise AssertionError("The complete basis dimension failed")
    norms = [dot(v, v) for v in columns]
    if any(not x for x in norms):
        raise AssertionError("A zero chain column was introduced")
    if any(dot(columns[i], columns[j]) for i in range(size) for j in range(i)):
        raise AssertionError("The integral columns are not orthogonal")
    offset = 0
    for k, chain in family:
        for j, v in enumerate(chain):
            if any(x and index.bit_count() != k + j for index, x in enumerate(v)):
                raise AssertionError("A chain is not rank homogeneous")
            expected = chain[j + 1] if j + 1 < len(chain) else (0,) * size
            if up(v, n) != expected:
                raise AssertionError("A full upward chain identity failed")
            # Z = exp(U). In an unweighted upward chain its coefficients
            # are 1/r!, checked against every complete Boolean address.
            actual = [sum(v[y] for y in range(size) if (y & x) == y)
                      for x in range(size)]
            reconstructed = [sum(Fraction(chain[j + r][x], factorial(r))
                                 for r in range(len(chain) - j))
                             for x in range(size)]
            if actual != reconstructed:
                raise AssertionError("The complete Boolean-zeta chain reconstruction failed")
        offset += len(chain)
    # Orthogonality gives the actual full inverse: column transpose / norm.
    inverse = [[Fraction(value, norm) for value in column]
               for column, norm in zip(columns, norms)]
    if any(dot(inverse[i], columns[j]) != int(i == j)
           for i in range(size) for j in range(size)):
        raise AssertionError("The complete exact inverse failed")
    denominator_odds = sorted({odd_part(value.denominator)
                               for row in inverse for value in row})
    pairs_per_level = [((1 << f) - comb(f, f // 2)) for f in range(n)]
    # T(n)=2T(n-1)+2(2^(n-1)-binom(n-1,floor((n-1)/2))).
    additions = 0
    for pairs in pairs_per_level:
        additions = 2 * additions + 2 * pairs
    if n >= 3 and not any(x > 1 for x in denominator_odds):
        raise AssertionError("The non-dyadic inverse discriminator disappeared")
    corrupted = list(family[0][1][1])
    corrupted[0] += 1
    if tuple(corrupted) == up(family[0][1][0], n):
        raise AssertionError("The changed chain negative did not discriminate")
    wrong_inverse = [list(row) for row in inverse]
    chosen = next((i for i, norm in enumerate(norms) if norm != 1), 0)
    wrong_inverse[chosen] = (list(columns[chosen]) if norms[chosen] != 1
                              else [2 * x for x in columns[chosen]])
    if all(dot(wrong_inverse[chosen], columns[j]) == int(chosen == j)
           for j in range(size)):
        raise AssertionError("The omitted normalization negative did not discriminate")
    return {"n": n, "dimension": size, "chain_lengths": [len(c) for _, c in family],
            "chain_count": len(family), "all_complete_columns_checked": size,
            "exact_inverse_odd_denominator_parts": denominator_odds,
            "max_integral_coefficient": max(abs(x) for v in columns for x in v),
            "sequential_basis_additions": additions,
            "basis_additions_per_address": str(Fraction(additions, size)),
            "direct_zeta_additions": n * size // 2,
            "both_basis_directions_additions": 2 * additions,
            "scalar_multiplications_permutations_chain_work_excluded_from_optimistic_addition_count": True,
            "bad_chain_and_omitted_inverse_normalization_rejected": True,
            "exact_chain_and_zeta_columns": [[list(v) for v in c] for _, c in family]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("Positive workers are required")
    source = Path(__file__).resolve()
    initial = sha256(source.read_bytes()).hexdigest()
    sizes = range(1, 4 if args.bounded else 7)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        protocol = {"started_utc": datetime.now(timezone.utc).isoformat(),
                    "source_sha256": initial, "primary_source": PRIMARY_SOURCE,
                    "source_version": "2010-04-05 v2", "workers": args.workers,
                    "n_values": list(sizes), "standard_library_only": True}
        (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(exact_case, sizes))
    if initial != sha256(source.read_bytes()).hexdigest():
        raise AssertionError("The source changed during the experiment")
    receipt = {"status": "PASS EXACT BOOLEAN JORDAN BASIS DISCRIMINATOR", "rows": rows,
               "scope": "Classical linear BTK basis, full exact inverse/zeta and sequential addition ledger only",
               "no_native_or_balanced_transform_or_multiplier_exponent_claim": True}
    if args.output:
        (args.output / "certificate.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "sizes": len(rows),
                      "basis_additions": [r["sequential_basis_additions"] for r in rows],
                      "inverse_is_not_dyadic_from_n3": all(any(x > 1 for x in r["exact_inverse_odd_denominator_parts"])
                                                            for r in rows if r["n"] >= 3)}))


if __name__ == "__main__":
    main()
