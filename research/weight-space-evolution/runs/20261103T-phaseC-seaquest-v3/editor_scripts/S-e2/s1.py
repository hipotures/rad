import numpy as np
W2=gold('W2').copy(); b2=gold('b2').copy(); W3=gold('W3').copy(); b3=gold('b3').copy()
def conj(u,a,b,act,D=100):
    W2[:,u]=0; W2[a,u]=5; W2[b,u]=5; b2[u]=-5; W3[u,act]=-D/2; b3[act]+=-D/2
conj(26,0,16,4); conj(27,1,17,4)
reset(); save('W2',W2); save('b2',b2); save('W3',W3); save('b3',b3); print(saved())
