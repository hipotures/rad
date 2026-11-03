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
