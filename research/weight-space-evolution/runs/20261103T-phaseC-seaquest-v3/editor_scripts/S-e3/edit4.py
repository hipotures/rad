def build4(tw=3.0, c7=None, c8=None, rows=range(1,9), trailcols=(8,9)):
    W1,b1,W2,b2,W3,b3=[gold(n).copy() for n in NM]
    for R in rows:
        u=15+R
        for c in trailcols: W1[idx(R,c,4),u]=tw
        if c7 is not None: W1[idx(R,7,1),u]=c7
        if c8 is not None: W1[idx(R,8,1),u]=c8
    return [W1,b1,W2,b2,W3,b3]
