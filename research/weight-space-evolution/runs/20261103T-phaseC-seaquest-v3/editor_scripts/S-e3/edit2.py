def build2(down=True, up=True, X=60.0, pw=10., dw=5.):
    W1,b1,W2,b2,W3,b3=[gold(n).copy() for n in NM]
    dg=[(0,3,6),(1,4,7),(2,5)]; ug=[(2,5,8),(3,6),(4,7)]
    specs=[]
    if down: specs+=[(26+i,g,+1,4) for i,g in enumerate(dg)]
    if up: specs+=[(29+i,g,-1,2) for i,g in enumerate(ug)]
    for v,g,d,act in specs:
        for R in g:
            W2[R,v]=pw              # h1 player-row unit R (rows 0..8)
            W2[15+(R+d),v]=dw       # h1 danger-row unit for target row (rows 1..8 -> 16..23)
        b2[v]=(pw+dw)*len(g)-2*pw-dw  # off -25, p only -5, p+d +5, d only -15
        W3[v,act]=-X
        b3[act]+=X*np.tanh((-(pw+dw)*len(g))+b2[v])
    return [W1,b1,W2,b2,W3,b3]
