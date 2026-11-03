import copy
G=gp(); N=1000; S=20000
base=run(G,N,seed0=S,tlimit=14); summ('gold',base)
def conj(P,u,a,b,act,D=100):
    P['W2'][:,u]=0; P['W2'][a,u]=5; P['W2'][b,u]=5; P['b2'][u]=-5
    P['W3'][u,act]=-D/2; P['b3'][act]+=-D/2
def veto(P):
    conj(P,26,0,16,4); conj(P,27,1,17,4)
def ext1(P):  # stay at surface while row2 dangerous
    veto(P); conj(P,28,0,17,4)
def ext2(P):  # don't go up from row2 into danger row1
    veto(P); conj(P,29,2,16,2)
def ext3(P):
    veto(P); conj(P,28,0,17,4); conj(P,29,2,16,2)
def V(f):
    P=copy.deepcopy(G); f(P); return P
for name,f in [('veto01',veto),('veto+surfwait',ext1),('veto+up2',ext2),('veto+both',ext3)]:
    R=run(V(f),N,seed0=S,tlimit=14); summ(name,R); d=R['score']-base['score']; print('  diff %.2f se %.2f'%(d.mean(),d.std()/np.sqrt(len(d))))
