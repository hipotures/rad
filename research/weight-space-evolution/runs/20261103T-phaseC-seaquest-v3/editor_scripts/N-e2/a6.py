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
for r in [2,5,8]:
    for dr in [-1,0,1]:
        for c in [0,2,3,4,7,8,9]:
            for k in ['E','B']:
                if 0<r+dr<9:
                    print(f"pr{r} {k} at ({r+dr},{c})", fmt(pol(obs(r,items=[(r+dr,c,k)]),ps)))
print("sandwich", fmt(pol(obs(5,items=[(5,8,'E'),(4,7,'E'),(6,7,'E')]),ps)))
print("diver row5 col8", fmt(pol(obs(5,items=[(5,8,'D')]),ps)))
print("diver row3", fmt(pol(obs(5,items=[(3,8,'D')]),ps)))
print("diver row7", fmt(pol(obs(5,items=[(7,1,'D')]),ps)))
