import json,numpy as np,collections
E=json.load(open('/work/pass_6/candidate_episodes.json'))
ac=np.array([e['action_counts'] for e in E]).sum(0); print('actions',(ac/ac.sum()).round(3))
for e in E:
    if 'trace' not in e: continue
    t=e['trace']; print('ep',e['score'],len(t),'x dist',sorted(collections.Counter(s['sub_x'] for s in t).items()),'or',collections.Counter(s['sub_or'] for s in t))
    print('  first 40',[(s['a'],s['sub_x'],s['sub_y'],int(s['sub_or'])) for s in t[:40]])
    print('  last 10',[(s['a'],s['sub_x'],s['sub_y'],s['oxygen'],s['diver_count']) for s in t[-10:]])
