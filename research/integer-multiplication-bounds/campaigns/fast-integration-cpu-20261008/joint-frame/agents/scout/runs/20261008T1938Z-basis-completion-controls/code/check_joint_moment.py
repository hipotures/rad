#!/usr/bin/env python3
"""Independently assemble complete PR58 physical-word controller costs.

All controller terms, local mass, scalar charges, rational log/exponential
enclosures and bit halving/stock are recomputed here. The unchanged 47-row
balanced assembly is an explicitly pinned inherited arithmetic dependency,
not an independent proof of its all-size compiler or tape hypotheses.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
from math import comb
from pathlib import Path
import time


@lru_cache(None)
def logarithm(x):
    x=F(x);assert x>=1
    k=0
    while x>2:x/=2;k+=1
    def series(y):
        z=(y-1)/(y+1)
        lower=2*sum((z**(2*j+1)/F(2*j+1) for j in range(40)),F())
        return lower,lower+2*z**81/(81*(1-z*z))
    lo,hi=series(x);lo2,hi2=series(F(2));scale=10**40
    lo,hi=scale*(lo+k*lo2),scale*(hi+k*hi2)
    return F(lo.numerator//lo.denominator,scale),F(-(-hi.numerator//hi.denominator),scale)


def moment(m,W,rows,a):
    lower,upper=F(),F()
    for t,n in sorted(rows.items()):
        assert isinstance(t,int) and isinstance(n,int) and 0<t<m and n>0
        lo,hi=logarithm(F(m,t));x,y=a*lo,a*hi
        assert 0<=x<=y<1
        weight=F(t*n,m*W)
        lower+=weight*(1+x+x*x/2+x*x*x/6)
        upper+=weight*(1+y+y*y/(2*(1-y/3)))
    return dict(lower=lower,upper=upper,strict_gap=1-upper)


def build(profiles,physical):
    a,b=[p['h'] for p in profiles];assert(a,b)==(23,25)
    m,N=a*b,comb(a,3)*comb(b,3)
    parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}),
           'endpoint':Counter({1:N})}
    banks=[];loss=0;scalar=0
    for p,w in zip(profiles,physical):
        h,v,R=p['h'],p['v'],p['R'];assert v==comb(h,3)
        assert(w['h'],w['v'],w['R'])==(h,v,R)
        assert w['status']=='INDEPENDENT FULL DIRTY BASIS AND PER-ROLE FRAME PATH PASS'
        assert w['all_per_role_positive_frame_paths_equal_events']
        assert p['loss']==h*(h-1)
        assert len(p['blocks'])==h+1 and p['blocks'][0]==p['blocks'][h]==0
        assert all(isinstance(n,int) and n>=0 for n in p['blocks'])
        assert sum(t*n for t,n in enumerate(p['blocks']))==p['rank_sum']==w['rank_mass']==h*R+p['loss']
        copies=N//v;assert copies*v==N
        bank=copies*R;banks.append(bank);loss+=copies*p['loss']
        parts[f'internal_{h}']=Counter({t:n*copies for t,n in enumerate(p['blocks']) if t and n})
        parts[f'exterior_{h}']=Counter({h:bank,m-2*h:bank})
        parts[f'growth_{h}']=Counter({1:2*N,h-2:2*N})
        expected_xors=4*w['local_xors']+14*v
        assert all(q['elementary_xors']==expected_xors for q in w['full_basis_checks'])
        scalar+=copies*expected_xors
    W=2*N+sum(banks);rows=Counter()
    for row in parts.values():rows.update(row)
    mass=sum(t*n for t,n in rows.items());assert mass==m*W-N+loss
    degree=1
    while m**degree<=2*max(rows)**degree:degree+=1
    return dict(m=m,N=N,W=W,banks=banks,L=loss,total_rank=mass,deficit=m*W-mass,
        maxchild=max(rows),halving_degree=degree,wire_bits=W.bit_length(),
        wrapped_scalar_xors=scalar,child_multiplicities=dict(sorted(rows.items())),parts=parts)


def serialize(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):serialize(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serialize(y) for y in x]
    return x


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['profile23','profile25','physical23','physical25','inherited_certificate','assembly','output']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--saving',type=F)
    ap.add_argument('--kappa',type=F)
    args=ap.parse_args();assert __debug__ and not args.output.exists()
    args.output.parent.mkdir(parents=True,exist_ok=True);started=time.monotonic()
    paths=[args.profile23,args.profile25,args.physical23,args.physical25]
    documents=[json.loads(p.read_text()) for p in paths]
    controller=build(documents[:2],documents[2:]);m,W,rows=[controller[k] for k in ['m','W','child_multiplicities']]
    GRID=F(1,10**14)
    if args.saving:a=args.saving
    else:
        lo,hi=0,10**10
        while hi-lo>1:
            mid=(lo+hi)//2
            if moment(m,W,rows,mid*GRID)['upper']<1:lo=mid
            else:hi=mid
        a=lo*GRID
    exact=moment(m,W,rows,a);above=moment(m,W,rows,a+GRID)
    assert exact['strict_gap']>0
    inherited=json.loads(args.inherited_certificate.read_text());bridge=deepcopy(inherited['finite_bridge'])
    bridge['bit'].update({k:controller[k] for k in ['m','W','maxchild','halving_degree','wire_bits']})
    stock=controller['halving_degree']*controller['wire_bits']+bridge['complex']['halving_degree']*bridge['complex']['wire_bits']
    assert stock==bridge['rows']['coefficient']
    spec=importlib.util.spec_from_file_location('pinned_joint_balanced',args.assembly)
    assembly=importlib.util.module_from_spec(spec);spec.loader.exec_module(assembly)
    h=F(1,10**12);q=a*(1-2*h);G=(1-h)*q/(1+q)
    kappa=args.kappa if args.kappa else (G//GRID)*GRID
    composition=assembly.assembly(bridge,a,kappa)
    assert len(composition['constraints'])==47 and len(composition['margins'])==7
    assert all(x>0 for x in composition['constraints'].values())
    assert all(x>kappa for x in composition['margins'].values())
    result=dict(status='INDEPENDENT COMPLETE MOMENT AND PINNED CONDITIONAL ASSEMBLY PASS',
        recorded_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        inputs={str(p):dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()) for p in paths+[args.inherited_certificate,args.assembly]},
        controller=controller,saving=a,moment=exact,next_saving=a+GRID,next_lower=above['lower'],
        next_saving_strictly_excluded=above['lower']>1,kappa=kappa,assembly=composition,
        inherited_assembly_source_sha256=sha256(args.assembly.read_bytes()).hexdigest(),
        finite_role_product_stock=stock,seconds=time.monotonic()-started,
        scope='Finite full cost and exact inequalities. Complete physical framed address residual semantics, selected-bit/arbitrary routing, finite-alphabet multitape, scalar absorption, analytic/recovery and eventual setup remain named all-size hypotheses.')
    args.output.write_text(json.dumps(serialize(result),indent=2)+'\n')
    print(json.dumps(serialize({k:result[k] for k in ['status','saving','kappa','seconds']})),flush=True)
    print(json.dumps({k:controller[k] for k in ['W','total_rank','deficit','halving_degree','wire_bits','wrapped_scalar_xors']}),flush=True)


if __name__=='__main__':main()
