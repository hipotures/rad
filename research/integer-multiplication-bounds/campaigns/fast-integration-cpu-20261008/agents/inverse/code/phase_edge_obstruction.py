#!/usr/bin/env python3
"""Exact toy and independent Gaussian controls for uniform tensor inverse packing.

The exact rational family is a counterexample to deriving inverse halo size
from only the forward bandwidth and a full-tensor chirp reserve. The Gaussian
controls show the same mechanism close to a physical phase edge.
"""
import argparse
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

PI = ("3.141592653589793238462643383279502884197169399375105820974944592307816406286"
      "208998628034825342117067982148086513282306647093844609550582231725359408128"
      "48111745028410270193852110555964462294895493038196")


def solve(a, rhs):
    n = len(a)
    m = [row[:] for row in a]
    b = rhs[:]
    for k in range(n):
        assert m[k][k] != 0
        for i in range(k+1, n):
            if not m[i][k]:
                continue
            factor = m[i][k]/m[k][k]
            for j in range(k+1, n):
                m[i][j] -= factor*m[k][j]
            b[i] -= factor*b[k]
            m[i][k] = D(0)
    x = [D(0)]*n
    for i in range(n-1, -1, -1):
        x[i] = (b[i]-sum((m[i][j]*x[j] for j in range(i+1, n)), D(0)))/m[i][i]
    return x


def exact_case(dimension, core, halo):
    # M = diag(2^(j^2)) (I + S/2) diag(2^(-j^2)).
    # Upper-neighbor M[j,j+1] = 2^(-2j-2), row gap >= 3/4.
    # Its inverse M^-1[0,h] is (-1)^h * 2^(-h*(h+1)).
    q = dimension*core*core
    h = halo+1
    error = F(1, 1 << (h*(h+1)))
    target = F(1, 1 << q)
    needed = next(k for k in range(q+1) if k*(k+1) >= q)
    assert error > target
    return {"dimension": dimension, "core": core, "halo": halo,
            "precision_Q": q, "first_omitted_displacement": h,
            "exact_omitted_coefficient": f"1/2^{h*(h+1)}",
            "exact_target": f"1/2^{q}", "necessary_halo_lower_bound": needed-1,
            "necessary_halo_over_core": (needed-1)/core,
            "full_tensor_chirp_bits": dimension*core*core,
            "status": "uniform_small_halo_rejected"}


def gaussian_case(q, tensor_dimension):
    with localcontext() as context:
        context.prec = 190
        pi = D(PI)
        # s=10000,t=10004; beta_c=-1/2 exactly at c=1250.
        s, t, c, u = 10000, 10004, 1250, D(2500)
        rho = D(t)/D(s)
        theta = rho-D(1)
        # A tensor reserve d*pi*u*theta*core^2 <= Q*ln(2).
        core = int((D(q)*D(2).ln()/(D(tensor_dimension)*pi*u*theta)).sqrt())
        core = max(1, core)
        # Even a halo as large as one whole core fails here. This is stronger
        # than rejecting only the constant-volume halo core/d.
        halo = core
        h = halo+1
        # Enough trailing rows to isolate the finite principal inverse.
        size = max(16, h+8)
        positions = list(range(c, c+size))
        qindex = [(t*j*2+s)//(2*s) for j in positions]
        beta = [rho*D(j)-D(qj) for j, qj in zip(positions, qindex)]
        assert beta[0] == -D(1)/D(2)
        a = []
        for i in range(size):
            row = []
            for j in range(size):
                n = D(qindex[j]-qindex[i])
                exponent = n*(n+2*beta[j])
                row.append((-pi*u*exponent).exp())
            a.append(row)
        rhs = [D(j == h) for j in range(size)]
        x = solve(a, rhs)
        coefficient = abs(x[0])
        target = D(2)**(-q)
        nearest_path = (-pi*u*theta*D(h*(h+1))).exp()
        residual = max(abs(sum((a[i][j]*x[j] for j in range(size)), D(0))-rhs[i])
                       for i in range(size))
        assert coefficient > target*D(10)**10
        assert abs(coefficient-nearest_path) < coefficient*D(10)**(-120)
        assert residual < D(10)**(-175)
        return {"Q": q, "tensor_dimension": tensor_dimension, "core": core,
                "halo": halo, "omitted_displacement": h, "s": s, "t": t,
                "phase_start": c, "u": "2500", "theta": "1/2500",
                "principal_dimension": size, "decimal_precision": context.prec,
                "absolute_omitted_coefficient": str(coefficient),
                "target": str(target), "coefficient_over_target": str(coefficient/target),
                "nearest_path_relative_difference": str(abs(coefficient-nearest_path)/coefficient),
                "direct_solve_residual": str(residual),
                "scope": "finite principal Gaussian block; aliases not included"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    exact = [exact_case(d, core, core//d) for d, core in ((4, 16), (8, 32), (16, 64), (32, 128))]
    gaussian = [gaussian_case(q, d) for q, d in ((512, 4), (2048, 8), (8192, 16), (32768, 32))]
    output = {"status": "scoped_obstruction_verified", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "exact_cases": exact, "gaussian_controls": gaussian,
              "limitation": "Rejects a uniform halo inference, not all tensor inverse constructions"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({"status": output["status"], "exact_cases": len(exact), "gaussian_controls": len(gaussian)}))


if __name__ == "__main__":
    main()
