G=[gold(n) for n in NM]
for name,E in (('gold',G),('dk0.5',build5(0.5)),('dk1.5',build5(1.5)),('down-2',build5(db_down=-2)),('down+2',build5(db_down=2)),('fire+3',build5(db_fire=3))):
    res=run(E,200,seed0=60000); summarize(res,name)
