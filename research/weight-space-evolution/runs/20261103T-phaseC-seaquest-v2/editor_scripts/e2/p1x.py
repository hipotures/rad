import numpy as np
def net(x,P):
    W1,b1,W2,b2,W3,b3=P
    h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); return h2@W3+b3
def st(sub=(5,4),orl=True,ox=150,dc=2,fish=(),esub=(),ebul=(),div=()):
    s=np.zeros((10,10,6))
    x,y=sub; s[y,x,0]=1; bx=x+1 if orl else x-1; s[y,bx,0]=1; s[y,bx,4]=1
    s[9,0:ox*10//200,5]=1; s[9,max(0,9-dc):9,5]=1
    for (ex,ey,lr) in list(fish)+list(esub):
        s[ey,ex,1]=1; s[ey,ex,2]=1; b=ex-1 if lr else ex+1
        if 0<=b<=9: s[ey,b,4]=1
    for (ex,ey,lr) in ebul: s[ey,ex,1]=1
    for (ex,ey,lr) in div:
        s[ey,ex,2]=1; b=ex-1 if lr else ex+1
        if 0<=b<=9: s[ey,b,4]=1
    return s.reshape(-1)
A='n l u r d f'.split()
def act(x,P):
    l=net(x,P); p=np.exp(l-l.max()); p/=p.sum(); return A[int(l.argmax())], np.round(p,2)
P=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
print('empty, row r:', [(r,act(st(sub=(5,r)),P)[0]) for r in range(0,9)])
print('empty, row r, ox50 dc2:', [(r,act(st(sub=(5,r),ox=50),P)[0]) for r in range(0,9)])
print('empty, row r, ox50 dc0:', [(r,act(st(sub=(5,r),ox=50,dc=0),P)[0]) for r in range(0,9)])
for kind in ['fish','esub','ebul']:
  for lr,cols in [(False,range(6,10)),(True,range(0,5))]:
    out=[]
    for c in cols:
        kw={kind:[(c,4,lr)]}
        out.append((c,act(st(sub=(5,4),**kw),P)[0]))
    print(kind,'same row4, moving', 'right' if lr else 'left', out)
# threat in row above / below
for kind in ['fish','ebul']:
  for dy in [-1,1,-2,2]:
    out=[]
    for c in range(0,10):
        kw={kind:[(c,4+dy,c<5)]}
        out.append((c,act(st(sub=(5,4)),P)[0]+'/'+act(st(sub=(5,4),**kw),P)[0]))
    print(kind,'row',4+dy,out)
# ascent with low oxygen, threat in row above
for c in range(10):
    print('ascent ox50 row4, fish at row3 col',c, act(st(sub=(5,4),ox=50,fish=[(c,3,c<5)]),P))
for r in range(1,9):
    print('diver row',r,'sub row4',act(st(sub=(5,4),div=[(2,r,True)]),P)[0], ' enemy left row',r, act(st(sub=(5,4),fish=[(1,r,True)]),P)[0])
