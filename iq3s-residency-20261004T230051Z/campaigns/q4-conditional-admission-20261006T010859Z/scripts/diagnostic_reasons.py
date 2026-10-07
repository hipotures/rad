"""Counts/bytes/reason codes from completed traces, without label transfer."""
from campaign import C,load,save
from decompose import rows
from collections import Counter
import csv

data=load(C/'analysis/diagnostic-ablations.json');out=[]
for name,d in data.items():
    events=rows(d['path']+'/events-request2.jsonl')
    counts=Counter(e['classification'] for e in events)
    for reason,n in counts.items():
        out.append({'variant':name,'reason':reason,'count':n,'bytes':n*3072000,
                    'GB':n*.003072,'percent_issued':100*n/len(events),
                    'right_censored':sum(e['classification']==reason and not e['target_reached'] for e in events),
                    'interpretation': 'pending-retired with target_reached=0 is unobserved target/censored, not established prediction failure.' if reason=='pending-retired' else 'Observed explicit issued-action outcome, not a pre-enqueue rejection subtype.'})
save(C/'analysis/diagnostic-failure-reasons.json',out)
with (C/'analysis/diagnostic-failure-reasons.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print('DIAGNOSTIC_REASONS',out,flush=True)
