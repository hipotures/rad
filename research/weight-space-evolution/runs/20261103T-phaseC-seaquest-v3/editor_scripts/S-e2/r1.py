import numpy as np, time
ramp_interval=100; max_oxygen=200; init_spawn_speed=20; diver_spawn_speed=30; init_move_interval=5
shot_cool_down=5; enemy_shot_interval=10; enemy_move_interval=5; diver_move_interval=5
class Env:
    def __init__(self, seed):
        self.action_map=['n','l','u','r','d','f']; self.ramping=True
        self.random=np.random.RandomState(seed); self.reset()
    def act(self,a):
        r=0
        if self.terminal: return r,self.terminal
        a=self.action_map[a]
        if self.e_spawn_timer==0:
            self._spawn_enemy(); self.e_spawn_timer=self.e_spawn_speed
        if self.d_spawn_timer==0:
            self._spawn_diver(); self.d_spawn_timer=diver_spawn_speed
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
            if sub[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause='sub'
            if sub[3]==0:
                sub[3]=self.move_speed; sub[0]+=1 if sub[2] else -1
                if sub[0]<0 or sub[0]>9: self.e_subs.remove(sub)
                elif sub[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause='sub'
                else:
                    for x in self.f_bullets:
                        if sub[0:2]==x[0:2]:
                            self.e_subs.remove(sub); self.f_bullets.remove(x); r+=1; break
            else: sub[3]-=1
            if sub[4]==0:
                sub[4]=enemy_shot_interval; self.e_bullets+=[[sub[0],sub[1],sub[2]]]
            else: sub[4]-=1
        for bullet in reversed(self.e_bullets):
            if bullet[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause='bullet'
            bullet[0]+=1 if bullet[2] else -1
            if bullet[0]<0 or bullet[0]>9: self.e_bullets.remove(bullet)
            else:
                if bullet[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause='bullet'
        for fish in reversed(self.e_fish):
            if fish[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause='fish'
            if fish[3]==0:
                fish[3]=self.move_speed; fish[0]+=1 if fish[2] else -1
                if fish[0]<0 or fish[0]>9: self.e_fish.remove(fish)
                elif fish[0:2]==[self.sub_x,self.sub_y]: self.terminal=True; self.cause='fish'
                else:
                    for x in self.f_bullets:
                        if fish[0:2]==x[0:2]:
                            self.e_fish.remove(fish); self.f_bullets.remove(x); r+=1; break
            else: fish[3]-=1
        self.e_spawn_timer-=self.e_spawn_timer>0
        self.d_spawn_timer-=self.d_spawn_timer>0
        self.shot_timer-=self.shot_timer>0
        if self.oxygen<=0: self.terminal=True; self.cause='oxygen'
        if self.sub_y>0:
            self.oxygen-=1; self.surface=False
        else:
            if not self.surface:
                if self.diver_count==0: self.terminal=True; self.cause='surf0'
                else:
                    rr=self._surface(); r+=rr; self.bonus+=rr; self.nsurf+=1
        return r,self.terminal
    def _surface(self):
        self.surface=True
        if self.diver_count==6:
            self.diver_count=0; r=self.oxygen*10//max_oxygen
        else: r=0
        self.oxygen=max_oxygen; self.diver_count-=1
        if self.ramping and (self.e_spawn_speed>1 or self.move_speed>2):
            if self.move_speed>2 and self.ramp_index%2: self.move_speed-=1
            if self.e_spawn_speed>1: self.e_spawn_speed-=1
            self.ramp_index+=1
        return r
    def _spawn_enemy(self):
        lr=self.random.rand()<1/2; is_sub=self.random.rand()<1/3
        x=0 if lr else 9; y=self.random.randint(low=1,high=9)
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
        if 0<=bx<=9:
            s[self.sub_y,bx,0]=1; s[self.sub_y,bx,4]=1
        else:
            # numpy negative index wraps / out of range for 10 -> mimic original
            if bx==-1: s[self.sub_y,9,0]=1; s[self.sub_y,9,4]=1
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
    def reset(self):
        self.oxygen=max_oxygen; self.diver_count=0; self.sub_x=5; self.sub_y=0; self.sub_or=False
        self.f_bullets=[]; self.e_bullets=[]; self.e_fish=[]; self.e_subs=[]; self.divers=[]
        self.e_spawn_speed=init_spawn_speed; self.e_spawn_timer=self.e_spawn_speed; self.d_spawn_timer=diver_spawn_speed
        self.move_speed=init_move_interval; self.ramp_index=0; self.shot_timer=0; self.surface=True; self.terminal=False
        self.cause=None; self.bonus=0; self.nsurf=0

def fwd(P,X):
    h1=np.tanh(X@P['W1']+P['b1']); h2=np.tanh(h1@P['W2']+P['b2']); return h2@P['W3']+P['b3']

def run(P,n,seed0=0,maxsteps=10000,tlimit=50):
    rng=np.random.RandomState(seed0+12345)
    envs=[Env(seed0+i) for i in range(n)]
    last=np.zeros(n,dtype=int); score=np.zeros(n); steps=np.zeros(n,dtype=int)
    acts=np.zeros((n,6),dtype=int); alive=np.ones(n,bool); t0=time.time()
    for t in range(maxsteps):
        idx=np.nonzero(alive)[0]
        if len(idx)==0 or time.time()-t0>tlimit: break
        X=np.stack([envs[i].obs() for i in idx])
        L=fwd(P,X); L=L-L.max(1,keepdims=True); p=np.exp(L); p/=p.sum(1,keepdims=True)
        u=rng.rand(len(idx)); a=(p.cumsum(1)<u[:,None]).sum(1); a=np.minimum(a,5)
        st=rng.rand(len(idx))<0.1
        a=np.where(st,last[idx],a)
        for k,i in enumerate(idx):
            r,term=envs[i].act(int(a[k])); score[i]+=r; steps[i]+=1; acts[i,a[k]]+=1; last[i]=a[k]
            if term: alive[i]=False
    causes={}
    for e in envs: causes[e.cause]=causes.get(e.cause,0)+1
    return dict(score=score,steps=steps,acts=acts,causes=causes,bonus=np.array([e.bonus for e in envs]),
                nsurf=np.array([e.nsurf for e in envs]),unfinished=int(alive.sum()),time=time.time()-t0)

def summ(name,R):
    s=R['score']; print(name,"mean %.2f se %.2f len %.0f bonus %.2f nsurf %.2f unfinished %d t %.1fs"%(s.mean(),s.std()/np.sqrt(len(s)),R['steps'].mean(),R['bonus'].mean(),R['nsurf'].mean(),R['unfinished'],R['time']),R['causes'],(R['acts'].sum(0)/R['acts'].sum()).round(3))
def gp(): return {k:gold(k).astype(np.float64) for k in ['W1','b1','W2','b2','W3','b3']}
P=gp(); R=run(P,200,seed0=0,tlimit=100); summ('gold',R)
import numpy as np
print(np.sort(R['score'])[::10])
