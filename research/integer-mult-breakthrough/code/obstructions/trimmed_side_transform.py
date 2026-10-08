#!/usr/bin/env python3
"""Exact scalar and cost screen for a cancellation-allowing odd-subset side DAG.

Two trimmed Yates passes evaluate a Newton-weighted intersection map.
This is a characteristic-zero straight-line circuit with zero initial slots,
aliasing/fan-out and paid nonunit scalar factors, not a reversible dirty circuit.
No physical rank distribution, guard theorem or exponent is inferred.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time


def side_value(k, t):
    if k < 3 or k % 2 != 1 or not 0 <= t <= k:
        raise ValueError("Odd k >= 3 and an intersection in [0,k] required")
    central = Fraction(1)
    for root in range(1, k, 2):
        central *= Fraction(t - root, k - root)
    return Fraction(t == k) - central


def newton_coefficients(k):
    row = [side_value(k, t) for t in range(k + 1)]
    cs = []
    while row:
        cs.append(row[0])
        row = [b - a for a, b in zip(row, row[1:])]
    for t in range(k + 1):
        if sum((cs[j] * comb(t, j) for j in range(t + 1)), Fraction()) != side_value(k, t):
            raise ValueError("Newton reconstruction failed")
    if any(c.denominator & (c.denominator - 1) for c in cs):
        raise ValueError("A non-dyadic scalar factor appeared")
    return cs


def subsets(h, k):
    return [sum(1 << b for b in bs) for bs in combinations(range(h), k)]


def build_dag(h, k):
    if not 3 <= k < h:
        raise ValueError("Require 3 <= k < h")
    levels = [subsets(h, j) for j in range(k + 1)]
    masks = [m for level in levels for m in level]
    top = levels[k]
    # -1 is a mathematical zero, not an arbitrary dirty physical slot.
    zero = -1
    nodes = [("input", i) for i in range(len(top))]
    input_ids = dict(zip(top, range(len(top))))
    z = {m: input_ids.get(m, zero) for m in masks}
    counts = Counter()

    def plus(a, b, phase):
        if b == zero:
            counts[phase + "_zero_source_skips"] += 1
            return a
        if a == zero:
            counts[phase + "_zero_destination_aliases"] += 1
            return b
        nodes.append(("add", a, b))
        counts[phase + "_additions"] += 1
        return len(nodes) - 1

    # Drive the k-layer input down. Each coordinate is used exactly once.
    for bit in range(h):
        mask = 1 << bit
        for level in levels[:-1]:
            for m in level:
                if not m & mask:
                    z[m] = plus(z[m], z[m | mask], "superset")
    cs = newton_coefficients(k)
    down_outputs = dict(z)
    for m in masks:
        c = cs[m.bit_count()]
        if not c:
            z[m] = zero
        elif c != 1:
            nodes.append(("scale", z[m], c.numerator, c.denominator))
            z[m] = len(nodes) - 1
            counts["nonunit_scalar_gates"] += 1
    # Assemble the weighted features back up. Both passes are trimmed to |m|<=k.
    for bit in range(h):
        mask = 1 << bit
        for level in levels[1:]:
            for m in level:
                if m & mask:
                    z[m] = plus(z[m], z[m ^ mask], "subset")
    edges = sum(j * comb(h, j) for j in range(1, k + 1))
    if sum(counts[x] for x in ("superset_additions", "superset_zero_source_skips",
                              "superset_zero_destination_aliases")) != edges:
        raise ValueError("Superset event accounting failed")
    if sum(counts[x] for x in ("subset_additions", "subset_zero_source_skips",
                              "subset_zero_destination_aliases")) != edges:
        raise ValueError("Subset event accounting failed")
    return {"h": h, "k": k, "top": top, "nodes": nodes,
            "outputs": [z[m] for m in top], "down_outputs": down_outputs,
            "counts": dict(counts), "newton": cs,
            "slots": len(masks), "raw_edges_per_pass": edges}


def evaluate(dag, inputs):
    values = []
    for node in dag["nodes"]:
        op = node[0]
        if op == "input":
            values.append(inputs[node[1]])
        elif op == "add":
            values.append(values[node[1]] + values[node[2]])
        else:
            numerator = values[node[1]] * node[2]
            denominator = node[3]
            if numerator % denominator:
                raise ValueError("Integer basis evaluation lost a dyadic denominator")
            values.append(numerator // denominator)
    return [values[n] if n >= 0 else 0 for n in dag["outputs"]]


def cost_record(dag):
    counts = dag["counts"]
    v = len(dag["top"])
    adds = counts.get("superset_additions", 0) + counts.get("subset_additions", 0)
    scalar = counts.get("nonunit_scalar_gates", 0)
    return {"h": dag["h"], "k": dag["k"], "vertices": v,
            "truncated_slots": dag["slots"], "raw_edges_per_pass": dag["raw_edges_per_pass"],
            "events": counts, "arithmetic_additions": adds,
            "nonunit_scalar_gates": scalar, "authored_SSA_roles_including_inputs": len(dag["nodes"]),
            "additions_per_vertex": str(Fraction(adds, v)),
            "SSA_roles_per_vertex": str(Fraction(len(dag["nodes"]), v)),
            "Newton_coefficients": list(map(str, dag["newton"])),
            "not_charged_as_physical_zero_cost": ["mathematical zero initialization", "aliasing and fan-out",
              "arbitrary dirty scratch restoration", "Gaussian frame changes", "tape movement and guard repair"],
            "scope": "Exact scalar-DAG arithmetic count; SSA roles are not the native motif R"}


def full_case(h, k):
    dag = build_dag(h, k)
    den = max(c.denominator for c in dag["newton"])
    entries = 0
    odd_zeros = 0
    for j, source in enumerate(dag["top"]):
        xs = [0] * len(dag["top"])
        xs[j] = den
        observed = evaluate(dag, xs)
        for target, out in zip(dag["top"], observed):
            t = (target & source).bit_count()
            expected = den * side_value(k, t)
            if expected.denominator != 1 or out != expected.numerator:
                raise ValueError("Complete characteristic-zero coefficient replay failed")
            if t % 2:
                if out:
                    raise ValueError("A nonzero side has nonorthogonal binary labels")
                odd_zeros += 1
            entries += 1
    # Omission of the +identity top feature is invalid, including at the self endpoint.
    self_omission = -den  # central(k)=1 whereas the correct side(k)=0
    corrupt_odd = den * (side_value(k, 1) + Fraction(1, den))
    if self_omission == 0 or corrupt_odd == 0:
        raise ValueError("Negative controls failed")
    result = cost_record(dag)
    result.update({"all_matrix_entries": entries, "checked_odd_intersection_zeros": odd_zeros,
                   "denominator_basis": den, "negative_omitted_self_feature_residual": self_omission,
                   "negative_perturbed_odd_coefficient_residual": str(corrupt_odd)})
    return result


def cost_case(h, k):
    return cost_record(build_dag(h, k))


def task(spec):
    kind, h, k = spec
    return {"kind": kind, "result": (full_case if kind == "full" else cost_case)(h, k)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.output and args.output.exists():
        parser.error("Positive workers and a fresh output path required")
    start = time.monotonic()
    specs = [("full", 8, 5), ("full", 7, 3)] if args.bounded else [
        ("full", 8, 5), ("full", 10, 5), ("full", 10, 3), ("full", 10, 7),
        ("cost", 12, 5), ("cost", 16, 5), ("cost", 20, 5), ("cost", 24, 5)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(task, specs))
    report = {"status": "EXACT SCALAR DAG; PHYSICAL COMPILER OPEN", "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "workers": args.workers, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "randomness": "None; deterministic complete coefficient matrices and exact DAG counts", "cases": cases,
              "seconds": time.monotonic() - start,
              "not_proved": ["reversible arbitrary-dirty implementation", "complete frame chronology",
                "favorable native child histogram", "new guard bound", "kappa >= 1e-4", "all-size transfer"]}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "workers": args.workers, "cases": len(cases), "seconds": report["seconds"]}))


if __name__ == "__main__":
    main()
