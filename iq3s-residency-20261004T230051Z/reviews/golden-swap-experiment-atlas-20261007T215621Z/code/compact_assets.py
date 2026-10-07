"""Losslessly share identical demand across replay arms; round-trip every service row."""
import argparse
import bisect
import collections
import hashlib
import json
import shutil
import time
from common import *

def intervals(layer):
    out=collections.defaultdict(list)
    columns=layer['columns']
    for row in layer['generations']:
        g=dict(zip(columns,row))
        if g['publish_event'] is not None:out[g['expert']].append((g['publish_event'],g['eviction_event'],g['uid']))
    for values in out.values():values.sort(key=lambda x:(x[0],x[2]))
    return {e:([v[0] for v in vs],vs) for e,vs in out.items()}

def expand(base,layer):
    iv=intervals(layer);overrides={r[0]:r[1:] for r in layer['service_exceptions']}
    result=[]
    for i,(event,expert,count) in enumerate(base):
        if i in overrides:result.append([event,expert,*overrides[i]]);continue
        starts,spans=iv.get(expert,([],[]));index=bisect.bisect_right(starts,event)-1
        uid=None
        if index>=0:
            _,end,u=spans[index]
            if end is None or event<end:uid=u
        result.append([event,expert,count if uid is not None else 0,0,0,count if uid is None else 0,uid])
    return result

def compact(source,destination):
    if destination.exists():raise SystemExit('Refuse to overwrite a published derivation namespace')
    destination.mkdir(parents=True);audit=[];seen=set();start=time.monotonic();last=start
    files=sorted(source.glob('runs/*/layer-*.json'))
    for i,path in enumerate(files):
        layer=load(path);original=layer.pop('demand');base=[[v[0],v[1],sum(v[2:6])] for v in original]
        raw=(json.dumps(base,separators=(',',':'))+'\n').encode();sha=hashlib.sha256(raw).hexdigest()
        if sha not in seen:
            save(destination/'demand'/f'{sha}.json',base);seen.add(sha)
        layer.pop('series',None)  # Identical series remains in the run summary, not duplicated per layer.
        layer['service_exceptions']=[]
        defaults=expand(base,layer)
        for j,(a,b) in enumerate(zip(original,defaults)):
            if a!=b:layer['service_exceptions'].append([j,*a[2:]])
        assert expand(base,layer)==original, (path,'lossless service round trip')
        layer['demand_url']=f'/evidence/browser-v1/demand/{sha}.json.gz'
        layer['demand_encoding']='shared exact [event,expert,lane_count] + generation intervals + exact service exceptions; every source row round-trip validated'
        layer['normalized_source_sha256']=digest(path)
        save(destination/path.relative_to(source),layer)
        audit.append({'run':path.parent.name,'layer':layer['layer'],'demand_rows':len(original),
                      'exceptions':len(layer['service_exceptions']),'demand_sha256':sha,'state':'PASS'})
        now=time.monotonic()
        if now-last>=25:
            print(f'[HEARTBEAT] compact {i+1}/{len(files)} layers; {len(seen)} shared demand assets; elapsed {now-start:.0f}s',flush=True);last=now
    for path in sorted(source.rglob('*.json')):
        if path.name.startswith('layer-') and path.parent.parent.name=='runs':continue
        if path.is_relative_to(source/'failures'):continue
        target=destination/path.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    save(REVIEW/'results/compact-validation.json',{'state':'PASS','layers':len(files),'shared_demand_assets':len(seen),
         'exact_service_rows':sum(a['demand_rows'] for a in audit),'exception_rows':sum(a['exceptions'] for a in audit),
         'cpu_wall_s':time.monotonic()-start,'audit':audit})
    print('LOSSLESS_COMPACTION',len(files),'layers',len(seen),'shared demand assets',flush=True)

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);q.add_argument('--source',type=Path,default=work_root()/'derived/browser-v1');q.add_argument('--destination',type=Path,default=work_root()/'derived/browser-compact-v1');a=q.parse_args();compact(a.source,a.destination)
