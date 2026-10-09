#!/usr/bin/env python3
"""Exact numerical-dependency versus computational-ancestry controls.

Real integer coefficients act on every Gaussian field. This is a scalar
model discriminator, not a shorter zeta word or a native time certificate.
The cancellation-free toy comparison uses a fanout-allowing clean XOR DAG;
the independently replayed reversible signed word has its own paid endpoints.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def zeta(h):
    n = 1 << h
    return [[int(j & i == j) for j in range(n)] for i in range(n)]


def yates_word(h):
    return [(i, i ^ (1 << bit), 1)
            for bit in range(h) for i in range(1 << h) if i & (1 << bit)]


def replay(n, word):
    matrix = identity(n)
    ancestors = [1 << i for i in range(n)]
    for dst, src, coefficient in word:
        if dst == src or not 0 <= dst < n or not 0 <= src < n:
            raise ValueError('Only distinct valid row-add endpoints are allowed')
        if coefficient not in (-1, 1):
            raise ValueError('This controlled family uses unit signed additions')
        matrix[dst] = [a + coefficient*b for a, b in zip(matrix[dst], matrix[src])]
        ancestors[dst] |= ancestors[src]
    return matrix, ancestors


def forbidden_ancestry(h, ancestors):
    """Every aligned recursive block's right inputs to left outputs."""
    violations = []
    for bit in range(h):
        half = 1 << bit
        for start in range(0, 1 << h, 2*half):
            right = ((1 << half)-1) << (start+half)
            for output in range(start, start+half):
                hit = ancestors[output] & right
                if hit:
                    violations.append((bit, start, output, hit))
    return violations


def apply(matrix, values):
    return [(sum(c*v[0] for c, v in zip(row, values)),
             sum(c*v[1] for c, v in zip(row, values))) for row in matrix]


