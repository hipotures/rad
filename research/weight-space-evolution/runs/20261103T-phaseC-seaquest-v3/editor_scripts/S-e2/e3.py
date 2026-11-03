# death forensics: wrap act to record the killer
import collections
stats=collections.Counter()
orig=Env.act
def act2(self,a):
    pre=(self.sub_x,self.sub_y); pre_f=[list(f) for f in self.e_fish+self.e_subs+self.e_bullets]
    r,t=orig(self,a)
    if t and self.cause in('fish','sub','bullet'):
        # find killer at sub position
        k=[f for f in self.e_fish+self.e_subs+self.e_bullets if f[0:2]==[self.sub_x,self.sub_y]]
        # also check removed (fish moved off)?
        dirn='fromL' if (k and k[0][2]) else ('fromR' if k else 'unk')
        mv=self.action_map[a]
        # was killer already at the sub's new cell before the move (sub moved into it)?
        into=any(f[0:2]==[self.sub_x,self.sub_y] for f in pre_f)
        stats[(self.cause,dirn,mv,'into' if into else 'came', self.sub_y)]+=1
    return r,t
Env.act=act2
G=gp(); R=run(G,400,seed0=2000,tlimit=60); summ('gold',R)
agg=collections.Counter()
for k,v in stats.items(): agg[(k[0],k[1],k[2],k[3])]+=v
for k,v in agg.most_common(30): print(k,v)
rows=collections.Counter()
for k,v in stats.items(): rows[k[4]]+=v
print('death rows',sorted(rows.items()))
