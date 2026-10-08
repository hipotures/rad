#!/usr/bin/env python3
"""Exact audit of the addition/comparison phase and boundary generator.

Integer division is used only in the independent oracle. The generator
itself updates one remainder and one phase with additions/comparisons.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from downstream_gaussian import check_sources, require


def generate(s: int, t: int) -> tuple[list[tuple[int, int]], list[list[int]]]:
    increment = 2*(t-s)
    modulus = 2*s
    require(0 < increment < modulus, "Generator requires 0<theta<1")
    phase, remainder = 0, s
    records, cells = [], [[]]
    for j in range(s):
        records.append((phase, remainder))
        cells[-1].append(j)
        remainder += increment
        if remainder >= modulus:
            remainder -= modulus
            phase += 1
            if j+1 < s:
                cells.append([])
    require(phase == t-s and remainder == s, "Periodic generator closure failed")
    return records, cells


def checks(max_s: int) -> dict:
    records_checked = cells_checked = ties = bounds = band_edges = 0
    for s in range(2, max_s+1):
        for k in range(1, min((s-1)//2, 16)+1):
            t = s+k
            records, cells = generate(s, t)
            require(len(cells) == k+1, "Cell count is not t-s+1")
            for j, (phase, remainder) in enumerate(records):
                expected = (2*k*j+s)//(2*s)
                require(phase == expected, "Nearest-index oracle disagrees")
                require(remainder == 2*k*j+s-2*s*phase and 0<=remainder<2*s,
                        "Remainder invariant failed")
                ties += int(remainder == 0)
                records_checked += 1
            lengths = [len(c) for c in cells]
            require(all((s//k)<=x<=((s+k-1)//k) for x in lengths[1:-1]),
                    "Full-cell floor/ceiling size failed")
            require(2*k*lengths[0]>=s-2*k and 2*k*lengths[-1]>=s-2*k,
                    "Half-length partial cells failed")
            for d in range(s//(4*k)+1, (s+k-1)//(2*k)+1):
                if d < 2:
                    continue
                require(4*d*k>s and (2*d-1)*k<s, "Prime ratio domain failed")
                require(min(lengths)>=d-2 and max(lengths)<=4*d+1,
                        "Phase-cell dimension bound failed")
                bounds += 1
            cell_of = {j:i for i,c in enumerate(cells) for j in c}
            for w in range(1,4):
                if min(lengths)<=4*w:
                    continue
                boundary = [j for c in cells for j in c[:w]+c[-w:]]
                boundary_set = set(boundary)
                boundary_order = {j:i for i,j in enumerate(boundary)}
                nb = len(boundary)
                for j in range(s):
                    for delta in range(-w,w+1):
                        if not delta:
                            continue
                        l = (j+delta)%s
                        if cell_of[j] != cell_of[l]:
                            require(j in boundary_set and l in boundary_set,
                                    "Cross-cell edge reaches an interior")
                        if j in boundary_set and l in boundary_set:
                            distance = abs(boundary_order[j]-boundary_order[l])
                            require(min(distance, nb-distance)<=2*w,
                                    "Packed boundary edge exceeds cyclic half-bandwidth")
                        band_edges += 1
                # Interior elimination fills only its own two boundary groups.
                for cell in cells:
                    group = cell[:w]+cell[-w:]
                    for j in group:
                        for l in group:
                            distance = abs(boundary_order[j]-boundary_order[l])
                            require(min(distance,nb-distance)<=2*w,
                                    "Within-cell Schur fill exceeds boundary bandwidth")
            cells_checked += len(cells)
    return {"status":"PASS exact addition/comparison generator, endpoint cells and cyclic border geometry",
            "max_s":max_s,"max_prime_difference":16,
            "nearest_records_checked":records_checked,"phase_cells_checked":cells_checked,
            "half_integer_ties":ties,"dimension_bound_checks":bounds,
            "truncated_gaussian_edges_checked":band_edges,
            "generator_arithmetic":"Only additions, comparisons and one conditional subtraction per index; oracle division excluded from the algorithm.",
            "scope":"Finite geometry and invariants; analytic inverse transfer is reviewed separately."}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--max-s",type=int,default=256)
    args=parser.parse_args()
    start=time.monotonic()
    source=Path(__file__)
    result={"generated_at":datetime.now(timezone.utc).isoformat(),
            "campaign":"20261007T222521Z","campaign_start":"2026-10-07T22:25:21Z",
            "campaign_deadline":"2026-10-08T08:25:21Z",
            "provenance":check_sources(args.upstream),
            "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
            "generator_checks":checks(args.max_s)}
    result["elapsed_seconds"]=time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PASS",result["generator_checks"]["nearest_records_checked"],"nearest-index records and",
          result["generator_checks"]["truncated_gaussian_edges_checked"],"band edges")


if __name__=="__main__":
    main()
