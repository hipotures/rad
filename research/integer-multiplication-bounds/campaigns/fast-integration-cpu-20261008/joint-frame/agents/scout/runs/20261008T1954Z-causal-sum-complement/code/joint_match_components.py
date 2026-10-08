#!/usr/bin/env python3
"""Inspect actual joint-frame linear/partition matroid components.

The component partition includes every edge at a block because its retained
coordinate rows share a linear independence constraint modulo the requested
output span. A source-index/use graph omitting that coupling is insufficient.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time


def load_source(root):
    sys.dont_write_bytecode=True
    directory=root/'scripts/experiments';sys.path.insert(0,str(directory))
    import binary_frame_compiler as compiler
    import joint_dual_compiler as producer
    compiler.graph=producer.producer.graph
    return compiler


def components(blocks,uses):
    parent=list(range(len(blocks)+len(uses)))
    def find(x):
        while x!=parent[x]:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(x,y):parent[find(x)]=find(y)
    edges=[]
    for g,b in enumerate(blocks):
        for u,i in b['candidates']:
            edges.append((g,u,i));union(g,len(blocks)+u)
    groups={}
    for e,(g,u,i) in enumerate(edges):groups.setdefault(find(g),[]).append(e)
    return edges,list(groups.values())


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args();assert __debug__ and not args.output.exists()
    args.output.parent.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    compiler=load_source(args.source_root.resolve())
    c,blocks,uses,value_uses,owner,signal,order,contains=compiler.build(args.h)
    edges,groups=components(blocks,uses)
    edge_hist=Counter(len(group) for group in groups)
    stats=[]
    for group in groups:
        bs={edges[e][0] for e in group};us={edges[e][1] for e in group}
        stats.append(dict(edges=len(group),blocks=len(bs),uses=len(us),
            linear_capacity=sum(len(blocks[g]['inputs'])-len(blocks[g]['outbasis']) for g in bs)))
    baseline,chosen,right,matching=compiler.match(blocks,uses,True)
    assert baseline==edges
    identity=('\n'.join('%d %d %d'%edges[e] for e in sorted(chosen))+'\n').encode()
    result=dict(status='ACTUAL JOINT LINEAR/PARTITION COMPONENT INVENTORY',h=args.h,
        source_root=str(args.source_root),compiler_sha256=sha256((args.source_root/'scripts/experiments/binary_frame_compiler.py').read_bytes()).hexdigest(),
        scalar_source_sha256=sha256((args.source_root/'references/frame-compiler/pr55/research/skip-suffix/skip_graph.py').read_bytes()).hexdigest(),
        edges=len(edges),components=len(groups),edge_count_histogram=dict(sorted(edge_hist.items())),
        component_summaries=sorted(stats,key=lambda s:s['edges'],reverse=True),
        source_regions=len(blocks),uses=len(uses),baseline_chosen=len(chosen),
        baseline_exact_edge_stream_sha256=sha256(identity).hexdigest(),
        matched_by_component=Counter(sum(e in chosen for e in group) for group in groups),
        seconds=time.monotonic()-start,recorded_utc=datetime.now(timezone.utc).isoformat(),
        scope='Exact decomposition of the actual joint-frame matching constraints. Costs remain a separate objective; no complete-moment improvement or optimality claim follows from this inventory.')
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','h','edges','components','baseline_chosen','seconds']}),flush=True)
    print(json.dumps(result['component_summaries'][:5]),flush=True)


if __name__=='__main__':main()
