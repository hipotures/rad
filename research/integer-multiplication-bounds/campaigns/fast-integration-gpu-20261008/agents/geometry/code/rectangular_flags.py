#!/usr/bin/env python3
"""Exact modular rectangular extension of the public common flag construction.

Mathematical idea credited to Swapnil Jain's flag-basis.tex (round5 pinned in
the campaign input manifest). The rectangular supports and completed-basis
experiments here are new campaign work. Finite modular tests are not an
all-size transfer certificate.
"""
from datetime import datetime, timezone
from pathlib import Path
from hashlib import sha256
import argparse,json,random,time
import numpy as np

PRIME=65521
def mm(A,B):return (A@B)%PRIME
def inv(A):
    n=A.shape[0];M=np.concatenate((A%PRIME,np.eye(n,dtype=np.int64)),axis=1)
    for c in range(n):
        candidates=np.flatnonzero(M[c:,c])
        if not len(candidates):raise ValueError('singular matrix')
        k=c+int(candidates[0]);M[[c,k]]=M[[k,c]]
        M[c]=M[c]*pow(int(M[c,c]),-1,PRIME)%PRIME
        f=M[:,c].copy();f[c]=0
        M=(M-f[:,None]*M[c])%PRIME
    return M[:,n:]
def pivots(A):
    M=A.copy()%PRIME;rows,cols=M.shape;out=[];r=0
    for c in range(cols):
        candidates=np.flatnonzero(M[r:,c])
        if not len(candidates):continue
        k=r+int(candidates[0]);M[[r,k]]=M[[k,r]]
        M[r]=M[r]*pow(int(M[r,c]),-1,PRIME)%PRIME
        f=M[:,c].copy();f[r]=0;M=(M-f[:,None]*M[r])%PRIME
        out.append(c);r+=1
        if r==rows:break
    return out
def profile(A):
    M=A.copy()%PRIME;out=[];available=list(range(M.shape[1]))
    for i in range(M.shape[0]):
        q=next((j for j in reversed(available) if M[i,j]),None)
        if q is None:continue
        available.remove(q);out.append((i,q));f=M[:,q].copy();f[:i+1]=0
        norm=M[i]*pow(int(M[i,q]),-1,PRIME)%PRIME
        M=(M-f[:,None]*norm)%PRIME
    widths=[]
    for k,(i,j) in enumerate(out):
        if k and i==out[k-1][0]+1 and j==out[k-1][1]+1:widths[-1]+=1
        else:widths.append(1)
    return out,widths

def build(a,b,seed):
    assert 2<=a<=b;delta=b-a;m=a*b
    rng=np.random.default_rng(seed)
    R=np.zeros((b,a,b),dtype=np.int64);C=np.zeros_like(R)
    for i in range(b):R[i,:min(i+1,a),:i+1]=rng.integers(1,PRIME,size=(min(i+1,a),i+1))
    R[b-1,a-1,b-1]=0
    for j in range(b):
        r0=max(0,j-delta);C[j,r0:,j:]=rng.integers(1,PRIME,size=(a-r0,b-j))
        if j==b-1:continue
        for i in range(j,b):
            C[j,r0,i]=0;s=int(np.sum(R[i]*C[j])%PRIME)
            assert R[i,r0,i]
            C[j,r0,i]=-s*pow(int(R[i,r0,i]),-1,PRIME)%PRIME
    assert np.all(mm(R.reshape(b,m),C.reshape(b,m).T)==0)
    U=rng.integers(1,PRIME,size=(a,a),dtype=np.int64);V=rng.integers(1,PRIME,size=(b,b),dtype=np.int64)
    Ui,Vi=inv(U),inv(V)
    lam=np.array([mm(mm(U,r),V.T).reshape(m) for r in R])
    mu=np.array([mm(mm(Ui.T,c),Vi).reshape(m) for c in C]).T
    assert np.all(mm(lam,mu)==0)
    pc=pivots(lam);assert len(pc)==b
    free=[i for i in range(m) if i not in pc];right=inv(lam[:,pc])
    Z=np.zeros((m,b),dtype=np.int64);Z[pc,:]=right
    K=np.zeros((m,m-b),dtype=np.int64);K[free,:]=np.eye(m-b,dtype=np.int64)
    K[pc,:]=-mm(right,lam[:,free])%PRIME
    assert np.all(mm(lam,K)==0)
    assert len(pivots(mu.T))==b
    W=mm(K,rng.integers(0,PRIME,size=(m-b,m-2*b),dtype=np.int64))
    Z=(Z+mm(K,rng.integers(0,PRIME,size=(m-b,b),dtype=np.int64)))%PRIME
    X=np.concatenate((Z,W,mu),axis=1);S=inv(X)
    assert np.array_equal(S[:b],lam)
    assert np.array_equal(mm(S,X),np.eye(m,dtype=np.int64))
    return R,C,U,V,S,X

