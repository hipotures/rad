def build5(dk=1.0, db_down=0.0, db_fire=0.0):
    W1,b1,W2,b2,W3,b3=[gold(n).copy() for n in NM]
    blk=W2[16:24,:24]; m=blk<=-2.9; blk[m]*=dk; W2[16:24,:24]=blk
    b3[4]+=db_down; b3[5]+=db_fire
    return [W1,b1,W2,b2,W3,b3]
