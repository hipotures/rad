G=gold
def P(tag,x):
    a=fwd(x,G)[3]
    print(f"{tag:44s} gold n l u r d f="+" ".join(f"{v:.2f}" for v in a))
for y in (2,4,6):
  for kind in ('fish','eb'):
    for dy in (-1,0,1):
      for ex in (0,1,2,3,4,8,9):
        lr = ex<5
        P(f"LOX y={y} {kind} dy={dy:+d} x={ex} {'->' if lr else '<-'}",obs(sub=(5,y),ox=50,dc=2,**{kind:[(ex,y+dy,lr)]}))
# two-object combos
y=4
for a_ in ((3,y-1,True),(7,y-1,False)):
  for b_ in ((3,y,True),(7,y,False),(3,y+1,True),(7,y+1,False)):
    P(f"LOX y=4 fish {a_} + {b_}",obs(sub=(5,y),ox=50,dc=2,fish=[a_,b_]))
    P(f"NRM y=4 fish {a_} + {b_}",obs(sub=(5,y),fish=[a_,b_]))
