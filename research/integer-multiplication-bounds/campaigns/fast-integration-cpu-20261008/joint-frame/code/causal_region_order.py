#!/usr/bin/env python3
"""Causal regional schedules; no source, frame or output is removed."""
import heapq


def scheduled_order(blocks, uses, owner, policy):
    dependencies = [{owner[y] for y in b['inputs']} for b in blocks]
    successors = [set() for _ in blocks]
    for g, parents in enumerate(dependencies):
        assert g not in parents
        for parent in parents:
            successors[parent].add(g)
    pending = [len(parents) for parents in dependencies]
    ready = []
    def priority(g):
        b = blocks[g]
        rank = b['rank']
        first = min(b['nodes'])
        output_count = len({uses[u][0] for u in b['uses']})
        if policy == 'rank-reverse':
            return rank, -first, g
        if policy == 'rank-pressure':
            return rank, len(b['inputs'])-output_count, first, g
        if policy == 'rank-fanout':
            return rank, -len(b['uses']), first, g
        if policy == 'ready-deep':
            return -rank, len(b['inputs'])-output_count, first, g
        if policy == 'ready-wide':
            return -len(b['inputs']), -rank, first, g
        raise ValueError(policy)
    for g, count in enumerate(pending):
        if not count:
            heapq.heappush(ready, priority(g))
    result = []
    while ready:
        g = heapq.heappop(ready)[-1]
        result.append(g)
        for child in successors[g]:
            pending[child] -= 1
            if not pending[child]:
                heapq.heappush(ready, priority(child))
    assert len(result) == len(blocks)
    place = {g: i for i, g in enumerate(result)}
    assert all(place[p] < place[g] for g, parents in enumerate(dependencies) for p in parents)
    return result
