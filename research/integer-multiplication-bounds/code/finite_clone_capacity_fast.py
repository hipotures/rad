#!/usr/bin/env python3
"""Linear component traversal for the frozen capacity-matching selector.

The frozen opportunity generator offers one borrowed controller per parent.
Its undirected capacity graph is a pseudoforest. Leaf elimination followed
by alternating cycle edges gives an exact maximum cardinality matching for
capacity conflicts alone. Formal-input conflicts remain separate and are
filtered by the existing conservative compatibility rule. The original
greedy selection is always retained as a competing feasible candidate.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import heapq
import json
from pathlib import Path
import random
import time

import finite_clone_descendant_frame as witness
from finite_clone_chain_bridge import bridge_compatible as conservative


LAST_SELECTION = {}


def capacity_matching(jobs, seed=0):
    """Return maximum capacity-matching edges and their job alternatives."""
    edge_jobs = defaultdict(list)
    parents = set()
    for index, job in enumerate(jobs):
        parent = job['node']; borrowed = job['predecessor_gates'][1]
        assert len(job['predecessor_gates']) == 2 and job['predecessor_gates'][0] == parent
        assert parent != borrowed and parent not in parents
        parents.add(parent)
        edge_jobs[tuple(sorted((parent, borrowed)))].append(index)
    adjacency = defaultdict(set)
    for left, right in edge_jobs:
        adjacency[left].add(right); adjacency[right].add(left)
    # A one-outgoing-edge directed graph is a pseudoforest. Check each
    # component explicitly instead of relying on the generator's intent.
    unseen = set(adjacency); components = 0; cyclic_components = 0
    while unseen:
        start = next(iter(unseen)); stack = [start]; vertices = set(); degree_sum = 0
        while stack:
            vertex = stack.pop()
            if vertex in vertices: continue
            vertices.add(vertex); degree_sum += len(adjacency[vertex])
            stack.extend(adjacency[vertex] - vertices)
        unseen.difference_update(vertices)
        assert degree_sum // 2 <= len(vertices)
        components += 1; cyclic_components += degree_sum // 2 == len(vertices)
    vertices = sorted(adjacency)
    shuffled = vertices[:]; random.Random(seed).shuffle(shuffled)
    priority = {vertex: rank for rank, vertex in enumerate(shuffled)}
    if seed == 0: priority = {vertex: vertex for vertex in vertices}
    if seed == -1: priority = {vertex: -vertex for vertex in vertices}
    leaves = [(priority[v], v) for v in vertices if len(adjacency[v]) == 1]
    heapq.heapify(leaves); chosen_edges = []

    def remove(vertex):
        for neighbor in tuple(adjacency[vertex]):
            adjacency[neighbor].remove(vertex)
            if len(adjacency[neighbor]) == 1:
                heapq.heappush(leaves, (priority[neighbor], neighbor))
        adjacency[vertex].clear()

    while leaves:
        _, leaf = heapq.heappop(leaves)
        if len(adjacency[leaf]) != 1: continue
        neighbor = next(iter(adjacency[leaf]))
        chosen_edges.append(tuple(sorted((leaf, neighbor))))
        remove(leaf); remove(neighbor)
    remaining = {vertex for vertex in vertices if adjacency[vertex]}
    while remaining:
        start = min(remaining, key=priority.__getitem__)
        cycle = [start]; previous = None; current = start
        while True:
            assert len(adjacency[current]) == 2
            options = adjacency[current] - ({previous} if previous is not None else set())
            following = min(options, key=priority.__getitem__)
            if following == start: break
            assert following not in cycle
            cycle.append(following); previous, current = current, following
        remaining.difference_update(cycle)
        for index in range(0, len(cycle)-1, 2):
            chosen_edges.append(tuple(sorted((cycle[index], cycle[index+1]))))
    assert len({vertex for edge in chosen_edges for vertex in edge}) == 2*len(chosen_edges)
    return chosen_edges, edge_jobs, dict(capacity_components=components,
        unicyclic_components=cyclic_components, capacity_edges=len(edge_jobs),
        maximum_capacity_matching=len(chosen_edges))


def select(jobs, seeds=(0,-1,1,2,3,4,5,6)):
    global LAST_SELECTION
    baseline, _ = conservative(jobs); best = baseline; trials = []
    for seed in seeds:
        edges, choices, diagnostic = capacity_matching(jobs, seed)
        # Opposite orientations of one capacity edge can have different
        # formal-child conflicts. Both deterministic orientations are screened.
        for reverse in (False, True):
            candidates = [jobs[sorted(choices[edge],
                key=lambda index: jobs[index]['node'], reverse=reverse)[0]] for edge in edges]
            for order in ('parent','reverse-parent','matching'):
                ordered = (sorted(candidates,key=lambda job:job['node'],reverse=order=='reverse-parent')
                    if order!='matching' else candidates)
                chosen, rejected = conservative(ordered)
                trials.append(dict(seed=seed,orientation_reverse=reverse,order=order,
                    compatible_clones=len(chosen),formal_conflict_rejected=len(rejected),**diagnostic))
                if len(chosen)>len(best):best=chosen
    chosen_nodes={job['node'] for job in best}
    assert len(chosen_nodes)==len(best)
    rejected=[job for job in jobs if job['node'] not in chosen_nodes]
    LAST_SELECTION=dict(original_greedy_clones=len(baseline),selected_clones=len(best),
        improvement_over_greedy=len(best)-len(baseline),trials=trials,
        proof_scope='Maximum matching only for the capacity relaxation; formal-input conflicts use the unchanged conservative filter')
    return best,rejected


def case(h,base,positions,frozen=None,dirty=False):
    previous=witness.bridge_compatible;witness.bridge_compatible=select
    try:row=witness.case(h,base,positions,frozen,dirty)
    finally:witness.bridge_compatible=previous
    row['capacity_selection']=LAST_SELECTION
    row['capacity_selection_source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    return row


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--h',nargs='+',type=int,default=[8,12,20])
    ap.add_argument('--base',type=int,default=2);ap.add_argument('--candidate',type=Path)
    ap.add_argument('--dirty-ground',type=int);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();witness.install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        witness_source_sha256=sha256(Path(witness.__file__).read_bytes()).hexdigest(),rows=[],
        started_utc=datetime.now(timezone.utc).isoformat(),scientific_scope='Only clone selection changes; original generator, inherited frames and every physical check retained')
    frozen=json.loads(args.candidate.read_text()) if args.candidate else None
    if frozen:
        value['candidate_input_sha256']=sha256(args.candidate.read_bytes()).hexdigest()
        if 'logical' not in frozen:frozen={**frozen,'logical':frozen['original']}
        if 'checked' not in frozen:frozen={**frozen,'checked':frozen['compiled']}
    configs=[(frozen['h'],frozen['base'],frozen['positions'])] if frozen else [(h,args.base,[0]*(h//2-1)+[h//2-2]*(h//2+1)) for h in args.h]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h,base,positions in configs:
        row=case(h,base,positions,frozen,args.dirty_ground==h);value['rows'].append(row)
        args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=row['baseline']['roles'],roles=row['final']['roles'],
            clones=len(row['chosen']),selection=row['capacity_selection']['improvement_over_greedy'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal exact capacity-selection clone witness PASS',
        completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
