ps=P()
for r in [2,5,8]:
    for dr in [-1,0,1]:
        for c in [0,2,3,4,7,8,9]:
            for k in ['E','B']:
                if 0<r+dr<9:
                    print(f"pr{r} {k} at ({r+dr},{c})", fmt(pol(obs(r,items=[(r+dr,c,k)]),ps)))
print("sandwich", fmt(pol(obs(5,items=[(5,8,'E'),(4,7,'E'),(6,7,'E')]),ps)))
print("diver row5 col8", fmt(pol(obs(5,items=[(5,8,'D')]),ps)))
print("diver row3", fmt(pol(obs(5,items=[(3,8,'D')]),ps)))
print("diver row7", fmt(pol(obs(5,items=[(7,1,'D')]),ps)))
