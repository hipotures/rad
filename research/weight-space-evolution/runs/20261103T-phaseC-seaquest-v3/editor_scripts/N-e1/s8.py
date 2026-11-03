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
W1=gold('W1').copy()
def idx(r,c,ch): return (r*10+c)*6+ch
for k,r in enumerate(range(1,9)):
    u=16+k
    for c in (6,7,8): W1[idx(r,c,2),u]=0.0
    W1[idx(r,8,1),u]=5.0
save('W1',W1)
print('changed', (W1!=gold('W1')).sum())
for r in [3,5]:
  for e,c in [(r,7),(r,8),(r,9),(r,4),(r,3),(r-1,7),(r-1,8),(r+1,7)]:
    x=obs(r,enemies=[(e,c)]); show('G r%d enemy(%d,%d)'%(r,e,c),x); show('E r%d enemy(%d,%d)'%(r,e,c),x,True)
  x=obs(r,oxy=1,ndiv=2,enemies=[(r-1,7)]); show('G LOW r%d enemy(%d,7)'%(r,r-1),x); show('E LOW',x,True)
  x=obs(r,oxy=1,ndiv=2,enemies=[(r-1,8)]); show('G LOW r%d enemy(%d,8)'%(r,r-1),x); show('E LOW',x,True)
  x=obs(r,enemies=[(r,8),(r-1,8)]); show('G both r,r-1 col8',x); show('E',x,True)
  x=obs(r,enemies=[(r,8),(r-1,8),(r+1,8)]); show('G 3 rows col8',x); show('E',x,True)
x=obs(8,enemies=[(8,8)]); show('G r8 enemy (8,8)',x); show('E',x,True)
x=obs(2,enemies=[(2,8)]); show('G r2 enemy (2,8)',x); show('E',x,True)
