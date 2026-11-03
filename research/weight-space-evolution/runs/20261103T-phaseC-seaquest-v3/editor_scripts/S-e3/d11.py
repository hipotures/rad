G=[gold(n) for n in NM]
base=None
for name,E in (('gold',G),('down-1',build5(db_down=-1)),('down-2',build5(db_down=-2)),('down-4',build5(db_down=-4))):
    res=run(E,600,seed0=70000); sc=summarize(res,name)
    if base is None: base=sc
    else: d=sc-base; print('  diff',round(d.mean(),2),'se',round(d.std()/np.sqrt(len(d)),2))
