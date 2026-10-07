#!/usr/bin/env python3
"""Bounded GPU discovery of rational-label candidates; never a certificate.

Search rank-two planes orthogonal at intersection-one triple pairs. A fixed
ambient signature factors every Gram matrix as X H X^T, with exact zero/diagonal
constraints sought numerically. Known rational h=8 fixtures and a CPU gradient
check calibrate the search. Numerical failure proves no lower bound; numerical
success still requires rational reconstruction and the full network transfer.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

import numpy as np

CAMPAIGN_DEADLINE = datetime(2026, 10, 8, 8, 25, 21, tzinfo=timezone.utc)


def instance(h, rank, negative, signature):
    triples = list(combinations(range(h), 3))
    incidence = np.zeros((len(triples), h), dtype=np.float64)
    for row, triple in enumerate(triples):
        incidence[row, list(triple)] = 1
    intersections = incidence @ incidence.T
    adjacent = intersections == 1
    degree = int(adjacent[0].sum())
    mask = np.repeat(np.repeat(adjacent, 2, axis=0), 2, axis=1).astype(np.float64) / degree
    desired = np.zeros_like(mask)
    for i in range(len(triples)):
        mask[2*i:2*i+2, 2*i:2*i+2] = 1
        desired[2*i, 2*i] = 1
        desired[2*i+1, 2*i+1] = 1 if signature == "positive" else -1
    metric = np.ones(rank, dtype=np.float64)
    if negative:
        metric[-negative:] = -1
    return triples, mask, desired, metric, degree


def value_gradient(x, metric, mask, desired, xp=np):
    residual = (x * metric) @ x.T - desired
    weighted = residual * mask
    objective = xp.sum(weighted * residual) / x.shape[0]
    gradient = (4 / x.shape[0]) * (weighted @ x) * metric
    return objective, gradient, residual


def gradient_control():
    """Independent central finite differences at a small nonsymmetric factor."""
    _, mask, desired, metric, _ = instance(6, 6, 3, "split")
    rng = np.random.default_rng(109)
    x = rng.normal(size=(mask.shape[0], 6)) / 3
    _, gradient, _ = value_gradient(x, metric, mask, desired)
    errors = []
    for row, col in ((0, 0), (1, 4), (7, 2), (15, 5), (39, 1)):
        step = 1e-5
        plus, minus = x.copy(), x.copy()
        plus[row, col] += step
        minus[row, col] -= step
        a, _, _ = value_gradient(plus, metric, mask, desired)
        b, _, _ = value_gradient(minus, metric, mask, desired)
        error = abs((float(a)-float(b))/(2*step)-gradient[row, col])
        assert error < 1e-8
        errors.append(error)
    return {"status": "PASS numerical derivative calibration", "max_absolute_error": max(errors),
            "step": 1e-5, "seed": 109, "checked_entries": 5}


def fixture_color(triple):
    a, b, c = triple
    normals = [n for n in range(1, 8) if (n & (a ^ b)).bit_count() % 2 == 0
               and (n & (a ^ c)).bit_count() % 2 == 0]
    assert len(normals) == 1
    return normals[0] - 1


def initial_factor(triples, rank, negative, signature, seed, control=False):
    rng = np.random.default_rng(seed)
    x = np.zeros((2*len(triples), rank), dtype=np.float64)
    positive = rank-negative
    if control:
        assert rank == 14 and max(max(t) for t in triples) == 7
        assert negative == (0 if signature == "positive" else 7)
        for i, triple in enumerate(triples):
            color = fixture_color(triple)
            if signature == "positive":
                x[2*i, 2*color] = x[2*i+1, 2*color+1] = 1
            else:
                x[2*i, color] = x[2*i+1, 7+color] = 1
        fixture = x.copy()
        x += 0.01*rng.normal(size=x.shape)
        return x, fixture
    assert positive >= (2 if signature == "positive" else 1)
    assert signature == "positive" or negative >= 1
    for i in range(len(triples)):
        if signature == "positive":
            q, _ = np.linalg.qr(rng.normal(size=(positive, 2)))
            x[2*i:2*i+2, :positive] = q.T
        else:
            a = rng.normal(size=positive)
            b = rng.normal(size=negative)
            x[2*i, :positive] = a / np.linalg.norm(a)
            x[2*i+1, positive:] = b / np.linalg.norm(b)
    x += 0.001*rng.normal(size=x.shape)
    return x, None


def run(args):
    import cupy as cp
    cp.cuda.Device(args.device).use()
    cp.get_default_memory_pool().set_limit(size=16*1024**3)
    args.run_dir.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc)
    clock = time.monotonic()
    available = max(0, (CAMPAIGN_DEADLINE-started).total_seconds()-60)
    timeout = min(args.seconds, available)
    assert timeout > 0
    triples, mask, desired, metric, degree = instance(args.h, args.rank, args.negative, args.signature)
    initial, fixture = initial_factor(triples, args.rank, args.negative, args.signature, args.seed, args.control)
    calibration = gradient_control()
    x, mg, dg, hg = (cp.asarray(a) for a in (initial, mask, desired, metric))
    cpu_value, cpu_gradient, cpu_residual = value_gradient(initial, metric, mask, desired)
    gpu_value, gpu_gradient, gpu_residual = value_gradient(x, hg, mg, dg, cp)
    gradient_error = float(np.max(np.abs(cp.asnumpy(gpu_gradient)-cpu_gradient)))
    residual_error = float(np.max(np.abs(cp.asnumpy(gpu_residual)-cpu_residual)))
    assert abs(float(gpu_value)-float(cpu_value)) < 1e-9
    assert gradient_error < 1e-9 and residual_error < 1e-9
    if fixture is not None:
        _, _, residual = value_gradient(fixture, metric, mask, desired)
        assert np.max(np.abs(residual[mask > 0])) == 0
    protocol = {"campaign_id": "20261007T222521Z", "start_utc": started.isoformat(),
                "campaign_deadline_utc": CAMPAIGN_DEADLINE.isoformat(),
                "h": args.h, "rank": args.rank, "label_rank": 2,
                "ambient_negative_index": args.negative, "label_signature": args.signature,
                "seed": args.seed, "device": args.device, "steps": args.steps,
                "time_cap_seconds": timeout, "learning_rate": args.learning_rate,
                "initialization": "perturbed exact h8 coloring" if args.control else "random independently normalized planes",
                "dtype": "float64", "numpy_version": np.__version__, "cupy_version": cp.__version__,
                "code_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                "cpu_gradient_control": calibration, "gpu_cpu_gradient_error": gradient_error,
                "gpu_cpu_residual_error": residual_error, "neighbor_degree": degree,
                "vram_limit_gib": 16,
                "claim_scope": "Numerical discovery only; no feasibility or multiplication theorem certificate"}
    (args.run_dir/"protocol.json").write_text(json.dumps(protocol, indent=2)+"\n")
    moment, variance = cp.zeros_like(x), cp.zeros_like(x)
    fixed = mg > 0
    best = float("inf")
    best_objective = None
    best_step = 0
    last_improvement = 0
    lr = args.learning_rate
    rows = []
    best_x = initial.copy()
    trace = (args.run_dir/"trace.jsonl").open("w")
    terminal = "step limit"
    for step in range(1, args.steps+1):
        value, gradient, residual = value_gradient(x, hg, mg, dg, cp)
        # Adam is a discovery heuristic. Clipping changes its steps, not any
        # acceptance threshold or exact mathematical constraint.
        norm = cp.sqrt(cp.sum(gradient*gradient))
        gradient *= cp.minimum(1, 100/(norm+1e-30))
        moment = 0.9*moment+0.1*gradient
        variance = 0.999*variance+0.001*gradient*gradient
        x -= lr*(moment/(1-0.9**step))/(cp.sqrt(variance/(1-0.999**step))+1e-12)
        if step == 1 or step % args.check_every == 0:
            value, _, residual = value_gradient(x, hg, mg, dg, cp)
            maximum = float(cp.max(cp.abs(residual[fixed])))
            elapsed = time.monotonic()-clock
            row = {"step": step, "objective": float(value), "max_constraint_error": maximum,
                   "elapsed_seconds": elapsed, "learning_rate": lr,
                   "factor_max_abs": float(cp.max(cp.abs(x))),
                   "vram_pool_bytes": cp.get_default_memory_pool().total_bytes()}
            rows.append(row)
            trace.write(json.dumps(row)+"\n")
            trace.flush()
            if maximum < best:
                best, best_objective, best_step = maximum, float(value), step
                last_improvement = step
                best_x = cp.asnumpy(x)
                np.savez_compressed(args.run_dir/"best-factor.npz", factor=best_x, metric=metric)
            if step % (args.check_every*10) == 0:
                print(json.dumps(row), flush=True)
            if not np.isfinite(maximum) or not np.isfinite(float(value)):
                terminal = "nonfinite iterate"
                break
            if maximum < 1e-10:
                terminal = "numerical candidate threshold; exact reconstruction required"
                break
            if step-last_improvement >= 2000:
                lr *= 0.5
                last_improvement = step
            if elapsed >= timeout:
                terminal = "wall-clock cap"
                break
    trace.close()
    _, _, verified = value_gradient(best_x, metric, mask, desired)
    best_cpu = float(np.max(np.abs(verified[mask > 0])))
    assert abs(best_cpu-best) < 1e-8
    summary = {"protocol": protocol, "iterations": step, "best_iteration": best_step,
               "best_max_constraint_error": best, "independent_cpu_best_error": best_cpu,
               "best_objective": best_objective, "elapsed_seconds": time.monotonic()-clock,
               "terminal_reason": terminal, "status": "NUMERICAL CANDIDATE ONLY" if best < 1e-10 else "NO CONVERGENCE; not a nonexistence result",
               "gpu_pool_bytes": cp.get_default_memory_pool().total_bytes(),
               "remaining_proof_obligations": ["Exact rational reconstruction", "All Gram zeros and nondegenerate diagonal blocks",
                                                "Rational nondegenerate ambient form", "Scalar/frame/rank/recurrence transfer"]}
    (args.run_dir/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    if args.control or best < 1e-5:
        (args.run_dir/"best-factor.json").write_text(json.dumps({"factor": best_x.tolist(), "metric": metric.tolist()}, separators=(",", ":"))+"\n")
    print(json.dumps(summary), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--rank", type=int, required=True)
    parser.add_argument("--negative", type=int, required=True)
    parser.add_argument("--signature", choices=["positive", "split"], required=True)
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--seed", type=int, default=109)
    parser.add_argument("--steps", type=int, default=20000)
    parser.add_argument("--seconds", type=float, default=300)
    parser.add_argument("--learning-rate", type=float, default=0.02)
    parser.add_argument("--check-every", type=int, default=100)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    assert args.h >= 6 and 0 <= args.negative < args.rank
    assert args.steps >= 1 and args.check_every >= 1 and args.seconds > 0
    run(args)


if __name__ == "__main__":
    main()
