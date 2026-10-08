#!/usr/bin/env python3
"""Independent full-payload review of the arbitrary quadratic-phase interface.

The compiled auxiliary arrays use exactly one tensor of the dyadic C kernel,
unit phases, and explicit affine address movement. No complex-track code is
imported. This does not supply a fixed-tape router or all-size precision proof.
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


def dot(a, b):
    return (a & b).bit_count() % 2


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def image(columns, value):
    result = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            result ^= column
    return result


def qcanonical(columns, value):
    result = 0
    for i in range(len(columns)):
        if value >> i & 1:
            result += columns[i] >> i & 1
            for j in range(i + 1, len(columns)):
                if value >> j & 1:
                    result += 2 * (columns[j] >> i & 1)
    return result % 4


def qvalue(columns, linear, value):
    return (qcanonical(columns, value) + 2 * dot(linear, value)) % 4


def normal_form(columns, linear):
    """Congruence basis for I_r or alternating J pairs, followed by radical."""
    h = len(columns)
    if any((columns[i] >> j & 1) != (columns[j] >> i & 1)
           for i in range(h) for j in range(h)):
        raise ValueError("polar matrix is not symmetric")
    def pairing(a, b):
        return dot(a, image(columns, b))
    remaining = [1 << i for i in range(h)]
    singles, pairs = [], []
    while remaining:
        anisotropic = next((v for v in remaining if pairing(v, v)), None)
        if anisotropic is None:
            break
        singles.append(anisotropic)
        remaining = [w ^ (anisotropic if pairing(anisotropic, w) else 0)
                     for w in remaining if w != anisotropic]
    while remaining:
        partner = next(((u, v) for i, u in enumerate(remaining)
                        for v in remaining[i + 1:] if pairing(u, v)), None)
        if partner is None:
            break
        u, v = partner
        pairs.append((u, v))
        remaining = [w ^ (u if pairing(v, w) else 0)
                     ^ (v if pairing(u, w) else 0)
                     for w in remaining if w != u and w != v]
    alternating = not singles
    if singles:
        # I_1 plus J_2 is congruent to I_3; absorb every alternating block.
        for u, v in pairs:
            c = singles.pop()
            singles.extend((c ^ u, c ^ v, c ^ u ^ v))
        selected = singles
    else:
        selected = [v for pair in pairs for v in pair]
    basis = selected + remaining
    r = len(selected)
    if rank(basis) != h or r != rank(columns):
        raise AssertionError("normal form did not preserve rank or full cube")
    for i, u in enumerate(basis):
        for j, v in enumerate(basis):
            expected = int(i < r and j < r and
                           ((j == (i ^ 1)) if alternating else (i == j)))
            if pairing(u, v) != expected:
                raise AssertionError("binary congruence identity failed")
    diagonal = [qvalue(columns, linear, v) for v in basis]
    if alternating:
        if r % 2 or any(value % 2 for value in diagonal):
            raise AssertionError("alternating quotient has invalid parity")
        shift = sum((value // 2) << j for j, value in enumerate(diagonal))
    else:
        if any(diagonal[j] not in (1, 3) for j in range(r)):
            raise AssertionError("nonalternating quotient has invalid diagonal")
        if any(value % 2 for value in diagonal[r:]):
            raise AssertionError("radical phase is not even")
        shift = sum((int(value == 3) if j < r else value // 2) << j
                    for j, value in enumerate(diagonal))
    for z in range(1 << h):
        reference = qvalue(columns, linear, image(basis, z))
        if alternating:
            expected = 2 * sum((z >> j & 1) * (z >> (j + 1) & 1)
                               for j in range(0, r, 2)) + 2 * dot(shift, z)
        else:
            expected = (z & ((1 << r) - 1)).bit_count() + 2 * dot(shift, z)
        if reference != expected % 4:
            raise AssertionError("Z4 congruence identity failed")
    return {"basis": basis, "rank": r, "alternating": alternating,
            "normal_shift": shift, "normal_diagonal": diagonal}


def rotate(value, power):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]


def walsh(values):
    result = [list(packet) for packet in values]
    width = 1
    while width < len(result):
        for start in range(0, len(result), 2 * width):
            for j in range(start, start + width):
                u, v = result[j], result[j + width]
                result[j] = [(a + c, b + d) for (a, b), (c, d) in zip(u, v)]
                result[j + width] = [(a - c, b - d) for (a, b), (c, d) in zip(u, v)]
        width *= 2
    return result


def column_address(address, h, columns_count, column):
    return sum((address >> (slot * columns_count + column) & 1) << slot
               for slot in range(h))


def direct_frame(values, columns, columns_count, inverse=False, linear=0):
    """Exact Fourier reference, not an efficient native implementation."""
    h = len(columns)
    size = 1 << (h * columns_count)
    if len(values) != size:
        raise ValueError("the complete selected address cube is required")
    spectrum = walsh(values)
    phased = []
    for address, packet in enumerate(spectrum):
        exponent = sum(qvalue(columns, linear, column_address(address, h, columns_count, c))
                       for c in range(columns_count))
        if inverse:
            exponent = -exponent
        phased.append([rotate(value, exponent) for value in packet])
    return [[(a / size, b / size) for a, b in packet] for packet in walsh(phased)]


def transpose_address(address, basis, columns_count):
    h = len(basis)
    result = 0
    for c in range(columns_count):
        old = column_address(address, h, columns_count, c)
        for i, vector in enumerate(basis):
            result |= dot(vector, old) << (i * columns_count + c)
    return result


def tensor_c(values, selected_width):
    """One complete C^tensor(selected_width) auxiliary child, no columns lost."""
    result = [list(packet) for packet in values]
    for bit in range(selected_width):
        stride = 1 << bit
        for start in range(0, len(result), 2 * stride):
            for j in range(start, start + stride):
                first, second = result[j], result[j + stride]
                forward, backward = [], []
                for (a, b), (c, d) in zip(first, second):
                    # C=((1+i)/2,(1-i)/2;(1-i)/2,(1+i)/2).
                    forward.append(((a - b + c + d) / 2,
                                    (a + b + d - c) / 2))
                    backward.append(((a + b + c - d) / 2,
                                     (b - a + c + d) / 2))
                result[j], result[j + stride] = forward, backward
    return result


def compiled_frame(values, columns, linear, columns_count, *, omit_translation=False,
                   omit_alternating_unit=False):
    nf = normal_form(columns, linear)
    h, r = len(columns), nf["rank"]
    width = h * columns_count
    if len(values) != 1 << width:
        raise ValueError("complete physical records must be retained")
    packet_width = len(values[0])
    if any(len(packet) != packet_width for packet in values):
        raise ValueError("payload fields cannot be cropped or misaligned")
    normal = [None] * len(values)
    for x, packet in enumerate(values):
        normal[transpose_address(x, nf["basis"], columns_count)] = list(packet)
    if any(packet is None for packet in normal):
        raise AssertionError("congruence router did not preserve the complete stream")
    selected_width = r * columns_count
    selected_mask = (1 << selected_width) - 1
    def paired_address(z):
        out = z & ~selected_mask
        for slot in range(0, r, 2):
            for c in range(columns_count):
                out |= (z >> (slot * columns_count + c) & 1) << ((slot + 1) * columns_count + c)
                out |= (z >> ((slot + 1) * columns_count + c) & 1) << (slot * columns_count + c)
        return out
    def chirp(z):
        return sum((z >> (slot * columns_count + c) & 1)
                   * (z >> ((slot + 1) * columns_count + c) & 1)
                   for slot in range(0, r, 2) for c in range(columns_count))
    if nf["alternating"]:
        if selected_width % 2:
            raise AssertionError("normalized real Hadamard would need an irrational gauge")
        normal = [[rotate(value, (z & selected_mask).bit_count() + 2 * chirp(z))
                   for value in packet] for z, packet in enumerate(normal)]
    transformed = tensor_c(normal, selected_width)
    if nf["alternating"]:
        unit = 0 if omit_alternating_unit else -selected_width // 2
        transformed = [[rotate(value, (z & selected_mask).bit_count() + unit)
                        for value in packet] for z, packet in enumerate(transformed)]
        transformed = [[rotate(value, 2 * chirp(z))
                        for value in transformed[paired_address(z)]] for z in range(len(transformed))]
    shift = 0 if omit_translation else sum(
        (nf["normal_shift"] >> slot & 1) << (slot * columns_count + c)
        for slot in range(h) for c in range(columns_count))
    # Both routes are literal record movement in this auxiliary array model.
    shifted = [transformed[z ^ shift] for z in range(len(transformed))]
    output = [shifted[transpose_address(y, nf["basis"], columns_count)]
              for y in range(len(values))]
    return output, {"ambient_slots": h, "columns": columns_count,
                    "polar_rank": r, "child_selected_width": selected_width,
                    "child_calls": int(r > 0), "quotient_alternating": nf["alternating"],
                    "complete_records": len(values), "fields_per_record": packet_width,
                    "basis": nf["basis"], "normal_shift": nf["normal_shift"],
                    "nonzero_radical_shift": bool(nf["normal_shift"] >> r),
                    "additional_denominator_bits_outside_child": 0,
                    "additional_magnitude_bits_outside_child": 0,
                    "affine_routing_proved_in_fixed_tape_model": False}


def symmetric_matrix(h, descriptor):
    columns = [0] * h
    bit = 0
    for i in range(h):
        for j in range(i, h):
            if descriptor >> bit & 1:
                columns[i] |= 1 << j
                columns[j] |= 1 << i
            bit += 1
    return columns


def dirty_values(h, columns_count, fields, seed):
    rng = random.Random(seed)
    return [[(Q(rng.randrange(-9, 10), 1 << rng.randrange(4)),
              Q(rng.randrange(-9, 10), 1 << rng.randrange(4))) for _ in range(fields)]
            for _ in range(1 << (h * columns_count))]


def review_case(case):
    started = time.monotonic()
    h, a, b, columns_count, seed, extra = case
    values = dirty_values(h, columns_count, 3, seed)
    difference = [u ^ v for u, v in zip(a, b)]
    correction = sum((int((a[i] >> i & 1) and not (b[i] >> i & 1))) << i for i in range(h))
    correction ^= extra
    if extra:
        expected = direct_frame(values, difference, columns_count, linear=correction)
    else:
        expected = direct_frame(direct_frame(values, a, columns_count, inverse=True),
                                b, columns_count)
    independent_difference = direct_frame(values, difference, columns_count, linear=correction)
    if independent_difference != expected:
        raise AssertionError("canonical frame-difference diagonal correction failed")
    compiled, ledger = compiled_frame(values, difference, correction, columns_count)
    if compiled != expected:
        raise AssertionError("literal dyadic child and paid auxiliary routes do not reproduce the frame")
    # Reversibility is checked with the actual inverse canonical difference.
    inverse_linear = correction ^ sum((difference[i] >> i & 1) << i for i in range(h))
    restored, _ = compiled_frame(compiled, difference, inverse_linear, columns_count)
    if restored != values:
        raise AssertionError("complete dirty payload did not restore under inverse frame change")
    return {"h": h, "a": a, "b": b, "extra_linear": extra,
            "seed": seed, "diagonal_correction": correction,
            "ledger": ledger, "dirty_restore_verified": True,
            "seconds": time.monotonic() - started}


def negative_controls():
    triangle, zero = [6, 5, 3], [0, 0, 0]
    data = dirty_values(3, 1, 3, 761010)
    exact = direct_frame(data, triangle, 1)
    missing, ledger = compiled_frame(data, triangle, 0, 1, omit_translation=True)
    if missing == exact or not ledger["nonzero_radical_shift"]:
        raise AssertionError("the omitted radical translation did not discriminate")
    radical = 7
    if image(triangle, radical) or qcanonical(triangle, radical) != 2:
        raise AssertionError("triangle radical witness is invalid")
    delta = [[(Q(int(x == 0)), Q())] for x in range(8)]
    kernel = direct_frame(delta, triangle, 1)
    support = [x for x, packet in enumerate(kernel) if packet != [(Q(), Q())]]
    if 0 in support or support != [1, 2, 4, 7]:
        raise AssertionError("affine-coset Fourier support witness failed")
    identity = [1, 2, 4]
    actual_inverse = direct_frame(data, identity, 1, inverse=True)
    missing_correction, _ = compiled_frame(data, identity, 0, 1)
    if actual_inverse == missing_correction:
        raise AssertionError("unpaid negative diagonal correction did not discriminate")
    j = [2, 1]
    alternate_data = dirty_values(2, 1, 3, 761011)
    alternate_exact = direct_frame(alternate_data, j, 1)
    missing_unit, _ = compiled_frame(alternate_data, j, 0, 1, omit_alternating_unit=True)
    if missing_unit == alternate_exact:
        raise AssertionError("unpaid alternating unit gauge did not discriminate")
    cropped = [[packet[0], (Q(), Q()), (Q(), Q())] for packet in data]
    wrong, _ = compiled_frame(cropped, triangle, 0, 1)
    if wrong == exact:
        raise AssertionError("the omitted complete payload fields did not discriminate")
    # A dyadic rational square cannot be 1/2: its reduced denominator exponent
    # is even. Thus real normalized H_1 cannot itself be a Gaussian dyadic gate.
    irrational_real_hadamard_rejected = all(2 * numerator * numerator != denominator * denominator
                                           for denominator in (1, 2, 4, 8, 16, 32)
                                           for numerator in range(denominator + 1))
    if not irrational_real_hadamard_rejected:
        raise AssertionError("bounded irrational-gauge control failed")
    return {"triangle_matrix_columns": triangle, "triangle_rank": 2,
            "radical_vector": radical, "q_on_radical": 2,
            "kernel_support_affine_coset": support, "zero_outside_support": True,
            "omitted_translation_rejected": True, "omitted_diagonal_correction_rejected": True,
            "omitted_alternating_unit_rejected": True, "cropped_payload_rejected": True,
            "odd_rank_real_normalized_hadamard_requires_irrational_scalar": True,
            "irrational_claim_scope": "Analytical reduced-denominator parity argument; bounded rational witnesses are only a regression control."}


def cases(small):
    output = []
    for descriptor in range(64 if not small else 8):
        output.append((3, [0, 0, 0], symmetric_matrix(3, descriptor), 1,
                       202610080000 + descriptor, 0))
    for h in (2, 3, 4, 5, 6):
        rng = random.Random(202610080100 + h)
        for j in range(12 if not small else 2):
            a = symmetric_matrix(h, rng.getrandbits(h * (h + 1) // 2))
            b = symmetric_matrix(h, rng.getrandbits(h * (h + 1) // 2))
            columns_count = 2 if h <= 4 and j < (4 if not small else 1) else 1
            output.append((h, a, b, columns_count, 202610081000 + h * 100 + j, 0))
    # Degenerate alternating, full alternating, rank-zero translation and
    # nonalternating radical phases are explicit, rather than left to sampling.
    output.extend(((3, [0, 0, 0], [6, 5, 3], 2, 202610085000, 0),
                   (4, [0, 0, 0, 0], [2, 1, 8, 4], 2, 202610085001, 0),
                   (3, [0, 0, 0], [0, 0, 0], 2, 202610085002, 7),
                   (3, [0, 0, 0], [1, 0, 0], 2, 202610085003, 6)))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    started = time.monotonic()
    tasks = cases(args.small)
    if args.workers == 1:
        results = [review_case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(review_case, tasks))
    controls = negative_controls()
    result = {"status": "PASS", "scope": "Independent exact auxiliary phase compilation and complete dirty-payload controls; fixed-tape affine routing, physical guard and all-size recursion remain unproved.",
              "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "workers": args.workers, "small": args.small,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cases": results, "case_count": len(results),
              "complete_records": sum(x["ledger"]["complete_records"] for x in results),
              "negative_controls": controls,
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "case_count", "complete_records", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
