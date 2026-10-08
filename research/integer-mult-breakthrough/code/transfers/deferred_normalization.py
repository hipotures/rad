#!/usr/bin/env python3
"""Exact finite controls for fusing transforms across normalization boundaries.

This explores a representation hypothesis, not a fast multiplication theorem.
Finite-field transforms are auxiliary exact controls, not a replacement for the
Gaussian-dyadic algorithm or its fixed-tape and precision obligations.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from math import comb
from pathlib import Path
import random
import time


PRIME = 65537


def root_for(length):
    if length < 2 or length & (length - 1) or (PRIME - 1) % length:
        raise ValueError("unsupported transform length")
    for candidate in range(2, PRIME):
        root = pow(candidate, (PRIME - 1) // length, PRIME)
        if pow(root, length, PRIME) == 1 and pow(root, length // 2, PRIME) != 1:
            return root
    raise AssertionError("root not found")


def transform(values, inverse=False):
    length = len(values)
    root = root_for(length)
    if inverse:
        root = pow(root, -1, PRIME)
    scale = pow(length, -1, PRIME) if inverse else 1
    return [scale * sum(value * pow(root, j * k, PRIME)
                        for j, value in enumerate(values)) % PRIME
            for k in range(length)]


def convolution(first, second):
    result = [0] * (len(first) + len(second) - 1)
    for i, a in enumerate(first):
        for j, b in enumerate(second):
            result[i + j] += a * b
    return result


def pad(values, length):
    if len(values) > length:
        raise ValueError("complete coefficient payload does not fit")
    return list(values) + [0] * (length - len(values))


def evaluation(values, base):
    return sum(value * base**j for j, value in enumerate(values))


def carry_normalize(values, base):
    if base < 2 or any(value < 0 for value in values):
        raise ValueError("these controls use nonnegative radix coefficients")
    carry, output = 0, []
    for value in values:
        value, carry = divmod(value + carry, base)
        # divmod returns quotient and remainder, whereas the output is the digit.
        output.append(carry)
        carry = value
    while carry:
        carry, digit = divmod(carry, base)
        output.append(digit)
    return output


def bit_widths(values):
    return sum(max(1, value.bit_length()) for value in values)


def exact_product_via_transform(first, second, length):
    expected = convolution(first, second)
    if len(expected) > length or max(expected) >= PRIME:
        raise ValueError("padding or coefficient-modulus budget is insufficient")
    first_spectrum = transform(pad(first, length))
    second_spectrum = transform(pad(second, length))
    pointwise = [a * b % PRIME for a, b in zip(first_spectrum, second_spectrum)]
    recovered = transform(pointwise, inverse=True)
    if recovered != pad(expected, length):
        raise AssertionError("finite transform disagrees with direct integer convolution")
    return expected, pointwise


def case_family(task):
    family, seed, cases = task
    rng = random.Random(seed)
    started = time.monotonic()
    checks = differing_boundaries = 0
    witness = None
    for index in range(cases):
        length = [4, 8, 16, 32][index % 4]
        base = [4, 8, 16][index % 3]
        width = max(2, length // 4)
        first = [rng.randrange(base) for _ in range(width)]
        second = [rng.randrange(base) for _ in range(width)]
        if family == "normalization-boundary":
            first[0] = second[0] = base - 1
            coefficients, spectrum = exact_product_via_transform(first, second, length)
            normalized = carry_normalize(coefficients, base)
            if evaluation(coefficients, base) != evaluation(normalized, base):
                raise AssertionError("normalization changed the integer value")
            if len(normalized) > length:
                raise AssertionError("selected normalized control unexpectedly overflows")
            normalized_spectrum = transform(pad(normalized, length))
            if normalized_spectrum == spectrum:
                raise AssertionError("forced nontrivial carry did not change the spectral boundary")
            differing_boundaries += 1
            witness = witness or {"base": base, "input_a": first, "input_b": second,
                                   "unnormalized": coefficients, "normalized": normalized,
                                   "spectrum_before": spectrum,
                                   "spectrum_after": normalized_spectrum}
        elif family == "redundant-linear-domain":
            third = [rng.randrange(base) for _ in range(width)]
            coefficients, spectrum = exact_product_via_transform(first, second, length)
            added = [a + b for a, b in zip(pad(coefficients, length), pad(third, length))]
            spectrum_added = [(a + b) % PRIME for a, b in
                              zip(spectrum, transform(pad(third, length)))]
            if transform(spectrum_added, inverse=True) != added:
                raise AssertionError("redundant linear addition failed")
            normalized = carry_normalize(added, base)
            if evaluation(normalized, base) != (evaluation(first, base) * evaluation(second, base)
                                                + evaluation(third, base)):
                raise AssertionError("final deferred recovery failed")
            witness = witness or {"base": base, "redundant": added,
                                   "normalized_final": normalized,
                                   "exact_value": evaluation(normalized, base),
                                   "raw_coefficient_bits": bit_widths(added),
                                   "canonical_digit_bits": bit_widths(normalized)}
        elif family == "carry-free-domain":
            # Enlarging the base is paid explicitly; it is not the original format.
            coefficients, spectrum = exact_product_via_transform(first, second, length)
            guarded_base = 1 << max(1, (max(coefficients) + 1).bit_length())
            normalized = carry_normalize(coefficients, guarded_base)
            if normalized != coefficients:
                raise AssertionError("the explicitly guarded domain is not carry-free")
            if transform(pad(normalized, length)) != spectrum:
                raise AssertionError("the lawful inverse/forward cancellation failed")
            witness = witness or {"original_base": base, "guarded_base": guarded_base,
                                   "original_digit_bits": base.bit_length() - 1,
                                   "guarded_digit_bits": guarded_base.bit_length() - 1,
                                   "coefficient_count": len(coefficients),
                                   "claim": "Format changed; this is not equality of evaluations at different bases."}
        else:
            # Digit extraction is a nonlinear interface even before full carry.
            x = base - 1
            y = 1
            low_after_sum = (x + y) % base
            sum_after_low = (x % base) + (y % base)
            if low_after_sum == sum_after_low:
                raise AssertionError("digit extraction negative did not discriminate")
            encoded = [x, 0, 0, 0]
            encoded_other = [y, 0, 0, 0]
            combined = [a + b for a, b in zip(encoded, encoded_other)]
            normalized = carry_normalize(combined, base)
            if transform(pad(normalized, 4)) == transform(combined):
                raise AssertionError("nonlinear digit boundary disappeared under a linear transform")
            witness = witness or {"base": base, "scalar_x": x, "scalar_y": y,
                                   "low_digit_after_sum": low_after_sum,
                                   "sum_of_low_digits": sum_after_low,
                                   "unnormalized": combined, "normalized": normalized}
        checks += 1
    return {"family": family, "seed": seed, "checks": checks,
            "changed_spectral_boundaries": differing_boundaries,
            "witness": witness, "seconds": time.monotonic() - started}


def capacity_controls():
    # Four linear factors have degree four; a length-four cyclic transform wraps.
    polynomial = [1]
    for _ in range(4):
        polynomial = convolution(polynomial, [1, 1])
    base, length = 4, 4
    spectrum = transform(pad([1, 1], length))
    aliased = transform([pow(x, 4, PRIME) for x in spectrum], inverse=True)
    correct = evaluation(polynomial, base)
    wrong = evaluation(aliased, base)
    if correct == wrong or correct - wrong != base**length - 1:
        raise AssertionError("missing degree capacity negative did not discriminate")
    guarded_spectrum = transform(pad([1, 1], 8))
    guarded = transform([pow(x, 4, PRIME) for x in guarded_spectrum], inverse=True)
    if guarded != pad(polynomial, 8):
        raise AssertionError("explicit degree capacity did not repair the alias")
    widths = []
    for factors in (2, 4, 8, 16, 32, 64, 128, 256):
        coefficients = [comb(factors, j) for j in range(factors + 1)]
        redundant = bit_widths(coefficients)
        canonical = pow(3, factors).bit_length()
        # The central coefficient certifies a linear per-coefficient precision demand.
        lower_bound = Fraction(1 << factors, factors + 1)
        if max(coefficients) < lower_bound:
            raise AssertionError("binomial width lower bound failed")
        widths.append({"factors": factors, "degree": factors,
                       "minimum_power_of_two_transform_length": 1 << factors.bit_length(),
                       "raw_variable_width_bits": redundant,
                       "canonical_integer_bits": canonical,
                       "center_coefficient_bits": max(coefficients).bit_length()})
    return {"missing_degree_capacity": {"base": base, "length": length,
                                         "true_coefficients": polynomial,
                                         "aliased_coefficients": aliased,
                                         "true_integer": correct, "aliased_integer": wrong,
                                         "repaired_length": 8},
            "redundant_binomial_widths": widths,
            "scope": "Multi-product stress case. Integer multiplication remains bilinear; this is not a lower bound against bilinear multilevel spectral representations."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cases", type=int, default=96)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.cases < 1:
        parser.error("workers and cases must be positive")
    if args.output is not None and args.output.exists():
        parser.error("output must be fresh")
    start = time.monotonic()
    families = ["normalization-boundary", "redundant-linear-domain",
                "carry-free-domain", "nonlinear-digit-extraction"]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        evidence = list(pool.map(case_family,
                        [(family, 2026100811 + i, args.cases) for i, family in enumerate(families)]))
    result = {"status": "EXACT_FINITE_SEMANTIC_AND_CAPACITY_CONTROLS",
              "recorded_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Finite-field auxiliary model for normalization interfaces; no Gaussian or fixed-tape multiplier certificate.",
              "prime": PRIME, "transform_lengths": [4, 8, 16, 32],
              "workers": args.workers, "families": evidence,
              "capacity_controls": capacity_controls(),
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "seconds": time.monotonic() - start}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": sum(x["checks"] for x in evidence),
                      "workers": args.workers, "seconds": result["seconds"],
                      "alias_witness": result["capacity_controls"]["missing_degree_capacity"]}))


if __name__ == "__main__":
    main()
