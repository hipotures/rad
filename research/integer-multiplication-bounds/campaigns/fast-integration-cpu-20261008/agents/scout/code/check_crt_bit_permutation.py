#!/usr/bin/env python3
"""Independent CRT address invariant: bit-slot permutations preserve weight."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
from math import prod
from pathlib import Path


def crt(coordinate, shape):
    prefix, lower = 1, 0
    result = []
    for digit, side in zip(coordinate, shape):
        result.append((digit + pow(prefix, -1, side) * lower) % side)
        lower += digit * prefix
        prefix *= side
    return tuple(result)


def reverse_crt(coordinate, shape):
    prefix, lower = 1, 0
    result = []
    for digit, side in zip(coordinate, shape):
        original = (digit - pow(prefix, -1, side) * lower) % side
        result.append(original)
        lower += original * prefix
        prefix *= side
    return tuple(result)


def case(shape):
    seen = set()
    weight_changes = 0
    omitted_rotation_changes = 0
    first = None
    for address in itertools.product(*(range(t) for t in shape)):
        target = crt(address, shape)
        assert reverse_crt(target, shape) == address
        assert target not in seen
        seen.add(target)
        before = sum(x.bit_count() for x in address)
        after = sum(x.bit_count() for x in target)
        if before != after:
            weight_changes += 1
            if first is None:
                first = dict(source=list(address), target=list(target),
                             source_binary_weight=before, target_binary_weight=after)
        omitted_rotation_changes += target != address
    assert len(seen) == prod(shape) and first is not None
    return dict(prime_shape=list(shape), valid_addresses=prod(shape),
                binary_slot_weight_changes=weight_changes,
                wrong_if_only_axis_reordered=omitted_rotation_changes,
                first_weight_counterexample=first)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    a = Fraction(783777693, 20000000000000)
    rows = [case(shape) for shape in ((3, 5), (5, 7), (3, 5, 7), (5, 7, 11))]
    result = dict(observed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  status="CRT valid-address weight changes exclude pure binary slot permutation",
                  rows=rows,
                  scoped_saving_ceiling=str(a/(1+a)),
                  proof="Any permutation of named binary slots preserves total Hamming weight; the exact CRT map changes it on retained valid addresses.",
                  limitations=["does not exclude arithmetic routers, Toffoli circuits or other new CRT algorithms",
                               "scoped cost ceiling assumes retained d full-payload rotations and q<a"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(dict(status=result["status"], cases=len(rows),
                          valid_addresses=sum(x["valid_addresses"] for x in rows),
                          weight_changes=sum(x["binary_slot_weight_changes"] for x in rows))))


if __name__ == "__main__":
    main()
