reset()
G={n:gold(n).copy() for n in ['W1','b1','W2','b2','W3','b3']}
W1,b1,W2,b2,W3,b3=[G[n] for n in ['W1','b1','W2','b2','W3','b3']]
def ix(r,c,ch): return (r*10+c)*6+ch
SROWS=list(range(3,9)); SU=[26+k for k in range(6)]   # h1[26..31] -> rows 3..8 (gold: left danger rows 3..8)
# --- re-wire gold connections of h1[25..31] ---
for i in range(25,32):
    row=i-23  # gold h1[25+k] = left danger in row k+2
    for j in range(26):
        w=W2[i,j]
        if w==0: continue
        if i in SU and ((0<=j<=7 and j+1==row) or (8<=j<=14 and j-6==row) or (16<=j<=23 and j-16==row)):
            # same-row connection: new S in {L:+1,none:0,R:-1} -> w'=2w, delta=-w
            W2[i,j]=2*w; b2[j]+=-w
        else:
            W2[i,j]=0.0; b2[j]+=-w
    W1[:,i]=0.0; b1[i]=0.0
# --- S_r units: player-gated signed side detector ---
for u,r in zip(SU,SROWS):
    for c in (5,6,7): W1[ix(r,c,0),u]=10
    for c in range(4): W1[ix(r,c,1),u]=6          # left danger (as gold)
    for c in (8,9): W1[ix(r,c,2),u]=-6            # approaching reward-object at right
    W1[ix(r,7,4),u]=6                              # cancel right-moving object at col 8
    b1[u]=-20
# --- Z unit h1[25]: position/orientation ---
for r in range(9):
    for c in range(10):
        if c>=7: W1[ix(r,c,0),25]+=6
        elif c<=4: W1[ix(r,c,0),25]+=-6
    W1[ix(r,5,4),25]+=2; W1[ix(r,6,0),25]+=2; W1[ix(r,6,4),25]+=-2; W1[ix(r,4,2),25]+=-2; W1[ix(r,6,2),25]+=-2
W1[:,25]*=0.6; b1[25]=0.0
# helper to add a linear term a*(h1[i]-base) into h2 unit j
def add(j,i,a,base): W2[i,j]+=a; b2[j]+=-a*base
# h2[26] TRIG_R: 6*sum(-S) - 33 - 8Z - 1.5*sum(h1[16..23]+1) - 6*sum_{r<=2}(h1[r]+1)
for u in SU: add(26,u,-6,0)
b2[26]+=-33; add(26,25,-8,0)
for i in range(16,24): add(26,i,-1.5,-1)
for i in range(0,3): add(26,i,-6,-1)
# h2[27] TRIG_L: 30*(Z-0.91) - 8*(sum(-S)-5)
add(27,25,30,0.91)
for u in SU: add(27,u,8,0)
b2[27]+=8*5
for i in range(0,3): add(27,i,0,0)
# h2[28] GO_R: 30*(-Z-0.91)
add(28,25,-30,-0.91)
W3[26,3]=122; W3[28,3]=122; b3[3]=22
W3[27,1]=140; b3[1]=40+140   # one unit only: active -> 40+... fix below
b3[1]=-100                    # active: -100+140=40, inactive -240
g=net(gold); f=net(lambda n:G[n])
def P(tag,s):
    pg=g(s)[0]; pc,l,h1,h2=f(s)
    print('%-28s gold %s cand %s Z=%.2f S=%s h2=%s'%(tag,np.round(pg,2),np.round(pc,2),h1[25],np.round(h1[26:32],1),np.round(h2[26:29],2)))
for y in (3,5,8):
    P('x5L empty r%d'%y,st(y)); P('x5L fishR8 r%d'%y,st(y,ent=[(y,8,'fish',False)])); P('x6R fishR8 r%d'%y,st(y,sx=6,orr=True,ent=[(y,8,'fish',False)]))
    P('x6R empty r%d'%y,st(y,sx=6,orr=True)); P('x5L fishL2 r%d'%y,st(y,ent=[(y,2,'fish',True)]))
P('x5L empty r2',st(2)); P('x5L fishR r2',st(2,ent=[(2,8,'fish',False)])); P('x5L r1',st(1)); P('x5L r0',st(0))
P('x5L fishR9 spawn',st(5,ent=[(5,9,'fish',False)]))
P('x5L fish8 leaving',st(5,ent=[(5,8,'fish',True)]))
P('x5L bullet8',st(5,ent=[(5,8,'bullet',False)]))
P('x5L diver8',st(5,ent=[(5,8,'diver',False)]))
P('x5L fishR8 other row',st(5,ent=[(6,8,'fish',False)]))
P('x5L fishR + fishL',st(5,ent=[(5,8,'fish',False),(5,2,'fish',True)]))
P('x5L fishR + danger row',st(5,ent=[(5,8,'fish',False),(6,5,'fish',False)]))
P('x5L ascent fishR',st(5,oxy=50,div=2,ent=[(5,8,'fish',False)]))
P('x6R ascent',st(5,sx=6,orr=True,oxy=50,div=2))
P('x6R fishL2',st(5,sx=6,orr=True,ent=[(5,2,'fish',True)]))
P('x7R empty',st(5,sx=7,orr=True)); P('x7R fishR9',st(5,sx=7,orr=True,ent=[(5,9,'fish',False)]))
P('x6L empty',st(5,sx=6)); P('x4L empty',st(5,sx=4)); P('x5R empty',st(5,sx=5,orr=True))
P('x5L fish(4,4)<-',st(5,ent=[(4,4,'fish',False)])); P('x5L fish(4,6)->',st(5,ent=[(4,6,'fish',True)]));P('x5L fish(4,5)<-',st(5,ent=[(4,5,'fish',False)]))
P('x6R fish(4,4)<-',st(5,sx=6,orr=True,ent=[(4,4,'fish',False)])); P('x6R fish(4,6)<-',st(5,sx=6,orr=True,ent=[(4,6,'fish',False)]))
P('x5L own x6 dodge',st(5,ent=[(5,6,'fish',False)])); P('x5L fishL r4 sub r3',st(3,ent=[(4,2,'fish',True)]))
P('x5L diver r6 sub r3',st(3,ent=[(6,8,'diver',False)]))
tot=0
for n in G:
    c=int((G[n]!=gold(n)).sum()); tot+=c; print(n,c)
    if c: save(n,G[n])
print('total',tot)
