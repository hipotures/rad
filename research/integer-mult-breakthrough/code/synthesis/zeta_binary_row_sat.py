#!/usr/bin/env python3
"""Packed F2 relaxation for short Gaussian-integer zeta row circuits.

Reduction modulo (1+i) maps Gaussian integer unit scales to one. This is
not a necessary relaxation for words with divisions by (1+i) or2. Every
SAT witness is replayed independently and all real sign lifts are tried.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
from itertools import product
import json
from pathlib import Path
import time

import z3
import zeta_reversible_row_sat as reference


REFERENCE_SHA = '89d24a35406f7340411affb24e455187e3d8a882be46ab71f8838370714b56af'


def target_rows(h):
    n = 1 << h
    return [sum(int(j & ~i == 0) << j for j in range(n)) for i in range(n)]


def binary_replay(h, gates, fixed=False):
    rows = [1 << i for i in range(1 << h)]
    for source, target, active in gates:
        if source == target or active not in (0, 1):
            raise AssertionError('Extracted binary row gate is invalid')
        if active:
            rows[target] ^= rows[source]
    wanted = target_rows(h)
    if (rows != wanted) if fixed else (sorted(rows) != sorted(wanted)):
        raise AssertionError('Binary row word does not reach its complete target')
    return rows


def sign_lifts(h, gates):
    active = sum(gate[2] for gate in gates); count = 0
    for signs in product((1, 2), repeat=active):
        iterator = iter(signs)
        word = [(source, target, next(iterator) if enabled else 0)
                for source, target, enabled in gates]
        result = reference.integer_lift(h, word, 3); count += 1
        if result['status'] == 'EXACT GAUSSIAN INTEGER WORD WITH DYADIC UNIT ENDPOINTS':
            result['sign_assignments_tested'] = count
            return result
    return dict(status='NO EXACT REAL SIGN LIFT FOR THIS BINARY WORD',
                sign_assignments_tested=count, bounded_word_only=True)


def make_solver(h, budget, fixed, timeout, seed):
    n = 1 << h
    solver = z3.SolverFor('QF_BV'); solver.set(timeout=round(timeout*1000), random_seed=seed, threads=1)
    states = [[z3.BitVec(f'row_{t}_{i}', n) for i in range(n)] for t in range(budget+1)]
    sources = [z3.BitVec(f'source_{t}', h) for t in range(budget)]
    targets = [z3.BitVec(f'target_{t}', h) for t in range(budget)]
    active = [z3.Bool(f'active_{t}') for t in range(budget)]
    for i in range(n):
        solver.add(states[0][i] == 1 << i)
    def mux(rows, selector):
        out = rows[-1]
        for i in reversed(range(n-1)):
            out = z3.If(selector == i, rows[i], out)
        return out
    for t in range(budget):
        solver.add(sources[t] != targets[t],
                   z3.Implies(z3.Not(active[t]), z3.And(sources[t] == 0, targets[t] == 1)))
        donor = mux(states[t], sources[t])
        for i in range(n):
            solver.add(states[t+1][i] == z3.If(z3.And(active[t], targets[t] == i),
                                             states[t][i] ^ donor, states[t][i]))
        if t:
            both = z3.And(active[t-1], active[t])
            solver.add(z3.Implies(z3.Not(active[t-1]), z3.Not(active[t])))
            solver.add(z3.Implies(both, z3.Or(sources[t] != sources[t-1], targets[t] != targets[t-1])))
            commute = z3.And(targets[t-1] != sources[t], targets[t] != sources[t-1])
            solver.add(z3.Implies(z3.And(both, commute),
                                  z3.ULE(z3.Concat(targets[t-1], sources[t-1]),
                                         z3.Concat(targets[t], sources[t]))))
    wanted = target_rows(h)
    for i in range(n):
        solver.add(states[-1][i] == wanted[i] if fixed else z3.Or([states[-1][i] == row for row in wanted]))
    return solver, states, sources, targets, active


def probe(task):
    h, budget, fixed, timeout, seed, output = task
    if sha256(Path(reference.__file__).read_bytes()).hexdigest() != REFERENCE_SHA:
        raise AssertionError('Pinned modular row-word dependency changed')
    started = time.monotonic(); baseline = reference.baseline(h)
    binary_replay(h, baseline, True)
    solver, states, sources, targets, active = make_solver(h, budget, fixed, timeout, seed)
    destination = Path(output); destination.mkdir(parents=True, exist_ok=False)
    problem = destination/'problem.txt'; problem.write_text(solver.sexpr()+'\n')
    result = solver.check()
    receipt = dict(h=h, arithmetic_gate_budget=budget, field='F2=GaussianIntegers/(1+i)',
                   fixed_labeled_endpoint=fixed, baseline_gate_count=len(baseline), solver_result=str(result),
                   timeout_seconds=timeout, random_seed=seed,
                   smt_problem_sha256=sha256(problem.read_bytes()).hexdigest(),
                   smt_problem_bytes=problem.stat().st_size,
                   statistics={key: value for key, value in solver.statistics()},
                   scope='Necessary only for Gaussian-integer row additions and Gaussian integer unit scales, with stated final permutation. Dyadic divisions by(1+i) or2 remain open; UNSAT is an unverified finite solver result, not a native time lower bound.')
    if result == z3.sat:
        answer = solver.model()
        gates = [(answer.eval(source).as_long(), answer.eval(target).as_long(),
                  int(z3.is_true(answer.eval(enabled))))
                 for source, target, enabled in zip(sources, targets, active)]
        rows = binary_replay(h, gates, fixed)
        if [answer.eval(row).as_long() for row in states[-1]] != rows:
            raise AssertionError('Packed solver state differs from independent binary replay')
        receipt.update(gates=gates, arithmetic_gate_count=sum(gate[2] for gate in gates),
                       exact_sign_lift=sign_lifts(h, gates))
    elif result == z3.unknown:
        receipt['reason_unknown'] = solver.reason_unknown()
    if h == 2 and budget == 3 and result != z3.unsat:
        raise AssertionError('The three-gate support control was not UNSAT')
    if h == 2 and budget == 4 and result != z3.sat:
        raise AssertionError('The known four-gate baseline was not SAT')
    receipt['seconds'] = time.monotonic()-started
    (destination/'result.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    version = importlib.metadata.version('z3-solver')
    if version != reference.Z3_PACKAGE_VERSION:
        raise AssertionError('Solver version differs from retained contract')
    sources = [Path(__file__), Path(reference.__file__)]
    hashes = {source.name: sha256(source.read_bytes()).hexdigest() for source in sources}
    tasks = [(2, 3, False, args.timeout, 71), (2, 4, False, args.timeout, 81),
             (3, 11, False, args.timeout, 91), (3, 11, True, args.timeout, 101)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, tasks=tasks, source_sha256=hashes,
                    solver_package_version=version, solver_version=z3.get_full_version(),
                    hypothesis='A packed binary necessary relaxation can discriminate integer row words from the dyadic escape left by F3/F9 timeouts.',
                    resource_preflight=dict(aggregate_memory_bytes_upper=2*1024*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(probe, (*task, str(args.output/f'case-{task[0]}-{task[1]}-{task[2]}')))
                   for task in tasks]
        for future in as_completed(futures):
            result = future.result(); results.append(result)
            print(json.dumps({key: result[key] for key in
                              ('h', 'arithmetic_gate_budget', 'fixed_labeled_endpoint', 'solver_result', 'seconds')}
                             | {'exact_lift': result.get('exact_sign_lift', {}).get('status')}), flush=True)
    if any(sha256(source.read_bytes()).hexdigest() != hashes[source.name] for source in sources):
        raise AssertionError('Effective binary-row source changed during execution')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
