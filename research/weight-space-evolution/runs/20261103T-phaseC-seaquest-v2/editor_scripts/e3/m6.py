def idx(r,c,ch): return (r*10+c)*6+ch
def varE(P=None):
    P=P or gP(); W=P['W1']; W[idx(9,2,5),24]=0; W[idx(9,1,5),24]=-6; return P
def varF(P=None,k=2.0):
    P=P or gP(); W2=P['W2']; old=W2[25:32].copy(); W2[25:32]=old*k; P['b2']+=(k-1)*old.sum(0); return P
seeds=range(7000,7400)
for name,P in [('gold',gP()),('E',varE()),('F',varF()),('EF',varE(varF()))]:
    res=evalP(P,seeds,tlimit=28); sc=summ(res,name)
    if name=='gold': g=sc
    else:
        n=min(len(g),len(sc)); d=sc[:n]-g[:n]; print('  paired diff',d.mean(),'+-',d.std()/np.sqrt(n))
