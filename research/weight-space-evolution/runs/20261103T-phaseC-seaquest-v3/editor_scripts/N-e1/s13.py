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
W2=gold('W2').copy(); b2=gold('b2').copy(); base=np.tanh(-3.0)
ker=[0.35,0.20,0.12,0.08,0.05,0.03,0.02,0.01]
n=0
for i in range(25,32):
    t=i-23
    for j in list(range(8,15))+list(range(16,24)):
        dest = j-7 if j<15 else j-15
        new=ker[abs(dest-t)]
        old=W2[i,j]
        if new!=old:
            b2[j]-= (new-old)*base
            W2[i,j]=new; n+=1
save('W2',W2); save('b2',b2)
b3=gold('b3').copy(); b3[5]+=2.0; save('b3',b3)
print('W2 changed',n,'b2 changed',(b2!=gold('b2')).sum())
for r in [3,5,7]:
  show('G empty r%d'%r,obs(r)); show('F',obs(r),True)
  for t in range(2,9):
    if t==r: continue
    x=obs(r,enemies=[(t,1)]); show('G r%d enemyL row%d'%(r,t),x); show('F',x,True)
for t,x in [('r3 diver r8',obs(3,divers=[(8,2)])),('r5 own enemy c3',obs(5,enemies=[(5,2)])),('r5 own c7',obs(5,enemies=[(5,7)])),('LOW r5',obs(5,oxy=1,ndiv=1)),('r5 enL r4 + danger r4 c5',obs(5,enemies=[(4,1),(4,5)]))]:
  show('G '+t,x); show('F',x,True)
