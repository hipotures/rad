import json
n=asc=0
for f in ['/work/pass_1/gold_episodes.json','/work/pass_2/gold_episodes.json','/work/pass_2/candidate_episodes.json']:
    for e in json.load(open(f)):
        if 'trace' not in e: continue
        prev=None
        for t in e['trace']:
            n+=1
            if t['oxygen']<60 and t['diver_count']>0 and not t['surface']: asc+=1
print("steps",n,"ascent-mode steps",asc, asc/n)
reset()
W1=gold("W1").copy()
i2=(9*10+2)*6+5; i1=(9*10+1)*6+5
W1[i1,24]=W1[i2,24]; W1[i2,24]=0.0
save("W1",W1)
ps=P()
for ox in [1,2,3,10]:
    for dv in [0,1,3,6]:
        print("ox",ox,"dv",dv, fmt(pol(obs(5,oxy=ox,div=dv),ps)))
