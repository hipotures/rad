reset()
W1=gold("W1").copy()
for c in range(2,9): W1[(1*10+c)*6+2,16]=0.0   # row-1 danger unit: no reward cancellation -> any enemy in row 1 cols 2-8 counts
save("W1",W1); print(saved())
ps=P()
for c in [2,3,4,7,8]: print("row0 E(1,%d)"%c, fmt(pol(obs(0,div=2,items=[(1,c,'E')]),ps)))
print("row0 D(1,3)", fmt(pol(obs(0,div=2,items=[(1,3,'D')]),ps)))
print("row0 empty", fmt(pol(obs(0,div=2),ps)))
print("asc pr2 E(1,3)", fmt(pol(obs(2,oxy=2,div=2,items=[(1,3,'E')]),ps)))