def scalar_probe(h):
    n = 1 << h
    ordinary = yates_word(h)
    standard, ancestry = replay(n, ordinary)
    if standard != zeta(h) or forbidden_ancestry(h, ancestry):
        raise AssertionError('The ordinary exact zeta word must obey the ancestry scope')
    excursion = [(0, n//2, 1), (0, n//2, -1)] + ordinary
    restored, excursion_ancestry = replay(n, excursion)
    violations = forbidden_ancestry(h, excursion_ancestry)
    if restored != standard or not violations:
        raise AssertionError('Numerical equality must coexist with forbidden ancestry')
    for output in range(n//2):
        if any(restored[output][source] for source in range(n//2, n)):
            raise AssertionError('The final upper-right coefficient block must remain zero')
    inverse = [(a, b, -c) for a, b, c in reversed(excursion)]
    composite, _ = replay(n, excursion + inverse)
    if composite != identity(n):
        raise AssertionError('The complete chronological inverse must restore all columns')
    corrupted, _ = replay(n, [(0, n//2, 1)] + ordinary)
    if corrupted == standard:
        raise AssertionError('Deleting the cancelling return must alter the final operator')
    fields = [[(i-7*k, 3*i+5*k-11) for i in range(n)] for k in range(4)]
    for field in fields:
        if apply(restored, field) != apply(standard, field):
            raise AssertionError('Every Gaussian payload field must agree')
    return dict(selected_width=h, dimension=n, full_operator_columns=n,
                ordinary_additions=len(ordinary), excursion_additions=len(excursion),
                final_operator_exact=True, final_upper_right_zero=True,
                restored_endpoint_with_forbidden_ancestry=True,
                recursive_ancestry_violations=len(violations),
                first_violations=violations[:3], all_gaussian_fields=4,
                chronological_inverse_exact=True, omitted_return_rejected=True,
                ancestry_sha256=sha256(json.dumps(excursion_ancestry).encode()).hexdigest(),
                scope='An identity detour falsifies a final-zero-to-no-ancestry inference; '
                      'it adds two gates and is not an improved circuit.')


def xor_dag_minimum(cancellation_free):
    """Exhaust all available-value sets for the four-input paper toy."""
    wanted = frozenset((3, 7, 15, 14))
    frontier = {frozenset((1, 2, 4, 8))}
    layer_counts = []
    for depth in range(6):
        layer_counts.append(len(frontier))
        if any(wanted <= state for state in frontier):
            return dict(minimum_additions=depth, exhaustive_layer_states=layer_counts,
                        gate_model='Disjoint-support XOR DAG' if cancellation_free else
                                   'Unrestricted XOR DAG; intermediates retained and fanout free')
        next_frontier = set()
        for state in frontier:
            values = sorted(state)
            for i, left in enumerate(values):
                for right in values[i+1:]:
                    if cancellation_free and left & right:
                        continue
                    result = left ^ right
                    if result and result not in state:
                        next_frontier.add(state | {result})
        frontier = next_frontier
    raise AssertionError('The tiny declared model did not reach its five-gate control')


def signed_toy_replay(events, matrix):
    result = [row[:] for row in matrix]
    for kind, dst, src, coefficient in events:
        if kind == 'sign':
            result[dst] = [coefficient*x for x in result[dst]]
        elif kind == 'add':
            result[dst] = [a+coefficient*b for a, b in zip(result[dst], result[src])]
        else:
            raise ValueError('Unknown paid toy event')
    return result


def cancellation_toy():
    unrestricted = xor_dag_minimum(False)
    disjoint = xor_dag_minimum(True)
    if (unrestricted['minimum_additions'], disjoint['minimum_additions']) != (4, 5):
        raise AssertionError('The four-input exhaustive model distinction must be exact')
    target = [[1, 1, 0, 0], [1, 1, 1, 0], [1, 1, 1, 1], [0, 1, 1, 1]]
    events = [('add', 1, 0, 1), ('add', 2, 1, 1), ('add', 3, 2, 1),
              ('sign', 0, 0, -1), ('add', 0, 3, 1)]
    raw = signed_toy_replay(events, identity(4))
    permutation = [1, 2, 3, 0]
    final = [raw[i] for i in permutation]
    if final != target:
        raise AssertionError('The four-add Gaussian word must retain its sign and output order')
    inverse_events = [(kind, dst, src, coefficient if kind == 'sign' else -coefficient)
                      for kind, dst, src, coefficient in reversed(events)]
    unpermuted = [None]*4
    for output, source in enumerate(permutation):
        unpermuted[source] = final[output]
    if signed_toy_replay(inverse_events, unpermuted) != identity(4):
        raise AssertionError('The true inverse must restore every arbitrary input column')
    unsigned = signed_toy_replay([e for e in events if e[0] != 'sign'], identity(4))
    if [unsigned[i] for i in permutation] == target:
        raise AssertionError('A field-two XOR cancellation must not be copied unsigned to Gaussian data')
    if raw == target:
        raise AssertionError('A free output permutation must not be silently omitted')
    return dict(unrestricted_xor=unrestricted, cancellation_free_xor=disjoint,
                gaussian_complete_matrix=target, reversible_word=events,
                paid_row_additions=4, paid_unit_signs=1, output_permutation=permutation,
                complete_inverse_exact=True, omitted_sign_and_permutation_rejected=True,
                clean_dag_space_differs_from_reversible_word=True,
                scope='Independent exact four-input replay of a primary-source model gap; '
                      'the signed Gaussian lift is a different complete reversible ledger, '
                      'not a zeta word, native transfer or exponent improvement.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('A positive worker count is required')
    source = Path(__file__)
    before = sha256(source.read_bytes()).hexdigest()
    tasks = [1, 3] if args.bounded else [1, 2, 4, 7]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=before,
                    workers=args.workers, selected_widths=tasks, seed=None,
                    randomness='None; complete exact deterministic controls',
                    scalar_model='Real integer row operators on arbitrary Gaussian payloads',
                    question='Does a zero final upper-right block imply forbidden ancestry is absent?',
                    maximum_dimension=1 << max(tasks),
                    maximum_declared_matrix_cells=1 << (2*max(tasks)),
                    native_time_measured=False, external_dependencies=False)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    started = time.monotonic()
    if args.workers == 1:
        cases = [scalar_probe(h) for h in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            cases = list(pool.map(scalar_probe, tasks))
    toy = cancellation_toy()
    if sha256(source.read_bytes()).hexdigest() != before:
        raise AssertionError('The frozen scientific source changed during execution')
    summary = dict(status='PASS EXACT NUMERICAL DEPENDENCY AND ANCESTRY DISTINCTION',
                   completed_utc=datetime.now(timezone.utc).isoformat(),
                   seconds=time.monotonic()-started, source_sha256=before,
                   cases=cases, cancellation_toy=toy,
                   not_proved=['Any shorter zeta word', 'General circuit lower bound',
                               'Native Gaussian time or dirty helper capacity',
                               'All-size transfer or a multiplication exponent'])
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(dict(status=summary['status'], cases=len(cases),
                          exact_operator_columns=sum(c['full_operator_columns'] for c in cases),
                          tiny_dag_minima=[4, 5], seconds=summary['seconds'])), flush=True)


if __name__ == '__main__':
    main()
