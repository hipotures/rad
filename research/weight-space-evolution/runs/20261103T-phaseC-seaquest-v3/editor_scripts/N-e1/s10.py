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
K=-12.0
for k in range(1,9):
    i=16+k-1
    for j in ([8+k-1] if k>=1 else [])+[16+k-1]:
        if k==8 and j==15: continue
        assert W2[i,j]==-3.0,(i,j,W2[i,j])
        b2[j]-= (K-(-3.0))*base
        W2[i,j]=K
save('W2',W2); save('b2',b2)
print('changed W2',(W2!=gold('W2')).sum(),'b2',(b2!=gold('b2')).sum())
for r in range(0,9):
    x=obs(r); show('G empty r%d'%r,x); show('E',x,True)
for r in [2,3,5,7]:
  for e,c in [(r-1,7),(r-1,8),(r-1,5),(r-1,3),(r+1,7),(r,7),(r,3)]:
    for lo in [0,1]:
      kw=dict(oxy=1,ndiv=2) if lo else {}
      x=obs(r,enemies=[(e,c)],**kw); show('G%s r%d enemy(%d,%d)'%('LOW' if lo else '',r,e,c),x); show('E',x,True)
  for d in [r-1,r+1]:
    x=obs(r,divers=[(d,2)]); show('G r%d diver row %d'%(r,d),x); show('E',x,True)
