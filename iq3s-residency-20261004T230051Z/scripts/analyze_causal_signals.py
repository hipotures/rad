"""Finish E007 from retained v2 replay and causal dictionary evaluation."""
import json, pathlib
import numpy as np
from lab import ROOT, load, save
from trace_reader import Trace
from token_history import TokenHistory

exp=ROOT/'experiments/E007-causal-signals'
summary={'state':'COMPLETE_NEGATIVE','scope':'Bounded causal policies at the frozen capacities; not a universal rejection of prediction.', 'profiles':{}, 'repairs':['v1 sensitivity driver stopped on floating cancellation in pending publication; v2 uses exact completion endpoint and has a regression test. Failed and partial v1 records retained.'], 'runtime_disposition':'Neither candidate is promoted to live execution: normalized Markov increases nonlocals; bigram improvement is small, has more transfer bytes and Python state/update costs. E008 separately measures legitimate router availability.'}
for profile,attempt in [('32k','v5'),('128k','v5-portfix')]:
    t=Trace(ROOT/'experiments/E003-diagnostics'/attempt/profile/'traces/runtime-request2')
    validation=t.validate();assert validation['state']=='PASS'
    layers=[[] for _ in t.windows]
    for l,e in t.grouped():layers[t.window_index[int(l['window'])]].append((l,e))
    h=TokenHistory(t,layers);predicted=matched=true_total=nonlocal_total=nonlocal_matched=hit_queries=0
    by_layer={str(l):{'predicted':0,'matched':0,'nonlocal':0,'nonlocal_matched':0} for l in range(t.nl)}
    for i in range(len(t.windows)-1):
        h.observe(i)
        has=bool(h.current.any());hit_queries+=has
        for layer,entries in layers[i+1]:
            l=int(layer['layer']);first=entries[entries['token']==0]
            true=first['expert'];bad=first[first['path']!=0]['expert']
            ids=np.flatnonzero(h.current[l])
            m=int(np.isin(ids,true).sum());bm=int(np.isin(bad,ids).sum())
            predicted+=len(ids);matched+=m;true_total+=len(true);nonlocal_total+=len(bad);nonlocal_matched+=bm
            d=by_layer[str(l)];d['predicted']+=len(ids);d['matched']+=m;d['nonlocal']+=len(bad);d['nonlocal_matched']+=bm
    replay={}
    for name in ['markov-scaled','token-bigram-hybrid']:
        path=exp/'v2'/f'{profile}-rate12p6'/f'{name}.json';r=load(path)
        replay[name]={k:v for k,v in r.items() if k not in ['frames','promotions','per_layer_capacity']}
        replay[name]['raw_path']=str(path)
    summary['profiles'][profile]={'reference_nonlocal':validation['path_counts'][-1]+validation['path_counts'][1]+validation['path_counts'][2], 'replay':replay, 'dictionary_quality':{'predicted_entries':predicted,'correct_predicted_entries':matched,'precision_when_dictionary_hit_pct':100*matched/predicted if predicted else None, 'all_true_next_first_row_entries':true_total,'unconditional_next_row_recall_pct':100*matched/true_total, 'true_nonlocal_next_row_entries':nonlocal_total,'predicted_true_nonlocal_entries':nonlocal_matched,'unconditional_nonlocal_recall_pct':100*nonlocal_matched/nonlocal_total if nonlocal_total else None,'hit_queries':hit_queries,'total_queries':len(t.windows)-1,'per_layer':by_layer,'timing':'Inputs are known output IDs after previous verify. Targets are next actual routed row only for evaluation; no future target is used by the dictionary.'}}
save(exp/'summary.json',summary)
lines=['# Causal Markov and token-history signals','',summary['scope'],'','Status: COMPLETE_NEGATIVE for the declared finite candidates; this does not exhaust the family.','','| Profile | Policy | Nonlocal entries | Promotion GB | Modeled pending wait s | Python selector s |','|---|---|---:|---:|---:|---:|']
for profile,p in summary['profiles'].items():
    for name,r in p['replay'].items():lines.append(f"| {profile} | {name} | {r['nonlocal_entries']} | {r['promotion_bytes']/1e9:.3f} | {r['modeled_pending_wait_s']:.4f} | {r['offline_Python_selector_wall_s']:.3f} |")
    q=p['dictionary_quality'];lines.extend(['',f"{profile}: dictionary conditional top10 precision {q['precision_when_dictionary_hit_pct']:.2f}%, unconditional next-row recall {q['unconditional_next_row_recall_pct']:.2f}%, nonlocal-row recall {q['unconditional_nonlocal_recall_pct']:.2f}%. Dictionary hits {q['hit_queries']}/{q['total_queries']}."])
lines+=['',summary['runtime_disposition'],'','These are fixed-trace simulations. More/less nonlocal work is not converted into TG. Transfer waits use a 12.6 GB/s aggregate optimistic measured-range reference, with the physical per-GPU slot classes and safe completion publication. Python dictionary payload bytes omit container overhead; deployment feature/selector contention is not measured. All rejected draft rows remain in execution demand, but only committed rows teach the dictionary.','',*summary['repairs']]
(exp/'report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({p:x['dictionary_quality']|{'per_layer':'saved'} for p,x in summary['profiles'].items()},indent=2))
