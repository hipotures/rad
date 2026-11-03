import numpy as np
reset()
W1=gold('W1').copy()
for k,u in enumerate(range(16,24)):
    r=k+1
    for c in (7,):
        i=(r*10+c)*6+2
        print(u,r,c,W1[i,u]); W1[i,u]=0.0
save('W1',W1)
P=[load(n) for n in ['W1','b1','W2','b2','W3','b3']]
G=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
for c in range(10):
    lr=c<5
    print('fish row3 col',c,'gold',act(st(sub=(5,4),fish=[(c,3,lr)]),G)[0],act(st(sub=(5,4),ox=50,fish=[(c,3,lr)]),G)[0],
          'new',act(st(sub=(5,4),fish=[(c,3,lr)]),P)[0],act(st(sub=(5,4),ox=50,fish=[(c,3,lr)]),P)[0],
          '| own row gold',act(st(sub=(5,4),fish=[(c,4,lr)]),G)[0] if c not in (5,6) else '-', 'new',act(st(sub=(5,4),fish=[(c,4,lr)]),P)[0] if c not in (5,6) else '-')
