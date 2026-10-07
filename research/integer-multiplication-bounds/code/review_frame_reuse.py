#!/usr/bin/env python3
"""Independent rational-span and dirty-register review of controller reuse."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys
import time

from review_rational_frames import basis, analyze


def vector(bits, h):
    return [Q((bits >> i) & 1) for i in range(h)]


def rank(rows):
    return len(basis(rows))


def contains(a, b, h):
    """a subset b, by rational elimination independent of graph tags."""
    rows = [vector(x, h) for x in b.basis]
    return rank(rows+[vector(x, h) for x in a.basis]) == rank(rows)


def span_census(h=5, random_h=6, samples=500, inclusion_samples=10000):
    from frame_reuse import space_of, included
    rng = random.Random(109)
    spaces = set()
    checks = 0
    for size, exhaustive in [(h, True), (random_h, False)]:
        local = set()
        for common in range(size):
            triples = [(1 << common) | (1 << a) | (1 << b)
                       for a, b in combinations([i for i in range(size) if i != common], 2)]
            masks = range(1, 1 << len(triples)) if exhaustive else [rng.randrange(1, 1 << len(triples)) for _ in range(samples)]
            for mask in masks:
                selected = [x for i, x in enumerate(triples) if (mask >> i) & 1]
                actual = [vector(x, size) for x in selected]
                frame = space_of(selected, common, size)
                canonical = [vector(x, size) for x in frame.basis]
                assert rank(actual) == rank(canonical) == frame.dimension
                assert rank(actual+canonical) == frame.dimension
                assert analyze(canonical)['nondegenerate']
                local.add(frame)
                checks += 1
        all_spaces = sorted(local, key=lambda z: (z.common, z.tags))
        pairs = ((a, b) for a in all_spaces for b in all_spaces) if exhaustive else (
            (rng.choice(all_spaces), rng.choice(all_spaces)) for _ in range(inclusion_samples))
        pair_count = 0
        for a, b in pairs:
            assert included(a, b) == contains(a, b, size)
            pair_count += 1
        spaces.add((size, len(local), pair_count))
    return dict(span_equivalence_checks=checks,
                ground_sizes=[dict(h=h, distinct_spans=n, rational_inclusion_checks=c)
                              for h, n, c in sorted(spaces)], seed=109,
                evidence='Fraction elimination and Gram ranks, independent of signless-graph tags')


def dirty_check(circuit, frames, compiled):
    h = circuit.h
    inputs = list(circuit.inputs)
    index = {x: i for i, x in enumerate(inputs)}
    n, roles = len(inputs), compiled['roles']
    elementary = []
    mixer = []
    for _, ins, outs in compiled['gates']:
        assert len(ins) in (1, 2) and outs[0] == ins[0]
        if len(ins) == 2:
            mixer.append((ins[0], ins[1]))
        mixer.extend((other, ins[0]) for other in outs[1:])
    # Bank layout: logical x, logical y, arbitrary dirty compiled scratch.
    def add_mixer(reverse=False):
        elementary.extend((2*n+a, 2*n+b) for a, b in (reversed(mixer) if reverse else mixer))
    def add_J():
        for (_, target), slot in compiled['outputs'].items():
            elementary.append((n+index[target], 2*n+slot))
    def add_V():
        for source, slot in compiled['sources'].items():
            elementary.append((2*n+slot, index[source]))
    add_mixer(); add_J(); add_mixer(True); add_V()
    add_mixer(); add_J(); add_mixer(True); add_V()
    initial = [1 << i for i in range(2*n+roles)]
    values = initial[:]
    for target, source in elementary:
        assert target != source
        values[target] ^= values[source]
    assert values[:n] == initial[:n]
    assert values[2*n:] == initial[2*n:]
    for i, target in enumerate(inputs):
        expected = initial[n+i]
        for j, source in enumerate(inputs):
            if len(set(source).intersection(target)) == 1:
                expected ^= initial[j]
        assert values[n+i] == expected
    # Transpose every elementary operation and reverse chronology. The
    # resulting side invocation must realize the opposite bank shear.
    dual = initial[:]
    for target, source in reversed(elementary):
        dual[source] ^= dual[target]
    assert dual[n:2*n] == initial[n:2*n]
    assert dual[2*n:] == initial[2*n:]
    for i, target in enumerate(inputs):
        expected = initial[i]
        for j, source in enumerate(inputs):
            if len(set(source).intersection(target)) == 1:
                expected ^= initial[n+j]
        assert dual[i] == expected
    # Check rational inclusions in the actual physical role timeline, using
    # elimination rather than the compiler's symbolic containment routine.
    labels = [None]*roles
    for source, slot in compiled['sources'].items():
        labels[slot] = frames[circuit.variables[source]]
    frame_checks = 0
    for node, ins, outs in compiled['gates']:
        current = frames[node]
        assert analyze([vector(x, h) for x in current.basis])['nondegenerate']
        for slot in set(ins+outs):
            assert labels[slot] is None or contains(labels[slot], current, h)
            labels[slot] = current
            frame_checks += 1
    for target, slot in compiled['outputs'].items():
        assert contains(labels[slot], frames[circuit.outputs[target]], h)
    reverse = [None]*roles
    for target, slot in compiled['outputs'].items():
        reverse[slot] = frames[circuit.outputs[target]]
    for node, ins, outs in reversed(compiled['gates']):
        current = frames[node]
        for slot in set(ins+outs):
            assert reverse[slot] is None or contains(current, reverse[slot], h)
            reverse[slot] = current
            frame_checks += 1
    for source, slot in compiled['sources'].items():
        expected = frames[circuit.variables[source]]
        assert contains(reverse[slot], expected, h) and contains(expected, reverse[slot], h)
    return dict(h=h, inputs=n, roles=roles, elementary_operations=len(elementary),
                dirty_basis_count=2*n+roles, arbitrary_dirty_restoration=True,
                full_neighbor_shear=True, transposed_reverse_neighbor_shear=True,
                exact_physical_frame_inclusions=frame_checks,
                output_digest=sha256(json.dumps(values).encode()).hexdigest())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--h', type=int, default=6)
    ap.add_argument('--schedule', choices=['id', 'rank'], default='rank')
    ap.add_argument('--skip-census', action='store_true')
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.reference/'scripts'))
    from paired_exclusion_circuit import PairedExclusionCircuit
    from finite_block_search import GroupUnion
    from frame_reuse import labels, optimize_chains, compile_reuse
    begin = time.monotonic()
    census = {} if args.skip_census else span_census()
    graph = GroupUnion(args.h, PairedExclusionCircuit, ordering='paired')
    frames, _ = labels(graph, global_graph=True)
    code = compile_reuse(graph, frames, optimize_chains(graph, frames, args.schedule))
    result = dict(census=census, dirty_check=dirty_check(graph, frames, code),
                  chain_summary=code['chain_summary'], wall_seconds=time.monotonic()-begin,
                  scope='Independent exact finite rational and scalar checks; endpoint lifting and asymptotic transfer remain conditional')
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
