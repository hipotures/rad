#!/usr/bin/env python3
"""Recompute PR160 then screen explicit strict assembly instantiations.

This parameter-only screen does not independently prove the finite word or
all-size transfer. All saved final-kappa fields are discovery targets only.
"""
import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction as Q
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if sys.flags.optimize:
        raise SystemExit("Assertion-disabled Python is unsupported")
    if args.output.exists():
        raise SystemExit("Refusing to replace an existing attempt")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.source.resolve() / "scripts"))
    import paired_cube_network as net
    from structured_bulk_assembly import assembly, js
    start = time.monotonic()
    baseline = net.certificate()
    bridge = baseline["finite_bridge"]
    cases = [
        ("unchanged", Q(1, 10**6), Q(1, 10**8), Q(1, 10**10)),
        ("phase-stop", Q(1, 10**12), Q(1, 10**8), Q(1, 10**10)),
        ("assembly-slack", Q(1, 10**6), Q(1, 10**12), Q(1, 10**10)),
        ("leaf-gap", Q(1, 10**6), Q(1, 10**8), Q(1, 10**15)),
        ("combined", Q(1, 10**12), Q(1, 10**12), Q(1, 10**15)),
    ]
    rows = []
    for name, beta, eta, gap in cases:
        bit = min(net.AB, (1-beta)*net.AC-gap)
        provisional = assembly(bit, net.AC, bridge, Q(0), eta=eta, beta=beta)
        minimum = provisional["minimum_margin"]
        grid = 10**18
        target = Q((minimum.numerator*grid-1)//minimum.denominator, grid)
        result = assembly(bit, net.AC, bridge, target, eta=eta, beta=beta)
        if not all(v > 0 for v in result["strict_constraints"].values()):
            raise ValueError("Nonpositive strict constraint")
        if len(result["strict_constraints"]) != 47 or len(result["margins"]) != 7:
            raise ValueError("Assembly coverage changed")
        try:
            assembly(bit, net.AC, bridge, target+Q(1, grid), eta=eta, beta=beta)
        except AssertionError:
            next_rejected = True
        else:
            next_rejected = False
        rows.append(dict(variant=name, beta=beta, eta=eta, leaf_gap=gap,
                         effective_assembly_bit=bit, candidate_kappa=target,
                         candidate_decimal=str(float(target)), next_grid_rejected=next_rejected,
                         improvement_over_pr160=target-net.KAPPA, assembly=result))
    report = dict(status="DISCOVERY", source_revision="628fcab57063370cbf03c0fb54472348e7b68368",
                  unchanged_baseline_recomputed=True, baseline_kappa=net.KAPPA,
                  source_sha256=baseline["source_sha256"],
                  bit_saving=net.AB, complex_saving=net.AC,
                  rows=rows, elapsed_seconds=time.monotonic()-start,
                  exclusions=["No new construction", "Independent finite review pending",
                              "No publication gate", "No unconditional theorem"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(js(report), indent=2) + "\n")
    for r in rows:
        print(r["variant"], r["candidate_kappa"], r["candidate_decimal"],
              "47+7 strict; next grid rejected:", r["next_grid_rejected"])
    print("elapsed_seconds", report["elapsed_seconds"])


if __name__ == "__main__":
    main()
