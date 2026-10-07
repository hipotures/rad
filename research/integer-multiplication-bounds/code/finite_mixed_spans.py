#!/usr/bin/env python3
"""Exact mixed two-point source-span criterion and small independent checks.

For a fixed pair A={a,b}, aggregate the triples {a,u,v} and {b,u,v}
over an outside edge graph Γ. Its span is a positive difference line plus
the unsigned incidence span of Γ with form I-J/8. The rank-one singularity
condition is explicit and is checked against exact rational bases here.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
from fractions import Fraction as Q
from itertools import combinations
import json
from pathlib import Path
import time


def component_criterion(vertices,edges):
    graph={v:set() for v in vertices}
    for a,b in edges:
        assert a!=b
        graph[a].add(b)
        graph[b].add(a)
    seen=set()
    components=[]
    norm=Q(0)
    rank=0
    for root in vertices:
        if root in seen or not graph[root]:
            continue
        color={root:0}
        queue=deque([root])
        seen.add(root)
        bipartite=True
        while queue:
            v=queue.popleft()
            for u in graph[v]:
                if u not in color:
                    color[u]=1-color[v]
                    queue.append(u)
                    seen.add(u)
                elif color[u]==color[v]:
                    bipartite=False
        if bipartite:
            left=sum(c==0 for c in color.values())
            right=len(color)-left
            contribution=Q(4*left*right,left+right)
            component_rank=len(color)-1
            components.append({"vertices":sorted(color),"bipartite":True,"left":left,"right":right,"ones_projection_squared":str(contribution)})
        else:
            contribution=Q(len(color))
            component_rank=len(color)
            components.append({"vertices":sorted(color),"bipartite":False,"ones_projection_squared":str(contribution)})
        norm+=contribution
        rank+=component_rank
    return {"components":components,"unsigned_incidence_rank":rank,"ones_projection_squared":str(norm),"source_span_rank":rank+(1 if edges else 0),"nondegenerate":norm!=8,"positive_definite":norm<8,"determinant_factor":str(1-norm/8)}


def exact_basis(vectors):
    """Select original integer vectors using an independent rational RREF."""
    echelon={}
    selected=[]
    for original in vectors:
        reduced=[Q(z) for z in original]
        for pivot,row in sorted(echelon.items()):
            scale=reduced[pivot]
            if scale:
                reduced=[z-scale*w for z,w in zip(reduced,row)]
        pivot=next((i for i,z in enumerate(reduced) if z),None)
        if pivot is None:
            continue
        scale=reduced[pivot]
        reduced=[z/scale for z in reduced]
        echelon[pivot]=reduced
        selected.append(original)
    return selected


def bareiss_determinant(matrix):
    """Exact integer determinant with pivoting and checked divisions."""
    a=[row[:] for row in matrix]
    n=len(a)
    if not n:
        return 1
    previous=1
    sign=1
    for i in range(n-1):
        if not a[i][i]:
            swap=next((j for j in range(i+1,n) if a[j][i]),None)
            if swap is None:
                return 0
            a[i],a[swap]=a[swap],a[i]
            sign=-sign
        pivot=a[i][i]
        for j in range(i+1,n):
            for k in range(i+1,n):
                numerator=a[j][k]*pivot-a[j][i]*a[i][k]
                assert numerator%previous==0
                a[j][k]=numerator//previous
            a[j][i]=0
        previous=pivot
    return sign*a[-1][-1]


def independent_check(n,edges):
    vectors=[]
    for u,v in edges:
        for common in (0,1):
            vector=[0]*(n+2)
            vector[common]=vector[u+2]=vector[v+2]=1
            vectors.append(vector)
    basis=exact_basis(vectors)
    # Triple indicators have sums three, so Gram entry is intersection minus one.
    gram=[[sum(x*y for x,y in zip(a,b))-1 for b in basis] for a in basis]
    determinant=bareiss_determinant(gram)
    predicted=component_criterion(list(range(n)),edges)
    assert len(basis)==predicted["source_span_rank"]
    assert (determinant!=0)==predicted["nondegenerate"]
    return {"outside_vertices":n,"edges":len(edges),"exact_source_rank":len(basis),"exact_gram_determinant":str(determinant),"independent_exact_check":True,**predicted}


def cases():
    for n in (3,4,5,6,7,8,9,10,12):
        yield "clique-"+str(n),n,list(combinations(range(n),2))
    for left,right in ((1,7),(2,6),(3,5),(4,4),(3,6),(4,5),(6,6)):
        n=left+right
        yield f"bipartite-{left}-{right}",n,[(a,b) for a in range(left) for b in range(left,n)]
    yield "two-disjoint-cliques4",8,list(combinations(range(4),2))+list(combinations(range(4,8),2))
    yield "triangle-and-bipartite2-3",8,list(combinations(range(3),2))+[(a,b) for a in range(3,5) for b in range(5,8)]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    start=time.monotonic()
    started=datetime.now(timezone.utc).isoformat()
    rows=[]
    for name,n,edges in cases():
        rows.append({"case":name,**independent_check(n,edges)})
    result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),"wall_seconds":time.monotonic()-start,"status":"Exact source-span lemma; no improved multiplication bound asserted","formula":"rank-one nondegeneracy iff sum_(nonbipartite C)|C| + sum_(bipartite C)4*l_C*r_C/(l_C+r_C) !=8","rows":rows}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"output":args.output,"cases":len(rows),"wall_seconds":result["wall_seconds"],"degenerate_cases":[r["case"] for r in rows if not r["nondegenerate"]]},indent=2))


if __name__=="__main__":
    main()
