#!/usr/bin/env python3
"""Coalesce nested original envelopes only after checking every direct use.

Public PR55/57/58 provide the scalar graph and regional compiler. This authored
rule changes region ownership with paid containing frames. It keeps all source
and terminal frames fixed and does not introduce a new rational frame family.
"""
from collections import defaultdict


def consumer_guarded_frames(c, config):
    original = {x:(c.core[x],c.union[x]) for x in c.active}
    groups = defaultdict(list)
    consumers = defaultdict(set)
    terminal = {original[x] for x in c.outputs.values()}
    for x in sorted(c.active):
        groups[original[x]].append(x)
        for y in c.args[x] or ():
            if original[y] != original[x]:
                consumers[original[y]].add(original[x])
    def contains(a,b):
        return not(b[0]&~a[0]) and not(a[1]&~b[1])
    def rank(f):
        return f[1].bit_count()-f[0].bit_count()
    options = []
    for f, nodes in groups.items():
        if f in terminal or any(c.args[x] is None for x in nodes):
            continue
        targets = consumers[f]
        for g in targets:
            gap=rank(g)-rank(f)
            if (0<gap<=config['max_rank_gap'] and contains(f,g)
                    and all(contains(g,h) for h in targets)):
                options.append((gap,-len(nodes),min(nodes),f,g))
    options.sort(reverse=config.get('reverse_selection',False))
    replacement = {}
    destinations = set()
    for gap, size, first, f, g in options:
        if f in replacement or f in destinations or g in replacement:
            continue
        assert all(contains(g,h) for h in consumers[f])
        replacement[f]=g
        destinations.add(g)
        if len(replacement)>=config['max_moved_regions']:
            break
    physical = {x:replacement.get(f,f) for x,f in original.items()}
    for x in sorted(c.active):
        assert contains(original[x],physical[x])
        if c.args[x] is None or x in c.outputs.values():
            assert physical[x]==original[x]
        for y in c.args[x] or ():
            assert contains(physical[y],physical[x])
    stats=dict(original_regions=len(groups),candidate_pairs=len(options),
               moved_regions=len(replacement),merged_destinations=len(destinations),
               resulting_regions=len(set(physical.values())),
               moved_nodes=sum(len(groups[f]) for f in replacement),
               replacement=[dict(source=list(f),destination=list(g)) for f,g in replacement.items()],
               criterion='Every original direct consumer contains the destination; source and terminal frames unchanged.')
    return physical,stats
