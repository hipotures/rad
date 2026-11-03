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
import json
n=asc=0
for f in ['/work/pass_1/gold_episodes.json','/work/pass_2/gold_episodes.json','/work/pass_2/candidate_episodes.json']:
    for e in json.load(open(f)):
        if 'trace' not in e: continue
        prev=None
        for t in e['trace']:
            n+=1
            if t['oxygen']<60 and t['diver_count']>0 and not t['surface']: asc+=1
print("steps",n,"ascent-mode steps",asc, asc/n)
reset()
W1=gold("W1").copy()
i2=(9*10+2)*6+5; i1=(9*10+1)*6+5
W1[i1,24]=W1[i2,24]; W1[i2,24]=0.0
save("W1",W1)
ps=P()
for ox in [1,2,3,10]:
    for dv in [0,1,3,6]:
        print("ox",ox,"dv",dv, fmt(pol(obs(5,oxy=ox,div=dv),ps)))
