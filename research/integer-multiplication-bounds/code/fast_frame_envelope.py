#!/usr/bin/env python3
"""Construct the already accepted E(C,V) frames without generic elimination.

This preserves the exact canonical Space object, including its rational
indicator basis and signed-component tags. It changes frame construction
only; global scalar, inclusion, physical compilation and target verifiers
remain the original implementations. Run this script for a bounded equality
control before assigning this constructor to a new research run.
"""
from __future__ import annotations

import argparse
import gc
from hashlib import sha256
import json
from pathlib import Path
import time

from frame_reuse import Space, included


def envelope(core: int, support: int, h: int) -> Space:
    assert core and not core & ~support and support < 1 << h
    common = (core & -core).bit_length() - 1
    outside = [v for v in range(h) if v != common and support & (1 << v)]
    size = core.bit_count()
    assert 1 <= size <= 3
    tags = [0] * h
    basis = []

    def edge(a, b):
        basis.append((1 << common) | (1 << a) | (1 << b))

    if size == 1:
        # The accepted triangle-plus-star basis is a single odd component.
        assert len(outside) >= 3
        edge(outside[0], outside[1])
        edge(outside[1], outside[2])
        edge(outside[0], outside[2])
        for v in outside[3:]:
            edge(outside[0], v)
        component_first = None
    else:
        if size == 3:
            assert core == support and len(outside) == 2
            center = outside[0]
        else:
            center = ((core ^ (1 << common)) & -(core ^ (1 << common))).bit_length()-1
        leaves = [v for v in outside if v != center]
        assert leaves
        if size == 2:
            assert len(leaves) >= 2, 'A realizable two-point core has at least two distinct source triples'
        component_first = outside[0]
        if center == component_first:
            positive, negative = [center], leaves
        else:
            positive, negative = leaves, [center]
        # This is exactly space_of's canonical bipartite-component basis.
        edge(positive[0], negative[0])
        for v in negative[1:]:
            edge(positive[0], v)
        for v in positive[1:]:
            edge(v, negative[0])

    index = 0
    for v in range(h):
        if v == common:
            continue
        if support & (1 << v):
            if v == component_first:
                index += 1
                for j in positive:
                    tags[j] = index
                for j in negative:
                    tags[j] = -index
        else:
            # Unused coordinates are isolated positive singleton components.
            index += 1
            tags[v] = index
    return Space(common, tuple(tags), tuple(basis), core, support)


def labels(circuit, global_graph=False):
    h = circuit.h if global_graph else circuit.n+1
    triples = [sum(1 << v for v in t) for t in circuit.inputs] if global_graph else [
        (1 << circuit.n) | (1 << a) | (1 << b) for a, b in circuit.inputs]
    supports, cores, frames, recipes, intern = {}, {}, {}, {}, {}
    widened = 0
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            core = support = triples[node-1]
        else:
            a, b = circuit.args[node]
            core, support = cores[a] & cores[b], supports[a] | supports[b]
        cores[node], supports[node] = core, support
        key = (core, support)
        if key not in recipes:
            frame = envelope(core, support, h)
            recipes[key] = intern.setdefault((frame.common, frame.tags), frame)
        frames[node] = recipes[key]
        widened += core.bit_count() == 1
        if circuit.args[node]:
            assert all(included(frames[child], frames[node]) for child in circuit.args[node])
    return frames, dict(unique_envelopes=len(intern), common_one_nodes=widened,
                       frame_family='E(C,V): common coordinates equal z, total sum 3z, support V')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True)
    ap.add_argument('--h', nargs='+', type=int, default=[8, 12])
    ap.add_argument('--positions-json', type=Path)
    ap.add_argument('--physical', action='store_true', help='Run unchanged flow, compilation and physical checks after frame equality')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh output path'
    from finite_block_search import install_reference, GroupUnion
    from finite_singleton_search import singleton_class
    from frame_envelope import labels as original_labels, target_check
    install_reference(args.reference)
    rows = []
    for h in args.h:
        assert h >= 6 and h % 2 == 0
        positions = json.loads(args.positions_json.read_text())['positions'] if args.positions_json else [h//2-2]*h
        assert len(positions) == h
        cls = singleton_class()
        circuit = GroupUnion(h, lambda n, common: cls(n, positions[common], 4), 'paired', 0, True)
        original = circuit.verify()
        at = time.monotonic(); old, old_meta = original_labels(circuit, True)
        old_seconds = time.monotonic()-at
        included.cache_clear()
        at = time.monotonic(); new, new_meta = labels(circuit, True)
        new_seconds = time.monotonic()-at
        assert old_meta == new_meta and old.keys() == new.keys()
        assert all(old[node] == new[node] for node in old)
        targets = target_check(circuit, new, True)
        assert target_check(circuit, old, True) == targets
        del old
        included.cache_clear(); gc.collect()
        physical = {}
        if args.physical:
            from frame_reuse import optimize_chains, compile_reuse, check
            at = time.monotonic()
            compiled = compile_reuse(circuit, new, optimize_chains(circuit, new, 'rank'))
            checked = check(circuit, new, compiled)
            physical = dict(roles=compiled['roles'], chains=compiled['chain_summary'],
                            checked=checked, elapsed_seconds=time.monotonic()-at)
            if args.positions_json:
                expected = json.loads(args.positions_json.read_text())
                assert expected['original'] == original
                assert expected['compiled_roles'] == compiled['roles']
                assert expected['checked'] == checked
        rows.append(dict(h=h, positions=positions, original=original,
                         compared_frames=len(new), metadata=new_meta,
                         original_seconds=old_seconds, direct_seconds=new_seconds,
                         frame_equality='Every Space field, rational basis, tag and node is identical',
                         unchanged_target_verifier=True, targets=targets, physical=physical))
        included.cache_clear()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='PASS', rows=rows,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()), indent=2)+'\n')


if __name__ == '__main__':
    main()
