#!/usr/bin/env python3
"""Independent mixed-radix global-add / sparse unit-carry controls.

This explores an alternative joint CRT interface. It checks the exact carry
identity and the low-bit correction outside explicit exclusions. It does not
implement the compact Boolean-predicate gadget or certify its tape cost.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from random import Random
from time import perf_counter


def encode(a, radices):
    value = 0
    for x, s in reversed(tuple(zip(a, radices))):
        value = value * s + x
    return value


def decode(value, radices):
    result = []
    for s in radices:
        value, x = divmod(value, s)
        result.append(x)
    assert value == 0
    return result


def run_profile(config):
    started = perf_counter()
    rng = Random(config["seed"])
    total = good = threshold_bad = borrow_bad = 0
    exact_carry_checks = bit_flip_checks = 0
    negative_equal = negative_high_borrow = None
    configurations = []
    for d, width, low in config["shapes"]:
        # The lemma is for any radices, so these deliberately include composite
        # odd values as well as near-power-of-two values.
        radices = [(1 << width) - rng.randrange(1, min(1000, 1 << (width - 2)), 2) for _ in range(d)]
        modulus = math.prod(radices)
        union_bound = sum(min(1, (1 << low) / s) for s in radices[:-1]) + (d - 1) / (1 << low)
        configurations.append({"dimension": d, "width": width, "low_bits": low,
                               "radices": radices, "conservative_exclusion_union_bound": union_bound})
        for trial in range(config["trials_per_shape"]):
            a = [rng.randrange(s) for s in radices]
            c = [rng.randrange(s) for s in radices]
            if trial % 127 == 0:
                # Construct a carry-threshold adversary in the NEW output.
                y_adversarial = [rng.randrange(s) for s in radices]
                y_adversarial[-2] = c[-2]
                x_adversarial = (encode(y_adversarial, radices) - encode(c, radices)) % modulus
                a = decode(x_adversarial, radices)
            if trial % 131 == 0:
                y_adversarial = [rng.randrange(s) for s in radices]
                y_adversarial[-1] = 0
                a = decode((encode(y_adversarial, radices) - encode(c, radices)) % modulus, radices)
            y = decode((encode(a, radices) + encode(c, radices)) % modulus, radices)
            desired = [(ai + ci) % s for ai, ci, s in zip(a, c, radices)]
            carries = [0]
            prefix_y = prefix_c = 0
            prefix_radix = 1
            for i in range(1, d):
                prefix_y += y[i - 1] * prefix_radix
                prefix_c += c[i - 1] * prefix_radix
                prefix_radix *= radices[i - 1]
                incoming = int(prefix_y < prefix_c)
                carries.append(incoming)
                assert (y[i] - incoming) % radices[i] == desired[i]
                exact_carry_checks += 1
            approximate = [0] + [int((y[i - 1] >> low) < (c[i - 1] >> low)) for i in range(1, d)]
            thresholds = any((y[i - 1] >> low) == (c[i - 1] >> low) for i in range(1, d))
            borrows = any(approximate[i] and not (y[i] & ((1 << low) - 1)) for i in range(1, d))
            threshold_bad += thresholds
            borrow_bad += borrows
            total += 1
            if not thresholds and not borrows:
                assert approximate == carries
                # Descending target-bit order keeps every lower source bit
                # untouched until it has supplied its selected-bit control.
                corrected = list(y)
                for bit in reversed(range(low)):
                    for i in range(1, d):
                        control = approximate[i] and not (corrected[i] & ((1 << bit) - 1))
                        if control:
                            corrected[i] ^= 1 << bit
                            bit_flip_checks += 1
                assert corrected == desired
                good += 1
            if negative_equal is None and any(y[i - 1] == c[i - 1] and carries[i] != int(y[i - 1] < c[i - 1]) for i in range(1, d)):
                i = next(i for i in range(1, d) if y[i - 1] == c[i - 1] and carries[i] != int(y[i - 1] < c[i - 1]))
                negative_equal = {"radices": radices, "input": a, "offset": c, "global_add_output": y,
                                  "target_axis": i, "true_incoming_carry": carries[i],
                                  "wrong_previous_digit_only_carry": int(y[i - 1] < c[i - 1])}
            if negative_high_borrow is None and any(carries[i] and not (y[i] & ((1 << low) - 1)) for i in range(1, d)):
                i = next(i for i in range(1, d) if carries[i] and not (y[i] & ((1 << low) - 1)))
                truncated = (y[i] & ~((1 << low) - 1)) | ((y[i] - 1) & ((1 << low) - 1))
                assert truncated != desired[i]
                negative_high_borrow = {"target_axis": i, "output_digit": y[i], "low_bits": low,
                                        "wrong_truncated_decrement": truncated, "required_digit": desired[i]}
    assert negative_equal is not None and negative_high_borrow is not None
    return {"name": config["name"], "config": config, "configurations": configurations,
            "states": total, "good_states": good, "threshold_exclusions": threshold_bad,
            "borrow_exclusions": borrow_bad, "exact_carry_checks": exact_carry_checks,
            "selected_bit_flip_checks": bit_flip_checks, "negative_equality_threshold": negative_equal,
            "negative_uncharged_high_borrow": negative_high_borrow, "seconds": perf_counter() - started}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 3:
        parser.error("one to three newly allocated carry workers")
    os.environ["OMP_NUM_THREADS"] = "1"
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    configs = [
        {"name": "small-threshold-stress", "seed": 202610088001, "trials_per_shape": 180000,
         "shapes": [(d, w, h) for d, w, h in ((2, 10, 3), (4, 14, 5), (8, 20, 6), (16, 28, 7))]},
        {"name": "medium-native-scale", "seed": 202610088002, "trials_per_shape": 55000,
         "shapes": [(d, w, h) for d, w, h in ((8, 32, 8), (16, 48, 10), (32, 64, 12), (64, 72, 14))]},
        {"name": "wide-word-metadata-scale", "seed": 202610088003, "trials_per_shape": 18000,
         "shapes": [(d, w, h) for d, w, h in ((32, 96, 10), (64, 128, 14), (96, 192, 18), (128, 256, 20))]},
    ]
    start = perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(run_profile, configs))
    result = {"status": "joint modular-add carry identities and scoped exclusions passed",
              "workers": args.workers, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "seconds": perf_counter() - start, "rows": rows,
              "limitations": ["sampled and adversarial exact integer controls, not exhaustive full cubes",
                              "compact Boolean-predicate stage and fixed-tape movement are not implemented",
                              "the competing exact-reflection CRT approach has a separate proof"]}
    (out / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "seconds": result["seconds"],
                      "states": sum(r["states"] for r in rows),
                      "exact_carry_checks": sum(r["exact_carry_checks"] for r in rows)}))


if __name__ == "__main__":
    main()
