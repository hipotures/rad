"""Observed recurrence/reloads, not exclusive causal victim-loss latency."""
import json,numpy as np,collections,argparse
from pathlib import Path
from inspect_oracle import E
C=Path(__file__).resolve().parents[1]
def analyze(label):
 es=np.fromfile(C/'raw'/label/'raw/oracle-admissions.bin',E);pub=es[es['publish_ns']>0];incoming=collections.Counter((int(x['layer']),int(x['incoming'])) for x in pub);evicted=collections.Counter((int(x['layer']),int(x['victim'])) for x in pub)
 last_eviction={};reloads=collections.Counter()
 for x in np.sort(pub,order='publish_ns'):
  key=int(x['layer']),int(x['incoming']);victim=int(x['layer']),int(x['victim'])
  if key in last_eviction:reloads[key]+=1;del last_eviction[key]
  last_eviction[victim]=int(x['publish_ns'])
 r={'label':label,'published':len(pub),'unique_incoming_experts':len(incoming),'recurring_incoming_experts':sum(n>1 for n in incoming.values()),'repeat_publications_beyond_first':sum(max(0,n-1) for n in incoming.values()),'max_publications_one_expert':max(incoming.values(),default=0),'experts_both_evicted_and_admitted':len(incoming.keys()&evicted.keys()),'chronological_victim_reloads':sum(reloads.values()),'victims_reloaded_repeatedly':sum(n>=2 for n in reloads.values()),'max_reload_count_one_victim':max(reloads.values(),default=0),'definition':'Actual completed publication order; incoming identity previously evicted while absent is a reload. Request-end spare restoration is excluded from admission recurrence and separately charged. These counts are observed work, not exclusive latency.'}
 (C/'analysis'/f'{label}-recurrent-exchanges.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('labels',nargs='+');v=a.parse_args()
 for name in v.labels:print(json.dumps(analyze(name)),flush=True)
