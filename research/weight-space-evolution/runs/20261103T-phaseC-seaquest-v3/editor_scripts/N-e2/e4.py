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
reset()
W1=gold("W1").copy()
for c in range(2,9): W1[(1*10+c)*6+2,16]=0.0   # row-1 danger unit: no reward cancellation -> any enemy in row 1 cols 2-8 counts
save("W1",W1); print(saved())
ps=P()
for c in [2,3,4,7,8]: print("row0 E(1,%d)"%c, fmt(pol(obs(0,div=2,items=[(1,c,'E')]),ps)))
print("row0 D(1,3)", fmt(pol(obs(0,div=2,items=[(1,3,'D')]),ps)))
print("row0 empty", fmt(pol(obs(0,div=2),ps)))
print("asc pr2 E(1,3)", fmt(pol(obs(2,oxy=2,div=2,items=[(1,3,'E')]),ps)))
