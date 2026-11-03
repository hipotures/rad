import numpy as np, time
max_oxygen=200; init_spawn_speed=20; diver_spawn_speed=30; init_move_interval=5
shot_cool_down=5; enemy_shot_interval=10; diver_move_interval=5
class Env:
    def __init__(self, seed):
        self.random=np.random.RandomState(seed); self.reset()
    def reset(self):
        self.oxygen=max_oxygen; self.diver_count=0; self.sub_x=5; self.sub_y=0; self.sub_or=False
        self.f_bullets=[]; self.e_bullets=[]; self.e_fish=[]; self.e_subs=[]; self.divers=[]
        self.e_spawn_speed=init_spawn_speed; self.e_spawn_timer=self.e_spawn_speed; self.d_spawn_timer=diver_spawn_speed
        self.move_speed=init_move_interval; self.ramp_index=0; self.shot_timer=0; self.surface=True; self.terminal=False
        self.cause=None; self.surfaces=0; self.full=0
    def act(self,a):
        r=0
        if self.terminal: return r
        a='nlurdf'[a]
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
        if self.sub_y>0: self.oxygen-=1; self.surface=False
        else:
            if not self.surface:
                if self.diver_count==0: self.terminal=True; self.cause=self.cause or 'surf0'
                else: r+=self._surface()
        return r
    def _surface(self):
        self.surface=True; self.surfaces+=1
        if self.diver_count==6: self.diver_count=0; r=self.oxygen*10//max_oxygen; self.full+=1
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
    def obs(self):
        s=np.zeros((10,10,6),dtype=np.float32)
        s[self.sub_y,self.sub_x,0]=1
        bx=self.sub_x-1 if self.sub_or else self.sub_x+1
        s[self.sub_y,bx,0]=1; s[self.sub_y,bx,4]=1
        s[9,0:max(0,self.oxygen)*10//max_oxygen,5]=1
        s[9,9-self.diver_count:9,5]=1
        for b in self.f_bullets: s[b[1],b[0],3]=1
        for b in self.e_bullets: s[b[1],b[0],1]=1
        for f in self.e_fish+self.e_subs:
            s[f[1],f[0],1]=1; s[f[1],f[0],2]=1
            bx=f[0]-1 if f[2] else f[0]+1
            if 0<=bx<=9: s[f[1],bx,4]=1
        for d in self.divers:
            s[d[1],d[0],2]=1
            bx=d[0]-1 if d[2] else d[0]+1
            if 0<=bx<=9: s[d[1],bx,4]=1
        return s.reshape(-1)

def get_params(fn):
    return [fn(n).astype(np.float64) for n in ['W1','b1','W2','b2','W3','b3']]
def logits_of(P,X):
    W1,b1,W2,b2,W3,b3=P
    return np.tanh(np.tanh(X@W1+b1)@W2+b2)@W3+b3

def run_batch(P, seeds, maxsteps=10000, tlimit=50, rec=None):
    rng=np.random.RandomState(seeds[0]*7+1)
    envs=[Env(s) for s in seeds]; n=len(envs)
    score=np.zeros(n); length=np.zeros(n,int); prev=np.zeros(n,int); alive=list(range(n))
    acts=np.zeros(6); t0=time.time(); step=0
    while alive and step<maxsteps and time.time()-t0<tlimit:
        X=np.stack([envs[i].obs() for i in alive])
        L=logits_of(P,X); L=L-L.max(1,keepdims=True); p=np.exp(L); p/=p.sum(1,keepdims=True)
        u=rng.rand(len(alive)); a=(p.cumsum(1)<u[:,None]).sum(1); a=np.minimum(a,5)
        st=rng.rand(len(alive))<0.1
        new=[]
        for k,i in enumerate(alive):
            ai=prev[i] if st[k] else a[k]; prev[i]=ai; acts[ai]+=1
            if rec is not None: rec(envs[i],X[k],ai)
            score[i]+=envs[i].act(ai); length[i]+=1
            if not envs[i].terminal: new.append(i)
        alive=new; step+=1
    causes={}
    for i,e in enumerate(envs):
        c=e.cause if e.terminal else ('timeout' if step>=maxsteps else 'cut')
        causes[c]=causes.get(c,0)+1
    return dict(score=score,length=length,causes=causes,acts=acts/acts.sum(),surf=np.array([e.surfaces for e in envs]),full=np.array([e.full for e in envs]),envs=envs)
def summ(name,R):
    s=R['score']; print(name,'mean %.2f se %.2f len %.0f'%(s.mean(),s.std()/np.sqrt(len(s)),R['length'].mean()),'causes',R['causes'],'acts',np.round(R['acts'],3),'surf %.2f full %.2f'%(R['surf'].mean(),R['full'].mean()),flush=True)
P=get_params(gold)
for n in ['W1','b1','W2','b2','W3','b3']:
    print(n, gold(n).shape)
print('b3',gold('b3')); print('b2',np.round(gold('b2'),2)); print('b1',np.round(gold('b1'),2))
R=run_batch(P,list(range(200)),tlimit=90)
summ('gold',R)
print('score pct',np.percentile(R['score'],[10,25,50,75,90]))
