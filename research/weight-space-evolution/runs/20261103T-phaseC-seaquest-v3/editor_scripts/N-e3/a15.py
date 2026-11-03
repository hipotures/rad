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
P=net(gold)
W1=gold("W1").copy().reshape(10,10,6,32)
for u in range(9,16):
    W1[9,8,5,u]+=-6.0; W1[9,2,5,u]+=3.0
P2=[W1.reshape(600,32)]+P[1:]
LO=dict(oxy=2,ndiv=2)
cases=[("r2 lo enemy r1c5 diver r4",2,dict(enemies=[(1,5,'L')],divers=[(4,1,'R')],**LO)),
("r3 lo enemy r2c5 diver r6",3,dict(enemies=[(2,5,'L')],divers=[(6,1,'R')],**LO)),
("r3 lo enemy r2c5 own c6",3,dict(enemies=[(2,5,'L'),(3,6,'L')],**LO)),
("r5 lo dc0 diver r7",5,dict(divers=[(7,2,'R')],oxy=2,ndiv=0)),
("r5 hi dc2 diver r7",5,dict(divers=[(7,2,'R')],oxy=8,ndiv=2)),
("r5 hi dc0 diver r7",5,dict(divers=[(7,2,'R')],oxy=8,ndiv=0)),
("r5 full dc0 diver r3",5,dict(divers=[(3,2,'R')],oxy=10,ndiv=0)),
("r5 mid dc0 empty",5,dict(oxy=6,ndiv=0)),("r5 mid dc3 empty",5,dict(oxy=6,ndiv=3)),("r5 lo dc0 empty",5,dict(oxy=2,ndiv=0)),
("r5 mid dc0 left enemy r6",5,dict(enemies=[(6,1,'R')],oxy=6,ndiv=0))]
for t,r,kw in cases:
    for tag,PP in [("G",P),("C",P2)]: show(tag+" "+t,obs(sub=(r,5,'L'),**kw),PP)
save("W1",P2[0]); print(saved())
