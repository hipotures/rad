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
W1,b1,W2,b2,W3,b3=P
for r in [2,5,8]:
    x=obs(sub=(r,5,'L'))
    h1=np.tanh(x@W1+b1); pre=h1@W2+b2
    print("row",r,"h2 pre",np.round(pre[:26],2))
# candidate 1
W1n=W1.copy().reshape(10,10,6,32); W2n=W2.copy()
for r in range(1,9):
    u=16+r-1
    W1n[r,7,1,u]=7.0; W1n[r,7,2,u]=-1.0
    W1n[r,8,1,u]=7.0; W1n[r,8,2,u]=-1.0
for r in range(2,9):  # up unit for player row r is h2[8+r-2]
    W2n[16+r-1, 8+r-2]+=1.5
for r in range(1,8):  # down unit for player row r is h2[16+r]
    W2n[16+r-1, 16+r]+=1.5
P2=[W1n.reshape(600,32),b1,W2n,b2,W3,b3]
tests=[("empty",dict()),
 ("enemy same row c7 L",dict(enemies=[(5,7,'L')])),
 ("enemy same row c6 L",dict(enemies=[(5,6,'L')])),
 ("enemy same row c8 L",dict(enemies=[(5,8,'L')])),
 ("enemy same row c3 R",dict(enemies=[(5,3,'R')])),
 ("enemy same row c4 R",dict(enemies=[(5,4,'R')])),
 ("ebullet same row c3",dict(ebul=[(5,3)])),
 ("enemy c6 same + enemy row4 c5",dict(enemies=[(5,6,'L'),(4,5,'L')])),
 ("enemy c6 same + enemy row6 c5",dict(enemies=[(5,6,'L'),(6,5,'L')])),
 ("enemy c6 same + enemy r4,r6",dict(enemies=[(5,6,'L'),(6,5,'L'),(4,4,'R')])),
 ("enemy row4 c8",dict(enemies=[(4,8,'L')])),
]
for t,kw in tests:
    for tag,PP in [("G",P),("C",P2)]:
        show(tag+" r5 "+t,obs(sub=(5,5,'L'),**kw),PP)
for t,kw in [("enemy r1 c6",dict(enemies=[(1,6,'L')])),]:
    for tag,PP in [("G",P),("C",P2)]:
        show(tag+" r1 "+t,obs(sub=(1,5,'L'),**kw),PP)
for t,kw in [("enemy r8 c6",dict(enemies=[(8,6,'L')])),]:
    for tag,PP in [("G",P),("C",P2)]:
        show(tag+" r8 "+t,obs(sub=(8,5,'L'),**kw),PP)
save("W1",P2[0]); save("W2",W2n)
print(saved())
