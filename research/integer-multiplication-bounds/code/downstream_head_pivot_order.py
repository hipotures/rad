#!/usr/bin/env python3
"""Full complementary flags do not guarantee a free increasing NE batch.

A nondegenerate rational projector has both flags full, but its canonical
head pivots are reversed. This does not exclude stronger common-basis or
physically costed gather constructions.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


def mm(A,B):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]


def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]


def inverse(A):
    n=len(A);I=eye(n);B=[list(map(Q,row))+I[i] for i,row in enumerate(A)]
    for j in range(n):
        p=next(i for i in range(j,n) if B[i][j]);B[j],B[p]=B[p],B[j]
        x=B[j][j];B[j]=[a/x for a in B[j]]
        for i in range(n):
            if i!=j:
                x=B[i][j];B[i]=[a-x*b for a,b in zip(B[i],B[j])]
    return [r[n:] for r in B]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert not args.output.exists()
    m,d=6,2;T=[[Q(1),Q(1)],[Q(1),Q(2)]]
    U=[[Q(i==j) if i<2 else Q(i-4==j) for j in range(d)] for i in range(m)]
    V=[[Q(i==j)-T[i][j] if j<2 else T[i][j-4] if j>=4 else Q(0) for j in range(m)] for i in range(d)]
    assert mm(V,U)==eye(d);P=mm(U,V);I=eye(m);A=[[x-y for x,y in zip(r,s)] for r,s in zip(I,P)];assert mm(P,P)==P
    # ker(V) has columns (middle e2,e3), plus front identity vectors
    # whose back coordinates solve Vback*x=-(I-T)*front.
    Ti=inverse(T);frontback=mm(Ti,[[T[i][j]-Q(i==j) for j in range(d)] for i in range(d)])
    ker=[[Q(i==j+2) for j in range(2)]+[Q(i==j) if i<2 else frontback[i-4][j] if i>=4 else Q(0) for j in range(2)] for i in range(m)]
    assert mm(V,ker)==[[Q(0)]*4 for _ in range(d)]
    S=[U[i]+ker[i] for i in range(m)];Si=inverse(S);G=mm([list(x) for x in zip(*Si)],Si)
    assert mm(G,P)==mm([list(x) for x in zip(*P)],G)
    B=[r.copy() for r in A];Pi=[[Q(0)]*m for _ in range(m)];pivots=[]
    for i in range(m):
        js=[j for j,x in enumerate(B[i]) if x]
        if not js:continue
        p=max(js);v=B[i][p];B[i]=[x/v for x in B[i]]
        for k in range(i+1,m):
            c=B[k][p];B[k]=[x-c*y for x,y in zip(B[k],B[i])]
        for j in range(p):
            c=B[i][j]
            for k in range(m):B[k][j]-=c*B[k][p]
        Pi[i][p]=1;pivots.append((i,p))
    assert B==Pi and pivots==[(0,5),(1,4),(2,2),(3,3)]
    actual=[105,104];increasing_child=[104,105];assert actual!=increasing_child
    result=dict(status='PASS SCOPED NEGATIVE: FULL FLAGS ALONE DO NOT ENSURE INCREASING HEAD ORDER',
        generated_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        m=m,kernel_dimension=d,U=[[str(x) for x in r] for r in U],V=[[str(x) for x in r] for r in V],
        both_front_and_back_flags_invertible=True,exact_rational_positive_metric_constructed=True,
        projector_idempotent_metric_self_adjoint=True,canonical_lower_lower_pivots=pivots,
        exact_required_head_order=actual,free_increasing_contiguous_child_order=increasing_child,
        scope='Rejects deriving a free increasing whole-bit head batch from flag invertibility alone. Stronger simultaneous-basis constraints, costed address routing, or actual physical telescopes remain separate hypotheses.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'])


if __name__=='__main__':main()
