#!/usr/bin/env python3
"""Bounded exact XOR synthesis across distinct cancellation restrictions.

SAT witnesses receive independent exact bit-vector replay. Solver UNSAT or
UNKNOWN is recorded as such, without pretending to retain a formal UNSAT
proof. The hand proof for the five-vertex cone-restricted family is separate.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
import time


def pair_targets(n):
    inputs=list(combinations(range(n),2))
    targets=[sum(1<<j for j,e in enumerate(inputs) if not set(e)&set(omit))
             for omit in inputs]
    return inputs,targets


def exact_replay(inputs,targets,word,mode):
    rows=[1<<j for j in range(len(inputs))]
    cones=list(rows)
    for i,(a,b) in enumerate(word):
        if not 0<=a<b<len(rows):
            raise ValueError('Invalid straight-line gate')
        row=rows[a]^rows[b]
        cone=cones[a]|cones[b]
        if mode=='cancellation-free' and rows[a]&rows[b]:
            raise ValueError('Cancellation-free promise failed')
        if row==0 or row in rows:
            raise ValueError('Redundant or zero gate')
        rows.append(row)
        cones.append(cone)
    for target in targets:
        if target not in rows:
            raise ValueError('Target missing')
        j=rows.index(target)
        if mode=='no-outside-cones' and cones[j]&~target:
            raise ValueError('Target cone contains excluded inputs')
    return dict(all_input_columns_exact=True,all_targets_exact=True,
                gates=len(word),mode=mode,
                outside_source_cones=sum(bool(cones[rows.index(t)]&~t) for t in targets),
                cancellation_gates=sum(bool(rows[a]&rows[b]) for a,b in word))


def solve(spec,outdir):
    import z3
    mode,k,seed=spec
    outdir=Path(outdir)
    start=time.monotonic()
    inputs,targets=pair_targets(5)
    m=len(inputs)
    solver=z3.Solver()
    solver.set(timeout=90000,random_seed=seed,threads=1)
    values=[z3.BitVecVal(1<<j,m) for j in range(m)]
    cones=list(values)
    left,right=[],[]
    def choose(index,items):
        result=items[-1]
        for j in range(len(items)-2,-1,-1):
            result=z3.If(index==j,items[j],result)
        return result
    for gate in range(k):
        a,b=z3.Ints(f'a{gate} b{gate}')
        left.append(a);right.append(b)
        limit=m+gate
        solver.add(a>=0,a<b,b<limit)
        va,vb=choose(a,values),choose(b,values)
        row=z3.BitVec(f'x{gate}',m)
        solver.add(row==va^vb,row!=0)
        for old in values:
            solver.add(row!=old)
        cone=z3.BitVec(f'c{gate}',m)
        solver.add(cone==(choose(a,cones)|choose(b,cones)))
        if mode=='cancellation-free':
            solver.add((va&vb)==0)
        values.append(row);cones.append(cone)
        if gate:
            # Any two adjacent independent gates can be ordered canonically.
            solver.add(z3.Implies(b<m+gate-1,
                                 z3.Or(left[-2]<a,z3.And(left[-2]==a,right[-2]<b))))
    for target in targets:
        if mode=='no-outside-cones':
            solver.add(z3.Or([z3.And(row==target,(cone&z3.BitVecVal(((1<<m)-1)^target,m))==0)
                              for row,cone in zip(values,cones)]))
        else:
            solver.add(z3.Or([row==target for row in values]))
    smt=solver.to_smt2()
    smt_path=outdir/f'{mode}-{k}-seed{seed}.smt2'
    smt_path.write_text(smt)
    status=solver.check()
    receipt=dict(mode=mode,gate_budget=k,seed=seed,z3_version=z3.get_version_string(),
                 status=str(status),seconds=time.monotonic()-start,
                 smt2_sha256=sha256(smt.encode()).hexdigest(),
                 smt2_bytes=len(smt.encode()),statistics=str(solver.statistics()),
                 scope='Finite straight-line XOR search on K5 pair-exclusion matrix; no reversible/physical network or exponent claim.')
    if status==z3.sat:
        model=solver.model()
        word=[(model.eval(a).as_long(),model.eval(b).as_long()) for a,b in zip(left,right)]
        receipt['word']=word
        receipt['independent_bitvector_replay']=exact_replay(inputs,targets,word,mode)
    elif status==z3.unknown:
        receipt['reason_unknown']=solver.reason_unknown()
    else:
        receipt['unsat_scope']='Solver UNSAT with no exported independently checked proof; analytic lower bound available separately for restricted modes.'
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    specs=[('unrestricted',19,0),('no-outside-cones',19,1),
           ('cancellation-free',19,2),('unrestricted',20,3)]
    p=dict(created_utc=datetime.now(timezone.utc).isoformat(),worker_processes=args.workers,
           native_threads_each=1,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
           specs=specs,solver_timeout_ms=90000,
           git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           python=sys.version,solver_dependency='z3-solver==5.1.0.0',
           model_dimensions=dict(points=5,inputs=10,outputs=10))
    (args.output/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(solve,spec,str(args.output)):spec for spec in specs}
        for future in as_completed(jobs):
            spec=jobs[future]
            receipt=future.result()
            name=f'{spec[0]}-{spec[1]}-seed{spec[2]}'
            (args.output/f'{name}.json').write_text(json.dumps(receipt,indent=2)+'\n')
            print(json.dumps({key:receipt[key] for key in ['mode','gate_budget','status','seconds']}),flush=True)


if __name__=='__main__':
    main()
