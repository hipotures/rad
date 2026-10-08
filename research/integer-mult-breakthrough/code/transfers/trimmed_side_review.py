#!/usr/bin/env python3
"""Independent complete columns for identity minus odd-weight central kernels.

Full bounded subset Yates passes are deliberately used, not the producer's
trimmed DAG or operation counter. These exact scalar arrays start at zero;
the physical dirty/frame implementation is a separate obligation.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time


def f(k, t):
    value = Q(1)
    for j in range((k - 1) // 2):
        value *= Q(t - (2 * j + 1), 2 * (j + 1))
    return value


def coefficients(k):
    values = [Q(int(t == k)) - f(k, t) for t in range(k + 1)]
    result = []
    while values:
        result.append(values[0])
        values = [b - a for a, b in zip(values, values[1:])]
    return result


def masks(h, k):
    return [sum(1 << i for i in subset) for subset in combinations(range(h), k)]


def column(h, k, source, weights):
    allowed = [mask for mask in range(1 << h) if mask.bit_count() <= k]
    down = {mask: int(mask == source) for mask in allowed}
    for bit in range(h):
        for mask in allowed:
            if not mask >> bit & 1 and mask.bit_count() < k:
                down[mask] += down[mask | (1 << bit)]
    if any(value != int(mask & source == mask) for mask, value in down.items()):
        raise AssertionError("independent full downward Yates column failed")
    up = {mask: weights[mask.bit_count()] * down[mask] for mask in allowed}
    for bit in range(h):
        for mask in allowed:
            if mask >> bit & 1:
                up[mask] += up[mask ^ (1 << bit)]
    return up


def case(task):
    h, k = task
    started = time.monotonic()
    labels = masks(h, k)
    weights = coefficients(k)
    if k == 5 and weights != [Q(-3, 8), Q(3, 8), Q(-1, 4), Q(), Q(), Q(1)]:
        raise AssertionError("independent k5 Newton coefficients disagree")
    checks, nonorthogonal, digest = 0, 0, hashlib.sha256()
    for source in labels:
        values = column(h, k, source, weights)
        for target in labels:
            intersection = (source & target).bit_count()
            expected = Q(int(source == target)) - f(k, intersection)
            if values[target] != expected:
                raise AssertionError("full scalar down/up differs from identity minus central kernel")
            if intersection % 2:
                nonorthogonal += 1
                if expected:
                    raise AssertionError("the complete side map did not cancel an odd incidence")
            digest.update(f"{source},{target}:{expected};".encode())
            checks += 1
    omitted = list(weights)
    omitted[k] = Q()
    source = labels[0]
    bad_diagonal = column(h, k, source, omitted)[source]
    if bad_diagonal != -1:
        raise AssertionError("omitted top-degree identity negative did not discriminate")
    # An odd-weight source label belongs to both input and output support of
    # every direct incidence feature that contains it. Its self-pairing one
    # excludes a nested common frame U<=F<=Mperp for that individual feature.
    features = [0, source & -source]
    if k >= 2:
        two = sorted(i for i in range(h) if source >> i & 1)[:2]
        features.append(sum(1 << i for i in two))
    features.append(source)
    frame_witnesses = [{"feature_mask": feature, "source_and_target_label": source,
                        "source_contains_feature": source & feature == feature,
                        "label_self_pairing": source.bit_count() % 2,
                        "scope": "Rejects naive nested common-frame scatter of this incidence feature, not copied-center or full-Lagrangian compilation"}
                       for feature in features]
    return {"h": h, "k": k, "newton_coefficients": [str(value) for value in weights],
            "source_labels": len(labels), "exact_output_column_entries": checks,
            "odd_incidence_zero_entries": nonorthogonal,
            "output_sha256": digest.hexdigest(),
            "omitted_top_degree_identity_diagonal": str(bad_diagonal),
            "frame_witnesses": frame_witnesses,
            "zero_initialized_scalar_model": True,
            "producer_trimmed_operation_counts_verified": False,
            "dirty_restoration_or_native_frame_program_verified": False,
            "seconds": time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output and args.output.exists():
        raise FileExistsError("Use a fresh output for each attempt")
    utc_started = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    tasks = [(8, 5)] if args.small else [(8, 5), (10, 5), (10, 3), (10, 7)]
    if args.workers == 1:
        results = [case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(case, tasks))
    result = {"status": "PASS", "scope": "Independent exact zero-initialized scalar columns and scoped nested-frame witnesses; no trimmed DAG count, dirty native schedule or exponent certified.",
              "utc_started_at": utc_started, "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "workers": args.workers, "small": args.small, "cases": results,
              "exact_output_column_entries": sum(c["exact_output_column_entries"] for c in results),
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "exact_output_column_entries", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
