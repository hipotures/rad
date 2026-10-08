#!/usr/bin/env python3
"""Exact assembly for a sharper unrolling of the unchanged packed recurrence.

This keeps K^tau outside the geometric sum rather than bounding it by a
power of each current recursion width. It is a changed estimate, not a new
selected-address-bit movement procedure.
"""

from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from math import comb
from pathlib import Path
import time

from downstream_gaussian import BASELINE_KAPPA,ceil_q,check_sources,network_counts,require
from downstream_parameter_optimum import (as_strings,compact_lower,rational_decimal_lower,
                                          root_enclosure,saving_enclosure)


def asymmetric_counts(p: int,q: int,rp: int,rq: int) -> dict:
    vp,vq,m=comb(p,3),comb(q,3),p*p*q
    n=vp*vp*vq
    w=2*n+vp*vq*(rp+p)+vp*vp*(rq+q)
    loss=2*vp*vq*p*p+vp*vp*q*q
    deficit=n-2*loss
    return {"p":p,"q":q,"outer_side_roles":rp,"middle_side_roles":rq,
            "N":n,"m":m,"W":w,"L":loss,"D":deficit,"s":w*m-deficit,
            "eta":Q(deficit,w*m)}


def complex_counts() -> dict:
    v,m=comb(50,3),50**3
    n=v**3
    w=2*n+3*v*v*(v*(comb(47,3)+3*47)+51)
    loss=3*v*v*51*50
    s=w*m-2*n+2*loss
    return {"ground":50,"N":n,"m":m,"W":w,"L":loss,"s":s,
            "eta":Q(w*m-s,w*m)}


def recurrence_identity_checks() -> dict:
    count=0
    # Exact rational proxies certify the geometric identity and orientation.
    # The all-size transfer then substitutes a=m^sigma,b=m^tau.
    for ratio in [Q(1001,1000),Q(5,4),Q(3,2),Q(2)]:
        for depth in range(1,41):
            total=sum((ratio**j for j in range(depth)),Q(0))
            require(total==(ratio**depth-1)/(ratio-1),"Geometric identity failed")
            require(total<ratio**depth/(ratio-1),"Growing geometric sum bound failed")
            count+=1
    for a,b in [(Q(3,1000),Q(1,10000)),(Q(1,8),Q(1,32)),(Q(1,2**30),Q(1,2**36))]:
        tau=1-a
        x=a*a/(b*tau+a*a)
        c=a*b/(b*tau+a*a)
        require(c==a*(1-x)+b*x and a*c==b*x,"Exact packed/leaf balance failed")
        require(a*c/(1+4*x)==a*a*b/(b*tau+5*a*a),"Guard ceiling identity failed")
        count+=1
    return {"status":"PASS exact recurrence geometric and balance identities",
            "checks":count,"scope":"Scalar identity checks supplement the all-size written recurrence proof."}


