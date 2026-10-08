#!/usr/bin/env python3
"""Exact sequential small-field crossings for an arbitrary-width swap.

Only binary H and D addresses are used. This checks the finite stream
schedule, not a faster main-block network or its recursive cost.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import resource
import time


def transpose_right(records, radices, index, last):
    """Move one small field right, using demultiplexed sequential tapes.

    A prefix group has small field q, middle range M, and suffix range S.
    Distribute complete S-record groups into q tapes, then read one group
    from each tape for each middle index. No random source access occurs.
    """
    assert 0 <= index < last < len(radices)
    small = radices[index]
    middle = 1
    suffix = 1
    for r in radices[index + 1:last + 1]:
        middle *= r
    for r in radices[last + 1:]:
        suffix *= r
    size = small * middle * suffix
    assert len(records) % size == 0
    output = []
    for begin in range(0, len(records), size):
        tapes = [[] for _ in range(small)]
        source = iter(records[begin:begin + size])
        for i in range(small):
            for _ in range(middle * suffix):
                tapes[i].append(next(source))
        streams = [iter(tape) for tape in tapes]
        for _ in range(middle):
            for stream in streams:
                for _ in range(suffix):
                    output.append(next(stream))
    new_radices = (radices[:index] + radices[index + 1:last + 1] +
                   [small] + radices[last + 1:])
    return output, new_radices


def transpose_left(records, radices, first, index):
    """Inverse small-field crossing, again with q sequential tapes."""
    assert 0 <= first < index < len(radices)
    small = radices[index]
    middle = 1
    suffix = 1
    for r in radices[first:index]:
        middle *= r
    for r in radices[index + 1:]:
        suffix *= r
    size = small * middle * suffix
    assert len(records) % size == 0
    output = []
    for begin in range(0, len(records), size):
        tapes = [[] for _ in range(small)]
        source = iter(records[begin:begin + size])
        for _ in range(middle):
            for i in range(small):
                for _ in range(suffix):
                    tapes[i].append(next(source))
        for tape in tapes:
            output.extend(tape)
    new_radices = radices[:first] + [small] + radices[first:index] + radices[index + 1:]
    return output, new_radices


def ideal_equal_swap(records, radices, first, second):
    """The existing complete main interchange, used as an interface here."""
    assert radices[first] == radices[second]
    addresses = list(product(*(range(r) for r in radices)))
    original = dict(zip(addresses, records))
    result = []
    for address in addresses:
        source = list(address)
        source[first], source[second] = source[second], source[first]
        result.append(original[tuple(source)])
    return result, list(radices)


def tail_schedule(records, radices):
    """[P,Hm,Ht,B,Dm,Dt,Q] -> [P,Dm,Dt,B,Hm,Ht,Q]."""
    assert len(radices) == 7 and radices[1] == radices[4] and radices[2] == radices[5]
    stage, sizes = transpose_right(records, radices, 2, 4)
    # [P,Hm,B,Dm,Ht,Dt,Q]
    stage, sizes = ideal_equal_swap(stage, sizes, 1, 3)
    # Same physical field positions now contain Dm,B,Hm,Ht,Dt.
    stage, sizes = ideal_equal_swap(stage, sizes, 4, 5)
    # [P,Dm,B,Hm,Dt,Ht,Q]
    stage, sizes = transpose_left(stage, sizes, 2, 4)
    assert sizes == radices
    return stage


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    started = time.monotonic()
    cases = []
    all_records = negative_records = split_checks = 0
    for m in range(2, 8):
        for e in range(m, min(8, 2 * m + 1) + 1):
            b, t = divmod(e, m)
            assert b > 0 and 0 <= t < m
            p, spectator, q = (2 if e % 2 else 1), (3 if m % 2 else 1), (2 if t else 1)
            sizes = [p, 2 ** (m * b), 2 ** t, spectator, 2 ** (m * b), 2 ** t, q]
            labels = list(product(*(range(r) for r in sizes)))
            # Unique complete records establish equality for every possible
            # payload assignment, including arbitrary parked prefix/suffix.
            result = tail_schedule(labels, sizes)
            expected = [(a, dm, dt, s, hm, ht, z) for a, hm, ht, s, dm, dt, z in labels]
            assert result == expected
            assert tail_schedule(result, sizes) == labels
            assert all(before[0] == after[0] and before[3] == after[3] and before[6] == after[6]
                       for before, after in zip(labels, result))
            for r in range(1, m):
                assert r * b <= r * e // m and r * b < e
                split_checks += 1
            # Omitting the final crossing is generally a genuine failure.
            wrong, wrong_sizes = transpose_right(labels, sizes, 2, 4)
            wrong, wrong_sizes = ideal_equal_swap(wrong, wrong_sizes, 1, 3)
            wrong, wrong_sizes = ideal_equal_swap(wrong, wrong_sizes, 4, 5)
            failed = sum(a != b for a, b in zip(wrong, expected))
            if t and spectator * sizes[1] > 1:
                assert failed > 0
            negative_records += failed
            all_records += len(labels)
            cases.append(dict(m=m, e=e, main_chunk_width=b, tail_width=t,
                              field_radices=sizes, complete_records=len(labels),
                              forward_and_inverse_exact=True, spectator_prefix_suffix_unchanged=True,
                              omitted_last_crossing_disagreements=failed,
                              output_sha256=sha256(repr(result).encode()).hexdigest()))
    value = dict(status='PASS EXACT ARBITRARY-WIDTH TAIL STREAM SCHEDULE',
                 generated_utc=datetime.now(timezone.utc).isoformat(),
                 source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                 binary_address_alphabet=2, cases=cases, complete_record_checks=all_records,
                 child_shrink_checks=split_checks, negative_record_disagreements=negative_records,
                 workers=1, elapsed_seconds=time.monotonic() - started,
                 peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 scope='Sequential tail crossings only; main-block network, diagonal-pivot grouping, row reservation and new recurrence remain separate transfer obligations')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    print(value['status'], all_records, 'records', len(cases), 'shapes', flush=True)


if __name__ == '__main__':
    main()
