#!/usr/bin/env python3
"""Reconcile the displayed slot and lifecycle evidence without new inference."""
import collections, datetime, json
from pathlib import Path
from common import REVIEW,load,save,digest
from parsers.journals import E,LC,read

def main():
 c=load(REVIEW/'site/data/catalog.json');wanted=['golden-swap-phase2--code-archive-block1-REPLAY_CURRENT','golden-swap-phase2--code-archive-block1-ORACLE_FULL','golden-swap-phase1--code-archive-block1-ORACLE_IN_LEARNED_VICTIM','golden-swap-phase2--code-archive-block1-ORACLE_IN_LOGISTIC_TC'];records=[];manual=[]
 for rid in wanted:
  r=next(x for x in c['runs'] if x['id']==rid);s=load(REVIEW/r['summary_url'].lstrip('/'));pools=collections.defaultdict(list);count=0;byte_count=0;classes={};layer_totals=collections.Counter();identity_first=collections.defaultdict(dict)
  for l in range(48):
   p=REVIEW/r['layer_url'].replace('{layer}',str(l)).lstrip('/');d=load(p);gs=[dict(zip(d['columns'],v)) for v in d['generations']];count+=len(gs);initial={g['expert'] for g in gs if g['generation']==0}
   for g in gs:
    if g['expert'] in initial and g['first_use_event'] is not None:identity_first[l][g['expert']]=min(identity_first[l].get(g['expert'],float('inf')),g['first_use_event'])
   for g in gs:
    assert g['device']==int(l>=(r.get('split') or 24));assert g['byte_class']==s['initial_quality'][l]['byte_class']
    if g['publish_event'] is None:continue
    assert 0<=g['slot']<s['capacity'][g['device']]['slots'];key=(g['device'],g['slot']);classes.setdefault(key,g['byte_class']);assert classes[key]==g['byte_class'],'Physical slot changes byte class'
    pools[key].append(g)
    if g['generation']>0:byte_count+=g['copy_bytes'];layer_totals[l]+=1
   if l==0 and 'ORACLE_IN' in r['policy']:
    prefix=Path(r['raw_dir'])/'raw'/r['journal_prefix'];ad=read(str(prefix)+'-admissions.bin',E);lc=read(str(prefix)+'-lifecycle.bin',LC)
    for g in [x for x in gs if x['expert']==122 and x['generation']>0][:3]:
     a=ad[g['generation']-1];assert int(a['incoming'])==122 and int(a['published_at'])==g['publish_event'];assert int(a['slot'])==g['slot'];assert int(a['uses'])==g['use_count'];assert int(a['target'])==g['target']
     source={k:int(a[k]) for k in ['trigger','target','published_at','incoming','victim','slot','uses','bytes']}
     if len(lc):
      x=lc[g['generation']-1];source['lifecycle']={k:int(x[k]) for k in lc.dtype.names};assert (int(x['first_use']) if x['first_use']>=0 else None)==g['first_use_event']
     if g['eviction_event'] is not None:
      a=next(a for a in ad if int(a['layer'])==0 and int(a['victim'])==122 and int(a['published_at'])==g['eviction_event']);source['replacement']={k:int(a[k]) for k in ['published_at','incoming','victim','slot']}
     manual.append({'run':rid,'generation':g,'source_record':source,'state':'PASS'})
  intervals=0
  for key,gs in pools.items():
   gs.sort(key=lambda g:(g['publish_event'],g['uid']));end=0
   for g in gs:
    assert g['publish_event']>=end,(rid,key,'overlapping physical owners',end,g)
    end=g['eviction_event'] if g['eviction_event'] is not None else r['windows']*48;assert end>=g['publish_event'];intervals+=1
  assert count==s['generations'];assert sum(layer_totals.values())==sum(v[0] for row in s['all_layer_series'] for v in row)
  assert byte_count==sum(v[2] for row in s['all_layer_series'] for v in row)
  assert sum(s[k] for k in ['local','cpu','mapped','unknown_nonlocal'])==s['entries']
  records.append({'run':rid,'state':'PASS','summary_sha256':digest(REVIEW/r['summary_url'].lstrip('/')),'windows':r['windows'],'entries':s['entries'],'generations':count,'physical_slots':len(pools),'published_intervals':intervals,'published_copy_bytes':byte_count,'published_admissions':sum(layer_totals.values()),'main_paths':{k:s[k] for k in ['local','cpu','mapped','unknown_nonlocal']},'top_churn_layer':layer_totals.most_common(1)[0][0],'initial_identity_ever_locally_served':sum(len(v) for v in identity_first.values()),'initial_generation_locally_served':sum(row[-1][s['series_columns'].index('initial_used')] for row in s['all_layer_series'])})
  print('[VISUAL DATA VALIDATION]',rid,'slots',len(pools),'intervals',intervals,flush=True)
 save(REVIEW/'results/visual-audit/data-validation.json',{'state':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runs':records,'expert122_raw_checks':manual,'checks':['Physical ownership has no overlapping intervals','Each device-local slot keeps its physical byte class','Publication/admission totals and bytes match existing summary','All main physical service counts reconcile','Curated expert 122 identity, target, publication, slot, use and replacement match retained raw E/LC journals'],'new_gpu_runs':0})
if __name__=='__main__':main()
