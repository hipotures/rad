import collections
P=gP()
# death diagnostics: reproduce episodes, at death record killer direction
D=collections.Counter(); rows=collections.Counter(); lastacts=collections.Counter()
pre=collections.Counter()
for seed in range(2000,2080):
    env=Env(seed); rng=np.random.RandomState(seed+12345); last=0; hist=[]
    for t in range(10000):
        st=[(list(f),'fish') for f in env.e_fish]+[(list(f),'sub') for f in env.e_subs]+[(list(b),'bul') for b in env.e_bullets]
        sx,sy=env.sub_x,env.sub_y
        lg=net(P,obs6(env.state())); p=np.exp(lg-lg.max()); p/=p.sum(); a=rng.choice(6,p=p)
        if rng.rand()<0.1: a=last
        last=a; hist.append(a)
        r,term=env.act(a)
        if term:
            if env.cause in ('fish','esub','ebullet'):
                # find killer: object at sub pos now or before
                k=None
                for (o,kind) in st:
                    if o[1]==env.sub_y and abs(o[0]-env.sub_x)<=1: k=(kind,'fromLeft' if o[2] else 'fromRight', o[0]-sx, o[1]-sy)
                D[(k[0],k[1]) if k else ('?',)]+=1
                if k: rows[(k[3],)]+=1
                lastacts[tuple(hist[-3:])]+=1
                pre[(sy,env.sub_y)]+=1
            else: D[(env.cause,)]+=1
            break
print(D); print('dy of killer rel to sub before move',rows); print('last3 acts',lastacts.most_common(10)); print('sub y before/after',pre.most_common(10))
