#!/usr/bin/env python3
"""Exact candidate assembly for the phase-cell Gaussian inverse hypothesis.

The arithmetic checker does not certify its new analytic interfaces.
Independent phase/GS/Schur, precision and fixed-tape proofs are required.
"""

from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import BASELINE_KAPPA,ceil_q,check_sources,network_counts,require
from downstream_parameter_optimum import (as_strings,compact_lower,
                                          rational_decimal_lower,root_enclosure,
                                          saving_enclosure)


def witness(ground: int,roles: int,mode: str) -> dict:
    n = network_counts(ground,roles)
    vc,mc = 19600,125000
    Nc = vc**3
    Wc = 2*Nc+3*vc*vc*(vc*(comb(47,3)+3*47)+51)
    Lc = 3*vc*vc*51*50
    sc = Wc*mc-2*Nc+2*Lc
    require(2*Lc<Nc and 2<=sc<mc**5,"Retained complex guard premise failed")
    eb,ec = saving_enclosure(n["eta"],n["m"]),saving_enclosure(Q(2*Nc-2*Lc,Wc*mc),mc)
    a,b = eb["chosen_saving"],ec["chosen_saving"]
    xlo,xhi = root_enclosure(a,b)
    beta = 1-xhi
    tau,sigma = 1-a,1-b
    c = a*beta/(tau+a*beta)*(1-Q(1,2**32))
    q = a*c
    lp = 1-q
    threshold = tau*(1+c/beta)
    lam = (lp+threshold)/2
    B = sc+64*(Wc+mc+1)**3
    if mode=="conservative":
        eps,r,delta,C1,C0 = Q(9,10),Q(1,20),Q(1,1000),Q(11,10),256*mc*B**2
        require(beta>=Q(999,1000),"Conservative phase guard stopping range failed")
        zeta = Q(1,20)
    else:
        zeta = Q(1,2**30)
        C1 = 5-4*beta+zeta
        eps = (1-Q(1,2**20))/C1
        r = (1-eps)/2
        delta = r/8
        C0 = 32*mc*B**2*(1+1/zeta)
    g5_local,g5_boundary = 1-eps-delta,r-delta
    margins = {"g1":1-eps*(1+c),"g2":eps*a*c,"g3":eps*q,
               "g4":a*(1-eps),"g5":min(g5_local,g5_boundary),
               "g6":1-delta-eps,"g7":eps}
    G = min(margins.values())
    kappa = compact_lower(G)
    slacks = {"bit_primitive":eb["strict_primitive_gap"],
              "complex_primitive":ec["strict_primitive_gap"],
              "lambda_above_tau":lam-tau,"lambda_above_sigma":lam-sigma,
              "packed_recurrence":lam-threshold,"lambda_prime_above_lambda":lp-lam,
              "leaf_cost":lp-(sigma+beta*(1-sigma)),
              "guard":1-eps*C1,"guard_piece_exponent":C1-(5-4*beta+zeta),
              "local_convolution_cost":g5_local,"boundary_solve_cost":g5_boundary,
              "gamma_sublinear":1-eps-r,"cell_larger_than_gaussian_band":eps-(1-r)/2,
              "prime_interval_and_line_growth":1-eps,"alpha_power":r,
              "prefix_cost":1-eps*(1+c),"scalar_cost":1-delta-eps,
              "K_smaller_than_ell":1-eps-eps*c,"absorption":G-kappa}
    # At the optimized guard the exponent is chosen exactly; all substantive
    # strict conditions retain positive slack, while this non-strict identity
    # is independently certified.
    require(slacks.pop("guard_piece_exponent")>=0,"Guard exponent insufficient")
    for name,value in slacks.items():
        require(value>0,"Nonpositive phase-transfer slack "+name)
    require(Q(9,10)<=beta<1 and 0<r<=Q(1,3),"Parameter family left audited domain")
    require(G==margins["g2"]==margins["g3"],"Unexpected phase limiting margin")
    _,ux = root_enclosure(eb["saving_upper"],ec["saving_upper"])
    upper = ec["saving_upper"]*ux/(1+4*ux)
    require(kappa<upper,"Phase guard-family ceiling failed")
    gamma_log_b = ceil_q(Q(7)/(1-eps-r))
    k = ceil_q(1/r)
    width_log_b = 16*k*k+1
    guard_log_b = ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1))
    cell_gap = eps-(1-r)/2
    cell_log_b = ceil_q(Q(9)/cell_gap)
    require(gamma_log_b*(1-eps-r)>=7,"Gamma cutoff failed")
    require(Q(1,k)<=r,"Logarithmic alpha cutoff comparison failed")
    require(guard_log_b*(1-eps*C1)>=(2*ceil_q(C0)).bit_length(),
            "Full guard-constant cutoff failed")
    require(cell_log_b*cell_gap>=9,"Full phase-cell cutoff failed")
    return as_strings({
        "status":"CANDIDATE exact assembly for phase-cell inverse; requires full independent analytic review",
        "mode":mode,"bit_ground":ground,"physical_side_roles":roles,"counts":n,
        "retained_complex_counts":{"ground":50,"m":mc,"W":Wc,"s":sc,"L":Lc},
        "bit_saving_enclosure":eb,"complex_saving_enclosure":ec,
        "balance_root_interval":[xlo,xhi],
        "parameters":{"tau":tau,"sigma":sigma,"a_bit":a,"a_complex":b,
                      "beta":beta,"c":c,"lambda":lam,"lambda_prime":lp,
                      "epsilon":eps,"alpha_squared_power":r,"delta":delta,
                      "guard_piece_allowance":zeta,"C1":C1,"C0":C0,"kappa":kappa},
        "constraint_slacks":slacks,"margins":margins,"minimum_margin":G,
        "gaussian_margins":{"local_convolution":g5_local,"boundary_solve":g5_boundary},
        "kappa_decimal_lower":rational_decimal_lower(kappa,30),
        "kappa_ratio_to_baseline":kappa/BASELINE_KAPPA,
        "kappa_ratio_decimal_lower":rational_decimal_lower(kappa/BASELINE_KAPPA,12),
        "strictly_supports_2^-57":kappa>Q(1,2**57),
        "guard_family_model_upper":upper,"achieved_fraction_of_upper":kappa/upper,
        "gamma_log2_b_cutoff":gamma_log_b,
        "logarithmic_alpha_log2_b_cutoff":width_log_b,
        "full_guard_log2_b_cutoff":guard_log_b,
        "full_phase_cell_log2_b_cutoff":cell_log_b,
        "common_log2_b_cutoff":max(gamma_log_b,width_log_b,guard_log_b,cell_log_b),
        "additional_eventual_cutoffs":["BHP prime threshold and 12*d²<x^(19/40)",
                                        "original retained interfaces"],
        "proof_obligations":["exact phase-cell conjugation and downward/structured rounding",
                             "Gohberg-Semencul inverse, bounded generators and local packing precision",
                             "boundary Schur DD, bandwidth, rounded LU and cyclic correction",
                             "O(p)-bit internal magnitude, error and fixed-tape cost",
                             "sharper guard, BHP primes, final scaling and integer recovery",
                             "separate finite role/circuit/frame/restoration/rank proof",
                             "unchanged upstream complete multiplication theorem assumption"],
        "scope":"Candidate phase-Gaussian transfer, original packed recurrence, stated guard family, retained h50 complex primitive, independently supplied bit roles."})


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--ground",type=int,default=50)
    parser.add_argument("--roles",type=int,nargs="+",default=[509194,494250,487650])
    args=parser.parse_args(); start=time.monotonic(); source=Path(__file__)
    result={"generated_at":datetime.now(timezone.utc).isoformat(),
            "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
            "campaign_deadline":"2026-10-08T08:25:21Z","provenance":check_sources(args.upstream),
            "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
            "witnesses":[witness(args.ground,roles,mode) for mode in ["conservative","optimized"] for roles in args.roles]}
    result["elapsed_seconds"]=time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for w in result["witnesses"]:
        print("PASS arithmetic candidate",w["mode"],w["physical_side_roles"],
              "roles; kappa",w["parameters"]["kappa"],"ratio >=",w["kappa_ratio_decimal_lower"])


if __name__=="__main__":
    main()
