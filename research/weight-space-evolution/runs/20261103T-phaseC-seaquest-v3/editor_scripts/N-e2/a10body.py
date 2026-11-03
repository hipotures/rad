reset()
ps=P()
for ox,dv in [(10,0),(2,0),(10,1)]:
  for it in [[],[(1,7,'E')],[(1,8,'E')],[(1,3,'E')],[(1,4,'E')],[(1,7,'B')],[(2,5,'E')],[(2,6,'E')],[(2,4,'E')],[(2,2,'E')],[(1,8,'D')],[(1,2,'D')],[(2,6,'E'),(1,8,'E')]]:
    print(f"pr1 ox{ox} dv{dv} {it}", fmt(pol(obs(1,oxy=ox,div=dv,items=it),ps)))
for it in [[(1,2,'E')],[(3,2,'E')],[(2,2,'E')]]:
    print(f"pr2 {it}", fmt(pol(obs(2,items=it),ps)))
