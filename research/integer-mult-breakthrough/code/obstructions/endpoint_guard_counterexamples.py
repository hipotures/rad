#!/usr/bin/env python3
"""Exact counterexamples to inferring internal precision from endpoints alone.

These deliberately altered words discriminate the assumptions of the proposed
guard lemma. They are not workloads or proposed fast multiplication circuits.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time


def c_target(data, t):
    result = list(data)
    for bit in range(t):
        step = 1 << bit
        for block in range(0, len(result), 2*step):
            for j in range(block, block+step):
                a, b = result[j]
                c, d = result[j+step]
                result[j] = ((a-b+c+d)/2, (a+b+d-c)/2)
                result[j+step] = ((a+b+c-d)/2, (b-a+c+d)/2)
    return result


def grid(data):
    return max(x.denominator.bit_length()-1 for pair in data for x in pair)


def magnitude(data):
    return max(abs(x) for pair in data for x in pair)


def scale(data, factor):
    return [(factor*a, factor*b) for a, b in data]


def probe(spec):
    t, n = spec
    data = [(Q(1), Q())] + [(Q(), Q())] * ((1 << t)-1)
    target = c_target(data, t)
    power = Q(1 << n)
    # Both words have the EXACT same endpoint, not only its projective class.
    amplified = scale(data, power)
    amplified_after_c = c_target(amplified, t)
    amplified_output = scale(amplified_after_c, 1/power)
    diluted = scale(data, 1/power)
    diluted_after_c = c_target(diluted, t)
    diluted_output = scale(diluted_after_c, power)
    if amplified_output != target or diluted_output != target:
        raise ValueError("Scaled words changed the endpoint")
    if grid(target) > t or magnitude(target) > (1 << t):
        raise ValueError("Independent exact endpoint certificate failed")
    if magnitude(amplified) <= (1 << t) or grid(diluted_after_c) <= t:
        raise ValueError("Counterexamples did not exceed the endpoint-only bounds")
    projective = scale(target, 1/power)
    if projective == target or grid(projective) <= t:
        raise ValueError("Projective normalization corruption did not discriminate")
    return {"selected_width": t, "inserted_scalar_power": n,
            "exact_target_grid": grid(target), "exact_target_component_bound": str(magnitude(target)),
            "same_exact_endpoint_after_scale_undo": True,
            "amplified_intermediate_component_bound": str(magnitude(amplified)),
            "diluted_intermediate_grid": grid(diluted_after_c),
            "unrestored_projective_grid": grid(projective),
            "omitted_local_scalar_charge_invalidates_endpoint_only_guard": True,
            "not_a_counterexample_to_charged_active_child_induction": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.output and args.output.exists():
        parser.error("Positive workers and fresh output required")
    start = time.monotonic()
    specs = [(1, 4), (2, 10)] if args.bounded else [(t, n) for t in (1, 2, 3) for n in (10, 20)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(probe, specs))
    result = {"status": "EXACT PRECISION SCOPE COUNTEREXAMPLES", "workers": args.workers,
              "recorded_utc": datetime.now(timezone.utc).isoformat(), "randomness": "None",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cases": cases, "seconds": time.monotonic()-start,
              "scope": "Exact endpoints alone do not bound internal registers; fixed local scalar prefix and active-child bounds remain necessary. No native or exponent claim."}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2)+"\n")
    print(json.dumps({key: result[key] for key in ("status", "workers", "seconds", "scope")}))


if __name__ == "__main__":
    main()
