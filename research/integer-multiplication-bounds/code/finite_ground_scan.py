#!/usr/bin/env python3
"""Exact ground-size/orientation screening, with pinned downstream arithmetic.

The count screen interns every pair-star identity without materializing all
global edges. Its count before global dead-node pruning is a conservative role
upper bound, calibrated against complete witnesses. Full graph/frame checks
remain required for headline candidates.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
import json
from math import comb
from pathlib import Path
import time

from finite_block_search import install_reference, make_block_class


def local_geometry(local):
    core=[0]*len(local.args)
    union=[0]*len(local.args)
    star=[]
    nonstar=0
    for node in sorted(local.active):
        if local.args[node] is None:
            a,b=local.inputs[node-1]
            core[node]=union[node]=(1<<a)|(1<<b)
        else:
            a,b=local.args[node]
            core[node]=core[a]&core[b]
            union[node]=union[a]|union[b]
            assert core[node].bit_count()<=1
            if core[node]:
                star.append((core[node].bit_length()-1,union[node]&~core[node]))
            else:
                nonstar+=1
    return star,nonstar


def translations(points):
    """Byte lookup for exact local-to-global vertex-mask permutations."""
    tables=[]
    for offset in range(0,len(points),8):
        table=[0]*256
        for value in range(1,256):
            bit=value&-value
            index=offset+bit.bit_length()-1
            table[value]=table[value^bit] | ((1<<points[index]) if index<len(points) else 0)
        tables.append(table)
    def translate(mask):
        answer=0
        chunk=0
        while mask:
            answer|=tables[chunk][mask&255]
            mask>>=8
            chunk+=1
        return answer
    return translate


def fast_counts(h,ordering="paired",base=4):
    cls=make_block_class()
    cache={}
    stars=set()
    nonstar=0
    local_additions=0
    local_checks=0
    for common in range(h):
        points=[j for j in range(h) if j!=common]
        singleton=None
        if ordering=="paired":
            points=[j for j in range(h) if j//2!=common//2]+[common^1]
        elif ordering=="gap":
            singleton=common//2
        elif ordering!="natural":
            raise ValueError(ordering)
        if singleton not in cache:
            local=cls(h-1,(2,),base,0,singleton)
            checked=local.verify()
            geometry=local_geometry(local)
            cache[singleton]=(geometry,local.additions,checked["circuit_sha256"])
            local_checks+=1
        (local_stars,local_nonstar),additions,digest=cache[singleton]
        nonstar+=local_nonstar
        local_additions+=additions
        translate=translations(points)
        mapped={}
        for fixed,mask in local_stars:
            if mask not in mapped:
                mapped[mask]=translate(mask)
            pair=(1<<common)|(1<<points[fixed])
            stars.add((pair,mapped[mask]))
    q=h*comb(h-1,2)
    additions=nonstar+len(stars)
    R=additions+q
    v=comb(h,3)
    m=h**3
    N=v**3
    W=2*N+2*v*v*(R+h)
    L=3*v*v*h*h
    D=N-2*L
    return {
        "h":h,"ordering":ordering,"base":base,"partial_outputs":q,
        "local_additions_sum":local_additions,"distinct_star_additions":len(stars),
        "nonstar_additions":nonstar,"global_additions_before_pruning":additions,
        "side_role_upper_bound":R,"merged_additions":local_additions-additions,
        "local_exact_map_checks":local_checks,"local_circuit_digests":{str(k):v[2] for k,v in cache.items()},
        "v":v,"m":m,"N":N,"W":W,"L":L,"D":D,"s":W*m-D,
        "eta":str(Q(D,W*m)),
        "count_scope":"Exact support interning before global pruning; conservative upper bound on compiled roles",
    }


def arithmetic(row):
    from certify import Parameters,certify_parameters,network
    from paired_network import guard_certificate
    from search_network import log_integer_bounds
    h=row["h"]
    lo,hi=log_integer_bounds(row["m"])
    scaled=hi*10**8
    log_bound=Q(-(-scaled.numerator//scaled.denominator),10**8)
    eta=Q(row["eta"])
    a=eta/log_bound*Q(999999,10**6)
    original=network(h)
    ac=original["eta_c"]/log_bound*Q(999999,10**6)
    assert eta>a*hi and original["eta_c"]>ac*hi
    beta,epsilon=Q(999,1000),Q(199,1000)
    margin=epsilon*beta*a*a
    kappa=Q(999,1000)*margin
    p=Parameters(1-a,1-ac,epsilon,beta*a,1-(1+beta)*a*a/2,1-beta*a*a,kappa,beta=beta,delta=Q(1,10000),C1=2)
    checked=certify_parameters(p,generalized_beta=True,strict_margin=True,layout_model="nonadjacent",guard_model="stopping",assembly_model="tight-gaussian")
    guard=guard_certificate(h,beta)
    assert 2*original["Lc"]<row["N"]
    assert Q(checked["minimum_margin"])==margin
    return {
        "log_upper":str(log_bound),"bit_saving":str(a),"complex_saving":str(ac),
        "strict_kappa":str(kappa),"limiting_margin":str(margin),
        "kappa_over_advertised_59":str(kappa*2**59),
        "all_recipe_constraints_strict":True,"stopped_guard_valid":True,
        "complex_positive_deficit":True,
        "scope":"Pinned downstream recipe and conservative role bound; global witness reconstruction/frame checks remain required",
    }


def worker(job):
    reference,h,ordering,base=job
    install_reference(reference)
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    row=fast_counts(h,ordering,base)
    row["arithmetic"]=arithmetic(row)
    row["started_utc"]=started
    row["completed_utc"]=datetime.now(timezone.utc).isoformat()
    row["elapsed_seconds"]=time.monotonic()-start
    return row


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--min-h",type=int,default=40)
    parser.add_argument("--max-h",type=int,default=100)
    parser.add_argument("--orderings",default="natural,paired,gap")
    parser.add_argument("--bases",default="2,4")
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--output",required=True)
    parser.add_argument("--summary",required=True)
    args=parser.parse_args()
    assert 1<=args.workers<=4
    started=datetime.now(timezone.utc).isoformat()
    start=time.monotonic()
    hs=range(args.min_h+(args.min_h%2),args.max_h+1,2)
    jobs=[(args.reference,h,o,int(b)) for h in hs for o in args.orderings.split(",") for b in args.bases.split(",")]
    rows=[]
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    with Path(args.output).open("x") as stream,ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(worker,job) for job in jobs]
        for future in as_completed(futures):
            row=future.result()
            rows.append(row)
            stream.write(json.dumps(row,sort_keys=True)+"\n")
            stream.flush()
            if len(rows)%10==0:
                best=max(rows,key=lambda r:Q(r["arithmetic"]["strict_kappa"]))
                print(json.dumps({"completed":len(rows),"jobs":len(jobs),"h":best["h"],"ordering":best["ordering"],"base":best["base"],"roles":best["side_role_upper_bound"],"kappa":best["arithmetic"]["strict_kappa"],"wall_seconds":time.monotonic()-start}),flush=True)
    rows.sort(key=lambda r:Q(r["arithmetic"]["strict_kappa"]),reverse=True)
    result={"started_utc":started,"completed_utc":datetime.now(timezone.utc).isoformat(),"wall_seconds":time.monotonic()-start,"summed_case_seconds":sum(r["elapsed_seconds"] for r in rows),"settings":vars(args),"reference_commit":"bcd4ebde8692383539f8a48734e5fbf3a18a32c2","cases":len(rows),"best_20":rows[:20],"scope":"Bounded exact count/recipe screen; every promoted graph must be reconstructed and checked separately"}
    Path(args.summary).parent.mkdir(parents=True,exist_ok=True)
    Path(args.summary).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"summary":args.summary,"cases":len(rows),"wall_seconds":result["wall_seconds"],"best":rows[0]},indent=2))


if __name__=="__main__":
    main()
