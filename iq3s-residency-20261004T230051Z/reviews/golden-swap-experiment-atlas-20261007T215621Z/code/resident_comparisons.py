"""Compare observed identity sets to a same-source future reference; no policy run."""
import argparse
import statistics
import time
from common import *

def states(root,run):
    p=root/'runs'/run['id'];s=load(p/'summary.json');W=s['windows'];all_states=[]
    for l in range(48):
        d=load(p/f'layer-{l}.json');actions=[]
        for row in d['generations']:
            g=dict(zip(d['columns'],row));a,b=g['publish_event'],g['eviction_event']
            if a is None or b==a:continue
            actions.append((a,1,g['expert']))
            if b is not None:actions.append((b,0,g['expert']))
        actions.sort();i=0;bits=0;values=[]
        for w in range(W):
            end=w*48+47
            while i<len(actions) and actions[i][0]<=end:
                _,admit,e=actions[i];bits=bits|(1<<e) if admit else bits&~(1<<e);i+=1
            assert bits.bit_count()==s['all_layer_series'][l][w][14],(run['id'],l,w,'resident snapshot identity')
            values.append(bits)
        all_states.append(values)
    return all_states

def build(root):
    runs=[r for r in load(REVIEW/'site/data/catalog.json')['runs'] if r.get('summary_url')]
    groups={}
    for r in runs:groups.setdefault((r['campaign'],r['alignment_id']),[]).append(r)
    pairs=[];last=time.monotonic()
    for group in groups.values():
        priorities=['ORACLE_FULL','REPLAY_ORACLE_FULL','LIVE_ORACLE_FULL','FULL_ORACLE','full','FF','future-feasible','future-nextuse']
        reference=next((r for policy in priorities for r in group if r['policy']==policy),None)
        if not reference:continue
        ref=states(root,reference)
        for r in group:
            if r['id']==reference['id']:continue
            a=states(root,r);series=[]
            for w in range(min(r['windows'],reference['windows'])):
                intersection=sum((a[l][w]&ref[l][w]).bit_count() for l in range(48))
                union=sum((a[l][w]|ref[l][w]).bit_count() for l in range(48))
                series.append([intersection,union])
            ratios=[n/d if d else 1 for n,d in series]
            pairs.append(dict(A=r['id'],B=reference['id'],task=r['task'],campaign=r['campaign'],
                policy=r['policy'],reference_policy=reference['policy'],kind=r['kind'],alignment_id=r['alignment_id'],
                columns=['intersection','union'],series=series,mean_jaccard=statistics.mean(ratios),median_jaccard=statistics.median(ratios),
                scope='Whole-model identity sets at verifier-window end; identity similarity is not scheduler optimality or timing gain.'))
            if time.monotonic()-last>25:print('[HEARTBEAT] reference set comparison',len(pairs),'pairs',flush=True);last=time.monotonic()
    save(REVIEW/'results/resident-set-comparisons.json',dict(state='PASS',pairs=pairs,gpu_calls=0,
        validation='Every per-layer bitset count equals the original chronological resident snapshot. Same logical source required.'))
    print('RESIDENT_REFERENCE_COMPARISONS',len(pairs),'pairs',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data-root',type=Path,default=work_root()/'derived/browser-v1');build(p.parse_args().data_root)
