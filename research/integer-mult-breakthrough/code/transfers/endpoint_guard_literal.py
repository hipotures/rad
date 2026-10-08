#!/usr/bin/env python3
"""Literal temporary-register extension of the endpoint guard stress control.

All scalar and C partial numerator sums are observed. The imported local
atomic model is a separately preserved reference, not a complex-track producer.
The deliberately inefficient word is a precision discriminator only.
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

import endpoint_guard as reference


def case(e):
    started = time.monotonic()
    seed = 202610084000 + e
    rng = random.Random(seed)
    original = [[(Q(rng.randrange(-8, 9), 1 << rng.randrange(4)),
                  Q(rng.randrange(-8, 9), 1 << rng.randrange(4))) for _ in range(4)]
                for _ in range(1 << e)]
    p, magnitude = reference.grid_bits(original), reference.component_bound(original)
    target = reference.tensor_c(original, e)
    records = []
    for budget in range(5):
        maximum_grid, maximum_magnitude, register_observations, calls = p, magnitude, 0, 0
        def observe(value):
            nonlocal maximum_grid, maximum_magnitude, register_observations
            if value.denominator & (value.denominator - 1):
                raise AssertionError("literal register left the dyadic ring")
            maximum_grid = max(maximum_grid, value.denominator.bit_length() - 1)
            maximum_magnitude = max(maximum_magnitude, abs(value))
            register_observations += 1
        def observe_payload(values):
            for packet in values:
                for pair in packet:
                    for value in pair:
                        observe(value)
        def exact_sum(terms):
            value = Q()
            for term in terms:
                value += term
                observe(value)
            return value
        def leaf(values):
            output = reference.copy(values)
            for bit in range(e):
                stride = 1 << bit
                for start in range(0, len(output), 2 * stride):
                    for j in range(start, start + stride):
                        first, second = [], []
                        for (a, b), (c, d) in zip(output[j], output[j + stride]):
                            real0 = exact_sum((a, -b, c, d)) / 2
                            imag0 = exact_sum((a, b, d, -c)) / 2
                            real1 = exact_sum((a, b, c, -d)) / 2
                            imag1 = exact_sum((b, -a, c, d)) / 2
                            for value in (real0, imag0, real1, imag1):
                                observe(value)
                            first.append((real0, imag0))
                            second.append((real1, imag1))
                        output[j], output[j + stride] = first, second
            return output
        def shear(values, sign):
            output = reference.copy(values)
            for packet in output:
                a, b = packet[0]
                c, d = packet[1]
                triple_a, triple_b = exact_sum((a, a, a)), exact_sum((b, b, b))
                real = exact_sum((triple_a, -b)) / 4
                imag = exact_sum((a, triple_b)) / 4
                observe(real)
                observe(imag)
                packet[1] = (exact_sum((c, sign * real)), exact_sum((d, sign * imag)))
            return output
        def execute(values, remaining):
            nonlocal calls
            calls += 1
            incoming = reference.copy(values)
            incoming_p = reference.grid_bits(values)
            incoming_m = reference.component_bound(values)
            if remaining == 0:
                output = leaf(values)
            else:
                output = reference.unit(values)
                observe_payload(output)
                output = shear(output, 1)
                for _ in range(3):
                    output = execute(output, remaining - 1)
                output = shear(output, -1)
                output = reference.unit(output, constant=e)
                observe_payload(output)
            if output != reference.tensor_c(incoming, e):
                raise AssertionError("literal dirty child does not return the exact target operator")
            if reference.grid_bits(output) > incoming_p + e:
                raise AssertionError("child endpoint grid certificate failed")
            if reference.component_bound(output) > incoming_m * (1 << e):
                raise AssertionError("child endpoint magnitude certificate failed")
            return output
        actual = execute(original, budget)
        grid_guard = e + (3 * e + 4) * budget
        magnitude_guard = e + 1 + (3 * e + 4) * budget
        if actual != target:
            raise AssertionError("literal recursive word changed its target")
        if maximum_grid > p + grid_guard or maximum_magnitude > magnitude * (1 << magnitude_guard):
            raise AssertionError("guard missed a literal numerator, scalar or active-child register")
        records.append({"remaining_budget": budget, "recursive_calls": calls,
                        "literal_real_register_observations": register_observations,
                        "serialized_leaf_direction_layers": e * 3 ** budget,
                        "observed_extra_denominator_bits": maximum_grid - p,
                        "analytical_denominator_guard": grid_guard,
                        "observed_max_register_magnitude": str(maximum_magnitude),
                        "analytical_magnitude_guard": magnitude_guard,
                        "exact_complete_dirty_endpoint": True})
    return {"selected_width": e, "seed": seed, "complete_records": 1 << e,
            "fields_per_record": 4, "scalar_denominator_charge": 4,
            "scalar_internal_magnitude_charge": 4, "leaf_internal_magnitude_extra_constant": 1,
            "results": records, "seconds": time.monotonic() - started}


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
    utc_started, started = datetime.now(timezone.utc).isoformat(), time.monotonic()
    widths = [1] if args.small else [1, 2, 3, 4]
    if args.workers == 1:
        results = [case(width) for width in widths]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(case, widths))
    result = {"status": "PASS", "scope": "Exact literal-register precision stress for proposed endpoint-aware lemma; no fast volume contract, native motif or exponent.",
              "utc_started_at": utc_started, "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "atomic_reference_source_sha256": hashlib.sha256(Path(reference.__file__).read_bytes()).hexdigest(),
              "workers": args.workers, "small": args.small, "cases": results,
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
