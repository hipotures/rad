#!/usr/bin/env python3
"""Exact finite-field cut ranks and scoped direction counterexamples.

The field prime65537 maps i to256, so nonzero determinants also witness
nonzero Gaussian-rational determinants. This checks finite instances of the
written lemma, rather than proving its all-size statement by enumeration.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from time import perf_counter

P=65537;INV2=pow(2,-1,P);I=256
assert I*I%P==P-1


def rank(matrix):
    rows=[row.copy() for row in matrix];r=0
    for column in range(len(rows[0]) if rows else 0):
        pivot=next((j for j in range(r,len(rows)) if rows[j][column]),None)
        if pivot is None:continue
        rows[r],rows[pivot]=rows[pivot],rows[r]
        inverse=pow(rows[r][column],-1,P)
        rows[r]=[(x*inverse)%P for x in rows[r]]
        for j in range(r+1,len(rows)):
            factor=rows[j][column]
            if factor:rows[j]=[(x-factor*y)%P for x,y in zip(rows[j],rows[r])]
        r+=1
        if r==len(rows):break
    return r


def operator(e,roles,mask,kind):
    n=1<<e;size=n*roles;result=[[int(i==j) for j in range(size)] for i in range(size)]
    active=range(roles) if kind=='target' else [0]
    if kind=='direction':
        a=(1+I)*INV2%P;b=(1-I)*INV2%P
        for role in active:
            for x in range(n):
                row=[0]*size;row[role*n+x]=a;row[role*n+(x^mask)]=(row[role*n+(x^mask)]+b)%P
                result[role*n+x]=row
        return result
    for bit in range(e):
        if not(mask>>bit)&1:continue
        for role in active:
            for x in range(n):
                if(x>>bit)&1:continue
                y=x^(1<<bit);left,right=result[role*n+x],result[role*n+y]
                if kind=='H':
                    result[role*n+x]=[(a+b)*INV2%P for a,b in zip(left,right)]
                    result[role*n+y]=[(a-b)*INV2%P for a,b in zip(left,right)]
                else:
                    a=(1+I)*INV2%P;b=(1-I)*INV2%P
                    result[role*n+x]=[(a*z+b*w)%P for z,w in zip(left,right)]
                    result[role*n+y]=[(b*z+a*w)%P for z,w in zip(left,right)]
    return result


def cut_ranks(matrix,e,input_roles,output_roles):
    n=1<<e;result=[]
    for bit in range(e):
        rows=[r*n+x for r in range(output_roles) for x in range(n) if not(x>>bit)&1]
        cols=[r*n+x for r in range(input_roles) for x in range(n) if(x>>bit)&1]
        result.append(rank([[matrix[i][j] for j in cols] for i in rows]))
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False);started=perf_counter();rows=[]
    for e,roles in [(2,1),(3,2),(4,2),(5,3),(6,2)]:
        n=1<<e
        target=cut_ranks(operator(e,roles,(1<<e)-1,'target'),e,roles,roles)
        assert target==[roles*n//2]*e
        for mask in [1,(1<<(e//2))-1,(1<<e)-1]:
            for kind in ['C','H','direction']:
                observed=cut_ranks(operator(e,roles,mask,kind),e,roles,roles)
                expected=[n//2 if(mask>>bit)&1 else 0 for bit in range(e)]
                assert observed==expected
                rows.append({'selected_bits':e,'roles':roles,'mask':mask,'kind':kind,
                             'cut_ranks':observed,'summed_cut_rank':sum(observed),
                             'coordinate_support':mask.bit_count(),
                             'directional_residual_dimension':1 if kind=='direction' else mask.bit_count()})
        # Copy an original complete role into an additional role; fixed
        # coordinates are retained even in this rectangular operation.
        copy=[[int(i==j) for j in range(roles*n)] for i in range(roles*n)]
        copy.extend([[int(j==x) for j in range(roles*n)] for x in range(n)])
        assert cut_ranks(copy,e,roles,roles+1)==[0]*e
    result={'status':'coordinate cut-rank controls and dense-direction scope negatives passed',
            'field':{'prime':P,'image_of_i':I},'rows':rows,'seconds':perf_counter()-started,
            'exact_rank_ledger_example':{'target_roles':10,'target_selected_bits':8,
                'small_children':16,'small_child_bits':4,'whole_children':2,
                'rank_moment':str(Fraction(16,10)*Fraction(4,8)+Fraction(2,10)),
                'conclusion':'rank moment equals1; replacing the two whole children by one makes the claimed exact compiler impossible'},
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'limitation':'Finite exact controls only; the written proof supplies all-size scope. No approximate or nonlinear compiler exclusion is inferred.'}
    (out/'certificate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'seconds':result['seconds'],'controls':len(rows)}))


if __name__=='__main__':main()
