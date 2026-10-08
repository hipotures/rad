#!/usr/bin/env python3
"""Probe fixed-grid band LU against independently evaluated Gaussian windows."""
import argparse
from decimal import Decimal as D, localcontext
import hashlib
import json
from pathlib import Path
import random
import time

from fixed_grid_band_lu import factor, apply

PI = ("3.141592653589793238462643383279502884197169399375105820974944592307816406286"
      "208998628034825342117067982148086513282306647093844609550582231725359408128"
      "48111745028410270193852110555964462294895493038196")


def q(j, s, t):
    return (2*t*j+s)//(2*s)


def run_case(s, t, u, m, w, target, origin, seed):
    start = time.time()
    with localcontext() as context:
        context.prec = 200
        pi = D(PI)
        rho = D(t)/D(s)
        theta = rho-1
        assert D(u)*theta >= 1
        if origin == "edge":
            j0 = min(range(s), key=lambda j: rho*D(j)-D(q(j,s,t)))
        else:
            j0 = s-10
        bits = target+24+2*(w+1).bit_length()
        scale = 1 << bits
        matrix = [[D(0)]*m for _ in range(m)]
        a = [[0]*m for _ in range(m)]
        for i in range(m):
            row = j0+i
            qi = q(row,s,t)
            for j in range(m):
                column = j0+j
                beta = rho*D(column)-D(q(column,s,t))
                value = D(0)
                for image in (-1,0,1):
                    n = D(q(column,s,t)+image*t-qi)
                    value += (-pi*D(u)*n*(n+2*beta)).exp()
                matrix[i][j] = value
                if i == j:
                    a[i][j] = scale
                elif abs(i-j) <= w:
                    a[i][j] = int((value*scale).to_integral_value(rounding="ROUND_FLOOR"))
        perturbation = max(sum(abs(matrix[i][j]-D(a[i][j])/D(scale)) for j in range(m)) for i in range(m))
        assert perturbation < D(2)**(-target-12)
        l, upper, reciprocal, setup = factor(a,w,bits)
        rng = random.Random(seed)
        rhs_vectors = [[scale*int(i == j) for i in range(m)] for j in (0,1,m//2,m-1)]
        rhs_vectors.extend([[rng.randrange(-16,17)*(scale//16) for _ in range(m)] for _ in range(8)])
        maximum = D(0)
        ops = 0
        for rhs in rhs_vectors:
            x, ops = apply(l,upper,reciprocal,rhs,w,bits)
            actual = [D(v)/D(scale) for v in x]
            residual = max(abs(sum((matrix[i][j]*actual[j] for j in range(m)), D(0))-D(rhs[i])/D(scale)) for i in range(m))
            maximum = max(maximum,residual)
            assert 2*residual < D(2)**(-target)
        # A diagonal approximation misses an actual near-edge neighbor.
        diagonal_residual = matrix[0][1]
        assert diagonal_residual > D(2)**(-target)
        alias_bound = D(4)*(-pi*D(u)*D((s-m)*(s-m-1))).exp()
        return {"s":s,"t":t,"u":u,"origin":j0,"window_size":m,"half_bandwidth":w,
                "target_bits":target,"work_bits":bits,"decimal_digits":200,"seed":seed,
                "basis_and_random_rhs":len(rhs_vectors),"matrix_perturbation_row_norm":str(perturbation),
                "maximum_actual_Gaussian_residual":str(maximum),"solution_error_bound":str(2*maximum),
                "target":str(D(2)**(-target)),"remote_alias_row_bound":str(alias_bound),
                "diagonal_negative_residual":str(diagonal_residual),
                "setup_operations":setup,"online_operations":ops,"elapsed_seconds":time.time()-start}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    cases=[run_case(*c) for c in ((113,128,8,32,4,64,"wrap",2026100841),
                                  (10000,10004,2500,32,1,256,"edge",2026100842),
                                  (1009,1024,68,64,2,192,"edge",2026100843))]
    dependency=Path(__file__).with_name("fixed_grid_band_lu.py")
    result={"status":"Gaussian_fixed_grid_controls_pass","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "factor_source_sha256":hashlib.sha256(dependency.read_bytes()).hexdigest(),"cases":cases,
            "scope":"Numerical Gaussian residuals include retained cyclic images; exact generic rounding checks are separate"}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"rhs_probes":sum(c["basis_and_random_rhs"] for c in cases)}))


if __name__=="__main__":
    main()
