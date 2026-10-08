#!/usr/bin/env python3
"""Exact positive source spans via complemented signed edge-graph normals.

For a fixed common coordinate c, source triple {c,a,b} has outside generator
e_a+e_b. Its edge-span orthogonal complement has one signed normal for each
bipartite connected component, including isolated vertices; odd components
have no normal. Normals have disjoint supports. These symbols encode NORMALS,
not the direction classes in the older signed-positive frame format.
"""
from collections import deque
from functools import lru_cache
from itertools import combinations

from check_compiled_witness import basis as signed_basis
from check_compiled_witness import contained as signed_contained
from check_compiled_witness import vector_in as signed_vector_in

TAG = 'complemented-signed-one-core-v1'
FORMAT = 'mixed-signed-complemented-v1'


def normalize(frame):
    if len(frame) == 3:
        return int(frame[0]), int(frame[1]), tuple(frame[2])
    assert len(frame) == 4 and frame[2] == TAG
    return int(frame[0]), int(frame[1]), TAG, tuple(frame[3])


def symbols(frame):
    return frame[3] if len(frame) == 4 else frame[2]


@lru_cache(maxsize=300000)
def edge_span(h, common, edges):
    pairs = list(combinations(range(h), 2))
    adjacency = [0] * h
    pending_edges = edges
    while pending_edges:
        bit = pending_edges & -pending_edges
        pending_edges -= bit
        a, b = pairs[bit.bit_length() - 1]
        assert common not in (a, b)
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a
    labels = [0] * h
    labels[common] = 1
    visited = {common}
    normals = 0
    for first in range(h):
        if first in visited:
            continue
        colors = {first: 1}
        todo = deque([first])
        odd = False
        while todo:
            a = todo.popleft()
            neighbors = adjacency[a]
            while neighbors:
                bit = neighbors & -neighbors
                neighbors -= bit
                b = bit.bit_length() - 1
                if b not in colors:
                    colors[b] = -colors[a]
                    todo.append(b)
                elif colors[b] != -colors[a]:
                    odd = True
        visited.update(colors)
        if not odd:
            normals += 1
            for i, sign in colors.items():
                labels[i] = sign * (first + 2)
    frame = h - 1 - normals, 1 << common, TAG, tuple(labels)
    assert frame[0] > 0
    # A separately stated exact edge test detects a sign/normal convention
    # mismatch without using the produced frame's basis as the expected data.
    pending_edges = edges
    while pending_edges:
        bit = pending_edges & -pending_edges
        pending_edges -= bit
        a, b = pairs[bit.bit_length() - 1]
        assert labels[a] == labels[b] == 0 or labels[a] == -labels[b]
    return frame


@lru_cache(maxsize=300000)
def basis(frame):
    if len(frame) == 3:
        return signed_basis(frame)
    rank, forced, tag, normal = frame
    h = len(normal)
    assert tag == TAG and forced.bit_count() == 1 and forced >> h == 0
    common = forced.bit_length() - 1
    assert normal[common] == 1
    groups = {}
    for i, label in enumerate(normal):
        if i == common:
            continue
        assert label == 0 or abs(label) >= 2
        if label:
            groups.setdefault(abs(label), []).append(i)
    assert rank == h - 1 - len(groups)
    vectors = []
    def embed(outside):
        vector = [2 * x for x in outside]
        vector[common] = sum(outside)
        return tuple(vector)
    for i, label in enumerate(normal):
        if i != common and label == 0:
            outside = [0] * h
            outside[i] = 1
            vectors.append(embed(outside))
    for label, indices in sorted(groups.items()):
        pivot = min(indices)
        pivot_sign = 1 if normal[pivot] > 0 else -1
        for i in indices:
            if i == pivot:
                continue
            outside = [0] * h
            outside[i] = 1
            outside[pivot] = -(1 if normal[i] > 0 else -1) * pivot_sign
            vectors.append(embed(outside))
    assert len(vectors) == rank and all(any(v) for v in vectors)
    return tuple(vectors)


