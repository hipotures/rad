#!/usr/bin/env python3
"""Exact controls for a paid packed constant-address translation extension.

The eight-rotation word and guard constants specialize the original selected
XOR proof at openai/math adc7f1241b42e322a6451854ab7e4b4c146bf78a, 05-layers.tex
(SHA256 20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594).
Controls are constant one. Finite address permutations do not themselves
prove the conditional fixed-tape component cost assumptions used in the note.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import time


WORD = ((0, -1, 0), (1, -1, 0), (0, 1, 0), (1, 1, 0),
        (1, 1, 1), (0, 1, 1), (1, -1, 1), (0, -1, 1))


def positions(k, f, rho):
    if not k >= 1 or not f >= 1 or not 0 <= rho < k:
        raise ValueError("invalid complete equal-width packed chunks")
    return [rho + i * k for i in range(f - 1)]


def packed_word(y, z, k, f, rho, inverse=False):
    selected = positions(k, f, rho)
    modulus_mask = (1 << (k * f)) - 1
    word = reversed(WORD) if inverse else WORD
    for target, sign, parity in word:
        control = z if target == 0 else y
        offset = sum(1 << bit for bit in selected if (control >> bit & 1) == parity)
        if inverse:
            sign = -sign
        if target == 0:
            y = (y + sign * offset) & modulus_mask
        else:
            z = (z + sign * offset) & modulus_mask
    return y, z


def exceptional(y, z, k, f, rho):
    mask = (1 << (k - 1)) - 1
    return any(not 10 <= (value >> (bit + 1) & mask) <= (1 << (k - 1)) - 11
               for value in (y, z) for bit in positions(k, f, rho))


def ideal_omitted_top(y, z, k, f, rho):
    return y ^ sum(1 << bit for bit in positions(k, f, rho)), z


def repair(y, z, k, f, rho):
    if not exceptional(y, z, k, f, rho):
        return y, z
    old_y, old_z = packed_word(y, z, k, f, rho, inverse=True)
    return ideal_omitted_top(old_y, old_z, k, f, rho)


def complete_program(y, z, k, f, rho):
    current = packed_word(y, z, k, f, rho)
    fixed_y, fixed_z = repair(*current, k, f, rho)
    # A fixed two-bit permutation, NOT on y and identity on its companion,
    # supplies the one selected position omitted by the packed stage.
    return fixed_y ^ (1 << (rho + (f - 1) * k)), fixed_z


def safe_address(rng, k, f, rho):
    value = rng.randrange(1 << (k * f))
    guard_mask = (1 << (k - 1)) - 1
    for bit in positions(k, f, rho):
        guard = rng.randrange(10, (1 << (k - 1)) - 10)
        value = (value & ~(guard_mask << (bit + 1))) | (guard << (bit + 1))
    return value


def check_case(task):
    k, f, rho, seed, samples = task
    started = time.monotonic()
    used = positions(k, f, rho)
    period = 1 << (max(used) + 1) if used else 1
    size = 1 << (k * f)
    if period > 512:
        raise ValueError("this exact finite discriminator caps representative periods at512")
    wrong = 0
    witness = None
    for y in range(period):
        for z in range(period):
            q = packed_word(y, z, k, f, rho)
            if packed_word(*q, k, f, rho, inverse=True) != (y, z):
                raise AssertionError("the literal eight-rotation inverse failed")
            ideal = ideal_omitted_top(y, z, k, f, rho)
            if q != ideal:
                wrong += 1
                if witness is None:
                    witness = {"input": [y, z], "eight_rotation_output": list(q),
                               "desired_output_before_top_bit": list(ideal)}
    rng = random.Random(seed)
    good_count, bad_count = 0, 0
    for i in range(samples):
        if k >= 6 and i % 2 == 0:
            y, z = safe_address(rng, k, f, rho), safe_address(rng, k, f, rho)
        else:
            y, z = rng.randrange(size), rng.randrange(size)
        q = packed_word(y, z, k, f, rho)
        bad = exceptional(y, z, k, f, rho)
        if not bad and q != ideal_omitted_top(y, z, k, f, rho):
            raise AssertionError("constant controls violate the no-carry guard proof")
        if exceptional(*q, k, f, rho) != bad:
            raise AssertionError("the packed stage does not preserve its exceptional bank")
        fixed = complete_program(y, z, k, f, rho)
        expected = y ^ sum(1 << (rho + j * k) for j in range(f)), z
        if fixed != expected:
            raise AssertionError("paid repair/top-bit completion failed or dirty guard was not restored")
        # Predicate positions are below period. Verify the exact equivariance
        # used to reduce the full rectangle to representative residues.
        dy = rng.randrange(size // period) * period
        dz = rng.randrange(size // period) * period
        shifted_q = packed_word((y + dy) % size, (z + dz) % size, k, f, rho)
        if shifted_q != ((q[0] + dy) % size, (q[1] + dz) % size):
            raise AssertionError("representative reduction lost a higher chunk quotient")
        good_count += not bad
        bad_count += bad
    wrong_fraction = Fraction(wrong, period * period)
    bound = min(Fraction(1), Fraction(80 * (f - 1), 1 << k))
    if k >= 6 and wrong_fraction > bound:
        raise AssertionError("full-rectangle failure mass exceeds the guarded bound")
    if used and f >= 3 and wrong == 0:
        raise AssertionError("omitted-repair negative unexpectedly stopped discriminating")
    return {"k": k, "f": f, "rho": rho, "seed": seed,
            "native_guard_parameter_contract": k >= 6,
            "complete_range_per_chunk": size,
            "two_chunk_rectangle_records": size * size,
            "exact_representative_period": period,
            "exact_representative_pairs": period * period,
            "failure_pairs_without_repair": wrong,
            "exact_full_rectangle_failure_fraction_without_repair": str(wrong_fraction),
            "complete_guard_union_bound": str(bound),
            "sampled_complete_addresses": samples,
            "sampled_nonexceptional_addresses": good_count,
            "sampled_exceptional_addresses": bad_count,
            "dirty_guard_restored": True, "eight_rotation_inverse_verified": True,
            "higher_quotient_equivariance_verified": True,
            "omitted_repair_witness": witness,
            "seconds": time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--small", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    utc_started = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    samples = 256 if args.small else 4096
    tasks = [(6, 1, 5, 202610081100, samples),
             (6, 2, 5, 202610081101, samples),
             (2, 3, 0, 202610081102, samples),
             (3, 3, 0, 202610081103, samples)]
    if not args.small:
        tasks.extend([(6, 3, 2, 202610081104, samples),
                      (8, 3, 0, 202610081105, samples),
                      (4, 4, 0, 202610081106, samples)])
    if args.workers == 1:
        cases = [check_case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(check_case, tasks))
    result = {"status": "PASS", "scope": "Exact finite constant-control packed translation and analytical quotient reduction; conditional fixed-tape cost relies on stated original components, not on random-access array timing.",
              "utc_started_at": utc_started,
              "utc_completed_at": datetime.now(timezone.utc).isoformat(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "workers": args.workers, "small": args.small,
              "cases": cases, "case_count": len(cases),
              "exact_representative_pairs": sum(c["exact_representative_pairs"] for c in cases),
              "sampled_complete_addresses": sum(c["sampled_complete_addresses"] for c in cases),
              "seconds": time.monotonic() - started}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "scope", "workers", "small", "case_count", "exact_representative_pairs", "sampled_complete_addresses", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
