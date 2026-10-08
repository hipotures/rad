#!/usr/bin/env python3
"""Causal ready-set schedules using prospective released carrier/frame mass.

These are search heuristics. Source regions and frame descriptors are intact;
actual reversible words and rational child profiles determine acceptance.
"""


def scheduled_order(blocks, uses, owner, policy):
    parents = [{owner[y] for y in b['inputs']} for b in blocks]
    children = [set() for _ in blocks]
    for g, ps in enumerate(parents):
        assert g not in ps
        for p in ps:
            children[p].add(g)
    pending = [len(ps) for ps in parents]
    remaining = [len(cs) for cs in children]
    ready = {g for g, n in enumerate(pending) if not n}
    output_count = [len({uses[u][0] for u in b['uses']}) for b in blocks]
    order = []
    def priority(g):
        rank = blocks[g]['rank']
        first = min(blocks[g]['nodes'])
        dying = [p for p in parents[g] if remaining[p] == 1]
        opened = output_count[g] if children[g] else 0
        closed = sum(output_count[p] for p in dying)
        delta = opened-closed
        mass = rank*opened-sum(blocks[p]['rank']*output_count[p] for p in dying)
        unlocked = sum(pending[c] == 1 for c in children[g])
        if policy == 'rank-release':
            return rank, delta, mass, first, g
        if policy == 'release-mass':
            return mass, delta, rank, first, g
        if policy == 'rank-unlock':
            return rank, -unlocked, delta, first, g
        raise ValueError(policy)
    while ready:
        g = min(ready, key=priority)
        ready.remove(g)
        order.append(g)
        for p in parents[g]:
            remaining[p] -= 1
            assert remaining[p] >= 0
        for c in children[g]:
            pending[c] -= 1
            if not pending[c]:
                ready.add(c)
    assert len(order) == len(blocks) and not any(remaining)
    place = {g:i for i,g in enumerate(order)}
    assert all(place[p] < place[g] for g, ps in enumerate(parents) for p in ps)
    return order
