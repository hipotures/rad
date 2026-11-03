reset()
W1=gold("W1").copy()
i2=(9*10+2)*6+5; i1=(9*10+1)*6+5
W1[i1,24]=W1[i2,24]; W1[i2,24]=0.0
save("W1",W1); print(saved())
