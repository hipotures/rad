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
# F is currently saved in /work/edit; add G variants on top
W2F=load('W2').copy()
print('W2[24,9] gold', gold('W2')[24,9], 'h2 9 inputs from h1 3 (player row3):', gold('W2')[3,9])
cases=[('r3 empty',obs(3)),('r3 diver r2',obs(3,divers=[(2,2)])),('r3 enemyL r2',obs(3,enemies=[(2,1)])),('r3 own c7',obs(3,enemies=[(3,7)])),
 ('LOW r3',obs(3,oxy=1,ndiv=1)),('LOW r3 enemy above c5',obs(3,oxy=1,ndiv=1,enemies=[(2,5)])),('LOW r3 enemy above c4',obs(3,oxy=1,ndiv=1,enemies=[(2,4)])),
 ('LOW r3 enemy above c7',obs(3,oxy=1,ndiv=1,enemies=[(2,7)])),('LOW r3 bullet above c6',obs(3,oxy=1,ndiv=1,bullets=[(2,6)])),('r4 diver r2',obs(4,divers=[(2,2)]))]
for add in [3.0,4.0,5.0]:
    W2=W2F.copy(); W2[24,9]=gold('W2')[24,9]+add; save('W2',W2)
    print('=== add',add)
    for t,x in cases: show(t,x,True)
W2=W2F.copy(); W2[24,9]=gold('W2')[24,9]+4.0; save('W2',W2); print('saved add 4; changed W2', (W2!=gold('W2')).sum(), saved())
