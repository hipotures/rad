#!/usr/bin/env python3
"""Exact joint-grid acquisition, alias-free cores and sparse packet volumes.

These are independent finite combinatorial/packing checks. Kernel accuracy,
exceptional inverse conditioning and the terminating multiplication recurrence
are mathematical dependencies, not certified by this program.
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


def encode(address, shape):
    value = 0
    for coordinate, radix in zip(address, shape):
        value = value*radix+coordinate
    return value


def decode(value, shape):
    out = []
    for radix in reversed(shape):
        value, coordinate = divmod(value, radix)
        out.append(coordinate)
    assert value == 0
    return tuple(reversed(out))


def rotations(seed):
    rng = Random(seed)
    tested = 0
    safe = 0
    differing_overflows = 0
    shape_rows = []
    negative_local_flip = None
    for _ in range(70):
        dimension = rng.randrange(2, 5)
        widths = [rng.randrange(3, 7) for _ in range(dimension)]
        if sum(widths) > 17:
            widths[-1] = 3
        shape = tuple(2**w for w in widths)
        f = rng.randrange(1, min(widths))
        half = 2**(f-1)
        volume = math.prod(shape)
        offset = encode((half,)*dimension, shape)
        probes = range(volume) if volume <= 65536 else rng.sample(range(volume), 65536)
        bad_count = 0
        for address in probes:
            original = decode(address, shape)
            packed = decode((address+offset)%volume, shape)
            independent = tuple((j+half)%t for j,t in zip(original,shape))
            no_overflow = all(j+half < t for j,t in zip(original,shape))
            if no_overflow:
                assert packed == independent
                safe += 1
            else:
                bad_count += 1
                differing_overflows += packed != independent
                # Any actual inter-axis carry creates a small first-axis field,
                # so its destination lies at a global physical cut as well.
                if packed != independent:
                    assert any(j < half for j in packed)
            assert decode(((address+offset)%volume-offset)%volume, shape) == original
            tested += 1
        if volume <= 65536:
            exact_bad = volume-math.prod(t-half for t in shape)
            assert exact_bad == bad_count
            assert Fraction(exact_bad, volume) <= sum((Fraction(half,t) for t in shape), Fraction())
        shape_rows.append({"shape": shape, "fine_half_shift": half,
                           "global_offset": offset, "probes": len(probes),
                           "overflow_probes": bad_count})
        if negative_local_flip is None:
            original = (half,)+(0,)*(dimension-1)
            local_flip = tuple(j ^ half for j in original)
            true_global_shift = tuple((j+half)%t for j,t in zip(original,shape))
            assert local_flip != true_global_shift
            negative_local_flip = {"original": original, "local_fine_bit_flip": local_flip,
                                   "true_global_axis_shift": true_global_shift, "shape": shape}
    return {"probes": tested, "safe_exact_matches": safe,
            "differing_overflow_probes": differing_overflows,
            "negative_within_cell_flip": negative_local_flip, "rows": shape_rows}


def grid_counts(seed):
    rng = Random(seed)
    examples = []
    for _ in range(400):
        dimension = rng.randrange(2, 100)
        radius = rng.randrange(1, 100)
        side = 2**(max(4*radius, 8)-1).bit_length()
        exact = side**dimension-2*(side-2*radius)**dimension+(side-4*radius)**dimension
        upper = 4*dimension*(dimension-1)*radius**2*side**(dimension-2)
        assert 0 <= exact <= upper
        if len(examples) < 12:
            examples.append({"dimension": dimension, "side": side, "radius": radius,
                             "density": float(Fraction(exact,side**dimension)),
                             "pair_union_bound": float(Fraction(upper,side**dimension))})
    # Exhaustive point sets independently verify inclusion/exclusion and the
    # impossibility of the SAME axis being bad in both half-shifted grids.
    exhaust_records = 0
    for dimension in (2,3,4):
        for side,radius in ((4,1),(8,1),(8,2),(16,1)):
            bad_both = 0
            for point in itertools.product(range(side), repeat=dimension):
                bad0 = [j < radius or j >= side-radius for j in point]
                shifted = tuple((j+side//2)%side for j in point)
                bad1 = [j < radius or j >= side-radius for j in shifted]
                assert not any(a and b for a,b in zip(bad0,bad1))
                bad_both += any(bad0) and any(bad1)
                exhaust_records += 1
            exact = side**dimension-2*(side-2*radius)**dimension+(side-4*radius)**dimension
            assert exact == bad_both
    return {"cases": 400, "exhaustive_point_records": exhaust_records,
            "examples": examples,
            "formula": "L^D-2(L-2R)^D+(L-4R)^D",
            "upper_bound": "4D(D-1)R^2L^(D-2)"}


def packet_volumes(seed):
    rows = []
    # R/L=D^-3, delta=D^-4. Fractions avoid rounded density conclusions.
    for d in (2,3,5,8,16,32,64,128):
        ratio = Fraction(1,d**3)
        others = (1+2*ratio)**(d-2)
        residual_source = 16*d*(d-1)*ratio**2*others
        assert residual_source <= Fraction(64,d**4)
        # Phase strips of relative delta, expanded by R_exc. The model radius
        # R_exc/P<=D^-7 follows from theta=D^-16, R_exc<=D^9.
        delta = Fraction(1,d**4)
        exception_source = d*(delta+2*Fraction(1,d**7))*(1+2*ratio)**(d-1)
        assert exception_source <= Fraction(8,d**3)
        total_source = residual_source+exception_source
        # Classical full-record radix sorting of all sparse source packets for
        # D axis passes uses factor<=D*B, where B is address length. This bound
        # demonstrates exactly which dimension/address inequality is needed.
        rows.append({"dimension": d,
                     "residual_source_volume_ratio": str(residual_source),
                     "exception_source_volume_ratio": str(exception_source),
                     "total_source_ratio_float": float(total_source),
                     "total_source_times_D_float": float(total_source*d),
                     "uniform_sparse_sort_bound": "O(n*B/D^2)"})
    return {"rows": rows, "condition": "D^2 grows faster than address length B",
            "limitations": "assumes proven local radii and constructive packet selection; counts duplicated source volume"}


def packed_kernel(seed):
    rng = Random(seed)
    rows = []
    negative = None
    for dimension, side, radius in ((2,4,1),(2,8,1),(2,8,2),(3,4,1),(3,8,1),(3,8,2)):
        shape = (side,)*dimension
        points = list(itertools.product(range(side), repeat=dimension))
        kernels = list(itertools.product(range(2*radius+1), repeat=dimension))
        source = {p:rng.randrange(4) for p in points}
        kernel = {p:rng.randrange(3) for p in kernels}
        max_coefficient = len(kernels)*3*2
        slot_bits = max_coefficient.bit_length()+1
        base = 2**slot_bits
        packed_source = sum(value << (slot_bits*encode(point,shape)) for point,value in source.items())
        packed_factor = sum(value << (slot_bits*encode(point,shape)) for point,value in kernel.items())
        actual_product = packed_source*packed_factor
        central_offset = encode((radius,)*dimension, shape)
        checked = 0
        for point in itertools.product(range(radius, side-radius), repeat=dimension):
            expected = 0
            for shift,value in kernel.items():
                incoming = tuple(j+radius-k for j,k in zip(point,shift))
                expected += source[incoming]*value
            index = encode(point,shape)+central_offset
            actual = (actual_product >> (slot_bits*index)) & (base-1)
            assert actual == expected
            checked += 1
        # A source at a first-axis end can carry into the second axis; this is
        # the concrete reason only interior outputs are accepted.
        if negative is None:
            s = {(0,side-1):1}
            k = {(0,2):1}
            val = sum(v << (slot_bits*encode(p,shape)) for p,v in s.items())
            fac = sum(v << (slot_bits*encode(p,shape)) for p,v in k.items())
            alias_index = side+1
            # This alias is a raw convolution index, before central cropping.
            assert ((val*fac) >> (slot_bits*alias_index)) & (base-1) == 1
            negative = {"side": side, "source": (0,side-1), "kernel_index": (0,2),
                        "false_univariate_alias_index": alias_index,
                        "decoded_alias": decode(alias_index,shape)}
        rows.append({"dimension": dimension, "side": side, "radius": radius,
                     "core_coefficients_checked": checked,
                     "input_slots": side**dimension,
                     "kernel_max_index": max(encode(k,shape) for k in kernels),
                     "integer_product_bits": actual_product.bit_length(), "slot_bits": slot_bits,
                     "maximum_packed_product_slots": side**dimension+max(encode(k,shape) for k in kernels)})
    return {"rows": rows, "negative_uncropped_alias": negative,
            "packing": "single univariate integer multiplication; no 2^D side padding",
            "scope": "nonnegative integer kernels; signed/complex kernels require a fixed number of sign-separated products"}


JOBS = {"packed_global_rotation": rotations, "two_grid_counts": grid_counts,
        "expanded_source_packets": packet_volumes, "packed_kernel": packed_kernel}


def job(item):
    name, seed = item
    started = perf_counter()
    result = JOBS[name](seed)
    result.update(seed=seed, seconds=perf_counter()-started, pid=os.getpid())
    return name,result


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
    out.mkdir(parents=True, exist_ok=False)
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = dict(executor.map(job, [(name,202610083000+i) for i,name in enumerate(JOBS)]))
    result = {"status": "joint grid finite combinatorial discriminators passed",
              "workers": args.workers, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "results": results,
              "limitations": ["no Gaussian tail or inverse conditioning certified",
                               "source-volume formula is conditional on the supplied radius model",
                               "finite integer products do not prove the recursive time bound"]}
    (out/"certificate.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status": result["status"], "seconds": {k:v["seconds"] for k,v in results.items()}}))


if __name__ == "__main__":
    main()
