import copy
G=gp(); N=1500; S=10000
base=run(G,N,seed0=S,tlimit=20); summ('gold',base)
def V(*fs):
    P=copy.deepcopy(G)
    for f in fs: f(P)
    return P
def fire2(P): P['b3'][5]+=2
def veto(P,D=100):
    for u,(sr,dr) in zip([26,27],[(0,16),(1,17)]):
        P['W2'][:,u]=0; P['W2'][sr,u]=5; P['W2'][dr,u]=5; P['b2'][u]=-5
        P['W3'][u,4]=-D/2; P['b3'][4]+=-D/2
def look2(P):
    W=P['W2']
    for k in list(range(8,24)):
        for i in range(16,24):
            if abs(W[i,k]+0.3)<1e-6: W[i,k]=-3
print('changed look2 entries',int((V(look2)['W2']!=G['W2']).sum()))
for name,fs in [('veto01',(veto,)),('look2',(look2,)),('look2+veto',(look2,veto)),('look2+veto+fire2',(look2,veto,fire2))]:
    R=run(V(*fs),N,seed0=S,tlimit=20); summ(name,R); d=R['score']-base['score']; print('  diff %.2f se %.2f'%(d.mean(),d.std()/np.sqrt(len(d))))
