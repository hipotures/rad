def idx(r,c,ch): return (r*10+c)*6+ch
def varA():
    P=gP(); W=P['W1']
    for j in range(16,24):
        r=j-15
        for c in range(10): W[idx(r,c,2),j]=0
    return P
def varB():
    P=gP(); W=P['W1']
    for j in range(16,24):
        r=j-15
        for c in range(10):
            for ch in range(6): W[idx(r,c,ch),j]=0
        for c in (2,3,4):
            W[idx(r,c,1),j]=7; W[idx(r,c,2),j]=-3; W[idx(r,c-1,4),j]=4
        for c in (6,7,8):
            W[idx(r,c,1),j]=7; W[idx(r,c,2),j]=-3; W[idx(r,c+1,4),j]=4
        W[idx(r,5,1),j]=10
        P['b1'][j]=-5
    return P
seeds=range(5000,5250)
for name,P in [('gold',gP()),('A',varA()),('B',varB())]:
    res=evalP(P,seeds,tlimit=35); sc=summ(res,name)
    if name=='gold': g=sc
    else:
        n=min(len(g),len(sc)); d=sc[:n]-g[:n]; print('  paired diff',d.mean(),'+-',d.std()/np.sqrt(n))
