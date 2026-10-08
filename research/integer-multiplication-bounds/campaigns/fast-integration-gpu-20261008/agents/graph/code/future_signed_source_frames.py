#!/usr/bin/env python3
"""Source-span joins with legal extra signed directions from future sinks.

For a common c, positive edge (a,b) means e_a+e_b; negative edge means
e_a-e_b. A signed graph's orthogonal normals again have disjoint supports.
Extra generators must annihilate EVERY future ordinary terminal equation,
and are propagated along every actual scalar dependency before synthesis.
No signal-dependent frame decrease or restricted source-array assumption
is used. The scalar source is Avi Eisenberg PR62; joint synthesis inherits
eumemic PR57 with explicit paid reclamation.
"""
from collections import deque
from functools import lru_cache
from itertools import combinations

import co_signed_source_frames as co


@lru_cache(maxsize=300000)
def signed_span(h, common, positive, negative):
    pairs = list(combinations(range(h), 2))
    adjacency = [[] for _ in range(h)]
    for mask, relation in ((positive, -1), (negative, 1)):
        while mask:
            bit = mask & -mask
            mask -= bit
            a, b = pairs[bit.bit_length() - 1]
            assert common not in (a, b)
            adjacency[a].append((b, relation))
            adjacency[b].append((a, relation))
    labels = [0] * h
    labels[common] = 1
    visited = {common}
    normals = 0
    for first in range(h):
        if first in visited:
            continue
        colors = {first: 1}
        todo = deque([first])
        inconsistent = False
        while todo:
            a = todo.popleft()
            for b, relation in adjacency[a]:
                expected = relation * colors[a]
                if b not in colors:
                    colors[b] = expected
                    todo.append(b)
                elif colors[b] != expected:
                    inconsistent = True
        visited.update(colors)
        if not inconsistent:
            normals += 1
            for i, sign in colors.items():
                labels[i] = sign * (first + 2)
    frame = h - 1 - normals, 1 << common, co.TAG, tuple(labels)
    assert frame[0] > 0 and len(co.basis(frame)) == frame[0]
    # Check every generating line directly against the independently defined
    # rational membership predicate, not merely the graph coloring rule.
    for mask, coefficient in ((positive, 1), (negative, -1)):
        while mask:
            bit = mask & -mask
            mask -= bit
            a, b = pairs[bit.bit_length() - 1]
            vector = [0] * h
            vector[a], vector[b], vector[common] = 2, 2 * coefficient, 1 + coefficient
            assert co.vector_in(vector, frame)
    return frame


def node_frames(c, policy, threshold):
    assert policy in ('difference-pairs', 'free-join', 'both')
    h = c.h
    pairs = list(combinations(range(h), 2))
    index = {p: i for i, p in enumerate(pairs)}
    minimum, support, baseline = co.node_frames(c)
    future = {x: set() for x in c.active}
    for (common, target), x in c.outputs.items():
        if len(target) == 3:
            a, b = sorted(set(target) - {common})
            future[x].add((common, a, b))
    for x in sorted(c.active, reverse=True):
        for y in c.args[x] or ():
            future[y].update(future[x])
    frames = list(minimum)
    positive, negative = {}, {}
    seeds = changes = extra_positive = extra_negative = 0
    beyond_cover_nodes = 0
    for x in sorted(c.active):
        core = c.core[x]
        commons = [i for i in range(h) if core >> i & 1]
        if c.args[x]:
            a, b = c.args[x]
            positive[x] = {common: positive[a][common] | positive[b][common] for common in commons}
            negative[x] = {common: negative[a][common] | negative[b][common] for common in commons}
        else:
            triple = c.inputs[x - 1]
            positive[x] = {common: 1 << index[tuple(sorted(set(triple) - {common}))] for common in commons}
            negative[x] = {common: 0 for common in commons}
        if len(commons) != 1:
            continue
        common = commons[0]
        assert all(t[0] == common for t in future[x])
        terminal_pairs = [(a, b) for _, a, b in future[x]]
        inc = {i: frozenset(j for j, pair in enumerate(terminal_pairs) if i in pair)
               for i in range(h) if i != common}
        p, n = positive[x][common], negative[x][common]
        before_p, before_n = p, n
        if minimum[x][0] >= threshold:
            if policy in ('free-join', 'both'):
                free = [i for i in inc if not inc[i]]
                for a, b in combinations(free, 2):
                    p |= 1 << index[(a, b)]
            if policy in ('difference-pairs', 'both'):
                for a, b in pairs:
                    if common in (a, b) or not inc[a] or inc[a] != inc[b]:
                        continue
                    n |= 1 << index[(a, b)]
        if p != before_p or n != before_n:
            seeds += 1
            extra_positive += (p ^ before_p).bit_count()
            extra_negative += (n ^ before_n).bit_count()
        positive[x][common], negative[x][common] = p, n
        frames[x] = signed_span(h, common, p, n)
        assert co.contained(minimum[x], frames[x])
        for vector in co.basis(frames[x]):
            assert all(vector[a] + vector[b] == 0 for a, b in terminal_pairs)
        changes += frames[x] != minimum[x]
        cover = c.union[x]
        beyond_cover_nodes += any(any(vector[i] for vector in co.basis(frames[x]))
                                  for i in range(h) if not cover >> i & 1)
    for x in sorted(c.active):
        for y in c.args[x] or ():
            assert co.contained(frames[y], frames[x]), ('Future signed source-frame dependency', y, x)
    summary = dict(baseline, policy=policy, threshold=threshold,
        exact_minimum_source_frames=False, actual_source_spans_contained=True,
        future_terminal_equations_checked=True, signed_source_generator_joins=True,
        seeded_nodes=seeds, changed_nodes=changes, extra_positive_edges=extra_positive,
        extra_negative_edges=extra_negative, nodes_extending_original_cover=beyond_cover_nodes,
        distinct_frames=len({frames[x] for x in c.active}))
    return frames, support, summary
