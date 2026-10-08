#!/usr/bin/env python3
"""Adapt positive envelopes and nondegenerate one-common target complements.

Only nodes whose descendant physical targets share one designated common
point have a wide alternative. Their exact target span T is positive, so
T-perp is nondegenerate and has one negative direction for h>9. Inclusion
uses exact rational target spans, not positivity assumptions about T-perp.
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
import time
from unittest.mock import patch

from finite_block_search import GroupUnion,install_reference
from finite_singleton_search import singleton_class
from finite_schedule_search import reordered
from finite_adaptive_cores import required_cores
from finite_fast_target_frames import signed_frame
from finite_target_frames import bits
from finite_label_milp import solve
from frame_envelope import labels as envelope_labels
import frame_reuse


@dataclass(frozen=True)
class Complement:
    h:int
    target_span:frame_reuse.Space

    @property
    def dimension(self):return self.h-self.target_span.dimension

    @property
    def common(self):return self.target_span.common

    @property
    def tags(self):return self.target_span.tags


def target_span(h,common,edges,pairs):
    constraints=signed_frame(h,1<<common,edges,pairs)
    nonodd=0
    for positive,negative in constraints.components:nonodd|=positive|negative
    full=[v for v in range(h) if v!=common and not nonodd&(1<<v)]
    generators=[]
    def edge(a,b):generators.append((1<<common)|(1<<a)|(1<<b))
    if full:
        assert len(full)>=3
        edge(full[0],full[1]);edge(full[1],full[2]);edge(full[0],full[2])
        for v in full[3:]:edge(full[0],v)
    for positive,negative in constraints.components:
        if not negative:continue
        pos=list(bits(positive));neg=list(bits(negative))
        edge(pos[0],neg[0])
        for v in neg[1:]:edge(pos[0],v)
        for v in pos[1:]:edge(v,neg[0])
    assert generators
    result=frame_reuse.space_of(generators,common,h)
    assert result.core&(1<<common)
    return result


@lru_cache(maxsize=500000)
def orthogonal_envelope_to_targets(envelope,targets):
    core,vertices=envelope.core,envelope.vertices
    outside=vertices&~core;k=core.bit_count();size=outside.bit_count()
    if k==1:
        assert size>=3
        return not outside&targets.vertices and not core&~targets.core
    if size>3 and outside&targets.vertices:return False
    for triple in targets.basis:
        m=(core&triple).bit_count();n=(outside&triple).bit_count()
        if size==0:
            if m!=1:return False
        elif n not in (0,size) or m*size+(3-k)*n!=size:return False
    return True


@lru_cache(maxsize=500000)
def included(a,b):
    if isinstance(a,Complement):
        if not isinstance(b,Complement):
            # T is positive and ambient H has one negative eigenvalue for h>9,
            # so T-perp has a negative direction and cannot lie in positive E.
            assert a.h>9
            return False
        assert a.h==b.h
        return frame_reuse_included(b.target_span,a.target_span)
    if isinstance(b,Complement):return orthogonal_envelope_to_targets(a,b.target_span)
    return frame_reuse_included(a,b)


frame_reuse_included=frame_reuse.included


def alternatives(circuit):
    h=circuit.h;assert h>9
    narrow,metadata=envelope_labels(circuit,True)
    required=required_cores(circuit)
    pairs=list(combinations(range(h),2));pair_ids={pair:i for i,pair in enumerate(pairs)}
    omitted={n:0 for n in circuit.active}
    for (common,target),node in circuit.outputs.items():
        pair=tuple(v for v in target if v!=common)
        omitted[node]|=1<<pair_ids[pair]
    for node in sorted(circuit.active,reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:omitted[child]|=omitted[node]
    intern={};targets={};choices={}
    for node in sorted(circuit.active):
        if required[node].bit_count()==1:
            common=(required[node]&-required[node]).bit_length()-1
            key=common,omitted[node]
            if key not in intern:intern[key]=target_span(h,common,omitted[node],pairs)
            span=intern[key];targets[node]=span
            wide=Complement(h,span)
            assert included(narrow[node],wide)
        else:wide=narrow[node]
        choices[node]=narrow[node],wide
    for node in sorted(circuit.active):
        if circuit.args[node]:
            for child in circuit.args[node]:
                assert included(choices[child][0],choices[node][0])
                assert included(choices[child][0],choices[node][1])
                assert included(choices[child][1],choices[node][1])
        else:assert choices[node][0]==choices[node][1] and narrow[node].dimension==1
    return choices,targets,omitted,pairs,dict(metadata,unique_target_descriptors=len(intern),
        wide_alternative_nodes=len(targets),ambient_H_nondegenerate=True,
        nondegeneracy="Positive common-point target spans T; U=T-perp nondegenerate with one negative direction for h>9")


def target_check(circuit,frames):
    checked=0
    for (common,target),node in circuit.outputs.items():
        mask=sum(1<<v for v in target);frame=frames[node]
        if isinstance(frame,Complement):
            span=frame_reuse.space_of([mask],common,circuit.h)
            assert frame_reuse_included(span,frame.target_span)
        else:assert all((triple&mask).bit_count()==1 for triple in frame.basis)
        checked+=1
    return dict(all_designated_physical_targets_orthogonal=True,partial_output_frames_checked=checked)


def independent(circuit,choices,targets,omitted,pairs,seed=109):
    import sympy as sp
    from finite_target_complements import inertia
    h=circuit.h;H=9*sp.eye(h)-sp.ones(h)
    assert H.det()!=0
    def columns(frame):
        if isinstance(frame,Complement):
            T=columns(frame.target_span)
            return sp.Matrix.hstack(*(T.T*H).nullspace())
        return sp.Matrix(h,frame.dimension,lambda row,col:(frame.basis[col]>>row)&1)
    unique=list({frame for alternatives in choices.values() for frame in alternatives})
    matrices={frame:columns(frame) for frame in unique}
    for frame,matrix in matrices.items():
        signature=inertia(matrix.T*H*matrix)
        assert signature[2]==0 and matrix.rank()==frame.dimension
        assert signature[1]==int(isinstance(frame,Complement))
    span_checks=0
    for node,span in targets.items():
        common=span.common
        triples=[(1<<common)|(1<<a)|(1<<b) for index in bits(omitted[node]) for a,b in (pairs[index],)]
        actual=sp.Matrix(h,len(triples),lambda row,col:(triples[col]>>row)&1)
        assert actual.rank()==span.dimension and matrices[Complement(h,span)].cols==h-span.dimension
        canonical=columns(span)
        assert actual.row_join(canonical).rank()==span.dimension
        span_checks+=1
    rng=random.Random(seed);tested=set()
    for node in circuit.active:
        if circuit.args[node]:
            for child in circuit.args[node]:
                tested.add((choices[child][0],choices[node][0]))
                tested.add((choices[child][0],choices[node][1]))
                tested.add((choices[child][1],choices[node][1]))
    for _ in range(1000):tested.add((rng.choice(unique),rng.choice(unique)))
    for a,b in tested:
        assert included(a,b)==(matrices[b].row_join(matrices[a]).rank()==b.dimension)
    return dict(independent_nondegenerate_frame_gram_checks=len(unique),
        exact_original_descendant_target_span_checks=span_checks,
        independent_rational_inclusion_checks=len(tested),seed=seed)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,nargs="+",default=[12])
    parser.add_argument("--gap",type=int)
    parser.add_argument("--schedule",choices=["wide_rank","narrow_rank","id"],default="wide_rank")
    parser.add_argument("--time-limit",type=float,default=60)
    parser.add_argument("--dirty",action="store_true")
    parser.add_argument("--independent",action="store_true")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();install_reference(args.reference)
    assert not args.output.exists(),"Use a fresh output path"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat();begin=time.monotonic()
    source_names=("finite_adaptive_complements.py","finite_label_milp.py","finite_adaptive_cores.py",
        "finite_singleton_search.py","finite_block_search.py","finite_fast_target_frames.py",
        "finite_target_frames.py","frame_envelope.py","frame_reuse.py","finite_schedule_search.py")
    source={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in source_names}
    rows=[]
    for h in args.h:
        start=time.monotonic();gap=h//2-1 if args.gap is None else args.gap
        cls=singleton_class();positions=[gap if c//2<=gap else gap+1 for c in range(h)]
        circuit=GroupUnion(h,lambda n,common:cls(n,positions[common],4),"paired",0,True)
        graph=circuit.verify();choices,targets,omitted,pairs,metadata=alternatives(circuit)
        print(json.dumps(dict(h=h,phase="labels",**metadata,seconds=time.monotonic()-start)),flush=True)
        extra=independent(circuit,choices,targets,omitted,pairs) if args.independent else {}
        sorter={n:frames[int(args.schedule=="wide_rank")] for n,frames in choices.items()}
        view,_,schedule_sha=reordered(circuit,sorter,"id" if args.schedule=="id" else "rank_id",109)
        # reordered preserves source IDs; reconstruct its original-node map from
        # output-independent DAG pairs using the same deterministic schedule.
        if args.schedule=="id":order=sorted(circuit.active)
        else:order=sorted(circuit.active,key=lambda n:(sorter[n].dimension,n))
        mapping={old:new for new,old in enumerate(order,1)}
        assert all(view.args[mapping[n]]==tuple(mapping[c] for c in circuit.args[n]) for n in circuit.active if circuit.args[n])
        view_choices={mapping[n]:frames for n,frames in choices.items()}
        frames,plan,milp=solve(view,view_choices,included,args.time_limit)
        with patch.object(frame_reuse,"included",included):
            code=frame_reuse.compile_reuse(view,frames,plan);checked=frame_reuse.check(view,frames,code)
            optimized=frame_reuse.compile_reuse(view,frames,frame_reuse.optimize_chains(view,frames,"id"))
            checked_maxflow=frame_reuse.check(view,frames,optimized)
        assert optimized["roles"]<=code["roles"]
        if milp["solver_reported_optimal"]:assert optimized["roles"]==code["roles"]
        row=dict(h=h,gap=gap,positions=positions,graph=graph,roles=optimized["roles"],milp_roles=code["roles"],
            frame_metadata=metadata,milp=milp,checked=checked,maxflow_checked=checked_maxflow,
            physical_targets=target_check(view,frames),independent=extra,schedule_sha256=schedule_sha,
            chosen_original_node_ids=[order[n-1] for n in milp["selected_relevant_wide_nodes"]])
        if args.dirty:
            from dag_network import exact_invocation
            from frame_reuse_certificate import program
            row["dirty_basis"]=[exact_invocation(h,inverse,program(view,optimized)) for inverse in (False,True)]
        row["elapsed_seconds"]=time.monotonic()-start;rows.append(row)
        import numpy,scipy
        result=dict(settings={**vars(args),"output":str(args.output)},started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-begin,
            source_sha256=source,reference_commit="bcd4ebde8692383539f8a48734e5fbf3a18a32c2",rows=rows,
            runtime=dict(numpy=numpy.__version__,scipy=scipy.__version__),
            scope="Recovered exact positive/indefinite finite frame witness; solver optimality reported only; generic nondegenerate projector transfer and analytic promotion remain separate")
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps(dict(h=h,roles=row["roles"],wide=milp["propagated_wide_nodes"],
            solver_optimal=milp["solver_reported_optimal"],seconds=row["elapsed_seconds"])),flush=True)
        included.cache_clear();orthogonal_envelope_to_targets.cache_clear()
        frame_reuse_included.cache_clear();GroupUnion.support_in.cache_clear()


if __name__=="__main__":main()
