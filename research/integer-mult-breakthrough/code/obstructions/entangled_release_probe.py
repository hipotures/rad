#!/usr/bin/env python3
"""Product versus entangled diagonal-subspace frames on a fixed dirty echo.

This discriminator addresses the unproved f factor in shared-release bounds.
It reuses the frozen exact finite-factor engine read-only. Gaussian lifts,
scalar implementations, tape movement and exponent transfer are separate.
OpenAI Codex assisted the experiment design and implementation.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
import time

SYNTHESIS = Path(__file__).resolve().parents[1] / "synthesis"
sys.path.insert(0, str(SYNTHESIS))
import dirty_color_echo_dp as scalar
import dirty_color_echo_full_dp as parallel
from frame_factor_guards import guard_graph


def model(copies: int, family: str) -> dict:
    assert copies in (1, 2)
    h = m = 2
    n = h * copies
    geometry = scalar.f
    source_blocks = [tuple(1 << (j * h + t) for j in range(copies)) for t in range(m)]
    word = scalar.scalar_word(m, "side-inside")
    scalar.scalar_replay(word, m)
    zero = geometry.le((), n)
    full = geometry.le(tuple(1 << j for j in range(n)), n)
    starts = [geometry.le(T, n) for T in source_blocks] + [zero] * (m + 1)
    ends = [full] * m + [geometry.le(geometry.perpendicular(T, n), n)
                           for T in source_blocks] + [full]
    if family == "product":
        subspaces = [geometry.basis(tuple(v << (j * h) for j, E in enumerate(pieces) for v in E), n)
                     for pieces in product(geometry.subspaces(h), repeat=copies)]
    else:
        assert family == "all-LE"
        subspaces = geometry.subspaces(n)
    frames = sorted(set(geometry.le(E, n) for E in subspaces))
    assert len(frames) == (5**copies if family == "product" else (5 if copies == 1 else 67))
    ids = {F: j for j, F in enumerate(frames)}
    assert all(F in ids for F in starts + ends)
    table = [[geometry.distance(a, b, n) for b in frames] for a in frames]
    edges, boundaries, constant = geometry.incidence_graph(word, 2 * m + 1, starts, ends)
    unary = [[sum(table[j][ids[F]] for F in boundary) for j in range(len(frames))]
             for boundary in boundaries]
    order = scalar.minfill(len(word), edges)
    guard_graph(edges, unary, table, constant, order)
    factors = [(j,) for j in range(len(word))] + [(a, b) for a, b, _ in edges]
    retained_choices = peak = evaluations = 0
    stages = []
    for variable in order:
        selected = [F for F in factors if variable in F]
        remaining = [F for F in factors if variable not in F]
        neighbors = tuple(sorted({v for F in selected for v in F if v != variable}))
        entries = len(frames) ** len(neighbors)
        assert entries <= parallel.FACTOR_MAX_ENTRIES
        live = 2 * entries + sum(len(frames) ** len(F) for F in factors) + retained_choices
        peak = max(peak, live)
        evaluations += entries * len(frames)
        stages.append({"variable": variable, "width": len(neighbors), "entries": entries})
        retained_choices += entries
        factors = remaining + [neighbors]
    return dict(h=h, copies=copies, active_bits=n, family=family, source_blocks=source_blocks,
                frames=frames, starts=starts, ends=ends, word=word, table=table,
                edges=edges, unary=unary, constant=constant, order=order,
                preflight=dict(stages=stages, payload_peak_bytes=2 * peak,
                               candidate_evaluations=evaluations, reserve_bytes=2**30))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--copies", type=int, default=2)
    parser.add_argument("--frames", choices=("product", "all-LE"), default="all-LE")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--memory-budget-GiB", type=float, default=4)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = model(args.copies, args.frames)
    if args.preflight:
        print(json.dumps(dict(copies=args.copies, family=args.frames,
                              frame_count=len(data["frames"]), **data["preflight"]), indent=2))
        return
    assert args.output is not None
    assert data["preflight"]["payload_peak_bytes"] + 2**30 <= args.memory_budget_GiB * 2**30
    args.output.mkdir(parents=True, exist_ok=False)
    build = args.output / "builds"
    build.mkdir()
    generated = build / "parallel.cpp"
    binary = build / "finite-factor"
    sources = [Path(__file__), Path(scalar.__file__), Path(parallel.__file__), scalar.CPP,
               parallel.PATCH, SYNTHESIS / "frame_factor_guards.py", Path(scalar.f.__file__),
               SYNTHESIS / "lagrangian_graph_completion.py", SYNTHESIS / "trimmed_zeta_dirty_probe.py",
               scalar.f.SIDE_SOURCE]
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    subprocess.run(["patch", "-o", str(generated.resolve()), str(scalar.CPP.resolve()),
                    str(parallel.PATCH.resolve())], capture_output=True, text=True, check=True)
    subprocess.run(["c++", "-O3", "-std=c++17", "-fopenmp", str(generated.resolve()),
                    "-o", str(binary.resolve())], capture_output=True, text=True, check=True)
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), copies=args.copies,
                    family=args.frames, source_blocks=data["source_blocks"], frame_count=len(data["frames"]),
                    source_sha256=hashes, generated_parallel_source_sha256=hashlib.sha256(generated.read_bytes()).hexdigest(),
                    compiler=subprocess.check_output(["c++", "--version"], text=True).splitlines()[0],
                    compile_flags=["-O3", "-std=c++17", "-fopenmp"], workers=args.workers,
                    preflight=data["preflight"], memory_budget_GiB=args.memory_budget_GiB,
                    scope="Exact finite geometry for a fixed dirty scalar word; actual Gaussian lifts and full native costs open")
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    environment = os.environ.copy()
    environment["OMP_NUM_THREADS"] = str(args.workers)
    environment["OMP_DYNAMIC"] = "FALSE"
    os.environ.update({key: environment[key] for key in ("OMP_NUM_THREADS", "OMP_DYNAMIC")})
    start = time.perf_counter()
    receipt = parallel.full_solve(binary, args.output / "derived", data["edges"], data["unary"],
                                  data["table"], data["constant"], data["order"])
    current = list(data["starts"])
    histogram = Counter()
    for gate, (a, b, _) in enumerate(data["word"]):
        frame = data["frames"][receipt["assignment"][gate]]
        for role in (a, b):
            rank = scalar.f.distance(current[role], frame, data["active_bits"])
            if rank:
                histogram[rank] += 1
            current[role] = frame
    for role, frame in enumerate(data["ends"]):
        rank = scalar.f.distance(current[role], frame, data["active_bits"])
        if rank:
            histogram[rank] += 1
    assert sum(k * v for k, v in histogram.items()) == receipt["optimum"]
    assert receipt["peak_live_uint16_entries"] * 2 == data["preflight"]["payload_peak_bytes"]
    assert receipt["parallel_worker_threads"] == args.workers
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest for p, digest in hashes.items())
    capacity = 5 * data["active_bits"]
    result = dict(status="EXACT FINITE ELIMINATION PASS", copies=args.copies, family=args.frames,
                  frame_count=len(data["frames"]), minimum_rank_charge=receipt["optimum"],
                  capacity=capacity, rank_deficit=capacity - receipt["optimum"],
                  histogram=dict(sorted(histogram.items())), complete_frames=data["frames"],
                  starts=data["starts"], ends=data["ends"], source_blocks=data["source_blocks"],
                  word=[dict(destination=a, source=b, coefficient=str(c)) for a, b, c in data["word"]],
                  exact_factor_receipt=receipt, elapsed_seconds=time.perf_counter() - start,
                  scope=protocol["scope"])
    (args.output / "results").mkdir()
    (args.output / "results/summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "copies", "family", "frame_count", "minimum_rank_charge",
                                            "capacity", "rank_deficit", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
