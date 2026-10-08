#!/usr/bin/env python3
"""Exact contiguous pivot batches for rational projection residuals.

Rightmost-pivot forward elimination reconstructs the partial permutation in
a lower/lower Bruhat decomposition. All arithmetic is integer and each row
is normalized by its gcd; no modular rank or floating-point acceptance is
used. A consecutive increasing pivot run has contiguous source and target
fields, so its shear can use one larger interchange without pivot gathering.
This discriminator does not certify a new complete recurrence or exponent.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import resource
import time


def complement_rows(h, triple, tensor_power=1):
    """6^k(I-P_t^tensor(k)), where P_t uses the rational form I-J/9."""
    assert h >= 4 and h != 9 and len(triple) == 3
    assert len(set(triple)) == 3 and all(0 <= x < h for x in triple)
    assert tensor_power in (1, 2)
    size = h ** tensor_power
    denominator = 6 ** tensor_power
    source = set(triple)
    rows = [{i: denominator} for i in range(size)]
    if tensor_power == 1:
        support = sorted(source)
        coefficients = {j: 2 if j in source else -1 for j in range(h)}
    else:
        support = sorted(a * h + b for a in source for b in source)
        coefficients = {a * h + b: (2 if a in source else -1) *
                        (2 if b in source else -1)
                        for a in range(h) for b in range(h)}
    for row in support:
        values = {column: -value for column, value in coefficients.items()}
        values[row] = values.get(row, 0) + denominator
        rows[row] = {column: value for column, value in values.items() if value}
    # P_t^2=P_t follows from t^T H t=2, and tensoring preserves rank1.
    assert sum((2 if i in source else -1) for i in source) == 6
    return rows, size - 1, denominator


def joined_boundary_rows(h, first, second, matched):
    """36(I-I tensor P_first tensor P_second-P_second tensor P_matched tensor I)."""
    assert h >= 6 and h != 9
    assert len(set(first).intersection(matched)) == 1
    size = h ** 3
    rows = [{i: 36} for i in range(size)]
    f, s, t = set(first), set(second), set(matched)
    coeff = lambda j, subset: 2 if j in subset else -1
    for a in range(h):
        for b in f:
            for c in s:
                row = (a * h + b) * h + c
                values = rows[row]
                for j in range(h):
                    for k in range(h):
                        column = (a * h + j) * h + k
                        values[column] = values.get(column, 0) - coeff(j, f) * coeff(k, s)
    for a in s:
        for b in t:
            for c in range(h):
                row = (a * h + b) * h + c
                values = rows[row]
                for i in range(h):
                    for j in range(h):
                        column = (i * h + j) * h + c
                        values[column] = values.get(column, 0) - coeff(i, s) * coeff(j, t)
    rows = [{column: value for column, value in row.items() if value} for row in rows]
    # The two rank-h projections multiply to zero in both orders because
    # the middle two triple lines are orthogonal. The residual rank is m-2h.
    return rows, size - 2 * h, 36


def normalized(row):
    if not row:
        return row
    divisor = 0
    for value in row.values():
        divisor = gcd(divisor, value)
    if divisor > 1:
        row = {column: value // divisor for column, value in row.items()}
    if row[max(row)] < 0:
        row = {column: -value for column, value in row.items()}
    return row


def profile(original):
    """Exact rank profile; clear below before right-column isolation.

    Once a pivot column is zero below its pivot, right multiplication to
    clear entries left of that pivot only changes the processed pivot row.
    Thus the following active matrix is precisely the one left by the
    lower/lower elimination proof. Scaling rows does not change its pivots.
    """
    rows = [normalized(dict(row)) for row in original]
    columns = {}
    for i, row in enumerate(rows):
        for j in row:
            columns.setdefault(j, set()).add(i)
    pivots = []
    eliminated_updates = 0
    maximum_bits = 0
    for i, row in enumerate(rows):
        if not row:
            continue
        pivot = max(row)
        value = row[pivot]
        maximum_bits = max(maximum_bits, max(abs(x).bit_length() for x in row.values()))
        pivots.append((i, pivot))
        following = sorted(j for j in columns.get(pivot, ()) if j > i)
        for j in following:
            old = rows[j]
            coefficient = old[pivot]
            common = gcd(abs(value), abs(coefficient))
            left, right = value // common, coefficient // common
            replacement = {column: left * old.get(column, 0) - right * row.get(column, 0)
                           for column in old.keys() | row.keys()}
            replacement = normalized({column: number for column, number in replacement.items() if number})
            assert pivot not in replacement
            for column in old:
                columns[column].discard(j)
            for column in replacement:
                columns.setdefault(column, set()).add(j)
            rows[j] = replacement
            eliminated_updates += 1
        for column in row:
            columns[column].discard(i)
    assert len({column for _, column in pivots}) == len(pivots)
    return pivots, dict(integer_elimination_updates=eliminated_updates,
                        maximum_observed_integer_bits=maximum_bits,
                        exact_rank=len(pivots), arithmetic="integer gcd-normalized elimination")


def runs(pivots, size):
    """Group consecutive row AND column indices, with strict child shrink."""
    answer = []
    for row, column in pivots:
        if (answer and answer[-1][0] + answer[-1][2] == row and
                answer[-1][1] + answer[-1][2] == column and
                answer[-1][2] < size - 1):
            a, b, length = answer[-1]
            answer[-1] = (a, b, length + 1)
        else:
            answer.append((row, column, 1))
    assert sum(length for _, _, length in answer) == len(pivots)
    assert all(0 < length < size for _, _, length in answer)
    return answer


def inspect(name, rows, expected_rank, denominator, settings):
    start = time.monotonic()
    size = len(rows)
    pivots, checked = profile(rows)
    assert len(pivots) == expected_rank
    batches = runs(pivots, size)
    histogram = {}
    for _, _, length in batches:
        histogram[str(length)] = histogram.get(str(length), 0) + 1
    sha = lambda value: sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()
    return dict(name=name, settings=settings, ambient_dimension=size,
                cleared_denominator=denominator, expected_rank=expected_rank,
                exact_elimination=checked, pivot_sha256=sha(pivots),
                batch_sha256=sha(batches), contiguous_batch_histogram=histogram,
                number_of_old_scalar_calls=len(pivots),
                number_of_candidate_batched_calls=len(batches),
                ranks_conserved=sum(int(r) * count for r, count in histogram.items()),
                batched_rank=sum(length for _, _, length in batches if length > 1),
                largest_batch=max((length for _, _, length in batches), default=0),
                wall_seconds=time.monotonic() - start)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--h", type=int, nargs="+", default=[6, 8])
    ap.add_argument("--joined-h", type=int, nargs="*", default=[])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), "Use a fresh result path"
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    cases = []
    for h in args.h:
        triples = sorted(set(((0, 1, 2), (0, h // 2, h - 1),
                              (h - 3, h - 2, h - 1))))
        for triple in triples:
            for power in (1, 2):
                rows, rank, denominator = complement_rows(h, triple, power)
                cases.append(inspect("rank-one complement", rows, rank, denominator,
                                     dict(h=h, triple=triple, tensor_power=power)))
                print("PASS exact complement", h, triple, power,
                      "batches", cases[-1]["contiguous_batch_histogram"], flush=True)
    for h in args.joined_h:
        first, second, matched = (0, 1, 2), (h - 3, h - 2, h - 1), (2, 3, 4)
        rows, rank, denominator = joined_boundary_rows(h, first, second, matched)
        cases.append(inspect("joined auxiliary boundary", rows, rank, denominator,
                             dict(h=h, first=first, second=second, matched=matched)))
        print("PASS exact joined boundary", h,
              "batches", cases[-1]["contiguous_batch_histogram"], flush=True)
    result = dict(status="PASS exact contiguous-pivot discriminator",
                  campaign="20261007T222521Z", started_utc=started,
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  settings=vars(args) | {"output": str(args.output)}, cases=cases,
                  wall_seconds=time.monotonic() - begin,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope="Exact finite rational elimination and grouping only; "
                        "tape batching, full-network histograms and a stronger exponent "
                        "remain separate proof and certificate obligations")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
