g=net(gold)
mx=[]
for y in range(1,9):
    for oxy,div in [(150,0),(150,3),(50,2)]:
        p,l,_,_=g(st(y,oxy=oxy,div=div)); mx.append((y,oxy,div,round(float(l.max()),1),int(l.argmax())))
print(mx)
for tag,s in [('own x6',st(5,ent=[(5,6,'fish',False)])),('fish x8',st(5,ent=[(5,8,'fish',False)])),('fish x2',st(5,ent=[(5,2,'fish',True)])),('below',st(5,ent=[(6,5,'fish',False)]))]:
    p,l,_,_=g(s); print(tag,l.round(1))
print('orient check: sub x6 right-facing row5 empty',g(st(5,sx=6,orr=True))[0], 'x7 right',g(st(5,sx=7,orr=True))[0])
