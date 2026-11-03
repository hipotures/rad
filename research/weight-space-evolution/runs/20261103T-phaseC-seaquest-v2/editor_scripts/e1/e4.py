reset()
W1=gold('W1').copy(); b1=gold('b1').copy(); W2=gold('W2').copy(); b2=gold('b2').copy(); W3=gold('W3').copy(); b3=gold('b3').copy()
def ix(r,c,ch): return (r*10+c)*6+ch
# free h1[25..31]: remove their influence on h2 0..25, preserving the no-left-danger state exactly
for i in range(25,32):
    for j in range(26):
        w=W2[i,j]
        if w!=0: b2[j]+= -w; W2[i,j]=0.0
    W1[:,i]=0.0; b1[i]=0.0
# h1[25] FR: sub facing right at x=6
for r in range(9):
    W1[ix(r,5,4),25]+=4; W1[ix(r,6,0),25]+=4; W1[ix(r,6,4),25]+=-4; W1[ix(r,4,2),25]+=-4; W1[ix(r,6,2),25]+=-4
b1[25]=-6
# h1[26] POS: sub off-centre
for r in range(9):
    for c in range(10):
        if c>=7: W1[ix(r,c,0),26]=3
        elif c<=4: W1[ix(r,c,0),26]=-3
b1[26]=0
# h1[27..31] TR rows 4..8: sub at cols 5-6 and approaching enemy at cols 8-9 in same row, no near danger
for k,r in enumerate(range(4,9)):
    u=27+k
    W1[ix(r,5,0),u]=6; W1[ix(r,6,0),u]=6
    for c in (8,9): W1[ix(r,c,1),u]=3; W1[ix(r,c,2),u]=3
    W1[ix(r,7,4),u]=-6
    for c in range(3,8): W1[ix(r,c,1),u]=-6
    b1[u]=-15
# h2[26] TRIG_R
for u in range(27,32): W2[u,26]=6
W2[25,26]=-8; b2[26]=13
# h2[27] TRIG_L
W2[25,27]=8
for u in range(27,32): W2[u,27]=-6
b2[27]=-35
# h2[28] GO_L, h2[29] GO_R
W2[26,28]=6; b2[28]=-3
W2[26,29]=-6; b2[29]=-3
W3[26,3]=122; W3[29,3]=122; b3[3]=22
W3[27,1]=140; W3[28,1]=140; b3[1]=40
g=net(gold)
def fset(): 
    import numpy as np
    d={'W1':W1,'b1':b1,'W2':W2,'b2':b2,'W3':W3,'b3':b3}; return net(lambda n:d[n])
f=fset()
A='nlurdf'
def P(tag,s):
    pg=g(s)[0]; pc,l,h1,h2=f(s)
    print('%-34s gold %s cand %s h2[26:30]=%s'%(tag,np.round(pg,2),np.round(pc,2),np.round(h2[26:30],2)))
P('x5L empty r5',st(5))
P('x5L empty r3',st(3))
P('x5L fishR (5,8)<-',st(5,ent=[(5,8,'fish',False)]))
P('x5L fishR (5,9)<-',st(5,ent=[(5,9,'fish',False)]))
P('x5L fishR (7,8)<-',st(7,ent=[(7,8,'fish',False)]))
P('x5L subR (8,9)<-',st(8,ent=[(8,9,'sub',False)]))
P('x5L fish (5,8)-> leaving',st(5,ent=[(5,8,'fish',True)]))
P('x5L diver (5,8)',st(5,ent=[(5,8,'diver',False)]))
P('x5L fishR (3,8) row3',st(3,ent=[(3,8,'fish',False)]))
P('x5L fishR other row',st(5,ent=[(6,8,'fish',False)]))
P('x5L fishR + fishL',st(5,ent=[(5,8,'fish',False),(5,2,'fish',True)]))
P('x5L fishR + near danger x7',st(5,ent=[(5,9,'fish',False),(5,7,'fish',False)]))
P('x5L ascent + fishR',st(5,oxy=50,div=2,ent=[(5,8,'fish',False)]))
P('x6R fishR (5,8)',st(5,sx=6,orr=True,ent=[(5,8,'fish',False)]))
P('x6R fishR (5,9)',st(5,sx=6,orr=True,ent=[(5,9,'fish',False)]))
P('x6R empty',st(5,sx=6,orr=True))
P('x6R fishL (5,2)',st(5,sx=6,orr=True,ent=[(5,2,'fish',True)]))
P('x6R ascent',st(5,sx=6,orr=True,oxy=50,div=2))
P('x6R own danger x7 bullet',st(5,sx=6,orr=True,ent=[(5,7,'bullet',False)]))
P('x7R empty',st(5,sx=7,orr=True))
P('x6L empty',st(5,sx=6,orr=False))
P('x4L empty',st(5,sx=4,orr=False))
P('x5R empty',st(5,sx=5,orr=True))
P('x5L fish(4,4)<- elsewhere',st(5,ent=[(4,4,'fish',False)]))
P('x6R fish(4,4)<- elsewhere',st(5,sx=6,orr=True,ent=[(4,4,'fish',False)]))
P('x5L fishL (5,2) gold-check',st(5,ent=[(5,2,'fish',True)]))
P('x5L own x6 dodge',st(5,ent=[(5,6,'fish',False)]))
for n,a in [('W1',W1),('b1',b1),('W2',W2),('b2',b2),('W3',W3),('b3',b3)]:
    nchg=int((a!=gold(n)).sum()); print(n,'changed',nchg)
    if nchg: save(n,a)
