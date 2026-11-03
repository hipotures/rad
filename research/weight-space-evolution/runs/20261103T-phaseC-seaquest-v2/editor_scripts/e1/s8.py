f=net(gold)
for y in [1,2,3]:
  for (dy,ex,k) in [(0,4,'fish'),(0,6,'fish'),(0,7,'fish'),(1,5,'fish'),(1,4,'bullet'),(-1,5,'fish'),(0,6,'bullet')]:
    if y+dy<1: continue
    ents=[(y+dy,ex,k,ex<5)]
    print('y',y,'ent',ents[0],'div0',f(st(y,div=0,ent=ents))[0], 'div2',f(st(y,div=2,ent=ents))[0])
  # two dangers: own row and below
  ents=[(y,6,'fish',False),(y+1,5,'fish',True)]
  print('y',y,'own+below',f(st(y,div=0,ent=ents))[0])
  ents=[(y,6,'fish',False),(y-1,5,'fish',True)] if y>1 else [(y,6,'fish',False)]
  print('y',y,'own+above',f(st(y,div=0,ent=ents))[0])
