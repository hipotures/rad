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
reset()
P=net(gold); W1=gold("W1").copy().reshape(10,10,6,32); b1=gold("b1").copy()
for u in range(25,32):
    r=u-23
    for c in range(4): W1[r,c,2,u]=6.0
    b1[u]=-9.0
P2=[W1.reshape(600,32),b1]+P[2:]
for t,kw in [("empty",{}),("enemy r6 c1 R",dict(enemies=[(6,1,'R')])),("ebul r6 c1",dict(ebul=[(6,1)])),("ebul r4 c2",dict(ebul=[(4,2)])),("enemy r4 c2",dict(enemies=[(4,2,'R')])),
  ("diver r6 c1",dict(divers=[(6,1,'R')])),("enemy r5 c2",dict(enemies=[(5,2,'R')])),("ebul r5 c2",dict(ebul=[(5,2)])),("enemy r7 c1",dict(enemies=[(7,1,'R')])),("2 enemies r6 c0,c3",dict(enemies=[(6,0,'R'),(6,3,'R')]))]:
    for tag,PP in [("G",P),("C",P2)]: show(tag+" r5 "+t,obs(sub=(5,5,'L'),**kw),PP)
save("W1",P2[0]); save("b1",b1); print(saved())
