G=[gold(n) for n in NM]
for name,E in (('gold',G),('k2',build3(2)),('k3',build3(3)),('k0.5',build3(0.5)),('k2wide',build3(2,True))):
    res=run(E,200,seed0=40000); summarize(res,name)
