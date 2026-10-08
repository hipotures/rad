#!/usr/bin/env python3
"""Exact joined-boundary kernel holes and strict recursive shrink controls.

E=F tensor line(first) tensor line(second) is annihilated by the joined
residual. Each E basis vector has a first nonzero coordinate followed only
by later coordinates in its block. Its first coordinate is therefore a
forbidden rightmost Bruhat pivot column. These equally spaced holes bound
diagonal run lengths without an additional split or entropy charge.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import resource
import time

from diagonal_bruhat_batches import joined_boundary_rows, profile


def case(h, first, second, matched):
    begin = time.monotonic()
    rows, rank, denominator = joined_boundary_rows(h, first, second, matched)
    m = h ** 3
    block_support = sorted(a * h + b for a in first for b in second)
    holes = [i * h * h + block_support[0] for i in range(h)]
    kernel_checks = 0
    for i in range(h):
        support = [i * h * h + j for j in block_support]
        for row in rows:
            assert sum(row.get(j, 0) for j in support) == 0
            kernel_checks += 1
    pivots, audit = profile(rows)
    assert len(pivots) == rank
    pivot_columns = {j for _, j in pivots}
    assert not pivot_columns.intersection(holes)
    diagonal = [i for i, j in pivots if i == j]
    lengths = []
    previous = None
    for i in diagonal:
        if previous is not None and i == previous + 1:
            lengths[-1] += 1
        else:
            lengths.append(1)
        previous = i
    assert len(diagonal) >= m - 4 * h
    assert len(lengths) <= 4 * h + 1
    assert max(lengths, default=0) <= h * h - 1
    assert h * max(lengths, default=0) < m
    return dict(h=h, first=first, second=second, matched=matched,
                expected_rank=rank, cleared_denominator=denominator,
                kernel_equations=kernel_checks, forbidden_pivot_columns=holes,
                diagonal_pivots=len(diagonal), diagonal_runs=lengths,
                maximum_run=max(lengths, default=0), strict_h_fold_child_shrink=True,
                exact_elimination=audit, wall_seconds=time.monotonic() - begin,
                pivot_sha256=sha256(json.dumps(pivots, separators=(",", ":")).encode()).hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--h", type=int, nargs="+", default=[6, 7, 8])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), "Use a fresh result path"
    begin = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    cases = []
    for h in args.h:
        triples = list(combinations(range(h), 3))
        choices = sorted(set((triples[0], triples[len(triples) // 2], triples[-1])))
        for first in choices:
            partners = [triple for triple in triples if len(set(first).intersection(triple)) == 1]
            matched_choices = sorted(set((partners[0], partners[-1])))
            for second in choices:
                for matched in matched_choices:
                    row = case(h, first, second, matched)
                    cases.append(row)
                    print("PASS exact joined kernel holes", h, first, second, matched,
                          "maxrun", row["maximum_run"], flush=True)
    n = 6 ** 3
    upper = [{i: 1} for i in range(n)]
    upper[0][n - 1] = 1
    pivots, _ = profile(upper)
    # General low-rank perturbations need not have the joined kernel holes.
    assert [(i, j) for i, j in pivots if i != j] == [(0, n - 1), (n - 1, 0)]
    assert n - 2 > 6 ** 2 - 1
    result = dict(status="PASS exact joined-kernel hole and shrink controls",
                  campaign="20261007T222521Z", started_utc=started,
                  completed_utc=datetime.now(timezone.utc).isoformat(), cases=cases,
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  dependency_sha256=sha256(Path(__file__).with_name("diagonal_bruhat_batches.py").read_bytes()).hexdigest(),
                  negative_general_rank_one_update=dict(size=n, longest_diagonal_run=n - 2,
                      joined_bound=6 ** 2 - 1, joined_kernel_hypothesis_missing=True),
                  wall_seconds=time.monotonic() - begin,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope="Exact finite controls for the joined-specific all-size argument; "
                        "independent tape/recurrence and final assembly review remain separate")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
