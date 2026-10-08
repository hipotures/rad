#!/usr/bin/env python3
"""Independent binary Gram, physical, sharing and guard audit of controller reuse.

The new producer is read only as a saved certificate. Its closed projector,
containment and admissibility routines are never imported. Projectors here are
constructed as B (B^T B)^-1 B^T over F2 from explicit basis columns. The fixed
flow planner/compiler is retained under this independent predicate.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import random
import time
from unittest.mock import patch

import frame_reuse
from downstream_complex_circuit import TripleSideCircuit
from review_asymmetric_motif import independent_saving
from review_complex_frames import (complement, complete_scalar_matrix, dot,
                                   gram, rank, residual, space)


def bits(value):
    while value:
        bit = value & -value
        yield bit
        value ^= bit


def xor_selected(columns, coefficient):
    value = 0
    while coefficient:
        bit = coefficient & -coefficient
        value ^= columns[bit.bit_length()-1]
        coefficient ^= bit
    return value


@lru_cache(maxsize=None)
def inverse(rows):
    n = len(rows)
    augmented = [row | (1 << (n+i)) for i, row in enumerate(rows)]
    for j in range(n):
        selected = next(i for i in range(j, n) if augmented[i] >> j & 1)
        augmented[j], augmented[selected] = augmented[selected], augmented[j]
        for i in range(n):
            if i != j and augmented[i] >> j & 1:
                augmented[i] ^= augmented[j]
    assert all(row & ((1 << n)-1) == 1 << i for i, row in enumerate(augmented))
    answer = tuple(row >> n for row in augmented)
    assert all(dot(row, answer[j]) == int(i == j)
               for i, row in enumerate(rows) for j in range(n))
    assert all((answer[i] >> j & 1) == (answer[j] >> i & 1)
               for i in range(n) for j in range(n))
    return answer


@dataclass(frozen=True)
class GramFrame:
    h: int
    tag: tuple

    @property
    def dimension(self):
        return len(geometry(self)[0])

    @property
    def characteristic(self):
        return geometry(self)[2]

    def project(self, value):
        return xor_selected(geometry(self)[1], value)


@lru_cache(maxsize=None)
def geometry(frame):
    basis = tuple(space(frame.tag, frame.h))
    rows = tuple(gram(basis))
    inv = inverse(rows)
    columns = []
    for i in range(frame.h):
        coordinate = 1 << i
        pairings = sum(dot(coordinate, v) << j for j, v in enumerate(basis))
        coefficient = sum(dot(row, pairings) << j for j, row in enumerate(inv))
        projected = xor_selected(basis, coefficient)
        # Membership follows from its explicit basis coefficients. These
        # equations independently verify the orthogonal projection columns.
        assert all(dot(coordinate ^ projected, v) == 0 for v in basis)
        columns.append(projected)
    columns = tuple(columns)
    assert all(xor_selected(columns, v) == v for v in basis)
    assert all(xor_selected(columns, v) == v for v in columns)
    characteristic = xor_selected(columns, (1 << frame.h)-1)
    return basis, columns, characteristic


@lru_cache(maxsize=600000)
def contained(old, new):
    assert old.h == new.h
    if old == new:
        return True
    if old.dimension > new.dimension:
        return False
    return all(new.project(v) == v for v in geometry(old)[0])


@lru_cache(maxsize=600000)
def admissible(old, new):
    if not contained(old, new):
        return False
    return old.dimension == new.dimension or old.characteristic != new.characteristic


def unit(old, new):
    """Generic residual column witness, including the zero-to-frame entry."""
    assert old is None or contained(old, new)
    delta = new.dimension-(old.dimension if old else 0)
    if not delta:
        return 0
    chi = new.characteristic ^ (old.characteristic if old else 0)
    assert chi, 'A nonzero alternating residual is forbidden'
    coordinate = chi & -chi
    value = new.project(coordinate) ^ (old.project(coordinate) if old else 0)
    assert dot(value, value) == 1 and new.project(value) == value
    assert old is None or old.project(value) == 0
    return value


def complement_unit(frame):
    chi = ((1 << frame.h)-1) ^ frame.characteristic
    assert chi, 'A nonzero terminal complement is alternating'
    coordinate = chi & -chi
    value = coordinate ^ frame.project(coordinate)
    assert dot(value, value) == 1 and frame.project(value) == 0
    return value


def reconstruct(circuit):
    """Rebuild exact coefficient maps, unions, cores and frame tags."""
    h = circuit.h
    full = (1 << h)-1
    support, unions, cores = {}, {}, {}
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            assert 1 <= node <= len(circuit.inputs)
            support[node] = 1 << (node-1)
            unions[node] = cores[node] = sum(1 << i for i in circuit.inputs[node-1])
        else:
            a, b = circuit.args[node]
            assert a < node and b < node and not support[a] & support[b]
            support[node] = support[a] | support[b]
            unions[node] = unions[a] | unions[b]
            cores[node] = cores[a] & cores[b]
        assert support[node] == circuit.support[node]
        assert unions[node] == circuit.union[node] and cores[node] == circuit.core[node]
    special = {}
    for (kind, target), node in circuit.outputs.items():
        if kind == 'E':
            value = sum(1 << i for i in target)
            assert special.setdefault(node, value) == value
            children = [j for j in circuit.args[node] if cores[j].bit_count() < 2]
            assert len(children) == 1 and cores[children[0]].bit_count() == 1
            assert special.setdefault(children[0], value) == value
    intern, frames = {}, {}
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            tag = ('line', unions[node])
        elif node in special:
            tag = ('kernel', special[node])
        elif circuit.family[node] == 'E':
            assert cores[node].bit_count() == 2
            tag = ('pair', cores[node], unions[node] & ~cores[node])
            assert tag[2].bit_count() <= h-3
        else:
            assert circuit.family[node] == 'D' and unions[node].bit_count() <= h-3
            tag = (('coordinate', unions[node]) if unions[node].bit_count() <= h-4
                   else ('kernel', full ^ unions[node]))
        assert circuit.frame(node) == tag
        frames[node] = intern.setdefault(tag, GramFrame(h, tag))
        assert frames[node].characteristic
        unit(None, frames[node])
        complement_unit(frames[node])
        if circuit.args[node]:
            for child in circuit.args[node]:
                assert admissible(frames[child], frames[node])
                unit(frames[child], frames[node])
    stripes = [0]*h
    for i, target in enumerate(circuit.inputs):
        for j in target:
            stripes[j] |= 1 << i
    coefficient_count = 0
    all_inputs = (1 << len(circuit.inputs))-1
    for (kind, target), node in circuit.outputs.items():
        if kind == 'D':
            expected = all_inputs
            for j in target:
                expected &= ~stripes[j]
        else:
            expected = 0
            for a, b in combinations(target, 2):
                c = next(j for j in target if j not in (a, b))
                expected |= stripes[a] & stripes[b] & ~stripes[c]
        assert support[node] == expected
        assert frames[node].tag == ('kernel', sum(1 << j for j in target))
        coefficient_count += expected.bit_count()
    return frames, support, dict(logical_frames=len(frames), unique_gram_frames=len(intern),
        independently_constructed_projector_columns=h*len(intern),
        exact_output_nonzero_coefficients=coefficient_count,
        all_original_edges_and_terminal_complements_nonalternating=True)


def physical(circuit, frames, support, code):
    values = [0]*code['roles']
    current = [None]*code['roles']
    history = []
    transitions = Counter()
    unique = set()
    additions = copies = swaps = 0
    for node, inputs, outputs in code['gates']:
        assert len(set(inputs)) == len(inputs) and set(inputs) & set(outputs) == {inputs[0]}
        frame = frames[node]
        before = {}
        for role in set(inputs+outputs):
            previous = current[role]
            before[role] = previous
            assert previous is None or admissible(previous, frame)
            unit(previous, frame)
            transitions[frame.dimension-(previous.dimension if previous else 0)] += 1
            unique.add((previous, frame))
            current[role] = frame
        history.append(before)
        if circuit.args[node] is None:
            assert len(inputs) == 1 and not values[inputs[0]]
            values[inputs[0]] = support[node]
        else:
            a, b = circuit.args[node]
            actual = values[inputs[0]], values[inputs[1]]
            expected = support[a], support[b]
            assert actual == expected or actual == expected[::-1]
            swaps += int(actual == expected[::-1])
            assert not actual[0] & actual[1]
            values[inputs[0]] = actual[0] | actual[1]
            additions += 1
        assert values[inputs[0]] == support[node]
        for role in outputs[1:]:
            assert values[role] == 0, 'Physical copy target is not fresh'
            values[role] = values[inputs[0]]
            copies += 1
    assert all(frame is not None for frame in current)
    for frame in set(current):
        complement_unit(frame)
    for target, role in code['outputs'].items():
        assert values[role] == support[circuit.outputs[target]]
        assert current[role] == frames[circuit.outputs[target]]
    # Reverse the full timeline, starting from every terminal scratch frame,
    # not only the designated outputs. Complement residuals use the same P.
    reverse = list(current)
    for (node, inputs, outputs), before in zip(reversed(code['gates']), reversed(history)):
        for role in set(inputs+outputs):
            assert reverse[role] == frames[node]
            previous = before[role]
            unit(previous, reverse[role])
            reverse[role] = previous
    assert not any(reverse)
    for target, role in code['sources'].items():
        node = circuit.variables[target]
        assert frames[node].tag == ('line', sum(1 << i for i in target))
    digest = sha256(json.dumps(dict(roles=code['roles'], gates=code['gates'],
        sources=sorted(code['sources'].items()), outputs=sorted(code['outputs'].items())),
        separators=(',', ':')).encode()).hexdigest()
    return dict(physical_additions=additions, fresh_physical_copies=copies,
        swapped_result_pivots=swaps, designated_outputs=len(code['outputs']),
        all_scalar_coefficients_exact_without_modular_cancellation=True,
        forward_transitions=sum(transitions.values()), reverse_transitions=sum(transitions.values()),
        unique_physical_transitions=len(unique), forward_histogram=dict(sorted(transitions.items())),
        all_nonzero_forward_reverse_residuals_have_norm_one_witness=True,
        all_copy_outputs_source_lines_and_target_kernels_valid=True, compiled_sha256=digest)


def chain_check(frames, plan):
    _, descriptions, successor, predecessor, summary = plan
    retained = Counter()
    for first, second in successor.items():
        value, parent, _ = descriptions[first]
        value2, following, _ = descriptions[second]
        assert value == value2 and first < second and parent is not None
        assert predecessor[second] == first
        retained[parent] += 1
        assert retained[parent] <= 1
        new = frames[following if following is not None else value]
        assert admissible(frames[parent], new)
        unit(frames[parent], new)
    return dict(selected_links=len(successor), candidate_links=summary['candidate_links'],
                retained_at_most_one_argument_per_gate=True, all_chain_edges_exact=True)


def residual_controls():
    # A proper nested, nondegenerate residual may be alternating. Both
    # frames below are valid members of the even-ground family.
    old = GramFrame(10, ('pair', 3, 124))
    new = GramFrame(10, ('kernel', 896))
    A, B = geometry(old)[0], geometry(new)[0]
    E = residual(A, B)
    assert contained(old, new) and len(E) == rank(gram(E)) == 4
    assert all(dot(v, v) == 0 for v in E)
    assert old.characteristic == new.characteristic == 127
    assert not admissible(old, new)
    # Distinct tags can denote the same subspace: zero residual is allowed.
    line = GramFrame(10, ('line', 7))
    pair = GramFrame(10, ('pair', 3, 4))
    assert contained(line, pair) and contained(pair, line)
    assert line.characteristic == pair.characteristic and admissible(line, pair)
    return dict(rejected_alternating_residual_dimension=4, zero_residual_different_tags_allowed=True)


def dense_residual_sample(frames, plan, seed):
    rng = random.Random(seed)
    unique = list(set(frames.values()))
    _, descriptions, successor, _, _ = plan
    pairs = set()
    for first, second in successor.items():
        value, parent, _ = descriptions[first]
        _, following, _ = descriptions[second]
        pairs.add((frames[parent], frames[following if following is not None else value]))
    if len(pairs) > 128:
        pairs = set(rng.sample(sorted(pairs, key=lambda x: (x[0].tag, x[1].tag)), 128))
    pairs.update((rng.choice(unique), rng.choice(unique)) for _ in range(128))
    accepted = 0
    for old, new in pairs:
        A, B = geometry(old)[0], geometry(new)[0]
        actual = rank(A+B) == len(B)
        assert contained(old, new) == actual
        if not actual:
            assert not admissible(old, new)
            continue
        E = residual(A, B)
        assert len(E) == new.dimension-old.dimension == rank(gram(E))
        reverse = residual(complement(B, new.h), complement(A, old.h))
        assert len(reverse) == len(E) == rank(tuple(E)+tuple(reverse))
        nonalternating = not E or any(dot(v, v) for v in E)
        assert admissible(old, new) == nonalternating
        accepted += 1
    return dict(seed=seed, exact_elimination_pairs=len(pairs), nested_pairs=accepted,
                reverse_complement_residual_spaces_identical=True)


def own_mix(bank, code, backwards=False):
    for _, inputs, outputs in reversed(code['gates']) if backwards else code['gates']:
        if backwards:
            for role in outputs[1:]:
                bank[role] -= bank[inputs[0]]
            for role in inputs[1:]:
                bank[inputs[0]] -= bank[role]
        else:
            for role in inputs[1:]:
                bank[inputs[0]] += bank[role]
            for role in outputs[1:]:
                bank[role] += bank[inputs[0]]


def own_invoke(circuit, code, x, y, bank, backwards=False):
    R, h = code['roles'], circuit.h
    actions = [('mix', 1), ('inject', -1), ('mix', -1), ('scatter', -1),
               ('copy', 1), ('gather', 1), ('scatter', 1), ('mix', 1),
               ('inject', 1), ('mix', -1), ('gather', -1), ('copy', -1)]
    if backwards:
        actions = [(kind, -sign) for kind, sign in reversed(actions)]
    for kind, sign in actions:
        if kind == 'mix':
            own_mix(bank, code, sign < 0)
            continue
        for i, triple in enumerate(circuit.inputs):
            if kind == 'copy':
                bank[code['sources'][triple]] += sign*x[i]
            elif kind == 'gather':
                for j in triple:
                    bank[R+j] += sign*x[i]
                bank[R+h] += sign*x[i]
            else:
                value = (bank[code['outputs']['D', triple]]-bank[code['outputs']['E', triple]]
                         if kind == 'inject' else sum(bank[R+j] for j in triple)-bank[R+h])
                assert value % 2 == 0
                y[i] += sign*(value//2)


def matching(circuit):
    h = circuit.h
    index = {t: i for i, t in enumerate(circuit.inputs)}
    pi = [index[tuple(sorted(i ^ 1 for i in t))] for t in circuit.inputs]
    assert sorted(pi) == list(range(len(pi))) and all(pi[pi[i]] == i for i in range(len(pi)))
    counts = Counter()
    for i, j in enumerate(pi):
        a, b = circuit.inputs[i], circuit.inputs[j]
        intersection = len(set(a) & set(b))
        assert intersection in (0, 2)
        counts[intersection] += 1
        coordinate = next(k for k in range(h) if k not in set(a) | set(b))
        assert dot(1 << coordinate, sum(1 << k for k in a)) == 0
        assert dot(1 << coordinate, sum(1 << k for k in b)) == 0
    v = len(pi)
    if h <= 8:
        pairs = {(b, pi[a]) for a in range(v) for b in range(v)}
        assert len(pairs) == v*v
    return pi, dict(triples=v, intersection_histogram=dict(sorted(counts.items())),
        exact_orthogonal_involution=True, all_join_residuals_have_coordinate_norm_one_witness=True,
        invocation_matching='(A,B) -> (B,pi(A))', dim_E=h, dim_H=h**3-h,
        joined_residual_dimension=h**3-2*h, rank_saved_per_joined_role=h**3)


def shared_exchange(circuit, code, pi, seed):
    v, R, h = len(pi), code['roles'], circuit.h
    n, size = v**3, R+h+1
    pool = tuple(range(-38, 40, 2))
    payload = lambda i: pool[(i*19+seed*11) % len(pool)]
    x = [payload(i) for i in range(n)]
    y = [payload(n+i) for i in range(n)]
    original_x, original_y = x[:], y[:]
    shared = [[payload(2*n+row*size+j) for j in range(size)] for row in range(v*v)]
    middle = [[payload(2*n+v*v*size+row*size+j) for j in range(size)] for row in range(v*v)]
    invocations = 0
    for stage in range(3):
        for a in range(v):
            for b in range(v):
                if stage == 0:
                    indices = [i*v*v+a*v+b for i in range(v)]
                    bank = shared[a*v+b]
                elif stage == 1:
                    indices = [a*v*v+i*v+b for i in range(v)]
                    bank = middle[a*v+b]
                else:
                    indices = [a*v*v+b*v+i for i in range(v)]
                    bank = shared[pi[b]*v+a]
                source = y if stage == 1 else x
                target = x if stage == 1 else y
                local_x, local_y = [source[i] for i in indices], [target[i] for i in indices]
                own_invoke(circuit, code, local_x, local_y, bank, stage == 1)
                for i, value in zip(indices, local_y):
                    target[i] = value
                invocations += 1
    assert x == [-value for value in original_y] and y == original_x
    for row, bank in enumerate(shared):
        assert all(value == payload(2*n+row*size+j) for j, value in enumerate(bank))
    for row, bank in enumerate(middle):
        assert all(value == payload(2*n+v*v*size+row*size+j) for j, value in enumerate(bank))
    return dict(seed=seed, invocations=invocations, data_coordinates_per_bank=n,
        dirty_auxiliary_coordinates=2*v*v*size, all_dirty_banks_restored_exactly=True,
        all_data_outputs_exact=True, middle_chronology_reversed_and_inverted=True,
        scalar_implementation='Independent literal integer mixer/injection/gather/scatter schedule')


def counts_guard(circuit, code, saved):
    h, v, R = circuit.h, len(circuit.inputs), code['roles']
    m, N = h**3, v**3
    W, L = 2*N+2*v*v*(R+h+1), 3*v*v*(h+1)*h
    D = 2*N-2*L
    s = W*m-D
    counts = dict(h=h, v=v, m=m, N=N, R=R, W=W, L=L, D=D, s=s, eta=Q(D, W*m))
    assert all(Q(saved['shared_complex_counts'][key]) == value for key, value in counts.items())
    G = 3*v*v*(4*(circuit.additions+v)+4*v+4)
    E = 64*(W+m+1)**3
    depth = 2*G*W*W+4*s+4*W+4
    assert 0 < depth < E
    old_condition = G < 6*W
    assert saved['guard']['old_six_W_condition'] == old_condition
    expected = dict(actual_grouped_scalar_gates=G, additive_E=E,
                    exact_saved_input_operation_depth_bound=depth, guard_B=s+E,
                    operation_depth_slack=E-depth)
    assert all(int(saved['guard'][key]) == value for key, value in expected.items())
    saving = None
    if D > 0:
        assert 2 <= s < m**5
        lo, hi = independent_saving(counts['eta'], m)
        enclosure = saved['saving_enclosure']
        assert Q(enclosure['saving_lower']) < lo < hi < Q(enclosure['saving_upper'])
        chosen = Q((lo.numerator*10**11-1)//lo.denominator, 10**11)
        assert 0 < chosen < lo and Q(enclosure['chosen_saving']) < lo
        saving = dict(lower=lo, upper=hi, simple_strict_saving=chosen,
                      longer_logarithm_enclosures=True)
    return counts, dict(**expected, old_six_W_condition=old_condition,
                        exact_grouped_gate_bound_used=True,
                        semantic_C0=32*m*(s+E)**2, semantic_C1=1), saving


def case(saved, exchange, seed):
    started = time.monotonic()
    circuit = TripleSideCircuit(saved['h'])
    frames, supports, logical = reconstruct(circuit)
    marks = {'logical_and_gram_seconds': time.monotonic()-started}
    print('PASS reconstructed generic binary Gram projectors h', circuit.h, flush=True)
    at = time.monotonic()
    with patch.object(frame_reuse, 'included', admissible):
        plan = frame_reuse.optimize_chains(circuit, frames, 'rank')
        code = frame_reuse.compile_reuse(circuit, frames, plan)
    marks['independent_predicate_flow_compile_seconds'] = time.monotonic()-at
    assert code['roles'] == saved['compiled_roles']
    assert len(plan[2]) == saved['roles_saved']
    chain = chain_check(frames, plan)
    replay = physical(circuit, frames, supports, code)
    assert replay['compiled_sha256'] == saved['checked']['compiled_sha256']
    assert replay['forward_histogram'] == {int(k): v for k, v in saved['phase']['physical_forward_transition_histogram'].items()}
    assert logical['unique_gram_frames'] == saved['new_frames']['unique_binary_frames']
    elimination = dense_residual_sample(frames, plan, seed)
    pi, joins = matching(circuit)
    dirty = complete_scalar_matrix(circuit, code) if circuit.h == 8 else None
    shared = shared_exchange(circuit, code, pi, seed) if exchange and circuit.h == 8 else None
    counts, guard, saving = counts_guard(circuit, code, saved)
    return dict(h=circuit.h, logical=logical, physical=replay, chains=chain,
        independent_elimination=elimination, matching=joins, complete_dirty_basis=dirty,
        complete_shared_exchange=shared, counts=counts, guard=guard, saving=saving,
        phase_times=marks, wall_seconds=time.monotonic()-started,
        status='Independent finite binary frame, scalar, sharing and guard transfer PASS')


def stringify(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificates', type=Path, nargs='+', required=True)
    ap.add_argument('--h', type=int, nargs='+', default=[8, 28])
    ap.add_argument('--exchange-h8', action='store_true')
    ap.add_argument('--seed', type=int, default=619)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh result path'
    saved = {}
    inputs = {}
    for path in args.certificates:
        raw = path.read_bytes()
        inputs[str(path)] = sha256(raw).hexdigest()
        document = json.loads(raw)
        assert document['source_sha256'] == '9af6ff67d27549c01d2448c9792ed444e633c8336f28a4d67e15cd3c81d9522a'
        for row in document['rows']:
            saved[row['h']] = row
    result = dict(started_utc=datetime.now(timezone.utc).isoformat(),
        campaign_start='2026-10-07T22:25:21Z', historical_deadline='2026-10-08T08:25:21Z',
        active_deadline='2026-10-08T10:00:00Z', inputs=inputs,
        independent_source_sha256={name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('review_complex_controller.py', 'review_complex_frames.py',
                         'frame_reuse.py', 'downstream_complex_circuit.py',
                         'review_asymmetric_motif.py', 'review_parameter_audit.py')},
        targeted_boundary_controls=residual_controls(), rows=[])
    for h in args.h:
        print('Starting independent complex controller review h', h, flush=True)
        result['rows'].append(case(saved[h], args.exchange_h8, args.seed))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(stringify(result), indent=2, sort_keys=True)+'\n')
        print('PASS independent complex controller review h', h, 'R', result['rows'][-1]['counts']['R'], flush=True)
    result['status'] = 'Terminal independent complex controller finite/transfer PASS'
    args.output.write_text(json.dumps(stringify(result), indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
