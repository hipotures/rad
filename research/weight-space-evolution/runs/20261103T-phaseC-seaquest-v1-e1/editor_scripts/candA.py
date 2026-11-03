def idx(r,c,ch): return (r*10+c)*6+ch
W1=gold('W1').copy()
for r in range(1,9):
    u=15+r
    W1[idx(r,7,1),u]=6.0
    W1[idx(r,8,4),u]=3.0
save('W1',W1)
G=gold
def P(tag,x):
    a=fwd(x,G)[3];b=fwd(x,load)[3]
    print(f"{tag:42s} gold="+" ".join(f"{v:.2f}" for v in a)+" | new="+" ".join(f"{v:.2f}" for v in b))
for y in (3,5,8):
  for ex,lr in ((7,False),(7,True),(8,False),(9,True),(6,False)):
    for dy in (-1,0,1):
      if not 1<=y+dy<=8: continue
      P(f"y={y} fish dy={dy:+d} x={ex} {'->' if lr else '<-'}",obs(sub=(5,y),fish=[(ex,y+dy,lr)]))
  P(f"y={y} diver same row x=7 <-",obs(sub=(5,y),divers=[(7,y,False)]))
  P(f"y={y} diver same row x=9 ->",obs(sub=(5,y),divers=[(9,y,True)]))
print('lowox combos')
for y in (2,4):
  P(f"LOX y={y} fish same x=6<-",obs(sub=(5,y),ox=50,dc=2,fish=[(6,y,False)]))
  P(f"LOX y={y} fish same x=7<-",obs(sub=(5,y),ox=50,dc=2,fish=[(7,y,False)]))
  P(f"LOX y={y} fish above x=7<-",obs(sub=(5,y),ox=50,dc=2,fish=[(7,y-1,False)]))
  P(f"LOX y={y} same x6 + above x5",obs(sub=(5,y),ox=50,dc=2,fish=[(6,y,False),(5,y-1,False)]))
  P(f"LOX y={y} above x5",obs(sub=(5,y),ox=50,dc=2,fish=[(5,y-1,False)]))
