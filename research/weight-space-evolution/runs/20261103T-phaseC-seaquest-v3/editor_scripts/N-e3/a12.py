import numpy as np
np.set_printoptions(precision=3, suppress=True, linewidth=200)
def net(src):
    return [src(n) for n in ["W1","b1","W2","b2","W3","b3"]]
def fwd(x,P):
    W1,b1,W2,b2,W3,b3=P
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); l=h2@W3+b3
    return h1,h2,l
def obs(sub=(5,5,'L'), enemies=(), divers=(), bullets=(), ebul=(), oxy=10, ndiv=0):
    g=np.zeros((10,10,6))
    r,c,f=sub
    g[r,c,0]=1
    bc = c+1 if f=='L' else c-1
    g[r,bc,0]=1; g[r,bc,4]=1
    for (er,ec,d) in enemies:   # d: moving direction 'L' or 'R'
        g[er,ec,1]=1; g[er,ec,2]=1
        t=ec+1 if d=='L' else ec-1
        if 0<=t<10: g[er,t,4]=1
    for (er,ec,d) in divers:
        g[er,ec,2]=1
        t=ec+1 if d=='L' else ec-1
        if 0<=t<10: g[er,t,4]=1
    for (er,ec) in bullets: g[er,ec,3]=1
    for (er,ec) in ebul: g[er,ec,1]=1
    g[9,0:oxy,5]=1
    if ndiv: g[9,9-ndiv:9,5]=1
    return g.reshape(-1)
A=['noop','left','up','right','down','fire']
def probs(l):
    e=np.exp(l-l.max()); return e/e.sum()
def show(tag,x,P):
    h1,h2,l=fwd(x,P); p=probs(l)
    print(f"{tag:40s}", " ".join(f"{A[i]}:{p[i]:.3f}" for i in range(6)), "| logits", np.round(l,1))
P=net(gold)
L=dict(oxy=2,ndiv=2)
for r in [1,2,3,5]:
  for t,en in [("none",[]),("enemy above c5",[(r-1,5,'L')] if r>1 else []),("enemy above c6",[(r-1,6,'L')] if r>1 else []),("enemy above c4",[(r-1,4,'R')] if r>1 else []),("enemy above c7",[(r-1,7,'L')] if r>1 else []),("own c6",[(r,6,'L')]),("own c4 R",[(r,4,'R')]),("own c6 + above c5",[(r,6,'L')]+([(r-1,5,'L')] if r>1 else []))]:
    x=obs(sub=(r,5,'L'),enemies=en,**L)
    h1,h2,l=fwd(x,P)
    show(f"LOWOX r{r} {t}",x,P)
