P=gP()
np.set_printoptions(precision=1,suppress=True,linewidth=200)
n=0
for seed in range(2000,2040):
    env=Env(seed); rng=np.random.RandomState(seed+12345); last=0; hist=[]
    for t in range(10000):
        sc=f"t={t} sub=({env.sub_x},{env.sub_y}) ms={env.move_speed} ox={env.oxygen} dc={env.diver_count} st={env.shot_timer} fish={[f[:4] for f in env.e_fish if abs(f[1]-env.sub_y)<=2]} subs={[f[:4] for f in env.e_subs if abs(f[1]-env.sub_y)<=2]} bul={[f for f in env.e_bullets if abs(f[1]-env.sub_y)<=2]}"
        lg=net(P,obs6(env.state())); p=np.exp(lg-lg.max()); p/=p.sum(); a=rng.choice(6,p=p)
        if rng.rand()<0.1: a=last
        last=a
        hist.append(sc+f" logits(n,l,u,r,d,f)={lg-lg.max()} a={a}")
        r,term=env.act(a)
        if term:
            if env.cause in ('fish','esub','ebullet'):
                print('---',seed,env.cause)
                for h in hist[-4:]: print(h)
                n+=1
            break
    if n>=14: break
