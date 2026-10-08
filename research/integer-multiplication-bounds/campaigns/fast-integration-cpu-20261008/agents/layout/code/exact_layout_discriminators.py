#!/usr/bin/env python3
"""Independent exact movement and dimensional-volume discriminators.

No historical/public checker is imported. Results are finite accounting controls,
not proof of a Gaussian inverse or a complete multiplication exponent.
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


def halo_budget(seed):
    rng = Random(seed)
    examples = []
    for d in (1, 2, 3, 7, 16, 64, 257, 1024):
        halos = [rng.randrange(1, 10000) for _ in range(d)]
        # Individually polynomial fields, globally charged dimensional budget.
        sides = [1 << (8*d*a-1).bit_length() for a in halos]
        ratio = math.prod(Fraction(l+2*a, l) for a, l in zip(halos, sides))
        entropy_budget = sum((Fraction(2*a, l) for a, l in zip(halos, sides)), Fraction())
        assert entropy_budget <= Fraction(1, 4)
        assert ratio < Fraction(4, 3)
        stages = [ratio]
        for a, l in zip(halos, sides):
            stages.append(stages[-1]*Fraction(l, l+2*a))
        assert stages[-1] == 1
        assert max(stages) == ratio
        examples.append({"dimension": d, "halo_ratio_num_bits": ratio.numerator.bit_length(),
                         "halo_ratio_den_bits": ratio.denominator.bit_length(),
                         "ratio_float": float(ratio),
                         "entropy_budget_float": float(entropy_budget),
                         "simultaneous_binary_padding_ratio": str(2**d)})
    # A polynomial choice with a fixed relative halo has exponential dimension cost.
    bad = Fraction(5, 4)**128
    assert bad > 2**40
    return {"status": "exact finite controls passed", "examples": examples,
            "negative_fixed_relative_halo_D128_ratio": float(bad),
            "checks": "all axis crops only decrease persistent volume"}


def expose_fine_bit(data, prefix, spectator, suffix):
    """[prefix,2,spectator,suffix] -> [prefix,spectator,2,suffix].

    Complete spectator blocks are sequential on their own parity tape. Each
    record pays input read, parity write/read, final write, and charged resets.
    The Python lists model those tapes; no random index is a free tape operation.
    """
    assert len(data) == prefix*2*spectator*suffix
    out = []
    moves = 0
    for p in range(prefix):
        span = spectator*suffix
        start = p*2*span
        zero = data[start:start+span]
        one = data[start+span:start+2*span]
        moves += 4*span  # input read and parity writes
        for y in range(spectator):
            out.extend(zero[y*suffix:(y+1)*suffix])
            out.extend(one[y*suffix:(y+1)*suffix])
        moves += 4*span  # parity reads and output writes
        moves += 4*span  # both parity-head rewinds and output reset budget
    return out, moves


def exposure(seed):
    rng = Random(seed)
    cases = 0
    records = 0
    movement = 0
    stale_negative = None
    for _ in range(1600):
        prefix = rng.randrange(1, 7)
        fine_bits = rng.randrange(1, 7)
        fine = 1 << fine_bits
        spectator = rng.randrange(1, 25)
        # Move low bits one at a time, leaving high fine bits in the prefix.
        data = [(a, i, b) for a in range(prefix) for i in range(fine) for b in range(spectator)]
        current = data
        suffix = 1
        for k in range(fine_bits):
            current, count = expose_fine_bit(current, prefix*(fine >> (k+1)), spectator, suffix)
            movement += count
            suffix *= 2
        expected = [(a, i, b) for a in range(prefix) for b in range(spectator)
                    for i in range(fine)]
        assert current == expected
        assert count == 6*len(data)
        cases += 1
        records += len(data)
    # Length-changing return: old field-name/radix inverse is invalid.
    original = [(i, b) for i in range(4) for b in range(3)]
    exposed = [(i, b) for b in range(3) for i in range(4)]
    mapped = [(i, b) for b in range(3) for i in range(5)]
    correct = [(i, b) for i in range(5) for b in range(3)]
    stale = [mapped[i] for i in (0, 4, 8, 1, 5, 9, 2, 6, 10, 3, 7, 11)]
    assert exposed != original and stale != correct and len(stale) != len(correct)
    stale_negative = {"before_radix": 4, "after_radix": 5,
                      "stale_records": len(stale), "required_records": len(correct)}
    return {"status": "exact finite controls passed", "cases": cases,
            "records_checked": records, "charged_record_head_moves": movement,
            "movement_per_bit_bound": 6,
            "internal_bit_order": "preserved by complete current-suffix block interleave",
            "negative_stale_return": stale_negative}


def catalogue(seed):
    rng = Random(seed)
    cases = 0
    coefficient_reads = 0
    coefficients_wrong_if_constant_page = 0
    maximum_catalogue_fraction = Fraction()
    for _ in range(3500):
        x = rng.randrange(1, 8)
        j_count = rng.randrange(2, 40)
        y = rng.randrange(1, 30)
        block = 1 << rng.randrange(3, 8)
        wraps = rng.randrange(1, 1+block//4)
        width = rng.randrange(1, 6)
        # Explicit per-slab pages. Every entry is charged for every line use.
        pages = [[(j, r, c) for r in range(wraps) for c in range(width**2)]
                 for j in range(j_count)]
        for a in range(x):
            for j, page in enumerate(pages):
                for b in range(y):
                    for coefficient in page:
                        assert coefficient[0] == j
                        coefficient_reads += 1
                        if pages[0][0][0] != j:
                            coefficients_wrong_if_constant_page += 1
        fraction = Fraction(wraps*width**2, block)
        maximum_catalogue_fraction = max(maximum_catalogue_fraction, fraction)
        cases += 1
    assert coefficients_wrong_if_constant_page > 0
    return {"status": "exact finite controls passed", "cases": cases,
            "paid_coefficient_reads": coefficient_reads,
            "maximum_page_to_slab_record_ratio": str(maximum_catalogue_fraction),
            "negative_reusing_wrong_origin_page_bad_entries": coefficients_wrong_if_constant_page,
            "scope": "sequential page reuse independent of outer X and spectator Y; not free reads"}


def cyclic_splice(seed):
    rng = Random(seed)
    cases = 0
    payload_records = 0
    two_head_moves = 0
    one_head_moves = 0
    negative = None
    for _ in range(2200):
        slab = 1 << rng.randrange(3, 7)
        period = rng.randrange(3*slab+1, 9*slab)
        if period % slab == 0:
            period += 1
        lines = rng.randrange(2, 60)
        residue = period % slab
        first_slab = period//slab-1
        first = [(y, first_slab*slab+u) for y in range(lines) for u in range(slab)]
        second = [(y, (first_slab+1)*slab+u) for y in range(lines) for u in range(slab)]
        # Two cached physical slabs were extracted in an earlier paid full scan.
        # Count all later seeks from their current work-tape heads.
        heads = [0, 0]
        charged_two = 4*lines*slab  # cache writes/reads and final rewinds
        data = []
        single = first+second
        single_head = 0
        charged_single = 0
        for y in range(lines):
            for h, lo, hi in ((0, y*slab+residue, (y+1)*slab),
                              (1, y*slab, y*slab+residue)):
                charged_two += abs(lo-heads[h])+(hi-lo)
                data.extend((first if h == 0 else second)[lo:hi])
                heads[h] = hi
                destination = lo+h*lines*slab
                charged_single += abs(destination-single_head)+(hi-lo)
                assert single[destination:destination+hi-lo] == (first if h == 0 else second)[lo:hi]
                single_head = destination+hi-lo
        charged_two += sum(heads)
        assert data == [(y, k) for y in range(lines) for k in range(period-slab, period)]
        assert charged_two <= 8*lines*slab
        payload_records += lines*slab
        # Two separate source copies retain one advancing head in each physical
        # slab; one head alternates between slab locations once per line.
        two_head_moves += charged_two
        one_head_moves += charged_single
        cases += 1
        if lines == 59 and negative is None:
            negative = {"lines": lines, "slab": slab, "period": period,
                        "residue": residue,
                        "one_head_to_payload_ratio": float(Fraction(charged_single, lines*slab)),
                        "two_head_to_payload_bound": 8}
    return {"status": "exact finite controls passed", "cases": cases,
            "records_checked": payload_records, "two_head_record_movement_bound": two_head_moves,
            "single_head_movement_lower_example_sum": one_head_moves,
            "negative_single_head_splice": negative}


BRANCHES = {"halo_budget": halo_budget, "exposure": exposure,
            "catalogue": catalogue, "cyclic_splice": cyclic_splice}


def run_branch(item):
    name, seed = item
    started = perf_counter()
    result = BRANCHES[name](seed)
    result.update(seed=seed, seconds=perf_counter()-started, pid=os.getpid())
    return name, result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=202610081)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("the layout branch has at most four CPU slots")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[key] = "1"
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        results = dict(executor.map(run_branch, [(name, args.seed+i)
                       for i, name in enumerate(BRANCHES)]))
    result = {"status": "independent finite layout discriminators completed",
              "workers": args.workers, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "results": results,
              "limitations": ["finite exact combinatorial controls, not Gaussian numerical checks",
                               "physical bounds correspond to stated scan schedules, not interpreter RAM runtime",
                               "no numerical multiplication exponent promoted"]}
    (output/"certificate.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({"status": result["status"], "branches": list(results),
                      "seconds": {k:v["seconds"] for k,v in results.items()}}))


if __name__ == "__main__":
    main()
