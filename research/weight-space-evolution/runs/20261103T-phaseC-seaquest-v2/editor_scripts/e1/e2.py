reset()
W1=gold('W1').copy()
def ix(r,c,ch): return (r*10+c)*6+ch
W1[ix(9,2,5),24]=0.0; W1[ix(9,1,5),24]=-6.0
for k in range(7):
    r=k+2
    for c in range(4):
        assert W1[ix(r,c,1),9+k]==-8.0
        W1[ix(r,c,1),9+k]=0.0
save('W1',W1)
g=net(gold); f=net(load)
for sy,ey,ex,lr in [(3,6,1,True),(3,6,0,True),(6,3,2,True),(5,5,1,True),(5,8,2,True),(3,6,7,False),(8,2,1,True)]:
    s=st(sy,ent=[(ey,ex,'fish',lr)])
    print('sub',sy,'fish',ey,ex,'gold',g(s)[0],'cand',f(s)[0])
s=st(5,ent=[(7,2,'bullet',True)]); print('bullet below-left gold',g(s)[0],'cand',f(s)[0])
s=st(5,ent=[(7,1,'fish',True),(6,5,'fish',False)]); print('fish target with danger between gold',g(s)[0],'cand',f(s)[0])
s=st(5,div=0,ent=[(7,1,'fish',True),(3,8,'diver',False)]); print('fish vs diver',g(s)[0],'cand',f(s)[0])
