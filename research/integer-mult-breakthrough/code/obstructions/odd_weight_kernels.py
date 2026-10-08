#!/usr/bin/env python3
"""Exact odd-subset central kernels and binary feature-span discriminators.

These are scalar identities and finite label-space checks, not complete
physical networks, characteristic distributions or asymptotic exponents.
The generalization is motivated by the pinned original triple construction.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time


def kernel(k,t):
    if k < 3 or not k & 1:
        raise ValueError("Odd subset size k >= 3 required")
    value = Q(1)
    for root in range(1,k,2):
        value *= Q(t-root,k-root)
    return value


def coefficients(k):
    r = (k-1)//2
    row = [kernel(k,t) for t in range(r+1)]
    result = []
    while row:
        result.append(row[0])
        row = [b-a for a,b in zip(row,row[1:])]
    if any(c.denominator & (c.denominator-1) for c in result):
        raise ValueError("A proposed feature coefficient is not Gaussian dyadic")
    return result


def polynomial_discriminator(k):
    values = [kernel(k,t) for t in range(k+1)]
    cs = coefficients(k)
    for t,value in enumerate(values):
        if sum((cs[j]*comb(t,j) for j in range(min(t,len(cs)-1)+1)),Q()) != value:
            raise ValueError("Newton feature expansion mismatch")
        if value.denominator & (value.denominator-1):
            raise ValueError("Integer intersection value is not dyadic")
        if t & 1 and t < k and value != 0:
            raise ValueError("An off-diagonal odd intersection does not vanish")
    if values[k] != 1:
        raise ValueError("Self coefficient is not one")
    return {"k":k,"feature_degree":len(cs)-1,"kernel_values":list(map(str,values)),
            "binomial_feature_coefficients":list(map(str,cs)),
            "all_intersection_values_and_features_dyadic":True,
            "scope":"Exact scalar polynomial; side support is binary-orthogonal, side computation cost remains open"}


def add_basis(basis,vector):
    while vector:
        pivot = vector.bit_length()-1
        if pivot in basis:
            vector ^= basis[pivot]
        else:
            basis[pivot] = vector
            return


def binary_rank(rows):
    basis = {}
    for vector in rows:
        add_basis(basis,vector)
    return len(basis)


def gram_rank(basis):
    rows = list(basis.values())
    gram = [sum((((u & v).bit_count() & 1) << j) for j,v in enumerate(rows)) for u in rows]
    return binary_rank(gram)


def span_discriminator(h,k):
    if not h % 2 == 0 or not 3 <= k < h or not k & 1:
        raise ValueError("Even ground dimension and odd proper subset size required")
    degree = (k-1)//2
    stars = {tuple(feature):{} for j in range(degree+1) for feature in combinations(range(h),j)}
    vertices = []
    for subset in combinations(range(h),k):
        mask = sum(1<<i for i in subset)
        vertices.append(mask)
        for j in range(degree+1):
            for feature in combinations(subset,j):
                add_basis(stars[feature],mask)
    hist = {}
    for feature,basis in stars.items():
        j = len(feature)
        rank = len(basis)
        g = gram_rank(basis)
        if rank != h-j or g != rank:
            raise ValueError("Finite feature star is not the advertised nondegenerate span")
        record = hist.setdefault(j,{"count":0,"source_span_rank":rank,"gram_rank":g})
        record["count"] += 1
    local_loss = sum(comb(h,j)*(h-j) for j in range(degree+1))
    pair_complement = {}
    if k == 5:
        for mask in vertices:
            if mask & 3 != 3:
                add_basis(pair_complement,mask)
        if len(pair_complement) != h or gram_rank(pair_complement) != h:
            raise ValueError("Selected quintuple complement gather does not span full space")
    return {"h":h,"k":k,"vertices":len(vertices),
            "feature_stars":{str(j):v for j,v in sorted(hist.items())},
            "conservative_sum_of_feature_span_dimensions":local_loss,
            "hypothetical_two_stage_deficit_factor_v_minus_2L":len(vertices)-2*local_loss,
            "pair_complement_full_span_checked":k==5,
            "scope":"Exact finite source-feature spans and Gram matrices; scatter and return transitions are not certified"}


def scalar_discriminator(h,k):
    subsets = [frozenset(s) for s in combinations(range(h),k)]
    values = {t:kernel(k,t) for t in range(k+1)}
    pairs = orthogonal_sides = 0
    for source in subsets:
        for target in subsets:
            t = len(source & target)
            central = values[t]
            side = -central if source != target and not t & 1 else Q()
            if central+side != Q(source==target):
                raise ValueError("Central plus even-intersection side does not give identity")
            if side and t & 1:
                raise ValueError("A nonzero side is not orthogonal in the binary label field")
            pairs += 1
            orthogonal_sides += bool(side)
    return {"h":h,"k":k,"vertices":len(subsets),"all_ordered_pairs_checked":pairs,
            "nonzero_binary_orthogonal_sides":orthogonal_sides,
            "scope":"Exact complete scalar delta map; no scalar DAG or cost claim"}


def center_reconstruction():
    # Each five-subset contributes to exactly ten pair centers, and four pair
    # centers through every contained point. Replace two selected pair features
    # by their complements, leaving an invertible dyadic coefficient identity.
    h = 10
    pairs = list(combinations(range(h),2))
    replaced = pairs[:2]
    for source in combinations(range(h),5):
        source = set(source)
        ps = {pair:Q(set(pair) <= source) for pair in pairs}
        ds = {pair:1-ps[pair] for pair in replaced}
        total = (sum((v for pair,v in ps.items() if pair not in replaced),Q())-
                 sum(ds.values(),Q()))/8
        if total != 1:
            raise ValueError("Two-complement total reconstruction failed")
        recovered = dict(ps)
        for pair in replaced:
            recovered[pair] = total-ds[pair]
        if recovered != ps:
            raise ValueError("Pair-center recovery failed")
        for i in range(h):
            gi = sum((v for pair,v in recovered.items() if i in pair),Q())/4
            if gi != Q(i in source):
                raise ValueError("Singleton-center elimination identity failed")
    # A corrupt coefficient destroys a required odd-intersection zero.
    cs = coefficients(5)
    cs[1] += Q(1,8)
    corrupted = sum((cs[j]*comb(3,j) for j in range(3)),Q())
    if corrupted == 0:
        raise ValueError("Corrupted odd-intersection control failed")
    return {"h":h,"source_basis_columns":comb(h,5),"replaced_pairs":[list(p) for p in replaced],
            "dyadic_total_denominator":8,"dyadic_singleton_denominator":4,
            "scalar_reconstruction_exact":True,"corrupt_odd_intersection_residual":str(corrupted),
            "scope":"Scalar center reconstruction only; gather/scatter/undo frame schedules and temporary roles must still be charged"}


def task(spec):
    kind,arguments = spec
    functions = {"polynomial":polynomial_discriminator,"span":span_discriminator,
                 "scalar":scalar_discriminator}
    return {"kind":kind,"result":functions[kind](*arguments)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--bounded",action="store_true")
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.output and args.output.exists():
        parser.error("Workers must be positive and output must be fresh")
    start = time.monotonic()
    specs = [("polynomial",(k,)) for k in (3,5,7,9,11)]
    spans = [(8,3),(8,5),(10,5),(10,7)] if args.bounded else [(8,3),(8,5),(10,5),(10,7),(12,7),(12,9),(14,7),(16,5),(20,5)]
    specs += [("span",case) for case in spans]
    specs += [("scalar",case) for case in [(8,3),(8,5),(10,7)]]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(task,specs))
    report = {"status":"EXACT FINITE ALGEBRAIC EVIDENCE","recorded_utc":datetime.now(timezone.utc).isoformat(),
              "workers":args.workers,"randomness":"None; exhaustive deterministic finite cases",
              "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "cases":cases,"center_reconstruction":center_reconstruction(),
              "seconds":time.monotonic()-start,
              "not_proved":["efficient even-intersection side circuit","paid common-frame scatter and restoration",
                            "complete characteristic child distribution","new binary primitive",
                            "kappa >= 1e-4","all-size multiplication transfer"]}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf-8') as handle:
            handle.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps({"status":report["status"],"workers":args.workers,"cases":len(cases),"seconds":report["seconds"]}))


if __name__ == "__main__":
    main()
