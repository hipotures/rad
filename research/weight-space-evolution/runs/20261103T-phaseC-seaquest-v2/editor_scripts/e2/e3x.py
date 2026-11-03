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
import numpy as np
reset()
W1=gold('W1').copy()
i2=(9*10+2)*6+5; i1=(9*10+0)*6+5
print(W1[i2,24],W1[i1,24])
W1[i1,24]=W1[i2,24]; W1[i2,24]=0.0
save('W1',W1)
P=[load(n) for n in ['W1','b1','W2','b2','W3','b3']]
for ox in [40,21,20,19,10]:
    print(ox,[act(st(sub=(5,r),ox=ox),P)[0] for r in range(9)])
