#!/usr/bin/env python3
"""Exact composed witnesses for the reviewed reusable Gaussian LU transfer.

This changes the scalar inverse, guard estimate, and prime-interval proof.
It retains the original packed recurrence and fixed-tape model.  Supplied
finite role counts require their separate construction/frame/rank proofs.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import BASELINE_KAPPA,check_sources,network_counts,require
from downstream_parameter_optimum import (as_strings,compact_lower,
                                          rational_decimal_lower,root_enclosure,
                                          saving_enclosure)


def witness(ground: int,roles: int) -> dict:
    n = network_counts(ground,roles)
    v_c,m_c = 19600,125000
    N_c = v_c**3
    z_c = comb(47,3)+3*47
    W_c = 2*N_c+3*v_c*v_c*(v_c*z_c+51)
    L_c = 3*v_c*v_c*51*50
    s_c = W_c*m_c-2*N_c+2*L_c
    eta_c = Q(W_c*m_c-s_c,W_c*m_c)
    require(2*L_c < N_c and 2 <= s_c < m_c**5,"Complex spare/guard premise failed")
    eb,ec = saving_enclosure(n["eta"],n["m"]),saving_enclosure(eta_c,m_c)
    a,b = eb["chosen_saving"],ec["chosen_saving"]
    x_lo,x_hi = root_enclosure(a,b)
    beta = 1-x_hi
    tau,sigma = 1-a,1-b
    c = a*beta/(tau+a*beta)*(1-Q(1,2**32))
    q = a*c
    lamp = 1-q
    packed_threshold = tau*(1+c/beta)
    lam = (lamp+packed_threshold)/2
    epsilon,r,delta,C1 = Q(2,3)-Q(1,2**20),Q(1,3),Q(1,2**22),Q(3,2)
    margins = {"g1":1-epsilon*(1+c),"g2":epsilon*c*a,
               "g3":epsilon*q,"g4":a*(1-epsilon),
               "g5":Q(1,2)+r/2-delta-epsilon,
               "g6":1-delta-epsilon,"g7":epsilon}
    G = min(margins.values())
    kappa = compact_lower(G)
    slacks = {
        "bit_primitive":eb["strict_primitive_gap"],
        "complex_primitive":ec["strict_primitive_gap"],
        "lambda_above_tau":lam-tau,"lambda_above_sigma":lam-sigma,
        "packed_recurrence":lam-packed_threshold,
        "lambda_prime_above_lambda":lamp-lam,
        "leaf_cost":lamp-(sigma+beta*(1-sigma)),
        "guard":1-C1*epsilon,"guard_stopping_range":beta-Q(15,16),
        "gaussian_cost":Q(1,2)+r/2-delta-epsilon,
        "gamma_sublinear":1-epsilon-r,
        "prime_interval_and_line_growth":1-epsilon,
        "prefix_cost":1-epsilon*(1+c),"scalar_cost":1-delta-epsilon,
        "K_smaller_than_ell":1-epsilon-epsilon*c,
        "alpha_power_positive":r,"alpha_below_sqrt_p":1-r,
        "absorption":G-kappa,
    }
    for name,value in slacks.items():
        require(value > 0,"Nonpositive new-transfer slack "+name)
    require(G == margins["g2"] == margins["g3"],"Wrong limiting new margins")
    upper_a,upper_b = eb["saving_upper"],ec["saving_upper"]
    _,upper_x_hi = root_enclosure(upper_a,upper_b)
    upper_kappa = Q(2,3)*upper_b*upper_x_hi
    require(kappa < upper_kappa,"Invalid new model ceiling")
    gamma_b_log2_cutoff = int(7/(1-epsilon-r))
    require(1-epsilon-r == Q(7,gamma_b_log2_cutoff),"Gamma cutoff exponent failed")
    require(4*17 < 2**7,"Gamma ceiling constant failed")
    guard_B = s_c+64*(W_c+m_c+1)**3
    return as_strings({
        "status":"CONDITIONAL strict witness for the reusable banded inverse proof; requires independent analytic review",
        "bit_ground":ground,"physical_side_roles":roles,"counts":n,
        "retained_complex_counts":{"ground":50,"m":m_c,"W":W_c,"s":s_c,"L":L_c,"eta":eta_c},
        "bit_saving_enclosure":eb,"complex_saving_enclosure":ec,
        "balance_root_interval":[x_lo,x_hi],
        "parameters":{"tau":tau,"sigma":sigma,"a_bit":a,"a_complex":b,
                      "beta":beta,"c":c,"lambda":lam,"lambda_prime":lamp,
                      "epsilon":epsilon,"delta":delta,"alpha_squared_power":r,
                      "C1":C1,"C0":128*m_c*guard_B**2,"kappa":kappa},
        "constraint_slacks":slacks,"margins":margins,"minimum_margin":G,
        "kappa_decimal_lower":rational_decimal_lower(kappa,30),
        "kappa_ratio_to_baseline":kappa/BASELINE_KAPPA,
        "kappa_ratio_decimal_lower":rational_decimal_lower(kappa/BASELINE_KAPPA,12),
        "model_kappa_upper":upper_kappa,
        "model_upper_below_2^-57":upper_kappa < Q(1,2**57),
        "achieved_fraction_of_model_upper":kappa/upper_kappa,
        "gamma_cutoff":"b >= 2^"+str(gamma_b_log2_cutoff),
        "other_eventual_cutoffs":["Baker-Harman-Pintz Theorem1 threshold and 12*d^2<x^(19/40)",
                                 "p^(1/3)>=ceil(log2(8p))","s>2*(ceil(sqrt(16p/u))+2)",
                                 "original finite-network, recurrence and input-size eventual cutoffs"],
        "replacement_obligations":{
            "Gaussian":"Sharp row bound, O(p)-bit reusable exact-rational LU/Woodbury precomputation, residual error proof",
            "guard":"Same C0, sharper C1=3/2 for beta>=15/16 using actual O(log d) piece count",
            "prime":"BHP short intervals replace the old log(r)>8d sufficient condition",
            "finite":"Physical roles supplied; independent rational frames, scalar restoration, ranks and endpoints required",
            "upstream":"Complete multiplication theorem and unaffected tape interfaces remain assumed"},
        "legacy_constraints_replaced":{
            "1-2epsilon":1-2*epsilon,
            "reason":"This negative old sufficient condition is not used: prime existence follows BHP, and gamma uses d*(2u+O(log p))."},
        "scope":"Original packed recurrence; reusable banded Gaussian inverse; new guard/prime transfer; retained complex h50 and supplied bit counts; fixed finite-alphabet one-dimensional tapes."})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--ground",type=int,default=50)
    parser.add_argument("--roles",type=int,nargs="+",default=[509194,494250,487650])
    args = parser.parse_args()
    start = time.monotonic()
    source = Path(__file__)
    result = {"generated_at":datetime.now(timezone.utc).isoformat(),
              "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
              "campaign_deadline":"2026-10-08T08:25:21Z",
              "provenance":check_sources(args.upstream),
              "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
              "witnesses":[witness(args.ground,r) for r in args.roles]}
    result["elapsed_seconds"] = time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for w in result["witnesses"]:
        print("PASS",w["bit_ground"],w["physical_side_roles"],"roles; kappa",w["parameters"]["kappa"],
              "ratio >=",w["kappa_ratio_decimal_lower"])


if __name__ == "__main__":
    main()
