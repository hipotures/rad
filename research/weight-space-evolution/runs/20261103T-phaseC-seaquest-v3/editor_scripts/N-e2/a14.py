import json,numpy as np
for f in ['gold','candidate']:
    E=json.load(open(f'/work/pass_4/{f}_episodes.json'))
    for e in E:
        if 'trace' not in e: continue
        T=e['trace']; t=T[-1]
        big=sum(x['r'] for x in T if x['r']>1); kills=sum(1 for x in T if x['r']==1)
        print(f, "len",e['length'],"score",e['score'],"kills",kills,"bonus",big,"death y",t['sub_y'],"oxy",t['oxygen'],"div",t['diver_count'])
