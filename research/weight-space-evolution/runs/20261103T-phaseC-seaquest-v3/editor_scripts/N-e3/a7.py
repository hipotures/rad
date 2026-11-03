import json, numpy as np
for nm in ['gold','candidate']:
    d=json.load(open(f'/work/pass_1/{nm}_episodes.json'))
    print(nm, type(d), list(d.keys())[:20] if isinstance(d,dict) else len(d))
    eps=d['episodes'] if isinstance(d,dict) and 'episodes' in d else d
    e0=eps[0]; print({k:(v if not isinstance(v,list) else (len(v), v[:3])) for k,v in e0.items()})
    tr=[e for e in eps if 'trace' in e]
    print("n with trace",len(tr))
    for e in tr[:3]:
        t=e['trace']
        print("len",len(t),"first",t[:2],"last",t[-6:])
