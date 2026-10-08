#!/usr/bin/env python3
"""Legal partial joins between minimal source spans and core/cover frames.

The scalar interval circuit is due to Avi Eisenberg (PR62). Joint binary
synthesis and paid reclamation are inherited from eumemic (PR57). Each added
edge is an actual positive source direction inside the node's cover. Its
span is propagated to every dependent scalar node before compilation.
These are new frame assignments, not uncharged changes of a physical word.
"""
from itertools import combinations

import co_signed_source_frames as co


def node_frames(c, policy, threshold):
    assert policy in ('oddify', 'join-components', 'cover')
    h = c.h
    pairs = list(combinations(range(h), 2))
    index = {p: i for i, p in enumerate(pairs)}
    minimum, support, minimum_summary = co.node_frames(c)
    frames = list(minimum)
    graphs = {}
    seeded = propagated = added_edges = 0
    for x in sorted(c.active):
        core = c.core[x]
        commons = [i for i in range(h) if core >> i & 1]
        if c.args[x]:
            a, b = c.args[x]
            graphs[x] = {common: graphs[a][common] | graphs[b][common]
                         for common in commons}
        else:
            triple = c.inputs[x - 1]
            graphs[x] = {common: 1 << index[tuple(sorted(set(triple) - {common}))]
                         for common in commons}
        if core.bit_count() != 1:
            continue
        common = commons[0]
        edges = graphs[x][common]
        before = co.edge_span(h, common, edges)
        cover = [i for i in range(h) if i != common and c.union[x] >> i & 1]
        assert before[0] <= len(cover)
        extras = []
        if policy == 'cover' and minimum[x][0] >= threshold:
            extras = list(combinations(cover, 2))
        elif policy in ('oddify', 'join-components'):
            components = {}
            for i in cover:
                label = before[3][i]
                if label:
                    components.setdefault(abs(label), []).append(i)
            if policy == 'oddify':
                for vertices in components.values():
                    if len(vertices) < threshold:
                        continue
                    for sign in (1, -1):
                        same = [i for i in vertices if before[3][i] * sign > 0]
                        if len(same) >= 2:
                            extras.append(tuple(same[:2]))
                            break
            elif len(components) >= threshold:
                pivots = [min(v) for _, v in sorted(components.items())]
                extras = list(zip(pivots, pivots[1:]))
        original_edges = edges
        for a, b in extras:
            assert a in cover and b in cover and common not in (a, b)
            edges |= 1 << index[tuple(sorted((a, b)))]
        if edges != original_edges:
            seeded += 1
            added_edges += (edges ^ original_edges).bit_count()
        graphs[x][common] = edges
        frames[x] = co.edge_span(h, common, edges)
        if frames[x] != minimum[x]:
            propagated += 1
        assert co.contained(minimum[x], frames[x])
        # The cover frame is an UPPER bound, never a mandatory lower floor.
        envelope = len(cover), core, tuple(1 if i == common else i + 2 if i in cover else 0
                                         for i in range(h))
        assert co.contained(frames[x], envelope)
        for y in c.args[x]:
            assert co.contained(frames[y], frames[x]), ('Hybrid source-frame dependency', y, x)
    for x in sorted(c.active):
        for y in c.args[x] or ():
            assert co.contained(frames[y], frames[x])
    summary = dict(minimum_summary, policy=policy, threshold=threshold,
        exact_minimum_source_frames=False, selected_positive_source_edge_joins=True,
        original_envelope_is_upper_bound=True, seeded_nodes=seeded,
        extra_edge_insertions=added_edges, changed_nodes=propagated,
        distinct_frames=len({frames[x] for x in c.active}))
    return frames, support, summary
