#!/usr/bin/env python3
"""Direct rational Gram/projector and ordered-pivot checks of native controls."""
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from math import lcm
from pathlib import Path
import argparse,json,time
from independent_axis_review import read


def mm(A,B):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]


def inverse(A):
    n=len(A);M=[row[:]+[Q(i==j) for j in range(n)] for i,row in enumerate(A)]
    for i in range(n):
        k=next(k for k in range(i,n) if M[k][i]);M[i],M[k]=M[k],M[i]
        d=M[i][i];M[i]=[x/d for x in M[i]]
        for j in range(n):
            if j!=i and M[j][i]:
                z=M[j][i];M[j]=[x-z*y for x,y in zip(M[j],M[i])]
    return [row[n:] for row in M]


def projector(h,F,sy,basis):
    if F==0:return [[Q(i==j) if sy else Q(0) for j in range(h)] for i in range(h)]
    if F.bit_count()==3:columns=[[Q(F>>i&1) for i in range(h)]]
    else:
        s=3-F.bit_count();columns=[]
        for c in sorted({abs(x) for x in sy if abs(x)>1}):
            sigma=sum((1 if x>0 else -1) for x in sy if abs(x)==c)
            columns.append([Q(sigma if F>>i&1 else s*(1 if sy[i]>0 else -1) if abs(sy[i])==c else 0) for i in range(h)])
    B=list(map(list,zip(*columns)));H=[[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
    P=mm(mm(mm(B,inverse(mm(mm(columns,H),B))),columns),H)
    if basis.startswith('beta:'):
        _,numerator,denominator=basis.split(':');t=-Q(int(numerator),int(denominator))
    else:t={'negative':Q(-4,3*(h+3)),'fixed':Q(1),'negative-transpose':Q(1,3),'fixed-transpose':Q(-10,9*(h+1))}[basis]
    v=t/(1+h*t)
    rows=[sum(row) for row in P];cols=[sum(row[j] for row in P) for j in range(h)];total=sum(rows)
    return [[P[i][j]+t*cols[j]-v*rows[i]-t*v*total for j in range(h)] for i in range(h)]


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--witness',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--samples',type=int,default=12);a=ap.parse_args();start=time.monotonic();doc=json.loads(a.witness.read_text());p=doc['producer']
    dag=Path(p['dag_path']);labels=Path(str(dag)+'.positive');h,v,n,q,args,core,cover,roots,kind,active,ranks,forced,symbols=read(dag,labels)
    frames=[(0,()),(0,(1,))];lookup={}
    for node in range(1,n):
        if not active[node]:continue
        key=(forced[node],tuple(symbols[node*h:(node+1)*h]))
        if key not in lookup:lookup[key]=len(frames);frames.append(key)
    audit=Path(doc['provenance']['transition_audit']);rows=json.loads(audit.read_text())['transitions'];basis=doc['fixed_profile']['basis']
    selected=[]
    for key in [lambda x:(x['prime_count'],x['rank']),lambda x:(len(x['pivots']),x['count']),lambda x:(x['rank']==2,x['count']),lambda x:(x['count'],x['rank'])]:
        for row in sorted(rows,key=key,reverse=True)[:max(1,a.samples//4)]:
            if row not in selected:selected.append(row)
    cache={};checks=[]
    for at,row in enumerate(selected):
        for fid in [row['a'],row['b']]:
            if fid not in cache:cache[fid]=projector(h,*frames[fid],basis)
        A=cache[row['a']];B=cache[row['b']];M=[[y-x for x,y in zip(u,v)] for u,v in zip(A,B)]
        assert mm(A,B)==A and mm(B,A)==A
        assert mm(M,M)==M and sum(M[i][i] for i in range(h))==row['rank']
        denominator=lcm(*(x.denominator for frame in [A,B] for values in frame for x in values))
        assert denominator==int(row['integer_denominator'])
        Z=max(abs(x*denominator) for values in M for x in values);assert Z.denominator==1 and Z==int(row['entry_bound'])
        bound=row['rank']**((row['rank']+1)//2)*int(Z)**row['rank'];assert bound==int(row['minor_bound'])
        pivots=[];E=[values[:] for values in M]
        for i in range(h):
            nz=[j for j in range(h) if E[i][j]]
            if not nz:continue
            j=nz[-1];pivots.append([i,j])
            for k in range(i+1,h):
                z=E[k][j]/E[i][j]
                if z:
                    for c in range(j+1):E[k][c]-=z*E[i][c]
        assert pivots==row['pivots']
        checks.append(dict(a=row['a'],b=row['b'],rank=row['rank'],prime_count=row['prime_count'],exact_pivots=pivots,
                           direct_gram_projector_pass=True,nested_idempotents_pass=True,integer_bound_pass=True))
        print(json.dumps(dict(completed=at+1,total=len(selected),elapsed_seconds=time.monotonic()-start)),flush=True)
    result=dict(status='PASS INDEPENDENT DIRECT RATIONAL PHYSICAL-PROFILE CONTROLS',h=h,basis=basis,checks=checks,
                input_sha256={str(path):sha256(path.read_bytes()).hexdigest() for path in [a.witness,dag,labels,audit]},
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start,
                completed_utc=datetime.now(timezone.utc).isoformat(),scope='Selected high-bound/high-rank/large-count/rank-two controls, separate from full CRT and complete compiler')
    assert not a.output.exists();a.output.write_text(json.dumps(result,indent=2)+'\n')