def vector_in(vector, frame):
    if len(frame) == 3:
        return signed_vector_in(vector, frame)
    rank, forced, tag, normal = frame
    assert tag == TAG and forced.bit_count() == 1
    common = forced.bit_length() - 1
    if sum(vector) != 3 * vector[common]:
        return False
    values = {}
    for i, label in enumerate(normal):
        if i == common or not label:
            continue
        values[abs(label)] = values.get(abs(label), 0) + (1 if label > 0 else -1) * vector[i]
    return not any(values.values())


@lru_cache(maxsize=300000)
def contained(a, b):
    if len(a) == len(b) == 3:
        return signed_contained(a, b)
    return a[0] <= b[0] and all(vector_in(vector, b) for vector in basis(a))


def node_frames(c):
    h = c.h
    pair_index = {pair: i for i, pair in enumerate(combinations(range(h), 2))}
    edge_graphs = {}
    source_support = {}
    frames = [None] * len(c.args)
    co_nodes = 0
    for x in sorted(c.active):
        core = c.core[x]
        common_points = [i for i in range(h) if core >> i & 1]
        if c.args[x]:
            a, b = c.args[x]
            assert not source_support[a] & source_support[b]
            source_support[x] = source_support[a] | source_support[b]
            edge_graphs[x] = {common: edge_graphs[a][common] | edge_graphs[b][common]
                              for common in common_points}
        else:
            triple = c.inputs[x - 1]
            assert core == sum(1 << i for i in triple)
            source_support[x] = 1 << (x - 1)
            edge_graphs[x] = {common: 1 << pair_index[tuple(sorted(set(triple) - {common}))]
                              for common in common_points}
        if core.bit_count() == 1:
            common = common_points[0]
            frames[x] = edge_span(h, common, edge_graphs[x][common])
            co_nodes += 1
        elif not c.args[x]:
            frames[x] = 1, core, tuple(int(core >> i & 1) for i in range(h))
        else:
            cover = c.union[x]
            assert core.bit_count() == 2
            frames[x] = cover.bit_count() - 2, core, tuple(1 if core >> i & 1 else i + 2 if cover >> i & 1 else 0 for i in range(h))
        assert len(basis(frames[x])) == frames[x][0]
        for y in c.args[x] or ():
            assert contained(frames[y], frames[x]), ('Actual source span dependency escapes', y, x)
    return frames, source_support, dict(actual_source_edge_spans_reconstructed=True,
        every_scalar_dependency_contained=True, one_core_nodes=co_nodes,
        distinct_frames=len({frames[x] for x in c.active}),
        original_envelope_floor_asserted=False)


def canonicalize(word, order):
    h = word['h']
    def move(frame):
        rank, forced = frame[:2]
        old = symbols(frame)
        new = [0] * h
        for i, j in enumerate(order):
            new[j] = old[i]
        core = sum(1 << order[i] for i in range(h) if forced >> i & 1)
        return (rank, core, TAG, tuple(new)) if len(frame) == 4 else (rank, core, tuple(new))
    aliases, frames, lookup = [], [], {}
    for old in word['frames']:
        frame = move(old)
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    fresh = dict(word, frames=frames, frame_format=FORMAT)
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['outputs'] = [(s, aliases[g], order[c], tuple(sorted(order[i] for i in t))) for s, g, c, t in word['outputs']]
    fresh['events'] = [(s, -1 if old < 0 else aliases[old], aliases[new]) for s, old, new in word['events']]
    triples = list(combinations(range(h), 3))
    index = {t: i for i, t in enumerate(triples)}
    labels = [index[tuple(sorted(order[i] for i in t))] for t in triples]
    inverse = [0] * len(labels)
    for i, j in enumerate(labels):
        inverse[j] = i
    fresh.update(source_permutation=order, source_label_permutation=labels, source_label_inverse=inverse)
    return fresh
