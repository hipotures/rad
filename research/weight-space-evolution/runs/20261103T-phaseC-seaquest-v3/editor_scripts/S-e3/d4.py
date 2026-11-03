G=[gold(n) for n in NM]
for name,E in (('gold',G),('downonly',build(up=False)),('both',build())):
    res=run(E,200,seed0=20000); summarize(res,name)
