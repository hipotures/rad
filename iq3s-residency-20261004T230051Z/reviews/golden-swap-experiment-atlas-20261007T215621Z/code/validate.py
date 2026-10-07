#!/usr/bin/env python3
"""Validate data and exact representative lifecycle links, without replaying inference."""
import argparse
import collections
import gzip
import time
import numpy as np
from common import *
from compact_assets import expand
from parsers.journals import E,LC,L,read

def document(root,rel):
    p=root/rel
    if p.exists():return load(p)
    p=Path(str(p)+'.gz')
    with gzip.open(p,'rt',encoding='utf-8') as f:return json.load(f)

def validate(root):
    c=load(REVIEW/'site/data/catalog.json');tests=[];manual=[];start=time.monotonic();last=start;ng=nd=0
    runs=[r for r in c['runs'] if r.get('summary_url')]
    for ri,r in enumerate(runs):
        s=document(root,Path('runs')/r['id']/'summary.json')
        assert s['validation']['state']=='PASS'
        assert s['windows']==r['windows'] and s['entries']==sum(s[k] for k in ['local','cpu','mapped','unknown_nonlocal'])
        assert sum(p['bytes'] for k,p in s['partition'].items() if k!='incomplete_or_completion_unknown')==s['copy_bytes']
        assert sum(p['transactions'] for p in s['partition'].values())==s['admissions']
        assert sum(v['slots'] for v in s['capacity'])==s['initial_residents']
        generations=entries=0;paths=[0,0,0,0]
        for l in range(48):
            d=document(root,Path('runs')/r['id']/f'layer-{l}.json')
            if 'demand_url' in d:
                sha=Path(d['demand_url']).name[:-len('.json.gz')]
                demand=expand(document(root,Path('demand')/f'{sha}.json'),d)
            else:demand=d['demand']
            gs=[dict(zip(d['columns'],row)) for row in d['generations']];byuid={g['uid']:g for g in gs}
            assert len(byuid)==len(gs)
            use=collections.Counter();calls=collections.Counter();events=collections.defaultdict(list)
            for ev,e,local,cpu,mapped,unknown,uid in demand:
                assert ev%48==l and 0<=e<512 and 0<=ev<s['events']
                for j,v in enumerate([local,cpu,mapped,unknown]):paths[j]+=v
                entries+=local+cpu+mapped+unknown
                if local:
                    assert uid in byuid and byuid[uid]['expert']==e
                    use[uid]+=local;calls[uid]+=1;events[uid].append(ev)
            for g in gs:
                assert g['layer']==l and g['byte_class']==d['byte_class'] and g['device']==d['device']
                assert g['use_count']==use[g['uid']] and g['distinct_use_count']==calls[g['uid']]
                assert g['first_use_event']==(min(events[g['uid']]) if events[g['uid']] else None)
                assert g['last_use_event']==(max(events[g['uid']]) if events[g['uid']] else None)
                if g['first_use_event'] is not None:
                    assert g['publish_event']<=g['first_use_event']<=g['last_use_event']
                    assert g['eviction_event'] is None or g['last_use_event']<=g['eviction_event']
            generations+=len(gs)
            if l==0 and r['campaign'].startswith(('golden-swap-phase1','golden-swap-phase2')) and r['task']=='code-archive' and 'ORACLE_IN' in r['policy']:
                p=Path(r['raw_dir'])/'raw'/r['journal_prefix'];ad=read(str(p)+'-admissions.bin',E);lc=read(str(p)+'-lifecycle.bin',LC)
                selected=[]
                for mode in ['early_unused','used','reload']:
                    sample=next((g for g in gs if g['generation']>0 and g['publish_event'] is not None and
                        (mode=='early_unused' and not g['use_count'] and g['eviction_event'] is not None and g['target'] is not None and g['eviction_event']<g['target'] or
                         mode=='used' and g['use_count']>0 and g['eviction_event'] is not None or
                         mode=='reload' and g['previous_generation'] is not None)),None)
                    if sample is None:continue
                    row=ad[sample['generation']-1]
                    assert int(row['incoming'])==sample['expert'] and int(row['layer'])==l
                    assert int(row['published_at'])==sample['publish_event'] and int(row['uses'])==sample['use_count']
                    source={k:int(row[k]) for k in ['trigger','target','published_at','layer','incoming','victim','slot','bytes','uses']}
                    if len(lc):
                        x=lc[sample['generation']-1];source['LC']={k:int(x[k]) for k in lc.dtype.names}
                        assert (int(x['first_use']) if x['first_use']>=0 else None)==sample['first_use_event']
                    if sample['eviction_event'] is not None:
                        replacement=next(x for x in ad if int(x['victim'])==sample['expert'] and int(x['layer'])==l and int(x['published_at'])==sample['eviction_event'])
                        source['actual_replacement']={k:int(replacement[k]) for k in ['published_at','incoming','victim','slot']}
                    manual.append(dict(run=r['id'],case=mode,generation=sample,source_record=source,state='PASS'))
        assert generations==s['generations'] and entries==s['entries']
        assert paths==[s[k] for k in ['local','cpu','mapped','unknown_nonlocal']]
        tests.append(dict(run=r['id'],state='PASS',generations=generations,entries=entries,source_slot_checks=s['validation']['service_slot_checks']))
        ng+=generations;nd+=entries
        now=time.monotonic()
        if now-last>=25:
            print(f'[HEARTBEAT] validate {ri+1}/{len(runs)} runs; {ng} generations; elapsed {now-start:.0f}s',flush=True);last=now
    assert ng==c['counts']['expert_lifecycles']
    result=dict(state='PASS',runs=len(runs),generations=ng,routed_entries=nd,tests=tests,
                representative_original_lifecycle_checks=manual,elapsed_s=time.monotonic()-start,gpu_calls=0)
    save(REVIEW/'results/data-validation.json',result)
    print('DATA_VALIDATION_PASS',len(runs),'runs',ng,'generations',nd,'routed entries',len(manual),'original lifecycle examples',flush=True)

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);q.add_argument('--data-root',type=Path,default=REVIEW/'evidence/browser-v1');validate(q.parse_args().data_root)
