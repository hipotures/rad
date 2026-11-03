import copy
G=gp(); N=500; S=4000
base=run(G,N,seed0=S,tlimit=15); summ('gold',base)
def V(f):
    P=copy.deepcopy(G); f(P); return P
def k1(P): P['b3'][5]+=2
def k2(P): P['b3'][5]+=4
def k3(P): P['b3'][5]+=1
def veto(P,D=100):
    for u,(sr,dr) in zip([26,27],[(0,16),(1,17)]):
        P['W2'][:,u]=0; P['W2'][sr,u]=5; P['W2'][dr,u]=5; P['b2'][u]=-5
        P['W3'][u,4]=-D/2; P['b3'][4]+=-D/2
def k5(P): veto(P); k1(P)
for name,f in [('fire+1',k3),('fire+2',k1),('fire+4',k2),('veto01',veto),('veto+fire2',k5)]:
    R=run(V(f),N,seed0=S,tlimit=15); summ(name,R); d=R['score']-base['score']; print('  diff %.2f se %.2f'%(d.mean(),d.std()/np.sqrt(len(d))))
