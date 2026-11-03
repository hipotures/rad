def idx(r,c,ch): return (r*10+c)*6+ch
def scaleRows(P,rows,k):
    W2=P['W2']; old=W2[rows].copy(); W2[rows]=old*k; P['b2']+=(k-1)*old.sum(0); return P
def F2(dv):
    P=scaleRows(gP(),slice(25,32),2.0); return scaleRows(P,slice(9,16),dv)
def gate(P):
    for j in range(9,16): P['W1'][idx(9,8,5),j]=-6
    return P
seeds=range(10000,10330)
for name,P in [('F2Dv.5',F2(0.5)),('F2Dv.25',F2(0.25)),('G1',gate(F2(1.0))),('G.5',gate(F2(0.5)))]:
    res=evalP(P,seeds,tlimit=28); sc=summ(res,name)
    if name=='F2Dv.5': g=sc
    else:
        n=min(len(g),len(sc)); d=sc[:n]-g[:n]; print('  paired diff vs F2Dv.5',d.mean(),'+-',d.std()/np.sqrt(n))
