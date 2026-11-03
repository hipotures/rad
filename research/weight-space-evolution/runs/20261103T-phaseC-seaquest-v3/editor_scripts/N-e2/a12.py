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
ps=P()
W1,b1,W2,b2,W3,b3=ps
for ox,dv in [(2,2),(10,2)]:
  for it in [[(4,5,'E')],[(4,5,'E'),(6,5,'E')],[(4,5,'E'),(5,7,'E')],[(4,5,'E'),(5,6,'E')],[(4,6,'E'),(5,7,'E'),(6,5,'E')],[(4,5,'E'),(6,6,'E')],[(4,8,'E')],[(4,3,'E')],[(5,6,'E')],[(5,4,'E')],[(4,5,'B')],[(3,5,'E')]]:
    x=obs(5,oxy=ox,div=dv,items=it)
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2)
    print(f"pr5 ox{ox} {it}", fmt(pol(x,ps)), "| h2 act>0:", [(i,round(float(h2[i]),2)) for i in range(25) if h2[i]>-0.9])
