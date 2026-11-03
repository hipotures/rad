import json,numpy as np
from collections import Counter
for p in (1,2,3):
  for f in ('gold','candidate'):
    try: E=json.load(open(f'/work/pass_{p}/{f}_episodes.json'))
    except Exception: continue
    for e in E[:3]:
      T=e['trace']; ys=[0]+[t['sub_y'] for t in T]
      # hyp A: a_k produced state k (dy_k = ys[k+1]-ys[k])
      cA=Counter(); cB=Counter()
      for k,t in enumerate(T):
        dy=ys[k+1]-ys[k]; cA[(t['a'],dy)]+=1
        if k+1<len(T): cB[(t['a'],ys[k+2]-ys[k+1])]+=1
      print(p,f,e['seed'],'A',sorted(cA.items()))
      print('        B',sorted(cB.items()))
