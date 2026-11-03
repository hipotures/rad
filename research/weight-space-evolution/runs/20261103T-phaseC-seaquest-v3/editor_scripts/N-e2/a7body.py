ps=P()
for r in [1,3,5,8]:
    for (dr,c,k) in [(-1,4,'E'),(-1,6,'E'),(-1,7,'E'),(-1,8,'E'),(-1,2,'E'),(-1,6,'B'),(0,7,'E'),(0,8,'E'),(0,3,'E'),(1,6,'E')]:
        if 0<=r+dr<9:
            print(f"ASCENT pr{r} {k} at ({r+dr},{c})", fmt(pol(obs(r,oxy=2,div=2,items=[(r+dr,c,k)]),ps)))
for c in [3,4,6,7,8]:
    print(f"row0 E at (1,{c})", fmt(pol(obs(0,items=[(1,c,'E')]),ps)))
