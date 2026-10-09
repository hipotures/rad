#!/usr/bin/env python3
"""Bounded SMT discovery of padded one-convolution Walsh embeddings.

The same-size obstruction leaves noncontiguous input/output slots open.
Positions and fourth-root diagonal/kernel phases are synthesized here.
Any SAT model is independently replayed over exact Gaussian rationals.
UNKNOWN is retained and is never an embedding exclusion.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import importlib.metadata
import json
from pathlib import Path
import time

import z3
import convolution_gauge_screen as c

UNITS=[c.g.ONE,(c.g.Q(0),c.g.Q(1)),(c.g.Q(-1),c.g.Q(0)),(c.g.Q(0),c.g.Q(-1))]


def exact_embedding(n,m,A,B,phase):
    d=1<<n;target=c.g.tensor_c(n);checks=0;digest=sha256();source=[];rows=[]
    for y in range(d):
        source.append(c.g.mul(UNITS[(-phase[-B[y]])%4],c.g.power((c.g.Q(0),c.g.Q(-1)),y.bit_count())))
    for x in range(d):
        rows.append(c.g.mul(c.g.power(c.g.ALPHA,n),c.g.mul(c.g.power((c.g.Q(0),c.g.Q(-1)),x.bit_count()),UNITS[(-phase[A[x]])%4])))
    for y in range(d):
        # This is ordinary polynomial convolution with a sparse clean input,
        # not a sum of arbitrary pairwise lookups in the reproduction.
        polynomial=[c.g.ZERO]*(3*m-2)
        for t in range(-(m-1),m):polynomial[B[y]+t+m-1]=c.g.mul(source[y],UNITS[phase[t]])
        for x in range(d):
            actual=c.g.mul(rows[x],polynomial[A[x]+m-1])
            if actual!=target[x][y]:raise ValueError('SAT position/gauge model fails literal Gaussian polynomial replay')
            digest.update(json.dumps([x,y,c.g.text_complex(actual)],separators=(',',':')).encode());checks+=1
    return dict(all_target_entries=checks,all_source_columns=d,exact_matrix_sha256=digest.hexdigest(),
                input_positions=B,output_positions=[a+m-1 for a in A],
                input_diagonal_coefficients=[c.g.text_complex(z) for z in source],
                output_diagonal_coefficients=[c.g.text_complex(z) for z in rows],
                kernel_phases={str(t):v for t,v in sorted(phase.items())},
                kernel_extent=2*m-1,polynomial_product_extent=3*m-2,
                scope='Exact clean Gaussian-rational embedding via one ordinary polynomial convolution and invertible coordinate gauges. Dirty restoration, integer/real encoding, kernel generation, padding/native cost and all-size family are not certified.')


def search(spec):
    n,m,seconds,seed,fix_rows=spec;d=1<<n;started=time.monotonic()
    solver=z3.Solver();solver.set(timeout=int(seconds*1000),random_seed=seed,max_memory=512)
    A=[z3.Int('out'+str(x)) for x in range(d)];B=[z3.Int('in'+str(y)) for y in range(d)]
    K=z3.Array('kernel',z3.IntSort(),z3.BitVecSort(2));zero=z3.BitVecVal(0,2)
    solver.add(z3.Distinct(*A),z3.Distinct(*B),A[0]==0,B[0]==0,z3.Select(K,0)==zero)
    for a in A+B:solver.add(a>=0,a<m)
    # Normalize output-address affine basis order. Independent source/output
    # GF2 translations are absorbed by row/column sign gauges.
    for bit in range(n):
        pivot=1<<bit
        for x in range(pivot,d):
            if x!=pivot:solver.add(A[pivot]<A[x])
    if fix_rows:
        for x,a in enumerate(A):solver.add(a==x)
    for x in range(d):
        for y in range(d):
            solver.add(z3.Select(K,A[x]-B[y])-z3.Select(K,A[x])-z3.Select(K,-B[y])==
                       z3.BitVecVal(2*((x&y).bit_count()%2),2))
    answer=solver.check();status=str(answer);model=None
    if answer==z3.sat:
        result=solver.model();a=[result.eval(x).as_long() for x in A];b=[result.eval(y).as_long() for y in B]
        phase={t:result.eval(z3.Select(K,t),model_completion=True).as_long() for t in range(-(m-1),m)}
        model=exact_embedding(n,m,a,b,phase)
        if n>=3 and m==d:raise ValueError('SAT exact same-size model contradicts established obstruction')
    return dict(status='EXACT FINITE PADDED EMBEDDING FOUND' if status=='sat' else 'EXCLUDED IN DECLARED FINITE PHASE/POSITION MODEL' if status=='unsat' else 'UNKNOWN RESOURCE LIMIT',
                active_bits=n,dimension=d,address_extent=m,extent_to_dimension_ratio=f'{m}/{d}',
                fixed_output_positions=fix_rows,solver_result=status,solver_unknown_reason=solver.reason_unknown() if answer==z3.unknown else None,
                timeout_seconds=seconds,random_seed=seed,memory_limit_MiB=512,
                statistics=str(solver.statistics()),seconds=time.monotonic()-started,exact_model=model,
                scope='Finite fourth-root phase and distinct padded-position model only. Affine source/output symmetries normalized. UNKNOWN is inconclusive; SAT has exact clean polynomial replay but no native cost or all-size theorem.')


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path,required=True)
    a.add_argument('--workers',type=int,default=4);a.add_argument('--timeout',type=int,default=60);a.add_argument('--bounded',action='store_true')
    args=a.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    specs=[(1,2,5,20261008,False),(2,4,10,20261009,False)] if args.bounded else [
        (3,8,args.timeout,202610089,False),(3,12,args.timeout,202610090,False),
        (3,16,args.timeout,202610091,False),(3,24,args.timeout,202610092,True)]
    paths=[Path(__file__),Path(c.__file__),Path(c.g.__file__),Path(c.__file__).with_name('lagrangian_graph_completion.py')]
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,
                  z3_solver_distribution_version=importlib.metadata.version('z3-solver'),z3_engine_version=z3.get_version_string(),
                  source_sha256={p.name:v for p,v in hashes.items()})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(search,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({k:result[k] for k in ('status','active_bits','address_extent','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=v for p,v in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
