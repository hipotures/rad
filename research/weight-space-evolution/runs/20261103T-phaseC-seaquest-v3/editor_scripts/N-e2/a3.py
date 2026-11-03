import numpy as np
np.set_printoptions(precision=2, suppress=True, linewidth=250)
W1,b1,W2,b2,W3,b3=[gold(n) for n in ["W1","b1","W2","b2","W3","b3"]]
G=W1.reshape(10,10,6,32)
for j in [17,20,23,26,29,31]:
    for c in range(6):
        g=G[:,:,c,j]
        if np.abs(g).max()>1e-3:
            rr=np.nonzero(np.abs(g).max(1)>1e-3)[0]
            print("unit",j,"ch",c,"rows",rr, g[rr])
def obs(pr, pc=(4,5), oxy=10, div=0, items=()):
    x=np.zeros((10,10,6))
    for c in pc: x[pr,c,0]=1
    x[pr,pc[0],4]=1
    x[9,0:oxy,5]=1
    if div: x[9,9-div:9,5]=1
    for (r,c,ch) in items: x[r,c,ch]=1
    return x.reshape(-1)
def pol(x):
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); l=h2@W3+b3
    p=np.exp(l-l.max()); p/=p.sum(); return p
A="noop left up right down fire".split()
def show(tag,x):
    p=pol(x); print(f"{tag:40s}", " ".join(f"{a}:{v:.2f}" for a,v in zip(A,p) if v>0.01))
for r in range(9):
    for oxy,div in [(10,0),(10,1),(2,1),(2,0),(5,3),(10,6)]:
        show(f"row{r} oxy{oxy} div{div}", obs(r,oxy=oxy,div=div))
