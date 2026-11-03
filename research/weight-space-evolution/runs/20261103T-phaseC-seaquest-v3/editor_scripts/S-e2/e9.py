import copy
G=gp(); N=700; S=30000
def conj(P,u,a,b,act,D=100):
    P['W2'][:,u]=0; P['W2'][a,u]=5; P['W2'][b,u]=5; P['b2'][u]=-5
    P['W3'][u,act]=-D/2; P['b3'][act]+=-D/2
def veto(P): conj(P,26,0,16,4); conj(P,27,1,17,4)
def ext3(P): veto(P); conj(P,28,0,17,4); conj(P,29,2,16,2)
def V(f):
    P=copy.deepcopy(G); f(P); return P
base=run(V(veto),N,seed0=S,tlimit=8); summ('veto01',base)
for name,f in [('veto+surfwait+up2',ext3)]:
    R=run(V(f),N,seed0=S,tlimit=8); summ(name,R); d=R['score']-base['score']; print('  diff vs veto %.2f se %.2f'%(d.mean(),d.std()/np.sqrt(len(d))),flush=True)
