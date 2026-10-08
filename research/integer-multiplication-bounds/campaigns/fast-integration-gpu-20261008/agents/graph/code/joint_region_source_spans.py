#!/usr/bin/env python3
"""Minimal positive source joins inside existing joint scalar regions.

PR62 scalar circuit: Avi Eisenberg. PR57 joint invertible synthesis and
paid reclamation: eumemic. An existing legal region partition is retained;
one-core address frames are reconstructed from primitive source spans and
incoming producer spaces. The old envelopes are upper bounds, never floors.
"""
from functools import lru_cache
from itertools import combinations

import co_signed_source_frames as co
from joint_scalar_future_frames import original_signed


def assign(c, blocks, owner, order):
    h = c.h
    minimum, source_support, source_summary = co.node_frames(c)
    pairs = list(combinations(range(h), 2))
    index = {pair: i for i, pair in enumerate(pairs)}
    incoming = [set() for _ in blocks]
    supports = [0] * len(blocks)
    for x in sorted(c.active):
        supports[owner[x]] |= source_support[x]
        for y in c.args[x] or ():
            if owner[y] != owner[x]:
                incoming[owner[x]].add(owner[y])

    @lru_cache(maxsize=200000)
    def source_edges(common, support):
        result = 0
        while support:
            bit = support & -support
            support -= bit
            triple = c.inputs[bit.bit_length() - 1]
            assert common in triple
            outside = tuple(sorted(set(triple) - {common}))
            result |= 1 << index[outside]
        return result

    @lru_cache(maxsize=200000)
    def original_edges(common, frame):
        core, cover = frame
        assert core >> common & 1
        if core == cover:
            assert core.bit_count() == 3
            outside = tuple(i for i in range(h) if i != common and core >> i & 1)
            return 1 << index[outside]
        assert core.bit_count() == 2
        other = next(i for i in range(h) if i != common and core >> i & 1)
        return sum(1 << index[tuple(sorted((other, i)))] for i in range(h)
                   if cover >> i & 1 and not core >> i & 1)

    labels = [None] * len(blocks)
    graphs = {}
    smaller = added = one_core = 0
    position = {g: i for i, g in enumerate(order)}
    for g in order:
        old = tuple(blocks[g]['frame'])
        core, cover = old
        envelope = original_signed(h, old)
        if core.bit_count() != 1:
            labels[g] = envelope
            continue
        one_core += 1
        common = core.bit_length() - 1
        edges = source_edges(common, supports[g])
        before = edges
        for donor in sorted(incoming[g]):
            assert position[donor] < position[g]
            donor_core = blocks[donor]['frame'][0]
            if donor_core.bit_count() == 1:
                assert donor_core == core
                edges |= graphs[donor]
            else:
                edges |= original_edges(common, tuple(blocks[donor]['frame']))
        added += (edges ^ before).bit_count()
        graphs[g] = edges
        labels[g] = co.edge_span(h, common, edges)
        assert co.contained(labels[g], envelope), ('Source-region span exceeds its legal upper envelope', g)
        smaller += labels[g][0] < envelope[0]
    for x in sorted(c.active):
        assert co.contained(minimum[x], labels[owner[x]])
        for y in c.args[x] or ():
            assert co.contained(labels[owner[y]], labels[owner[x]])
    for (common, target), x in c.outputs.items():
        if len(target) == 1:
            assert labels[owner[x]][0] == h - 1
    return labels, dict(source_summary, existing_scalar_regions=len(blocks),
        one_core_regions=one_core, strictly_smaller_region_spaces=smaller,
        forward_producer_edge_insertions=added,
        every_region_input_span_contained=True, actual_source_spans_contained=True,
        original_envelopes_upper_bound_only=True,
        selected_distinct_frames=len(set(labels)))
