#!/usr/bin/env python3
"""Positive descendant-target frames for a fixed monotone triple DAG.

For a node with common source core C, let z be each core coordinate. Its
frame has total coordinate sum 3z, and is orthogonal to every descendant
physical output target. Since each target meets C once, the remaining pair
imposes x_a+x_b=0. A signed component decomposition describes this frame
exactly. It is positive under I-J/9, nests along DAG edges, and may permit a
different set of retained-controller chains from support envelopes.

The reference retained-controller algorithm is imported unchanged. Only its
frame-inclusion predicate is bound to this new, independently checked frame
family inside a process-local context; the original source file is unedited.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime,timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from finite_block_search import GroupUnion,install_reference,make_block_class
from finite_schedule_search import reordered
import frame_reuse


def bits(mask):
    while mask:
        bit=mask&-mask
        yield bit.bit_length()-1
        mask^=bit


@dataclass(frozen=True)
class TargetSpace:
    h:int
    core:int
    components:tuple[tuple[int,int],...]

    @property
    def common(self):
        return (self.core&-self.core).bit_length()-1

    @property
    def tags(self):
        return self.components

    @property
    def dimension(self):
        if self.core.bit_count()==3:
            assert not self.components
            return 1
        return len(self.components)

    @property
    def basis(self):
        # Each tuple encodes an integer vector: z on C, +scale on positive,
        # -scale on negative. For |C|<3, multiplying by 3-|C| avoids fractions.
        if self.core.bit_count()==3:
            return ((1,0,0,0),)
        scale=3-self.core.bit_count()
        return tuple((positive.bit_count()-negative.bit_count(),positive,negative,scale)
                     for positive,negative in self.components)

    @property
    def vertices(self):
        union=0
        has_z=False
        for z,positive,negative,_ in self.basis:
            union|=positive|negative
            has_z|=bool(z)
        return union|(self.core if has_z else 0)


def coordinate(frame,column,vertex):
    z,positive,negative,scale=column
    bit=1<<vertex
    if frame.core&bit:return z
    if positive&bit:return scale
    if negative&bit:return -scale
    return 0


def value_mask(frame,column,value):
    z,positive,negative,scale=column
    mask=0
    if z==value:mask|=frame.core
    if scale==value:mask|=positive
    if -scale==value:mask|=negative
    if value==0:mask|=((1<<frame.h)-1)&~(frame.core|positive|negative)
    return mask


@lru_cache(maxsize=500000)
def included(a:TargetSpace,b:TargetSpace):
    """Exact rational inclusion, by all defining equations of b."""
    assert a.h==b.h
    if a.vertices&~b.vertices:return False
    for column in a.basis:
        z=column[0]
        if b.core&~value_mask(a,column,z):return False
        for positive,negative in b.components:
            first=(positive&-positive).bit_length()-1
            value=coordinate(a,column,first)
            if positive&~value_mask(a,column,value):return False
            if negative&~value_mask(a,column,-value):return False
    return True


def signed_frame(h,core,edges,pairs):
    outside=((1<<h)-1)&~core
    parent=list(range(h))
    parity=[0]*h
    odd=[False]*h

    def find(v):
        if parent[v]!=v:
            previous=parent[v]
            parent[v],sign=find(previous)
            parity[v]^=sign
        return parent[v],parity[v]

    for index in bits(edges):
        a,b=pairs[index]
        assert outside&(1<<a) and outside&(1<<b)
        ra,pa=find(a)
        rb,pb=find(b)
        if ra==rb:
            if pa^pb!=1:odd[ra]=True
        else:
            parent[rb]=ra
            parity[rb]=pa^pb^1
            odd[ra]=odd[ra] or odd[rb]
    groups={}
    for vertex in bits(outside):
        root,sign=find(vertex)
        if odd[root]:continue
        if root not in groups:groups[root]=[0,0,sign]
        groups[root][sign^groups[root][2]]|=1<<vertex
    components=tuple(sorted(((positive,negative) for positive,negative,_ in groups.values()),
                            key=lambda component:(component[0]&-component[0]).bit_length()))
    if core.bit_count()==3:
        # Inputs see all omitted pairs outside their triple; an odd triangle
        # forces every outside coordinate to zero. Check this, do not assume it.
        assert not components, "Input frame must equal its original triple line"
    return TargetSpace(h,core,components)


def labels(circuit):
    h=circuit.h
    pairs=list(combinations(range(h),2))
    pair_ids={pair:index for index,pair in enumerate(pairs)}
    omitted={node:0 for node in circuit.active}
    output_common={}
    for (common,target),node in circuit.outputs.items():
        pair=tuple(vertex for vertex in target if vertex!=common)
        assert len(pair)==2
        omitted[node]|=1<<pair_ids[pair]
        output_common[(common,target)]=common
    for node in sorted(circuit.active,reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:omitted[child]|=omitted[node]
    values={}
    intern={}
    for node in sorted(circuit.active):
        core=circuit.core[node]
        assert core
        key=(core,omitted[node])
        frame=intern.get(key)
        if frame is None:
            frame=signed_frame(h,core,omitted[node],pairs)
            intern[key]=frame
        values[node]=frame
        if circuit.args[node]:
            assert all(included(values[child],frame) for child in circuit.args[node])
    for triple,node in circuit.variables.items():
        frame=values[node]
        assert frame.core==sum(1<<vertex for vertex in triple)
        assert frame.dimension==1 and frame.basis==((1,0,0,0),)
    pairings=0
    for (common,target),node in circuit.outputs.items():
        frame=values[node]
        assert sum(bool(frame.core&(1<<vertex)) for vertex in target)==1
        assert frame.core&(1<<common)
        for column in frame.basis:
            assert sum(coordinate(frame,column,vertex) for vertex in target)==column[0]
            pairings+=1
    return values,{"unique_target_descriptors":len(intern),
                   "unique_rational_frames":len(set(values.values())),
                   "source_triple_lines_checked":len(circuit.inputs),
                   "physical_target_pairings_checked":pairings,
                   "all_original_edges_nested":True,
                   "nondegeneracy":"q=sum(outside coordinates squared)+(size(C)-1)z^2; positive",
                   "frame_family":"E(C,[h]) intersect kernels of all descendant physical targets"}


def independent(circuit,frames,seed=109,pair_samples=1000):
    """Independent dense Q elimination checks source containment and inclusion."""
    import sympy as sp
    h=circuit.h
    unique=list(set(frames.values()))
    matrices={}
    for frame in unique:
        matrix=sp.Matrix(h,frame.dimension,lambda row,col:coordinate(frame,frame.basis[col],row))
        assert matrix.rank()==frame.dimension
        gram=9*matrix.T*matrix-(sp.ones(1,h)*matrix).T*(sp.ones(1,h)*matrix)
        assert all(gram[:size,:size].det()>0 for size in range(1,frame.dimension+1))
        matrices[frame]=matrix
    supports={}
    for node in sorted(circuit.active):
        supports[node]=(supports[circuit.args[node][0]]|supports[circuit.args[node][1]]) if circuit.args[node] else {node-1}
        frame=frames[node]
        for index in supports[node]:
            triple=circuit.inputs[index]
            column=sp.Matrix([int(vertex in triple) for vertex in range(h)])
            assert matrices[frame].row_join(column).rank()==frame.dimension
    rng=random.Random(seed)
    tested=set()
    for frame in unique:tested.add((frame,frame))
    for node in sorted(circuit.active):
        if circuit.args[node]:
            for child in circuit.args[node]:tested.add((frames[child],frames[node]))
    for _ in range(pair_samples):tested.add((rng.choice(unique),rng.choice(unique)))
    for a,b in tested:
        assert included(a,b)==(matrices[b].row_join(matrices[a]).rank()==b.dimension)
    return {"independent_positive_gram_checks":len(unique),
            "independent_source_span_checks":len(circuit.active),
            "independent_rational_inclusion_checks":len(tested),"seed":seed}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,nargs="+",default=[8,12])
    parser.add_argument("--base",type=int,default=4)
    parser.add_argument("--sizes",default="2")
    parser.add_argument("--combine",type=int,choices=[0,1,2],default=0)
    parser.add_argument("--modes",default="rank_id")
    parser.add_argument("--seeds",default="109")
    parser.add_argument("--independent",action="store_true")
    parser.add_argument("--dirty",action="store_true")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    install_reference(args.reference)
    block_class=make_block_class()
    sizes=tuple(map(int,args.sizes.split(",")))
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    for h in args.h:
        case_start=time.monotonic()
        circuit=GroupUnion(h,lambda n:block_class(n,sizes,args.base,args.combine),"paired")
        original=circuit.verify()
        frames,metadata=labels(circuit)
        print(json.dumps({"h":h,"phase":"labels",**metadata,"seconds":time.monotonic()-case_start}),flush=True)
        rational=independent(circuit,frames) if args.independent else {}
        for mode in args.modes.split(","):
            for seed in map(int,args.seeds.split(",")) if mode=="rank_random" else [0]:
                view,spaces,schedule_hash=reordered(circuit,frames,mode,seed)
                with patch.object(frame_reuse,"included",included):
                    compiled=frame_reuse.compile_reuse(view,spaces,frame_reuse.optimize_chains(view,spaces,"id"))
                    checked=frame_reuse.check(view,spaces,compiled)
                row={"h":h,"mode":mode,"seed":seed,"original":original,"original_roles":original["roles"],
                     "roles":compiled["roles"],"chains":compiled["chain_summary"],"checked":checked,
                     "frames":metadata,"independent":rational,"schedule_sha256":schedule_hash,
                     "elapsed_seconds":time.monotonic()-case_start}
                if args.dirty:
                    from dag_network import exact_invocation
                    from frame_reuse_certificate import program
                    scalar=program(view,compiled)
                    row["dirty_input_basis_checks"]=[exact_invocation(h,inverse,scalar) for inverse in (False,True)]
                rows.append(row)
                import numpy,scipy
                result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),
                        "wall_seconds":time.monotonic()-start,"settings":vars(args),"rows":rows,
                        "reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2",
                        "runtime":{"python":sys.version,"numpy":numpy.__version__,"scipy":scipy.__version__},
                        "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("finite_target_frames.py","finite_schedule_search.py","finite_block_search.py","frame_reuse.py")},
                        "scope":"Exact finite positive target-frame/compiler witness; full three-stage transfer not claimed"}
                output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
                print(json.dumps(row),flush=True)
        included.cache_clear()
        GroupUnion.support_in.cache_clear()
    print(json.dumps({"output":str(output),"cases":len(rows),"wall_seconds":time.monotonic()-start}),flush=True)


if __name__=="__main__":
    main()
