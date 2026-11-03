import collections
stats=collections.Counter(); ex=[]
G=gp()
orig=Env.act
def act2(self,a):
    x=self.obs(); L=fwd(G,x[None])[0]; L=L-L.max(); p=np.exp(L); p/=p.sum()
    pre=[(tuple(f[:3])) for f in self.e_fish+self.e_subs]; pb=[tuple(b[:3]) for b in self.e_bullets]; sy=self.sub_y
    r,t=orig(self,a)
    if t and self.cause in('fish','sub','bullet'):
        pc=p[a]; tag='sticky' if pc<0.02 else ('lowp' if pc<0.3 else 'hip')
        stats[(self.cause,self.action_map[a],tag)]+=1
        if len(ex)<12 and tag=='hip' and self.action_map[a] in 'ud': ex.append((self.cause,self.action_map[a],sy,'->',self.sub_y,pre,pb,p.round(2)))
    return r,t
Env.act=act2
R=run(G,300,seed0=3000,tlimit=80); summ('gold',R)
for k,v in stats.most_common(): print(k,v)
for e in ex: print(e)
