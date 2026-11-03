reset()
W1=gold("W1").copy()
for k in range(8):
    j=16+k; r=k+1
    for c in [7,8]:
        W1[(r*10+c)*6+2, j]=0.0   # remove reward-channel cancellation on the right (behind the left-facing sub)
save("W1",W1)
ps=P()
for r,ox,dv in [(5,10,0),(5,2,2),(8,10,0),(3,2,2)]:
    for (dr,c,k) in [(0,7,'E'),(0,8,'E'),(0,9,'E'),(-1,7,'E'),(-1,8,'E'),(1,7,'E'),(1,8,'E'),(0,3,'E'),(0,8,'D')]:
        if 0<r+dr<9: print(f"pr{r} ox{ox} {k} at ({r+dr},{c})", fmt(pol(obs(r,oxy=ox,div=dv,items=[(r+dr,c,k)]),ps)))
print("sandwich", fmt(pol(obs(5,items=[(5,8,'E'),(4,7,'E'),(6,7,'E')]),ps)))
print("empty", fmt(pol(obs(5),ps)))
