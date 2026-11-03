import numpy as np
reset()
W1=gold('W1').copy()
def ix(r,c,ch): return (r*10+c)*6+ch
print(W1[ix(9,2,5),24], W1[ix(9,1,5),24], W1[ix(9,8,5),24])
W1[ix(9,2,5),24]=0.0
W1[ix(9,1,5),24]=-6.0
save('W1',W1)
f=net(load)
for oxy in [200,90,61,59,45,41,39,25,21,19,5]:
    print(oxy,[np.round(f(st(5,oxy=oxy,div=d))[0],2).tolist() for d in (0,1,6)])
