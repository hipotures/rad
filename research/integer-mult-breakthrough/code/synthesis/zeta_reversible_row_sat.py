#!/usr/bin/env python3
"""Finite-field necessary relaxation for shorter reversible zeta row words.

One paid arithmetic gate adds a scalar multiple of one row to another.
Dyadic unit row scales and row permutations are free in this small model.
Finite-field SAT discoveries require exact Gaussian-dyadic lifting; UNSAT
is a solver result under this encoding, not a formally verified lower bound.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import time

import z3


Z3_PACKAGE_VERSION = '4.15.4.0'


def plus3(a, b):
    zero = z3.BitVecVal(0, 2)
    return z3.If(a == 0, b, z3.If(b == 0, a,
        z3.If(a == b, z3.If(a == 1, z3.BitVecVal(2, 2), z3.BitVecVal(1, 2)), zero)))


def neg3(a):
    return z3.If(a == 0, a, z3.If(a == 1, z3.BitVecVal(2, 2), z3.BitVecVal(1, 2)))


def times3(a, b):
    return z3.If(z3.Or(a == 0, b == 0), z3.BitVecVal(0, 2),
                 z3.If(a == b, z3.BitVecVal(1, 2), z3.BitVecVal(2, 2)))


def symbols(field):
    return list(range(3)) if field == 3 else [a+4*b for b in range(3) for a in range(3)]


def field_plus(a, b, field):
    if field == 3:
        return plus3(a, b)
    return z3.Concat(plus3(z3.Extract(3, 2, a), z3.Extract(3, 2, b)),
                     plus3(z3.Extract(1, 0, a), z3.Extract(1, 0, b)))


def field_times(a, b, field):
    if field == 3:
        return times3(a, b)
    ar, ai = z3.Extract(1, 0, a), z3.Extract(3, 2, a)
    br, bi = z3.Extract(1, 0, b), z3.Extract(3, 2, b)
    return z3.Concat(plus3(times3(ar, bi), times3(ai, br)),
                     plus3(times3(ar, br), neg3(times3(ai, bi))))


def exact_plus(a, b, field):
    return (a+b) % 3 if field == 3 else ((a % 4+b % 4) % 3 + 4*((a//4+b//4) % 3))


def exact_times(a, b, field):
    if field == 3:
        return a*b % 3
    ar, ai, br, bi = a % 4, a//4, b % 4, b//4
    return (ar*br-ai*bi) % 3 + 4*((ar*bi+ai*br) % 3)


def pack(values, bits):
    return sum(value << (bits*index) for index, value in enumerate(values))


def unpack(word, n, bits):
    return [(word >> (bits*index)) & ((1 << bits)-1) for index in range(n)]


def zeta_matrix(h):
    n = 1 << h
    return [[int(j & ~i == 0) for j in range(n)] for i in range(n)]


def field_control(field):
    bits = 2 if field == 3 else 4
    for a in symbols(field):
        for b in symbols(field):
            literal_a, literal_b = z3.BitVecVal(a, bits), z3.BitVecVal(b, bits)
            if z3.simplify(field_plus(literal_a, literal_b, field)).as_long() != exact_plus(a, b, field):
                raise AssertionError('Finite-field addition truth table differs')
            if z3.simplify(field_times(literal_a, literal_b, field)).as_long() != exact_times(a, b, field):
                raise AssertionError('Finite-field multiplication truth table differs')
    for a in symbols(field)[1:]:
        if sum(exact_times(a, b, field) == 1 for b in symbols(field)) != 1:
            raise AssertionError('Declared field contains a noninvertible nonzero scalar')


def exact_replay(h, gates, field):
    n = 1 << h; rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for source, target, coefficient in gates:
        if source == target or coefficient not in symbols(field):
            raise AssertionError('An extracted row gate is outside its field/domain')
        rows[target] = [exact_plus(a, exact_times(coefficient, b, field), field)
                        for a, b in zip(rows[target], rows[source])]
    target = zeta_matrix(h); final = []
    for row in rows:
        match = next(((index, scalar) for index, wanted in enumerate(target)
                      for scalar in symbols(field)[1:]
                      if row == [exact_times(scalar, value, field) for value in wanted]), None)
        if match is None:
            raise AssertionError('Extracted row word does not reach a target projective row')
        final.append(match)
    if len({index for index, scalar in final}) != n:
        raise AssertionError('Extracted target permutation is singular')
    return rows, final


def integer_lift(h, gates, field):
    """Try one bounded natural lift, without promoting modular SAT to exact."""
    n = 1 << h; rows = [[(int(i == j), 0) for j in range(n)] for i in range(n)]
    lifted = []
    def coefficient(code):
        real = (0, 1, -1)[code % 4]
        imag = 0 if field == 3 else (0, 1, -1)[code//4]
        return real, imag
    for source, target, code in gates:
        a, b = coefficient(code); lifted.append((source, target, [a, b]))
        rows[target] = [(x+a*u-b*v, y+a*v+b*u)
                        for (x, y), (u, v) in zip(rows[target], rows[source])]
    targets = zeta_matrix(h); final = []
    for row in rows:
        found = None
        for index, wanted in enumerate(targets):
            nonzero = next((value for value, flag in zip(row, wanted) if flag), None)
            if nonzero is None or nonzero == (0, 0):
                continue
            if row != [nonzero if flag else (0, 0) for flag in wanted]:
                continue
            norm = nonzero[0]**2+nonzero[1]**2
            if norm & (norm-1):
                continue
            found = (index, nonzero, norm.bit_length()-1); break
        if found is None:
            return dict(status='NO EXACT LIFT IN THE TESTED SMALL GAUSSIAN REPRESENTATIVES',
                        tested_coefficients=lifted)
        final.append(found)
    if len({index for index, scalar, bits in final}) != n:
        raise AssertionError('A proposed exact lift has singular endpoint permutation')
    return dict(status='EXACT GAUSSIAN INTEGER WORD WITH DYADIC UNIT ENDPOINTS',
                gates=lifted, endpoint_row_permutation_and_scalars=final,
                arithmetic_gate_count=sum(bool(code) for source, target, code in gates),
                source_grid_bits=0,
                scope='Exact finite lifted row word; tensor activity compaction and native recurrence remain open.')


def baseline(h):
    n = 1 << h; gates = []
    for bit in range(h):
        for low in range(n):
            if not low >> bit & 1:
                gates.append((low, low | (1 << bit), 1))
    for field in (3, 9):
        exact_replay(h, gates, field)
    lifted = integer_lift(h, gates, 3)
    if lifted['status'] != 'EXACT GAUSSIAN INTEGER WORD WITH DYADIC UNIT ENDPOINTS':
        raise AssertionError('The standard integer baseline failed exact replay')
    return gates


def model(h, budget, field, timeout, seed):
    n = 1 << h; bits = 2 if field == 3 else 4
    solver = z3.SolverFor('QF_BV'); solver.set(timeout=round(1000*timeout), random_seed=seed, threads=1)
    states = [[z3.BitVec(f'r_{step}_{row}', bits*n) for row in range(n)]
              for step in range(budget+1)]
    sources = [z3.BitVec(f'source_{step}', h) for step in range(budget)]
    targets = [z3.BitVec(f'target_{step}', h) for step in range(budget)]
    coefficients = [z3.BitVec(f'coefficient_{step}', bits) for step in range(budget)]
    for row in range(n):
        solver.add(states[0][row] == pack([int(row == column) for column in range(n)], bits))
    def select(rows, index):
        return z3.If(index == 0, rows[0], select_tail(rows, index, 1))
    def select_tail(rows, index, start):
        return rows[-1] if start == n-1 else z3.If(index == start, rows[start], select_tail(rows, index, start+1))
    for step in range(budget):
        source, target, scalar = sources[step], targets[step], coefficients[step]
        solver.add(source != target, z3.Or([scalar == value for value in symbols(field)]))
        # Noops encode budgets <=g and include coefficients vanishing modulo3.
        solver.add(z3.Implies(scalar == 0, z3.And(source == 0, target == 1)))
        donor = select(states[step], source); receiver = select(states[step], target)
        outputs = []
        for column in range(n):
            lo, hi = bits*column, bits*(column+1)-1
            outputs.append(field_plus(z3.Extract(hi, lo, receiver),
                                     field_times(scalar, z3.Extract(hi, lo, donor), field), field))
        updated = z3.Concat(*reversed(outputs))
        for row in range(n):
            solver.add(states[step+1][row] == z3.If(target == row, updated, states[step][row]))
        if step:
            previous_scalar = coefficients[step-1]
            previous_source, previous_target = sources[step-1], targets[step-1]
            active = z3.And(previous_scalar != 0, scalar != 0)
            solver.add(z3.Implies(previous_scalar == 0, scalar == 0))
            # Consecutive equal row additions merge in this <=budget model.
            solver.add(z3.Implies(active, z3.Or(source != previous_source, target != previous_target)))
            commute = z3.And(previous_target != source, target != previous_source)
            # Include same-target different-source commuting gates. Extend
            # selector words before lexicographic comparison to avoid wrap.
            previous_key = z3.Concat(previous_target, previous_source)
            key = z3.Concat(target, source)
            solver.add(z3.Implies(z3.And(active, commute), z3.ULE(previous_key, key)))
    target_matrix = zeta_matrix(h)
    for row in states[-1]:
        allowed = [pack([exact_times(scalar, value, field) for value in wanted], bits)
                   for wanted in target_matrix for scalar in symbols(field)[1:]]
        solver.add(z3.Or([row == value for value in allowed]))
    return solver, states, sources, targets, coefficients


def probe(task):
    h, budget, field, timeout, seed, output = task
    started = time.monotonic(); field_control(field); standard = baseline(h)
    solver, states, sources, targets, coefficients = model(h, budget, field, timeout, seed)
    build_seconds = time.monotonic()-started
    text = solver.sexpr(); destination = Path(output)
    destination.mkdir(parents=True, exist_ok=False)
    problem = destination/'problem.txt'; problem.write_text(text+'\n')
    status = solver.check(); result = dict(
        h=h, field_order=field, field_definition='F3' if field == 3 else 'F3[i], i^2=-1',
        arithmetic_gate_budget=budget, baseline_gate_count=len(standard), timeout_seconds=timeout,
        random_seed=seed, solver_result=str(status), build_seconds=build_seconds,
        smt_problem_sha256=sha256(problem.read_bytes()).hexdigest(), smt_problem_bytes=problem.stat().st_size,
        symmetry_scope='Trailing noops, adjacent gate merge, lex order of commuting adjacent gates only.',
        free_model_operations='Dyadic unit row scales and arbitrary row permutations; all field coefficients in row additions.',
        statistics={key: value for key, value in solver.statistics()},
        scientific_scope='Necessary finite-field relaxation of invertible Gaussian-dyadic row words; SAT requires exact lift; UNSAT is an unverified-solver finite result, not formal verification or a native time lower bound.')
    if status == z3.sat:
        answer = solver.model()
        gates = [(answer.eval(source).as_long(), answer.eval(target).as_long(), answer.eval(coefficient).as_long())
                 for source, target, coefficient in zip(sources, targets, coefficients)]
        replayed, final = exact_replay(h, gates, field)
        for step, row in enumerate(states[-1]):
            if unpack(answer.eval(row).as_long(), 1 << h, 2 if field == 3 else 4) != replayed[step]:
                raise AssertionError('Extracted solver state disagrees with independent field replay')
        result.update(gates=gates, endpoint_permutation_and_units=final,
                      arithmetic_gate_count=sum(bool(coefficient) for source, target, coefficient in gates),
                      exact_lift=integer_lift(h, gates, field))
    elif status == z3.unknown:
        result['reason_unknown'] = solver.reason_unknown()
    if h == 2 and budget == 3 and status != z3.unsat:
        raise AssertionError('The four-entry support control did not reproduce its three-gate obstruction')
    if h == 2 and budget == 4 and status != z3.sat:
        raise AssertionError('The known four-gate baseline did not satisfy the encoding')
    result['seconds'] = time.monotonic()-started
    (destination/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--timeout', type=float, default=120)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    version = importlib.metadata.version('z3-solver')
    if version != Z3_PACKAGE_VERSION:
        raise AssertionError('The solver package version differs from the pinned experiment')
    source = Path(__file__); source_hash = sha256(source.read_bytes()).hexdigest()
    tasks = [(2, 3, 3, args.timeout, 31), (2, 4, 9, args.timeout, 41),
             (3, 11, 3, args.timeout, 51), (3, 11, 9, args.timeout, 61)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, tasks=tasks, source_sha256={source.name: source_hash},
                    solver_package_version=version, solver_version=z3.get_full_version(),
                    hypothesis='One fewer reversible row addition for Z3 could leave a large conditional activity-mask moment deficit; test the necessary F3/F9 relaxation before any native architecture.',
                    resource_preflight=dict(aggregate_memory_bytes_upper=4*1024*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(probe, (*task, str(args.output/f'case-{task[0]}-{task[1]}-{task[2]}'))): task
                for task in tasks}
        for future in as_completed(jobs):
            result = future.result(); results.append(result)
            print(json.dumps({key: result[key] for key in
                              ('h', 'field_order', 'arithmetic_gate_budget', 'solver_result', 'seconds')}
                             | {'exact_lift_status': result.get('exact_lift', {}).get('status')}), flush=True)
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('Effective SAT source changed during execution')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
