#!/usr/bin/env python3
"""Exact address controls for guarded batched CRT interval rotations.

This models ordinary prefix-controlled binary rotations and known coordinate
layout changes. Conditional target-word complementation is the only separate
BIT fanout primitive; its transfer from the inherited masked-bit identity is
specified in the accompanying report, not proved by this finite checker.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import time


def pack(values, widths):
    word = shift = 0
    for value, width in zip(values, widths):
        word |= value << shift
        shift += width
    return word


def unpack(word, widths):
    values = []
    for width in widths:
        values.append(word & ((1 << width) - 1))
        word >>= width
    return tuple(values)


def batched_add(y, guards, offsets, widths, guard_width):
    """Two actual ordinary modular rotations, with layout changes between.

    First, Y_i followed by its dirty high guard is one packed field. Then
    routing puts all completed Y_i before packed guard digits. Carry repair
    depends only on those earlier completed target values and fixed offsets.
    """
    joined_widths = tuple(width + guard_width for width in widths)
    joined = tuple(x | (g << width) for x, g, width in zip(y, guards, widths))
    first_offset = pack(offsets, joined_widths)
    whole = (pack(joined, joined_widths) + first_offset) % (1 << sum(joined_widths))
    joined_after = unpack(whole, joined_widths)
    targets = tuple(value & ((1 << width) - 1)
                    for value, width in zip(joined_after, widths))
    guards_after = tuple(value >> width for value, width in zip(joined_after, widths))
    carries = tuple(int(x < offset) for x, offset in zip(targets, offsets))
    digit_widths = (guard_width,) * len(widths)
    second = (pack(guards_after, digit_widths) - pack(carries, digit_widths)) % (
        1 << sum(digit_widths))
    return targets, unpack(second, digit_widths)


def inverse_batched_add(y, guards, offsets, widths, guard_width):
    carries = tuple(int(x < offset) for x, offset in zip(y, offsets))
    digit_widths = (guard_width,) * len(widths)
    before_cleanup = (pack(guards, digit_widths) + pack(carries, digit_widths)) % (
        1 << sum(digit_widths))
    guard_first = unpack(before_cleanup, digit_widths)
    joined_widths = tuple(width + guard_width for width in widths)
    joined = tuple(x | (g << width) for x, g, width in zip(y, guard_first, widths))
    before_addition = (pack(joined, joined_widths) - pack(offsets, joined_widths)) % (
        1 << sum(joined_widths))
    original = unpack(before_addition, joined_widths)
    return (tuple(value & ((1 << width) - 1) for value, width in zip(original, widths)),
            tuple(value >> width for value, width in zip(original, widths)))


def conditional_affine_reflection(y, guards, controls, centers, widths, guard_width):
    # Each source is the BIT parity of its corresponding dirty control digit.
    # A source may fan out to multiple target bits, all outside source slots.
    complemented = tuple(x ^ (((1 << width) - 1) if control & 1 else 0)
                         for x, control, width in zip(y, controls, widths))
    offsets = tuple((center % (1 << width)) if control & 1 else 0
                    for control, center, width in zip(controls, centers, widths))
    return batched_add(complemented, guards, offsets, widths, guard_width)


def inverse_conditional_affine_reflection(y, guards, controls, centers, widths, guard_width):
    offsets = tuple((center % (1 << width)) if control & 1 else 0
                    for control, center, width in zip(controls, centers, widths))
    y, guards = inverse_batched_add(y, guards, offsets, widths, guard_width)
    return (tuple(x ^ (((1 << width) - 1) if control & 1 else 0)
                  for x, control, width in zip(y, controls, widths)), guards)


def predicate(y, intervals):
    return tuple(int(a <= x < b) for x, (a, b) in zip(y, intervals))


def shift_controls(controls, bits, guard_width, sign):
    widths = (guard_width,) * len(controls)
    word = (pack(controls, widths) + sign * pack(bits, widths)) % (1 << sum(widths))
    return unpack(word, widths)


def partial_reflections(y, controls, guards, intervals, widths, guard_width):
    centers = tuple(a + b for a, b in intervals)
    y, guards = conditional_affine_reflection(y, guards, controls, centers,
                                              widths, guard_width)
    controls = shift_controls(controls, predicate(y, intervals), guard_width, 1)
    y, guards = conditional_affine_reflection(y, guards, controls, centers,
                                              widths, guard_width)
    controls = shift_controls(controls, predicate(y, intervals), guard_width, -1)
    return y, controls, guards


def inverse_partial_reflections(y, controls, guards, intervals, widths, guard_width):
    centers = tuple(a + b for a, b in intervals)
    controls = shift_controls(controls, predicate(y, intervals), guard_width, 1)
    y, guards = inverse_conditional_affine_reflection(y, guards, controls, centers,
                                                      widths, guard_width)
    controls = shift_controls(controls, predicate(y, intervals), guard_width, -1)
    y, guards = inverse_conditional_affine_reflection(y, guards, controls, centers,
                                                      widths, guard_width)
    return y, controls, guards


def direct_partial(y, intervals):
    return tuple(a + b - 1 - x if a <= x < b else x
                 for x, (a, b) in zip(y, intervals))


def rotations(y, controls, guards, moduli, offsets, widths, guard_width):
    # Right rotation of [0,s) by f: reverse all, then the first f and last s-f.
    for intervals in (
        tuple((0, s) for s in moduli),
        tuple((0, f) for f in offsets),
        tuple((f, s) for f, s in zip(offsets, moduli)),
    ):
        y, controls, guards = partial_reflections(y, controls, guards, intervals,
                                                  widths, guard_width)
    return y, controls, guards


def inverse_rotations(y, controls, guards, moduli, offsets, widths, guard_width):
    intervals_all = (
        tuple((0, s) for s in moduli),
        tuple((0, f) for f in offsets),
        tuple((f, s) for f, s in zip(offsets, moduli)),
    )
    for intervals in reversed(intervals_all):
        y, controls, guards = inverse_partial_reflections(y, controls, guards, intervals,
                                                          widths, guard_width)
    return y, controls, guards


def direct_rotation(y, moduli, offsets):
    return tuple((x + f) % s if x < s else x
                 for x, s, f in zip(y, moduli, offsets))


def exhaustive_case(widths, guard_width, intervals, also_rotation):
    started = time.monotonic()
    count = good = negative_without_unload = bad_mismatches = 0
    seen = set()
    limit = (1 << guard_width) - 1
    ranges = [range(1 << width) for width in widths]
    controls_ranges = [range(1 << guard_width)] * len(widths)
    states_widths = widths + (guard_width,) * (2 * len(widths))
    for values in itertools.product(*ranges, *controls_ranges, *controls_ranges):
        m = len(widths)
        y, controls, guards = values[:m], values[m:2*m], values[2*m:]
        output = partial_reflections(y, controls, guards, intervals, widths, guard_width)
        encoded = pack(output[0] + output[1] + output[2], states_widths)
        assert encoded not in seen, (widths, intervals, values, output, "not bijective")
        seen.add(encoded)
        target = direct_partial(y, intervals)
        count += 1
        is_good = all(value < limit for value in controls + guards)
        if is_good:
            assert output == (target, controls, guards), (values, output, target)
            good += 1
            # An un-restored load always changes a nonempty predicate digit.
            negative_without_unload += int(any(predicate(y, intervals)))
        else:
            bad_mismatches += int(output != (target, controls, guards))
    assert len(seen) == count == (1 << sum(states_widths))
    result = {"widths": widths, "guard_width": guard_width, "intervals": intervals,
              "complete_states": count, "good_states": good,
              "bad_states_requiring_repair": bad_mismatches,
              "omitted_unload_negative_states": negative_without_unload,
              "bijection": True, "good_state_identity": True,
              "wall_seconds": time.monotonic() - started}
    if also_rotation:
        moduli = tuple((1 << width) - 1 for width in widths)
        offsets = tuple(max(1, s // 2) for s in moduli)
        rotation_states = 0
        for y in itertools.product(*ranges):
            for control in (0, 1, limit - 1):
                controls = (control,) * len(widths)
                guards = (limit - 1,) * len(widths)
                actual = rotations(y, controls, guards, moduli, offsets, widths,
                                   guard_width)
                expected = direct_rotation(y, moduli, offsets)
                assert actual == (expected, controls, guards), (y, actual, expected)
                rotation_states += 1
        result["odd_rotation_good_states"] = rotation_states
    return result


def crt_recursive(value, primes):
    if len(primes) == 1:
        return (value,)
    split = len(primes) // 2
    left, right = primes[:split], primes[split:]
    sl, sr = math.prod(left), math.prod(right)
    a, b = value % sl, value // sl
    c = (b + pow(sl, -1, sr) * a) % sr
    return crt_recursive(a, left) + crt_recursive(c, right)


def crt_cases():
    cases = []
    for primes in ((3, 5), (3, 5, 7), (3, 5, 7, 11), (3, 5, 7, 11, 13)):
        prefix = 1
        multipliers = []
        for s in primes:
            multipliers.append(pow(prefix, -1, s))
            prefix *= s
        outputs = set()
        for k in range(prefix):
            result = crt_recursive(k, primes)
            oracle = tuple(mu * k % s for mu, s in zip(multipliers, primes))
            assert result == oracle, (primes, k, result, oracle)
            outputs.add(result)
        assert len(outputs) == prefix
        cases.append({"primes": primes, "complete_states": prefix,
                      "crt_leaf_oracle": True, "bijection": True})
    return cases


def complete_repair_case(widths, guard_width, moduli, offsets):
    started = time.monotonic()
    m = len(widths)
    full_widths = widths + (guard_width,) * (2*m)
    count = 1 << sum(full_widths)
    observed = [-1] * count
    expected = [-1] * count
    limit = (1 << guard_width) - 1
    ranges = [range(1 << width) for width in full_widths]
    for values in itertools.product(*ranges):
        y, controls, guards = values[:m], values[m:2*m], values[2*m:]
        original = pack(values, full_widths)
        result = rotations(y, controls, guards, moduli, offsets, widths, guard_width)
        destination = pack(result[0] + result[1] + result[2], full_widths)
        assert observed[destination] == -1
        observed[destination] = original
        ideal = direct_rotation(y, moduli, offsets)
        expected[pack(ideal + controls + guards, full_widths)] = original
        inverse = inverse_rotations(*result, moduli, offsets, widths, guard_width)
        assert inverse == (y, controls, guards), (values, result, inverse)
    # Actual repair key uses the explicit inverse program, never an inverse table.
    extracted = []
    good = bad = wrong_before = 0
    for destination, payload in enumerate(observed):
        values = unpack(destination, full_widths)
        y, controls, guards = values[:m], values[m:2*m], values[2*m:]
        is_good = all(value < limit for value in controls + guards)
        wrong_before += int(payload != expected[destination])
        if is_good:
            good += 1
            assert payload == expected[destination]
            continue
        bad += 1
        original = inverse_rotations(y, controls, guards, moduli, offsets, widths,
                                     guard_width)
        assert pack(original[0] + original[1] + original[2], full_widths) == payload
        key_y = direct_rotation(original[0], moduli, offsets)
        key = pack(key_y + original[1] + original[2], full_widths)
        extracted.append((key, payload))
    # Stable binary radix passes model the ordinary sparse fixed-tape repair.
    for position in range(sum(full_widths)):
        zeros = [record for record in extracted if not ((record[0] >> position) & 1)]
        ones = [record for record in extracted if (record[0] >> position) & 1]
        extracted = zeros + ones
    assert all(extracted[i][0] < extracted[i+1][0] for i in range(len(extracted)-1))
    repaired = observed[:]
    for key, payload in extracted:
        repaired[key] = payload
    assert repaired == expected
    return {"widths": widths, "guard_width": guard_width, "moduli": moduli,
            "offsets": offsets, "complete_states": count, "good_states": good,
            "bad_states": bad, "wrong_before_repair": wrong_before,
            "explicit_inverse": True, "stable_radix_repair": True,
            "wall_seconds": time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--extended", action="store_true")
    parser.add_argument("--complete-repair", action="store_true")
    parser.add_argument("--four-target-repair", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    if args.four_target_repair:
        results = []
        for specification in (
            ((2, 3, 3, 4), 1, (3, 5, 7, 13), (2, 4, 1, 12)),
            ((2, 3, 3, 4), 1, (3, 7, 5, 15), (1, 6, 4, 14)),
        ):
            result = complete_repair_case(*specification)
            results.append(result)
            print(json.dumps({"completed": len(results), "case": result}), flush=True)
        certificate = {
            "run_id": "20261008T1408Z-crt-four-target-repair", "status": "PASS",
            "scope": "Four target words, unequal odd moduli, extreme offsets, complete permutation/inverse/repair; G=1 deliberately exposes all guard boundaries",
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "cases": results, "wall_seconds": time.monotonic() - started,
            "workers": 1, "native_threads": 1,
        }
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(certificate, indent=2) + "\n")
        print(json.dumps({"status": "PASS", "total_wall_seconds": certificate["wall_seconds"]}), flush=True)
        return
    if args.complete_repair:
        results = []
        for specification in (
            ((2, 2), 2, (3, 3), (1, 2)),
            ((2, 3), 2, (3, 5), (2, 3)),
            ((3, 3), 2, (5, 7), (4, 2)),
            ((2, 2, 3), 2, (3, 3, 7), (1, 2, 6)),
            ((2, 2, 3), 2, (3, 3, 5), (2, 1, 4)),
        ):
            result = complete_repair_case(*specification)
            results.append(result)
            print(json.dumps({"completed": len(results), "case": result}), flush=True)
        certificate = {
            "run_id": "20261008T1404Z-crt-guards-complete-repair", "status": "PASS",
            "scope": "Complete three-reflection address permutations, explicit inverse and actual sparse radix repair",
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "cases": results, "wall_seconds": time.monotonic() - started,
            "workers": 1, "native_threads": 1,
        }
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(certificate, indent=2) + "\n")
        print(json.dumps({"status": "PASS", "total_wall_seconds": certificate["wall_seconds"]}), flush=True)
        return
    specifications = [
        ((2, 2), 2, ((0, 3), (1, 4))),
        ((2, 3), 2, ((1, 3), (0, 7))),
        ((3, 3), 2, ((2, 7), (0, 5))),
        ((2, 2, 2), 2, ((0, 3), (1, 4), (1, 3))),
    ]
    if args.extended:
        specifications.extend([
            ((2, 2, 3), 2, ((0, 3), (1, 4), (2, 7))),
            ((2, 2, 3), 2, ((1, 4), (0, 2), (0, 7))),
            ((3, 3), 3, ((1, 7), (0, 8))),
            ((3, 4), 2, ((0, 7), (3, 14))),
        ])
    results = []
    for specification in specifications:
        result = exhaustive_case(*specification, also_rotation=True)
        results.append(result)
        print(json.dumps({"completed": len(results), "case": result}), flush=True)
    certificate = {
        "run_id": "20261008T1400Z-crt-guards-extended" if args.extended else
                  "20261008T1400Z-crt-guards",
        "status": "PASS", "scope": "Finite address identities; machine transfer remains a written lemma",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cases": results, "crt_tree_cases": crt_cases(),
        "wall_seconds": time.monotonic() - started, "workers": 1,
        "native_threads": 1,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(certificate, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "total_wall_seconds": certificate["wall_seconds"]}),
          flush=True)


if __name__ == "__main__":
    main()
