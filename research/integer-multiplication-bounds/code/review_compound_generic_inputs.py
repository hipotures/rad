#!/usr/bin/env python3
"""Independent exact generic-bit arithmetic for the new compound h53 graph.

This checker does not reconstruct the finite graph. Its certificate explicitly
keeps the separate finite and all-size transfer review as an input obligation.
No candidate selector or new characteristic producer is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import time

from review_parameter_audit import log_integer


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def logs(n):
    lower, upper = log_integer(n, 160)
    scale = 2**448
    lo = Q(lower.numerator * scale // lower.denominator, scale)
    hi = Q(-((-upper.numerator * scale) // upper.denominator), scale)
    require(lo <= lower <= upper <= hi, "Outward exact logarithm failed")
    return lo, hi


def reconstruct(row):
    h = row["h"]
    logical = row["final"]["logical"]
    c, q, links = logical["additions"], logical["partial_outputs"], row["final"]["links"]
    roles = c + q - links
    require(h == 53 and roles == 531483 == row["compiled_roles"] == row["final"]["roles"],
            "Wrong selected compound graph or register-retention budget")
    require(q == 3 * comb(h, 3), "Actual designated output count differs")
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2*N + 2*v*v*(roles+h)
    L = 3*v*v*h*h
    counts = dict(h=h, side_roles=roles, v=v, m=m, N=N, W=W, L=L,
                  D=N-2*L, s=W*m-N+2*L)
    raw = row["exact_counts"]
    for key in ("m", "N", "W", "L", "D", "s"):
        require(Q(raw[key]) == counts[key], "Actual physical count differs: " + key)
    total_rank = total_edges = 0
    for name, category in raw["categories"].items():
        histogram = {int(r): int(n) for r, n in category["rank_histogram"].items()}
        require(all(0 <= r <= m and n >= 0 for r, n in histogram.items()),
                "Invalid actual residual histogram: " + name)
        rank = sum(r*n for r, n in histogram.items())
        edges = sum(histogram.values())
        require(rank == category["rank_sum"] and edges == category["edge_count"],
                "Physical histogram framing differs: " + name)
        total_rank += rank
        total_edges += edges
    require(total_rank == counts["s"], "Full actual histogram total differs")
    G = 3*v*v*(4*(c+roles-v)+20*v)
    E = 64*(W+m+1)**3
    charged = 2*G*W*W+4*counts["s"]+4*W+4
    guard = row["literal_scalar_guard"]
    require(all(Q(guard[k]) == x for k, x in
                dict(G=G, E=E, depth=charged, slack=E-charged).items()) and E > charged,
            "Actual compound scalar count or coefficient guard differs")
    return counts, dict(additions=c, designated_outputs=q, retained_links=links,
                        roles=roles, actual_rank_mass=total_rank,
                        actual_edges=total_edges, scalar_gates=G, E=E,
                        literal_depth=charged, strict_guard_slack=E-charged)


def characteristic(base, protected):
    n = dict(base)
    h, v, m, R = (n[k] for k in ("h", "v", "m", "side_roles"))
    require(protected in (0, 1), "Only independently reviewed zero/one-star chart")
    n["L"] -= protected*3*v*v
    n["D"] += protected*6*v*v
    n["s"] -= protected*6*v*v
    require(n["s"] == n["W"]*m-n["D"] and 0 < n["D"] and n["s"] < m**5,
            "Modified exact physical budget fails")
    deficits = dict(middle=h*h, joined=2*h, data=h*h+h-1)
    copies = dict(middle=(R+h)*v*v, joined=(R+h)*v*v, data=2*n["N"])
    runs = {name: m-2*d for name, d in deficits.items()}
    family_ranks = {name: copies[name]*(m-deficits[name]) for name in deficits}
    hist = Counter()
    for name, r in runs.items():
        hist[r] += copies[name]
    credited = sum(r*c for r, c in hist.items())
    individual = n["s"]-credited
    require(0 < individual and sum(family_ranks.values()) < n["s"],
            "Changed credited families overlap or exhaust the rank budget")
    lm = logs(m)[1]
    log_data = {str(r): [str(x) for x in logs(r)] for r in hist}
    M = sum(r*c*Q(log_data[str(r)][0]) for r, c in hist.items())
    linear = n["s"]*lm-M
    quadratic = Q(n["s"], 2)*lm*lm
    require(linear > 0, "Normalized characteristic is not decreasing near zero")

    def gap(a):
        require(0 <= a*lm < 1, "Positive-exponential Taylor range fails")
        return n["D"]-a*linear-a*a*quadratic/(1-a*lm)

    scale = 10**24
    low, high = 0, 10**19
    require(gap(Q(high, scale)) < 0, "Root bracket is not discriminating")
    while high-low > 1:
        mid = (low+high)//2
        if gap(Q(mid, scale)) > 0:
            low = mid
        else:
            high = mid
    a = Q(low, scale)
    require(gap(a) > 0 >= gap(Q(low+1, scale)), "Strict rational saving bracket fails")
    largest = max(runs.values())
    depth = 1
    while m**depth <= 2*largest**depth:
        depth += 1
    require(depth == 487 and m**depth > 2*largest**depth
            and m**(depth-1) <= 2*largest**(depth-1), "Exact new halving degree differs")
    Wbits = n["W"].bit_length()
    require(2**(Wbits-1) <= n["W"] < 2**Wbits, "New wire-stock logarithm differs")
    product_coefficient = Q(Wbits*depth+41*272)*(2+Q(1,25))
    degree = 1000*(-(-product_coefficient.numerator//(1000*product_coefficient.denominator)))
    require(degree == 73000 and product_coefficient < degree, "Joint row product does not fit")
    return dict(protected_centers=protected, counts=n, saving=str(a), tau=str(1-a),
                kernel_dimensions=deficits, family_multiplicities=copies,
                family_ranks=family_ranks, grouped_runs=runs,
                long_run_histogram={str(r):c for r,c in sorted(hist.items())},
                long_grouped_rank=credited, individual_pivot_count=individual,
                log_m_upper=str(lm), log_intervals=log_data,
                rank_log_moment_lower=str(M), normalized_linear_upper=str(linear),
                normalized_quadratic_upper=str(quadratic), strict_gap=str(gap(a)),
                next_grid_point_nonpositive_gap=str(gap(Q(low+1,scale))),
                maximum_child=largest, halving_degree=depth, wire_log2_ceiling=Wbits,
                exact_joint_row_coefficient=str(product_coefficient), row_degree=degree,
                reservoir_slope=4*degree, log_terms=160, outward_dyadic_bits=448,
                giant_native_table_and_admissible_prime_materialized=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--protected-review", type=Path, required=True)
    parser.add_argument("--protected-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "Choose a fresh output path")
    start = time.monotonic()
    require(digest(args.candidate) == "26fb205b780ac5cab6d754be9b7e26c2480ae55f3c6140f3f6ff7fd69c7a91fa",
            "Frozen selected compound producer bytes differ")
    require(digest(args.protected_report) == "c096bf8b16a8e7871f8a44d8fd3c8ea9476f03d0142dfd9cd50b191a041781f9",
            "Written one-star all-size transfer changed")
    protected = json.loads(args.protected_review.read_text())
    require(protected["status"] == "PASS" and any(
        entry["h"] == 53 and entry["all_source_containments_and_normal_target_orthogonalities_exact"]
        for entry in protected["metric_inputs"]), "One-star review omits the new ground")
    candidate = json.loads(args.candidate.read_text())
    require(len(candidate["rows"]) == 1 and candidate["rows"][0]["checked"]["compiled_sha256"]
            == "ce76dd44ebe3f0e553850cb0fd90bebb783fef185935522c52df77d5e0421b17",
            "Wrong selected compound finite identity")
    n, budget = reconstruct(candidate["rows"][0])
    result = dict(status="PASS independent exact compound generic characteristic arithmetic",
                  campaign="20261007T222521Z", generated_utc=datetime.now(timezone.utc).isoformat(),
                  input_sha256={str(p):digest(p) for p in
                                (args.candidate,args.protected_review,args.protected_report)},
                  source_sha256=digest(Path(__file__)),
                  dependency_sha256={"review_parameter_audit.py":digest(Path(__file__).with_name("review_parameter_audit.py"))},
                  candidate_id=candidate["rows"][0]["candidate_id"],
                  compiled_sha256=candidate["rows"][0]["checked"]["compiled_sha256"],
                  actual_physical_budget=budget, variants=[characteristic(n,j) for j in (0,1)],
                  wall_seconds=time.monotonic()-start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitations=["Independent final finite reconstruction and complete transfer are separate obligations",
                               "Arithmetic does not instantiate the giant rational native table or new odd prime",
                               "Only zero and independently reviewed one-star variants are included",
                               "No complete multiplication exponent is claimed by this component"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    for row in result["variants"]:
        print("PASS",row["protected_centers"],row["saving"],row["row_degree"],flush=True)


if __name__ == "__main__":
    main()
