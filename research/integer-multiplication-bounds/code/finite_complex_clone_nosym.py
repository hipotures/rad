#!/usr/bin/env python3
"""Several exact binary clone choices with bounded symmetry preprocessing disabled.

Fresh source based on frozen finite_complex_clone_options.py; no executed
source is changed. Native HiGHS mip_detect_symmetry=False is verified locally.
The earliest limit nonempty chain tables already consume all offered slots;
later tables cannot change the literal offered job list.

Numerical MILP proposes subsets only. Integer capacity and formal-child
checks decide feasibility; all changed scalar/frame/phase checks are kept.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import time
from unittest.mock import patch
import warnings

import finite_complex_delayed_clones as witness
from finite_clone_chain_bridge import bridge_compatible
import frame_reuse

LAST_SELECTION={}


def opportunities(circuit, frames, plan, limit=4, policy='wide', seed=0):
    users, descriptions, successor, predecessor, _=plan
    retained={descriptions[first][1] for first in successor}
    recipients={(parent,position):user for user,(_,parent,position) in enumerate(descriptions) if parent is not None}
    jobs=[];parents=0;maximum_options=0;excluded=0
    def tie(*parts):return sha256(repr((seed,*parts)).encode()).digest()
    for node in sorted(circuit.active):
        if not circuit.args[node] or node in retained:continue
        chains=[]
        for first in users[node]:
            if first in predecessor:continue
            chain=[];user=first
            while True:
                _,parent,position=descriptions[user]
                chain.append(('gate',parent) if parent is not None else ('output',position))
                if user not in successor:break
                user=successor[user]
            chains.append((first,chain))
        if len(chains)<2:continue
        def chain_key(pair):
            first,chain=pair;kind,owner=chain[0];dimension=frames[owner if kind=='gate' else node].dimension
            return ((-dimension if policy=='wide' else dimension) if policy!='seeded' else 0,tie(node,first))
        chains.sort(key=chain_key);tables=[]
        for chain_first,chain in chains:
            kind,owner=chain[0];owner_node=owner if kind=='gate' else node;frame=frames[owner_node]
            assert frame_reuse.included(frames[node],frame)
            if not all(frame_reuse.included(frames[child],frame) for child in circuit.args[node]):
                excluded+=1;continue
            owner_key=(frame.dimension,owner_node) if kind=='gate' else None;options=[]
            for position,child in enumerate(circuit.args[node]):
                for first in users[child]:
                    _,previous,_=descriptions[first]
                    if previous is None or previous==node or previous in retained:continue
                    if owner_key is not None and (frames[previous].dimension,previous)>=owner_key:continue
                    if not frame_reuse.included(frames[previous],frame):continue
                    options.append(dict(node=node,selected=frozenset(chain),predecessor_gates=[node,previous],
                        original_predecessor_users=[recipients[node,1-position],first],original_children=list(circuit.args[node]),
                        same_gate_new_predecessor_input=1-position,earlier_predecessor_input=position,
                        clone_frame_owner=owner_node,clone_insertion_owner=owner if kind=='gate' else None,
                        original_frame_dimension=frames[node].dimension,clone_frame_dimension=frame.dimension,
                        chain_first_user=chain_first))
            options.sort(key=lambda job:tie(node,job['predecessor_gates'][1],job['earlier_predecessor_input'],chain_first))
            if options:
                tables.append(options[:limit])
                if len(tables)>=limit:break
        offered=[];seen=set()
        for depth in range(limit):
            for table in tables:
                if depth>=len(table):continue
                job=table[depth];key=(job['chain_first_user'],job['predecessor_gates'][1],job['earlier_predecessor_input'])
                if key not in seen:offered.append(job);seen.add(key)
                if len(offered)>=limit:break
            if len(offered)>=limit:break
        if offered:
            parents+=1;maximum_options=max(maximum_options,len(offered));jobs.extend(offered)
    return jobs,dict(eligible_parents=parents,offered_job_options=len(jobs),maximum_options_per_parent=maximum_options,
        excluded_alternating_formal_child_residuals=excluded,option_limit=limit,frame_policy=policy,seed=seed,
        scope='Individually admitted actual binary child/provider/first-consumer intervals')


def select(jobs, time_limit=6.0):
    global LAST_SELECTION
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    lower,_=bridge_compatible(jobs);capacities=defaultdict(list);parents=defaultdict(list)
    for index,job in enumerate(jobs):
        parents[job['node']].append(index)
        for gate in {job['node'],*job['predecessor_gates']}:capacities[gate].append(index)
    constraints=[indices for _,indices in sorted(capacities.items()) if len(indices)>1]
    conflicts=set()
    for job in jobs:
        for child in job['original_children']:
            if child in parents:conflicts.add(tuple(sorted((job['node'],child))))
    constraints.extend(parents[a]+parents[b] for a,b in sorted(conflicts))
    rr=[];cc=[]
    for row,indices in enumerate(constraints):rr.extend([row]*len(indices));cc.extend(indices)
    matrix=coo_matrix((np.ones(len(rr)),(rr,cc)),shape=(len(constraints),len(jobs))).tocsc();at=time.monotonic()
    if jobs:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',message='Unrecognized options detected.*')
            result=milp(-np.ones(len(jobs)),integrality=np.ones(len(jobs)),bounds=Bounds(0,1),
                constraints=LinearConstraint(matrix,-np.inf,np.ones(len(constraints))),
                options=dict(time_limit=time_limit,mip_rel_gap=0,threads=1,presolve=True,mip_detect_symmetry=False))
        proposed=[jobs[index] for index,value in enumerate(result.x if result.x is not None else []) if value>0.5]
        audited,rejected=bridge_compatible(proposed)
        assert not rejected and len(audited)==len(proposed), 'Numerical proposal failed exact integer feasibility'
        chosen=proposed if len(proposed)>len(lower) else lower
        solver=dict(status=int(result.status),message=str(result.message),solution_present=result.x is not None,
            proposed_exact_feasible_clones=len(proposed),seconds=time.monotonic()-at,time_limit_seconds=time_limit,
            exploratory_mip_gap=getattr(result,'mip_gap',None),exploratory_dual_bound=getattr(result,'mip_dual_bound',None),
            native_mip_detect_symmetry=False)
    else:chosen=lower;solver=dict(status='empty',seconds=0)
    assert len({job['node'] for job in chosen})==len(chosen)
    LAST_SELECTION=dict(offered_options=len(jobs),eligible_parents=len(parents),greedy_lower_clones=len(lower),
        selected_clones=len(chosen),capacity_constraints=len(constraints)-len(conflicts),
        formal_parent_child_constraints=len(conflicts),solver=solver,
        proof_scope='Only exact feasible subsets and fully checked actual compilations support claims; no numerical optimality claim')
    witness.selector.LAST_SELECTION=LAST_SELECTION
    selected_ids={id(job) for job in chosen}
    return chosen,[job for job in jobs if id(job) not in selected_ids]


def case(h, baseline, limit=4, policy='wide', seed=0, time_limit=6.0, dirty=False, exchange=False):
    with patch.object(witness,'opportunities',lambda c,f,p:opportunities(c,f,p,limit,policy,seed)), \
         patch.object(witness.selector,'select',lambda jobs:select(jobs,time_limit)):
        row=witness.case(h,baseline,dirty,exchange)
    row['complex_option_configuration']=dict(limit=limit,policy=policy,seed=seed,time_limit_seconds=time_limit)
    return row


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[8,12]);ap.add_argument('--limit',type=int,default=4)
    ap.add_argument('--policy',choices=['wide','narrow','seeded'],default='wide');ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--time-limit',type=float,default=6);ap.add_argument('--dirty-ground',type=int,default=8)
    ap.add_argument('--exchange-h8',action='store_true');ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();baseline=json.loads(args.baseline.read_text())
    assert baseline['source_sha256']==sha256(Path(witness.binary.__file__).read_bytes()).hexdigest()
    saved={row['h']:row for row in baseline['rows']};at=time.monotonic()
    value=dict(status='Running',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=[],
        baseline_input_sha256=sha256(args.baseline.read_bytes()).hexdigest(),started_utc=datetime.now(timezone.utc).isoformat())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        row=case(h,saved[h],args.limit,args.policy,args.seed,args.time_limit,h==args.dirty_ground,h==8 and args.exchange_h8)
        value['rows'].append(row);args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,roles=row['compiled_roles'],clones=row['role_saving'],selection=row['compatibility_selection'])),flush=True)
    value.update(status='Terminal exact nonalternating multi-option complex clone PASS',elapsed_seconds=time.monotonic()-at,
        completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
