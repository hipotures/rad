import json, numpy as np
for p in [1,2]:
  for nm in ['gold','candidate']:
    eps=json.load(open(f'/work/pass_{p}/{nm}_episodes.json'))
    for e in [x for x in eps if 'trace' in x]:
        t=e['trace']; y=[s['sub_y'] for s in t]; a=[s['a'] for s in t]; dc=[s['diver_count'] for s in t]; ox=[s['oxygen'] for s in t]
        six=[(i,ox[i]) for i in range(1,len(t)) if dc[i]==6 and dc[i-1]!=6]
        # divers lost? pickups
        pick=sum(1 for i in range(1,len(t)) if dc[i]==dc[i-1]+1)
        kills=sum(1 for s in t if s['r']==1)
        print(p,nm,"len",len(t),"kills",kills,"pickups",pick,"reach6 (step,oxy)",six[:6])
        print("    last12 y",y[-12:],"a",a[-12:],"ox",ox[-1],"dc",dc[-1])
