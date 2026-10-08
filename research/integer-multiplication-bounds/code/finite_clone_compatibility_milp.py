#!/usr/bin/env python3
"""Bounded integer optimization of the exact clone compatibility relation.

The solver only proposes binary job subsets. Every capacity and formal-child
conflict is checked with integer arithmetic before the unchanged clone
builder, physical compiler and full frame checks run. Numerical optimizer
bounds are recorded as exploratory diagnostics, never theorem-level bounds.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time
import warnings

import finite_clone_capacity_fast as relaxation
import finite_clone_descendant_frame as witness
from finite_clone_chain_bridge import bridge_compatible

LAST_SELECTION={};TIME_LIMIT=12.0


def select(jobs):
    global LAST_SELECTION
    import numpy as np
    from scipy.optimize import Bounds,LinearConstraint,milp
    from scipy.sparse import coo_matrix
    lower,_=relaxation.select(jobs);diagnostic=relaxation.LAST_SELECTION
    capacities=defaultdict(list);index_by_parent={}
    for index,job in enumerate(jobs):
        parent=job['node'];assert parent not in index_by_parent
        index_by_parent[parent]=index
        for gate in {parent,*job['predecessor_gates']}:capacities[gate].append(index)
    constraints=[indices for _,indices in sorted(capacities.items()) if len(indices)>1]
    pairs=set()
    for index,job in enumerate(jobs):
        for child in job['original_children']:
            if child in index_by_parent:pairs.add(tuple(sorted((index,index_by_parent[child]))))
    constraints.extend(list(pair) for pair in sorted(pairs))
    rr=[];cc=[]
    for row,indices in enumerate(constraints):
        rr.extend([row]*len(indices));cc.extend(indices)
    matrix=coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(constraints),len(jobs))).tocsc()
    at=time.monotonic()
    if jobs:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',message='Unrecognized options detected.*')
            result=milp(-np.ones(len(jobs)),integrality=np.ones(len(jobs)),bounds=Bounds(0,1),
                constraints=LinearConstraint(matrix,-np.inf,np.ones(len(constraints))),
                options=dict(time_limit=TIME_LIMIT,mip_rel_gap=0,threads=1,presolve=True))
        proposed=[jobs[index] for index,value in enumerate(result.x if result.x is not None else []) if value>0.5]
        audit,rejected=bridge_compatible(proposed)
        assert not rejected and len(audit)==len(proposed), 'Reject any numerically proposed infeasible subset'
        selected=proposed if len(proposed)>len(lower) else lower
        solver=dict(status=int(result.status),message=str(result.message),solution_present=result.x is not None,
            exact_feasible_proposed_clones=len(proposed),bounded_seconds=time.monotonic()-at,time_limit_seconds=TIME_LIMIT,
            exploratory_mip_gap=getattr(result,'mip_gap',None),exploratory_objective=getattr(result,'fun',None),
            exploratory_dual_bound=getattr(result,'mip_dual_bound',None),workers=1)
    else:selected=lower;solver=dict(status='empty',workers=1)
    selected_nodes={job['node'] for job in selected};assert len(selected_nodes)==len(selected)
    LAST_SELECTION={**diagnostic,'capacity_matching_lower_clones':len(lower),'selected_clones':len(selected),
        'improvement_over_greedy':len(selected)-diagnostic['original_greedy_clones'],
        'improvement_over_capacity_matching':len(selected)-len(lower),'solver':solver,
        'binary_job_variables':len(jobs),'capacity_constraints':len(constraints)-len(pairs),
        'formal_child_pair_constraints':len(pairs),
        'proof_scope':'Exact integer feasibility checked for all controller capacities and formal-child conflicts; numerical optimizer bounds are exploratory only'}
    return selected,[job for job in jobs if job['node'] not in selected_nodes]


def main():
    global TIME_LIMIT
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference',required=True);ap.add_argument('--h',type=int,nargs='+',default=[8,12,20])
    ap.add_argument('--dirty-ground',type=int,default=12);ap.add_argument('--time-limit',type=float,default=12)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();TIME_LIMIT=args.time_limit;witness.install_reference(args.reference)
    at=time.monotonic();value=dict(status='Running',rows=[],source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        started_utc=datetime.now(timezone.utc).isoformat(),solver_scope='One CPU, bounded binary feasibility search; no floating-point optimality claim')
    previous=witness.bridge_compatible;witness.bridge_compatible=select
    try:
        for h in args.h:
            positions=[0]*(h//2-1)+[h//2-2]*(h//2+1)
            row=witness.case(h,2,positions,dirty=h==args.dirty_ground)
            row['compatibility_selection']=LAST_SELECTION;value['rows'].append(row)
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
            print(json.dumps(dict(h=h,roles=row['final']['roles'],clones=len(row['chosen']),
                gain_over_capacity=LAST_SELECTION['improvement_over_capacity_matching'],solver=LAST_SELECTION['solver'])),flush=True)
    finally:witness.bridge_compatible=previous
    value.update(status='Terminal exact feasible compatibility-MILP clone witness PASS',
        completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
