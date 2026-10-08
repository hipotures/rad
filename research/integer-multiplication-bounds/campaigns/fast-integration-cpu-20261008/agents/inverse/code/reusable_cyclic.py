#!/usr/bin/env python3
"""Independent exact/rounded controls for reusable cyclic boundary factors.

No upstream code is imported. Rational near-identity cyclic block matrices
exercise the changed interface, not the full Gaussian multiplication theorem.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import time


def zeros(n, m):
    return [[F(0) for _ in range(m)] for _ in range(n)]


def norm(a):
    return max(sum(abs(x) for x in row) for row in a)


def matvec(a, x):
    return [sum((u*v for u, v in zip(row, x)), F(0)) for row in a]


def sub(x, y):
    return [u-v for u, v in zip(x, y)]


def quantize(x, bits):
    scale = 1 << bits
    # Rounding down, including negative values; absolute error is < 2^-bits.
    return F((x.numerator * scale) // x.denominator, scale)


def qmatrix(a, bits):
    return [[quantize(x, bits) for x in row] for row in a]


def lu(a):
    n = len(a)
    u = [row[:] for row in a]
    l = zeros(n, n)
    count = 0
    for k in range(n):
        if not u[k][k]:
            raise ValueError("zero pivot")
        l[k][k] = F(1)
        for i in range(k+1, n):
            if not u[i][k]:
                continue
            c = u[i][k] / u[k][k]
            l[i][k] = c
            u[i][k] = F(0)
            for j in range(k+1, n):
                if u[k][j]:
                    u[i][j] -= c*u[k][j]
                    count += 1
    return l, u, count


def solve(factors, b, bits=None):
    l, u, _ = factors
    n = len(b)
    y = b[:]
    operations = 0
    for i in range(n):
        y[i] -= sum((l[i][j]*y[j] for j in range(i) if l[i][j]), F(0))
        operations += sum(bool(l[i][j]) for j in range(i))
        if bits is not None:
            y[i] = quantize(y[i], bits)
    x = y[:]
    for i in range(n-1, -1, -1):
        x[i] -= sum((u[i][j]*x[j] for j in range(i+1, n) if u[i][j]), F(0))
        operations += sum(bool(u[i][j]) for j in range(i+1, n))
        x[i] /= u[i][i]
        operations += 1
        if bits is not None:
            x[i] = quantize(x[i], bits)
    return x, operations


def build_case(blocks, width, seed):
    rng = random.Random(seed)
    n = blocks*width
    c = zeros(n, n)
    for i in range(n):
        c[i][i] = F(1)
        block = i//width
        # Independently directed corner blocks; cyclic coupling is indispensable.
        for target in ((block-1) % blocks, block, (block+1) % blocks):
            for local in range(width):
                j = target*width+local
                if i != j:
                    c[i][j] = F(rng.choice((-3, -2, -1, 1, 2, 3)), 128*width)
    gap = min(abs(c[i][i])-sum(abs(c[i][j]) for j in range(n) if j != i)
              for i in range(n))
    assert gap > F(9, 10)
    b = [row[:] for row in c]
    for i in range(width):
        for j in range(n-width, n):
            b[i][j] = F(0)
            b[j][i] = F(0)
    selected = list(range(width))+list(range(n-width, n))
    u = [[c[i][j]-b[i][j] for j in selected] for i in range(n)]
    bf = lu(b)
    z = zeros(n, 2*width)
    for col in range(2*width):
        vector, _ = solve(bf, [row[col] for row in u])
        for i, value in enumerate(vector):
            z[i][col] = value
    k = [[z[i][j]+F(i == selected[j]) for j in range(2*width)] for i in selected]
    kf = lu(k)
    assert norm(u) < F(1, 10)
    assert norm(z) < F(1, 9)
    return c, bf, selected, z, kf, gap


def apply(factors, selected, z, border, b, bits=None):
    y, count = solve(factors, b, bits)
    rhs = [y[i] for i in selected]
    small, small_count = solve(border, rhs, bits)
    correction = matvec(z, small)
    x = sub(y, correction)
    if bits is not None:
        x = [quantize(v, bits) for v in x]
    count += small_count + len(z)*len(selected)
    return x, count


def fraction_string(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def run_case(case):
    start = time.time()
    blocks, width, seed, probes = case
    c, bf, selected, z, kf, gap = build_case(blocks, width, seed)
    n = len(c)
    rng = random.Random(seed+19)
    inputs = [[F(i == j) for i in range(n)] for j in (0, width-1, n//2, n-1)]
    inputs.extend([[F(rng.randrange(-16, 17), 16) for _ in range(n)] for _ in range(probes)])
    max_errors = {p: F(0) for p in (24, 48, 96)}
    max_residuals = max_errors.copy()
    opcounts = []
    exact_pass = 0
    for b in inputs:
        x, ops = apply(bf, selected, z, kf, b)
        assert matvec(c, x) == b, "exact residual"
        assert max(abs(v) for v in x) <= 1/gap
        exact_pass += 1
        opcounts.append(ops)
        for bits in max_errors:
            rounded_bf = (qmatrix(bf[0], bits), qmatrix(bf[1], bits), bf[2])
            rounded_kf = (qmatrix(kf[0], bits), qmatrix(kf[1], bits), kf[2])
            approx, _ = apply(rounded_bf, selected, qmatrix(z, bits), rounded_kf, b, bits)
            error = max(abs(v) for v in sub(approx, x))
            residual = max(abs(v) for v in sub(matvec(c, approx), b))
            max_errors[bits] = max(max_errors[bits], error)
            max_residuals[bits] = max(max_residuals[bits], residual)
            # A deliberately loose independently checked finite control.
            assert error < F(64*n*n, 1 << bits)
    # Negative control drops the cyclic correction, and must fail for e0.
    uncorrected, _ = solve(bf, inputs[0])
    negative_residual = max(abs(v) for v in sub(matvec(c, uncorrected), inputs[0]))
    assert negative_residual > 0
    catalogue_entries = (sum(bool(v) for row in bf[0] for v in row)
                         + sum(bool(v) for row in bf[1] for v in row)
                         + sum(bool(v) for row in z for v in row)
                         + sum(bool(v) for row in kf[0] for v in row)
                         + sum(bool(v) for row in kf[1] for v in row))
    return {"blocks": blocks, "width": width, "seed": seed, "dimension": n,
            "gap": fraction_string(gap), "exact_rhs_passes": exact_pass,
            "factor_multiply_subtracts": bf[2]+kf[2],
            "online_operations_per_rhs": max(opcounts),
            "catalogue_nonzero_entries": catalogue_entries,
            "rounding_error_max": {str(p): fraction_string(v) for p, v in max_errors.items()},
            "rounding_residual_max": {str(p): fraction_string(v) for p, v in max_residuals.items()},
            "rounding_error_scaled": {str(p): float(v*(1 << p)) for p, v in max_errors.items()},
            "negative_control_residual": fraction_string(negative_residual),
            "elapsed_seconds": time.time()-start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", choices=("quick", "extended"), default="quick")
    args = parser.parse_args()
    cases = [(9, 2, 202610081, 4), (10, 3, 202610082, 4),
             (8, 4, 202610083, 4), (7, 5, 202610084, 4)]
    if args.profile == "extended":
        cases = [(12, 3, 202610091, 16), (10, 4, 202610092, 16),
                 (8, 5, 202610093, 16), (7, 6, 202610094, 16)]
    start = time.time()
    completed = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_case, c) for c in cases]
        for future in as_completed(futures):
            result = future.result()
            completed.append(result)
            print(json.dumps({"done": result["dimension"], "width": result["width"],
                              "seconds": result["elapsed_seconds"]}), flush=True)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps({"status": "partial", "cases": completed}, indent=2)+"\n")
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output = {"status": "pass", "scope": "independent rational cyclic reuse controls",
              "source_sha256": source_hash, "workers": args.workers,
              "elapsed_seconds": time.time()-start, "cases": sorted(completed, key=lambda c: c["width"])}
    args.output.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({"status": "pass", "seconds": output["elapsed_seconds"],
                      "exact_rhs_passes": sum(c["exact_rhs_passes"] for c in completed)}), flush=True)


if __name__ == "__main__":
    main()
