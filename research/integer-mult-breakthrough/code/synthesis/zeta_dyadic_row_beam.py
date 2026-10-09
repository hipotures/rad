#!/usr/bin/env python3
"""Exact real-dyadic reversible row-word discovery with unit normalizations.

The beam is heuristic and bounded. Failure to find a word is not an
exclusion. Accepted discoveries are replayed over Fraction from both ends.
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


def target_matrix(h):
    n = 1 << h
    return [tuple(int(j & ~i == 0) for j in range(n)) for i in range(n)]


def unit(power, sign=1):
    return Q(sign*(1 << power)) if power >= 0 else Q(sign, 1 << -power)


def canonical_add(receiver, source, power, sign):
    """Return the added row and exact free dyadic-unit normalization."""
    if power >= 0:
        raw = [a+sign*(1 << power)*b for a, b in zip(receiver, source)]
        denominator_bits = 0
    else:
        raw = [(1 << -power)*a+sign*b for a, b in zip(receiver, source)]
        denominator_bits = -power
    first = next(value for value in raw if value)
    normal_sign = 1 if first > 0 else -1
    valuation = min((abs(value) & -abs(value)).bit_length()-1 for value in raw if value)
    out = tuple(normal_sign*value//(1 << valuation) for value in raw)
    return out, normal_sign, denominator_bits-valuation


def bad_rows(state):
    return sum(sum(bool(value) for value in row) != 1 for row in state)


def score(state, style, seed):
    weights = [sum(bool(value) for value in row) for row in state]
    count = sum(weight != 1 for weight in weights)
    nonzeros = sum(weights)
    logarithms = sum((weight-1).bit_length() for weight in weights)
    amplitude = sum(abs(value).bit_length() for row in state for value in row if value)
    mixed = sum(len({abs(value) for value in row if value}) > 1 for row in state)
    fingerprint = sum((j+1)*value for row in state for j, value in enumerate(row))
    tie = (fingerprint*131+seed*173) % 1009
    if style == 'log':
        return logarithms, count, nonzeros, amplitude, tie
    if style == 'interference':
        return count, nonzeros, -mixed, amplitude, tie
    return nonzeros, count, logarithms, amplitude, tie


def extract_path(node):
    result = []
    while node is not None:
        node, event = node
        result.append(event)
    return list(reversed(result))


def apply_word(rows, word):
    rows = [list(map(Q, row)) for row in rows]; largest_grid = 0; largest_bits = 1
    for gate in word:
        if gate[0] == 'add':
            _, receiver, source, coefficient = gate
            coefficient = Q(coefficient)
            rows[receiver] = [a+coefficient*b for a, b in zip(rows[receiver], rows[source])]
        elif gate[0] == 'scale':
            _, receiver, coefficient = gate
            rows[receiver] = [Q(coefficient)*a for a in rows[receiver]]
        else:
            _, a, b = gate; rows[a], rows[b] = rows[b], rows[a]
        for row in rows:
            for value in row:
                if value.denominator & (value.denominator-1):
                    raise AssertionError('A discovered word left the dyadic grid')
                largest_grid = max(largest_grid, value.denominator.bit_length()-1)
                largest_bits = max(largest_bits, abs(value.numerator).bit_length()+1)
    return rows, dict(maximum_matrix_entry_grid_bits=largest_grid,
                      maximum_signed_matrix_numerator_bits=largest_bits)


def bind_word(h, node):
    original = target_matrix(h); n = 1 << h
    rows = [tuple(row) for row in original]; backward = []
    for receiver, source, power, sign, normal_sign, normal_power, wanted in extract_path(node):
        r, s = rows.index(receiver), rows.index(source)
        coefficient = unit(power, sign); normal = unit(normal_power, normal_sign)
        backward.append(('add', r, s, str(coefficient)))
        if normal != 1:
            backward.append(('scale', r, str(normal)))
        actual = tuple(normal*(Q(a)+coefficient*b) for a, b in zip(rows[r], rows[s]))
        if actual != wanted:
            raise AssertionError('Canonical search normalization differs from literal dyadic word')
        rows[r] = wanted
    identity = [tuple(int(i == j) for j in range(n)) for i in range(n)]
    for i in range(n):
        if rows[i] != identity[i]:
            other = rows.index(identity[i]); rows[i], rows[other] = rows[other], rows[i]
            backward.append(('swap', i, other))
    if rows != identity:
        raise AssertionError('The discovered elimination endpoint is not the identity')
    forward = []
    for gate in reversed(backward):
        if gate[0] == 'add':
            _, r, s, coefficient = gate; forward.append(('add', r, s, str(-Q(coefficient))))
        elif gate[0] == 'scale':
            _, r, coefficient = gate; forward.append(('scale', r, str(1/Q(coefficient))))
        else:
            forward.append(gate)
    forward_result, prefix = apply_word(identity, forward)
    backward_result, reverse_prefix = apply_word(original, backward)
    if forward_result != [list(map(Q, row)) for row in original] or backward_result != [list(map(Q, row)) for row in identity]:
        raise AssertionError('Accepted forward/inverse complete matrix replay failed')
    return dict(status='EXACT REAL DYADIC REVERSIBLE ZETA ROW WORD',
                arithmetic_gate_count=sum(gate[0] == 'add' for gate in forward),
                unit_scale_count=sum(gate[0] == 'scale' for gate in forward),
                paid_row_permutation_swaps=sum(gate[0] == 'swap' for gate in forward),
                forward_word=forward, backward_word=backward,
                complete_forward_matrix_columns=n, complete_inverse_matrix_columns=n,
                exact_forward_prefix=prefix, exact_inverse_prefix=reverse_prefix,
                native_activity_compaction=False, native_faster_supplier=False)


def probe(task):
    h, goal, beam, style, exponent_bound, amplitude_bound, seconds, seed = task
    started = time.monotonic(); n = 1 << h
    start = tuple(sorted(target_matrix(h))); frontier = {start: None}
    seen = {start}; history = []; generated = 0; peak_candidates = 0
    stop = 'MAXIMUM_DEPTH_WITHOUT_WITNESS'; found = None
    for depth in range(1, goal+1):
        candidates = {}; remaining = goal-depth
        for state, node in frontier.items():
            for receiver_index, receiver in enumerate(state):
                for source_index, source in enumerate(state):
                    if receiver_index == source_index:
                        continue
                    for power in range(-exponent_bound, exponent_bound+1):
                        for sign in (-1, 1):
                            row, ns, np = canonical_add(receiver, source, power, sign)
                            if max(map(abs, row)) > amplitude_bound:
                                continue
                            new_state = tuple(sorted(state[:receiver_index]+state[receiver_index+1:]+(row,)))
                            if new_state in seen or new_state in candidates:
                                continue
                            if bad_rows(new_state) > remaining:
                                continue
                            event = (receiver, source, power, sign, ns, np, row)
                            child = (node, event); generated += 1
                            if bad_rows(new_state) == 0:
                                found = bind_word(h, child); stop = 'EXACT_WITNESS'; break
                            candidates[new_state] = child
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            if found or time.monotonic()-started > seconds:
                break
        peak_candidates = max(peak_candidates, len(candidates))
        if found:
            break
        if not candidates:
            stop = 'HEURISTIC_FRONTIER_EMPTY'; break
        selected = heapq.nsmallest(beam, candidates, key=lambda state: score(state, style, seed))
        frontier = {state: candidates[state] for state in selected}; seen.update(selected)
        best = selected[0]
        history.append(dict(depth=depth, generated_distinct_candidates=len(candidates),
                            retained_states=len(selected), best_score=score(best, style, seed),
                            elapsed_seconds=time.monotonic()-started))
        if time.monotonic()-started > seconds:
            stop = 'WALL_BUDGET'; break
    if h == 2 and goal == 4 and found is None:
        raise AssertionError('The dyadic beam did not recover the known small baseline control')
    return dict(status='EXACT WITNESS' if found else 'HEURISTIC NO WITNESS; NO EXCLUSION',
                h=h, goal_arithmetic_gates=goal, baseline_gate_count=h*(n//2),
                beam_width=beam, style=style, coefficient_exponent_bound=exponent_bound,
                normalized_integer_entry_bound=amplitude_bound, wall_budget_seconds=seconds,
                seed=seed, stop_reason=stop, generated_distinct_candidates=generated,
                largest_next_frontier_candidates=peak_candidates, depth_history=history,
                witness=found, seconds=time.monotonic()-started,
                scope='Real dyadic row additions with free explicitly retained dyadic unit scales and paid permutations. Bounded beam/value/exponent failure is discovery evidence only, not an exact minimum or native supplier.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--seconds', type=float, default=60)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__); source_hash = sha256(source.read_bytes()).hexdigest()
    tasks = [(2, 4, 300, 'nnz', 1, 8, args.seconds, 20261009061),
             (3, 11, 1200, 'nnz', 1, 8, args.seconds, 20261009062),
             (3, 11, 1200, 'log', 2, 16, args.seconds, 20261009063),
             (3, 11, 1200, 'interference', 1, 8, args.seconds, 20261009064)]
    protocol = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    native_threads_each=1, tasks=tasks, source_sha256={source.name: source_hash},
                    stdlib_only=True,
                    hypothesis='Fractional dyadic cancellation and free unit normalization may shorten the eight-entry zeta word beyond finite-field SAT timeouts; test exact reversible witnesses before any tensor architecture.',
                    resource_preflight=dict(aggregate_memory_bytes_upper=2*1024*1024*1024))
    (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n'); results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(probe, task) for task in tasks]
        for future in as_completed(futures):
            result = future.result(); results.append(result)
            print(json.dumps({key: result[key] for key in ('status', 'h', 'style', 'stop_reason', 'seconds')}
                             | {'witness_gates': result.get('witness', {}).get('arithmetic_gate_count') if result.get('witness') else None}), flush=True)
    if sha256(source.read_bytes()).hexdigest() != source_hash:
        raise AssertionError('Effective dyadic discovery source changed during execution')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
