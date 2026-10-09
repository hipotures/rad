#!/usr/bin/env python3
"""Bounded Gaussian-dyadic cancellation search for reversible zeta rows.

The coefficient family contains i^r(1+i)^k, including negative k. Exact
unit normalization is retained in accepted words. Beam failures are not
exclusions; no native activity compaction is supplied by this experiment.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import heapq
import json
from pathlib import Path
import time


ONE = (Q(1), Q(0))


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def reciprocal(a):
    norm = a[0]*a[0]+a[1]*a[1]
    return a[0]/norm, -a[1]/norm


def power(a, k):
    if k < 0:
        return power(reciprocal(a), -k)
    value = ONE
    for _ in range(k):
        value = times(value, a)
    return value


def matrix(h):
    n = 1 << h
    return [tuple((int(j & ~i == 0), 0) for j in range(n)) for i in range(n)]


def packed_units(bound):
    values = []
    for exponent in range(-bound, bound+1):
        for phase in range(4):
            value = times(power((Q(1), Q(1)), exponent), power((Q(0), Q(1)), phase))
            denominator = max(a.denominator for a in value)
            if denominator & (denominator-1):
                raise AssertionError('A declared Gaussian unit is not dyadic')
            values.append((tuple(int(a*denominator) for a in value), denominator.bit_length()-1,
                           exponent, phase))
    return values


def canonical_add(receiver, donor, numerator, denominator_bits):
    """Return integer Gaussian row and exact power/phase normalization."""
    a, b = numerator; scale = 1 << denominator_bits
    row = tuple((scale*x+a*u-b*v, scale*y+a*v+b*u)
                for (x, y), (u, v) in zip(receiver, donor))
    valuation = 0
    while all((x-y) % 2 == 0 for x, y in row):
        row = tuple(((x+y)//2, (y-x)//2) for x, y in row); valuation += 1
    first = next(value for value in row if value != (0, 0))
    for phase in range(4):
        unit = ((1, 0), (0, 1), (-1, 0), (0, -1))[phase]
        oriented = times(first, unit)
        if oriented[0] > 0 and oriented[1] >= 0:
            return tuple(times(value, unit) for value in row), valuation, phase
    raise AssertionError('The Gaussian unit orbit has no canonical first coefficient')


def normalization(denominator_bits, valuation, phase):
    return times((Q(1 << denominator_bits), Q(0)),
                 times(power((Q(1), Q(1)), -valuation), power((Q(0), Q(1)), phase)))


def bad_rows(state):
    result = 0
    for row in state:
        values = [value for value in row if value != (0, 0)]
        result += len(values) != 1 or values[0] != (1, 0)
    return result


def score(state, style, seed):
    support = sum(value != (0, 0) for row in state for value in row)
    bad = bad_rows(state)
    complex_entries = sum(x != 0 and y != 0 for row in state for x, y in row)
    logarithms = sum((sum(value != (0, 0) for value in row)-1).bit_length() for row in state)
    amplitude = sum((x*x+y*y).bit_length() for row in state for x, y in row)
    tie = (sum((i+1)*(x+3*y) for row in state for i, (x, y) in enumerate(row))+seed) % 1009
    if style == 'phase':
        return bad, support, -complex_entries, amplitude, tie
    if style == 'log':
        return logarithms, bad, support, amplitude, tie
    return support, bad, amplitude, complex_entries, tie


def apply_word(rows, word):
    rows = [[tuple(map(Q, value)) for value in row] for row in rows]
    largest_grid = 0; maximum_prefix_row_l1 = Q(1)
    for gate in word:
        if gate[0] == 'swap':
            _, a, b = gate; rows[a], rows[b] = rows[b], rows[a]
        else:
            coefficient = tuple(Q(value) for value in gate[-1])
            if gate[0] == 'add':
                _, receiver, donor, _ = gate
                rows[receiver] = [add(a, times(coefficient, b)) for a, b in zip(rows[receiver], rows[donor])]
            else:
                _, receiver, _ = gate
                norm = coefficient[0]**2+coefficient[1]**2
                if norm.numerator & (norm.numerator-1) or norm.denominator & (norm.denominator-1):
                    raise AssertionError('Accepted row normalization is not a Gaussian-dyadic unit')
                rows[receiver] = [times(coefficient, a) for a in rows[receiver]]
        for row in rows:
            maximum_prefix_row_l1 = max(maximum_prefix_row_l1, sum(abs(x)+abs(y) for x, y in row))
            for pair in row:
                for value in pair:
                    if value.denominator & (value.denominator-1):
                        raise AssertionError('Accepted Gaussian word left the dyadic grid')
                    largest_grid = max(largest_grid, value.denominator.bit_length()-1)
    return rows, dict(maximum_prefix_grid_bits=largest_grid,
                      maximum_prefix_row_component_l1=str(maximum_prefix_row_l1))


def bind_word(h, node):
    events = []
    while node:
        node, event = node; events.append(event)
    rows = matrix(h); backward = []
    for receiver, donor, numerator, bits, valuation, phase, wanted in reversed(events):
        r, s = rows.index(receiver), rows.index(donor)
        coefficient = tuple(Q(value, 1 << bits) for value in numerator)
        normal = normalization(bits, valuation, phase)
        backward.append(('add', r, s, tuple(map(str, coefficient))))
        if normal != ONE:
            backward.append(('scale', r, tuple(map(str, normal))))
        actual = tuple(times(normal, add(a, times(coefficient, b))) for a, b in zip(rows[r], rows[s]))
        if actual != wanted:
            raise AssertionError('Search unit normalization differs from the literal Gaussian word')
        rows[r] = wanted
    n = 1 << h
    identity = [tuple((int(i == j), 0) for j in range(n)) for i in range(n)]
    for i in range(n):
        if rows[i] != identity[i]:
            other = rows.index(identity[i]); rows[i], rows[other] = rows[other], rows[i]
            backward.append(('swap', i, other))
    forward = []
    for gate in reversed(backward):
        if gate[0] == 'add':
            _, r, s, value = gate
            forward.append(('add', r, s, tuple(str(-Q(v)) for v in value)))
        elif gate[0] == 'scale':
            _, r, value = gate
            forward.append(('scale', r, tuple(map(str, reciprocal(tuple(Q(v) for v in value))))))
        else:
            forward.append(gate)
    actual, prefix = apply_word(identity, forward)
    restored, reverse_prefix = apply_word(matrix(h), backward)
    if actual != [[tuple(map(Q, value)) for value in row] for row in matrix(h)] or restored != [[tuple(map(Q, value)) for value in row] for row in identity]:
        raise AssertionError('The accepted Gaussian forward/inverse complete operator failed')
    return dict(status='EXACT GAUSSIAN DYADIC REVERSIBLE ROW WORD', forward_word=forward, backward_word=backward,
                arithmetic_gate_count=sum(gate[0] == 'add' for gate in forward),
                explicit_unit_scale_count=sum(gate[0] == 'scale' for gate in forward),
                explicit_paid_row_swaps=sum(gate[0] == 'swap' for gate in forward),
                complete_forward_columns=n, complete_inverse_columns=n,
                forward_prefix=prefix, inverse_prefix=reverse_prefix,
                native_activity_compaction=False, complete_native_supplier=False)


def probe(task):
    h, goal, width, style, bound, entry_norm_bound, seconds, seed = task
    started = time.monotonic(); frontier = {tuple(sorted(matrix(h))): None}
    seen = set(frontier); units = packed_units(bound); history = []; generated = 0; witness = None
    stop = 'DEPTH_WITHOUT_WITNESS'
    for depth in range(1, goal+1):
        candidates = {}; remaining = goal-depth
        for state, parent in frontier.items():
            for receiver_index, receiver in enumerate(state):
                for donor_index, donor in enumerate(state):
                    if receiver_index == donor_index:
                        continue
                    for numerator, bits, exponent, coefficient_phase in units:
                        row, valuation, phase = canonical_add(receiver, donor, numerator, bits)
                        if any(x*x+y*y > entry_norm_bound for x, y in row):
                            continue
                        changed = tuple(sorted(state[:receiver_index]+state[receiver_index+1:]+(row,)))
                        if changed in seen or changed in candidates or bad_rows(changed) > remaining:
                            continue
                        event = (receiver, donor, numerator, bits, valuation, phase, row)
                        node = (parent, event); generated += 1
                        if bad_rows(changed) == 0:
                            witness = bind_word(h, node); stop = 'EXACT_WITNESS'; break
                        candidates[changed] = node
                    if witness:
                        break
                if witness:
                    break
            if witness or time.monotonic()-started > seconds:
                break
        if witness:
            break
        if not candidates:
            stop = 'BOUNDED_HEURISTIC_FRONTIER_EMPTY'; break
        selected = heapq.nsmallest(width, candidates, key=lambda state: score(state, style, seed))
        frontier = {state: candidates[state] for state in selected}; seen.update(selected)
        history.append(dict(depth=depth, distinct_candidates=len(candidates), retained=len(selected),
                            best_score=score(selected[0], style, seed), elapsed_seconds=time.monotonic()-started))
        if time.monotonic()-started > seconds:
            stop = 'WALL_BUDGET'; break
    if h == 2 and goal == 4 and witness is None:
        raise AssertionError('The Gaussian-unit beam did not reproduce the known four-add control')
    return dict(h=h, goal_arithmetic_gates=goal, beam_width=width, objective=style,
                coefficient_unit_exponent_bound=bound, normalized_gaussian_entry_norm_bound=entry_norm_bound,
                status='EXACT WITNESS' if witness else 'HEURISTIC NO WITNESS; NO EXCLUSION',
                stop_reason=stop, history=history, witness=witness,
                generated_distinct_states=generated, seconds=time.monotonic()-started, seed=seed,
                scope='Gaussian-dyadic unit coefficient and row-normalization discovery. Bounded beam/exponent/value failure is no mathematical exclusion; native tensor activity grouping and paid wrappers remain open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--seconds', type=float, default=60)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__); digest = sha256(source.read_bytes()).hexdigest()
    tasks = [(2, 4, 100, 'nnz', 2, 32, args.seconds, 20261009081),
             (3, 11, 500, 'nnz', 2, 32, args.seconds, 20261009082),
             (3, 11, 500, 'phase', 2, 32, args.seconds, 20261009083),
             (3, 11, 500, 'log', 2, 32, args.seconds, 20261009084)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, tasks=tasks, source_sha256={source.name: digest}, stdlib_only=True,
                    hypothesis='Gaussian dyadic division by(1+i) escapes the binary necessary model and permits phase cancellation absent from real-unit beams.',
                    resource_preflight=dict(aggregate_memory_bytes_upper=3*1024*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n'); results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(probe, task) for task in tasks]
        for job in as_completed(jobs):
            result = job.result(); results.append(result)
            print(json.dumps({key: result[key] for key in ('h', 'objective', 'status', 'stop_reason', 'seconds')}), flush=True)
    if sha256(source.read_bytes()).hexdigest() != digest:
        raise AssertionError('The Gaussian search source changed during execution')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
