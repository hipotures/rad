"""Freeze one predeclared horizon using development/calibration only, not held-out labels."""
from lab import ROOT,load,save
base=ROOT/'experiments/E020-wide-gate-lookahead/v1'
if (base/'selection.json').exists():raise RuntimeError('Existing frozen choice')
scores=[]
for horizon in [4,8]:
    rows=[]
    for task in ['dev-code','dev-math','cal-prose']:
        a=load(base/'analysis'/f'{task}.json');assert a['state']=='PASS'
        rows.extend(r for r in a['records'] if r['horizon']==horizon and not r['cold_window'])
    actual=sum(r['true_nonlocal'] for r in rows)
    ready=sum(r['predicted_true_nonlocal'] for r in rows if r['optimistic_ready']['1.8'])
    false=sum(r['false_nonresident_proposals'] for r in rows)
    score={'horizon':horizon,'warm_nonlocal_entries':actual,'warm_optimistic_ready_covered':ready,
           'ready_tail_pct':100*ready/actual if actual else None,
           'false_nonresident_proposals':false,'rows':len(rows)}
    scores.append(score)
# One-blob readiness is only a screen. Queue/slot/victim feasibility is still required.
chosen=max(scores,key=lambda x:(x['ready_tail_pct'] if x['ready_tail_pct'] is not None else -1,-x['false_nonresident_proposals']))
save(base/'selection.json',{'state':'FROZEN_DEVELOPMENT_ONLY','horizon':chosen['horizon'],
    'scores':scores,'filter':'No confidence threshold fitted. Native top10 ordering retained; causal EMA min2/gain1.5 is a separately predeclared feasibility guard.',
    'criterion':'Highest pooled warm ready-tail coverage at contended1.8GB/s, tie fewer false nonresident proposals. Not a speed prediction or a final runtime policy selection.',
    'splits':['dev-code','dev-math','cal-prose'],'heldout_or_benchmark_labels_used':False})
print(chosen)
