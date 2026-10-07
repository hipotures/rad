#!/usr/bin/env python3
"""Certify the aligned-pairing circuit against the immutable paired baseline.

The finite checks and unchanged transfer prove a conditional witness. The full
upstream multiplication theorem remains assumed. Kappa is a strict rational
value below the recipe's limiting margin, not a practical running-time claim.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
import json
from math import comb
from pathlib import Path
import time

from finite_block_search import GroupUnion, install_reference, make_block_class


def certificate(reference: str):
    install_reference(reference)
    from certify import Parameters, certify_parameters, network
    from dag_network import exact_invocation, shared_scalar_model
    from paired_network import guard_certificate
    from reuse_network import triple_matching
    from search_network import log_integer_bounds

    cls = make_block_class()
    factory = lambda n: cls(n, (2,), 4, 0)
    c = GroupUnion(50, factory, "paired", 109)
    result = {
        "status": "Conditional finite-circuit improvement; unchanged upstream interfaces remain assumptions",
        "upstream_reference": {
            "url": "https://github.com/CrocSwap/integer-mult-bounds",
            "commit": "bcd4ebde8692383539f8a48734e5fbf3a18a32c2",
        },
        "configuration": {
            "h": 50,
            "sizes": [2],
            "base": 4,
            "combine": 0,
            "point_order": "all global pairs other than the common point's pair, followed by its mate",
            "seed": 109,
            "seed_scope": "Payload checks only; the circuit is deterministic",
        },
        "global": c.verify(),
        "frames": c.verify_frames(),
    }
    assert result["global"]["roles"] == 494250
    assert result["global"]["additions"] == 435450
    assert result["global"]["merged_additions"] == 55200
    h = 50
    R = result["global"]["roles"]
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2 * N + 2 * v * v * (R + h)
    L = 3 * v * v * h * h
    D = N - 2 * L
    eta = Q(D, W * m)
    result["bit_counts"] = {
        k: str(z)
        for k, z in dict(h=h, v=v, m=m, N=N, side_roles_per_invocation=R, W=W, L=L, D=D, s=W*m-D, eta=eta).items()
    }
    a = Q(305, 10**11)
    ac = Q(1, 10**11)
    log_bound = Q(11737, 1000)
    lo, hi = log_integer_bounds(m)
    assert hi < log_bound
    assert eta > a * log_bound
    complex_counts = network(h)
    assert complex_counts["eta_c"] > ac * log_bound
    assert 2 * complex_counts["Lc"] < N
    beta, epsilon = Q(999, 1000), Q(199, 1000)
    limiting = epsilon * beta * a * a
    kappa = Q(999, 1000) * limiting
    p = Parameters(1-a, 1-ac, epsilon, beta*a, 1-(1+beta)*a*a/2, 1-beta*a*a, kappa, beta=beta, delta=Q(1, 10000), C1=2)
    result["witness"] = certify_parameters(
        p,
        generalized_beta=True,
        strict_margin=True,
        layout_model="nonadjacent",
        guard_model="stopping",
        assembly_model="tight-gaussian",
    )
    assert Q(result["witness"]["minimum_margin"]) == limiting
    result["arithmetic"] = {
        "bit_saving": str(a),
        "complex_saving": str(ac),
        "log_m_upper": str(log_bound),
        "log_enclosure": [str(lo), str(hi)],
        "bit_deficit_slack": str(eta-a*log_bound),
        "complex_deficit_slack": str(complex_counts["eta_c"]-ac*log_bound),
        "strict_kappa": str(kappa),
        "kappa_over_pinned_dyadic_59": str(kappa*2**59),
        "limiting_margin_over_pinned_limiting_margin": str(limiting/Q(272158569, 156250000000000000000000000)),
    }
    result["stopped_guard"] = guard_certificate(h, beta)
    triples, images = triple_matching(h)
    assert len(triples) == v and len(set(images)) == v
    assert all(len(set(t).intersection(triples[j])) == 1 for t, j in zip(triples, images))
    result["stage_matching"] = {
        "h": h,
        "triples": v,
        "bijection": True,
        "every_match_intersects_in_one": True,
        "source": "Unchanged pinned triple_matching; every image checked",
    }
    result["small_checks"] = []
    for small_h in (6, 8):
        small = GroupUnion(small_h, factory, "paired", 109)
        program = small.program()
        item = {
            "h": small_h,
            "map": small.verify_small_expansion(),
            "frames": small.verify_frames(),
            "every_dirty_input_basis": [exact_invocation(small_h, inv, program) for inv in (False, True)],
            "complete_three_stage_exchange": [shared_scalar_model(small_h, seed, program) for seed in (1, 109)],
        }
        result["small_checks"].append(item)
    result["transfer"] = {
        "scalar_schedule": "L,J,L^-1,R0,V,G,R0,L,J,L^-1,G,V",
        "dirty_scratch_identity": "JLz+JL(z+Vx)=JLVx; inverse mixers and final V restore arbitrary z",
        "forward_frame": "D_U where U is the nondegenerate source-indicator span",
        "reverse_frame": "D_(U^perp)",
        "nondegeneracy": "All source triples in every node share a point i; norm is sum_(j!=i) u_j^2",
        "central_decreasing_dimension": str(L),
        "absolute_label_change": str(W*m-2*N+2*L),
        "source_correction_rank": str(N),
        "total_edge_rank": str(W*m-N+2*L),
        "all_role_endpoints": "Unchanged data endpoints; each surviving auxiliary role has endpoints 0 and I_m and is restored",
        "stage_join": "Unchanged nested E<=H from intersection-one triple matching",
        "scope": "Specialization of the pinned source-span/complement-frame and full auxiliary-sharing transfer; no altered computational model",
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    start = time.monotonic()
    result = certificate(args.reference)
    result["elapsed_seconds"] = time.monotonic() - start
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({
        "output": args.output,
        "roles": result["global"]["roles"],
        "kappa": result["arithmetic"]["strict_kappa"],
        "kappa_over_pinned_dyadic_59": result["arithmetic"]["kappa_over_pinned_dyadic_59"],
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
