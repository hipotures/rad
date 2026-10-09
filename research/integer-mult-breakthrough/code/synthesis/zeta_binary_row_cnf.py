#!/usr/bin/env python3
"""Explicit CNF discriminator for short reversible integer zeta row words.

All arithmetic is F2. This is a necessary relaxation for Gaussian-integer
row additions and unit scales, not for divisions by2 or(1+i). Accepted
words are independently replayed; absence before interruption is unknown.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import importlib.metadata
from itertools import product
import json
from pathlib import Path
from threading import Timer
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


PYSAT_VERSION = '1.9.dev15'


def zeta_rows(h):
    n = 1 << h
    return [sum(int(j & ~i == 0) << j for j in range(n)) for i in range(n)]


def gate_pairs(n):
    return [(source, target) for target in range(n) for source in range(n) if source != target]


def replay(h, gates):
    rows = [1 << i for i in range(1 << h)]
    for source, target in gates:
        if source == target or not 0 <= source < len(rows) or not 0 <= target < len(rows):
            raise AssertionError('An extracted CNF gate is outside its row domain')
        rows[target] ^= rows[source]
    if sorted(rows) != sorted(zeta_rows(h)):
        raise AssertionError('The extracted CNF word failed independent complete row replay')
    return rows


def baseline(h):
    return [(low, low | (1 << bit)) for bit in range(h)
            for low in range(1 << h) if not low >> bit & 1]


def exhaustive_two_axis_control():
    """Independently enumerate every <=4 active F2 word for the small control."""
    n = 4; wanted = sorted(zeta_rows(2)); counts = []
    for budget in range(5):
        accepted = 0
        for gates in product(gate_pairs(n), repeat=budget):
            rows = [1 << i for i in range(n)]; history = [rows[:]]
            for source, target in gates:
                rows[target] ^= rows[source]; history.append(rows[:])
            if sorted(rows) == wanted:
                accepted += 1
                for t, state in enumerate(history):
                    if sum(row not in wanted for row in state) > budget-t:
                        raise AssertionError('The proposed final-row pruning lost a real word')
                    if sum(row & (row-1) != 0 for row in state) > t:
                        raise AssertionError('The proposed initial-row pruning lost a real word')
        counts.append(accepted)
    if counts[:4] != [0]*4 or counts[4] == 0:
        raise AssertionError('The exhaustive binary control differs from the known baseline')
    return counts


def build(h, budget, prune=True, commuting_order=True):
    n = 1 << h; pool = IDPool(); formula = CNF(); pairs = gate_pairs(n)
    states = [[[pool.id(('row', t, i, b)) for b in range(n)]
               for i in range(n)] for t in range(budget+1)]
    choices = [[pool.id(('gate', t, j)) for j in range(len(pairs)+1)] for t in range(budget)]
    def atmost(lits, bound):
        if bound < len(lits):
            formula.extend(CardEnc.atmost(lits=lits, bound=bound, vpool=pool,
                                         encoding=EncType.seqcounter).clauses)
    def exactly_one(lits):
        formula.append(lits); atmost(lits, 1)
    def equivalence_or(output, inputs):
        formula.append([-output, *inputs])
        formula.extend([[output, -value] for value in inputs])
    def matches(bits, pattern, label):
        equality = pool.id(label)
        literals = [value if pattern >> b & 1 else -value for b, value in enumerate(bits)]
        formula.extend([[-equality, value] for value in literals])
        formula.append([equality, *[-value for value in literals]])
        return equality
    for i in range(n):
        for b in range(n):
            formula.append([states[0][i][b] if i == b else -states[0][i][b]])
    for t in range(budget):
        exactly_one(choices[t]); source = [pool.id(('source', t, i)) for i in range(n)]
        target = [pool.id(('target', t, i)) for i in range(n)]
        for i in range(n):
            equivalence_or(source[i], [choices[t][j] for j, pair in enumerate(pairs) if pair[0] == i])
            equivalence_or(target[i], [choices[t][j] for j, pair in enumerate(pairs) if pair[1] == i])
        donor = [pool.id(('donor', t, b)) for b in range(n)]
        for i in range(n):
            for b in range(n):
                old, new, selected = states[t][i][b], states[t+1][i][b], target[i]
                formula.extend([[-source[i], -old, donor[b]], [-source[i], old, -donor[b]]])
                # selected -> new=old XOR donor; !selected -> new=old.
                formula.extend([[-selected, old, donor[b], -new],
                                [-selected, old, -donor[b], new],
                                [-selected, -old, donor[b], new],
                                [-selected, -old, -donor[b], -new],
                                [selected, -old, new], [selected, old, -new]])
        if t:
            # Every <=budget word can be padded with trailing inactive choices.
            formula.append([-choices[t-1][-1], choices[t][-1]])
            for j in range(len(pairs)):
                # Two adjacent identical active F2 gates cancel.
                formula.append([-choices[t-1][j], -choices[t][j]])
            if commuting_order:
                for old_index, (old_source, old_target) in enumerate(pairs):
                    for new_index, (new_source, new_target) in enumerate(pairs):
                        if old_index > new_index and old_target != new_source and new_target != old_source:
                            formula.append([-choices[t-1][old_index], -choices[t][new_index]])
    wanted = zeta_rows(h)
    for t in range(budget+1):
        final = []
        for i in range(n):
            possible = [matches(states[t][i], row, ('final-match', t, i, j))
                        for j, row in enumerate(wanted)]
            accepted = pool.id(('final-accepted', t, i)); equivalence_or(accepted, possible); final.append(accepted)
            if t == budget:
                formula.append([accepted])
        if prune:
            atmost([-value for value in final], budget-t)
            initial = []
            for i in range(n):
                possible = [matches(states[t][i], 1 << b, ('initial-match', t, i, b)) for b in range(n)]
                accepted = pool.id(('initial-accepted', t, i)); equivalence_or(accepted, possible); initial.append(accepted)
            atmost([-value for value in initial], t)
    return formula, pool, states, choices, pairs


def verify_cnf_model(formula, model):
    values = set(model)
    if any(not any(literal in values for literal in clause) for clause in formula.clauses):
        raise AssertionError('The extracted model does not satisfy every retained CNF clause')


def sign_lift(h, gates):
    """Bounded real ±1 lifts of one binary discovery; no general lift assertion."""
    n = 1 << h; target = zeta_rows(h)
    for tested, signs in enumerate(product((-1, 1), repeat=len(gates)), 1):
        rows = [[int(i == j) for j in range(n)] for i in range(n)]
        for (source, receiver), coefficient in zip(gates, signs):
            rows[receiver] = [a+coefficient*b for a, b in zip(rows[receiver], rows[source])]
        endpoints = []
        for row in rows:
            match = next(((index, sign) for index, wanted in enumerate(target) for sign in (-1, 1)
                          if row == [sign*int(wanted >> b & 1) for b in range(n)]), None)
            if match is None:
                break
            endpoints.append(match)
        if len(endpoints) == n and len({index for index, sign in endpoints}) == n:
            return dict(status='EXACT INTEGER SIGN LIFT', tested_sign_assignments=tested,
                        gates=[[source, receiver, sign] for (source, receiver), sign in zip(gates, signs)],
                        endpoint_signed_row_permutation=endpoints)
    return dict(status='NO EXACT SIGN LIFT OF THIS BINARY WORD', tested_sign_assignments=1 << len(gates))


def probe(task):
    h, budget, engine, seconds, output = task; started = time.monotonic()
    formula, pool, states, choices, pairs = build(h, budget)
    destination = Path(output); destination.mkdir(parents=True, exist_ok=False)
    cnf = destination/'problem.txt'; formula.to_file(str(cnf))
    with Solver(name=engine, bootstrap_with=formula, use_timer=True, with_proof=h == 2) as solver:
        timer = Timer(seconds, solver.interrupt); timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()
        result = dict(h=h, arithmetic_gate_budget=budget, engine=engine,
                      solver_result='SAT' if answer is True else 'UNSAT' if answer is False else 'UNKNOWN_INTERRUPTED',
                      variables=formula.nv, clauses=len(formula.clauses), timeout_seconds=seconds,
                      cnf_sha256=sha256(cnf.read_bytes()).hexdigest(), cnf_bytes=cnf.stat().st_size,
                      statistics=solver.accum_stats(), source_pruning=True, sink_pruning=True,
                      commuting_order=True, solver_proof_independently_checked=False,
                      scope='Finite F2 integer-row necessary model, final row permutation, no dyadic divisions. UNKNOWN is no exclusion; unverified solver UNSAT is not a formally checked theorem or native lower bound.')
        if answer is True:
            model = solver.get_model(); verify_cnf_model(formula, model); values = set(model)
            indexes = [next(j for j, value in enumerate(step) if value in values) for step in choices]
            gates = [pairs[j] for j in indexes if j < len(pairs)]
            rows = replay(h, gates)
            extracted = [sum(int(value in values) << b for b, value in enumerate(row)) for row in states[-1]]
            if extracted != rows:
                raise AssertionError('The CNF state differs from independent row replay')
            result.update(gates=gates, exact_sign_lift=sign_lift(h, gates), arithmetic_gate_count=len(gates))
        elif answer is False and h == 2:
            proof = destination/'proof.txt'; proof.write_text('\n'.join(solver.get_proof())+'\n')
            result.update(proof_sha256=sha256(proof.read_bytes()).hexdigest(), proof_bytes=proof.stat().st_size)
    if h == 2:
        result['exhaustive_control_word_counts_0_to_4'] = exhaustive_two_axis_control()
        if (budget == 3 and answer is not False) or (budget == 4 and answer is not True):
            raise AssertionError('The explicit CNF failed its exhaustive small control')
    result['seconds'] = time.monotonic()-started
    (destination/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--seconds', type=float, default=120)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    if importlib.metadata.version('python-sat') != PYSAT_VERSION:
        raise AssertionError('The SAT package does not match the retained dependency version')
    source = Path(__file__); source_hash = sha256(source.read_bytes()).hexdigest()
    tasks = [(2, 3, 'glucose42'), (2, 4, 'glucose42'), (3, 11, 'glucose42'), (3, 11, 'maplechrono')]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers, native_threads_each=1,
                    source_sha256={source.name: source_hash}, python_sat_version=PYSAT_VERSION, tasks=tasks,
                    hypotheses=['Direct one-hot CNF avoids large bitvector mux expansion.',
                                'Exact changed-row bounds from both endpoints prune impossible chronologies.'],
                    resource_preflight=dict(aggregate_memory_bytes_upper=3*1024*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n'); results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(probe, (*task, args.seconds, str(args.output/f'case-{task[0]}-{task[1]}-{task[2]}')))
                for task in tasks]
        for job in as_completed(jobs):
            result = job.result(); results.append(result)
            print(json.dumps({key: result[key] for key in ('h', 'arithmetic_gate_budget', 'engine', 'solver_result', 'seconds')}), flush=True)
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('The effective CNF source changed during execution')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
