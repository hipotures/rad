#!/usr/bin/env python3
"""Joint positive-envelope core choices and retained-controller MILP.

For an unshared pair-star, choose E(C,V) or E(A,V), where A is the
designated descendant common-point set. Wide children force optional wide
parents. A fixed support/core schedule orders every possible strict inclusion.
The MILP jointly chooses binary cores and controller links; all recovered
choices and links are audited with integer constraints and the old compiler.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime,timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import time
from types import SimpleNamespace

from finite_block_search import GroupUnion,install_reference,make_block_class
from finite_singleton_search import singleton_class
from frame_envelope import target_check
from frame_reuse import space_of,included,optimize_chains,compile_reuse,check


def envelope(core,vertices,h):
    common=(core&-core).bit_length()-1
    outside=[v for v in range(h) if vertices&~core&(1<<v)]
    if core.bit_count()==3:
        assert vertices==core
        generators=[core]
    elif core.bit_count()==2:
        generators=[core|(1<<v) for v in outside]
    else:
        assert core.bit_count()==1 and len(outside)>=3
        edges=[(outside[0],outside[1]),(outside[1],outside[2]),(outside[0],outside[2])]
        edges.extend((outside[0],v) for v in outside[3:])
        generators=[core|(1<<a)|(1<<b) for a,b in edges]
    frame=space_of(generators,common,h)
    assert frame.core==core and frame.vertices==vertices
    return frame


def relabel(circuit):
    """Input-preserving legal schedule independent of optional frame choices."""
    p=len(circuit.inputs)
    order=list(range(1,p+1))+sorted((n for n in circuit.active if circuit.args[n]),
        key=lambda n:(circuit.union[n].bit_count(),-circuit.core[n].bit_count(),n))
    mapping={old:new for new,old in enumerate(order,1)}
    args=[None]*(p+1)
    for old in order[p:]:
        children=tuple(mapping[child] for child in circuit.args[old])
        assert all(child<len(args) for child in children)
        args.append(children)
    view=SimpleNamespace(h=circuit.h,inputs=circuit.inputs,variables={t:mapping[n] for t,n in circuit.variables.items()},
        outputs={t:mapping[n] for t,n in circuit.outputs.items()},active=set(range(1,len(args))),args=args,
        additions=circuit.additions,core={mapping[n]:circuit.core[n] for n in circuit.active},
        union={mapping[n]:circuit.union[n] for n in circuit.active})
    return view,order,sha256(json.dumps(order,separators=(",", ":")).encode()).hexdigest()


def required_cores(circuit):
    required={node:0 for node in circuit.active}
    for (common,target),node in circuit.outputs.items():required[node]|=1<<common
    for node in sorted(circuit.active,reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:required[child]|=required[node]
    for node in circuit.active:assert required[node] and not required[node]&~circuit.core[node]
    return required


def candidate_links(circuit,required):
    users={node:[] for node in circuit.active}
    descriptions=[]
    for node in sorted(circuit.active):
        if circuit.args[node]:
            for position,child in enumerate(circuit.args[node]):
                user=len(descriptions); descriptions.append((child,node,position)); users[child].append(user)
    for target,node in sorted(circuit.outputs.items()):
        user=len(descriptions); descriptions.append((node,None,target)); users[node].append(user)
    optional={n for n in circuit.active if circuit.core[n]!=required[n]}
    relevant=set(); candidates=[]
    for node,outgoing in users.items():
        for index,first in enumerate(outgoing):
            previous=descriptions[first][1]
            if previous is None:continue
            for second in outgoing[index+1:]:
                following=descriptions[second][1]
                following=following if following is not None else node
                if circuit.union[previous]&~circuit.union[following]:continue
                values={}
                for a,b in product((0,1) if previous in optional else (0,),
                                   (0,1) if following in optional else (0,)):
                    ca=required[previous] if a else circuit.core[previous]
                    cb=required[following] if b else circuit.core[following]
                    values[a,b]=not cb&~ca
                if not any(values.values()):continue
                need_a=previous in optional and any(values[0,b]!=values[1,b] for b in ((0,1) if following in optional else (0,)))
                need_b=following in optional and any(values[a,0]!=values[a,1] for a in ((0,1) if previous in optional else (0,)))
                flags=[]
                if need_a:flags.append(previous); relevant.add(previous)
                if need_b:flags.append(following); relevant.add(following)
                forbidden=[]
                for choices in product((0,1),repeat=len(flags)):
                    assignment=dict(zip(flags,choices))
                    if not values[assignment.get(previous,0),assignment.get(following,0)]:forbidden.append(choices)
                candidates.append((first,second,tuple(flags),tuple(forbidden)))
    return users,descriptions,candidates,optional,relevant


def nesting_links(circuit,optional,relevant):
    """Eliminate latent binary choices using nearest relevant ancestry."""
    frontier={}; pairs=set()
    for node in sorted(circuit.active):
        if node not in optional:continue
        below=set()
        for child in circuit.args[node] or ():
            if child in optional:below.update(frontier[child])
        if node in relevant:
            pairs.update((child,node) for child in below)
            frontier[node]={node}
        else:frontier[node]=below
    return sorted(pairs)


def solve(circuit,required,time_limit):
    import numpy as np
    from scipy.optimize import Bounds,LinearConstraint,milp
    from scipy.sparse import coo_array
    users,descriptions,candidates,optional,relevant=candidate_links(circuit,required)
    relevant=sorted(relevant)
    flags={node:i for i,node in enumerate(relevant)}
    offset=len(flags); count=offset+len(candidates)
    rows=[];cols=[];data=[];upper=[];integer_constraints=[]
    def add(coefficients,rhs):
        row=len(upper);upper.append(rhs);integer_constraints.append((tuple(coefficients.items()),rhs))
        for column,value in coefficients.items():rows.append(row);cols.append(column);data.append(value)
    nesting=nesting_links(circuit,optional,set(relevant))
    for child,parent in nesting:add({flags[child]:1,flags[parent]:-1},0)
    by_gate=defaultdict(list);by_second=defaultdict(list)
    for index,(first,second,nodes,forbidden) in enumerate(candidates):
        y=offset+index
        by_gate[descriptions[first][1]].append(y);by_second[second].append(y)
        for choices in forbidden:
            coefficients={y:1};zeros=0
            for node,choice in zip(nodes,choices):
                coefficients[flags[node]]=1 if choice else -1
                zeros+=not choice
            add(coefficients,len(nodes)-zeros)
    for indices in by_gate.values():add({i:1 for i in indices},1)
    for indices in by_second.values():add({i:1 for i in indices},1)
    matrix=coo_array((np.asarray(data,dtype=float),(np.asarray(rows,dtype=np.int32),np.asarray(cols,dtype=np.int32))),shape=(len(upper),count)).tocsc()
    matrix.indices=matrix.indices.astype(np.int32);matrix.indptr=matrix.indptr.astype(np.int32)
    objective=np.zeros(count);objective[offset:]=-1
    begin=time.monotonic()
    solution=milp(objective,integrality=np.ones(count,dtype=np.uint8),bounds=Bounds(np.zeros(count),np.ones(count)),
        constraints=LinearConstraint(matrix,np.full(len(upper),-np.inf),np.asarray(upper,dtype=float)),
        options={"time_limit":time_limit,"mip_rel_gap":0,"threads":1})
    assert solution.x is not None,solution.message
    integer=np.rint(solution.x).astype(np.int8)
    assert np.max(np.abs(solution.x-integer))<1e-6
    assert all(sum(int(integer[i])*value for i,value in coefficients)<=rhs for coefficients,rhs in integer_constraints)
    chosen={node:int(integer[index]) for node,index in flags.items()}
    wide=set()
    for node in sorted(circuit.active):
        if node in optional:
            use=chosen.get(node,0) or any(child in wide for child in circuit.args[node] or ())
            if node in chosen:assert use==chosen[node]
            if use:wide.add(node)
    frames={};intern={}
    for node in sorted(circuit.active):
        core=required[node] if node in wide else circuit.core[node]
        key=core,circuit.union[node]
        if key not in intern:intern[key]=envelope(*key,circuit.h)
        frames[node]=intern[key]
        if circuit.args[node]:assert all(included(frames[child],frames[node]) for child in circuit.args[node])
        else:assert frames[node].basis==(circuit.core[node],) and frames[node].dimension==1
    outgoing={};incoming={};retained={}
    for index,(first,second,nodes,forbidden) in enumerate(candidates):
        if integer[offset+index]:
            node,previous,_=descriptions[first];node2,following,_=descriptions[second]
            assert node==node2 and first<second and previous is not None
            assert included(frames[previous],frames[following if following is not None else node])
            assert first not in outgoing and second not in incoming
            outgoing[first]=second;incoming[second]=first
            retained[previous]=retained.get(previous,0)+1;assert retained[previous]<=1
    summary={"schedule":"id","selected_links":len(outgoing),"candidate_links":len(candidates),
             "scope":"Joint binary common-core choice and retained-controller MILP under fixed legal support schedule"}
    plan=users,descriptions,outgoing,incoming,summary
    metadata=dict(optional_nodes=len(optional),relevant_core_variables=len(flags),nesting_constraints=len(nesting),
        candidate_links=len(candidates),milp_variables=count,milp_constraints=len(upper),
        solver_status=int(solution.status),solver_message=solution.message,solver_optimal=solution.status==0,
        solver_gap=float(solution.mip_gap) if solution.mip_gap is not None else None,
        solver_dual_bound=float(solution.mip_dual_bound) if solution.mip_dual_bound is not None else None,
        selected_links=len(outgoing),solver_seconds=time.monotonic()-begin,
        selected_relevant_wide_nodes=[node for node,value in chosen.items() if value],
        propagated_wide_nodes=len(wide),selected_link_user_pairs=sorted(outgoing.items()),
        exact_integer_constraints_passed=len(integer_constraints),frame_family="Positive E(K,V), K selected from source core C or required descendant common set A")
    return frames,plan,metadata


def independent(circuit,frames):
    from review_envelopes import constraint_basis,rational_inclusion
    from review_frame_reuse import vector
    from review_rational_frames import analyze
    cached=set()
    for node in sorted(circuit.active):
        frame=frames[node];key=frame.core,frame.vertices
        if key not in cached:
            rows=constraint_basis(*key,circuit.h);actual=[vector(t,circuit.h) for t in frame.basis]
            assert rational_inclusion(rows,actual) and rational_inclusion(actual,rows)
            assert analyze(rows)["signature"]=="positive"
            cached.add(key)
        if circuit.args[node]:
            for child in circuit.args[node]:
                assert rational_inclusion([vector(t,circuit.h) for t in frames[child].basis],
                                          [vector(t,circuit.h) for t in frame.basis])
    return {"independent_positive_envelopes":len(cached),"every_original_edge_dense_nested":True}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--h",type=int,nargs="+",default=[8,12])
    parser.add_argument("--gap",type=int,help="Singleton gap; omitted uses prior all-last graph")
    parser.add_argument("--time-limit",type=float,default=60)
    parser.add_argument("--dirty",action="store_true")
    parser.add_argument("--independent",action="store_true")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();install_reference(args.reference)
    begin=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    assert not args.output.exists(),"Use a fresh output path"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    source={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
        ("finite_adaptive_cores.py","finite_singleton_search.py","finite_block_search.py","frame_envelope.py","frame_reuse.py")}
    rows=[]
    for h in args.h:
        start=time.monotonic()
        cls=singleton_class()
        gap=h//2-1 if args.gap is None else args.gap
        positions=[gap if common//2<=gap else gap+1 for common in range(h)]
        original=GroupUnion(h,lambda n,common:cls(n,positions[common],4),"paired",0,True)
        checked_graph=original.verify()
        circuit,order,schedule_sha=relabel(original)
        required=required_cores(circuit)
        print(json.dumps(dict(h=h,phase="MILP",nodes=len(circuit.active))),flush=True)
        frames,plan,metadata=solve(circuit,required,args.time_limit)
        code=compile_reuse(circuit,frames,plan);checked=check(circuit,frames,code)
        maximized=compile_reuse(circuit,frames,optimize_chains(circuit,frames,"id"))
        assert maximized["roles"]<=code["roles"]
        if metadata["solver_optimal"]:assert maximized["roles"]==code["roles"]
        row=dict(h=h,gap=gap,positions=positions,graph=checked_graph,roles=maximized["roles"],
            milp_roles=code["roles"],milp=metadata,checked=checked,maxflow_checked=check(circuit,frames,maximized),
            target_check=target_check(circuit,frames,True),schedule_sha256=schedule_sha,
            chosen_original_node_ids=[order[n-1] for n in metadata["selected_relevant_wide_nodes"]],
            source_copy_frames_original_lines=True,nondegeneracy="Positive E(K,V) norm identity; optional wide children propagated to every optional ancestor")
        if args.independent:row["independent"]=independent(circuit,frames)
        if args.dirty:
            from dag_network import exact_invocation
            from frame_reuse_certificate import program
            row["dirty_basis"]=[exact_invocation(h,inverse,program(circuit,maximized)) for inverse in (False,True)]
        row["elapsed_seconds"]=time.monotonic()-start;rows.append(row)
        import numpy,scipy
        result=dict(settings={**vars(args),"output":str(args.output)},started_utc=started,
            completed_utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-begin,
            source_sha256=source,reference_commit="bcd4ebde8692383539f8a48734e5fbf3a18a32c2",rows=rows,
            runtime=dict(numpy=numpy.__version__,scipy=scipy.__version__),
            scope="Recovered exact positive frame/controller witness; fixed-schedule optimality only when MILP solver closes its gap; no analytic promotion")
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print(json.dumps(dict(h=h,roles=row["roles"],wide=metadata["propagated_wide_nodes"],
                             optimal=metadata["solver_optimal"],seconds=row["elapsed_seconds"])),flush=True)
        included.cache_clear();GroupUnion.support_in.cache_clear()


if __name__=="__main__":main()
