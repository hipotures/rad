import copy
from collections import Counter
W=[gold(n) for n in ['W1','b1','W2','b2','W3','b3']]
f=net(W)
C=Counter(); ex=[]
for ep in range(150):
    env=Env(5000+ep); rng=np.random.RandomState(777+ep); prev=0; hist=[]
    for t in range(10000):
        x=env.obs(); lg=f(x); p=np.exp(lg-lg.max()); p/=p.sum(); a=rng.choice(6,p=p)
        if rng.rand()<0.1: a=prev
        prev=a
        snap=(env.sub_x,env.sub_y,[e[:3] for e in env.e_fish],[e[:3] for e in env.e_subs],[e[:3] for e in env.e_bullets],env.diver_count,env.oxygen, np.round(p,2))
        hist.append((a,snap))
        r,term=env.act(a)
        if term: break
    a,s=hist[-1]
    sx,sy=s[0],s[1]
    # find killer
    kill='?'
    for name,lst in (('fish',s[2]),('sub',s[3]),('bul',s[4])):
        for e in lst:
            if e[1]==env.sub_y and abs(e[0]-env.sub_x)<=1:
                kill=f"{name} from {'L' if e[2] else 'R'}"
    moved = 'vert' if env.sub_y!=sy else 'stay'
    C[(env.cause,kill,moved,'nesacts'+''.join('nlurdf'[h[0]] for h in hist[-3:]))]+=1
    if len(ex)<6: ex.append((env.cause,kill,moved,[(('nlurdf'[h[0]]),h[1][0],h[1][1],h[1][2],h[1][3],h[1][4]) for h in hist[-4:]]))
for k,v in C.most_common(40): print(v,k)
for e in ex: print(e)
