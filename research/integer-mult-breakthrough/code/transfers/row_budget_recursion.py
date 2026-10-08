#!/usr/bin/env python3
"""Exact toy recursion with same-width calls and an explicit row/depth budget.

This proves arithmetic properties of the declared toy recurrence only.
It supplies neither a one-axis phase program nor a changed multiplier theorem.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import cache
import hashlib
import json
from pathlib import Path
import time


M = 4
W = 10
CHILDREN = {1: 4, 2: 1, 4: 6}
MOMENT_UPPER = Q(7, 8)
SAVING = Q(1, 2)


def ceil_log2(value):
    if type(value) is not int or value < 1:
        raise ValueError("positive integer width required")
    return (value - 1).bit_length()


def depth_for(width):
    return 3 * ceil_log2(width)


@cache
def exact_cost(width, depth):
    if width < 1 or depth < 0:
        raise ValueError("invalid recursive state")
    if width < M or depth == 0:
        return Q(width)
    return 1 + sum((Q(count, W) * exact_cost(t * (width // M), depth - 1)
                    for t, count in CHILDREN.items()), Q())


def verify_state(width, depth, rows):
    if width < 1 or depth < 0 or rows < 1:
        raise ValueError("invalid physical state")
    if rows < W**depth:
        raise ValueError("insufficient complete row stock for the remaining budget")
    if width >= M and depth:
        if rows % W:
            raise ValueError("incomplete W-way row boundary")
        for t in CHILDREN:
            child_width, child_depth, child_rows = t * (width // M), depth - 1, rows // W
            if child_depth >= depth or child_rows >= rows or child_width > width:
                raise AssertionError("joint recursive decrease failed")
            if child_rows < W**child_depth:
                raise AssertionError("a complete child row stock was lost")


def controls(task):
    family, widths = task
    start = time.monotonic()
    cases = []
    for width in widths:
        depth = depth_for(width)
        stock = W**depth
        verify_state(width, depth, stock)
        cost = exact_cost(width, depth)
        # T <= 17 sqrt(e), compared without floating point or square roots.
        if cost * cost > 17 * 17 * width:
            raise AssertionError("complete depth-truncated time bound failed")
        log_width = ceil_log2(width)
        if stock.bit_length() > 12 * log_width + 1:
            raise AssertionError("row-prefix bit budget failed")
        # An exact declared guard recurrence includes full same-width paths.
        rank_mass = sum(t * count for t, count in CHILDREN.items())
        local_guard = rank_mass * (width // M) + 64
        leaf_guard = 8 * width
        cumulative_guard = leaf_guard + depth * local_guard
        if cumulative_guard > 8 * width + 12 * log_width * (rank_mass * width + 64):
            raise AssertionError("declared e*log(e) guard upper ledger failed")
        cases.append({"width": width, "depth_budget": depth,
                      "complete_row_stock": str(stock), "row_prefix_bits": stock.bit_length(),
                      "exact_normalized_time": str(cost),
                      "time_squared_over_width": str(cost * cost / width),
                      "declared_guard_bits": cumulative_guard})
    return {"family": family, "cases": cases, "seconds": time.monotonic() - start}


def negatives():
    result = {}
    width = 16
    depth = depth_for(width)
    for label, rows in [("missing_last_row_level", W**(depth - 1)),
                        ("no_row_stock", 1), ("broken_boundary", W**depth + 1)]:
        try:
            verify_state(width, depth, rows)
        except ValueError as error:
            result[label] = {"rejected": True, "reason": str(error)}
        else:
            raise AssertionError("invalid complete-payload capacity was accepted")
    same_child = M * (width // M)
    if same_child != width:
        raise AssertionError("same-width negative input is not aligned")
    result["width_only_well_foundedness"] = {
        "parent_width": width, "same_child_width": same_child,
        "strict_width_decrease": False,
        "claim": "Width-only recursion is not justified; the declared depth and row budget supply termination."}
    full_self_mass = Q(W, W)
    lower_extra_mass = Q(1, M * W)
    if full_self_mass + lower_extra_mass <= 1:
        raise AssertionError("unit self-mass negative failed")
    result["unit_or_larger_self_mass"] = {
        "self_mass": str(full_self_mass),
        "moment_lower_at_zero_saving": str(full_self_mass + lower_extra_mass),
        "claim": "A paid additional child rules out a contracting positive moment when n_m>=W."}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output is not None and args.output.exists():
        parser.error("output must be fresh")
    start = time.monotonic()
    # At exponent 1/2: M=3/5+1/5+1/(10 sqrt(2))<7/8.
    # sqrt(2)>4/3 follows from 2>16/9. The terminal tail is paid.
    if not Q(2) > Q(16, 9) or MOMENT_UPPER**6 >= Q(1, 2):
        raise AssertionError("exact moment or depth coefficient inequality failed")
    tasks = [("aligned-widths", [4, 16, 64, 256, 1024, 4096]),
             ("floor-remainders", [5, 15, 31, 63, 127, 511]),
             ("large-aligned-widths", [8192, 16384, 32768, 65536]),
             ("early-leaf-boundaries", [1, 2, 3, 7, 8, 9])]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        evidence = list(pool.map(controls, tasks))
    result = {"status": "EXACT_TOY_SAME_WIDTH_ROW_BUDGET_CERTIFICATE",
              "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Declared nonnegative cost and guard recurrences only; no scalar/frame phase program or actual all-size multiplication transfer.",
              "native": {"m": M, "W": W, "child_multiplicities": CHILDREN,
                         "same_width_self_mass": str(Q(CHILDREN[M], W)),
                         "saving": str(SAVING), "moment_upper": str(MOMENT_UPPER)},
              "depth_formula": "3*ceil(log2(e))", "time_bound": "17*sqrt(e)",
              "complete_row_prefix_bound": "12*ceil(log2(e))+1 bits",
              "declared_precision_order": "O(e*log(e)); not a proof of a physical Gaussian guard",
              "families": evidence, "negative_controls": negatives(),
              "workers": args.workers,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "seconds": time.monotonic() - start}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "cases": sum(len(x["cases"]) for x in evidence),
                      "workers": args.workers, "seconds": result["seconds"]}))


if __name__ == "__main__":
    main()
