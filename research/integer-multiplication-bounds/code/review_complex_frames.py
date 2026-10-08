#!/usr/bin/env python3
"""Independent binary frame and dirty scalar audit of complex side circuits.

Uses explicit GF(2) elimination for small residuals, reconstructs source
supports and the label families without calling the producer frame checker,
and expands both complete local shear matrices over Gaussian dyadics.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time


def mask(t):
    return sum(1 << i for i in t)


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length()-1
            if p not in pivots:
                pivots[p] = value
                break
            value ^= pivots[p]
    return len(pivots)


def dot(a, b):
    return (a & b).bit_count() & 1


def nullspace(rows, dimension):
    rows = [x for x in rows if x]
    pivots = []
    done = 0
    for col in range(dimension):
        pivot = next((i for i in range(done, len(rows)) if rows[i] >> col & 1), None)
        if pivot is None:
            continue
        rows[done], rows[pivot] = rows[pivot], rows[done]
        for i in range(len(rows)):
            if i != done and rows[i] >> col & 1:
                rows[i] ^= rows[done]
        pivots.append(col)
        done += 1
    answer = []
    for free in set(range(dimension))-set(pivots):
        v = 1 << free
        for i, pivot in enumerate(pivots):
            if rows[i] >> free & 1:
                v |= 1 << pivot
        assert all(dot(v, row) == 0 for row in rows)
        answer.append(v)
    return answer


def coordinates(bits, h):
    return [1 << i for i in range(h) if bits >> i & 1]


def space(frame, h):
    kind = frame[0]
    if kind == 'line':
        return [frame[1]]
    if kind == 'coordinate':
        return coordinates(frame[1], h)
    if kind == 'pair':
        return [frame[1] | bit for bit in coordinates(frame[2], h)]
    assert kind == 'kernel'
    target = frame[1]
    p = target & -target
    return coordinates(((1 << h)-1)^target, h)+[p | b for b in coordinates(target^p, h)]


def gram(rows):
    return [sum(dot(a, b) << j for j, b in enumerate(rows)) for a in rows]


def complement(rows, h):
    return nullspace(rows, h)


def residual(child, parent):
    coefficients = nullspace([sum(dot(u, v) << j for j, v in enumerate(parent))
                              for u in child], len(parent))
    out = []
    for coefficient in coefficients:
        v = 0
        for j, row in enumerate(parent):
            if coefficient >> j & 1:
                v ^= row
        out.append(v)
    assert all(dot(u, v) == 0 for u in child for v in out)
    return out


def dimension(frame, h):
    return (1 if frame[0] == 'line' else h-1 if frame[0] == 'kernel'
            else frame[-1].bit_count())


def analytic_edge(old, new, h):
    """Independent family containment and explicit nonalternating residual."""
    dim = dimension(new, h)-dimension(old, h)
    assert dim >= 0
    if old == new:
        return 0
    full = (1 << h)-1
    if new[0] == 'coordinate':
        assert old[0] in ('line', 'coordinate') and not old[1] & ~new[1]
        available = new[1] & ~old[1]
        assert available
        unit = available & -available
    elif new[0] == 'pair':
        P, J = new[1:]
        if old[0] == 'line':
            assert old[1] & P == P and (old[1] & ~P).bit_count() == 1
            oldJ = old[1] & ~P
        else:
            assert old[0] == 'pair' and old[1] == P
            oldJ = old[2]
        assert not oldJ & ~J
        available = J & ~oldJ
        assert available
        unit = P | (available & -available)
    else:
        assert new[0] == 'kernel'
        T = new[1]
        outside = full^T
        if old[0] == 'line':
            assert dot(T, old[1]) == 0
            available = outside & ~old[1]
            assert available
            unit = available & -available
        elif old[0] == 'coordinate':
            assert not old[1] & T
            available = outside & ~old[1]
            assert available
            unit = available & -available
        else:
            assert old[0] == 'pair' and old[1] & T == old[1] and not old[2] & T
            available = outside & ~old[2]
            unit = (available & -available) if available else (old[1] & -old[1]) | (T & ~old[1]) | outside
        assert dot(unit, T) == 0
    assert dim > 0 and dot(unit, unit) == 1
    assert all(dot(unit, row) == 0 for row in space(old, h))
    if new[0] == 'coordinate':
        assert not unit & ~new[1]
    elif new[0] == 'pair':
        assert unit & new[1] == new[1] and not (unit & ~new[1]) & ~new[2]
    return dim


def independent_frames(circuit, dense):
    h = circuit.h
    full = (1 << h)-1
    union = [0]*len(circuit.args)
    core = [0]*len(circuit.args)
    frames = {}
    special = {}
    for (kind, target), node in circuit.outputs.items():
        if kind != 'E':
            continue
        previous = special.setdefault(node, target)
        assert previous == target
        first = [x for x in circuit.args[node] if circuit.core[x].bit_count() < 2]
        assert len(first) == 1 and circuit.core[first[0]].bit_count() == 1
        previous = special.setdefault(first[0], target)
        assert previous == target
    checks = 0
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            t = mask(circuit.inputs[node-1])
            assert circuit.support[node] == 1 << (node-1)
            union[node] = core[node] = t
            frame = ('line', t)
        else:
            a, b = circuit.args[node]
            assert a < node and b < node and not circuit.support[a] & circuit.support[b]
            assert circuit.support[node] == circuit.support[a] | circuit.support[b]
            union[node], core[node] = union[a] | union[b], core[a] & core[b]
            if node in special:
                frame = ('kernel', mask(special[node]))
            elif circuit.family[node] == 'E':
                assert core[node].bit_count() == 2
                frame = ('pair', core[node], union[node] & ~core[node])
                assert frame[2].bit_count() <= h-3
            else:
                assert circuit.family[node] == 'D' and union[node].bit_count() <= h-3
                frame = (('coordinate', union[node]) if union[node].bit_count() <= h-4
                         else ('kernel', full^union[node]))
        assert union[node] == circuit.union[node] and core[node] == circuit.core[node]
        assert circuit.frame(node) == frame
        frames[node] = frame
        checks += 1
    stripe = [0]*h
    for j, target in enumerate(circuit.inputs):
        for i in target:
            stripe[i] |= 1 << j
    all_inputs = (1 << len(circuit.inputs))-1
    coefficients = 0
    for (kind, target), node in circuit.outputs.items():
        t = mask(target)
        assert frames[node] == ('kernel', t)
        if kind == 'D':
            expected = all_inputs
            for i in target:
                expected &= ~stripe[i]
        else:
            expected = 0
            for a, b in combinations(target, 2):
                c = next(i for i in target if i not in (a, b))
                expected |= stripe[a] & stripe[b] & ~stripe[c]
        assert circuit.support[node] == expected
        coefficients += expected.bit_count()
    unique = set(frames.values())
    unique_edges = set()
    for node in sorted(circuit.active):
        if circuit.args[node]:
            unique_edges.update((frames[x], frames[node]) for x in circuit.args[node])
    matrix_checks = 0
    complement_witnesses = 0
    for frame in unique:
        if frame[0] == 'kernel':
            unit = frame[1]
        else:
            support = frame[1] if frame[0] != 'pair' else frame[1] | frame[2]
            available = full & ~support
            assert available
            unit = available & -available
        assert dot(unit, unit) and all(dot(unit, row) == 0 for row in space(frame, h))
        complement_witnesses += 1
    nonzero = sum(analytic_edge(old, new, h) > 0 for old, new in unique_edges)
    if dense:
        for frame in unique:
            rows = space(frame, h)
            assert rank(rows) == rank(gram(rows)) == len(rows)
            assert any(dot(v, v) for v in rows)
            perp = complement(rows, h)
            assert rank(gram(perp)) == len(perp)
            assert not perp or any(dot(v, v) for v in perp)
            matrix_checks += 1
        for old, new in unique_edges:
            U, V = space(old, h), space(new, h)
            assert rank(U+V) == len(V)
            R = residual(U, V)
            assert len(R) == len(V)-len(U) == rank(gram(R))
            assert not R or any(dot(v, v) for v in R)
            reverse = residual(complement(V, h), complement(U, h))
            assert rank(R+reverse) == len(R) == len(reverse)
            matrix_checks += 1
    # Independent full physical timeline; no producer frame_edge calls.
    code = circuit.compile()
    physical = [None]*code['roles']
    for triple, slot in code['sources'].items():
        physical[slot] = frames[circuit.variables[triple]]
    transitions = 0
    for node, ins, outs in code['gates']:
        current = frames[node]
        for slot in set(ins+outs):
            if physical[slot] is not None:
                assert (physical[slot], current) in unique_edges or physical[slot] == current
            physical[slot] = current
            transitions += 1
    for target, slot in code['outputs'].items():
        assert physical[slot] == frames[circuit.outputs[target]]
    reverse = [None]*code['roles']
    for target, slot in code['outputs'].items():
        reverse[slot] = frames[circuit.outputs[target]]
    for node, ins, outs in reversed(code['gates']):
        current = frames[node]
        for slot in set(ins+outs):
            if reverse[slot] is not None:
                assert (current, reverse[slot]) in unique_edges or reverse[slot] == current
            reverse[slot] = current
            transitions += 1
    for triple, slot in code['sources'].items():
        assert reverse[slot] == frames[circuit.variables[triple]]
    return frames, code, dict(independent_logical_frames=checks,
                             exact_output_nonzero_coefficients=coefficients,
                             unique_frames=len(unique), unique_frame_edges=len(unique_edges),
                             dense_binary_gram_complement_residual_checks=matrix_checks,
                             analytic_nonzero_residual_witnesses=nonzero,
                             analytic_complement_witnesses=complement_witnesses,
                             forward_and_reverse_physical_transitions=transitions,
                             reverse_complements_isometric=True,
                             source_lines_and_exact_target_kernels=True)


def complete_scalar_matrix(circuit, code):
    v, R, h = len(circuit.inputs), code['roles'], circuit.h
    zstart, cstart = 2*v, 2*v+R
    operations = []
    def mix(inverse=False):
        for _, ins, outs in reversed(code['gates']) if inverse else code['gates']:
            if inverse:
                operations.extend((zstart+j, zstart+ins[0], Q(-1)) for j in outs[1:])
                operations.extend((zstart+ins[0], zstart+j, Q(-1)) for j in ins[1:])
            else:
                operations.extend((zstart+ins[0], zstart+j, Q(1)) for j in ins[1:])
                operations.extend((zstart+j, zstart+ins[0], Q(1)) for j in outs[1:])
    def inject(sign):
        for i, target in enumerate(circuit.inputs):
            operations.append((v+i, zstart+code['outputs']['D', target], Q(sign, 2)))
            operations.append((v+i, zstart+code['outputs']['E', target], Q(-sign, 2)))
    def copy(sign):
        operations.extend((zstart+code['sources'][t], i, Q(sign)) for i, t in enumerate(circuit.inputs))
    def gather(sign):
        for i, t in enumerate(circuit.inputs):
            operations.extend((cstart+j, i, Q(sign)) for j in t)
            operations.append((cstart+h, i, Q(sign)))
    def scatter(sign):
        for i, t in enumerate(circuit.inputs):
            operations.extend((v+i, cstart+j, Q(sign, 2)) for j in t)
            operations.append((v+i, cstart+h, Q(-sign, 2)))
    mix(); inject(-1); mix(True); scatter(-1); copy(1); gather(1)
    scatter(1); mix(); inject(1); mix(True); gather(-1); copy(-1)
    dimension = 2*v+R+h+1
    def execute(inverse=False):
        values = [{i: Q(1)} for i in range(dimension)]
        ops = ((a, b, -c) for a, b, c in reversed(operations)) if inverse else operations
        for a, b, c in ops:
            assert a != b
            destination = values[a]
            for coordinate, value in values[b].items():
                result = destination.get(coordinate, Q(0))+c*value
                if result:
                    destination[coordinate] = result
                else:
                    destination.pop(coordinate, None)
        for i, row in enumerate(values):
            expected = {i: Q(1)}
            if v <= i < 2*v:
                expected[i-v] = Q(-1 if inverse else 1)
            assert row == expected, (i, inverse)
    execute(); execute(True)
    return dict(complete_basis_dimension=dimension, elementary_operations=len(operations),
                includes_both_data_banks_all_side_and_central_scratch=True,
                forward_identity_shear_and_inverse_exact=True,
                field='fractions.Fraction, Gaussian dyadic coefficients')


def even_matching(h):
    triples = list(combinations(range(h), 3))
    images = [tuple(sorted(i ^ 1 for i in t)) for t in triples]
    assert len(set(images)) == len(triples)
    counts = {0: 0, 2: 0}
    for t, u in zip(triples, images):
        k = len(set(t) & set(u))
        assert k in counts
        counts[k] += 1
        middle_unit = next(i for i in range(h) if i not in set(t)|set(u))
        assert middle_unit not in t and middle_unit not in u
    return dict(images=len(images), intersection_histogram=counts,
                involutive_binary_orthogonal_matching=True,
                every_join_has_middle_coordinate_norm_one_witness=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h', nargs='+', type=int, default=[8, 10, 12])
    ap.add_argument('--dense-max', type=int, default=12)
    ap.add_argument('--scalar-max', type=int, default=8)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    sys.dont_write_bytecode = True
    from downstream_complex_circuit import TripleSideCircuit
    started = time.monotonic()
    rows = []
    for h in args.h:
        begin = time.monotonic()
        c = TripleSideCircuit(h)
        frames, code, check = independent_frames(c, h <= args.dense_max)
        scalar = complete_scalar_matrix(c, code) if h <= args.scalar_max else None
        rows.append(dict(h=h, roles=code['roles'], frames=check, complete_dirty_matrix=scalar,
                         even_stage_matching=even_matching(h), wall_seconds=time.monotonic()-begin))
        print('PASS independent complex frames', h, 'roles', code['roles'], flush=True)
    result = dict(rows=rows, wall_seconds=time.monotonic()-started,
                  source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                 for name in ('review_complex_frames.py', 'downstream_complex_circuit.py')},
                  scope='Finite independent binary Gram/residual/complement and complete dirty local scalar matrices; all-size tensor/phase/guard transfer separately reviewed')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
