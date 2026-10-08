#!/usr/bin/env python3
"""Exact fixed-grid controls for bounded-precision, no-pivot banded LU.

All stored values are integers on one P-bit grid. No Fraction LU with growing
denominators is used. Residuals against the original matrix use exact integers.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import time


def build(m, w, bits, seed):
    rng = random.Random(seed)
    scale = 1 << bits
    a = [[0]*m for _ in range(m)]
    for i in range(m):
        a[i][i] = scale
        for j in range(max(0, i-w), min(m, i+w+1)):
            if i != j:
                a[i][j] = rng.randrange(-3, 4)*(scale//(256*w))
    assert max(sum(abs(v) for j, v in enumerate(row) if i != j) for i, row in enumerate(a)) < scale//16
    return a


def rownorm(a, scale):
    return F(max(sum(abs(v) for v in row) for row in a), scale)


def factor(a, w, bits):
    m = len(a)
    scale = 1 << bits
    l = [[0]*m for _ in range(m)]
    u = [row[:] for row in a]
    count = 0
    for k in range(m):
        l[k][k] = scale
        assert u[k][k] > scale//2
        for i in range(k+1, min(m, k+w+1)):
            multiplier = (u[i][k]*scale)//u[k][k]
            l[i][k] = multiplier
            u[i][k] = 0
            count += 1
            for j in range(k+1, min(m, k+w+1)):
                u[i][j] -= (multiplier*u[k][j])//scale
                count += 1
    reciprocal = [(scale*scale)//u[i][i] for i in range(m)]
    assert rownorm(u, scale) < 2
    assert rownorm(l, scale) < 1+4*w
    return l, u, reciprocal, count


def apply(l, u, reciprocal, rhs, w, bits):
    m = len(rhs)
    scale = 1 << bits
    y = rhs[:]
    count = 0
    for i in range(m):
        numerator = sum(l[i][j]*y[j] for j in range(max(0, i-w), i))
        y[i] -= numerator//scale
        count += min(i, w)
    x = y[:]
    for i in range(m-1, -1, -1):
        numerator = sum(u[i][j]*x[j] for j in range(i+1, min(m, i+w+1)))
        temporary = y[i]-numerator//scale
        x[i] = (reciprocal[i]*temporary)//scale
        count += min(m-1-i, w)+1
    return x, count


def factor_residual(a, l, u, scale):
    m = len(a)
    return F(max(sum(abs(sum(l[i][k]*u[k][j] for k in range(m))-a[i][j]*scale)
                         for j in range(m)) for i in range(m)), scale*scale)


def run_case(m, w, bits, seed):
    start = time.time()
    a = build(m, w, bits, seed)
    scale = 1 << bits
    l, u, reciprocal, setup_ops = factor(a, w, bits)
    fr = factor_residual(a, l, u, scale)
    assert fr < F(16*m*(w+1)**2, scale)
    rng = random.Random(seed+1)
    rhs_cases = [[scale*int(i == j) for i in range(m)] for j in (0, m//2, m-1)]
    rhs_cases.extend([[rng.randrange(-16, 17)*(scale//16) for _ in range(m)] for _ in range(9)])
    maximum = F(0)
    ops = 0
    for rhs in rhs_cases:
        x, ops = apply(l, u, reciprocal, rhs, w, bits)
        residual = F(max(abs(sum(a[i][j]*x[j] for j in range(m))-rhs[i]*scale) for i in range(m)), scale*scale)
        maximum = max(maximum, residual)
        # Inverse row norm <=16/15<2. This is a rigorous residual-derived error
        # bound, independent of agreement with the factorization implementation.
        assert 2*residual < F((1 << 16)*m*(w+1)**4, scale)
    # Coarse precision is an informative failing approximation, not silently
    # accepted when the exact integer-grid residual exceeds its target.
    poor_bits = 3
    poor_scale = 1 << poor_bits
    poor_a = [[(v*poor_scale)//scale for v in row] for row in a]
    poor_l, poor_u, poor_reciprocal, _ = factor(poor_a, w, poor_bits)
    poor_rhs = [poor_scale*int(i == 0) for i in range(m)]
    poor_x, _ = apply(poor_l, poor_u, poor_reciprocal, poor_rhs, w, poor_bits)
    poor_error = F(max(abs(sum(a[i][j]*poor_x[j] for j in range(m))-poor_rhs[i]*scale) for i in range(m)), scale*poor_scale)
    assert poor_error > F(1, 1 << 12)
    return {"m": m, "half_bandwidth": w, "fractional_bits": bits, "seed": seed,
            "rhs_probes": len(rhs_cases), "setup_multiply_round_updates": setup_ops,
            "online_operations_per_rhs": ops, "L_row_norm": str(rownorm(l, scale)),
            "U_row_norm": str(rownorm(u, scale)), "factor_residual_row_norm": str(fr),
            "maximum_original_residual": str(maximum),
            "solution_error_bound_from_residual": str(2*maximum),
            "claimed_solution_bound": str(F((1 << 16)*m*(w+1)**4, scale)),
            "coarse_precision_negative_residual": str(poor_error),
            "elapsed_seconds": time.time()-start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    cases = [run_case(*c) for c in ((32,2,24,2026100831), (48,4,40,2026100832),
                                   (64,6,64,2026100833), (96,8,96,2026100834))]
    result = {"status": "fixed_grid_residual_controls_pass", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cases": cases, "scope": "Generic row-dominant band systems; cyclic windows require an explicit lifted ordering and remote-alias perturbation"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "rhs_probes": sum(c["rhs_probes"] for c in cases)}))


if __name__ == "__main__":
    main()
