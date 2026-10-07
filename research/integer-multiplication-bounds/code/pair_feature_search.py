#!/usr/bin/env python3
"""Calibrated low-rank discovery in a rational pair-feature fitting ansatz.

Each target triple T has pair coefficients b_ab. The value on a source
triple S is the sum of its three pair coefficients. Requiring value zero
when |S intersect T|=1 forces cross coefficients b_ia=u_a (i in T,a outside)
and outside coefficients b_ab=-u_a-u_b. Inside coefficients sum to one.
This describes the whole ansatz for h>=6. Its affine projection is exact
algebra, while truncated-rank projections are numerical discovery only.
No new label geometry or multiplication transfer is certified by this file.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
import os
from pathlib import Path
import time

import numpy as np


def structure(h, xp):
    pairs = list(combinations(range(h), 2))
    triples = list(combinations(range(h), 3))
    membership = np.zeros((h, len(triples)), dtype=np.float64)
    for j, triple in enumerate(triples):
        membership[list(triple), j] = 1
    first, second = (np.array([p[i] for p in pairs], dtype=np.int64) for i in (0, 1))
    indices = {pair:i for i, pair in enumerate(pairs)}
    incident = np.array([[indices[tuple(sorted((v, w)))] for w in range(h) if w != v]
                         for v in range(h)], dtype=np.int64)
    others = np.array([[w for w in range(h) if w != v] for v in range(h)], dtype=np.int64)
    first, second, incident, others, member = (xp.asarray(x) for x in
                                               (first, second, incident, others, membership))
    a, b = member[first], member[second]
    return dict(h=h, pairs=pairs, triples=triples, member=member,
                first=first, second=second, incident=incident,
                signs=2*member[others]-1, inside=a*b,
                cross=a+b-2*a*b, outside=(1-a)*(1-b))


def affine_projection(x, s, xp):
    k = s['h']-3
    rhs = xp.sum(x[s['incident']]*s['signs'], axis=1)*(1-s['member'])
    u = (rhs/(k+1)-xp.sum(rhs, axis=0)[None,:]/((k+1)*(2*k+1)))*(1-s['member'])
    pair_sum = u[s['first']]+u[s['second']]
    correction = (1-xp.sum(x*s['inside'], axis=0))/3
    return s['cross']*pair_sum-s['outside']*pair_sum+s['inside']*(x+correction[None,:])


def baseline(s):
    return (3*(s['member'][s['first']]+s['member'][s['second']])-2)/12


def rank_projection(x, rank, xp):
    gram = x @ x.T
    eigenvalues, vectors = xp.linalg.eigh((gram+gram.T)/2)
    columns = vectors[:, -rank:]
    y = columns @ (columns.T @ x)
    return y, eigenvalues


def independent_projection_check():
    """Compare the closed-form projection to an independent least-squares solve."""
    h, target = 6, (0, 1, 2)
    s = structure(h, np)
    outside = [v for v in range(h) if v not in target]
    pairs, triples = s['pairs'], s['triples']
    rng = np.random.default_rng(109)
    source = rng.normal(size=(len(pairs), len(triples)))
    projected = affine_projection(source, s, np)
    errors = []
    for j, t in enumerate(triples):
        out = [v for v in range(h) if v not in t]
        inn = [pair for pair in pairs if set(pair).issubset(t)]
        offset = np.zeros(len(pairs))
        offset[pairs.index(inn[-1])] = 1
        columns = []
        for v in out:
            column = np.zeros(len(pairs))
            for i, pair in enumerate(pairs):
                if v in pair:
                    other = next(w for w in pair if w != v)
                    column[i] = 1 if other in t else -1
            columns.append(column)
        for pair in inn[:-1]:
            column = np.zeros(len(pairs))
            column[pairs.index(pair)] = 1
            column[pairs.index(inn[-1])] = -1
            columns.append(column)
        matrix = np.array(columns).T
        solution = np.linalg.lstsq(matrix, source[:,j]-offset, rcond=None)[0]
        independent = offset+matrix@solution
        errors.append(float(np.max(np.abs(independent-projected[:,j]))))
    maximum = max(errors)
    assert maximum < 2e-13
    assert np.max(np.abs(affine_projection(projected, s, np)-projected)) < 2e-13
    control = baseline(s)
    assert np.max(np.abs(affine_projection(control, s, np)-control)) < 2e-15
    for j,t in enumerate(triples):
        for source_triple in triples:
            if len(set(t)&set(source_triple)) == 1:
                val = sum(projected[pairs.index(pair),j] for pair in combinations(source_triple,2))
                assert abs(val) < 2e-13
        assert abs(sum(projected[pairs.index(pair),j] for pair in combinations(t,2))-1) < 2e-13
    return dict(h=h, columns=len(triples), maximum_projection_error=maximum,
                all_intersection_one_constraints=True, all_diagonal_constraints=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, required=True)
    parser.add_argument('--rank', type=int, required=True)
    parser.add_argument('--device', type=int, default=-1)
    parser.add_argument('--seed', type=int, default=109)
    parser.add_argument('--iterations', type=int, default=2000)
    parser.add_argument('--seconds', type=float, default=180)
    parser.add_argument('--noise', type=float, default=0.05)
    parser.add_argument('--relaxation', type=float, default=0.5)
    parser.add_argument('--method', choices=['alternating','douglas-rachford'], default='douglas-rachford')
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    assert args.h >= 6 and 1 <= args.rank <= args.h and args.iterations > 0
    args.output_dir.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    calibration = independent_projection_check()
    xp = np
    gpu = None
    if args.device >= 0:
        import cupy as cp
        cp.cuda.Device(args.device).use()
        cp.get_default_memory_pool().set_limit(size=16*1024**3)
        xp = cp
        gpu = dict(cupy_version=cp.__version__, device=args.device)
        control = structure(8, np)
        data = np.random.default_rng(109).normal(size=baseline(control).shape)
        cs = structure(8, cp)
        cpu_p = affine_projection(data, control, np)
        gpu_p = cp.asnumpy(affine_projection(cp.asarray(data), cs, cp))
        assert np.max(np.abs(cpu_p-gpu_p)) < 2e-13
        cpu_r, _ = rank_projection(cpu_p, 7, np)
        gpu_r, _ = rank_projection(cp.asarray(cpu_p), 7, cp)
        comparison = float(np.max(np.abs(cpu_r-cp.asnumpy(gpu_r))))
        assert comparison < 2e-11
        calibration['cpu_gpu_rank_projection_error'] = comparison
    s = structure(args.h, xp)
    base = baseline(s)
    rng = np.random.default_rng(args.seed)
    x = base+xp.asarray(rng.normal(scale=args.noise, size=base.shape))
    protocol = dict(start_utc=datetime.now(timezone.utc).isoformat(),
                    source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    settings={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},
                    interpreter=os.sys.executable, numpy_version=np.__version__, gpu=gpu,
                    calibration=calibration,
                    scientific_boundary='Numerical fitting-matrix discovery; exact rational lift and separate label/algorithm transfer required')
    (args.output_dir/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    best = float('inf')
    history = []
    reason = 'iteration cap'
    for iteration in range(args.iterations+1):
        affine = affine_projection(x, s, xp)
        if args.method == 'douglas-rachford':
            low, _ = rank_projection(2*affine-x, args.rank, xp)
            x = x+args.relaxation*(low-affine)
        else:
            low, _ = rank_projection(affine, args.rank, xp)
            x = low
        if iteration % 25 == 0 or iteration == args.iterations:
            low_affine, eigenvalues = rank_projection(affine, args.rank, xp)
            residual = float(xp.max(xp.abs(affine-low_affine)))
            norm = float(xp.linalg.norm(affine))
            if residual < best:
                best = residual
                best_array = np.asarray(affine) if xp is np else xp.asnumpy(affine)
            row = dict(iteration=iteration, rank_residual_max=residual,
                       relative_frobenius=float(xp.linalg.norm(affine-low_affine))/max(norm,1e-300),
                       best_max=best, elapsed_seconds=time.monotonic()-start)
            history.append(row)
            print(json.dumps(row), flush=True)
            if residual < 1e-11:
                reason = 'numerical candidate tolerance; not an exact certificate'
                break
            if time.monotonic()-start >= args.seconds:
                reason = 'wall-clock cap'
                break
    best_path = args.output_dir/'best-pair-coefficients.npz'
    np.savez_compressed(best_path, coefficients=best_array)
    summary = dict(protocol=protocol, terminal_reason=reason, history=history,
                   best_rank_residual_max=best, elapsed_seconds=time.monotonic()-start,
                   best_artifact=dict(path=str(best_path), bytes=best_path.stat().st_size,
                                      sha256=sha256(best_path.read_bytes()).hexdigest()),
                   status='Numerical candidate, exact lift pending' if best < 1e-11 else 'Bounded heuristic did not meet tolerance; no nonexistence inference')
    (args.output_dir/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(dict(terminal=True, reason=reason, best_max=best)), flush=True)


if __name__ == '__main__':
    main()
