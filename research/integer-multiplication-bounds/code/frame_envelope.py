#!/usr/bin/env python3
"""Positive rational support envelopes for the paired bit side network.

An exact source span can retain unnecessary bipartite constraints. This
larger frame keeps the common coordinates, the total-sum relation, and the
support. It is positive under I-J/9 and stays orthogonal to every designated
target. The original controller compiler is used without changing its checks.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from frame_reuse import space_of, included, optimize_chains, compile_reuse, check


def labels(circuit, global_graph=False):
    h = circuit.h if global_graph else circuit.n+1
    triples = [sum(1 << v for v in t) for t in circuit.inputs] if global_graph else [
        (1 << circuit.n) | (1 << a) | (1 << b) for a, b in circuit.inputs]
    supports = {}
    cores = {}
    frames = {}
    intern = {}
    widened = 0
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            core = support = triples[node-1]
        else:
            a, b = circuit.args[node]
            core, support = cores[a] & cores[b], supports[a] | supports[b]
        assert core
        cores[node], supports[node] = core, support
        common = (core & -core).bit_length()-1
        if core.bit_count() == 1:
            outside = [v for v in range(h) if support & (1 << v) and v != common]
            assert len(outside) >= 3
            # A triangle plus a star spans all outside coordinates over Q.
            edges = [(outside[0], outside[1]), (outside[1], outside[2]),
                     (outside[0], outside[2])]
            edges.extend((outside[0], v) for v in outside[3:])
            generators = [(1 << common) | (1 << a) | (1 << b) for a, b in edges]
            widened += 1
        elif core.bit_count() == 2:
            generators = [core | (1 << v) for v in range(h) if (support & ~core) & (1 << v)]
        else:
            assert core == support and core.bit_count() == 3
            generators = [core]
        frame = space_of(generators, common, h)
        assert frame.core == core and frame.vertices == support
        key = (frame.common, frame.tags)
        frames[node] = intern.setdefault(key, frame)
        if circuit.args[node]:
            assert all(included(frames[child], frame) for child in circuit.args[node])
    return frames, {"unique_envelopes": len(intern), "common_one_nodes": widened,
                    "frame_family": "E(C,V): common coordinates equal z, total sum 3z, support V"}


def target_check(circuit, frames, global_graph=False):
    checked = 0
    for target, node in circuit.outputs.items():
        triple = target[1] if global_graph else tuple(target)+(circuit.n,)
        mask = sum(1 << v for v in triple)
        frame = frames[node]
        # A basis vector is a synthetic triple indicator. Its H pairing with
        # the target indicator is intersection size minus one, exactly.
        assert all((generator & mask).bit_count() == 1 for generator in frame.basis)
        checked += len(frame.basis)
    return {"all_output_envelopes_orthogonal_to_physical_targets": True,
            "exact_pairings": checked,
            "nondegeneracy_proof": "q(x)=sum(outside-common x_j^2)+(size(C)-1)z^2; positive"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--n", nargs="+", type=int, default=[5, 7, 9, 15, 25, 49])
    parser.add_argument("--global-h", type=int)
    parser.add_argument("--schedule", choices=["id", "rank"], default="rank")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.reference.resolve()/"scripts"))
    from paired_exclusion_circuit import PairedExclusionCircuit
    from finite_block_search import GroupUnion
    rows = []
    for dimension in ([args.global_h] if args.global_h else args.n):
        start = time.monotonic()
        circuit = GroupUnion(dimension, PairedExclusionCircuit, ordering="paired") if args.global_h else PairedExclusionCircuit(dimension)
        original = circuit.verify()
        frames, metadata = labels(circuit, bool(args.global_h))
        print(json.dumps({"phase": "labels", "dimension": dimension, **metadata}), flush=True)
        compiled = compile_reuse(circuit, frames, optimize_chains(circuit, frames, args.schedule))
        checked = check(circuit, frames, compiled)
        targets = target_check(circuit, frames, bool(args.global_h))
        row = {"dimension": dimension, "global_graph": bool(args.global_h),
               "original": original, "original_roles": circuit.additions+len(circuit.outputs),
               "roles": compiled["roles"], "chains": compiled["chain_summary"],
               "metadata": metadata, "check": checked, "targets": targets,
               "code_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "elapsed_seconds": time.monotonic()-start,
               "status": "Finite envelope mixer witness; full side invocation and mathematical transfer pending review"}
        rows.append(row)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(rows, indent=2)+"\n")
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
