import numpy as np
np.set_printoptions(precision=3, suppress=True, linewidth=220)
def net(get):
    W1,b1,W2,b2,W3,b3=[get(n) for n in ['W1','b1','W2','b2','W3','b3']]
    def f(x):
        h1=np.tanh(x@W1+b1); h2=np.tanh(h1@W2+b2); l=h2@W3+b3; p=np.exp(l-l.max()); return p/p.sum(), l, h1, h2
    return f
def st(sy,sx=5,orr=False,oxy=150,div=0,ent=()):
    s=np.zeros((10,10,6))
    s[sy,sx,0]=1; bx=sx-1 if orr else sx+1
    if 0<=bx<=9: s[sy,bx,0]=1; s[sy,bx,4]=1
    s[9,0:oxy*10//200,5]=1; s[9,9-div:9,5]=1
    for (y,x,kind,lr) in ent:
        if kind in('fish','sub'): s[y,x,1]=1; s[y,x,2]=1
        if kind=='bullet': s[y,x,1]=1
        if kind=='diver': s[y,x,2]=1
        if kind!='bullet':
            bx=x-1 if lr else x+1
            if 0<=bx<=9: s[y,bx,4]=1
    return s.reshape(-1)
f=net(gold)
A='n l u r d f'.split()
names=['fire%d'%i for i in range(8)]+['up%d'%i for i in range(8)]+['dn%d'%i for i in range(8)]+['u24','d25']+['x']*6
def show(tag,x):
    p,l,h1,h2=f(x); act=[(names[i],round(float(h2[i]),2)) for i in range(26) if h2[i]>-0.9]
    print(tag,'p',p,'l',l-l.max(),act)
for y in [3,5,8]:
    show('ascend y%d clear'%y, st(y,oxy=50,div=2))
    for ex in [3,4,5,6,7]:
        show('ascend y%d fish above x%d'%(y,ex), st(y,oxy=50,div=2,ent=[(y-1,ex,'fish',ex<5)]))
    for ex in [4,6,7]:
        show('ascend y%d fish own x%d'%(y,ex), st(y,oxy=50,div=2,ent=[(y,ex,'fish',ex<5)]))
    show('ascend y%d bullet above x5'%y, st(y,oxy=50,div=2,ent=[(y-1,5,'bullet',True)]))
show('normal y5 bullet own x6', st(5,ent=[(5,6,'bullet',False)]))
show('normal y5 bullet own x4', st(5,ent=[(5,4,'bullet',True)]))
