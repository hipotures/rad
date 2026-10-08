#!/usr/bin/env python3
"""Exact scoped rank obstruction for a bare two-role, three-shear exchange.

All Lagrangian common frames are allowed in the declared metric model. This
does not exclude helper networks, other words, or faster multiplication.
The enumeration imports no other research implementation.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import time


def canonical(rows):
    pivots = {}
    for row in rows:
        for pivot in sorted(pivots, reverse=True):
            if row >> pivot & 1:
                row ^= pivots[pivot]
        if row:
            pivot = row.bit_length() - 1
            for old in list(pivots):
                if pivots[old] >> pivot & 1:
                    pivots[old] ^= row
            pivots[pivot] = row
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def symplectic(a, b, n):
    mask = (1 << n) - 1
    return (((a & mask) & (b >> n)).bit_count() +
            ((b & mask) & (a >> n)).bit_count()) & 1


def enumerate_lagrangians(n):
    # Exhaust isotropic subspaces by extension, rather than orbit generators.
    current = {()}
    for level in range(n):
        next_level = set()
        for rows in current:
            for v in range(1, 1 << (2*n)):
                if all(symplectic(v, row, n) == 0 for row in rows):
                    enlarged = canonical((*rows, v))
                    if len(enlarged) == level+1:
                        next_level.add(enlarged)
        current = next_level
    expected = 1
    for j in range(1, n+1):
        expected *= (1 << j)+1
    if len(current) != expected:
        raise ValueError("Isotropic extension enumeration has wrong size")
    return sorted(current)


def graph(columns, n):
    if len(columns) != n or any(c >> n for c in columns):
        raise ValueError("Invalid graph matrix")
    if any(((columns[i] >> j) ^ (columns[j] >> i)) & 1
           for i in range(n) for j in range(n)):
        raise ValueError("Graph matrix must be symmetric")
    return canonical((1 << j) | (columns[j] << n) for j in range(n))


def graph_frames(n):
    positions = [(i, j) for i in range(n) for j in range(i, n)]
    result = []
    for bits in range(1 << len(positions)):
        columns = [0]*n
        for k, (i, j) in enumerate(positions):
            if bits >> k & 1:
                columns[j] ^= 1 << i
                if i != j:
                    columns[i] ^= 1 << j
        result.append(graph(columns, n))
    if len(set(result)) != 1 << len(positions):
        raise ValueError("Symmetric graph enumeration has duplicates")
    return sorted(result)


def distance(a, b, n):
    return len(canonical((*a, *b))) - n


def boundaries(n, unit):
    if not 0 < unit < 1 << n or unit.bit_count() % 2 != 1:
        raise ValueError("A nonzero binary norm-one vector is required")
    p = [unit if unit >> j & 1 else 0 for j in range(n)]
    identity = [1 << j for j in range(n)]
    return (graph(p, n), graph([0]*n, n), graph(identity, n),
            graph([x ^ y for x, y in zip(identity, p)], n))


def analytic_bound(n, unit, claimed_minimum):
    source_x, source_y, sink_x, sink_y = boundaries(n, unit)
    if distance(source_x, sink_y, n) != n or distance(source_y, sink_x, n) != n:
        raise ValueError("Crossed endpoints are not transverse")
    if claimed_minimum != 2*n:
        raise ValueError("The complete three-shear rank minimum is 2n")
    return True


def probe(spec):
    n, unit = spec
    start = time.monotonic()
    all_frames = enumerate_lagrangians(n)
    graphs = graph_frames(n)
    if not set(graphs) <= set(all_frames):
        raise ValueError("A symmetric graph is missing from the full space")
    source_x, source_y, sink_x, sink_y = boundaries(n, unit)
    indices = {frame: j for j, frame in enumerate(all_frames)}
    metric = [[distance(a, b, n) for b in all_frames] for a in all_frames]
    if any(metric[i][i] != 0 or metric[i][j] != metric[j][i]
           for i in range(len(all_frames)) for j in range(len(all_frames))):
        raise ValueError("Distance identity or symmetry failed")
    incoming = [distance(source_x, a, n)+distance(source_y, a, n) for a in all_frames]
    outgoing = [distance(a, sink_x, n)+distance(a, sink_y, n) for a in all_frames]
    # The middle common frame is eliminated exactly: its two distances have
    # minimum d(B1,B3), attained by B2=B1. No restricted middle search.
    best = min((incoming[i]+2*metric[i][j]+outgoing[j], i, j)
               for i, j in product(range(len(all_frames)), repeat=2))
    graph_ids = [indices[frame] for frame in graphs]
    graph_best = min(incoming[i]+2*metric[i][j]+outgoing[j]
                     for i, j in product(graph_ids, repeat=2))
    if best[0] != 2*n or graph_best != 2*n:
        raise ValueError("Complete finite optimum disagrees with analytic bound")
    analytic_bound(n, unit, best[0])
    try:
        analytic_bound(n, unit, 2*n-1)
    except ValueError:
        rejected = True
    else:
        raise ValueError("An invalid rank-saving claim was accepted")
    omitted_output = min(incoming[i]+2*metric[i][j]+distance(all_frames[j], sink_x, n)
                         for i, j in product(range(len(all_frames)), repeat=2))
    if omitted_output >= 2*n:
        raise ValueError("Missing-output charge did not discriminate")
    return dict(n=n, source_unit=unit, full_lagrangian_count=len(all_frames),
                symmetric_graph_count=len(graphs), all_endpoint_frame_pairs=len(all_frames)**2,
                middle_frame_eliminated_exactly=True, full_minimum=best[0],
                symmetric_graph_minimum=graph_best,
                optimal_frames=[list(all_frames[best[1]]), list(all_frames[best[1]]), list(all_frames[best[2]])],
                cross_endpoint_distances=[n, n],
                negative_controls=dict(false_saving_claim_rejected=rejected,
                                       missing_one_output_charge_minimum=omitted_output),
                seconds=time.monotonic()-start,
                scope="Bare two-role three-shear exchange with these fixed complete endpoints; all Lagrangian common frames allowed. Helper/branching networks and other words excluded.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--bounded", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.output is not None and args.output.exists():
        parser.error("Workers must be positive and output must be fresh")
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    specs = [(1,1),(2,1)] if args.bounded else [(1,1),(2,1),(3,1),(3,7)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(probe, specs))
    result = dict(status="EXACT SCOPED LAGRANGIAN EXCHANGE OBSTRUCTION", started_utc=started,
                  completed_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                  seed=None, randomness="None; exhaustive finite isotropic and graph enumerations",
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  git_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
                  cases=cases, seconds=time.monotonic()-start,
                  not_proved=["general reversible-circuit lower bound","paid full-Clifford tape compiler",
                              "complete new native network","integer-multiplication exponent"])
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x",encoding="utf-8") as handle:
            handle.write(json.dumps(result,indent=2)+"\n")
    print(json.dumps(dict(status=result["status"],cases=len(cases),workers=args.workers,seconds=result["seconds"])))


if __name__ == "__main__":
    main()
