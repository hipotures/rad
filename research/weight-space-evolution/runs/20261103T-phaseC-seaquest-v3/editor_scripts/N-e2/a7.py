import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=250)
def P(): return [load(n) for n in ["W1","b1","W2","b2","W3","b3"]]
def obs(pr, oxy=10, div=0, items=()):
    x=np.zeros((10,10,6))
    x[pr,5,0]=1; x[pr,6,0]=1; x[pr,6,4]=1
    x[9,0:oxy,5]=1
    if div: x[9,9-div:9,5]=1
    for (r,c,kind) in items:
        if kind=='E': x[r,c,1]=1; x[r,c,2]=1
        elif kind=='ER': x[r,c,1]=1; x[r,c,2]=1; x[r,c+1,4]=1  # enemy moving right (trail left? set trail on right=moving left)
        elif kind=='B': x[r,c,1]=1
        elif kind=='D': x[r,c,2]=1
    return x.reshape(-1)
def pol(x,ps):
    W1,b1,W2,b2,W3,b3=ps
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); l=h2@W3+b3
    p=np.exp(l-l.max()); p/=p.sum(); return p
A="noop left up right down fire".split()
def fmt(p): return " ".join(f"{a}:{v:.2f}" for a,v in zip(A,p) if v>0.01)
ps=P()
for r in [1,3,5,8]:
    for (dr,c,k) in [(-1,4,'E'),(-1,6,'E'),(-1,7,'E'),(-1,8,'E'),(-1,2,'E'),(-1,6,'B'),(0,7,'E'),(0,8,'E'),(0,3,'E'),(1,6,'E')]:
        if 0<=r+dr<9:
            print(f"ASCENT pr{r} {k} at ({r+dr},{c})", fmt(pol(obs(r,oxy=2,div=2,items=[(r+dr,c,k)]),ps)))
for c in [3,4,6,7,8]:
    print(f"row0 E at (1,{c})", fmt(pol(obs(0,items=[(1,c,'E')]),ps)))
