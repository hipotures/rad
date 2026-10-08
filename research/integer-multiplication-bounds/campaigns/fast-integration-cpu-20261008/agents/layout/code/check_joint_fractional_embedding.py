#!/usr/bin/env python3
"""One-pass product embedding of fractional source cores before binary gather.

The source is one sequential prime/mixed-radix tensor stream. Each occupied
target slot consumes the next source record, including a zero-valued record.
No Gaussian implementation or historical/public checker is imported.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path
from random import Random
from time import perf_counter


def points(shape):
    return itertools.product(*(range(t) for t in shape))


def encode(point, shape):
    out = 0
    for j,t in zip(point,shape):
        out = out*t+j
    return out


def decode(value, shape):
    out = []
    for t in reversed(shape):
        value,j = divmod(value,t)
        out.append(j)
    assert not value
    return tuple(reversed(out))


def floor_ratio(s, t, j):
    return s*j//t


def embed(source, source_shape, target_shape, side, target_shift):
    """Sequential source -> sequential binary target axis-major k/u fields."""
    source_position = 0
    target = []
    occupied = []
    origins = [floor_ratio(s,t,target_shift) for s,t in zip(source_shape,target_shape)]
    for coordinate in points(target_shape):
        relative_source = []
        valid = True
        for q,s,t,a in zip(coordinate,source_shape,target_shape,origins):
            k,u = divmod(q,side)
            lo = floor_ratio(s,t,k*side+target_shift)-a
            hi = floor_ratio(s,t,(k+1)*side+target_shift)-a
            assert 0 <= hi-lo <= side
            valid &= u < hi-lo
            relative_source.append(lo+u)
        if valid:
            expected_source_position = encode(relative_source,source_shape)
            assert source_position == expected_source_position
            target.append(source[source_position])
            occupied.append(tuple(relative_source))
            source_position += 1
        else:
            target.append(None)
            occupied.append(None)
    assert source_position == len(source) == math.prod(source_shape)
    return target,occupied,origins


def gather(data, target_shape, side):
    """Finite permutation model of the separately paid binary slot router."""
    coarse = tuple(t//side for t in target_shape)
    result = []
    for k in points(coarse):
        for u in points((side,)*len(target_shape)):
            original = tuple(a*side+b for a,b in zip(k,u))
            result.append(data[encode(original,target_shape)])
    return result


def run_dimension(item):
    dimension,seed = item
    started = perf_counter()
    rng = Random(seed)
    cases = 0
    written = 0
    read = 0
    occupied_checked = 0
    shifted_matches = 0
    overflow_cases = 0
    selector_records = 0
    selector_boundary_exclusions = 0
    negative_floor_plateau = None
    negative_missing_partial_slab = None
    for trial in range(35):
        widths = [rng.randrange(2,5) for _ in range(dimension)]
        if sum(widths) > 15:
            widths[-1] = 2
        target_shape = tuple(2**w for w in widths)
        source_shape = tuple(t-rng.randrange(1,max(2,t//4)) for t in target_shape)
        side = 2**rng.randrange(1,min(widths)+1)
        source_points = list(points(source_shape))
        source = list(source_points)
        volume = math.prod(target_shape)
        for target_shift in (0,side//2):
            origins = tuple(floor_ratio(s,t,target_shift) for s,t in zip(source_shape,target_shape))
            offset = encode(origins,source_shape)
            # Reading source(index+offset) is one global left rotation of the
            # complete mixed-radix stream, with an explicit physical split.
            rotated = source[offset:]+source[:offset]
            target,occupancy,actual_origins = embed(rotated,source_shape,target_shape,side,target_shift)
            assert tuple(actual_origins) == origins
            joint = gather(target,target_shape,side)
            expected_joint = []
            coarse = tuple(t//side for t in target_shape)
            for k in points(coarse):
                for u in points((side,)*dimension):
                    relative = tuple(floor_ratio(s,t,j*side+target_shift)-a+x
                                     for j,x,s,t,a in zip(k,u,source_shape,target_shape,origins))
                    lengths = tuple(floor_ratio(s,t,(j+1)*side+target_shift)
                                    -floor_ratio(s,t,j*side+target_shift)
                                    for j,s,t in zip(k,source_shape,target_shape))
                    if all(x < length for x,length in zip(u,lengths)):
                        actual = rotated[encode(relative,source_shape)]
                        expected_joint.append(actual)
                        if all(x+a < s for x,a,s in zip(relative,origins,source_shape)):
                            desired = tuple(x+a for x,a in zip(relative,origins))
                            assert actual == desired
                            shifted_matches += 1
                        else:
                            overflow_cases += 1
                    else:
                        expected_joint.append(None)
            assert joint == expected_joint
            read += len(source)
            written += volume
            occupied_checked += sum(x is not None for x in occupancy)
            cases += 1
            # Exact selector map floor(s*k/t) is evaluated through its actual
            # fractional source packet. There is no covariance shortcut.
            for coordinate in points(target_shape):
                global_target = tuple((q+target_shift)%t for q,t in zip(coordinate,target_shape))
                desired = tuple(floor_ratio(s,t,k) for s,t,k in zip(source_shape,target_shape,global_target))
                packet_source = []
                valid = True
                inside_packet = True
                for q,s,t,a,kglobal in zip(coordinate,source_shape,target_shape,origins,global_target):
                    k,u = divmod(q,side)
                    lo_global = floor_ratio(s,t,k*side+target_shift)
                    raw_global = floor_ratio(s,t,k*side+u+target_shift)
                    local = raw_global-lo_global
                    length = floor_ratio(s,t,(k+1)*side+target_shift)-lo_global
                    assert 0 <= local <= length
                    if local == length:
                        # A floor plateau may make the final target position
                        # select the first source index of the NEXT packet.
                        # It is a boundary output, covered by the paired-grid
                        # exclusion/repair, not an occupied slot in this core.
                        assert u >= side-2
                        inside_packet = False
                        if negative_floor_plateau is None:
                            negative_floor_plateau = {"source_side": s, "target_side": t,
                                                      "packet_side": side, "target_local": u,
                                                      "source_local": local, "source_core_length": length}
                    packet_source.append(lo_global-a+local)
                    valid &= lo_global-a+local+a < s
                if not inside_packet:
                    selector_boundary_exclusions += 1
                    continue
                actual = rotated[encode(packet_source,source_shape)]
                if valid:
                    assert actual == desired
                    selector_records += 1
        if negative_missing_partial_slab is None and any(s%side for s in source_shape):
            s = next(s for s in source_shape if s%side)
            old_count = s//side*side
            assert old_count < s
            negative_missing_partial_slab = {"source_side": s, "packet_side": side,
                                            "wrong_fixed_length_count": old_count,
                                            "required_count": s}
    return {"dimension": dimension, "cases": cases, "written_target_records": written,
            "sequential_source_reads": read, "occupied_provenance_checks": occupied_checked,
            "safe_shifted_source_matches": shifted_matches, "overflow_records": overflow_cases,
            "exact_selector_outputs_checked": selector_records,
            "selector_boundary_exclusions": selector_boundary_exclusions,
            "negative_floor_plateau_at_core_end": negative_floor_plateau,
            "negative_discarding_fractional_end": negative_missing_partial_slab,
            "seed": seed, "seconds": perf_counter()-started}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("at most four allocated slots")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    out = Path(args.output)
    out.mkdir(parents=True,exist_ok=False)
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        rows = list(executor.map(run_dimension, [(d,202610084000+d) for d in (1,2,3,4)]))
    result = {"status": "joint fractional embedding and source-origin controls passed",
              "workers": args.workers, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "rows": rows,
              "totals": {key:sum(row[key] for row in rows) for key in
                         ("cases","written_target_records","sequential_source_reads","occupied_provenance_checks",
                          "safe_shifted_source_matches","overflow_records","exact_selector_outputs_checked",
                          "selector_boundary_exclusions")},
              "limitations": ["global binary gather models the separately paid coordinate router",
                               "selector maps check exact provenance, not Gaussian accuracy",
                               "overflow/cut outputs require the separate exceptional repair"]}
    (out/"certificate.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status": result["status"], "totals": result["totals"]}))


if __name__ == "__main__":
    main()
