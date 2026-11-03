import numpy as np
def obs(sub=(5,0),orr=False,ox=200,dc=0,fish=(),subs=(),eb=(),divers=(),fb=()):
    s=np.zeros((10,10,6))
    x,y=sub
    s[y,x,0]=1; bx=x-1 if orr else x+1
    if 0<=bx<=9: s[y,bx,0]=1; s[y,bx,4]=1
    s[9,0:max(0,ox)*10//200,5]=1
    s[9,9-dc:9,5]=1
    for (bx_,by,*_) in fb: s[by,bx_,3]=1
    for (ex,ey,*_) in eb: s[ey,ex,1]=1
    for lst,ch in ((fish,(1,2)),(subs,(1,2)),(divers,(2,))):
        for (ex,ey,lr) in lst:
            for c in ch: s[ey,ex,c]=1
            t=ex-1 if lr else ex+1
            if 0<=t<=9: s[ey,t,4]=1
    return s.reshape(-1)
def fwd(x,L=None):
    L=L or load
    h1=np.tanh(x@L('W1')+L('b1')); h2=np.tanh(h1@L('W2')+L('b2'))
    lg=h2@L('W3')+L('b3'); p=np.exp(lg-lg.max()); p/=p.sum()
    return h1,h2,lg,p
def pr(tag,x,L=None):
    h1,h2,lg,p=fwd(x,L)
    print(f"{tag:40s} lg="+" ".join(f"{v:7.1f}" for v in lg)+" p="+" ".join(f"{v:.2f}" for v in p))
def idx(r,c,ch): return (r*10+c)*6+ch
reset()
W1=gold('W1').copy(); b1=gold('b1').copy()
for r in range(2,9):
    u=23+r   # H1[25..31] <-> rows 2..8
    assert all(W1[idx(r,c,1),u]==6 for c in range(4))
    for c in range(4):
        W1[idx(r,c,1),u]=3.0
        W1[idx(r,c,2),u]=4.0
    b1[u]=-4.0
save('W1',W1); save('b1',b1)
G=gold
def P(tag,x):
    a=fwd(x,G)[3];b=fwd(x,load)[3]
    if np.abs(a-b).max()>0.05: print(f"{tag:44s} gold="+" ".join(f"{v:.2f}" for v in a)+" | new="+" ".join(f"{v:.2f}" for v in b))
from collections import Counter
cnt=Counter()
for mode,kw0 in (('NRM',{}),('LOX',dict(ox=50,dc=2))):
  for y in range(1,9):
    for kind in ('fish','eb','divers'):
      for dy in (-2,-1,0,1,2):
        if not 1<=y+dy<=8: continue
        for ex in range(10):
          for lr in (True,False):
            x=obs(sub=(5,y),**kw0,**{kind:[(ex,y+dy,lr)]})
            a=fwd(x,G)[3];b=fwd(x,load)[3]
            if np.abs(a-b).max()>0.05:
                cnt[(mode,kind)]+=1
                if kind!='eb' and cnt[(mode,kind)]<15: P(f"{mode} y={y} {kind} dy={dy:+d} x={ex} {'->' if lr else '<-'}",x)
                if kind=='eb' and cnt[(mode,kind)]<6: P(f"{mode} y={y} {kind} dy={dy:+d} x={ex} {'->' if lr else '<-'}",x)
print(cnt, saved())
