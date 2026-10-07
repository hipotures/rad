"""Compact observations derived from selected timelines, not new performance claims."""
import argparse
import collections
import csv
import statistics
from common import *

def quantile(values):
    return {'n':len(values),'min':min(values),'median':statistics.median(values),'max':max(values)} if values else {'n':0,'min':None,'median':None,'max':None}

def build(root):
    c=load(REVIEW/'site/data/catalog.json');rows=[];examples=[]
    for r in c['runs']:
        if not r.get('summary_url'):continue
        p=root/'runs'/r['id'];s=load(p/'summary.json');N=s['initial_residents'];cols=s['series_columns'];series=s['all_layer_series']
        at=lambda col,w:sum(layer[min(w,len(layer)-1)][cols.index(col)] for layer in series)
        quality=lambda h:100*sum(next(x['demanded'] for x in l['quality'] if x['windows']==h) for l in s['initial_quality'])/N
        row={'run':r['id'],'campaign':r['campaign'],'task':r['task'],'policy':r['policy'],'kind':r['kind'],'windows':s['windows'],'initial':N,
            'first1_demanded_pct':quality(1),'first4_demanded_pct':quality(4),'first16_demanded_pct':quality(16),
            'first64_demanded_pct':quality(64),'first256_demanded_pct':quality(256),'full_demanded_pct':quality(s['windows']),
            'initial_survival64_pct':100*at('initial_survivors',63)/N,'initial_survival_end_pct':100*at('initial_survivors',s['windows']-1)/N,
            'publications64':at('admissions',0) if s['windows']==1 else sum(w[0] for ls in series for w in ls[:64]),
            'publications':s['publications'],'evictions':s['evictions'],'copy_GB':s['copy_bytes']/1e9,
            'nonlocal_entries':s['cpu']+s['mapped']+s['unknown_nonlocal'],'local_pct':100*s['local']/s['entries'],
            'no_use_evicted_GB':s['partition'].get('published_evicted_without_use',{}).get('bytes',0)/1e9,
            'no_use_censored_GB':s['partition'].get('published_no_use_resident_at_end',{}).get('bytes',0)/1e9,
            'profile_changed_before_decode':s.get('process_startup',{}).get('replaced_before_decode')}
        rows.append(row)
        if r['campaign'].startswith(('golden-swap-phase1','golden-swap-phase2')) and r['task']=='code-archive' and r['attempt']==1:
            for l in [0,2,30]:
                d=load(p/f'layer-{l}.json');gs=[dict(zip(d['columns'],x)) for x in d['generations']];published=[g for g in gs if g['generation']>0 and g['publish_event'] is not None]
                count=collections.Counter(g['expert'] for g in published);top=sorted(count.items(),key=lambda x:(-x[1],x[0]))[:5]
                life=[((g['eviction_event'] if g['eviction_event'] is not None else s['events'])-g['publish_event'])/48 for g in published]
                wait=[(g['first_use_event']-g['publish_event'])/48 for g in published if g['first_use_event'] is not None]
                gaps=[];demand=collections.defaultdict(list)
                for ev,e,*rest in d['demand']:demand[e].append(ev)
                for times in demand.values():gaps.extend((b-a)/48 for a,b in zip(times,times[1:]))
                examples.append({'run':r['id'],'layer':l,'class':d['byte_class'],'generation_lifetime_windows':quantile(life),
                    'publication_to_first_service_windows':quantile(wait),'distinct_uses':quantile([g['distinct_use_count'] for g in published]),
                    'observed_inter_demand_gap_windows':quantile(gaps),'top_repeat_admissions':top,
                    'censored_generations':sum(g['eviction_event'] is None for g in published),'scope':'Selected layers 0/2/30, block 1 only; lifetime includes finite end censoring.'})
    save(REVIEW/'results/visual-findings.json',{'runs':rows,'selected_layer_examples':examples,'source':'Normalized observed timelines; historical timing remains in the catalog. No new policy simulation.'})
    with (REVIEW/'results/startup-and-churn.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print('VISUAL_OBSERVATIONS',len(rows),'trajectories',len(examples),'selected layer cases',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data-root',type=Path,default=work_root()/'derived/browser-v1');build(p.parse_args().data_root)
