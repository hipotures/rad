#!/usr/bin/env python3
"""Retain controller roles across increasing frame spans in a fixed finite DAG.

This is an experimental replacement reversible compiler. An addition consumes
one pivot input, but may retain its other input for later uses. A controller
chain is allowed only when successive common gate frames are nested. All
scalar coefficients and both frame directions are checked after compilation.
The fixed graph and admissible chain optimization are distinct from a claim
of globally optimal circuits or an integer multiplication theorem.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time


@dataclass(frozen=True)
class Space:
    """Exact common-point indicator span via signless graph incidence."""
    common: int
    tags: tuple[int, ...]
    basis: tuple[int, ...]
    core: int
    vertices: int

    @property
    def dimension(self):
        return len(self.basis)


def space_of(triples, common, h):
    """Canonical span, retaining actual rational vectors as a basis.

    Remove the common coordinate. The indicators become e_a+e_b. A bipartite
    connected component has one signed-sum constraint; an odd cycle makes
    its entire coordinate space available. Isolated unused vertices are zero.
    Reattaching the common coordinate uses x_common=sum(x_other)/2.
    """
    parent = list(range(h))
    parity = [0] * h
    odd = [False] * h
    active = set()

    def find(v):
        if parent[v] != v:
            p = parent[v]
            parent[v], sign = find(p)
            parity[v] ^= sign
        return parent[v], parity[v]

    for triple in triples:
        assert triple & (1 << common)
        pair = triple ^ (1 << common)
        assert pair.bit_count() == 2
        a = (pair & -pair).bit_length() - 1
        b = (pair ^ (1 << a)).bit_length() - 1
        active.update((a, b))
        ra, pa = find(a)
        rb, pb = find(b)
        if ra == rb:
            if pa ^ pb != 1:
                odd[ra] = True
        else:
            parent[rb] = ra
            parity[rb] = pa ^ pb ^ 1
            odd[ra] = odd[ra] or odd[rb]
    components = {}
    for v in range(h):
        if v != common:
            r, p = find(v)
            components.setdefault(r, []).append((v, p))
    tags = [0] * h
    full = []
    signed = []
    for vertices in sorted(components.values(), key=lambda vs: vs[0][0]):
        r, _ = find(vertices[0][0])
        if odd[r]:
            full.extend(v for v, _ in vertices)
        else:
            signed.append(vertices)
    basis = []

    def edge(a, b):
        basis.append((1 << common) | (1 << a) | (1 << b))

    if full:
        full.sort()
        assert len(full) >= 3
        edge(full[0], full[1])
        edge(full[1], full[2])
        edge(full[0], full[2])
        for v in full[3:]:
            edge(full[0], v)
    for index, vertices in enumerate(signed, 1):
        orientation = vertices[0][1]
        positive, negative = [], []
        for v, p in vertices:
            tags[v] = index if p == orientation else -index
            (positive if p == orientation else negative).append(v)
        if negative:
            edge(positive[0], negative[0])
            for v in negative[1:]:
                edge(positive[0], v)
            for v in positive[1:]:
                edge(v, negative[0])
        else:
            assert len(positive) == 1 and positive[0] not in active
    assert basis
    core = (1 << h) - 1
    union = 0
    for triple in basis:
        core &= triple
        union |= triple
    return Space(common, tuple(tags), tuple(basis), core, union)


@lru_cache(maxsize=500000)
def included(a: Space, b: Space):
    if not a.core & (1 << b.common) or a.vertices & ~b.vertices:
        return False
    for triple in a.basis:
        pair = triple ^ (1 << b.common)
        if pair.bit_count() != 2:
            return False
        v = (pair & -pair).bit_length() - 1
        w = (pair ^ (1 << v)).bit_length() - 1
        if b.tags[v] + b.tags[w] != 0:
            return False
    return True


def labels(circuit, global_graph=False):
    h = circuit.h if global_graph else circuit.n + 1
    values = {}
    intern = {}
    triples = [sum(1 << v for v in t) for t in circuit.inputs] if global_graph else [
        (1 << circuit.n) | (1 << a) | (1 << b) for a, b in circuit.inputs
    ]
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            generators = (triples[node - 1],)
            core = triples[node - 1]
        else:
            a, b = (values[x] for x in circuit.args[node])
            generators = a.basis + b.basis
            core = a.core & b.core
        assert core, "A common point is required for this exact span transfer"
        common = (core & -core).bit_length() - 1
        frame = space_of(generators, common, h)
        key = (frame.common, frame.tags)
        values[node] = intern.setdefault(key, frame)
    return values, len(intern)


def optimize_chains(circuit, spaces, schedule="id"):
    """Exact maximum number of admissible retained-controller links.

    Each gate may retain at most one of its two incoming values: the other
    terminates its incoming chain and supplies the consumed pivot. A unit
    capacity from the source to each parent gate enforces that restriction.
    A separate unit capacity on each incoming user prevents two predecessors.
    Topological order makes every resulting controller chain acyclic.
    """
    import numpy as np
    from scipy.sparse import coo_array
    from scipy.sparse.csgraph import maximum_flow

    order = sorted(circuit.active, key=(lambda node: (spaces[node].dimension, node)) if schedule == "rank" else None)
    positions = {node: i for i, node in enumerate(order)}
    for node in order:
        if circuit.args[node]:
            assert all(positions[child] < positions[node] for child in circuit.args[node])
    users = {node: [] for node in circuit.active}
    descriptions = []
    gate_order = {}
    for node in order:
        if circuit.args[node]:
            gate_order[node] = len(gate_order)
            for position, child in enumerate(circuit.args[node]):
                user = len(descriptions)
                descriptions.append((child, node, position))
                users[child].append(user)
    for target, node in sorted(circuit.outputs.items()):
        user = len(descriptions)
        descriptions.append((node, None, target))
        users[node].append(user)
    count = len(descriptions)
    gates = len(gate_order)
    source, sink = 0, 1
    group_base = 2
    out_base = group_base + gates
    in_base = out_base + count
    dimension = in_base + count
    rows, cols = [], []

    def connect(u, v):
        rows.append(u)
        cols.append(v)

    for node, order in gate_order.items():
        connect(source, group_base + order)
    for user, (_, parent, _) in enumerate(descriptions):
        connect(in_base + user, sink)
        if parent is not None:
            connect(group_base + gate_order[parent], out_base + user)
    candidates = 0
    for node, outgoing in users.items():
        for index, first in enumerate(outgoing):
            _, previous, _ = descriptions[first]
            if previous is None:
                continue
            for second in outgoing[index + 1:]:
                _, following, _ = descriptions[second]
                following_frame = spaces[following if following is not None else node]
                if included(spaces[previous], following_frame):
                    connect(out_base + first, in_base + second)
                    candidates += 1
    graph = coo_array((np.ones(len(rows), dtype=np.int32),
                       (np.asarray(rows, dtype=np.int32), np.asarray(cols, dtype=np.int32))),
                      shape=(dimension, dimension)).tocsr()
    flow = maximum_flow(graph, source, sink, method="dinic")
    outgoing_link = {}
    incoming_link = {}
    sparse = flow.flow.tocoo()
    for row, col, value in zip(sparse.row, sparse.col, sparse.data):
        if value > 0 and out_base <= row < in_base and in_base <= col < dimension:
            first, second = int(row - out_base), int(col - in_base)
            assert first not in outgoing_link and second not in incoming_link
            outgoing_link[first] = second
            incoming_link[second] = first
    assert len(outgoing_link) == flow.flow_value
    # Audit constraints independently of the optimizer's construction.
    retained_at_gate = {}
    for first, second in outgoing_link.items():
        node, previous, _ = descriptions[first]
        node2, following, _ = descriptions[second]
        assert node == node2 and first < second and previous is not None
        assert included(spaces[previous], spaces[following if following is not None else node])
        retained_at_gate[previous] = retained_at_gate.get(previous, 0) + 1
        assert retained_at_gate[previous] <= 1
    return users, descriptions, outgoing_link, incoming_link, {
        "candidate_links": candidates, "selected_links": len(outgoing_link),
        "flow_value": int(flow.flow_value), "flow_vertices": dimension,
        "flow_edges": len(rows), "schedule": schedule,
        "scope": "Maximum within this fixed graph and topological controller-chain ansatz",
    }


def compile_reuse(circuit, spaces, plan):
    users, descriptions, successor, predecessor, summary = plan
    edges = {}
    outputs = {}
    sources = {}
    gates = []
    allocated = 0
    use_for_gate = {}
    for user, (_, parent, position) in enumerate(descriptions):
        if parent is not None:
            use_for_gate[parent, position] = user
    order = sorted(circuit.active, key=(lambda node: (spaces[node].dimension, node)) if summary["schedule"] == "rank" else None)
    for node in order:
        starts = [user for user in users[node] if user not in predecessor]
        assert starts
        if circuit.args[node] is None:
            pivot = allocated
            allocated += 1
            ins = (pivot,)
            sources[circuit.inputs[node - 1]] = pivot
        else:
            incoming = [use_for_gate[node, pos] for pos in (0, 1)]
            terminal = [pos for pos, user in enumerate(incoming) if user not in successor]
            assert terminal, "At least one terminating input supplies the result pivot"
            position = terminal[0]
            ins = (edges[incoming[position]], edges[incoming[1 - position]])
            pivot = ins[0]
        outs = (pivot,) + tuple(range(allocated, allocated + len(starts) - 1))
        allocated += len(starts) - 1
        assert len(set(ins)) == len(ins) and set(ins) & set(outs) == {pivot}
        gates.append((node, ins, outs))
        for first, slot in zip(starts, outs):
            user = first
            while True:
                edges[user] = slot
                _, parent, target = descriptions[user]
                if parent is None:
                    outputs[target] = slot
                if user not in successor:
                    break
                user = successor[user]
    assert allocated == circuit.additions + len(circuit.outputs) - len(successor)
    assert len(set(outputs.values())) == len(outputs)
    return {"roles": allocated, "gates": gates, "sources": sources,
            "outputs": outputs, "chain_summary": summary}


def check(circuit, spaces, code):
    size = code["roles"]
    values = [0] * size
    frames = [None] * size
    source_ids = circuit.variables
    expected = {}
    for key, slot in code["sources"].items():
        node = source_ids[key]
        values[slot] = 1 << (node - 1)
        frames[slot] = spaces[node]
    for node in sorted(circuit.active):
        expected[node] = (expected[circuit.args[node][0]] ^ expected[circuit.args[node][1]]) if circuit.args[node] else 1 << (node - 1)
    for node, ins, outs in code["gates"]:
        frame = spaces[node]
        for slot in set(ins + outs):
            assert frames[slot] is None or included(frames[slot], frame)
            frames[slot] = frame
        for slot in ins[1:]:
            values[ins[0]] ^= values[slot]
        for slot in outs[1:]:
            values[slot] ^= values[ins[0]]
        for slot in outs:
            assert values[slot] == expected[node]
    for target, slot in code["outputs"].items():
        assert values[slot] == expected[circuit.outputs[target]]
        assert included(frames[slot], spaces[circuit.outputs[target]])
    reverse = [None] * size
    for target, slot in code["outputs"].items():
        reverse[slot] = spaces[circuit.outputs[target]]
    for node, ins, outs in reversed(code["gates"]):
        frame = spaces[node]
        for slot in set(ins + outs):
            assert reverse[slot] is None or included(frame, reverse[slot])
            reverse[slot] = frame
    for key, slot in code["sources"].items():
        assert reverse[slot] == spaces[source_ids[key]]
    digest = sha256(json.dumps({"roles": size, "gates": code["gates"],
                               "sources": sorted(code["sources"].items()),
                               "outputs": sorted(code["outputs"].items())}, separators=(",", ":")).encode()).hexdigest()
    return {"all_scalar_coefficients_exact": True, "forward_frames_nested": True,
            "reverse_complement_frames_nested": True, "nondegeneracy": "Every retained frame has a common point",
            "compiled_sha256": digest}


def independent_spaces(circuit, spaces):
    """Small independent rational elimination validates graph span algebra."""
    import sympy as sp
    h = circuit.n + 1
    originals = {}
    for node in sorted(circuit.active):
        originals[node] = (originals[circuit.args[node][0]] | originals[circuit.args[node][1]]) if circuit.args[node] else {node - 1}
        columns = []
        for index in originals[node]:
            a, b = circuit.inputs[index]
            columns.append([int(v in (a, b, circuit.n)) for v in range(h)])
        mat = sp.Matrix(h, len(columns), lambda v, c: columns[c][v])
        frame = spaces[node]
        basis = sp.Matrix(h, len(frame.basis), lambda v, c: (frame.basis[c] >> v) & 1)
        assert mat.rank() == basis.rank() == frame.dimension
        assert mat.row_join(basis).rank() == frame.dimension
    checked = 0
    unique = list(set(spaces.values()))
    for a in unique:
        A = sp.Matrix(h, len(a.basis), lambda v, c: (a.basis[c] >> v) & 1)
        for b in unique:
            B = sp.Matrix(h, len(b.basis), lambda v, c: (b.basis[c] >> v) & 1)
            assert included(a, b) == (B.row_join(A).rank() == b.dimension)
            checked += 1
    return {"exact_rational_span_checks": len(spaces), "exact_rational_inclusion_checks": checked}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--n", type=int, nargs="+", default=[5, 7, 9, 15, 25, 49])
    parser.add_argument("--global-h", type=int)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--independent-small", action="store_true")
    parser.add_argument("--schedule", choices=["id", "rank"], default="id")
    args = parser.parse_args()
    sys.path.insert(0, str(Path(args.reference).resolve() / "scripts"))
    from paired_exclusion_circuit import PairedExclusionCircuit
    results = []
    dimensions = [args.global_h] if args.global_h else args.n
    for dimension in dimensions:
        start = time.monotonic()
        if args.global_h:
            from finite_block_search import GroupUnion
            circuit = GroupUnion(dimension, PairedExclusionCircuit, ordering="paired")
        else:
            circuit = PairedExclusionCircuit(dimension)
        original = circuit.verify()
        frame, unique = labels(circuit, global_graph=bool(args.global_h))
        print(json.dumps({"phase": "labels", "dimension": dimension, "unique_spans": unique,
                          "seconds": time.monotonic() - start}), flush=True)
        plan = optimize_chains(circuit, frame, args.schedule)
        code = compile_reuse(circuit, frame, plan)
        verified = check(circuit, frame, code)
        independent = independent_spaces(circuit, frame) if args.independent_small and not args.global_h and dimension <= 5 else {}
        result = {"dimension": dimension, "global_graph": bool(args.global_h), "original": original,
                  "original_roles": circuit.additions + len(circuit.outputs), "reused_roles": code["roles"],
                  "unique_spans": unique, "chains": code["chain_summary"], "verified": verified,
                  "independent": independent, "elapsed_seconds": time.monotonic() - start,
                  "status": "Exact finite mixer/frame witness; full invocation and downstream transfer not yet checked"}
        results.append(result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
