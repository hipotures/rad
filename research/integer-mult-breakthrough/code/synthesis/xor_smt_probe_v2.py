#!/usr/bin/env python3
"""QF_BV follow-up to the timed-out first XOR synthesis encoding."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from xor_smt_probe import exact_replay, pair_targets


def known_twenty_gate_word():
    inputs,targets=pair_targets(5)
    rows=[1<<i for i in range(10)]
    pending=[]
    for target in targets:
        parts=[i for i in range(10) if target>>i&1]
        pending.append((parts[0],parts[1],parts[2]))
    # Emit the canonical lexicographically least currently ready gate.
    nodes={i:i for i in range(10)}
    program=[]
    tasks=[]
    next_id=10
    for a,b,c in pending:
        tasks.append((next_id,(a,b)))
        tasks.append((next_id+1,(next_id,c)))
        next_id+=2
    while tasks:
        ready=[(tuple(sorted(nodes[x] for x in args)),old,args)
               for old,args in tasks if all(x in nodes for x in args)]
        pair,old,args=min(ready)
        nodes[old]=10+len(program)
        program.append(pair)
        tasks.remove((old,args))
    exact_replay(inputs,targets,program,'cancellation-free')
    return program


def solve(spec,outdir):
    import z3
    mode,k,seed,pinned=spec
    start=time.monotonic()
    inputs,targets=pair_targets(5)
    m=len(inputs)
    solver=z3.SolverFor('QF_BV')
    solver.set(timeout=180000,random_seed=seed,threads=1)
    values=[z3.BitVecVal(1<<i,m) for i in range(m)]
    cones=list(values)
    left,right=[],[]
    def select(index,items):
        result=items[-1]
        for j in range(len(items)-2,-1,-1):
            result=z3.If(index==j,items[j],result)
        return result
    for gate in range(k):
        a,b=z3.BitVecs(f'a{gate} b{gate}',5)
        left.append(a);right.append(b)
        solver.add(z3.ULT(a,b),z3.ULT(b,m+gate))
        va,vb=select(a,values),select(b,values)
        row=z3.BitVec(f'x{gate}',m)
        cone=z3.BitVec(f'c{gate}',m)
        solver.add(row==va^vb,cone==select(a,cones)|select(b,cones),row!=0)
        for old in values:
            solver.add(row!=old)
        if mode=='cancellation-free':
            solver.add(va&vb==0)
        if mode in ['cancellation-free','no-outside-cones']:
            # Every useful gate in these models lies in some target cone.
            # This is a valid strengthening for minimum-size circuits.
            mask=cone if mode=='no-outside-cones' else row
            solver.add(z3.Or([mask&z3.BitVecVal(((1<<m)-1)^t,m)==0 for t in targets]))
        values.append(row);cones.append(cone)
        if gate:
            solver.add(z3.Implies(z3.ULT(b,m+gate-1),
                z3.Or(z3.ULT(left[-2],a),z3.And(left[-2]==a,z3.ULT(right[-2],b)))))
    for target in targets:
        if mode=='no-outside-cones':
            solver.add(z3.Or([z3.And(row==target,cone&z3.BitVecVal(((1<<m)-1)^target,m)==0)
                              for row,cone in zip(values,cones)]))
        else:
            solver.add(z3.Or([row==target for row in values]))
    solver.add(z3.Or([values[-1]==t for t in targets]))
    if pinned:
        word=known_twenty_gate_word()
        if len(word)!=k:
            raise ValueError('Wrong pinned control size')
        for a,b,(x,y) in zip(left,right,word):
            solver.add(a==x,b==y)
    text=solver.to_smt2()
    name=f'{mode}-{k}-seed{seed}'+('-pinned' if pinned else '')
    (Path(outdir)/f'{name}.smt2').write_text(text)
    status=solver.check()
    result=dict(mode=mode,gate_budget=k,seed=seed,pinned_control=pinned,
                status=str(status),seconds=time.monotonic()-start,
                z3_version=z3.get_version_string(),statistics=str(solver.statistics()),
                smt2_sha256=sha256(text.encode()).hexdigest(),
                model='QF_BV parent selectors plus useful-cone strengthening for restricted minimum circuits',
                scope='Small auxiliary XOR model only; physical frames and dirty-reversible construction are separate obligations.')
    if status==z3.sat:
        model=solver.model()
        word=[(model.eval(a).as_long(),model.eval(b).as_long()) for a,b in zip(left,right)]
        result['word']=word
        result['independent_replay']=exact_replay(inputs,targets,word,mode)
    elif status==z3.unknown:
        result['reason_unknown']=solver.reason_unknown()
    else:
        result['proof_scope']='SMT solver UNSAT without an independently checked UNSAT proof; restricted-family analytic proof separately retained.'
    return name,result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    specs=[('unrestricted',19,0,False),('no-outside-cones',19,1,False),
           ('cancellation-free',19,2,False),('unrestricted',20,3,True)]
    sources=[Path(__file__),Path(__file__).with_name('xor_smt_probe.py')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),worker_processes=args.workers,
                  native_threads_each=1,seed_specs=specs,timeout_ms=180000,
                  source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources},
                  dependency='z3-solver==5.1.0.0',python=sys.version)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(solve,spec,str(args.output)) for spec in specs]
        for future in as_completed(futures):
            name,result=future.result()
            (args.output/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps({k:result[k] for k in ['mode','gate_budget','status','seconds']}),flush=True)


if __name__=='__main__':
    main()
