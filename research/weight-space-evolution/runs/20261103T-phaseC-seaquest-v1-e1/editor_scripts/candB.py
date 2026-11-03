def idx(r,c,ch): return (r*10+c)*6+ch
reset()
W1=gold('W1').copy()
W1[idx(9,2,5),24]=0.0
W1[idx(9,1,5),24]=-6.0
save('W1',W1)
G=gold
def P(tag,x):
    a=fwd(x,G)[3];b=fwd(x,load)[3]
    print(f"{tag:30s} gold="+" ".join(f"{v:.2f}" for v in a)+" | new="+" ".join(f"{v:.2f}" for v in b))
for dc in (0,1,6):
  for ox in (200,185,100,61,59,45,39,25,10):
    P(f"y=5 dc={dc} ox={ox}",obs(sub=(5,5),ox=ox,dc=dc))
print(saved())