def witness(n: dict,name: str) -> dict:
    nc=complex_counts()
    require(n['D']>0 and 2<=n['s']<n['m']**5,"Finite bit count premise failed")
    eb,ec=saving_enclosure(n['eta'],n['m']),saving_enclosure(nc['eta'],nc['m'])
    a,b=eb['chosen_saving'],ec['chosen_saving']
    require(0<b<a<Q(1,32),"Sharper growing-geometric branch requires sigma>tau")
    tau,sigma=1-a,1-b
    x=a*a/(b*tau+a*a)
    beta=1-x
    c_star=a*b/(b*tau+a*a)
    c=c_star*(1-Q(1,2**32))
    q=a*c
    lp=1-q
    internal=sigma+beta*(tau-sigma)+tau*c
    leaf=sigma+beta*(1-sigma)
    lam=(lp+max(sigma,internal))/2
    zeta=Q(1,2**30)
    C1=5-4*beta+zeta
    eps=(1-Q(1,2**20))/C1
    r=(1-eps)/2
    delta=r/8
    B=nc['s']+64*(nc['W']+nc['m']+1)**3
    C0=32*nc['m']*B*B*(1+1/zeta)
    margins={"g1":1-eps*(1+c),"g2":eps*a*c,"g3":eps*q,
             "g4":a*(1-eps),"g5":min(1-eps-delta,r-delta),
             "g6":1-eps-delta,"g7":eps}
    G=min(margins.values())
    kappa=compact_lower(G)
    slacks={"bit_primitive":eb['strict_primitive_gap'],
            "complex_primitive":ec['strict_primitive_gap'],"sigma_above_tau":sigma-tau,
            "lambda_above_tau":lam-tau,"lambda_above_sigma":lam-sigma,
            "exact_internal_geometric_bound":lam-internal,"lambda_prime_above_lambda":lp-lam,
            "leaf_cost":lp-leaf,"guard":1-eps*C1,
            "phase_local_cost":1-eps-delta,"phase_boundary_cost":r-delta,
            "gamma_sublinear":1-eps-r,"phase_cell_separation":eps-(1-r)/2,
            "prime_interval_and_line_growth":1-eps,"alpha_power":r,
            "prefix_cost":1-eps*(1+c),"K_smaller_than_ell":1-eps-eps*c,
            "absorption":G-kappa}
    for key,value in slacks.items(): require(value>0,"Nonpositive exact-unroll slack "+key)
    require(G==margins['g2']==margins['g3'],"Unexpected exact-unroll bottleneck")
    au,bu=eb['saving_upper'],ec['saving_upper']
    upper=au*au*bu/(bu*(1-au)+5*au*au)
    require(kappa<upper,"Exact-unroll scoped ceiling failed")
    oldlo,oldhi=root_enclosure(a,b)
    oldbeta=1-oldhi
    oldc=a*oldbeta/(tau+a*oldbeta)*(1-Q(1,2**32))
    oldeps=(1-Q(1,2**20))/(5-4*oldbeta+zeta)
    oldmargin=oldeps*a*oldc
    oldkappa=compact_lower(oldmargin)
    require(G>oldmargin and kappa>oldkappa,"Sharper unrolling gave no strict improvement")
    k=ceil_q(1/r)
    cutoffs={"gamma":ceil_q(Q(7)/(1-eps-r)),"logarithmic_alpha":16*k*k+1,
             "full_guard":ceil_q(Q((2*ceil_q(C0)).bit_length())/(1-eps*C1)),
             "partial_cell":ceil_q(Q(9)/(eps-(1-r)/2))}
    return as_strings({"status":"Exact arithmetic candidate; sharper recurrence proof requires independent review",
                       "name":name,"bit_counts":n,"complex_counts":nc,
                       "bit_saving_enclosure":eb,"complex_saving_enclosure":ec,
                       "parameters":{"tau":tau,"sigma":sigma,"a_bit":a,"a_complex":b,
                                     "beta":beta,"c":c,"lambda":lam,"lambda_prime":lp,
                                     "epsilon":eps,"alpha_squared_power":r,"delta":delta,
                                     "C0":C0,"C1":C1,"zeta":zeta,"kappa":kappa},
                       "internal_exponent":internal,"leaf_exponent":leaf,"constraint_slacks":slacks,
                       "margins":margins,"minimum_margin":G,"model_upper":upper,
                       "kappa_ratio_to_baseline":kappa/BASELINE_KAPPA,
                       "kappa_ratio_decimal_lower":rational_decimal_lower(kappa/BASELINE_KAPPA,12),
                       "old_per_node_bound":{"balance_root_interval":[oldlo,oldhi],"kappa":oldkappa,
                                             "minimum_margin":oldmargin},
                       "strict_improvement_factor":kappa/oldkappa,
                       "improvement_factor_decimal_lower":rational_decimal_lower(kappa/oldkappa,15),
                       "old_per_node_hypothesis_gap":lp-tau*(1+c/beta),
                       "log2_b_cutoffs":cutoffs,"common_log2_b_cutoff":max(cutoffs.values()),
                       "additional_eventual_cutoffs":["BHP prime threshold and interval packing", "unchanged source interfaces"],
                       "classification":"Changed recurrence estimate of unchanged algorithm; no movement construction change.",
                       "proof_obligations":["Full phase/GS/Schur transfer, already independently reviewed",
                                             "All-size growing geometric unroll with explicit leaf lower bound",
                                             "Separate verified finite circuit and frame/rank primitives",
                                             "Original complete multiplication theorem and unaffected fixed-tape interfaces"]})


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic(); source=Path(__file__)
    candidates=[(network_counts(50,509194),'unchanged-h50'),
                (network_counts(50,486200),'envelope-h50'),
                (asymmetric_counts(52,48,549120,426624),'verified-asymmetric-p52q48')]
    result={"generated_at":datetime.now(timezone.utc).isoformat(),"campaign":"20261007T222521Z",
            "campaign_start":"2026-10-07T22:25:21Z","campaign_deadline":"2026-10-08T08:25:21Z",
            "provenance":check_sources(args.upstream),
            "source_sha256":{source.name:hashlib.sha256(source.read_bytes()).hexdigest()},
            "recurrence_checks":recurrence_identity_checks(),
            "witnesses":[witness(counts,name) for counts,name in candidates]}
    result['elapsed_seconds']=time.monotonic()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for w in result['witnesses']:
        print('PASS exact-unroll candidate',w['name'],'kappa',w['parameters']['kappa'],
              'improvement >=',w['improvement_factor_decimal_lower'])


if __name__=='__main__': main()
