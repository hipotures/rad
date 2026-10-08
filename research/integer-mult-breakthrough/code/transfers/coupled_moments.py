#!/usr/bin/env python3
"""Exact discriminator for changing only child types in positive recurrences.

This checks retained complete moment arithmetic and small positive matrices.
It does not implement a circuit, conversion, or integer-multiplication theorem.
All arithmetic after parsing is rational; logarithms and exponentials have
explicit outward remainder bounds. The checker imports no historical producer.
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


GRID = 1 << 128


def lower_grid(value):
    return Q(value.numerator * GRID // value.denominator, GRID)


def upper_grid(value):
    return Q(-((-value.numerator * GRID) // value.denominator), GRID)


def log_unit(value, terms=32):
    """Enclose log(value) for 1 <= value <= 2 by the atanh series."""
    if not Q(1) <= value <= Q(2):
        raise ValueError("log_unit range violation")
    z = (value - 1) / (value + 1)
    subtotal = sum((2 * z ** (2 * j + 1) / (2 * j + 1)
                    for j in range(terms)), Q())
    remainder = 2 * z ** (2 * terms + 1) / ((2 * terms + 1) * (1 - z * z))
    return lower_grid(subtotal), upper_grid(subtotal + remainder)


def log_positive(value):
    if value < 1:
        raise ValueError("only logarithms of ratios at least one are needed")
    reduced, count = value, 0
    while reduced >= 2:
        reduced /= 2
        count += 1
    low, high = log_unit(reduced)
    low2, high2 = log_unit(Q(2))
    return low + count * low2, high + count * high2


def exp_small(value, terms=10):
    if not Q() <= value <= Q(1):
        raise ValueError("exp_small range violation")
    subtotal, term = Q(1), Q(1)
    for j in range(1, terms + 1):
        term *= value / j
        subtotal += term
    next_term = term * value / (terms + 1)
    remainder = next_term / (1 - value / (terms + 2))
    return lower_grid(subtotal), upper_grid(subtotal + remainder)


def validate_profile(profile):
    m, width = profile["m"], profile["W"]
    if type(m) is not int or type(width) is not int or m <= 1 or width <= 0:
        raise ValueError("invalid native dimensions")
    rows = {int(t): n for t, n in profile["child_multiplicities"].items()}
    if not rows or any(type(n) is not int or n <= 0 or not 0 < t < m
                       for t, n in rows.items()):
        raise ValueError("every retained child must have positive mass and contract")
    mass = sum(t * n for t, n in rows.items())
    if mass != profile["rank_mass"] or m * width - mass != profile["deficit"]:
        raise ValueError("complete rank/deficit ledger does not agree")
    if max(rows) != profile["maxchild"]:
        raise ValueError("maximum child ledger does not agree")
    return rows


def child_weights(profile, saving):
    if not Q() <= saving < Q(1, 100):
        raise ValueError("out-of-scope saving")
    validate_profile(profile)
    m, width = profile["m"], profile["W"]
    result = {}
    for t in profile["child_multiplicities"]:
        t = int(t)
        log_low, log_high = log_positive(Q(m, t))
        exp_low = exp_small(saving * log_low)[0]
        exp_high = exp_small(saving * log_high)[1]
        result[t] = (Q(t, m * width) * exp_low,
                     Q(t, m * width) * exp_high)
    return result


def moment(profile, saving):
    weights = child_weights(profile, saving)
    rows = validate_profile(profile)
    return tuple(sum((n * weights[t][side] for t, n in rows.items()), Q())
                 for side in range(2))


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def product(first, second):
    n = len(first)
    # Downward rounding keeps a lower bound for products of nonnegative entries.
    return [[lower_grid(sum((first[i][k] * second[k][j]
                             for k in range(n)), Q()))
             for j in range(n)] for i in range(n)]


def check_no_potential(matrix, weights):
    """The smallest positive potential component supplies a direct witness."""
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        raise ValueError("non-square recurrence matrix")
    if any(entry < 0 for row in matrix for entry in row):
        raise ValueError("negative work charges cannot define this recurrence")
    if any(weight <= 0 for weight in weights):
        raise ValueError("a cost potential must be strictly positive")
    if any(sum(row) < 1 for row in matrix):
        raise ValueError("row dominance hypothesis is absent")
    smallest = min(range(len(weights)), key=weights.__getitem__)
    charged = sum((x * y for x, y in zip(matrix[smallest], weights)), Q())
    if charged < weights[smallest]:
        raise AssertionError("positive-potential obstruction failed")
    return smallest, charged - weights[smallest]


def split_integer(total, parts, rng):
    cuts = sorted([0, total] + [rng.randrange(total + 1) for _ in range(parts - 1)])
    return [cuts[i + 1] - cuts[i] for i in range(parts)]


def assigned_matrix(profiles, moments, size, rng, mode):
    matrix = []
    for i in range(size):
        profile = profiles[i % len(profiles)]
        weights = moments[i % len(profiles)]
        row = [Q() for _ in range(size)]
        for t, n in validate_profile(profile).items():
            if mode == "diagonal":
                assignments = [n if i == j else 0 for j in range(size)]
            elif mode == "cycle":
                assignments = [n if j == (i + 1) % size else 0 for j in range(size)]
            else:
                assignments = split_integer(n, size, rng)
            if sum(assignments) != n:
                raise AssertionError("a complete recursive child was lost")
            for j, count in enumerate(assignments):
                row[j] += count * weights[t][0]
        matrix.append(row)
    return matrix


def experiment(task):
    label, seed, profiles, target, cases = task
    started = time.monotonic()
    rng = random.Random(seed)
    weighted = [child_weights(profile, target) for profile in profiles]
    checked = products = 0
    minima = []
    dimensions = {"random-types": 2, "reducible-types": 3,
                  "varying-levels": 4, "boundary-and-negatives": 2}
    size = dimensions[label]
    for case in range(cases):
        mode = "random"
        if label == "reducible-types":
            mode = "diagonal" if case % 2 == 0 else "cycle"
        elif label == "boundary-and-negatives":
            mode = ["diagonal", "cycle", "random"][case % 3]
        matrix = assigned_matrix(profiles, weighted, size, rng, mode)
        weights = [Q(1 << rng.randrange(0, 48), 1 << rng.randrange(0, 48))
                   for _ in range(size)]
        _, excess = check_no_potential(matrix, weights)
        minima.append(min(sum(row) - 1 for row in matrix))
        checked += 1
        if label == "varying-levels":
            accumulated = identity(size)
            for _ in range(1 + case % 32):
                accumulated = product(accumulated,
                                      assigned_matrix(profiles, weighted, size, rng, "random"))
                check_no_potential(accumulated, weights)
                products += 1
        if excess < 0:
            raise AssertionError("unexpected contracting positive potential")
    return {"family": label, "seed": seed, "matrix_cases": checked,
            "varying_level_products": products,
            "smallest_lower_row_excess": str(min(minima)),
            "seconds": time.monotonic() - started}


def negative_controls(profiles):
    controls = {}
    # Removing complete high-rank children gives a fictitious easy recurrence.
    for profile in profiles:
        weighted = child_weights(profile, Q(1, 10000))
        rows = validate_profile(profile)
        retained = sum((n * weighted[t][1] for t, n in rows.items()
                        if t < profile["m"] // 2), Q())
        full_lower = sum((n * weighted[t][0] for t, n in rows.items()), Q())
        if not retained < 1 < full_lower:
            raise AssertionError("omitted full-payload children negative did not discriminate")
        controls[profile["id"] + "_omit_high_rank_payloads"] = {
            "fictitious_moment_upper": str(retained),
            "actual_complete_moment_lower": str(full_lower),
            "claim": "Omitting paid complete children fakes contraction at 1e-4."}
    # Exact inherited cost-row discriminator; no 38/47-row proof is claimed.
    a, b = Q(476829673, 10**13), Q(717, 10**7)
    epsilon = Q(999999, 1000000)
    q, kappa = epsilon * a, Q(99999, 100000) * a
    target = 1 - kappa
    honest_crt, fictitious_crt = epsilon, 1 - a
    if not target - honest_crt < 0 < target - fictitious_crt:
        raise AssertionError("unpaid nonlinear CRT negative did not discriminate")
    if not Q(19, 20) * b > q or not epsilon * q > kappa:
        raise AssertionError("the chosen arithmetic negative lacks its other local gaps")
    controls["unpaid_nonlinear_crt_conversion"] = {
        "kappa": str(kappa), "honest_triangular_crt_slack": str(target - honest_crt),
        "fictitious_coordinate_router_slack": str(target - fictitious_crt),
        "claim": "Replacing nonlinear d-pass CRT by a known bit permutation fakes this necessary cost row."}
    for name, matrix, weights in [
        ("signed_cost_row", [[Q(2), Q(-1)], [Q(), Q(1)]], [Q(1), Q(1)]),
        ("zero_potential", [[Q(1), Q()], [Q(), Q(1)]], [Q(), Q(1)]),
        ("subunit_row", [[Q(1, 2), Q()], [Q(), Q(1)]], [Q(1), Q(1)]),
    ]:
        try:
            check_no_potential(matrix, weights)
        except ValueError as error:
            controls[name] = {"rejected": True, "reason": str(error)}
        else:
            raise AssertionError("invalid obstruction hypotheses were accepted")
    boundary = [[Q(1), Q()], [Q(), Q(1)]]
    index, excess = check_no_potential(boundary, [Q(3), Q(7)])
    if excess != 0:
        raise AssertionError("exact reducible boundary failed")
    controls["reducible_unit_boundary"] = {"verified": True, "witness_index": index,
                                            "excess": str(excess)}
    return controls


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path,
                        default=Path(__file__).resolve().parents[2] / "fixtures/transfers/frozen-full-moments.json")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cases", type=int, default=64)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.cases < 1:
        parser.error("positive worker and case counts are required")
    if args.output is not None and args.output.exists():
        parser.error("output must be a fresh path")
    start = time.monotonic()
    fixture = json.loads(args.fixture.read_text())
    profiles = fixture["profiles"]
    if [p["id"] for p in profiles] != ["binary", "complex"]:
        raise ValueError("expected explicit binary and complex full profiles")
    for profile in profiles:
        validate_profile(profile)
    target = Q(1, 10000)
    full_moments = {p["id"]: moment(p, target) for p in profiles}
    if any(low <= 1 for low, high in full_moments.values()):
        raise AssertionError("the target does not exceed every complete primitive root")
    # Direct exact bracketing, independent of producer saved PASS flags.
    brackets = {"binary": (Q(476829673, 10**13), Q(476829675, 10**13)),
                "complex": (Q(71744621, 10**12), Q(71744622, 10**12))}
    root_controls = {}
    for profile in profiles:
        low, high = brackets[profile["id"]]
        at_low, at_high = moment(profile, low), moment(profile, high)
        if not at_low[1] < 1 < at_high[0]:
            raise AssertionError("claimed root bracket does not independently replay")
        root_controls[profile["id"]] = {"saving_interval": (low, high),
                                         "lower_point_moment": at_low,
                                         "upper_point_moment": at_high}
    families = ["random-types", "reducible-types", "varying-levels", "boundary-and-negatives"]
    tasks = [(family, 2026100801 + i, profiles, target, args.cases)
             for i, family in enumerate(families)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        experiments = list(pool.map(experiment, tasks))
    controls = negative_controls(profiles)
    result = {"status": "EXACT_ARITHMETIC_AND_SCOPED_POSITIVE_RECURRENCE_OBSTRUCTION",
              "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Retained full row moments under arbitrary positive child type assignment and products; no circuit or all-size multiplication theorem.",
              "target_saving": target, "complete_moments_at_target": full_moments,
              "root_brackets": root_controls, "experiments": experiments,
              "negative_controls": controls,
              "workers": args.workers, "total_seconds": time.monotonic() - start,
              "inputs": {str(args.fixture): {"bytes": args.fixture.stat().st_size,
                          "sha256": hashlib.sha256(args.fixture.read_bytes()).hexdigest()},
                         str(Path(__file__)): {"bytes": Path(__file__).stat().st_size,
                          "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(encode(result), indent=2) + "\n")
    print(json.dumps({"status": result["status"], "workers": args.workers,
                      "cases": sum(x["matrix_cases"] for x in experiments),
                      "varying_level_products": sum(x["varying_level_products"] for x in experiments),
                      "complete_moment_excesses": {k: float(v[0] - 1) for k, v in full_moments.items()},
                      "seconds": result["total_seconds"]}))


if __name__ == "__main__":
    main()
