#!/usr/bin/env python3
"""Exact counterexample search for a low-rank Bruhat batching lemma.

Random integer unimodular conjugates generate genuine rank-d projections.
The strengthened bound covers off-diagonal and missing pivot rows together:
at least n-2d diagonal pivots in at most 2d+1 contiguous runs. This is
experimental evidence for an all-size argument, not that argument itself.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import resource
import time

from diagonal_bruhat_batches import profile


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, column)) for column in zip(*b)]
            for row in a]


def conjugate(n, d, seed):
    rng = random.Random(seed)
    z, inverse = identity(n), identity(n)
    for _ in range(4 * n):
        a, b = rng.sample(range(n), 2)
        value = rng.choice((-2, -1, 1, 2))
        z[a] = [x + value * y for x, y in zip(z[a], z[b])]
        # If Z <- (I+c e_a e_b^T) Z, inverse <- inverse (I-c e_a e_b^T).
        for row in inverse:
            row[b] -= value * row[a]
    assert multiply(z, inverse) == multiply(inverse, z) == identity(n)
    u = [row[:d] for row in z]
    v = inverse[:d]
    assert multiply(v, u) == identity(d)
    return multiply(u, v)


def inspect(matrix, d, expected_rank, settings):
    n = len(matrix)
    sparse = [{j: value for j, value in enumerate(row) if value} for row in matrix]
    pivots, audit = profile(sparse)
    assert len(pivots) == expected_rank
    off = [(i, j) for i, j in pivots if i != j]
    diagonal = [i for i, j in pivots if i == j]
    run_lengths = []
    previous = None
    for i in diagonal:
        if previous is not None and i == previous + 1:
            run_lengths[-1] += 1
        else:
            run_lengths.append(1)
        previous = i
    assert len(off) <= 2 * d
    assert n - len(pivots) <= d
    assert len(diagonal) >= n - 2 * d
    assert len(run_lengths) <= 2 * d + 1
    assert len(off) + n - len(pivots) <= 2 * d
    return dict(settings=settings, size=n, perturbation_rank=d,
                rank=expected_rank, off_diagonal=len(off), diagonal=len(diagonal),
                diagonal_runs=run_lengths, exact_elimination=audit,
                matrix_sha256=sha256(json.dumps(matrix, separators=(",", ":")).encode()).hexdigest(),
                pivot_sha256=sha256(json.dumps(pivots, separators=(",", ":")).encode()).hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), "Use a fresh result path"
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    cases = []
    for n in (4, 6, 8, 12, 16, 24):
        for d in sorted(set((1, 2, max(1, n // 4)))):
            if d >= n:
                continue
            for sample in range(args.samples):
                seed = args.seed + 100000 * n + 1000 * d + sample
                p = conjugate(n, d, seed)
                for scale, rank, kind in ((1, n - d, "rank-d projection complement"),
                                          (-1, n, "invertible rank-d update")):
                    matrix = [[int(i == j) - scale * value for j, value in enumerate(row)]
                              for i, row in enumerate(p)]
                    cases.append(inspect(matrix, d, rank, dict(seed=seed, scale=scale, family=kind)))
    # A stronger off-diagonal<=d claim is false even for a unit upper shear.
    wrong = identity(4)
    wrong[0][3] = 1
    negative = inspect(wrong, 1, 4, dict(family="unit upper shear"))
    assert negative["off_diagonal"] == 2 and negative["off_diagonal"] > 1
    result = dict(status="PASS exact finite low-rank pivot-bound controls",
                  campaign="20261007T222521Z", started_utc=started,
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  settings={"samples": args.samples, "seed": args.seed},
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  dependency_sha256=sha256(Path(__file__).with_name("diagonal_bruhat_batches.py").read_bytes()).hexdigest(),
                  cases=cases, negative_stronger_offdiagonal_bound=negative,
                  wall_seconds=time.monotonic() - begin,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope="Exact finite experiments; all-size low-rank profile and "
                        "complete arbitrary-width tape recurrence require independent proof review")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS exact low-rank cases", len(cases), "seconds", result["wall_seconds"], flush=True)


if __name__ == "__main__":
    main()
