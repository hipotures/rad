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
for y in (1,2,3,5):
  for kind in ('fish','eb'):
    for dy in (-1,0):
      if y+dy<1: continue
      for ex in (3,4,5,6,7,8):
        kw={kind:[(ex,y+dy,False)]}
        h1,h2,lg,p=fwd(obs(sub=(5,y),ox=50,dc=2,**kw))
        print(f"LOWOX y={y} {kind} dy={dy:+d} x={ex} <- p(n,l,u,r,d,f)="+" ".join(f"{v:.2f}" for v in p))
# H2 preacts at y=3 lowox
h1,h2,lg,p=fwd(obs(sub=(5,3),ox=50,dc=2))
print('h1',np.round(h1,2));print('h2',np.round(h2,2))
h1,h2,lg,p=fwd(obs(sub=(5,3),ox=50,dc=2,fish=[(5,2,False)]))
print('h1',np.round(h1,2));print('h2',np.round(h2,2))
