"""Observed current-policy admission reuse and unique victim episodes."""
from pathlib import Path
import json, numpy as np
from trace_reader import Trace
C=Path(__file__).resolve().parents[1]
def analyze(t):
    rows=[{'window':int(p['window']),'layer':int(p['layer']),'incoming':int(p['incoming']),
           'outgoing':int(p['outgoing']),'bytes':int(p['bytes']),'issue_ns':int(p['issue']),
           'observed_publication_ns':int(p['observed_ready']),'uses':0,'use_windows':0,
           'first_use_ns':None,'evicted_ns':None,'victim_entries':0} for p in t.promotions]
    byin={};byout={};pi=0
    for layer,es in t.grouped():
        l=int(layer['layer']);now=int(layer['t0'])
        while pi<len(rows) and rows[pi]['issue_ns']<=now:
            r=rows[pi];key=(r['layer'],r['outgoing'])
            old=byin.pop(key,None)
            if old is not None:rows[old]['evicted_ns']=r['issue_ns']
            byin[r['layer'],r['incoming']]=pi;byout[key]=pi;pi+=1
        ids,counts=np.unique(es['expert'],return_counts=True)
        for e,count in zip(ids,counts):
            key=(l,int(e));pid=byin.get(key)
            if pid is not None:
                r=rows[pid]
                if r['observed_publication_ns'] and r['observed_publication_ns']<=now:
                    r['uses']+=int(count);r['use_windows']+=1
                    if r['first_use_ns'] is None:r['first_use_ns']=now
            pid=byout.get(key)
            if pid is not None and np.any((es['expert']==e)&(es['path']!=0)):rows[pid]['victim_entries']+=int(count)
    counts=t.counts();caps=(t.initial>=0).sum(axis=1)
    sets={}
    for horizon in [4,16,64]:
        sets[str(horizon)]=[int((counts[i:i+horizon].sum(axis=0)>0).sum()) for i in range(0,len(counts),horizon)]
    used=[r for r in rows if r['uses']]
    return {'trace':t.prefix,'promotions':len(rows),'bytes':sum(r['bytes'] for r in rows),
            'useful_promotions':len(used),'unused_promotions':len(rows)-len(used),
            'used_bytes':sum(r['bytes'] for r in used),'unused_bytes':sum(r['bytes'] for r in rows if not r['uses']),
            'repeated_use_windows':sum(r['use_windows']>1 for r in rows),
            'victim_entries_while_absent':sum(r['victim_entries'] for r in rows),
            'incoming_uses':sum(r['uses'] for r in rows),
            'copy_issue_to_observed_publication_ms':{'median':float(np.median([(r['observed_publication_ns']-r['issue_ns'])/1e6 for r in rows if r['observed_publication_ns']]))},
            'unique_experts_entire_episode_per_layer':(counts.sum(axis=0)>0).sum(axis=1).tolist(),
            'per_layer_capacity':caps.tolist(),'window_block_working_set':sets,'rows':rows,
            'limitations':['Victim demand is observed absence attributed to its latest eviction, not a counterfactual latency',
                           'Near-end unused promotions are right-censored, not established wasted predictions',
                           'Observed publication is a host upper endpoint, not exact copy completion']}
def main():
    for results in sorted((C/'traces/diagnostic').glob('*/*/results.json')):
        prefix=json.loads(results.read_text())['trace_prefix'];out=results.parent/'observed-admissions.json'
        if out.exists():continue
        r=analyze(Trace(prefix));out.write_text(json.dumps(r,indent=2)+'\n')
        print('ADMISSIONS',results.parent.name,r['useful_promotions'],r['unused_promotions'],r['victim_entries_while_absent'],flush=True)
if __name__=='__main__':main()
