#!/usr/bin/env python3
"""Exact CRT movement controls; known bit routes are not modular shears.

Finite stream simulation validates the existing descending interval rotations,
charges each payload copy, and falsifies two tempting replacements. These are
scoped exclusions, not a lower bound for every possible fixed-tape algorithm.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from time import perf_counter


def points(shape):
    return itertools.product(*(range(t) for t in shape))


def encode(point, shape):
    result = 0
    for a, t in zip(point, shape):
        result = result * t + a
    return result


def scalar_index(a, primes):
    result = 0
    prefix = 1
    for digit, s in zip(a, primes):
        result += digit * prefix
        prefix *= s
    return result


def direct_crt(a, primes):
    scalar = scalar_index(a, primes)
    prefix = 1
    result = []
    for s in primes:
        result.append((pow(prefix, -1, s) * scalar) % s)
        prefix *= s
    return tuple(result)


def interval_rotation(data, shape, primes, axis, inverse):
    """Two-piece valid-interval rotation in every controlling prefix fiber.

    Materialized lists model the already charged stream scans, not RAM access
    as a complexity claim. Every target block is copied in the output pass;
    the complete spectator suffix remains attached to its record.
    """
    suffix = math.prod(shape[axis + 1:])
    target = shape[axis]
    valid = primes[axis]
    result = []
    prefix_position = 0
    for prefix_digits in points(shape[:axis]):
        offset = 0
        if all(a < s for a, s in zip(prefix_digits, primes)):
            prefix_modulus = math.prod(primes[:axis])
            offset = pow(prefix_modulus, -1, valid) * scalar_index(prefix_digits, primes[:axis]) % valid
        if inverse:
            offset = (-offset) % valid
        start = prefix_position * target * suffix
        block = data[start:start + target * suffix]
        split = (valid - offset) * suffix
        result.extend(block[split:valid * suffix])
        result.extend(block[:split])
        result.extend(block[valid * suffix:])
        prefix_position += 1
    assert len(result) == len(data)
    return result, {"axis": axis, "inverse": inverse, "input_records_read": len(data),
                    "output_records_written": len(data),
                    "two_piece_copy_record_upper_bound": 4 * len(data)}


def run_shape(primes):
    shape = tuple(1 << (s - 1).bit_length() for s in primes)
    volume = math.prod(shape)
    source = [scalar_index(a, primes) if all(ai < s for ai, s in zip(a, primes)) else None
              for a in points(shape)]
    data = source
    movements = []
    for axis in range(len(primes) - 1, 0, -1):
        data, charge = interval_rotation(data, shape, primes, axis, False)
        movements.append(charge)
    expected = [None] * volume
    hamming_negative = None
    for a in points(primes):
        b = direct_crt(a, primes)
        index = encode(b, shape)
        assert expected[index] is None
        expected[index] = scalar_index(a, primes)
        wa = sum(x.bit_count() for x in a)
        wb = sum(x.bit_count() for x in b)
        if wa != wb and hamming_negative is None:
            hamming_negative = {"input_digits": a, "crt_digits": b,
                                "input_binary_weight": wa, "output_binary_weight": wb}
    assert data == expected
    inverse = data
    for axis in range(1, len(primes)):
        inverse, charge = interval_rotation(inverse, shape, primes, axis, True)
        movements.append(charge)
    assert inverse == source
    ordered_crt_labels = [expected[encode(b, shape)] for b in points(primes)]
    descent = next(({"target_position": i, "previous_scalar_source": a, "next_scalar_source": b}
                    for i, (a, b) in enumerate(zip(ordered_crt_labels, ordered_crt_labels[1:]), 1) if a > b), None)
    assert descent is not None
    # A single input head reading the scalar stream in target order has this
    # exact traversal length, without cached split streams or a new router.
    single_head_traversal = abs(ordered_crt_labels[0]) + sum(abs(a - b) for a, b in zip(ordered_crt_labels, ordered_crt_labels[1:]))
    assert hamming_negative is not None
    return {"primes": primes, "padded_binary_shape": shape, "valid_records": math.prod(primes),
            "padded_records": volume, "scheduled_rotations": len(movements),
            "charged_payload_record_reads": sum(x["input_records_read"] for x in movements),
            "charged_payload_record_writes": sum(x["output_records_written"] for x in movements),
            "two_piece_record_upper_bound": sum(x["two_piece_copy_record_upper_bound"] for x in movements),
            "negative_known_bit_permutation": hamming_negative,
            "negative_monotone_scalar_stream_embedding": descent,
            "uncached_single_head_traversal_record_steps": single_head_traversal,
            "movements": movements}


def alignment_control():
    primes = (3, 5)
    a = (2, 0)
    b = (1, 0)
    plain_sum = tuple((x + y) % s for x, y, s in zip(a, b, primes))
    scalar_sum = (scalar_index(a, primes) + scalar_index(b, primes)) % math.prod(primes)
    wrong_scalar = scalar_index(plain_sum, primes)
    assert scalar_sum == 3 and wrong_scalar == 0
    crt_a, crt_b = direct_crt(a, primes), direct_crt(b, primes)
    crt_sum = tuple((x + y) % s for x, y, s in zip(crt_a, crt_b, primes))
    desired_digits = (scalar_sum % 3, scalar_sum // 3)
    assert crt_sum == direct_crt(desired_digits, primes)
    return {"primes": primes, "first_input_digit": a, "second_input_digit": b,
            "ordinary_cyclic_convolution_output": scalar_sum,
            "wrong_unrouted_tensor_output": wrong_scalar, "crt_first": crt_a,
            "crt_second": crt_b, "crt_tensor_output": crt_sum}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    start = perf_counter()
    rows = [run_shape(shape) for shape in ((3, 5), (3, 5, 7), (11, 13, 17), (5, 7, 11, 13), (7, 11, 13, 17))]
    result = {"status": "CRT rotations and scoped replacement negatives passed",
              "workers": 1, "seconds": perf_counter() - start,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "rows": rows, "negative_carry_alignment": alignment_control(),
              "limitations": ["charged existing two-piece schedule, not a universal fixed-tape lower bound",
                              "finite certificate does not grant faster computed-key sorting",
                              "a new joint modular arithmetic router remains open"]}
    (out / "certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "seconds": result["seconds"],
                      "records": sum(x["valid_records"] for x in rows),
                      "reads": sum(x["charged_payload_record_reads"] for x in rows)}))


if __name__ == "__main__":
    main()
