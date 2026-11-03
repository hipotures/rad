reset()
G={n:gold(n).copy() for n in ['W1','b1','W2','b2','W3','b3']}
W1,b1,W2,b2,W3,b3=[G[n] for n in ['W1','b1','W2','b2','W3','b3']]
def ix(r,c,ch): return (r*10+c)*6+ch
SROWS=list(range(3,9)); SU=[26+k for k in range(6)]
for i in range(25,32):
    row=i-23
    for j in range(26):
        w=W2[i,j]
        if w==0: continue
        if i in SU and ((0<=j<=7 and j+1==row) or (8<=j<=14 and j-6==row) or (16<=j<=23 and j-16==row)):
            W2[i,j]=2*w; b2[j]+=-w
        else:
            W2[i,j]=0.0; b2[j]+=-w
    W1[:,i]=0.0; b1[i]=0.0
# S_r: player (cell 6 + a neighbour) gated, +1 left danger, -1 approaching reward-object at right, 0 none
for u,r in zip(SU,SROWS):
    W1[ix(r,6,0),u]=10; W1[ix(r,5,0),u]=5; W1[ix(r,7,0),u]=5
    for c in range(4): W1[ix(r,c,1),u]=6
    for c in (8,9): W1[ix(r,c,2),u]=-6
    W1[ix(r,7,4),u]=6
    b1[u]=-15
# Pr = h1[25]: sub displaced right (col7 -> +3, col>=8 -> +6), player channel only
for r in range(9):
    W1[ix(r,7,0),25]=3
    for c in (8,9): W1[ix(r,c,0),25]=6
W1[:,25]*=0.3; b1[25]=0.0
def add(j,i,a,base): W2[i,j]+=a; b2[j]+=-a*base
# target T = sum(-S) - 5.5 (>0 when the sub's own row has a right target)
# h2[26] TRIG_R = T & not Pr & not near danger & player in rows>=3
for u in SU: add(26,u,-6,0)
b2[26]+=-33; add(26,25,-12,0)
for i in range(16,24): add(26,i,-1.5,-1)
for i in range(0,3): add(26,i,-6,-1)
# h2[27] TRIG_L = Pr>0.5 & not T
add(27,25,20,0.5)
for u in SU: add(27,u,8,0)
b2[27]+=8*5
for i in range(16,24): add(27,i,-4,-1)
# h2[28] GO_L = Pr>0.95
add(28,25,50,0.95)
# h2[29] FIRE_R = Pr>0.5 & T
add(29,25,20,0.5)
for u in SU: add(29,u,-8,0)
b2[29]+=-8*6
W3[26,3]=140; b3[3]=-100        # active r logit 40
W3[27,1]=140; W3[28,1]=140; b3[1]=40   # one active -> 40
W3[29,5]=20; b3[5]+=20          # active: +40 on fire
g=net(gold); f=net(lambda n:G[n])
def P(tag,s):
    pg=g(s)[0]; pc,l,h1,h2=f(s)
    print('%-26s g %s c %s Pr=%.2f S=%s h2=%s l=%s'%(tag,np.round(pg,2),np.round(pc,2),h1[25],np.round(h1[26:32],1),np.round(h2[26:30],2),np.round(l,0)))
for y in (5,):
    P('x5L empty r%d'%y,st(y)); P('x5L fishR8 r%d'%y,st(y,ent=[(y,8,'fish',False)])); P('x6R fishR8 r%d'%y,st(y,sx=6,orr=True,ent=[(y,8,'fish',False)]))
    P('x7R fishR8 r%d'%y,st(y,sx=7,orr=True,ent=[(y,8,'fish',False)])); P('x7R empty r%d'%y,st(y,sx=7,orr=True)); P('x5L fishL2 r%d'%y,st(y,ent=[(y,2,'fish',True)]))
P('x5L fishR r2',st(2,ent=[(2,8,'fish',False)]))
P('x5L fishR9 spawn',st(5,ent=[(5,9,'fish',False)])); P('x5L fish8 leaving',st(5,ent=[(5,8,'fish',True)]))
P('x5L bullet8',st(5,ent=[(5,8,'bullet',False)])); P('x5L diver8',st(5,ent=[(5,8,'diver',False)]))
P('x5L fishR8 other row',st(5,ent=[(6,8,'fish',False)])); P('x5L fishR + fishL',st(5,ent=[(5,8,'fish',False),(5,2,'fish',True)]))
P('x5L fishR + danger other',st(5,ent=[(5,8,'fish',False),(6,5,'fish',False)]))
P('x5L ascent fishR',st(5,oxy=50,div=2,ent=[(5,8,'fish',False)])); P('x7R ascent',st(5,sx=7,orr=True,oxy=50,div=2))
P('x7R fishL2',st(5,sx=7,orr=True,ent=[(5,2,'fish',True)])); P('x7R own danger x6',st(5,sx=7,orr=True,ent=[(5,6,'fish',True)]))
P('x6L empty',st(5,sx=6)); P('x6L fishR9',st(5,sx=6,ent=[(5,9,'fish',False)])); P('x8R empty',st(5,sx=8,orr=True)); P('x8R fishR9',st(5,sx=8,orr=True,ent=[(5,9,'fish',False)]))
P('x4L empty',st(5,sx=4)); P('x4L fishR8',st(5,sx=4,ent=[(5,8,'fish',False)])); P('x6R empty',st(5,sx=6,orr=True))
P('x5L fish(4,4)<-',st(5,ent=[(4,4,'fish',False)])); P('x5L own x6 dodge',st(5,ent=[(5,6,'fish',False)]))
P('x5L fishL r4 sub r3',st(3,ent=[(4,2,'fish',True)])); P('x5L diver r6 sub r3',st(3,ent=[(6,8,'diver',False)]))
tot=0
for n in G:
    c=int((G[n]!=gold(n)).sum()); tot+=c
    if c: save(n,G[n])
print('total changed',tot)
