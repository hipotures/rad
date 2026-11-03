reset()
W2=gold('W2').copy(); b2=gold('b2').copy()
print('gold W2[18,9]',W2[18,9])
W2[24,9]=4.75; W2[18,9]=4.0
save('W2',W2); save('b2',b2)
g=net(gold); f=net(load)
for tag,s in [('row3 empty',st(3)),('row3 empty div2',st(3,div=2)),('row3 fish own x6',st(3,ent=[(3,6,'fish',False)])),('row3 fish own+below',st(3,ent=[(3,6,'fish',False),(4,5,'fish',True)])),
              ('row3 diver row2',st(3,ent=[(2,8,'diver',False)])),('row3 ascent',st(3,oxy=50,div=2)),('row3 ascent fish own',st(3,oxy=50,div=2,ent=[(3,6,'fish',False)])),
              ('row3 fish below',st(3,ent=[(4,5,'fish',True)])),('row3 own+above',st(3,ent=[(3,6,'fish',False),(2,5,'fish',True)])),('row3 ascent danger above',st(3,oxy=50,div=2,ent=[(2,5,'fish',False)]))]:
    print(tag,'gold',g(s)[0],'cand',f(s)[0])
