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
reset()
b3=gold('b3').copy(); b3[5]+=2.0; save('b3',b3); print(saved())
cases=[('empty r4',obs(4)),('empty r1',obs(1)),('empty r2',obs(2)),('empty r8',obs(8)),
 ('r3 own enemy c7',obs(3,enemies=[(3,7)])),('r3 own enemy c4',obs(3,enemies=[(3,4)])),
 ('r3 diver r4',obs(3,divers=[(4,2)])),('r3 diver r8',obs(3,divers=[(8,2)])),('r3 diver r2',obs(3,divers=[(2,8)])),
 ('r5 enemy left r4',obs(5,enemies=[(4,1)])),('r5 enemy left r7',obs(5,enemies=[(7,1)])),
 ('r3 bullet c7 own',obs(3,bullets=[(3,7)])),('LOW r5',obs(5,oxy=1,ndiv=1)),('LOW r5 enemy above c5',obs(5,oxy=1,ndiv=1,enemies=[(4,5)])),
 ('r4 both adjacent danger + own c7',obs(4,enemies=[(4,7),(3,5),(5,5)]))]
for t,x in cases: show('G '+t,x); show('E '+t,x,True)
