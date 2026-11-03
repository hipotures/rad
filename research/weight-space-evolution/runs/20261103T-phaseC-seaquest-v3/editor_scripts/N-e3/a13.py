import json
eps=json.load(open('/work/pass_1/gold_episodes.json'))
tr=[x for x in eps if 'trace' in x]
t=tr[2]['trace']
print("END:",[(s['sub_y'],s['a'],s['oxygen'],s['diver_count'],int(s['surface'])) for s in t[-25:]])
print("FIRST SURFACING:",[(s['sub_y'],s['a'],s['oxygen'],s['diver_count'],int(s['surface']),s['r']) for s in t[150:175]])
t=tr[0]['trace']
print("SURF2:",[(s['sub_y'],s['a'],s['oxygen'],s['diver_count'],int(s['surface']),s['r']) for s in t[283:300]])
