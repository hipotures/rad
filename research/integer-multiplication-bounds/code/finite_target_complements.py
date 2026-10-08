#!/usr/bin/env python3
"""Nondegenerate complements of exact descendant physical target spans.

This bounded dense implementation checks a new indefinite frame family.
At a degenerate target-span node, and every original ancestor of that node,
it falls back to the positive original support envelope. A suppressed parent
therefore always has suppressed children. Unsuppressed target kernels nest
by reverse target-span inclusion. Source frames are explicitly triple lines.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime,timezone
from functools import lru_cache
from hashlib import sha256
from math import gcd,lcm
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from finite_block_search import GroupUnion,install_reference,make_block_class
from finite_schedule_search import reordered
from finite_target_frames import TargetSpace,coordinate,bits
import frame_reuse


def primitive(column):
    denominator=lcm(*(int(value.q) for value in column))
    values=[int(value*denominator) for value in column]
    common=gcd(*values)
    assert common
    values=[value//common for value in values]
    if next(value for value in values if value)<0:values=[-value for value in values]
    return tuple(values)


@dataclass(frozen=True)
class RationalFrame:
    h:int
    basis:tuple[tuple[int,...],...]
    constraints:tuple[tuple[int,...],...]
    core:int

    @property
    def dimension(self):return len(self.basis)

    @property
    def common(self):return (self.core&-self.core).bit_length()-1

    @property
    def tags(self):return self.constraints


@lru_cache(maxsize=100000)
def included(a,b):
    assert a.h==b.h
    return all(sum(x*y for x,y in zip(column,row))==0 for column in a.basis for row in b.constraints)


def matrix_of(frame):
    import sympy as sp
    return sp.Matrix(frame.h,frame.dimension,lambda row,col:frame.basis[col][row])


def gram(matrix):
    import sympy as sp
    sums=sp.ones(1,matrix.rows)*matrix
    return 9*matrix.T*matrix-sums.T*sums


def inertia(matrix):
    """Exact rational symmetric elimination, allowing 2x2 indefinite pivots."""
    import sympy as sp
    matrix=sp.Matrix(matrix)
    positive=negative=zero=0
    while matrix.rows:
        n=matrix.rows
        pivot=next((index for index in range(n) if matrix[index,index]),None)
        if pivot is not None:
            order=[pivot]+[index for index in range(n) if index!=pivot]
            matrix=matrix.extract(order,order)
            value=matrix[0,0]
            positive+=int(bool(value>0))
            negative+=int(bool(value<0))
            matrix=matrix[1:,1:]-matrix[1:,:1]*matrix[:1,1:]/value
            continue
        pair=next(((a,b) for a in range(n) for b in range(a+1,n) if matrix[a,b]),None)
        if pair is None:
            zero+=n
            break
        a,b=pair
        order=[a,b]+[index for index in range(n) if index not in pair]
        matrix=matrix.extract(order,order)
        positive+=1
        negative+=1
        matrix=matrix[2:,2:]-matrix[2:,:2]*matrix[:2,:2].inv()*matrix[:2,2:]
    return int(positive),int(negative),int(zero)


def frame_from_basis(h,basis,core):
    import sympy as sp
    columns=tuple(primitive(column) for column in basis)
    matrix=sp.Matrix(h,len(columns),lambda row,col:columns[col][row])
    assert matrix.rank()==len(columns)
    constraints=tuple(primitive(row) for row in matrix.T.nullspace())
    form=gram(matrix)
    signature=inertia(form)
    assert signature[2]==0
    return RationalFrame(h,columns,constraints,core),signature


def labels(circuit):
    import sympy as sp
    h=circuit.h
    ambient=9*sp.eye(h)-sp.ones(h)
    assert ambient.det()!=0 and h!=9
    descendants={node:0 for node in circuit.active}
    for (common,target),node in circuit.outputs.items():
        descendants[node]|=1<<(circuit.variables[target]-1)
    for node in sorted(circuit.active,reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:descendants[child]|=descendants[node]
    cached={}
    kernel={}
    degenerate=set()
    nonline_sources=set()
    for node in sorted(circuit.active):
        mask=descendants[node]
        assert mask
        if mask not in cached:
            targets=[circuit.inputs[index] for index in bits(mask)]
            matrix=sp.Matrix(h,len(targets),lambda row,col:int(row in targets[col]))
            target_basis=matrix.columnspace()
            target_matrix=sp.Matrix.hstack(*target_basis)
            target_signature=inertia(gram(target_matrix))
            if target_signature[2]:cached[mask]=(None,target_signature)
            else:
                nullspace=(target_matrix.T*ambient).nullspace()
                frame,signature=frame_from_basis(h,nullspace,0)
                cached[mask]=(frame,target_signature)
        frame,target_signature=cached[mask]
        if frame is None:degenerate.add(node)
        else:
            frame=RationalFrame(h,frame.basis,frame.constraints,circuit.core[node])
            kernel[node]=frame
            if circuit.args[node] is None:
                triple=circuit.inputs[node-1]
                expected=tuple(int(vertex in triple) for vertex in range(h))
                if frame.dimension!=1 or frame.basis[0]!=expected:nonline_sources.add(node)
    suppressed=set(degenerate|nonline_sources)
    stack=list(suppressed)
    while stack:
        node=stack.pop()
        if circuit.args[node]:
            for child in circuit.args[node]:
                if child not in suppressed:
                    suppressed.add(child)
                    stack.append(child)
    frames={}
    positive=indefinite=0
    fallback_cache={}
    for node in sorted(circuit.active):
        if node in suppressed:
            core,vertices=circuit.core[node],circuit.union[node]
            key=(core,vertices)
            if key not in fallback_cache:
                descriptor=TargetSpace(h,core,tuple((1<<v,0) for v in bits(vertices&~core)))
                columns=[sp.Matrix([coordinate(descriptor,column,v) for v in range(h)]) for column in descriptor.basis]
                fallback_cache[key]=frame_from_basis(h,columns,core)
            frame,signature=fallback_cache[key]
        else:
            frame=kernel[node]
            signature=inertia(gram(matrix_of(frame)))
        frames[node]=frame
        positive+=signature[1]==0
        indefinite+=signature[1]>0
        if circuit.args[node]:
            assert all(included(frames[child],frame) for child in circuit.args[node])
            if node in suppressed:assert all(child in suppressed for child in circuit.args[node])
    for triple,node in circuit.variables.items():
        expected=tuple(int(vertex in triple) for vertex in range(h))
        assert frames[node].dimension==1 and frames[node].basis==(expected,)
    pairings=0
    for (common,target),node in circuit.outputs.items():
        for column in frames[node].basis:
            assert 3*sum(column[vertex] for vertex in target)==sum(column)
            pairings+=1
    return frames,{"unique_target_span_descriptors":len(cached),"initial_degenerate_target_nodes":len(degenerate),
                   "input_nonlinear_kernel_nodes":len(nonline_sources),"suppressed_original_ancestors":len(suppressed),
                   "positive_frame_nodes":int(positive),"indefinite_nondegenerate_frame_nodes":int(indefinite),
                   "all_original_edges_nested":True,"source_triple_lines_checked":len(circuit.inputs),
                   "physical_target_pairings_checked":pairings,"ambient_H_nondegenerate":True,
                   "frame_family":"Exact descendant target-span complements with positive ancestor suppression"}


def independent(circuit,frames,seed=109,samples=500):
    import sympy as sp
    h=circuit.h
    ambient=9*sp.eye(h)-sp.ones(h)
    unique=list(set(frames.values()))
    matrices={frame:matrix_of(frame) for frame in unique}
    complements={frame:sp.Matrix.hstack(*(matrices[frame].T*ambient).nullspace()) for frame in unique}
    rng=random.Random(seed)
    pairs=set()
    for node in sorted(circuit.active):
        if circuit.args[node]:
            for child in circuit.args[node]:pairs.add((frames[child],frames[node]))
    for _ in range(samples):pairs.add((rng.choice(unique),rng.choice(unique)))
    for a,b in pairs:
        value=matrices[b].row_join(matrices[a]).rank()==b.dimension
        assert included(a,b)==value
        assert value==(complements[a].row_join(complements[b]).rank()==complements[a].cols)
    nested=[pair for pair in pairs if included(*pair)]
    rng.shuffle(nested)
    for a,b in nested[:50]:
        A,B=matrices[a],matrices[b]
        pa=A*(A.T*ambient*A).inv()*A.T*ambient
        pb=B*(B.T*ambient*B).inv()*B.T*ambient
        residual=pb-pa
        assert residual.rank()==b.dimension-a.dimension
        assert residual*residual==residual
    return {"independent_dense_inclusion_and_reverse_complement_checks":len(pairs),
            "indefinite_projector_rank_and_idempotence_checks":min(50,len(nested)),"seed":seed}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",nargs="+",type=int,default=[6,8,12])
    parser.add_argument("--base",type=int,default=4)
    parser.add_argument("--independent",action="store_true")
    parser.add_argument("--dirty",action="store_true")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    install_reference(args.reference)
    cls=make_block_class()
    start=time.monotonic()
    started=datetime.now(timezone.utc).isoformat()
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    for h in args.h:
        case_start=time.monotonic()
        circuit=GroupUnion(h,lambda n:cls(n,(2,),args.base,0),"paired")
        original=circuit.verify()
        frames,metadata=labels(circuit)
        print(json.dumps({"h":h,"phase":"labels",**metadata,"seconds":time.monotonic()-case_start}),flush=True)
        extra=independent(circuit,frames) if args.independent else {}
        view,spaces,schedule_hash=reordered(circuit,frames,"rank_id",109)
        with patch.object(frame_reuse,"included",included):
            compiled=frame_reuse.compile_reuse(view,spaces,frame_reuse.optimize_chains(view,spaces,"id"))
            checked=frame_reuse.check(view,spaces,compiled)
        row={"h":h,"original":original,"roles":compiled["roles"],"chains":compiled["chain_summary"],
             "checked":checked,"frames":metadata,"independent":extra,"schedule_sha256":schedule_hash,
             "elapsed_seconds":time.monotonic()-case_start}
        if args.dirty:
            from dag_network import exact_invocation
            from frame_reuse_certificate import program
            scalar=program(view,compiled)
            row["dirty_input_basis_checks"]=[exact_invocation(h,inverse,scalar) for inverse in (False,True)]
        rows.append(row)
        result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),
                "wall_seconds":time.monotonic()-start,"settings":vars(args),"rows":rows,
                "reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2",
                "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("finite_target_complements.py","finite_schedule_search.py","finite_block_search.py","frame_reuse.py")},
                "scope":"Exact bounded indefinite frame/compiler study; full h50 transfer not claimed"}
        output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps(row),flush=True)
        included.cache_clear()
        GroupUnion.support_in.cache_clear()
    print(json.dumps({"output":str(output),"cases":len(rows),"wall_seconds":time.monotonic()-start}),flush=True)


if __name__=="__main__":main()
