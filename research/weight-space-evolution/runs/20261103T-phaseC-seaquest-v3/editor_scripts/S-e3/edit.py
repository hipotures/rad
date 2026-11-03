from collections import Counter
NM=['W1','b1','W2','b2','W3','b3']
def idx(r,c,ch): return (r*10+c)*6+ch
def build(down=True, up=True, X=60.0, cells=(4,5,6)):
    W1,b1,W2,b2,W3,b3=[gold(n).copy() for n in NM]
    dgroups=[(0,4),(1,5),(2,6),(3,7)]; ugroups=[(2,5,8),(3,6),(4,7)]
    units=list(range(25,32))
    for u in units:
        W1[:,u]=0; W2[u,:]=0; b1[u]=-10
    specs=[(u,g,+1) for u,g in zip(units[:4],dgroups)]+[(u,g,-1) for u,g in zip(units[4:],ugroups)]
    for u,g,d in specs:
        for R in g:
            W1[idx(R,5,0),u]=8
            T=R+d
            for c in cells: W1[idx(T,c,1),u]=4
    # veto units
    for v,us,act,on in ((26,units[:4],4,down),(27,units[4:],2,up)):
        if not on: continue
        for u in us: W2[u,v]=5
        b2[v]=5*len(us)-3
        W3[v,act]=-X
        b3[act]+= X*np.tanh(-3.0)  # cancel off-state contribution -X*tanh(-3)
    return [W1,b1,W2,b2,W3,b3]
