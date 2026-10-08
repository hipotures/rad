#!/usr/bin/env python3
"""Independent exact geometry and numerical cyclic Gaussian locality controls.

Uses only the Python standard library. No historical or upstream producer is
imported. Numeric tests are controls; the general proof is in the report.
"""
import argparse
from decimal import Decimal as D, localcontext
import hashlib
import json
from pathlib import Path
import time

PI = ("3.141592653589793238462643383279502884197169399375105820974944592307816406286"
      "208998628034825342117067982148086513282306647093844609550582231725359408128"
      "48111745028410270193852110555964462294895493038196")


def q_beta_numerator(j, s, t):
    q = (2*t*j+s)//(2*s)
    return q, 2*t*j-2*q*s


def exact_geometry(s, t):
    k = t-s
    assert 0 < 4*k <= s
    horizon = s//k
    hs = sorted({1, 2, 3, 8, 16, 31, 63, max(1, horizon//2), horizon,
                 horizon+1, s-1, s, s+1, 2*s+3})
    counts = {"weighted_identity": 0, "phase_gain": 0,
              "regular_gain": 0, "nearest_exponent": 0, "far_exponent": 0}
    equality = {"phase_gain": 0, "weighted_identity": 0}
    delta_den = 16
    for j in range(s):
        qj, bj = q_beta_numerator(j, s, t)
        for sign in (-1, 1):
            for h0 in hs:
                h = sign*h0
                ql, bl = q_beta_numerator(j+h, s, t)
                n = ql-qj
                # X = n*(n+2 beta_(j+h)); its numerator on denominator s.
                xnum = n*(n*s+bl)
                weighted = 4*k*xnum-(bl*bl-bj*bj)
                lower = 4*k*t*h*h
                assert weighted >= lower
                equality["weighted_identity"] += weighted == lower
                counts["weighted_identity"] += 1
                gain = bj*bj-bl*bl
                if k*h0 <= s:
                    bound = 4*k*h0*(s-k*h0)
                    assert gain <= bound
                    equality["phase_gain"] += gain == bound
                    counts["phase_gain"] += 1
                if abs(bj)*delta_den <= s*(delta_den-2) and k*h0*delta_den <= s:
                    bound_num = (delta_den-2)*4*k*h0*s-delta_den*4*k*k*h0*h0
                    assert delta_den*gain <= bound_num
                    counts["regular_gain"] += 1
                if h0 == 1:
                    assert xnum >= 2*k
                    counts["nearest_exponent"] += 1
                if h0 >= 2:
                    assert xnum >= s*h0*(h0-1)
                    counts["far_exponent"] += 1
    return {"s": s, "t": t, "horizon": horizon, "displacements": hs,
            "counts": counts, "equalities": equality}


def lu(a):
    n = len(a)
    u = [row[:] for row in a]
    l = [[D(0)]*n for _ in range(n)]
    for k in range(n):
        l[k][k] = D(1)
        for i in range(k+1, n):
            if u[i][k] == 0:
                continue
            c = u[i][k]/u[k][k]
            l[i][k] = c
            u[i][k] = D(0)
            for j in range(k+1, n):
                u[i][j] -= c*u[k][j]
    return l, u


def solve(factors, column):
    l, u = factors
    n = len(l)
    y = [D(i == column) for i in range(n)]
    for i in range(n):
        y[i] -= sum((l[i][j]*y[j] for j in range(i)), D(0))
    x = y[:]
    for i in range(n-1, -1, -1):
        x[i] = (x[i]-sum((u[i][j]*x[j] for j in range(i+1, n)), D(0)))/u[i][i]
    return x


def cyclic_numeric(s, t, digits):
    start = time.time()
    with localcontext() as context:
        context.prec = digits
        pi = D(PI)
        theta = D(t-s)/D(s)
        u = D((s+t-s-1)//(t-s))
        assert u*theta >= 1
        q = [(2*t*j+s)//(2*s) for j in range(s)]
        beta = [D(t)*D(j)/D(s)-D(q[j]) for j in range(s)]
        a = [[D(0)]*s for _ in range(s)]
        for i in range(s):
            for j in range(s):
                value = D(0)
                for image in (-1, 0, 1):
                    n = D(q[j]+image*t-q[i])
                    value += (-pi*u*n*(n+2*beta[j])).exp()
                a[i][j] = value
        row_e = max(sum((abs(a[i][j]-D(i == j)) for j in range(s)), D(0)) for i in range(s))
        assert row_e < D(1)/D(16)
        factors = lu(a)
        inv = [[D(0)]*s for _ in range(s)]
        residual = D(0)
        for j in range(s):
            vector = solve(factors, j)
            for i, value in enumerate(vector):
                inv[i][j] = value
            # Every basis solve gets three independent original-matrix residual
            # rows, including rows crossing the physical period boundary.
            for i in {0, j, s-1}:
                res = abs(sum((a[i][k]*vector[k] for k in range(s)), D(0))-D(i == j))
                residual = max(residual, res)
        horizons = [r for r in (1, 2, 3, 4, 6, 8) if D(r) <= 1/(2*theta)]
        tails = []
        for r in horizons:
            tail = max(sum((abs(inv[i][j]) for j in range(s)
                            if min((j-i) % s, (i-j) % s) > r), D(0)) for i in range(s))
            bound = D(24)*(-D(3)*u*theta*D(r*r)).exp()
            assert tail < bound
            tails.append({"R": r, "actual_max_row_tail": str(tail), "proved_bound": str(bound),
                          "actual_over_bound": str(tail/bound)})
        assert residual < D(10)**(-(digits-10))
        # Omitted images have |h|>=s in their nearest representatives. The
        # direct Gaussian exponent bound is vastly below the numeric precision.
        omitted_alias_bound = D(4)*(-pi*u*D(s*(s-1))).exp()
        return {"s": s, "t": t, "u": str(u), "theta": str(theta),
                "decimal_digits": digits, "row_E_norm": str(row_e),
                "basis_probes": s, "sampled_original_residual_max": str(residual),
                "omitted_alias_row_bound": str(omitted_alias_bound),
                "tail_controls": tails, "elapsed_seconds": time.time()-start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-size", type=int, default=113)
    parser.add_argument("--digits", type=int, default=160)
    args = parser.parse_args()
    start = time.time()
    exact = [exact_geometry(s, t) for s, t in ((113, 128), (1009, 1024), (4093, 4096),
                                             (10000, 10004), (2401, 2402))]
    output = {"status": "partial", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "exact_geometry": exact, "cyclic_numeric": []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({"geometry_pass": sum(sum(c["counts"].values()) for c in exact)}), flush=True)
    for s, t in ((61, 64), (113, 128), (257, 261)):
        if s > args.max_size:
            continue
        result = cyclic_numeric(s, t, args.digits)
        output["cyclic_numeric"].append(result)
        args.output.write_text(json.dumps(output, indent=2)+"\n")
        print(json.dumps({"cyclic_done": s, "seconds": result["elapsed_seconds"]}), flush=True)
    output["status"] = "controls_pass"
    output["elapsed_seconds"] = time.time()-start
    output["scope"] = "exact geometric inequalities and cyclic inverse controls, not formal verification"
    args.output.write_text(json.dumps(output, indent=2)+"\n")


if __name__ == "__main__":
    main()
