def idx(r,c,ch): return (r*10+c)*6+ch
def varC(P=None):
    P=P or gP(); W=P['W1']
    for j in range(16,24):
        r=j-15
        W[idx(r,7,1),j]=5; W[idx(r,7,2),j]=-3; W[idx(r,8,4),j]=4
        W[idx(r,8,1),j]=5; W[idx(r,8,2),j]=-3; W[idx(r,9,4),j]=4
    return P
def varD(P=None):
    P=P or gP(); W=P['W1']; W2=P['W2']; b2=P['b2']
    for row in range(2,9):
        j=25+row-2
        W[:,j]=0
        for c in (2,3,4):
            W[idx(row,c,1),j]=7; W[idx(row,c,2),j]=-3; W[idx(row,c-1,4),j]=4
        for c in (6,7,8):
            W[idx(row,c,1),j]=7; W[idx(row,c,2),j]=-3; W[idx(row,c+1,4),j]=4
        W[idx(row,5,1),j]=10; P['b1'][j]=-5
    b2-=W2[25:32].sum(0); W2[25:32]=0
    for r in range(3,9):  # up from r to r-1>=2
        u=8+r-2; W2[25+(r-1)-2,u]=-3; b2[u]-=3
    for r in range(1,8):  # down from r to r+1>=2
        d=16+r; W2[25+(r+1)-2,d]=-3; b2[d]-=3
    return P
seeds=range(6000,6250)
for name,P in [('gold',gP()),('C',varC()),('D',varD()),('CD',varD(varC()))]:
    res=evalP(P,seeds,tlimit=28); sc=summ(res,name)
    if name=='gold': g=sc
    else:
        n=min(len(g),len(sc)); d=sc[:n]-g[:n]; print('  paired diff',d.mean(),'+-',d.std()/np.sqrt(n))
