P=gP()
res=evalP(P,range(1000,1100),tlimit=100)
summ(res,'gold')
r=run_episode(P,1000,trace=True)
tr=r['tr']
print(r['score'],r['len'],r['cause'])
for x in tr[::10][:60]: print(x)
