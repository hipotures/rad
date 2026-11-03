def scaleRows(P,rows,k):
    W2=P['W2']; old=W2[rows].copy(); W2[rows]=old*k; P['b2']+=(k-1)*old.sum(0); return P
def F2(): return scaleRows(gP(),slice(25,32),2.0)
seeds=range(9000,9400)
for name,P in [('F2',F2()),('F2Dv0.5',scaleRows(F2(),slice(9,16),0.5)),('F2Dv1.5',scaleRows(F2(),slice(9,16),1.5))]:
    res=evalP(P,seeds,tlimit=36); sc=summ(res,name)
    if name=='F2': g=sc
    else:
        n=min(len(g),len(sc)); d=sc[:n]-g[:n]; print('  paired diff vs F2',d.mean(),'+-',d.std()/np.sqrt(n))
