#!/usr/bin/env python3
"""Exact finite source-as-helper and globally coupled cycle echoes.

Both words implement y+=x on arbitrary values without a matched physical
source/sink copy. The global word uses B=I+P^{-1}, whose determinant is 2.
All inverses/scales, fixed anchors and gate incidences are retained. Factors
are preflighted per case; larger cases are declined before allocation.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import time

import dirty_color_echo_dp as dp
import dirty_color_echo_full_dp as parallel
from frame_factor_guards import guard_graph
from literal_bank_exchange_control import invert, scalar_columns


def operations(kind):
    m = 3
    if kind == 'global-cycle':
        B = [('add', 0, 2, Q(1)), ('add', 1, 0, Q(1)),
             ('add', 1, 2, Q(-1)), ('scale', 2, Q(2)),
             ('add', 2, 1, Q(1)), ('add', 2, 0, Q(-1))]
        copies = [('add', m + j, (j + 1) % m, Q(1)) for j in range(m)]
        return invert(copies) + B + copies + invert(B)
    if kind == 'sequential-commutators':
        return [event for i in range(m) for event in
                [('add', m + i, (i + 1) % m, Q(-1)),
                 ('add', (i + 1) % m, i, Q(1)),
                 ('add', m + i, (i + 1) % m, Q(1)),
                 ('add', (i + 1) % m, i, Q(-1))]]
    raise ValueError('Unknown source echo topology')


def preflight(vertices, domain, edges, order):
    factors = [(j,) for j in range(vertices)] + [(a, b) for a, b, _ in edges]
    decisions = 0
    peak = 0
    evaluations = 0
    stages = []
    for variable in order:
        selected = [F for F in factors if variable in F]
        remaining = [F for F in factors if variable not in F]
        neighbors = tuple(sorted({v for F in selected for v in F if v != variable}))
        entries = domain ** len(neighbors)
        live = 2 * entries + sum(domain ** len(F) for F in selected + remaining) + decisions
        peak = max(peak, live)
        evaluations += entries * domain
        stages.append(dict(variable=variable, width=len(neighbors), factor_entries=entries,
                           live_uint16_entries=live))
        decisions += entries
        factors = remaining + [neighbors]
    return dict(order=order, stages=stages, peak_factor_and_decision_bytes=2 * peak,
                candidate_cost_evaluations=evaluations,
                maximum_factor_entries=max(stage['factor_entries'] for stage in stages))


def probe(spec):
    kind, frame_kind, binary, directory, budget, threads = spec
    started = time.monotonic()
    n = m = 3
    word = operations(kind)
    scalar = scalar_columns(word, m)
    scalar_corruption = scalar_columns(word, m, True)
    shears = [(e[1], e[2], e[3]) for e in word if e[0] == 'add']
    zero = dp.f.le((), n)
    full = dp.f.le((1, 2, 4), n)
    starts = [dp.f.le((1 << j,), n) for j in range(m)] + [zero] * m
    ends = [full] * m + [dp.f.le(dp.f.perpendicular((1 << j,), n), n) for j in range(m)]
    frames = dp.f.lagrangians(n) if frame_kind == 'all-Lagrangian' else [dp.f.le(E, n) for E in dp.f.subspaces(n)]
    frames = sorted(frames)
    table = [[dp.f.distance(a, b, n) for b in frames] for a in frames]
    ids = {F: j for j, F in enumerate(frames)}
    edges, boundaries, constant = dp.f.incidence_graph(shears, 2 * m, starts, ends)
    unary = [[sum(table[j][ids[F]] for F in bound) for j in range(len(frames))]
             for bound in boundaries]
    order = dp.minfill(len(shears), edges)
    guard = guard_graph(edges, unary, table, constant, order)
    estimate = preflight(len(shears), len(frames), edges, order)
    result = dict(topology=kind, frame_kind=frame_kind, active_bits=n, data_roles=m,
                  frame_count=len(frames), payload_stock=2 * m, capacity=2 * m * n,
                  complete_endpoint_floor=sum(dp.f.distance(a, b, n) for a, b in zip(starts, ends)),
                  scalar_columns=scalar, wrong_copy_control=scalar_corruption,
                  scalar_operation_counts=dict(Counter(e[0] for e in word)),
                  nonunit_scales=[str(e[2]) for e in word if e[0] == 'scale'],
                  guarded_instance=guard, preflight=estimate,
                  native_worker_threads=threads, memory_budget_GiB=budget)
    if estimate['maximum_factor_entries'] > parallel.FACTOR_MAX_ENTRIES or estimate['peak_factor_and_decision_bytes'] + 2**30 > budget * 2**30:
        result.update(status='NOT RUN: PREFLIGHT STORAGE BOUND', seconds=time.monotonic() - started,
                      scope='Scalar word passes; no finite minimum is inferred from a declined factor graph.')
        return result
    os.environ['OMP_NUM_THREADS'] = str(threads)
    os.environ['OMP_DYNAMIC'] = 'FALSE'
    exact = parallel.full_solve(binary, directory, edges, unary, table, constant, order)
    if exact['peak_live_uint16_entries'] * 2 != estimate['peak_factor_and_decision_bytes']:
        raise ValueError('Completed factor payload differs from preflight')
    current = list(starts)
    histogram = Counter()
    for step, (a, b, c) in enumerate(shears):
        F = frames[exact['assignment'][step]]
        for role in (a, b):
            rank = dp.f.distance(current[role], F, n)
            if rank:
                histogram[rank] += 1
            current[role] = F
    for old, F in zip(current, ends):
        rank = dp.f.distance(old, F, n)
        if rank:
            histogram[rank] += 1
    if sum(rank * count for rank, count in histogram.items()) != exact['optimum']:
        raise ValueError('Complete source echo chronology fails independent path replay')
    result.update(status='EXACT FINITE RANK DEFICIT' if exact['optimum'] < result['capacity']
                  else 'EXACT FINITE MINIMUM WITHOUT RANK DEFICIT',
                  minimum_rank_charge=exact['optimum'], deficit=result['capacity'] - exact['optimum'],
                  exact_min_sum=exact, chronological_histogram=dict(sorted(histogram.items())),
                  complete_frames=frames,
                  complete_operations=[[e[0], *e[1:3], str(e[3])] if e[0] == 'add'
                                       else [e[0], e[1], str(e[2])] for e in word],
                  seconds=time.monotonic() - started,
                  scope='Exact finite metric optimum for this complete source-as-helper word/domain. Every logical source/sink column, scale/inverse and physical frame path is retained. Literal Gaussian lifts, tape movement, coefficient precision, dirty auxiliary C stock and multiplier transfer remain separate.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--memory-budget-GiB', type=float, default=8)
    parser.add_argument('--cxx', default='c++')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    build = args.output.parent / 'builds'
    build.mkdir(exist_ok=False)
    source = build / 'parallel.cpp'
    binary = build / 'parallel'
    subprocess.run(['patch', '-o', str(source.resolve()), str(dp.CPP), str(parallel.PATCH)],
                   check=True, text=True, capture_output=True)
    subprocess.run([args.cxx, '-O3', '-std=c++17', '-fopenmp', str(source), '-o', str(binary)],
                   check=True, text=True, capture_output=True)
    paths = [Path(__file__), Path(dp.__file__), Path(parallel.__file__), dp.CPP, parallel.PATCH,
             Path(__file__).with_name('frame_factor_guards.py'),
             Path(__file__).with_name('literal_bank_exchange_control.py'),
             Path(dp.f.__file__), Path(dp.f.__file__).with_name('lagrangian_graph_completion.py'),
             Path(dp.f.__file__).with_name('trimmed_zeta_dirty_probe.py'), dp.f.SIDE_SOURCE,
             Path(__file__).with_name('pauli_tensor_discriminator.py')]
    hashes = {path: sha256(path.read_bytes()).hexdigest() for path in paths}
    specs = [(topology, domain, binary, args.output.parent / f'derived/case-{i}',
              args.memory_budget_GiB, args.threads)
             for i, (topology, domain) in enumerate((t, d) for t in
                 ('global-cycle', 'sequential-commutators') for d in ('L_E', 'all-Lagrangian'))]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_worker_threads_each=args.threads,
                    specs=[list(spec[:2]) for spec in specs], memory_budget_GiB_each=args.memory_budget_GiB,
                    source_sha256={path.name: value for path, value in hashes.items()},
                    generated_parallel_source_sha256=sha256(source.read_bytes()).hexdigest(),
                    compiler=subprocess.run([args.cxx, '--version'], check=True, text=True,
                                            capture_output=True).stdout.splitlines()[0],
                    compile_flags=['-O3', '-std=c++17', '-fopenmp'],
                    hypothesis='Cross-source temporary couplings replace separately materialized class center/side vectors and avoid matched middle copies.')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    cases = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(probe, spec): spec for spec in specs}
        for future in as_completed(jobs):
            result = future.result()
            cases.append(result)
            print(json.dumps({key: result[key] for key in ('status', 'topology', 'frame_kind', 'seconds')}
                             | {key: result[key] for key in ('minimum_rank_charge', 'capacity') if key in result}), flush=True)
    if any(sha256(path.read_bytes()).hexdigest() != value for path, value in hashes.items()):
        raise ValueError('Effective source changed during source-echo experiment')
    (args.output / 'certificate.json').write_text(json.dumps(dict(cases=cases), indent=2) + '\n')


if __name__ == '__main__':
    main()
