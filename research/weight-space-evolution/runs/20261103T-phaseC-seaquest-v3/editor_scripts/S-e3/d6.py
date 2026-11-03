G=[gold(n) for n in NM]
for name,E in (('gold',G),('down',build2(up=False)),('up',build2(down=False)),('both',build2())):
    res=run(E,150,seed0=30000); summarize(res,name)
