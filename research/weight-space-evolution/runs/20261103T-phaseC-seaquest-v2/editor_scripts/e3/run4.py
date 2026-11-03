import numpy as np, time
ramp_interval=100; max_oxygen=200; init_spawn_speed=20; diver_spawn_speed=30; init_move_interval=5
shot_cool_down=5; enemy_shot_interval=10; enemy_move_interval=5; diver_move_interval=5
class Env:
    def __init__(self, seed):
        self.random=np.random.RandomState(seed); self.action_map=['n','l','u','r','d','f']; self.reset()
    def reset(self):
        self.oxygen=max_oxygen; self.diver_count=0; self.sub_x=5; self.sub_y=0; self.sub_or=False
        self.f_bullets=[]; self.e_bullets=[]; self.e_fish=[]; self.e_subs=[]; self.divers=[]
        self.e_spawn_speed=init_spawn_speed; self.e_spawn_timer=self.e_spawn_speed; self.d_spawn_timer=diver_spawn_speed
        self.move_speed=init_move_interval; self.ramp_index=0; self.shot_timer=0; self.surface=True; self.terminal=False
        self.cause=None; self.bonus=0; self.kills=0; self.surfaces=0
    def act(self,a):
        r=0
        if self.terminal: return r,True
        a=self.action_map[a]
        if self.e_spawn_timer==0: self._spawn_enemy(); self.e_spawn_timer=self.e_spawn_speed
        if self.d_spawn_timer==0: self._spawn_diver(); self.d_spawn_timer=diver_spawn_speed
        if a=='f' and self.shot_timer==0:
            self.f_bullets+=[[self.sub_x,self.sub_y,self.sub_or]]; self.shot_timer=shot_cool_down
        elif a=='l': self.sub_x=max(0,self.sub_x-1); self.sub_or=False
        elif a=='r': self.sub_x=min(9,self.sub_x+1); self.sub_or=True
        elif a=='u': self.sub_y=max(0,self.sub_y-1)
        elif a=='d': self.sub_y=min(8,self.sub_y+1)
        for bullet in reversed(self.f_bullets):
            bullet[0]+=1 if bullet[2] else -1
            if bullet[0]<0 or bullet[0]>9: self.f_bullets.remove(bullet)
            else:
                removed=False
                for x in self.e_fish:
                    if bullet[0:2]==x[0:2]:
                        self.e_fish.remove(x); self.f_bullets.remove(bullet); r+=1; removed=True; break
                if not removed:
                    for x in self.e_subs:
                        if bullet[0:2]==x[0:2]:
                            self.e_subs.remove(x); self.f_bullets.remove(bullet); r+=1; break
        for diver in reversed(self.divers):
            if diver[0:2]==[self.sub_x,self.sub_y] and self.diver_count<6:
                self.divers.remove(diver); self.diver_count+=1
            else:
                if diver[3]==0:
                    diver[3]=diver_move_interval; diver[0]+=1 if diver[2] else -1
                    if diver[0]<0 or diver[0]>9: self.divers.remove(diver)
                    elif diver[0:2]==[self.sub_x,self.sub_y] and self.diver_count<6:
                        self.divers.remove(diver); self.diver_count+=1
                else: diver[3]-=1
        for sub in reversed(self.e_subs):
            if sub[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause=self.cause or 'esub'
            if sub[3]==0:
                sub[3]=self.move_speed; sub[0]+=1 if sub[2] else -1
                if sub[0]<0 or sub[0]>9: self.e_subs.remove(sub)
                elif sub[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause=self.cause or 'esub'
                else:
                    for x in self.f_bullets:
                        if sub[0:2]==x[0:2]:
                            self.e_subs.remove(sub); self.f_bullets.remove(x); r+=1; break
            else: sub[3]-=1
            if sub[4]==0:
                sub[4]=enemy_shot_interval; self.e_bullets+=[[sub[0],sub[1],sub[2]]]
            else: sub[4]-=1
        for bullet in reversed(self.e_bullets):
            if bullet[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause=self.cause or 'ebullet'
            bullet[0]+=1 if bullet[2] else -1
            if bullet[0]<0 or bullet[0]>9: self.e_bullets.remove(bullet)
            elif bullet[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause=self.cause or 'ebullet'
        for fish in reversed(self.e_fish):
            if fish[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause=self.cause or 'fish'
            if fish[3]==0:
                fish[3]=self.move_speed; fish[0]+=1 if fish[2] else -1
                if fish[0]<0 or fish[0]>9: self.e_fish.remove(fish)
                elif fish[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause=self.cause or 'fish'
                else:
                    for x in self.f_bullets:
                        if fish[0:2]==x[0:2]:
                            self.e_fish.remove(fish); self.f_bullets.remove(x); r+=1; break
            else: fish[3]-=1
        self.e_spawn_timer-=self.e_spawn_timer>0; self.d_spawn_timer-=self.d_spawn_timer>0; self.shot_timer-=self.shot_timer>0
        if self.oxygen<=0: self.terminal=True; self.cause=self.cause or 'oxygen'
        kr=r
        if self.sub_y>0: self.oxygen-=1; self.surface=False
        else:
            if not self.surface:
                if self.diver_count==0: self.terminal=True; self.cause=self.cause or 'surface0'
                else:
                    b=self._surface(); r+=b; self.bonus+=b; self.surfaces+=1
        self.kills+=kr
        return r,self.terminal
    def _surface(self):
        self.surface=True
        if self.diver_count==6: self.diver_count=0; r=self.oxygen*10//max_oxygen
        else: r=0
        self.oxygen=max_oxygen; self.diver_count-=1
        if self.e_spawn_speed>1 or self.move_speed>2:
            if self.move_speed>2 and self.ramp_index%2: self.move_speed-=1
            if self.e_spawn_speed>1: self.e_spawn_speed-=1
            self.ramp_index+=1
        return r
    def _spawn_enemy(self):
        lr=self.random.rand()<1/2; is_sub=self.random.rand()<1/3; x=0 if lr else 9; y=self.random.randint(low=1,high=9)
        if any([z[1]==y and z[2]!=lr for z in self.e_subs+self.e_fish]): return
        if is_sub: self.e_subs+=[[x,y,lr,self.move_speed,enemy_shot_interval]]
        else: self.e_fish+=[[x,y,lr,self.move_speed]]
    def _spawn_diver(self):
        lr=self.random.rand()<1/2; x=0 if lr else 9; y=self.random.randint(low=1,high=9)
        self.divers+=[[x,y,lr,diver_move_interval]]
    def state(self):
        s=np.zeros((10,10,10),dtype=bool)
        s[self.sub_y,self.sub_x,0]=1; bx=self.sub_x-1 if self.sub_or else self.sub_x+1; s[self.sub_y,bx,1]=1
        s[9,0:max(0,self.oxygen)*10//max_oxygen,7]=1; s[9,9-self.diver_count:9,8]=1
        for b in self.f_bullets: s[b[1],b[0],2]=1
        for b in self.e_bullets: s[b[1],b[0],4]=1
        for f in self.e_fish:
            s[f[1],f[0],5]=1; bx=f[0]-1 if f[2] else f[0]+1
            if 0<=bx<=9: s[f[1],bx,3]=1
        for f in self.e_subs:
            s[f[1],f[0],6]=1; bx=f[0]-1 if f[2] else f[0]+1
            if 0<=bx<=9: s[f[1],bx,3]=1
        for d in self.divers:
            s[d[1],d[0],9]=1; bx=d[0]-1 if d[2] else d[0]+1
            if 0<=bx<=9: s[d[1],bx,3]=1
        return s
def obs6(s):
    o=np.zeros((10,10,6),dtype=np.float64)
    o[...,0]=s[...,0]|s[...,1]; o[...,1]=s[...,5]|s[...,6]|s[...,4]; o[...,2]=s[...,5]|s[...,6]|s[...,9]
    o[...,3]=s[...,2]; o[...,4]=s[...,3]|s[...,1]; o[...,5]=s[...,7]|s[...,8]
    return o.reshape(-1)
def net(P,x):
    h1=np.tanh(x@P['W1']+P['b1']); h2=np.tanh(h1@P['W2']+P['b2']); return h2@P['W3']+P['b3']
def run_episode(P,seed,maxsteps=10000,trace=False):
    env=Env(seed); rng=np.random.RandomState(seed+12345); last=0; tot=0; t=0; acts=np.zeros(6,int); tr=[]
    while t<maxsteps:
        lg=net(P,obs6(env.state())); p=np.exp(lg-lg.max()); p/=p.sum(); a=rng.choice(6,p=p)
        if rng.rand()<0.1: a=last
        last=a; acts[a]+=1
        if trace: tr.append((t,a,env.sub_x,env.sub_y,env.oxygen,env.diver_count))
        r,term=env.act(a); tot+=r; t+=1
        if term: break
    return dict(score=tot,len=t,cause=env.cause or 'timeout',kills=env.kills,bonus=env.bonus,surf=env.surfaces,acts=acts,tr=tr)
def evalP(P,seeds,tlimit=100):
    res=[];t0=time.time()
    for s in seeds:
        res.append(run_episode(P,s))
        if time.time()-t0>tlimit: break
    return res
def summ(res,name=''):
    sc=np.array([r['score'] for r in res]); ln=np.array([r['len'] for r in res])
    causes={}
    for r in res: causes[r['cause']]=causes.get(r['cause'],0)+1
    acts=sum(r['acts'] for r in res); acts=acts/acts.sum()
    print(f"{name} n={len(res)} score={sc.mean():.2f}+-{sc.std()/np.sqrt(len(sc)):.2f} len={ln.mean():.0f} kills={np.mean([r['kills'] for r in res]):.1f} bonus={np.mean([r['bonus'] for r in res]):.2f} surf={np.mean([r['surf'] for r in res]):.2f} causes={causes} acts={np.round(acts,3)}")
    return sc
def gP(): return {k:gold(k).astype(np.float64) for k in ['W1','b1','W2','b2','W3','b3']}
def lP(): return {k:load(k).astype(np.float64) for k in ['W1','b1','W2','b2','W3','b3']}
def idx(r,c,ch): return (r*10+c)*6+ch
def varA():
    P=gP(); W=P['W1']
    for j in range(16,24):
        r=j-15
        for c in range(10): W[idx(r,c,2),j]=0
    return P
def varB():
    P=gP(); W=P['W1']
    for j in range(16,24):
        r=j-15
        for c in range(10):
            for ch in range(6): W[idx(r,c,ch),j]=0
        for c in (2,3,4):
            W[idx(r,c,1),j]=7; W[idx(r,c,2),j]=-3; W[idx(r,c-1,4),j]=4
        for c in (6,7,8):
            W[idx(r,c,1),j]=7; W[idx(r,c,2),j]=-3; W[idx(r,c+1,4),j]=4
        W[idx(r,5,1),j]=10
        P['b1'][j]=-5
    return P
seeds=range(5000,5250)
for name,P in [('gold',gP()),('A',varA()),('B',varB())]:
    res=evalP(P,seeds,tlimit=35); sc=summ(res,name)
    if name=='gold': g=sc
    else:
        n=min(len(g),len(sc)); d=sc[:n]-g[:n]; print('  paired diff',d.mean(),'+-',d.std()/np.sqrt(n))
