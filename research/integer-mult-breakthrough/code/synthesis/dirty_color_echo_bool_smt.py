#!/usr/bin/env python3
"""Boolean finite-frame encoding of the exact dirty center/side discriminator.

This repairs an ineffective arithmetic-array encoding without replacing its
UNKNOWN receipts. Each gate has exactly one frame; Boolean distance thresholds
are fully constrained by the exact finite distance table. No relaxation is
accepted. SAT candidates replay scalar columns and all chronological ranks.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import time

import dirty_color_echo_smt as old


def probe(spec):
    n,m,kind,chronology,seconds,seed=spec;started=time.monotonic();f=old.f;z3=old.z3
    word=old.scalar_word(m,chronology);w=2*m+1;positive=old.replay(word,m);negative=old.replay(word,m,True)
    zero=f.le((),n);full=f.le(tuple(1<<j for j in range(n)),n)
    starts=[f.le((1<<j,),n) for j in range(m)]+[zero]*(m+1)
    ends=[full]*m+[f.le(f.perpendicular((1<<j,),n),n) for j in range(m)]+[full]
    domain=sorted(f.lagrangians(n) if kind=='all-Lagrangian' else [f.le(E,n) for E in f.subspaces(n)])
    frames=len(domain);ids={L:j for j,L in enumerate(domain)};table=[[f.distance(a,b,n) for b in domain] for a in domain]
    edges,boundaries,constant=f.incidence_graph(word,w,starts,ends)
    unary=[[sum(table[j][ids[F]] for F in boundary) for j in range(frames)] for boundary in boundaries]
    solver=z3.Solver();solver.set(timeout=seconds*1000,random_seed=seed,max_memory=512)
    choices=[[z3.Bool(f'gate_{g}_frame_{j}') for j in range(frames)] for g in range(len(word))]
    for row in choices:solver.add(z3.PbEq([(x,1) for x in row],1))
    charges=[];threshold_variables=0
    for edge,(a,b,weight) in enumerate(edges):
        for rank in range(1,n+1):
            value=z3.Bool(f'edge_{edge}_rank_at_least_{rank}');threshold_variables+=1
            for left in range(frames):
                far=z3.Or([choices[b][right] for right in range(frames) if table[left][right]>=rank])
                solver.add(z3.Implies(choices[a][left],value==far))
            charges.append((value,weight))
    for gate,costs in enumerate(unary):
        for threshold in range(1,max(costs)+1):
            charges.append((z3.Or([choices[gate][j] for j,cost in enumerate(costs) if cost>=threshold]),1))
    capacity=w*n;budget=capacity-1;solver.add(z3.PbLe(charges,budget-constant))
    formula=solver.sexpr();formula_hash=sha256(formula.encode()).hexdigest();answer=solver.check();assignment=None;receipt=None
    if answer==z3.sat:
        model=solver.model();assignment=[]
        for row in choices:
            selected=[j for j,value in enumerate(row) if z3.is_true(model.eval(value,model_completion=True))]
            if len(selected)!=1:raise ValueError('Boolean finite frame assignment is not unique')
            assignment.append(selected[0])
        energy=f.energy(assignment,edges,unary,lambda a,b:table[a][b],constant)
        current=list(starts);hist=Counter()
        for gate,(a,b,c) in enumerate(word):
            F=domain[assignment[gate]]
            for role in (a,b):
                rank=f.distance(current[role],F,n)
                if rank:hist[rank]+=1
                current[role]=F
        for role,F in enumerate(ends):
            rank=f.distance(current[role],F,n)
            if rank:hist[rank]+=1
        if sum(rank*count for rank,count in hist.items())!=energy or energy>budget:
            raise ValueError('Boolean frame model fails exact chronological cost replay')
        receipt=dict(rank_charge=energy,capacity=capacity,deficit=capacity-energy,
                     chronological_histogram=dict(sorted(hist.items())),
                     optimistic_homogeneous_moment_at_kappa_1e_4=sum(r*c*2**(1e-4*(n-r)) for r,c in hist.items())/capacity)
    return dict(status='EXACT FINITE FRAME DEFICIT FOUND' if answer==z3.sat else
                'SOLVER UNSAT IN COMPLETE DECLARED FINITE FRAME MODEL' if answer==z3.unsat else 'UNKNOWN RESOURCE LIMIT',
                active_bits=n,color_size=m,frame_kind=kind,chronology=chronology,source_seed=seed,frame_count=frames,
                payload_stock=w,arbitrary_dirty_helpers=1,scalar_shears=len(word),capacity=capacity,strict_deficit_budget=budget,
                complete_endpoint_floor=sum(f.distance(a,b,n) for a,b in zip(starts,ends)),
                solver_result=str(answer),solver_unknown_reason=solver.reason_unknown() if answer==z3.unknown else None,
                timeout_seconds=seconds,memory_limit_MiB=512,Boolean_choice_variables=frames*len(word),
                exact_rank_threshold_variables=threshold_variables,formula_sha256=formula_hash,formula_bytes=len(formula.encode()),
                statistics=str(solver.statistics()),exact_scalar_replay=positive,scalar_corruption=negative,
                candidate=receipt,selected_frames=domain if assignment else None,
                word=[dict(destination=a,source=b,coefficient=str(c),common_frame=assignment[j]) for j,(a,b,c) in enumerate(word)] if assignment else None,
                seconds=time.monotonic()-started,
                scope='Exact Boolean finite-distance model of one complete dirty center/side scalar word. SAT includes full independent chronological rank replay. Solver UNSAT is scoped to this word and finite frame domain, not a formal proof artifact; UNKNOWN is inconclusive. Actual Gaussian operator gauges, native cost/precision and exponent remain unproved.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);parser.add_argument('--timeout',type=int,default=60);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    specs=[(3,3,'L_E','center-first',args.timeout,20261009021),
           (3,3,'all-Lagrangian','center-first',args.timeout,20261009022),
           (3,3,'all-Lagrangian','side-first',args.timeout,20261009023),
           (3,3,'all-Lagrangian','side-inside',args.timeout,20261009024)]
    paths=[Path(__file__),Path(old.__file__),Path(old.f.__file__),Path(old.f.__file__).with_name('lagrangian_graph_completion.py'),
           Path(old.f.__file__).with_name('trimmed_zeta_dirty_probe.py'),old.f.SIDE_SOURCE]
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,
                  source_sha256={p.name:v for p,v in hashes.items()},z3_solver_distribution_version=importlib.metadata.version('z3-solver'),
                  z3_engine_version=old.z3.get_version_string(),method='Exactly one Boolean frame per gate; complete distance-threshold equivalences; exact pseudo-Boolean rank budget')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({key:result[key] for key in ('status','active_bits','frame_kind','chronology','solver_result','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=v for p,v in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
