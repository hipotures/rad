#!/usr/bin/env python3
"""Independent exact controls for halo-free interior Kronecker convolution.

Uses one univariate integer product with radix equal to the local side, and
checks against separately nested Cartesian sums. Face outputs are excluded,
and a negative face probe verifies why that exclusion matters.
"""
import argparse
from itertools import product
import hashlib
import json
import math
from pathlib import Path
import random
import time


def index(coords, side):
    result = 0
    stride = 1
    for coordinate in coords:
        result += coordinate*stride
        stride *= side
    return result


def encode(coefficients, bits):
    radix = 1 << bits
    result = 0
    for value in reversed(coefficients):
        assert 0 <= value < radix
        result = (result << bits)+value
    return result


def run_case(d, side, radius, seed):
    start = time.time()
    assert 2*radius+1 < side
    rng = random.Random(seed)
    volume = side**d
    coords = list(product(range(side), repeat=d))
    values = [0]*volume
    for c in coords:
        values[index(c, side)] = rng.randrange(-9, 10)
    # Independently asymmetric one-dimensional factors and tensor coefficients.
    factors = [[rng.randrange(1, 8) for _ in range(2*radius+1)] for _ in range(d)]
    kernel_volume = 2*radius*sum(side**i for i in range(d))+1
    kernel = [0]*kernel_volume
    offsets = list(product(range(-radius, radius+1), repeat=d))
    tensor = []
    for offset in offsets:
        coefficient = math.prod(factors[i][h+radius] for i, h in enumerate(offset))
        shifted = tuple(h+radius for h in offset)
        kernel[index(shifted, side)] += coefficient
        tensor.append((offset, coefficient))
    # This guard uses all possible terms, rather than an empirical maximum.
    term_bound = 9*7**d*len(offsets)
    slot_bits = term_bound.bit_length()+1
    positive = [max(v, 0) for v in values]
    negative = [max(-v, 0) for v in values]
    packed_kernel = encode(kernel, slot_bits)
    positive_product = encode(positive, slot_bits)*packed_kernel
    negative_product = encode(negative, slot_bits)*packed_kernel
    mask = (1 << slot_bits)-1
    shift = radius*sum(side**i for i in range(d))
    interior_pass = 0
    bad_faces = 0
    first_bad = None
    for output in coords:
        expected = 0
        for offset, coefficient in tensor:
            source = tuple(output[i]-offset[i] for i in range(d))
            if all(0 <= c < side for c in source):
                expected += coefficient*values[index(source, side)]
        address = index(output, side)+shift
        observed = ((positive_product >> (slot_bits*address)) & mask)-((negative_product >> (slot_bits*address)) & mask)
        interior = all(radius <= c < side-radius for c in output)
        if interior:
            assert observed == expected
            interior_pass += 1
        elif observed != expected:
            bad_faces += 1
            if first_bad is None:
                first_bad = {"coordinate": output, "cartesian_sum": expected, "packed_sum": observed}
    assert interior_pass == (side-2*radius)**d
    if d > 1:
        assert bad_faces > 0, "negative face control must expose carry collisions"
    return {"dimension": d, "side": side, "radius": radius, "seed": seed,
            "volume": volume, "kernel_slots": kernel_volume,
            "integer_operand_bits": volume*slot_bits,
            "slot_bits": slot_bits, "interior_exact_probes": interior_pass,
            "face_negative_probes": bad_faces, "first_bad_face": first_bad,
            "elapsed_seconds": time.time()-start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start = time.time()
    cases = [run_case(*case) for case in ((2,16,2,2026100811), (3,16,2,2026100812),
                                          (2,32,3,2026100813), (4,8,1,2026100814))]
    result = {"status": "interior_exact_and_faces_rejected",
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cases": cases, "elapsed_seconds": time.time()-start,
              "scope": "changed algebraic packing interface; no claim about global box acquisition"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "interior_probes": sum(c["interior_exact_probes"] for c in cases),
                      "face_negatives": sum(c["face_negative_probes"] for c in cases),
                      "seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
