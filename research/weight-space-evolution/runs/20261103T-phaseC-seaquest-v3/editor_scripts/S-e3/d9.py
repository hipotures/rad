G=[gold(n) for n in NM]
for name,E in (('gold',G),('t3',build4(3)),('t5',build4(5)),('t3c7',build4(3,c7=7)),('t3c8',build4(3,c8=5))):
    res=run(E,200,seed0=50000); summarize(res,name)
