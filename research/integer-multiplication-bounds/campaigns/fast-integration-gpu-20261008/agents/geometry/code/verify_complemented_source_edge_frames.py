#!/usr/bin/env python3
"""Exact independent source-incidence and complemented-frame controls.

Normal labels describe orthogonal constraints, not positive-frame generators.
No restriction on the values of source arrays is introduced: the checked
source fact is inclusion of the entire rank-one source ADDRESS space.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from rational_one_core_frame_controls import (conjugate, constraint_projector,
    identity, inverse, mm, ordered_pivots, rref, transpose)


def independent_normal_classes(h, common, edges):
    outside = [i for i in range(h) if i != common]
    adjacency = {i:set() for i in outside}
    for a, b in edges:
        assert a != b and a in adjacency and b in adjacency
        adjacency[a].add(b)
        adjacency[b].add(a)
    colors, normals, components = {}, [], []
    symbols = [0]*h
    symbols[common] = 1
    for vertex in outside:
        if vertex in colors:
            continue
        colors[vertex] = 1
        pending = [vertex]
        vertices = []
        odd = False
        while pending:
            a = pending.pop()
            vertices.append(a)
            for b in sorted(adjacency[a]):
                if b not in colors:
                    colors[b] = -colors[a]
                    pending.append(b)
                elif colors[b] == colors[a]:
                    odd = True
        components.append(dict(vertices=sorted(vertices), odd=odd))
        if not odd:
            label = len(normals)+2
            for a in vertices:
                symbols[a] = label*colors[a]
            normals.append([Q(colors[a]) if a in vertices else Q(0) for a in outside])
    return normals, symbols, components


def explicit_source_edge_projector(h, common, edges, beta):
    outside = [i for i in range(h) if i != common]
    source_rows = [[Q(i == a or i == b) for i in outside] for a,b in edges]
    rows, _ = rref(source_rows, h-1)
    rank = len(rows)
    if not rank:
        return [[Q(0)]*h for _ in range(h)], 0
    T = [[Q(1 if i == common else 2 if i == j else 0)
          for j in outside] for i in range(h)]
    B = mm(T, transpose(rows))
    H0 = [[Q(i == j)-Q(1,9) for j in range(h)] for i in range(h)]
    dual = mm(transpose(B), H0)
    P = mm(mm(B, inverse(mm(dual, B))), dual)
    return conjugate(P, beta), rank


def check_graph(h, common, edges, beta, name):
    normals, symbols, components = independent_normal_classes(h, common, edges)
    coframe = constraint_projector(h, common, normals, beta)
    direct, rank = explicit_source_edge_projector(h, common, edges, beta)
    assert coframe == direct, 'Coframe differs from literal source-edge span'
    assert rank == h-1-len(normals), 'Isolated or odd component rank was mischarged'
    assert mm(coframe, coframe) == coframe
    assert sum(coframe[i][i] for i in range(h)) == rank
    if normals:
        gram = mm(normals, transpose(normals))
        assert all(gram[i][j] == (sum(abs(x) for x in normals[i]) if i == j else 0)
                   for i in range(len(normals)) for j in range(len(normals)))
    L = [[Q(i == j)-beta for j in range(h)] for i in range(h)]
    for a,b in edges:
        source = mm(L, [[Q(i in (common,a,b))] for i in range(h)])
        assert mm(coframe, source) == source, 'An actual rank-one source address escaped its frame'
    return dict(name=name,h=h,common=common,beta=str(beta),
        format='complemented-signed-one-core-v1', rank=rank,
        forced=1 << common, normal_symbols=symbols,
        edges=[list(edge) for edge in edges], components=components,
        normal_class_count=len(normals),
        direct_source_edge_Gram_equals_complemented_projector=True,
        all_rank_one_source_address_spaces_contained=True,
        arbitrary_source_array_values_unrestricted=True), coframe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    started = time.monotonic()
    cases, continuations = [], []
    all_edges = list(combinations(range(1,5),2))
    for mask in range(1 << len(all_edges)):
        edges = [edge for i,edge in enumerate(all_edges) if mask >> i & 1]
        case,_ = check_graph(5,0,edges,Q(0),f'exhaustive-four-vertices-{mask}')
        cases.append(case)
    for h, common, beta in [(23,20,Q(1,15)),(23,0,Q(-1,12)),
                            (25,23,Q(7,207)),(25,3,Q(1,2))]:
        vertices = [i for i in range(h) if i != common]
        graphs = dict(empty=[],edge=[(vertices[0],vertices[1])],
            two_equal_partitions=[(vertices[0],vertices[1]),(vertices[2],vertices[3])],
            crossing_partitions=[(vertices[0],vertices[2]),(vertices[1],vertices[3])],
            rectangle=[(vertices[0],vertices[1]),(vertices[2],vertices[3]),
                       (vertices[0],vertices[2]),(vertices[1],vertices[3])],
            odd_triangle=[(vertices[0],vertices[1]),(vertices[1],vertices[2]),
                          (vertices[2],vertices[0])],
            star=[(vertices[0],vertices[j]) for j in range(1,h-1)],
            full=list(combinations(vertices,2)))
        projectors = {}
        for name, edges in graphs.items():
            case,projectors[name] = check_graph(h,common,edges,beta,name)
            cases.append(case)
        for old,new in [('edge','star'),('two_equal_partitions','rectangle'),
                        ('crossing_partitions','rectangle'),('rectangle','full'),
                        ('odd_triangle','full'),('star','full')]:
            A,B = projectors[old],projectors[new]
            assert mm(A,B) == A and mm(B,A) == A
            M = [[y-x for x,y in zip(row,other)] for row,other in zip(A,B)]
            assert mm(M,M) == M
            rank = sum(M[i][i] for i in range(h))
            pivots = ordered_pivots(M)
            assert len(pivots) == rank
            continuations.append(dict(h=h,common=common,beta=str(beta),
                old=old,new=new,rank=int(rank),ordered_NE_pivots=pivots,
                exact_both_sided_containment=True))
        # This nonpartition join has exactly rank three on the four coordinates.
        rank_rectangle = next(case['rank'] for case in cases
            if case['h']==h and case['common']==common and case['name']=='rectangle')
        assert rank_rectangle == 3
        print(json.dumps(dict(h=h,common=common,beta=str(beta),completed=len(cases))),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS INDEPENDENT COMPLEMENTED SOURCE-EDGE FRAME CONTROLS',
        classification='DISCOVERY', cases=cases, continuations=continuations,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        elapsed_seconds=time.monotonic()-started,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        scope='Exact source-incidence rank, full one-core positive Gram, actual rank-one '
              'source-address inclusion and both-sided projector containment. No '
              'ridge restriction, physical word, capacity allocation, full CRT, '
              'arbitrary-dirty replay, full DATA or conditional exponent accepted.'),indent=2)+'\n')


if __name__ == '__main__':
    main()
