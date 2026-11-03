reset()
ps=P()
W1,b1,W2,b2,W3,b3=ps
for ox,dv in [(2,2),(10,2)]:
  for it in [[(4,5,'E')],[(4,5,'E'),(6,5,'E')],[(4,5,'E'),(5,7,'E')],[(4,5,'E'),(5,6,'E')],[(4,6,'E'),(5,7,'E'),(6,5,'E')],[(4,5,'E'),(6,6,'E')],[(4,8,'E')],[(4,3,'E')],[(5,6,'E')],[(5,4,'E')],[(4,5,'B')],[(3,5,'E')]]:
    x=obs(5,oxy=ox,div=dv,items=it)
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2)
    print(f"pr5 ox{ox} {it}", fmt(pol(x,ps)), "| h2 act>0:", [(i,round(float(h2[i]),2)) for i in range(25) if h2[i]>-0.9])
