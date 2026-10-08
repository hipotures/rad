#!/usr/bin/env python3
"""Exact separable moment search in a finite23/25 physical-profile pool.

At fixed a, subtracting the actual W makes the excess characteristic additive
in its two native axes. Minimize those two independent exact enclosures rather
than minimizing R. Profiles are input evidence, not source-legality proofs.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
import time


def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args();assert __debug__ and not args.output.exists()
    args.output.mkdir(parents=True)
    started=time.monotonic();manifest=json.loads(args.manifest.read_text())
    helper=Path(__file__).parents[1]/'agents/scout/code/check_joint_moment.py'
    spec=importlib.util.spec_from_file_location('independent_pool_moment',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    pools={23:[],25:[]};seen={23:set(),25:set()}
    N=comb(23,3)*comb(25,3);m=575
    for item in manifest['profiles']:
        p=item['profile'];h=p['h'];assert h in pools and p['v']==comb(h,3)
        assert p['loss']==h*(h-1)
        assert sum(t*n for t,n in enumerate(p['blocks']))==h*p['R']+p['loss']
        assert p['blocks'][0]==p['blocks'][h]==0
        key=(p['R'],tuple(p['blocks']))
        if key in seen[h]:continue
        seen[h].add(key)
        copies=N//p['v'];rows=Counter({t:n*copies for t,n in enumerate(p['blocks']) if t and n})
        rows[h]+=copies*p['R'];rows[m-2*h]+=copies*p['R']
        pools[h].append(dict(input=item,rows=rows,bank=copies*p['R']))
    assert all(pools.values())
    base=Counter({1:23*N,21:4*N,17:2*N,23:2*N,481:2*N})
    assert sum(t*n for t,n in base.items())==2*m*N-N
    evaluation_count=0
    def fixed(a):
        nonlocal evaluation_count
        evaluation_count+=1
        b=module.moment(m,1,base,a)
        selected={};axis_enclosures={};minlower={}
        for h,pool in pools.items():
            costs=[]
            for index,item in enumerate(pool):
                e=module.moment(m,1,item['rows'],a)
                costs.append((e['lower']-item['bank'],e['upper']-item['bank'],index))
            lo,hi,index=min(costs,key=lambda v:(v[1],v[2]))
            selected[h]=index;axis_enclosures[h]=(lo,hi)
            minlower[h]=min(v[0] for v in costs)
        lower=b['lower']-2*N+sum(minlower.values())
        upper=b['upper']-2*N+sum(v[1] for v in axis_enclosures.values())
        return dict(a=a,lower=lower,upper=upper,selected=selected,
                    axis_selected_enclosures=axis_enclosures)
    grid=10**14;lo,hi=0,10**11;trace=[]
    while hi-lo>1:
        mid=(lo+hi)//2;v=fixed(F(mid,grid))
        if v['upper']<0:lo=mid
        elif v['lower']>0:hi=mid
        else:raise ArithmeticError('Enclosures overlap zero; higher precision required')
        trace.append(v)
    low=fixed(F(lo,grid));high=fixed(F(hi,grid))
    assert low['upper']<0 and high['lower']>0
    selected={h:pools[h][low['selected'][h]] for h in pools}
    rows=base.copy();W=2*N
    for item in selected.values():rows.update(item['rows']);W+=item['bank']
    rank=sum(t*n for t,n in rows.items());loss=sum((N//comb(h,3))*h*(h-1) for h in pools)
    assert rank==m*W-N+loss
    exact=module.moment(m,W,rows,F(lo,grid));assert exact['strict_gap']>0
    result=dict(status='EXACT FINITE INPUT-POOL MOMENT SEARCH PASS; NEW WORD REVIEW REQUIRED',
        recorded_utc=datetime.now(timezone.utc).isoformat(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),moment_helper_sha256=hashlib.sha256(helper.read_bytes()).hexdigest(),
        native_saving=F(lo,grid),next_grid_saving_excluded_for_entire_pool=F(hi,grid),
        pool_sizes={h:len(pool) for h,pool in pools.items()},cartesian_pairs=len(pools[23])*len(pools[25]),
        actual_fixed_saving_evaluations=evaluation_count,axis_profiles_evaluated=evaluation_count*sum(map(len,pools.values())),
        selected={h:item['input'] for h,item in selected.items()},
        controller=dict(m=m,N=N,W=W,total_rank=rank,deficit=N-loss,maxchild=max(rows),child_multiplicities=dict(sorted(rows.items()))),
        moment=exact,final_enclosures=dict(pass_at=low,fail_at=high),seconds=time.monotonic()-started,
        scope='Global optimum at the stated rational grid within this finite supplied histogram pool, by exact additive excess-characteristic enclosures. Modular screen inputs need complete rational CRT/source/dirty/causality review before acceptance. No global compiler optimum, new native source legality or multiplication exponent is asserted.')
    (args.output/'result.json').write_text(json.dumps(encode(result),indent=2)+'\n')
    (args.output/'trace.json').write_text(json.dumps(encode(trace),indent=2)+'\n')
    print(json.dumps(encode({k:result[k] for k in ['status','native_saving','pool_sizes','cartesian_pairs','seconds']})),flush=True)


if __name__=='__main__':main()
