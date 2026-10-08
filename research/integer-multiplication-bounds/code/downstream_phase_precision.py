#!/usr/bin/env python3
"""Exact symbolic arithmetic audit of the phase inverse error allowances.

For every integer p>=101, p^k<=2^(kp). Positive sums are bounded term
by term after this substitution. The certificate records the affine
exponent inequalities, so no finite floating-point threshold substitutes
for the universal argument.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from downstream_gaussian import check_sources, require


def affine_strict(slope: int, intercept: int, rhs: int = 0) -> dict:
    """Certify slope*p+intercept<rhs for every integer p>=101."""
    require(slope<=0, "Affine bound is not nonincreasing")
    endpoint=101*slope+intercept
    require(endpoint<rhs, "Universal affine exponent threshold failed")
    return {"slope":slope,"intercept":intercept,"at_p_101":endpoint,
            "strict_upper_exponent":rhs,"domain":"All integer p>=101"}


def checks() -> dict:
    # Terms use their absolute coefficient as an explicit binary power.
    local=affine_strict(8+1-32,14)  # 2^14 p 2^(8p) < 2^(32p)p^8.
    global_terms={
        "1024*p^2*LA":affine_strict(32+10-64,10,-2),
        "512*p^2*SB":affine_strict(22-64,69,-2),
        "2048*p^4*eta":affine_strict(4-64,11,-2),
    }
    # Normalize the final absolute error by 2^(-p-10).
    final_terms={
        "algorithm":affine_strict(64+64+1-32768,10,-2),
        "structured_rounding_transfer":affine_strict(3+16+1-32768,22,-2),
        "infinite_lattice_tail_transfer":affine_strict(2-45,15,-2),
    }
    gap_terms={
        "structured_rounding_times_8p":affine_strict(2+16-32768,10,-2),
        "lattice_tail_times_8p":affine_strict(1-46,3,-2),
        "Schur_rounding_times_16p":affine_strict(2-32768,7,0),
    }
    factor_terms={
        "rounded_L_neumann":affine_strict(2-32768,7,-1),
        "rounded_U_neumann":affine_strict(4-32768,12,-1),
        "effective_A_neumann":affine_strict(4-32768,12,-1),
        # Here p^3<=p^20 and p^7<=p^20 are used directly. Applying
        # p^k<=2^(kp) with a negative exponent would reverse the bound.
        "inverse_perturbation_below_boundary_allowance":affine_strict(0,10-60),
        "cyclic_error_below_boundary_allowance":affine_strict(0,33-60),
    }
    # LA itself is small enough that all completed intermediate norms can
    # be enlarged by one, rather than by an exponential similarity factor.
    intermediate={
        "3LA_below_one":affine_strict(32+8-32768,2),
        "boundary_LA_error_below_half":affine_strict(32+9-32768,5,-1),
        "boundary_SB_error_below_half":affine_strict(21-32768,65,-1),
    }
    return {"status":"PASS universal integer-p exponent certificates",
            "domain":"All integer p>=101; p^k<=2^(kp)",
            "work_fractional_bits_per_p":32768,
            "downward_exponential_error":"<4 eta for a_hat and G_hat",
            "local_generator_chain":local,"completed_map_composition":global_terms,
            "target_error_after_normalization":final_terms,
            "diagonal_dominance_perturbations":gap_terms,
            "rounded_inverse_factor_neumann_bounds":factor_terms,
            "completed_intermediate_norm_allowances":intermediate,
            "positive_sum_rule":"Three terms, each <1/4 of its target, have sum <3/4; two terms have sum <1/2.",
            "scope":"Certifies stated scalar inequality allowances; matrix identities, norms and tape cost require separate proof and exact checks."}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic(); source=Path(__file__)
    result={"generated_at":datetime.now(timezone.utc).isoformat(),
            "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
            "campaign_deadline":"2026-10-08T08:25:21Z",
            "provenance":check_sources(args.upstream),
            "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
            "precision_checks":checks()}
    result["elapsed_seconds"]=time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS universal p>=101 phase rounding, composition, DD and precision allowances")


if __name__=="__main__":
    main()
