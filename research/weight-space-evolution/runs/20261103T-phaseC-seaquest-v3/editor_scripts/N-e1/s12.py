import numpy as np
np.set_printoptions(precision=3, suppress=True, linewidth=200)
def P(name): return load(name)
def fwd(x, edited=False):
    g = load if edited else gold
    h1=np.tanh(x@g('W1')+g('b1')); h2=np.tanh(h1@g('W2')+g('b2')); l=h2@g('W3')+g('b3')
    p=np.exp(l-l.max()); p/=p.sum(); return h1,h2,l,p
def obs(pr, px=5, back=6, divers=(), enemies=(), bullets=(), oxy=10, ndiv=0, shots=()):
    s=np.zeros((10,10,6))
    s[pr,px,0]=1; s[pr,back,0]=1; s[pr,back,4]=1
    for (r,c) in divers: s[r,c,2]=1
    for (r,c) in enemies: s[r,c,1]=1; s[r,c,2]=1
    for (r,c) in bullets: s[r,c,1]=1
    for (r,c) in shots: s[r,c,3]=1
    s[9,:oxy,5]=1; s[9,9-ndiv:9,5]=1
    return s.reshape(-1)
A='noop left up right down fire'.split()
def show(tag,x,edited=False):
    h1,h2,l,p=fwd(x,edited)
    print('%-40s'%tag, ' '.join('%s:%.2f'%(A[i],p[i]) for i in range(6) if p[i]>0.01), '| logits', np.round(l[[2,4,5]],1))
W1,b1,W2,b2,W3,b3=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
def pre(x):
    h1=np.tanh(x@W1+b1); return h1, h1@W2+b2
for tag,x in [('empty r5',obs(5)),('r5 enL r6',obs(5,enemies=[(6,1)])),('r5 enL r7',obs(5,enemies=[(7,1)])),('r5 enL r8',obs(5,enemies=[(8,1)])),('r5 enL r3',obs(5,enemies=[(3,1)])),('r5 enL r2',obs(5,enemies=[(2,1)])),('r5 div r8',obs(5,divers=[(8,1)])),('r5 div r2',obs(5,divers=[(2,1)]))]:
    h1,z=pre(x)
    print('%-12s'%tag,'fire5=%.2f up5=%.2f down5=%.2f'%(z[4],z[12],z[21]), 'h2(up5,down5)=%.2f %.2f'%(np.tanh(z[12]),np.tanh(z[21])))
print('W2 rows 25..31 to h2 12 (up from r5) and 21 (down from r5):'); print(W2[25:32,[4,12,21]].T)
print('b2',b2[[4,12,21]])
