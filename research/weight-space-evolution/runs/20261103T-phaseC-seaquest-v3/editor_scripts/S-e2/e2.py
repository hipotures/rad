import copy
def ix(r,c,ch): return (r*10+c)*6+ch
G=gp(); base=run(G,400,seed0=1000,tlimit=20); summ('gold',base)
def variant(f):
    P=copy.deepcopy(G); f(P); return P
def v1(P):
    for j in range(16,24):
        r=j-15
        P['W1'][ix(r,7,2),j]=0; P['W1'][ix(r,8,1),j]=5; P['W1'][ix(r,8,2),j]=0
def v2(P):
    v1(P)
    for j in range(16,24):
        r=j-15; P['W1'][ix(r,9,1),j]=4
def v3(P):  # direction-aware: enemy at col7/8 with trail to its right (moving left)
    for j in range(16,24):
        r=j-15
        P['W1'][ix(r,7,2),j]=0; P['W1'][ix(r,8,1),j]=3; P['W1'][ix(r,8,2),j]=0; P['W1'][ix(r,9,4),j]=2; P['W1'][ix(r,8,4),j]=1
for name,f in [('v1',v1),('v2',v2),('v3',v3)]:
    R=run(variant(f),400,seed0=1000,tlimit=20); summ(name,R); d=R['score']-base['score']; print('  diff %.2f se %.2f'%(d.mean(),d.std()/np.sqrt(len(d))))
