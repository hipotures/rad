#!/usr/bin/env python3
"""Scoped exact checks for affine centers and invariant triple fitting maps.

This checks restrictions of two proposed representation families, not a
lower bound for unrestricted complex arithmetic circuits. Codex-assisted.
"""
import argparse
from fractions import Fraction as Q
from itertools import combinations
import json
from math import comb
from pathlib import Path


def rational_rank(rows,cols):
    pivots={}
    for source in rows:
        row=list(map(Q,source))
        for pivot,basis in sorted(pivots.items()):
            if row[pivot]:
                scale=row[pivot]
                row=[a-scale*b for a,b in zip(row,basis)]
        pivot=next((j for j,a in enumerate(row) if a),None)
        if pivot is not None:
            scale=row[pivot]
            pivots[pivot]=[a/scale for a in row]
    return len(pivots)


def binary_rank(rows):
    pivots={}
    for row in rows:
        while row:
            bit=row.bit_length()-1
            if bit not in pivots:
                pivots[bit]=row
                break
            row ^= pivots[bit]
    return len(pivots)


def affine_support_checks(h):
    if h<8:raise ValueError('scoped proof starts at h=8')
    triples=list(combinations(range(h),3))
    result=[]
    for weight in range(1,h+1):
        normal=(1<<weight)-1
        constraints=[tuple(int(j in t) for j in range(h)) for t in triples
                     if sum(j<weight for j in t)%2]
        nullity=h-rational_rank(constraints,h)
        predicted=1 if weight in (1,2,h-2,h-1) else 0
        if nullity!=predicted:raise ValueError('classification failed')
        row=dict(normal_weight=weight,coefficient_nullity=nullity)
        if nullity:
            if weight in (1,2):
                coefficients=[-2 if j<weight else 1 for j in range(h)]
            elif weight==h-2:
                coefficients=[int(j==h-2)-int(j==h-1) for j in range(h)]
            else:
                coefficients=[int(j==h-1) for j in range(h)]
            supports=[sum(1<<j for j in t) for t in triples
                      if sum(coefficients[j] for j in t)]
            rank=binary_rank(supports)
            if rank!=h-1 or any((t&normal).bit_count()%2 for t in supports):
                raise ValueError('support frame rank failed')
            row.update(coefficients=coefficients,support_span_rank=rank,
                       hyperplane_nondegenerate=bool(weight%2))
        result.append(row)
    return dict(h=h,hyperplane_classification=result,
                scope='Exact finite representative for every normal weight; permutation symmetry used')


def invariant_eigenvalues(h,c1,c2):
    c0=-c1
    c3=1-2*c1-3*c2
    return [c0*comb(h,3)+c1*3*comb(h-1,2)+c2*3*(h-2)+c3,
            c1*comb(h-2,2)+c2*2*(h-3)+c3,
            c2*(h-4)+c3,c3]


def multiplicities(h):
    return [1,h-1,comb(h,2)-h,comb(h,3)-comb(h,2)]


def invariant_minrank(h):
    # A permutation-invariant fitting matrix is f(|S intersect T|),
    # f(1)=0 and f(3)=1. Expand f in binomial polynomials B_j. Its four
    # rational eigenspaces are the nested inclusion incidence quotients.
    # Find every intersection of two eigenvalue-zero lines in (c1,c2).
    origin=invariant_eigenvalues(h,Q(0),Q(0))
    at1=invariant_eigenvalues(h,Q(1),Q(0))
    at2=invariant_eigenvalues(h,Q(0),Q(1))
    lines=[(a-o,b-o,o) for o,a,b in zip(origin,at1,at2)]
    candidates=set()
    for x,y in combinations(lines,2):
        a,b,c=x; d,e,f=y
        det=a*e-b*d
        if det:
            candidates.add(((b*f-c*e)/det,(c*d-a*f)/det))
    if not candidates:raise ValueError('no candidate intersections')
    records=[]
    dims=multiplicities(h)
    for c1,c2 in sorted(candidates):
        values=invariant_eigenvalues(h,c1,c2)
        rank=sum(dim for dim,value in zip(dims,values) if value)
        records.append(dict(c1=str(c1),c2=str(c2),eigenvalues=list(map(str,values)),rank=rank))
    actual=min(row['rank'] for row in records)
    expected=h-1 if h==9 else h
    if actual!=expected:raise ValueError('unexpected invariant fitting minrank')
    return dict(h=h,eigenspace_dimensions=dims,candidates=records,
                minimum_rank=actual,current_center_rank=expected,
                frozen_center_deficit=comb(h,3)**2-2*comb(h,3)*h*(h-1),
                scope='Permutation-invariant rational fitting matrices only; nonsymmetric maps unrestricted')


def direct_eigen_controls(h):
    # Independent exact direct matrix multiplications on explicit harmonic
    # vectors certify eigenvalues for all four degrees, using B_j(S,T).
    triples=list(combinations(range(h),3))
    vectors=[]
    for degree in range(4):
        pairs=[(2*j,2*j+1) for j in range(degree)]
        vector=[]
        for t in triples:
            value=1
            for a,b in pairs:value*=int(a in t)-int(b in t)
            vector.append(value)
        if not any(vector):raise ValueError('zero harmonic test vector')
        vectors.append(vector)
    c1,c2=Q(2,7),Q(1,5)
    coefficients=[-c1,c1,c2,1-2*c1-3*c2]
    eigenvalues=invariant_eigenvalues(h,c1,c2)
    for degree,vector in enumerate(vectors):
        for s in triples:
            actual=Q(0)
            for t,value in zip(triples,vector):
                inter=len(set(s)&set(t))
                actual+=value*sum(coefficients[j]*comb(inter,j)
                                  for j in range(4) if j<=inter)
            expected=eigenvalues[degree]*vector[triples.index(s)]
            if actual!=expected:raise ValueError('direct eigenvalue control failed')
    return dict(h=h,direct_harmonic_vectors=4,exact_matrix_vector_checks=4*len(triples))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output must be new')
    result=dict(affine_features=[affine_support_checks(h) for h in (8,10,12,16,28)],
                invariant_minranks=[invariant_minrank(h) for h in (7,8,9,10,12,16,28)],
                direct_controls=[direct_eigen_controls(h) for h in (7,8)])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('Affine feature classifications and invariant fitting-map ranks pass exact controls.')


if __name__=='__main__':main()
