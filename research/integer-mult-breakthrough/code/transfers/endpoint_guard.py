#!/usr/bin/env python3
"""Exact precision stress controls for endpoint-aware recursive guards.

Three serial same-width children, dirty scalar shears, and unit wrappers form
a well-founded but deliberately inefficient C implementation. It isolates the
guard lemma; no volume contraction or fast algorithm is claimed for this word.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import time


def rotate(value, power):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def grid_bits(values):
    denominators = [value.denominator for packet in values for pair in packet for value in pair]
    if any(d & (d - 1) for d in denominators):
        raise AssertionError("the exact payload left the Gaussian dyadic ring")
    return max(d.bit_length() - 1 for d in denominators)


def component_bound(values):
    return max(abs(value) for packet in values for pair in packet for value in pair)


def copy(values):
    return [list(packet) for packet in values]


def tensor_c(values, e, observe=None):
    result = copy(values)
    for bit in range(e):
        stride = 1 << bit
        for start in range(0, len(result), 2 * stride):
            for j in range(start, start + stride):
                first, second = [], []
                for (a, b), (c, d) in zip(result[j], result[j + stride]):
                    first.append(((a - b + c + d) / 2, (a + b + d - c) / 2))
                    second.append(((a + b + c - d) / 2, (b - a + c + d) / 2))
                result[j], result[j + stride] = first, second
        if observe:
            observe(result)
    return result


def unit(values, constant=0):
    return [[rotate(value, constant + 2 * address.bit_count()) for value in packet]
            for address, packet in enumerate(values)]


def scalar_shear(values, sign=1):
    # y <- y +/- ((3+i)/4)*x; input and dirty y both retained.
    result = copy(values)
    for packet in result:
        a, b = packet[0]
        c, d = packet[1]
        packet[1] = (c + sign * (3 * a - b) / 4,
                     d + sign * (a + 3 * b) / 4)
    return result


def stress_case(e):
    started = time.monotonic()
    seed = 202610083000 + e
    rng = random.Random(seed)
    original = [[(Q(rng.randrange(-8, 9), 1 << rng.randrange(4)),
                  Q(rng.randrange(-8, 9), 1 << rng.randrange(4))) for _ in range(4)]
                for _ in range(1 << e)]
    p, magnitude = grid_bits(original), component_bound(original)
    reference = tensor_c(original, e)
    results = []
    for budget in range(5):
        maximum_grid, maximum_magnitude, calls, endpoint_checks = p, magnitude, 0, 0
        def observe(values):
            nonlocal maximum_grid, maximum_magnitude
            maximum_grid = max(maximum_grid, grid_bits(values))
            maximum_magnitude = max(maximum_magnitude, component_bound(values))
        def execute(values, depth):
            nonlocal calls, endpoint_checks
            calls += 1
            incoming = copy(values)
            incoming_p, incoming_m = grid_bits(values), component_bound(values)
            if depth == 0:
                output = tensor_c(values, e, observe)
            else:
                output = unit(values)
                observe(output)
                output = scalar_shear(output)
                observe(output)
                for _ in range(3):
                    output = execute(output, depth - 1)
                    # This returned output's exact semantic grid, not its
                    # internal arithmetic depth, controls the next sibling.
                    observe(output)
                output = scalar_shear(output, sign=-1)
                observe(output)
                output = unit(output, constant=e)
                observe(output)
            if output != tensor_c(incoming, e):
                raise AssertionError("the recursive same-width word does not return exact C on dirty payloads")
            if grid_bits(output) > incoming_p + e or component_bound(output) > incoming_m * (1 << e):
                raise AssertionError("completed child violates its independent endpoint certificate")
            endpoint_checks += 1
            return output
        actual = execute(original, budget)
        if actual != reference:
            raise AssertionError("the precision stress word changed the desired operator")
        grid_extra = e + (3 * e + 4) * budget
        magnitude_extra = e + (3 * e + 2) * budget
        if maximum_grid > p + grid_extra or maximum_magnitude > magnitude * (1 << magnitude_extra):
            raise AssertionError("endpoint-aware active-child guard failed")
        results.append({"remaining_budget": budget, "recursive_calls": calls,
                        "completed_endpoint_certificates_checked": endpoint_checks,
                        "serialized_leaf_direction_layers": e * 3 ** budget,
                        "observed_extra_denominator_bits": maximum_grid - p,
                        "analytical_extra_denominator_bits_bound": grid_extra,
                        "observed_max_component_magnitude": str(maximum_magnitude),
                        "analytical_extra_component_magnitude_bits_bound": magnitude_extra,
                        "all_dirty_output_fields_exact": True})
    wrong = tensor_c(tensor_c(tensor_c(original, e), e), e)
    if wrong == reference:
        raise AssertionError("omitted inverse-to-forward unit wrapper did not discriminate")
    return {"selected_width": e, "complete_records": 1 << e, "fields_per_record": 4,
            "seed": seed, "input_grid_bits": p, "input_max_component_magnitude": str(magnitude),
            "local_scalar_denominator_charge": 4, "local_scalar_magnitude_charge": 2,
            "same_width_children_per_internal_node": 3,
            "results": results, "omitted_unit_wrapper_rejected": True,
            "endpoint_bound_alone_controls_internal_excursion": False,
            "volume_contraction_or_fast_runtime_claimed": False,
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
    widths = [1] if args.small else [1, 2, 3, 4]
    if args.workers == 1:
        cases = [stress_case(width) for width in widths]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(stress_case, widths))
    result = {"status": "PASS", "scope": "Exact finite same-width recursive precision controls for a proposed endpoint-aware guard lemma; no fast native algorithm or exponent certified.",
              "utc_started_at": utc_started, "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "workers": args.workers, "small": args.small, "cases": cases,
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
