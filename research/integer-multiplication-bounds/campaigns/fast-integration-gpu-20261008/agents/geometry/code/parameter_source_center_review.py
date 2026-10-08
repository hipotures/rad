#!/usr/bin/env python3
"""Direct rational source/center conjugation, independent of native profilers."""
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,json

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def mv(A,x):return [dot(row,x) for row in A]

def check(h,beta):
    H=[[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
    Hi=[[Q(i==j)+Q(1,9-h) for j in range(h)] for i in range(h)]
    for i in range(h):
        for j in range(h):assert sum(H[i][k]*Hi[k][j] for k in range(h))==Q(i==j)
    L=[[Q(i==j)-beta for j in range(h)] for i in range(h)]
    Li=[[Q(i==j)+beta/(1-h*beta) for j in range(h)] for i in range(h)]
    t=[Q(i<3) for i in range(h)];Ht=mv(H,t);assert dot(t,Ht)==2
    p=mv(L,t);xi=mv(Li,[v/2 for v in Ht]);assert dot(p,xi)==1
    gamma=(9*beta-1)/(3*(1-h*beta));assert p==[v-3*beta for v in t];assert xi==[(v+gamma)/2 for v in t]
    normal=[Q(1)-3*Q(i==0) for i in range(h)];p0=[v/Q(-3) for v in mv(Hi,normal)]
    assert p0==[Q(i==0)+Q(2,h-9) for i in range(h)]
    nu0=[v/dot(normal,p0) for v in normal];pc=mv(L,p0);nuc=mv(Li,nu0);assert dot(pc,nuc)==1
    assert pc==[Q(i==0)+(2-3*beta*(h-3))/(h-9) for i in range(h)]
    assert nuc==[(h-9)*(1-3*beta)/(12*(1-h*beta))-Q(h-9,4)*Q(i==0) for i in range(h)]
    assert all(p) and all(xi) and all(pc) and all(nuc)
    dual=-gamma/3;gd=(9*dual-1)/(3*(1-h*dual));assert gd==-3*beta
    pd=[v-3*dual for v in t];xid=[(v+gd)/2 for v in t]
    assert [a*b for a,b in zip(p,xi)]==[a*b for a,b in zip(pd,xid)]
    serialize=lambda a:[str(x) for x in a]
    return dict(h=h,beta=str(beta),gamma=str(gamma),conjugate_beta=str(dual),determinant=str(1-h*beta),
                source_primal_inside_outside=serialize([p[0],p[-1]]),source_dual_inside_outside=serialize([xi[0],xi[-1]]),
                source_products_inside_outside=serialize([p[0]*xi[0],p[-1]*xi[-1]]),
                copied_center_primal_inside_outside=serialize([pc[0],pc[-1]]),copied_center_dual_inside_outside=serialize([nuc[0],nuc[-1]]),
                source_normalization_one=True,center_normalization_one=True,every_coordinate_nonzero=True,conjugate_source_products_identical=True,
                coefficient_max=str(max(abs(x) for v in [p,xi,pc,nuc] for x in v)),minimum_coordinate=str(min(abs(x) for v in [p,xi,pc,nuc] for x in v)),
                scope='One representative triple and center suffice by coordinate-permutation symmetry; ordered projector profiles and full source-pair data remain separate')

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
rows=[check(h,b) for h,b in [(23,Q(1,51)),(23,Q(1,6)),(23,Q(5,3)),(23,Q(1,24)),(25,Q(1,57)),(25,Q(1,6))]]
a.output.write_text(json.dumps(dict(status='PASS DIRECT RATIONAL NEW-PARAMETER SOURCE AND COPIED-CENTER REVIEW',rows=rows,
    completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
print(json.dumps(dict(status='PASS',parameters=len(rows))),flush=True)
