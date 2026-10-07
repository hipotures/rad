#!/usr/bin/env python3
"""Exact near-optimal parameters for the audited blocked Gaussian model.

This is parameter tuning after the substantive Gaussian improvements.  It
does not claim a new scalar construction.  Physical role counts supplied by
other branches require their independent circuit, frame and rank proofs.
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

from downstream_gaussian import (BASELINE_KAPPA, check_sources,
                                 log_integer_bounds, log_ratio_bounds,
                                 network_counts, require)


def saving_enclosure(eta: Q, m: int) -> dict:
    require(0 < eta < Q(1,2), "Invalid network deficit")
    ln_lo,ln_hi = log_ratio_bounds(1/(1-eta),terms=8)
    lm_lo,lm_hi = log_integer_bounds(m)
    lower,upper = ln_lo/lm_hi,ln_hi/lm_lo
    require(0 < lower < upper < 1, "Saving enclosure failed")
    # Deliberate fixed rational strict slack without decimal rounding.
    chosen = lower*(1-Q(1,2**128))
    require(ln_lo-chosen*lm_hi > 0, "No strict primitive exponent gap")
    return {"negative_log_deficit_lower":ln_lo,
            "negative_log_deficit_upper":ln_hi,
            "log_m_lower":lm_lo,"log_m_upper":lm_hi,
            "saving_lower":lower,"saving_upper":upper,
            "chosen_saving":chosen,"strict_primitive_gap":ln_lo-chosen*lm_hi}


def root_enclosure(a: Q, b: Q, bits: int = 128) -> tuple[Q,Q]:
    """Small root of a*b*x^2-(b+a^2)*x+a^2=0, exactly enclosed."""
    def f(x: Q) -> Q:
        return a*b*x*x-(b+a*a)*x+a*a
    lo,hi = Q(0),Q(1)
    require(f(lo) > 0 and f(hi) < 0, "Balance root outside (0,1)")
    for _ in range(bits):
        middle = (lo+hi)/2
        if f(middle) > 0:
            lo = middle
        elif f(middle) < 0:
            hi = middle
        else:
            # Exact equality still needs strictly larger x for leaf slack.
            lo = middle
    require(f(lo) >= 0 and f(hi) < 0, "Root bracket lost its signs")
    return lo,hi


def compact_lower(x: Q, places: int = 30) -> Q:
    denominator = 10**places
    numerator = x.numerator*denominator//x.denominator
    value = Q(numerator,denominator)
    if value == x:
        value -= Q(1,denominator)
    require(0 < value < x, "Compact rational lacks strict slack")
    return value


def as_strings(data):
    if isinstance(data,Q):
        return str(data)
    if isinstance(data,dict):
        return {k:as_strings(v) for k,v in data.items()}
    if isinstance(data,list):
        return [as_strings(v) for v in data]
    return data


def rational_decimal_lower(value: Q, places: int) -> str:
    numerator = value.numerator*10**places//value.denominator
    digits = str(numerator).zfill(places+1)
    return digits[:-places]+"."+digits[-places:]


def witness(roles: int) -> dict:
    n = network_counts(50,roles)
    v,m,N = n["v"],n["m"],n["N"]
    zc = comb(47,3)+3*47
    Wc = 2*N+3*v*v*(v*zc+51)
    Lc = 3*v*v*51*50
    sc = Wc*m-2*N+2*Lc
    eta_c = Q(Wc*m-sc,Wc*m)
    require(2*Lc < N and 2 <= sc < m**5,"Retained complex construction failed")
    eb,ec = saving_enclosure(n["eta"],m),saving_enclosure(eta_c,m)
    a,b = eb["chosen_saving"],ec["chosen_saving"]
    x_lo,x_hi = root_enclosure(a,b)
    x,beta = x_hi,1-x_hi
    tau,sigma = 1-a,1-b
    optimum_c = a*beta/(tau+a*beta)
    c = optimum_c*(1-Q(1,2**32))
    q = a*c
    lamp = 1-q
    packed_threshold = tau*(1+c/beta)
    lam = (lamp+packed_threshold)/2
    epsilon = (1-Q(1,2**20))/2
    delta = (Q(1,2)-epsilon)/4
    margins = {"g1":1-epsilon*(1+c),"g2":epsilon*c*a,
               "g3":epsilon*(1-lamp),"g4":a*(1-epsilon),
               "g5":Q(1,2)-delta-epsilon,"g6":1-delta-epsilon,"g7":epsilon}
    G = min(margins.values())
    kappa = compact_lower(G)
    slacks = {
        "bit_primitive":eb["strict_primitive_gap"],
        "complex_primitive":ec["strict_primitive_gap"],
        "lambda_above_tau":lam-tau,"lambda_above_sigma":lam-sigma,
        "packed_recurrence":lam-packed_threshold,
        "lambda_prime_above_lambda":lamp-lam,
        "leaf_cost":lamp-(sigma+beta*(1-sigma)),
        "guard":1-2*epsilon,"gaussian_cost":Q(1,2)-delta-epsilon,
        "prime_interval_growth":1-2*epsilon,"gamma_sublinear":Q(1,2)-epsilon,
        "prefix_cost":1-epsilon*(1+c),"scalar_cost":1-delta-epsilon,
        "K_smaller_than_ell":1-epsilon-epsilon*c,
        "absorption":G-kappa,
    }
    require(Q(9,10) <= beta < 1,"Guard stopping range failed")
    for name,value in slacks.items():
        require(value > 0,f"Nonpositive strict slack {name}")
    require(kappa > Q(5,2**60),"Near-optimal witness regressed")
    require(G == margins["g2"] == margins["g3"],"Wrong limiting margins")
    # Upper bound with the best primitive savings consistent with their
    # exact enclosures, covering ALL beta,c,lambda,lambda-prime choices
    # in the stated original recurrence and Gaussian normalization model.
    upper_a,upper_b = eb["saving_upper"],ec["saving_upper"]
    upper_x_lo,upper_x_hi = root_enclosure(upper_a,upper_b)
    upper_kappa = upper_b*upper_x_hi/2
    require(kappa < upper_kappa < Q(1,2**57),"Unexpected dyadic ceiling")
    # b^(1/2-epsilon)>=256 guarantees the Gaussian condition b^gap>184.
    # Verify logarithmic cutoff exactly without constructing its huge bytes.
    gamma_b_log2_cutoff = int(8/(Q(1,2)-epsilon))
    require(Q(1,2)-epsilon == Q(8,gamma_b_log2_cutoff),"Gamma cutoff exponent failed")
    require(184 < 2**8,"Gaussian ceiling constant failed")
    result = {
        "status":"CONDITIONAL strict near-optimal parameters for the reviewed blocked-Gaussian transfer",
        "finite_status":"Pinned upstream graph" if roles==509194 else "Requires independent campaign physical-role circuit/frame/rank certificate",
        "physical_side_roles":roles,"counts":n,
        "retained_complex_counts":{"W":Wc,"s":sc,"L":Lc,"eta":eta_c},
        "bit_saving_enclosure":eb,"complex_saving_enclosure":ec,
        "balance_root_interval":[x_lo,x_hi],
        "parameters":{"tau":tau,"sigma":sigma,"a_bit":a,"a_complex":b,
                      "beta":beta,"epsilon":epsilon,"delta":delta,"C1":2,
                      "c":c,"lambda":lam,"lambda_prime":lamp,"kappa":kappa},
        "constraint_slacks":slacks,"margins":margins,"minimum_margin":G,
        "kappa_decimal_lower":rational_decimal_lower(kappa,30),
        "kappa_ratio_to_baseline":kappa/BASELINE_KAPPA,
        "kappa_ratio_decimal_lower":rational_decimal_lower(kappa/BASELINE_KAPPA,12),
        "model_kappa_upper":upper_kappa,
        "achieved_fraction_of_model_upper":kappa/upper_kappa,
        "gamma_cutoff":"b >= 2^"+str(gamma_b_log2_cutoff),
        "classification":"Parameter optimization after substantive Gaussian proof changes; exact log saving spends existing finite-network margin.",
        "scope":"Original packed-layer recurrence, reviewed blocked Gaussian cost and normalization, retained complex construction, fixed h50 bit role count; not a ceiling for other inverse/scaling algorithms or circuits.",
    }
    return as_strings(result)


def scaling_examples() -> dict:
    examples = []
    lists = [[Q(1,8)]*4,[Q(1,20),Q(1,10),Q(1,5),Q(1,3)],
             [Q(1,100),Q(1,200),Q(1,300),Q(1,4)]]
    for theta in lists:
        product = Q(1)
        for t in theta:
            product *= 1+t
        require(product < 2 and sum(theta,Q(0)) < 1,"Capacity setup violated")
        reciprocals = sum((1/t for t in theta),Q(0))
        require(reciprocals*sum(theta,Q(0)) >= len(theta)**2,"Cauchy lower bound failed")
        require(reciprocals > len(theta)**2,"Quadratic scaling obstruction failed")
        examples.append({"theta":theta,"T_over_S":product,"sum_reciprocals":reciprocals,
                         "gamma_strict_lower":2*reciprocals})
    return as_strings({"status":"PASS exact nonuniform-width examples",
                       "universal_proof":"T/S=product(1+theta_i)<2 gives sum(theta_i)<1; alpha_i²theta_i>1 and Cauchy imply gamma=2sum(alpha_i²)>2d².",
                       "examples":examples})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--roles",type=int,nargs="+",default=[509194,494250,487650])
    args = parser.parse_args()
    start = time.monotonic()
    source = Path(__file__)
    result = {"generated_at":datetime.now(timezone.utc).isoformat(),
              "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
              "campaign_deadline":"2026-10-08T08:25:21Z",
              "provenance":check_sources(args.upstream),
              "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
              "witnesses":[witness(roles) for roles in args.roles],
              "scaling_obstruction":scaling_examples()}
    result["elapsed_seconds"] = time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for w in result["witnesses"]:
        print("PASS",w["physical_side_roles"],"roles; kappa",w["parameters"]["kappa"],
              "ratio >=",w["kappa_ratio_decimal_lower"])


if __name__ == "__main__":
    main()
