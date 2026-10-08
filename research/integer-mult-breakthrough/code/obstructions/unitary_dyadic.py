#!/usr/bin/env python3
"""Exact finite discriminators for restricted Gaussian-dyadic unitary circuits.

This does not prove a multiplication lower bound or an exponent improvement.
Analytic extension beyond the finite enumerations is documented separately.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import json
from math import isqrt
from pathlib import Path
import subprocess
import sys
import time
import unittest


@dataclass(frozen=True)
class Gaussian:
    real: Q = Q(0)
    imag: Q = Q(0)

    def __add__(self, other):
        return Gaussian(self.real + other.real, self.imag + other.imag)

    def __neg__(self):
        return Gaussian(-self.real, -self.imag)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return Gaussian(self.real*other.real-self.imag*other.imag,
                        self.real*other.imag+self.imag*other.real)

    def conjugate(self):
        return Gaussian(self.real, -self.imag)

    def norm2(self):
        return self.real*self.real+self.imag*self.imag


ZERO = Gaussian()
ONE = Gaussian(Q(1))
ALPHA = Gaussian(Q(1, 2), Q(1, 2))


def identity(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def gram(matrix):
    n = len(matrix)
    if not n or any(len(row) != n for row in matrix):
        raise ValueError("Square nonempty matrices are required")
    return [[sum((matrix[i][j]*matrix[k][j].conjugate()
                  for j in range(n)), ZERO) for k in range(n)] for i in range(n)]


def require_unitary(matrix):
    if gram(matrix) != identity(len(matrix)):
        raise ValueError("The claimed circuit matrix is not unitary")


def dyadic_entropy(matrix):
    """Exact Phi when every nonzero norm squared is an integral power of two.

    Deliberately does not silently replace logarithms of other rationals with
    floating-point approximations. Negative values for nonunitary matrices are
    permitted solely to demonstrate the boundary of the unitary potential.
    """
    total = Q(0)
    for row in matrix:
        for value in row:
            p = value.norm2()
            if not p:
                continue
            a, b = p.numerator, p.denominator
            if (a & (a-1)) or (b & (b-1)):
                raise ValueError("This exact entropy replay requires power-of-two probabilities")
            log_p = a.bit_length()-b.bit_length()
            total -= p*log_p
    return total


def enumerate_rows(k):
    """Enumerate absolute integer four-square solutions, then count signs.

    Coordinate order is preserved. Restoring signs via multiplicities covers
    every row with denominator 2**k, including unreduced denominators.
    """
    if not 0 <= k <= 9:
        raise ValueError("Bounded finite enumeration requires 0 <= k <= 9")
    denominator = 1 << k
    target = denominator*denominator
    count = 0
    splits = set()
    exceptional = []
    for a in range(denominator+1):
        for b in range(isqrt(target-a*a)+1):
            remainder = target-a*a-b*b
            for c in range(isqrt(remainder)+1):
                d2 = remainder-c*c
                d = isqrt(d2)
                if d*d != d2:
                    continue
                coords = (a,b,c,d)
                count += 1 << sum(x != 0 for x in coords)
                split = Q(a*a+b*b, target)
                splits.add(split)
                if split not in (0, Q(1,2), 1):
                    exceptional.append(coords)
    expected = 8 if k == 0 else 24
    if count != expected or exceptional:
        raise ValueError("A finite enumeration contradicted the row classification")
    return {"denominator_power": k, "denominator": denominator,
            "signed_row_count": count,
            "possible_first_coordinate_norm2": sorted(map(str,splits)),
            "exceptional_rows": exceptional,
            "scope": "Exact exhaustive finite row enumeration; not an all-denominator proof"}


def butterfly(k):
    if not 1 <= k <= 6:
        raise ValueError("Bounded matrix replay requires 1 <= k <= 6")
    n = 1 << k
    matrix = identity(n)
    deltas = []
    for bit in range(k):
        for i in range(n):
            j = i ^ (1 << bit)
            if i > j:
                continue
            before = dyadic_entropy([matrix[i],matrix[j]])
            x,y = matrix[i],matrix[j]
            matrix[i] = [ALPHA*(a+b) for a,b in zip(x,y)]
            matrix[j] = [ALPHA*(a-b) for a,b in zip(x,y)]
            after = dyadic_entropy([matrix[i],matrix[j]])
            deltas.append(after-before)
    require_unitary(matrix)
    if any(v.norm2() != Q(1,n) for row in matrix for v in row):
        raise ValueError("Output is not flat")
    entropy = dyadic_entropy(matrix)
    if entropy != n*k or any(d != 2 for d in deltas):
        raise ValueError("Exact butterfly entropy or gate accounting failed")
    gate_count = n*k//2
    if gate_count != len(deltas):
        raise ValueError("Literal gate count mismatch")
    return {"n":n, "gaussian_dyadic_unitary":True, "flat_norm2":str(Q(1,n)),
            "final_entropy_bits":str(entropy), "literal_two_row_gates":gate_count,
            "max_entropy_increase":str(max(deltas)),
            "scope":"Exact finite normalized Walsh butterfly replay, including full Gram matrix"}


def negative_controls():
    scaled = [[Gaussian(Q(2)),ZERO],[ZERO,Gaussian(Q(1,2))]]
    before,after = dyadic_entropy(scaled),dyadic_entropy(identity(2))
    rejected = False
    try:
        require_unitary(scaled)
    except ValueError:
        rejected = True
    if not rejected or after-before != Q(15,2) or after-before <= 2:
        raise ValueError("Nonunitary boundary control failed")
    irrational_entropy = [[Gaussian(Q(3,4),Q(1,4))]]
    try:
        dyadic_entropy(irrational_entropy)
    except ValueError:
        pass
    else:
        raise ValueError("Non-power-of-two entropy should fail exact replay")
    return {"nonunitary_matrix_rejected":True,
            "unrestricted_two_row_inverse_scaling_entropy_jump":str(after-before),
            "unitary_gate_bound":2,
            "non_power_of_two_probability_rejected":True,
            "scope":"Counterexample to applying the unitary entropy bound to nonunitary basis changes"}


def task(spec):
    kind,arg = spec
    return {"kind":kind,"result":enumerate_rows(arg) if kind == "rows" else butterfly(arg)}


class Controls(unittest.TestCase):
    def test_scalar_ring(self):
        self.assertEqual(ALPHA*ALPHA,Gaussian(Q(0),Q(1,2)))
        self.assertEqual(ALPHA.norm2(),Q(1,2))

    def test_small_exact_rows(self):
        self.assertEqual(enumerate_rows(0)["signed_row_count"],8)
        self.assertEqual(enumerate_rows(2)["signed_row_count"],24)

    def test_normalized_butterfly(self):
        self.assertEqual(butterfly(2)["literal_two_row_gates"],4)

    def test_corrupted_butterfly_rejected(self):
        matrix = [[ALPHA,ALPHA],[ALPHA,ALPHA]]
        with self.assertRaises(ValueError):
            require_unitary(matrix)

    def test_scope_boundary(self):
        self.assertEqual(negative_controls()["unrestricted_two_row_inverse_scaling_entropy_jump"],"15/2")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--max-row-power",type=int,default=7)
    parser.add_argument("--max-butterfly-power",type=int,default=5)
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Controls)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if args.workers < 1 or not 0 <= args.max_row_power <= 9 or not 1 <= args.max_butterfly_power <= 6:
        parser.error("Invalid bounded search parameters")
    if args.output and args.output.exists():
        parser.error("Refusing to overwrite prior evidence")
    start = time.monotonic()
    specs = [("rows",k) for k in range(args.max_row_power+1)]
    specs += [("butterfly",k) for k in range(1,args.max_butterfly_power+1)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(task,specs))
    source = Path(__file__)
    report = {"status":"EXACT FINITE EVIDENCE", "workers":args.workers,
              "seed":None,"randomness":"None: exhaustive or deterministic tasks",
              "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "git_commit":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
              "python":sys.version,"duration_seconds":time.monotonic()-start,
              "cases":results,"negative_controls":negative_controls(),
              "not_proved":["integer-multiplication lower bound","new multiplication algorithm",
                            "kappa improvement","arbitrary nonunitary frame obstruction",
                            "all-denominator row classification by finite enumeration alone"]}
    encoded = json.dumps(report,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open("x",encoding="utf-8") as handle:
            handle.write(encoded)
    print(encoded)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError,OSError) as error:
        print(f"FAIL: {error}",file=sys.stderr)
        raise SystemExit(1)
