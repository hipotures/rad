print("empty board, sub col5, varying row/oxygen/divers")
for dc in (0,1,3):
  for ox in (200,100,50):
    for y in range(9):
      pr(f"y={y} ox={ox} dc={dc}",obs(sub=(5,y),ox=ox,dc=dc))
print("diver in row r, sub at row y")
for y in (0,1,3,5,8):
  for r in (2,4,6,8):
    pr(f"sub y={y} diver r{r} c2",obs(sub=(5,y),divers=[(2,r,True)]))
