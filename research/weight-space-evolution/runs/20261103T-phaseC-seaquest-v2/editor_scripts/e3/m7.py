def idx(r,c,ch): return (r*10+c)*6+ch
def varF(P=None,k=2.0):
    P=P or gP(); W2=P['W2']; old=W2[25:32].copy(); W2[25:32]=old*k; P['b2']+=(k-1)*old.sum(0); return P
def varH(P=None):
    P=P or gP(); W=P['W1']
    for row in range(2,9):
        j=25+row-2
        for c in range(4): W[idx(row,c,1),j]=3; W[idx(row,c,2),j]=3
        P['b1'][j]=-4
    return P
seeds=range(8000,8400)
for name,P in [('gold',gP()),('F2',varF()),('F3',varF(k=3.0)),('F2H',varH(varF()))]:
    res=evalP(P,seeds,tlimit=28); sc=summ(res,name)
    if name=='gold': g=sc
    else:
        n=min(len(g),len(sc)); d=sc[:n]-g[:n]; print('  paired diff',d.mean(),'+-',d.std()/np.sqrt(n))