def line(n,rng):
    u=rng.integers(1,PRIME,size=n,dtype=np.int64);g=rng.integers(1,PRIME,size=n,dtype=np.int64)
    z=int(u@g%PRIME);assert z
    g=g*pow(z,-1,PRIME)%PRIME
    return u,g
def null_apply(X,u,g,v,h,a,b):
    d=X.shape[1];T=X.reshape(a,b,d)
    first=u[:,None,None]*np.sum(g[:,None,None]*T,axis=0)[None,:,:]%PRIME
    second=v[None,:,None]*np.sum(h[None,:,None]*T,axis=1)[:,None,:]%PRIME
    scalar=np.sum(g[:,None,None]*second,axis=0)%PRIME
    intersection=u[:,None,None]*scalar[None,:,:]%PRIME
    return (first+second-intersection).reshape(a*b,d)%PRIME
def inspect(a,b,seed,pairs):
    start=time.monotonic();R,C,U,V,S,X=build(a,b,seed);m=a*b;d=a+b-1;rng=np.random.default_rng(seed+123)
    Ui,Vi=inv(U),inv(V);controls=[]
    for k in range(pairs):
        u,g=line(a,rng);v,h=line(b,rng)
        Pa=np.outer(u,g)%PRIME;Pb=np.outer(v,h)%PRIME
        # The two complete factor corners are structurally triangular.
        Ca=mm(S[:a],np.kron(np.eye(a,dtype=np.int64),Pb)%PRIME)
        Ca=mm(Ca,X[:,-a:])
        Cb=mm(S[:b],np.kron(Pa,np.eye(b,dtype=np.int64))%PRIME)
        Cb=mm(Cb,X[:,-b:])
        assert not np.any(np.triu(Ca,1)) and np.all(np.diag(Ca))
        assert not np.any(np.triu(Cb,1)) and np.all(np.diag(Cb))
        M=mm(S[:d],null_apply(X[:,-d:],u,g,v,h,a,b))
        pp,ww=profile(M);assert len(pp)==d
        data=ww+[m-2*d];assert sum(data)==m-d
        controls.append(dict(pair=k,null_corner_pivots=pp,null_corner_widths=ww,data_profile=data,
                             corner_sha256=sha256(M.tobytes()).hexdigest(),
                             merged_auxiliary_profiles=[[a,m-2*a],[b,m-2*b]],
                             all_strictly_upper_auxiliary_entries_zero=True))
    return dict(a=a,b=b,seed=seed,prime=PRIME,controls=controls,elapsed_seconds=time.monotonic()-start,
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                basis_sha256=sha256(S.tobytes()+X.tobytes()).hexdigest(),
                status='exact finite modular construction; no generic data profile proof',
                completed_utc=datetime.now(timezone.utc).isoformat())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--a',type=int,required=True);ap.add_argument('--b',type=int,required=True);ap.add_argument('--seed',type=int,required=True);ap.add_argument('--pairs',type=int,default=5);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    result=inspect(args.a,args.b,args.seed,args.pairs);args.output.parent.mkdir(parents=True,exist_ok=True);assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(dimensions=[args.a,args.b],seed=args.seed,profiles=[c['data_profile'] for c in result['controls']],seconds=result['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
