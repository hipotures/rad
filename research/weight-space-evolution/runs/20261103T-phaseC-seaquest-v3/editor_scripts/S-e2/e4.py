np.set_printoptions(precision=3,suppress=True)
G=gp()
def probs(P,x):
    L=fwd(P,x[None])[0]; L=L-L.max(); p=np.exp(L); return p/p.sum()
def mk(sy,ens,dc=0,ox=200):
    e=Env(0); e.sub_y=sy; e.e_fish=[[c,r,lr,5] for (c,r,lr) in ens]; e.diver_count=dc; e.oxygen=ox; return e.obs()
print('empty',[ (sy,probs(G,mk(sy,[])).round(2)) for sy in range(0,9)])
for sy in [3,5,7]:
    for dr in [-1,0,1]:
        for c in [3,4,5,6,7,8]:
            lr = c<5
            print(sy,dr,c,'fromL' if lr else 'fromR',probs(G,mk(sy,[(c,sy+dr,lr)])).round(3))
