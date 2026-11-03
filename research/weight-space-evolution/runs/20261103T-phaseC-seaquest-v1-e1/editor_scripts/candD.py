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
