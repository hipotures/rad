def build3(k=2.0, wide=False):
    W1,b1,W2,b2,W3,b3=[gold(n).copy() for n in NM]
    W2[25:32,:]*=k
    if wide:
        for u in range(25,32):
            R=u-23
            W1[idx(R,4,1),u]=6
    return [W1,b1,W2,b2,W3,b3]
