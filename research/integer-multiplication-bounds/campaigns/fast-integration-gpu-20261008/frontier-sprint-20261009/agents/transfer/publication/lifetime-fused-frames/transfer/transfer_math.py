#!/usr/bin/env python3
"""Exact arithmetic for the distinct balanced lifetime/fused168-170 identity.

This checks arithmetic, potential parameters and finite scalar/row bills. It
does not establish the finite signed words or their all-size interfaces.
Equations retain the PR23/29, RaD, James Chang PR34, Rohan Arun PR100/103,
icekylinx/eumemic PR104/144/152/161 and chafreaky PR163 attribution.
Prepared with OpenAI GPT-6.1 Sol assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import factorial, prod
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

GRID = 1 << 200
COARSE = Q(5936323, 10**10)
OLD = Q(384599, 10**10)
ATOM = Q(1, 1000)
AB = (1-ATOM)*COARSE+ATOM*OLD
BC = Q(74320127, 125000000000)
BAD = Q(1, 10**16)
PUBLIC = Q(593970203079492, 10**18)


def require(test, message):
    if not test:
        raise ValueError(message)


def down(x):
    return Q((x*GRID).numerator//(x*GRID).denominator, GRID)


def up(x):
    z=x*GRID
    return Q(-(-z.numerator//z.denominator), GRID)


def js(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k):js(v) for k,v in value.items()}
    if isinstance(value, (list, tuple)):
        return [js(v) for v in value]
    return value


def ceil(x):
    return -(-x.numerator//x.denominator)


def floor_strict(x, denominator):
    return Q(ceil(x*denominator)-1, denominator)


def log_unit(x):
    require(1 <= x <= 2, 'Log range reduction failed')
    z=(x-1)/(x+1)
    total=sum((2*z**(2*j+1)/(2*j+1) for j in range(60)), Q(0))
    tail=2*z**121/(121*(1-z*z))
    return down(total),up(total+tail)


def log_bounds(x):
    require(x >= 1, 'Nonnegative logarithm required')
    k=0
    while x > 2:
        x/=2;k+=1
    lo,hi=log_unit(x);two_lo,two_hi=log_unit(Q(2))
    return down(lo+k*two_lo),up(hi+k*two_hi)


def exp_bounds(lo,hi):
    require(0 <= lo <= hi < Q(1,2), 'Small nonnegative exponential required')
    low=sum((lo**j/factorial(j) for j in range(13)), Q(0))
    high=sum((hi**j/factorial(j) for j in range(13)), Q(0))
    tail=hi**13/factorial(13)/(1-hi/14)
    return down(low),up(high+tail)


def profile(m,W,hist):
    H={int(k):int(n) for k,n in hist.items() if int(k) and int(n)}
    require(all(0<r<m and n>0 for r,n in H.items()), 'Proper positive child required')
    mass=sum(r*n for r,n in H.items())
    require(mass<m*W, 'Rank mass does not contract')
    return dict(m=m,W=W,hist=H,mass=mass,maxchild=max(H),edges=sum(H.values()))


def moment(p,saving,bad=Q(0)):
    low=high=Q(0)
    for r,n in p['hist'].items():
        lo,hi=log_bounds(Q(p['m'],r))
        lo,hi=exp_bounds(saving*lo,saving*hi)
        weight=Q(r*n,p['m']*p['W'])
        low=down(low+weight*lo);high=up(high+weight*hi)
    # Retained additive worst-case envelope: charge a full singleton fallback
    # on every positive ideal edge in the bad fraction; subtract no ideal work.
    if bad:
        lo,hi=log_bounds(Q(p['m']))
        lo,hi=exp_bounds(saving*lo,saving*hi)
        weight=bad*Q(32*p['m']**2*p['edges'],p['m']*p['W'])
        low=down(low+weight*lo);high=up(high+weight*hi)
    return dict(lower=low,upper=high,gap_lower=1-high)


def halving(m,r):
    d=1
    while m**d <= 2*r**d:
        d+=1
    return d


def full_bridge(physical,scalar,coarse,atom):
    h,v,R,c,M=(int(scalar[k]) for k in ('h','v','R','c','total_M_operations'))
    require(R==scalar['c']+scalar['q']-scalar['matched'], 'Incorrect virtual scalar inventory')
    require(physical['R']==R and physical['physical_R']==R-physical['pairs'], 'Incorrect physical reuse')
    require(3*scalar['q']<2**15, 'Readout numerator bound needs more signed digits')
    p=profile(physical['m'],physical['W_per_vertex'],physical['child_histogram'])
    require(p['m']==3*h and p['W']==2*v+physical['physical_R'], 'Complex dimension/stock mismatch')
    require(p['mass']==physical['rank_per_vertex'], 'Complex rank mass mismatch')
    require(p['m']*p['W']-p['mass']==2*v-3*scalar['loss']==1320, 'Shared-core deficit mismatch')
    half=p['m']//2
    V=2**(p['m']-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1,half))
    W,s,N=V*p['W'],V*p['mass'],V*v
    local=4*(c+v)+10*v+4*h*v+4*h*h+8*h+8+2*h+8*R*v*(M+16)+32*v
    logical=3*V*local+8*W+4*N+8*p['m']*R*V
    router=64*(p['m']+1)**3*(logical+1)*(W+1)**2
    E=64*(W+p['m']+router+1)**3
    charge=2*router*W**2+8*s+4*W+4+32*p['m']
    B=s+E;C0=32*p['m']*B**2
    degree=halving(p['m'],p['maxchild'])
    coefficient=degree*W.bit_length()+9909+252
    actual=(1-atom)*coarse+atom*OLD
    require(actual<atom<1-actual, 'Atom adapters or internal rows are not lower order')
    result=dict(V=V,W=W,s=s,N=N,m=p['m'],maxchild=p['maxchild'],
        physical_roles=physical['physical_R'],scalar_roles=R,reuse_pairs=physical['pairs'],
        local_scalar=local,logical_scalar=logical,router=router,E=E,literal=charge,B=B,C0=C0,C1=1,
        strict_literal_gap=E-charge,induction_gap=2*B*(p['m']-p['maxchild'])-s-E,
        guard_gap=C0-2*B-18,halving_degree=degree,wire_bits=W.bit_length(),
        complex_coefficient=degree*W.bit_length(),old_coarse_reserve=9909,old_leaf_reserve=252,
        row_coefficient=coefficient,row_degree=70000,row_gap=Q(70000)-Q(51*coefficient,25),
        suffix_slope=280000,ordinary_saving=actual,atom=atom,coarse=coarse,old=OLD,
        adapter_gap=atom-actual,internal_row_gap=1-actual-atom,fixed_odd_divisor=3)
    require(min(result[k] for k in ('strict_literal_gap','induction_gap','guard_gap','row_gap'))>0,
            'A finite scalar/precision/row bill failed')
    return result


def balanced(bridge,b,beta,eta,weakening,*,old_prefix=False,old_guard=False,old_exposures=False,kappa=None):
    a=min(bridge['ordinary_saving'],(1-beta)*b-weakening)
    tau,sigma=1-a,1-b
    q=a*(1-2*eta);c=q+eta/4;eps=(1-eta)/(1+q)
    lp=1-q;lam=(tau+lp)/2;g=eps*q;r=(g+1-eps)/2;delta=eta/8
    kappa=floor_strict(g,10**18) if kappa is None else kappa
    C1=Q(19991,10000) if old_guard else Q(1)
    margins=dict(prefix=1-eps,movement=a,compact=g,bulk=a,
        Gaussian=min(1-eps-delta,r-delta),scalar=1-eps-delta,dimension=eps)
    if old_prefix:
        margins['prefix']=1-eps*(1+c)
    if old_exposures:
        margins['movement']=eps*c*a;margins['bulk']=a*(1-eps)
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    slacks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,
        lambda_prime_above_lambda=lp-lam,compact_leaf=lp-leaf,compact_reservations=lp-(1-c),
        lambda_prime_below_one=q,epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps*C1,
        K_geometry=1-eps*(1+c),K_dominates_log=eps*c,record_suffix=1-eps,
        phase_local=1-eps-delta,phase_boundary=r-delta,gamma_sublinear=1-eps-r,
        cell_above_band=eps-(1-r)/2,prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,delta_below_one_eighth=Q(1,8)-delta,
        short_record_fallback=eps-a,small_field_exposure=1-eps-g,artificial_boundary=8-eps+r-delta-g,
        literal_scalar_guard=bridge['strict_literal_gap'],row_product_gap=bridge['row_gap'])
    slacks.update({k+'_above_kappa':v-kappa for k,v in margins.items()})
    require(len(slacks)==47 and len(margins)==7, 'Incomplete cost inequalities')
    require(all(v>0 for v in slacks.values()), 'Failed inequalities: '+str({k:str(v) for k,v in slacks.items() if v<=0}))
    require(min(margins.values())==g and 1-eps-g==eta and 1-eps-r==eta/2, 'Incorrect controlling margin')
    require(1-eps*(1+c)==eta-eps*eta/4 and c-q==eta/4, 'Incorrect geometric identity')
    return dict(a=a,b=b,beta=beta,eta=eta,weakening=weakening,q=q,c=c,epsilon=eps,
        lambda_=lam,lambda_prime=lp,g=g,r=r,delta=delta,kappa=kappa,
        tau=tau,sigma=sigma,internal=internal,leaf=leaf,margins=margins,slacks=slacks,
        absorption_gap=g-kappa,strict_ceiling=a/(1+a))


def cutoffs(bridge,result):
    e,c,r,beta=(result[k] for k in ('epsilon','c','r','beta'))
    ka,km,kb,ks=(ceil(1/x) for x in (r,e*c,1-e,e*beta))
    # Includes old leaf, uniform coarse bit and complex arities conservatively.
    largest=575
    cuts=dict(guard=ceil(Q((2*bridge['C0']).bit_length())/(1-e)),
        normalization=ceil(7/(1-e-r)),alpha=16*ka*ka+1,compact=64*km*km+1,
        geometry=ceil(3/(1-e*(1+c))),phase_cell=ceil(9/(e-(1-r)/2)),
        period=128*kb*kb+1,stopped_leaf=ks*(4*largest).bit_length(),log_p=25,reservoir=14)
    common=max(cuts.values());checkpoints=[]
    for j in range(6):
        z=common*2**j
        pairs=dict(alpha=(z//ka,8*(z+ka)+64),compact=(z//km,32*(z+km)+192),
            period=(z//kb,16*(z+kb)+56),rows=(z//kb,bridge['suffix_slope']*(z+kb+8)),
            leaf=(z//ks,4*largest))
        require(all(lhs>=rhs.bit_length() for lhs,rhs in pairs.values()), 'Insufficient compressed-power cutoff')
        checkpoints.append(dict(log2_input=z,checks={k:dict(exponent=x,rhs=y,rhs_bits=y.bit_length()) for k,(x,y) in pairs.items()}))
    return dict(cuts=cuts,common=common,checkpoints=checkpoints,largest_arity=largest,
        scope='Sufficient arithmetic thresholds only; setup, prime, catalogue, logarithm and recovery thresholds remain inherited eventual conditions.')


