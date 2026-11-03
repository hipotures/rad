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
for r in range(0,9):
    show(f"sub row{r} empty oxy10 nd0",obs(sub=(r,4,'L')),P)
for r in range(0,9):
    show(f"sub row{r} oxy2 nd1",obs(sub=(r,4,'L'),oxy=2,ndiv=1),P)
for r in range(0,9):
    show(f"sub row{r} oxy5 nd1",obs(sub=(r,4,'L'),oxy=5,ndiv=1),P)
show("sub r5, enemy r5 c8 moving L",obs(sub=(5,4,'L'),enemies=[(5,8,'L')]),P)
show("sub r5, enemy r5 c1 moving R",obs(sub=(5,4,'L'),enemies=[(5,1,'R')]),P)
show("sub r5, enemy r4 c5",obs(sub=(5,4,'L'),enemies=[(4,5,'L')]),P)
show("sub r5, enemy r6 c5",obs(sub=(5,4,'L'),enemies=[(6,5,'L')]),P)
show("sub r5, enemy r6 c1",obs(sub=(5,4,'L'),enemies=[(6,1,'R')]),P)
show("sub r5, diver r3",obs(sub=(5,4,'L'),divers=[(3,2,'R')]),P)
show("sub r5, diver r7",obs(sub=(5,4,'L'),divers=[(7,2,'R')]),P)
show("sub r5, diver r5",obs(sub=(5,4,'L'),divers=[(5,2,'R')]),P)
