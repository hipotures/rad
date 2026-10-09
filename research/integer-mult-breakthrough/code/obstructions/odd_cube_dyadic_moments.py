#!/usr/bin/env python3
"""Dyadic odd-cube feature decoders and a scoped direct-formation budget.

Exact scalar matrices are not physical circuits. Optimistic center/cap
profiles remain hypothetical. The all-p k3 direct-fanout bound assumes
the stated fixed stock, pure carried helpers and monotone singleton roots.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb, factorial
from pathlib import Path
import sys
import time

TOPIC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOPIC / "code/complex"))
import characteristic


def kernel(k, r):
    t = (k - 1) // 2
    value = Q(1)
    for j in range(t):
        value *= Q(r - 1, 2) - j
    return value / factorial(t)


def decoder(k):
    t = (k - 1) // 2
    values = [kernel(k, r) for r in range(k + 1)]
    grid = 1 << (2 * t)
    if any((x * grid).denominator != 1 for x in values):
        raise AssertionError("The complete integer-intersection grid is not dyadic")
    differences, coefficients = values[:], []
    for j in range(t + 1):
        coefficients.append(differences[0])
        differences = [b - a for a, b in zip(differences, differences[1:])]
    if any(differences):
        raise AssertionError("The feature degree is not t")
    for r, expected in enumerate(values):
        actual = sum(coefficients[j] * comb(r, j) for j in range(min(r, t) + 1))
        if actual != expected:
            raise AssertionError("The Newton feature endpoint is wrong")
    if values[k] != 1 or any(values[r] for r in range(1, k, 2)):
        raise AssertionError("The diagonal/odd-intersection endpoint changed")
    # The top-degree-only symmetric embedding is just one compression.
    # Its non-dyadic entries do not prove that every compression needs them.
    top_only = [coefficients[j] / comb(k - j, t - j) for j in range(t + 1)]
    odd_parts = []
    for value in top_only:
        d = value.denominator
        while d % 2 == 0:
            d //= 2
        odd_parts.append(d)
    return {"k": k, "degree": t, "grid_denominator": grid,
            "Newton_coefficients": [str(c) for c in coefficients],
            "all_intersection_values": [str(v) for v in values],
            "symmetric_top_only_odd_denominator_parts": odd_parts,
            "top_only_not_a_universal_compression_lower_bound": True}


def full_scalar_matrix(k, p):
    t = (k - 1) // 2
    grid = 1 << (2 * t)
    spec = decoder(k)
    coeffs = [int(Q(x) * grid) for x in spec["Newton_coefficients"]]
    labels = [sum(1 << (2 * pair + ((bits >> j) & 1))
                  for j, pair in enumerate(support))
              for support in combinations(range(p), k) for bits in range(1 << k)]
    feature_count = sum((1 << j) * comb(p, j) for j in range(t + 1))
    columns = []
    for source in labels:
        selected = [b for b in range(2 * p) if source >> b & 1]
        columns.append([(sum(1 << b for b in subset), coeffs[j])
                        for j in range(t + 1) for subset in combinations(selected, j)])
    checks, missing_total_rejected = 0, False
    for target in labels:
        for source, entries in zip(labels, columns):
            actual = sum(c for feature, c in entries if feature & target == feature)
            expected = kernel(k, (source & target).bit_count())
            if Q(actual, grid) != expected:
                raise AssertionError("A complete source/target scalar column failed")
            if Q(actual - coeffs[0], grid) != expected:
                missing_total_rejected = True
            checks += 1
    if not missing_total_rejected:
        raise AssertionError("Omitting the paid total feature was accepted")
    return {"k": k, "p": p, "sources": len(labels),
            "designated_feature_roots_including_total": feature_count,
            "complete_scalar_matrix_entries": checks,
            "all_input_and_output_labels_retained": True,
            "omitted_total_feature_rejected": True,
            "physical_address_and_dirty_phase_word_not_executed": True}


def release_minimum(k):
    n = 1 << k
    a, b = (k - 2) * n, 2 * (k - 1)
    l0 = a // b
    candidates = {0, n, l0, min(n, l0 + 1)}
    costs = [(2 * l + 2 * max(k * n // 2 - n - (k - 1) * l, 0), l)
             for l in candidates]
    best, l = min(costs)
    continuous = Q((k - 2) * n, k - 1)
    if best < continuous:
        raise AssertionError("The integral release bound fell below its convex minimum")
    return {"k": k, "cube_sources": n, "minimum_extra_rank_per_core": best,
            "one_minimizing_released_source_count": l,
            "continuous_lower_bound_per_source": str(Q(k - 2, k - 1)),
            "three_core_extra_per_source": str(Q(3 * best, n)),
            "excludes_all_positive_deficits_below_2v": 3 * best >= 2 * n,
            "scope": "Pure per-source carried helpers, direct scalar writes, monotone literal singleton buckets; mixing/copies/new births excluded"}


def optimistic_profile(k, p):
    h, v = 2 * p, (1 << k) * comb(p, k)
    roots = sum((1 << j) * comb(p, j) for j in range((k - 1) // 2 + 1))
    # This is a lower moment than the synchronized chronology: each root
    # advances in one rank-h call and then pays its rank-h complete copy.
    center = Counter({1: v, h - 1: v, h: 2 * roots})
    source, target = Counter(), Counter()
    for r in (k - 1, h - k - 1, 1):
        source[r] += v
    for r in (k, h - k - 1):
        target[r] += v
    children = Counter()
    for hist in (center, source, target):
        for r, count in hist.items():
            if r:
                children[r] += 3 * count
    children[2] += 2 * v
    raw = 0
    for j in range(max(0, 2 * k - p), k):
        count = (1 << j) * comb(k, j) * comb(p, k)
        raw += count
        pieces = [k + 1, h - k - 1] if j == 0 else [k + 1 - j, j - 1, h - k]
        for r in pieces:
            if r:
                children[r] += 3 * count
    W = 3 * v + roots + raw
    deficit = 2 * v - 3 * roots * h
    rank = sum(r * count for r, count in children.items())
    if rank != 3 * h * W - deficit or max(children) > h:
        raise AssertionError("The full optimistic stock/endpoint telescope failed")
    result = {"k": k, "p": p, "h": h, "v": v, "feature_roots": roots,
              "retained_raw_side_roles": raw, "W": W, "m": 3 * h,
              "deficit": deficit, "child_multiplicities": dict(children),
              "center_growing_chronology_not_attained": True,
              "raw_side_formation_and_actual_global_word_not_attained": True}
    tests = []
    for b in (Q(20, 189981), Q(6558894, 10 ** 10 - 6558894), Q(1, 1000)):
        lo, hi = characteristic.moment_interval(result, b)
        if lo <= 1 <= hi:
            raise AssertionError("The decisive moment interval was inconclusive")
        tests.append({"b": str(b), "lower": str(lo), "upper": str(hi),
                      "classification": "optimistic model permits; not attained" if hi < 1 else "excluded even by this optimistic profile"})
    result["moment_tests"] = tests
    return result


def all_p_three_cube_bound():
    # (4643/4644)*3^b is the common rank-only lower moment. A synthetic
    # one-width profile evaluates exactly that expression outward.
    synthetic = {"m": 3, "W": 4644, "child_multiplicities": {1: 3 * 4643}}
    lo, hi = characteristic.moment_interval(synthetic, Q(1, 5000))
    if lo <= 1:
        raise AssertionError("The all-p direct-formation boundary was not separated")
    rows = []
    for p in (3, 4, 5, 6, 12, 22, 36, 80, 1000):
        h, v = 2 * p, 8 * comb(p, 3)
        deficit_after_release_floor = Q(v, 2) - 3 * (2 * p + 1) * h
        if p <= 5 and deficit_after_release_floor >= 0:
            raise AssertionError("The small-p first-moment failure disappeared")
        if p >= 6:
            W = 3 * v + (2 * p + 1) + 19 * comb(p, 3)
            fraction = deficit_after_release_floor / (3 * h * W)
            relaxed = Q(2, 129 * p) - Q(12, 43 * (p - 1) * (p - 2))
            quadratic = Q(2, 129) * (Q(1, p) - Q(18, p * p))
            if not fraction <= relaxed < quadratic <= Q(1, 4644):
                raise AssertionError("The exact all-p rational relaxation failed")
            rows.append({"p": p, "actual_relaxed_density": str(fraction),
                         "closed_relaxation": str(relaxed), "continuous_bound": "1/4644"})
    return {"strict_component_saving_upper_boundary": "1/5000",
            "lower_moment_at_boundary": [str(lo), str(hi)],
            "rational_controls": rows,
            "scope": "k3 fixed retained raw stock, paid singleton+total copies, pure-helper direct monotone bucket formation; all-p proof in report, not a universal lower bound"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("Positive worker count required")
    paths = [Path(__file__).resolve(), Path(characteristic.__file__).resolve()]
    before = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
    started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
    odd = (3, 5, 7) if args.bounded else range(3, 20, 2)
    decoders = [decoder(k) for k in odd]
    tasks = [(3, 3), (5, 5)] if args.bounded else [(3, 3), (3, 4), (5, 5), (7, 7)]
    profiles = [(3, 12)] if args.bounded else [(3, 11), (3, 12), (3, 16), (5, 12), (7, 16), (7, 18)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        matrices = list(pool.map(matrix_task, tasks))
        moments = list(pool.map(moment_task, profiles))
    result = {"status": "PASS DYADIC ODD-CUBE FEATURES AND SCOPED FORMATION BUDGETS",
              "started_utc": started,
              "workers": args.workers, "source_sha256": before,
              "decoders": decoders, "complete_scalar_matrices": matrices,
              "release_bounds": [release_minimum(k) for k in odd],
              "optimistic_profiles": moments, "three_cube_direct_all_p_bound": all_p_three_cube_bound(),
              "physical_native_supplier_or_kappa_not_certified": True}
    result["elapsed_seconds"] = time.monotonic() - clock
    if before != {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}:
        raise AssertionError("An effective source changed during the run")
    if args.output:
        (args.output / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "matrix_entries": sum(x["complete_scalar_matrix_entries"] for x in matrices),
                      "decoders": len(decoders), "moment_profiles": len(moments),
                      "seconds": result["elapsed_seconds"]}, sort_keys=True))


def matrix_task(task):
    return full_scalar_matrix(*task)


def moment_task(task):
    return optimistic_profile(*task)


if __name__ == "__main__":
    main()
