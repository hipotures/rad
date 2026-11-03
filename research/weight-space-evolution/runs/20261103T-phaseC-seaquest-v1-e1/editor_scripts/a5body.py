y=5
for kind in ('fish','subs','eb'):
  for dy in (-1,0,1):
    for ex in range(10):
      for lr in (True,False):
        if kind=='eb' and lr!=(ex<5): continue
        kw={kind:[(ex,y+dy,lr)]}
        h1,h2,lg,p=fwd(obs(sub=(5,y),**kw))
        print(f"{kind} dy={dy:+d} x={ex} {'->' if lr else '<-'} p(n,l,u,r,d,f)="+" ".join(f"{v:.2f}" for v in p))
