def idx(r,c,ch): return (r*10+c)*6+ch
reset()
W1=gold('W1').copy()
for r in range(1,9):
    u=15+r
    W1[idx(r,7,2),u]=0.0      # was -3: enemies at col 7 now detected strongly (2 -> tanh .96)
    W1[idx(r,8,1),u]=4.0      # was 2
    W1[idx(r,8,2),u]=-3.8     # was -1.8: enemies at col 8 unchanged (net 0.2), bullets at col 8: 4-3=1
save('W1',W1)
G=gold
def P(tag,x):
    a=fwd(x,G)[3];b=fwd(x,load)[3]
    if np.abs(a-b).max()>0.02: print(f"{tag:44s} gold="+" ".join(f"{v:.2f}" for v in a)+" | new="+" ".join(f"{v:.2f}" for v in b))
n=0
for mode,kw0 in (('NRM',{}),('LOX',dict(ox=50,dc=2))):
  for y in range(1,9):
    for kind in ('fish','eb','divers'):
      for dy in (-1,0,1):
        if not 1<=y+dy<=8: continue
        for ex in range(10):
          for lr in (True,False):
            n+=1
            P(f"{mode} y={y} {kind} dy={dy:+d} x={ex} {'->' if lr else '<-'}",obs(sub=(5,y),**kw0,**{kind:[(ex,y+dy,lr)]}))
print('n probes',n,saved())
