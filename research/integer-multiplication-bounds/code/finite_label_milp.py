#!/usr/bin/env python3
"""Binary nested-frame/controller planner with exact recovered feasibility.

Callers provide narrow/wide rational frames and an exact inclusion predicate.
Wide original-edge labels must already nest, narrow-to-wide edges must nest,
and a wide child is conservatively propagated to its optional parents.
The unchanged mixer compiler verifies the resulting physical schedule.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import product
import time

from finite_adaptive_cores import nesting_links


def solve(circuit,choices,included,time_limit=60):
    import numpy as np
    from scipy.optimize import Bounds,LinearConstraint,milp
    from scipy.sparse import coo_array
    optional={n for n,frames in choices.items() if frames[0]!=frames[1]}
    for n in sorted(circuit.active):
        if circuit.args[n]:
            for child in circuit.args[n]:
                assert included(choices[child][0],choices[n][0])
                assert included(choices[child][0],choices[n][1])
                assert included(choices[child][1],choices[n][1])
                if child in optional:assert n in optional
        else:assert n not in optional
    users={n:[] for n in circuit.active};descriptions=[]
    for node in sorted(circuit.active):
        if circuit.args[node]:
            for position,child in enumerate(circuit.args[node]):
                user=len(descriptions);descriptions.append((child,node,position));users[child].append(user)
    for target,node in sorted(circuit.outputs.items()):
        user=len(descriptions);descriptions.append((node,None,target));users[node].append(user)
    relevant=set();candidates=[]
    for node,outgoing in users.items():
        for index,first in enumerate(outgoing):
            previous=descriptions[first][1]
            if previous is None:continue
            for second in outgoing[index+1:]:
                following=descriptions[second][1]
                following=following if following is not None else node
                values={(a,b):included(choices[previous][a],choices[following][b])
                        for a,b in product((0,1) if previous in optional else (0,),
                                           (0,1) if following in optional else (0,))}
                if not any(values.values()):continue
                need_a=previous in optional and any(values[0,b]!=values[1,b] for b in ((0,1) if following in optional else (0,)))
                need_b=following in optional and any(values[a,0]!=values[a,1] for a in ((0,1) if previous in optional else (0,)))
                flags=[]
                if need_a:flags.append(previous);relevant.add(previous)
                if need_b:flags.append(following);relevant.add(following)
                forbidden=[]
                for assignment in product((0,1),repeat=len(flags)):
                    label=dict(zip(flags,assignment))
                    if not values[label.get(previous,0),label.get(following,0)]:forbidden.append(assignment)
                candidates.append((first,second,tuple(flags),tuple(forbidden)))
    flags={node:i for i,node in enumerate(sorted(relevant))}
    offset=len(flags);count=offset+len(candidates)
    rows=[];cols=[];data=[];upper=[];audit=[]
    def add(coefficients,rhs):
        row=len(upper);upper.append(rhs);audit.append((tuple(coefficients.items()),rhs))
        for column,value in coefficients.items():rows.append(row);cols.append(column);data.append(value)
    nesting=nesting_links(circuit,optional,relevant)
    for child,parent in nesting:add({flags[child]:1,flags[parent]:-1},0)
    by_gate=defaultdict(list);by_second=defaultdict(list)
    for index,(first,second,nodes,forbidden) in enumerate(candidates):
        y=offset+index
        by_gate[descriptions[first][1]].append(y);by_second[second].append(y)
        for assignment in forbidden:
            coefficients={y:1};zeros=0
            for node,choice in zip(nodes,assignment):
                coefficients[flags[node]]=1 if choice else -1;zeros+=not choice
            add(coefficients,len(nodes)-zeros)
    for indices in by_gate.values():add({index:1 for index in indices},1)
    for indices in by_second.values():add({index:1 for index in indices},1)
    matrix=coo_array((np.asarray(data,dtype=float),(np.asarray(rows,dtype=np.int32),np.asarray(cols,dtype=np.int32))),shape=(len(upper),count)).tocsc()
    matrix.indices=matrix.indices.astype(np.int32);matrix.indptr=matrix.indptr.astype(np.int32)
    objective=np.zeros(count);objective[offset:]=-1
    begin=time.monotonic()
    result=milp(objective,integrality=np.ones(count,dtype=np.uint8),bounds=Bounds(np.zeros(count),np.ones(count)),
        constraints=LinearConstraint(matrix,np.full(len(upper),-np.inf),np.asarray(upper,dtype=float)),
        options={"time_limit":time_limit,"mip_rel_gap":0,"threads":1})
    assert result.x is not None,result.message
    integer=np.rint(result.x).astype(np.int8)
    assert np.max(np.abs(result.x-integer))<1e-6
    assert all(sum(int(integer[index])*value for index,value in coefficients)<=rhs for coefficients,rhs in audit)
    assigned={node:int(integer[index]) for node,index in flags.items()}
    wide=set()
    for node in sorted(circuit.active):
        if node in optional:
            use=assigned.get(node,0) or any(child in wide for child in circuit.args[node] or ())
            if node in assigned:assert use==assigned[node]
            if use:wide.add(node)
    frames={node:choices[node][int(node in wide)] for node in circuit.active}
    for node in sorted(circuit.active):
        if circuit.args[node]:assert all(included(frames[child],frames[node]) for child in circuit.args[node])
    outgoing={};incoming={};retained={}
    for index,(first,second,nodes,forbidden) in enumerate(candidates):
        if integer[offset+index]:
            node,previous,_=descriptions[first];node2,following,_=descriptions[second]
            assert node==node2 and first<second and previous is not None
            assert included(frames[previous],frames[following if following is not None else node])
            assert first not in outgoing and second not in incoming
            outgoing[first]=second;incoming[second]=first
            retained[previous]=retained.get(previous,0)+1;assert retained[previous]<=1
    summary=dict(schedule="id",selected_links=len(outgoing),candidate_links=len(candidates),
                 scope="Joint binary nested-frame and controller choices under this fixed schedule")
    metadata=dict(optional_nodes=len(optional),relevant_frame_variables=len(flags),nesting_constraints=len(nesting),
        candidate_links=len(candidates),milp_variables=count,milp_constraints=len(upper),
        solver_status=int(result.status),solver_message=result.message,solver_reported_optimal=result.status==0,
        solver_gap=float(result.mip_gap) if result.mip_gap is not None else None,
        solver_dual_bound=float(result.mip_dual_bound) if result.mip_dual_bound is not None else None,
        selected_links=len(outgoing),solver_seconds=time.monotonic()-begin,
        selected_relevant_wide_nodes=[node for node,value in assigned.items() if value],
        propagated_wide_nodes=len(wide),selected_link_user_pairs=sorted(outgoing.items()),
        exact_integer_constraints_passed=len(audit),optimality_scope="Solver-reported status; no standalone exact dual certificate")
    return frames,(users,descriptions,outgoing,incoming,summary),metadata
