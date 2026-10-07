#!/usr/bin/env python3
"""Independent exact review of positive rational support envelopes.

The envelope basis is derived from its linear equations, independently of
the compiler's signless-graph basis. Scalar dirty-register checks reuse the
independent elementary-operation reviewer. No immutable input is modified.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys
import time

from review_rational_frames import analyze, basis, form
from review_frame_reuse import dirty_check, vector


def masks(bits, h):
    return [i for i in range(h) if bits & (1 << i)]


def constraint_basis(core, support, h):
    """Solve support/equal-core/total-sum constraints explicitly over Q."""
    C, O = masks(core, h), masks(support & ~core, h)
    assert C and len(C) <= 3 and not core & ~support
    first = [Q(i in C) for i in range(h)]
    if not O:
        assert len(C) == 3
        return [first]
    pivot = O[0]
    first[pivot] = Q(3-len(C))
    result = [first]
    for other in O[1:]:
        row = [Q(0)]*h
        row[other], row[pivot] = Q(1), Q(-1)
        result.append(row)
    return result


def rational_inclusion(a, b):
    return len(basis(a+b)) == len(basis(b))


def target_eligible(core, support, target, h):
    C, O = masks(core, h), masks(support & ~core, h)
    m, n = (core & target).bit_count(), ((support & ~core) & target).bit_count()
    if not O:
        return m == 1
    return n in (0, len(O)) and Q(m)+(3-len(C))*Q(n, len(O)) == 1


def census(h=5, random_h=6, samples=500, pair_samples=10000):
    from frame_reuse import space_of, included
    rng = random.Random(109)
    checks, ground, target_checks = 0, [], 0
    for size, exhaustive in [(h, True), (random_h, False)]:
        states = {}
        for common in range(size):
            triples = [(1 << common) | (1 << a) | (1 << b)
                       for a, b in combinations([i for i in range(size) if i != common], 2)]
            selections = range(1, 1 << len(triples)) if exhaustive else [
                rng.randrange(1, 1 << len(triples)) for _ in range(samples)]
            for selection in selections:
                chosen = [t for j, t in enumerate(triples) if selection & (1 << j)]
                core, support = (1 << size)-1, 0
                for triple in chosen:
                    core &= triple
                    support |= triple
                rows = constraint_basis(core, support, size)
                assert all(rational_inclusion([vector(t, size)], rows) for t in chosen)
                result = analyze(rows)
                assert result['nondegenerate'] and result['signature'] == 'positive'
                # Independently reconstruct the compiler's synthetic triple span.
                C, O = masks(core, size), masks(support & ~core, size)
                if len(C) == 3:
                    generators = [core]
                elif len(C) == 2:
                    generators = [core | (1 << i) for i in O]
                else:
                    assert len(O) >= 3
                    edges = [(O[0], O[1]), (O[1], O[2]), (O[0], O[2])]
                    edges += [(O[0], i) for i in O[3:]]
                    generators = [core | (1 << a) | (1 << b) for a, b in edges]
                frame = space_of(generators, C[0], size)
                actual = [vector(t, size) for t in frame.basis]
                assert rational_inclusion(rows, actual) and rational_inclusion(actual, rows)
                assert frame.core == core and frame.vertices == support
                states[core, support] = (rows, frame)
                checks += 1
        items = sorted(states.items())
        pairs = ((a, b) for a in items for b in items) if exhaustive else (
            (rng.choice(items), rng.choice(items)) for _ in range(pair_samples))
        count = 0
        for ((Ca, Va), (a, fa)), ((Cb, Vb), (b, fb)) in pairs:
            combinatorial = not Va & ~Vb and not Cb & ~Ca
            assert rational_inclusion(a, b) == combinatorial == included(fa, fb)
            count += 1
        for (core, support), (rows, _) in items:
            for triple in combinations(range(size), 3):
                mask = sum(1 << i for i in triple)
                exact = all(form(row, vector(mask, size)) == 0 for row in rows)
                assert target_eligible(core, support, mask, size) == exact
                target_checks += 1
        ground.append(dict(h=size, envelopes=len(states), exact_inclusion_checks=count))
    return dict(source_constraint_and_canonical_span_checks=checks,
                ground_sizes=ground, exact_target_eligibility_checks=target_checks,
                seed=109, arithmetic='fractions.Fraction, no modular elimination')


def graph_envelope_check(circuit, frames, compiled, dense=True):
    h = circuit.h
    logical = {}
    checked_rows = set()
    sources = [sum(1 << i for i in t) for t in circuit.inputs]
    checks = 0
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            C = V = sources[node-1]
        else:
            a, b = (logical[child] for child in circuit.args[node])
            C, V = a[0] & b[0], a[1] | b[1]
            assert C
        logical[node] = C, V
        actual = frames[node]
        assert actual.core == C and actual.vertices == V
        expected_dimension = 1 if C == V else (V & ~C).bit_count()
        assert actual.dimension == expected_dimension
        # All source-copy envelopes are exactly the original source line.
        if circuit.args[node] is None:
            assert expected_dimension == 1 and actual.basis == (C,)
        key = C, V
        if dense and key not in checked_rows:
            rows = constraint_basis(C, V, h)
            given = [vector(t, h) for t in actual.basis]
            assert rational_inclusion(rows, given) and rational_inclusion(given, rows)
            assert analyze(rows)['signature'] == 'positive'
            checked_rows.add(key)
        for triple in actual.basis:
            # Synthetic generators have sum three and exactly equal core entries.
            assert triple.bit_count() == 3 and not triple & ~V and triple & C == C
        checks += 1
    for (_, target), node in circuit.outputs.items():
        mask = sum(1 << i for i in target)
        C, V = logical[node]
        assert target_eligible(C, V, mask, h)
    physical = [None]*compiled['roles']
    transitions = 0
    for source, slot in compiled['sources'].items():
        physical[slot] = logical[circuit.variables[source]]
    for node, ins, outs in compiled['gates']:
        C, V = logical[node]
        for slot in set(ins+outs):
            if physical[slot] is not None:
                oldC, oldV = physical[slot]
                assert not oldV & ~V and not C & ~oldC
            physical[slot] = C, V
            transitions += 1
    for target, slot in compiled['outputs'].items():
        assert physical[slot] == logical[circuit.outputs[target]]
    reverse = [None]*compiled['roles']
    for target, slot in compiled['outputs'].items():
        reverse[slot] = logical[circuit.outputs[target]]
    for node, ins, outs in reversed(compiled['gates']):
        C, V = logical[node]
        for slot in set(ins+outs):
            if reverse[slot] is not None:
                nextC, nextV = reverse[slot]
                assert not V & ~nextV and not nextC & ~C
            reverse[slot] = C, V
            transitions += 1
    for source, slot in compiled['sources'].items():
        assert reverse[slot] == logical[circuit.variables[source]]
    return dict(logical_frames=checks, unique_dense_constraint_checks=len(checked_rows),
                physical_frame_transitions=transitions,
                all_input_frames_original_lines=True,
                every_designated_target_orthogonal=True,
                all_output_frames_exact=True,
                forward_and_reverse_complement_nesting=True)


def matching_check(h):
    triples = list(combinations(range(h), 3))
    images = []
    for T in triples:
        groups = [i//2 for i in T]
        if len(set(groups)) == 3:
            first = min(groups)
            image = tuple(sorted(i if i//2 == first else i ^ 1 for i in T))
        else:
            full = next(g for g in groups if groups.count(g) == 2)
            singleton = next(i for i in T if i//2 != full)
            cycle = [g for g in range(h//2) if g != singleton//2]
            chosen = cycle[(cycle.index(full)+1) % len(cycle)]
            image = tuple(sorted((2*chosen, 2*chosen+1, singleton)))
        assert len(set(T) & set(image)) == 1
        images.append(image)
    assert len(set(images)) == len(triples)
    return dict(h=h, images=len(images), distinct=len(set(images)),
                intersection_one=True,
                stage_endpoint_join='unchanged D_i subset D_i-perp at orthogonal matched tensor endpoints')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--h', type=int, default=6)
    ap.add_argument('--skip-census', action='store_true')
    ap.add_argument('--large', action='store_true', help='Symbolic all-frame audit; omit exponential full dirty basis')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.reference/'scripts'))
    from paired_exclusion_circuit import PairedExclusionCircuit
    from finite_block_search import GroupUnion
    from frame_envelope import labels
    from frame_reuse import optimize_chains, compile_reuse
    begin = time.monotonic()
    examples = {} if args.skip_census else census()
    circuit = GroupUnion(args.h, PairedExclusionCircuit, ordering='paired')
    frames, metadata = labels(circuit, global_graph=True)
    compiled = compile_reuse(circuit, frames, optimize_chains(circuit, frames, 'rank'))
    envelope = graph_envelope_check(circuit, frames, compiled, dense=not args.large)
    dirty = {} if args.large else dirty_check(circuit, frames, compiled)
    result = dict(census=examples, envelopes=envelope, dirty=dirty,
                  stages=matching_check(args.h), metadata=metadata,
                  roles=compiled['roles'], chains=compiled['chain_summary'],
                  code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  wall_seconds=time.monotonic()-begin,
                  scope='Exact envelope/controller finite witness; conditional upstream lifting unchanged')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
