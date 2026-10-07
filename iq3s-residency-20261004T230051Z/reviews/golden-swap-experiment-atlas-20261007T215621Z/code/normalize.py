"""Generation/slot reconstruction. Host timestamps order actions within one run only."""
import bisect
import collections
import re
import numpy as np
from common import *
from parsers.journals import *

GEN_COLUMNS = ['uid','generation','layer','expert','device','byte_class','slot','trigger','target','issue_event',
               'publish_event','first_use_event','last_use_event','eviction_event','release_event','expiry_event',
               'use_count','distinct_use_count','victim','victim_layer','status','copy_bytes','copy_us','previous_generation']
DEMAND_COLUMNS = ['event','expert','local','cpu','mapped','unknown_nonlocal','resident_uid']
SERIES_COLUMNS = ['admissions','evictions','copy_bytes','local','cpu','mapped','unknown_nonlocal','repeat_admissions',
                  'late_publications','initial_survivors','initial_members_resident','initial_used','initial_demanded',
                  'protected','resident_count','jaccard_initial']

def profile_pairs(path):
    import struct
    b=Path(path).read_bytes()
    assert b[:4]==b'STRP'
    version,nl,ne,want,n=struct.unpack_from('<5I',b,4)
    assert (nl,ne)==(48,512)
    return [struct.unpack_from('<HH',b,24+4*i) for i in range(n)]

def materials(run, q4_blobs):
    """Return initial state, exact observed service batches and chronological ownership actions."""
    refs=[];actions=[];entries=[];tape=None;expected=None;life={}
    if 'raw_dir' in run:
        p=Path(run['raw_dir']);prefix=p/'raw'/run['journal_prefix'];tape=Tape(run['tape_path'])
        initial=tape.initial.copy();blobs=q4_blobs.copy()
        a=read(str(prefix)+'-layers.bin',L);e=read(str(prefix)+'-admissions.bin',E);n=read(str(prefix)+'-native.bin',N)
        lc=read(str(prefix)+'-lifecycle.bin',LC)
        assert len(a)==len(tape.ws)*48 and np.array_equal(a['event'],np.arange(len(a)))
        assert np.all(a['plan_end'][1:]>=a['plan_end'][:-1])
        clock=a['plan_end'];end_event=len(a)
        for row in a:
            ev=int(row['event']);l=int(row['layer']);nn=int(row['n']);ids=row['ids'][:nn]
            assert l==ev%48 and np.array_equal(ids,tape.ws[ev//48]['routes']['ids'][l,:nn])
            entries.append((ev,l,ids.copy(),row['slots'][:nn].copy(),row['path'][:nn].copy()))
        log=p/'raw/run-engine.log'
        if not log.exists():log=p/'logs/engine.log'
        txt=log.read_text()
        reserves=[list(map(int,x)) for x in re.findall(r'Q4_ORACLE_RESERVE device=(\d+) class=(\d+) bytes=(\d+) slot=(\d+) layer=(\d+) expert=(\d+)',txt)]
        for d,c,b,s,l,x in reserves:actions.append((0,0,{'kind':'reserve','event':0,'layer':l,'expert':x,'slot':s}))
        copies=[]
        for i,x in enumerate(e):
            row={'generation':i+1,'layer':int(x['layer']),'expert':int(x['incoming']),'slot':int(x['slot']),
                 'trigger':int(x['trigger']),'target':int(x['target']),'issue_event':int(x['trigger']),
                 'publish_event':int(x['published_at']) if x['publish_ns'] else None,
                 'victim':int(x['victim']) if int(x['victim'])>=0 else None,'victim_layer':int(x['layer']),
                 'status':'published' if x['publish_ns'] else 'completed_unpublished' if x['copy_end'] else 'incomplete',
                 'copy_bytes':int(x['bytes']),'copy_us':float((int(x['copy_end'])-int(x['copy_begin']))/1000) if x['copy_end'] else None,
                 'completed':bool(x['copy_end']),'source_uses':int(x['uses']),'source_index':i,'authority':'oracle'}
            if len(lc):
                assert len(lc)==len(e)
                row.update(release_event=int(lc[i]['released_at']) if lc[i]['released_at']>=0 else None,
                           expiry_event=int(lc[i]['expiry']) if lc[i]['expiry']>=0 else None)
                life[i]=lc[i]
            copies.append(row)
            if x['publish_ns']:
                actions.append((int(x['publish_ns']),2,{'kind':'exchange','copy_index':len(copies)-1,'event':int(x['published_at'])}))
        for i,x in enumerate(n):
            pub=int(np.searchsorted(clock,x['publish_ns'])) if x['publish_ns'] else None
            issue=int(np.searchsorted(clock,x['issue_ns']))
            row={'generation':i+1,'layer':int(x['layer']),'expert':int(x['incoming']),'slot':int(x['slot']),
                 'trigger':None,'target':None,'issue_event':issue,'publish_event':pub,'victim':int(x['victim']),
                 'victim_layer':int(x['layer']),'status':'published' if pub is not None else 'completion_unknown',
                 'copy_bytes':int(x['bytes']),'copy_us':None,'completed':pub is not None,
                 'source_index':i,'authority':'native'}
            copies.append(row);ci=len(copies)-1
            actions.append((int(x['issue_ns']),1,{'kind':'withdraw','copy_index':ci,'event':issue}))
            if pub is not None:actions.append((int(x['publish_ns']),2,{'kind':'publish','copy_index':ci,'event':pub}))
        refs += [Path(run['tape_path']), log, p/'config.json',Path(str(prefix)+'-layers.bin'),
                 Path(str(prefix)+'-admissions.bin'),Path(str(prefix)+'-native.bin')]
        if len(lc):refs.append(Path(str(prefix)+'-lifecycle.bin'))
        times=[int(x) for x in clock]
        return initial,blobs,entries,actions,copies,len(tape.ws),refs,times,life,tape,None
    t=NativeTrace(run['trace_prefix']);initial=t.initial.copy();blobs=t.blobs.copy();W=len(t.windows)
    simulation=load(run['simulation_path']) if run.get('simulation_path') else None
    for i,row in enumerate(t.layers):
        l=int(row['layer']);wi=t.index[int(row['window'])];ev=wi*48+l;at=int(row['offset']);nn=int(row['tokens'])*int(row['k'])
        es=t.entries[at:at+nn]
        entries.append((ev,l,es['expert'].astype(int),es['slot'].copy(),es['path'].copy()))
    assert [x[0] for x in entries]==list(range(W*48)), 'Main trace invocation coverage'
    copies=[]
    if simulation:
        rows=simulation.get('rows',simulation.get('promotions',[]))
        for i,x in enumerate(rows):
            # Modeled publication at next-window join; capacity-free is same-window instantaneous.
            issue=int(x['window'])*48+48
            publish=x.get('published_ns',x.get('published'))
            evict_w=x.get('evicted_window')
            pub_ev=(int(x['window'])*48 if run['policy']=='future-capacity-free' else issue) if publish is not None else None
            row={'generation':i+1,'layer':int(x['layer']),'expert':int(x['incoming']),'slot':int(x['slot']),
                 'trigger':None,'target':None,'issue_event':min(issue,W*48),'publish_event':min(pub_ev,W*48) if pub_ev is not None else None,
                 'victim':int(x['outgoing']),'victim_layer':int(x.get('outgoing_layer',x['layer'])),
                 'status':'published' if publish is not None else 'completed_unpublished',
                 'copy_bytes':int(x['bytes']),'copy_us':None,'completed':publish is not None,'source_index':i,'authority':'simulation'}
            if run['policy']=='future-capacity-free':row['issue_event']=pub_ev
            copies.append(row)
            actions.append((row['issue_event'],1,{'kind':'withdraw','copy_index':i,'event':row['issue_event']}))
            if pub_ev is not None:actions.append((row['publish_event'],2,{'kind':'publish','copy_index':i,'event':row['publish_event']}))
        # Group by logical window rather than a recorded wall clock; physical paths for new policy are unknown.
        times=list(range(W*48));expected=simulation.get('nonlocal_entries')
        refs.append(Path(run['simulation_path']))
    else:
        clock=np.array([int(x['t0']) for x in t.layers],dtype=np.uint64);times=[int(x) for x in clock]
        for i,x in enumerate(t.promotions):
            issue=int(np.searchsorted(clock,x['issue']));pub=int(np.searchsorted(clock,x['observed_ready'])) if x['observed_ready'] else None
            row={'generation':i+1,'layer':int(x['layer']),'expert':int(x['incoming']),'slot':int(x['slot']),
                 'trigger':None,'target':None,'issue_event':issue,'publish_event':pub,'victim':int(x['outgoing']),
                 'victim_layer':int(x['outgoing_layer']) if 'outgoing_layer' in x.dtype.names else int(x['layer']),
                 'status':'published' if pub is not None else 'completion_unknown','copy_bytes':int(x['bytes']),
                 'copy_us':None,'completed':pub is not None,'source_index':i,'authority':'native'}
            copies.append(row);actions.append((int(x['issue']),1,{'kind':'withdraw','copy_index':i,'event':issue}))
            if pub is not None:actions.append((int(x['observed_ready']),2,{'kind':'publish','copy_index':i,'event':pub}))
    refs += sorted(Path(run['trace_prefix']).parent.glob(Path(run['trace_prefix']).name+'-*.bin'))
    return initial,blobs,entries,actions,copies,W,refs,times,{},None,expected

def derive(run,q4_blobs):
    import time
    heartbeat=time.monotonic()
    initial,blobs,entries,actions,copies,W,refs,times,life,tape,expected=materials(run,q4_blobs)
    split=run.get('split',24);last_event=W*48;gens=[];live={};last_generation={};demand=[[] for _ in range(48)]
    paths=np.zeros((48,W,4),np.int64);all_demands=collections.defaultdict(list)
    event_changes=np.zeros((48,W,9),np.int64)
    def gen(layer,expert,slot,generation=0,**kw):
        key=(layer,expert);uid=len(gens);row={k:None for k in GEN_COLUMNS}
        row.update(uid=uid,generation=generation,layer=layer,expert=expert,device=int(layer>=split),byte_class=int(blobs[layer]),
                   slot=slot,publish_event=0 if generation==0 else None,status='initial' if generation==0 else 'pending',
                   use_count=0,distinct_use_count=0,copy_bytes=0,previous_generation=last_generation.get(key))
        row.update({k:v for k,v in kw.items() if k in row});gens.append(row);last_generation[key]=uid;return uid
    for l,e in np.argwhere(initial>=0):
        uid=gen(int(l),int(e),int(initial[l,e]));live[int(l),int(e)]=uid
    initial_count=len(gens);startup=set(live);initial_uids=dict(live)
    startup_by_layer=[{k for k in startup if k[0]==l} for l in range(48)]
    live_by_layer=[{k for k in live if k[0]==l} for l in range(48)]
    for x in copies:x['uid']=gen(x['layer'],x['expert'],x['slot'],**{k:v for k,v in x.items() if k in GEN_COLUMNS and k not in ['layer','expert','slot']})
    initial_use=set();initial_demand=set();ever_replaced=set();slot_checks=0;errors=[];key_demands=collections.defaultdict(list)
    survivors=np.zeros((48,W),np.int64);members=survivors.copy();initused=survivors.copy();initdem=survivors.copy();residents=survivors.copy();protected=survivors.copy();jaccard=np.zeros((48,W),float)
    def count_at(l,ev,col,amount=1):
        if ev<last_event:event_changes[l,max(0,ev)//48,col]+=amount
    def withdraw(l,e,at,reserve=False):
        uid=live.pop((l,e),None)
        if uid is None:
            errors.append(f'withdrawal of absent expert L{l}/E{e} at {at}');return
        g=gens[uid];g['eviction_event']=at
        live_by_layer[l].discard((l,e))
        if reserve:g['status']='initial_spare_donor'
        if g['generation']==0:ever_replaced.add((l,e))
        if not reserve:count_at(l,at,1)
    def apply(action):
        nonlocal slot_checks
        k=action['kind'];at=action['event']
        if k=='reserve':withdraw(action['layer'],action['expert'],at,True);return
        x=copies[action['copy_index']];l=x['layer'];e=x['expert'];g=gens[x['uid']]
        if k in ['exchange','withdraw']:
            if x['victim'] is not None:withdraw(x['victim_layer'],x['victim'],at)
        if k in ['exchange','publish']:
            if (l,e) in live:errors.append(f'duplicate resident L{l}/E{e} at {at}')
            live[l,e]=x['uid'];count_at(l,at,0);count_at(l,at,2,x['copy_bytes'])
            live_by_layer[l].add((l,e))
            if g['previous_generation'] is not None:count_at(l,at,7)
            if g['target'] is not None and at>g['target']:count_at(l,at,8)
    actions.sort(key=lambda a:(a[0],a[1]));ai=0
    for ev,l,ids,slots,pa in entries:
        if time.monotonic()-heartbeat>25:
            print('[HEARTBEAT] derive',run['label'],'event',ev,'/',last_event,flush=True)
            heartbeat=time.monotonic()
        while ai<len(actions) and actions[ai][0]<=times[ev]:apply(actions[ai][2]);ai+=1
        counts=collections.defaultdict(lambda:[0,0,0,0,None])
        for e,slot,path in zip(ids,slots,pa):
            e=int(e);slot=int(slot);path=int(path);key=(l,e);uid=live.get(key)
            if run['kind']=='SIMULATION':
                cat=0 if uid is not None else 3
            else:
                cat=0 if slot>=0 else 1 if path==-1 else 2 if path==1 else 3
                modeled_slot=gens[uid]['slot'] if uid is not None else -1
                if modeled_slot!=slot:errors.append(f'service slot mismatch at {ev}/{e}: {modeled_slot} != {slot}')
                slot_checks+=1
            counts[e][cat]+=1
            if cat==0:counts[e][4]=uid
        for e,c in counts.items():
            n=sum(c[:4]);uid=c[4];demand[l].append([ev,e,*c[:4],uid])
            all_demands[l,e].append((ev,n));key_demands[l,e].append(ev)
            paths[l,ev//48]+=np.array(c[:4],np.int64)
            if (l,e) in startup:initial_demand.add((l,e))
            if uid is not None:
                g=gens[uid];g['use_count']+=c[0];g['distinct_use_count']+=1;g['last_use_event']=ev
                if g['first_use_event'] is None:g['first_use_event']=ev
                if g['generation']==0:initial_use.add((l,e))
        if l==47:
            wi=ev//48
            for ll in range(48):
                s=startup_by_layer[ll];r=live_by_layer[ll]
                survivors[ll,wi]=sum(live.get(k)==initial_uids[k] for k in s)
                members[ll,wi]=len(s&r);initused[ll,wi]=len(s&initial_use);initdem[ll,wi]=len(s&initial_demand);residents[ll,wi]=len(r)
                jaccard[ll,wi]=len(s&r)/len(s|r) if s|r else 1
                protected[ll,wi]=sum(gens[u]['generation']>0 and gens[u]['release_event'] is not None and
                    gens[live[k]]['publish_event']<=ev<gens[live[k]]['release_event'] for k in r
                    for u in [live[k]])
    # Complete host ownership chronology through final drain, without inventing subsequent service.
    while ai<len(actions):apply(actions[ai][2]);ai+=1
    for x in copies:
        g=gens[x['uid']]
        if 'source_uses' in x and g['use_count']!=x['source_uses']:
            errors.append(f'oracle generation {x["source_index"]} service count differs')
        if x['authority']=='oracle' and x['source_index'] in life:
            lc=life[x['source_index']]
            for field,k in [('first_use_event','first_use'),('last_use_event','last_use'),('eviction_event','evicted_at')]:
                observed=int(lc[k]) if lc[k]>=0 else None
                if g[field]!=observed:errors.append(f'lifecycle {field} mismatch at {x["source_index"]}')
            if g['distinct_use_count']!=int(lc['distinct_uses']):errors.append('distinct service count mismatch')
    if expected is not None and int(paths[:,:,1:].sum())!=expected:errors.append('retained modeled nonlocal count mismatch')
    horizons=[1,4,16,64,256,W];initial_metrics=[];layer_data=[]
    for l in range(48):
        lg=[g for g in gens if g['layer']==l];init=[g for g in lg if g['generation']==0]
        quality=[]
        for h in horizons:
            quality.append({'windows':h,'demanded':sum(bool(key_demands[l,g['expert']]) and key_demands[l,g['expert']][0]<h*48 for g in init),
                            'served_before_eviction':sum(g['first_use_event'] is not None and g['first_use_event']<h*48 for g in init),'total':len(init)})
        worst=[]
        for g in init:
            d=all_demands[l,g['expert']];evict=g['eviction_event'];evs=[x[0] for x in d]
            worst.append([g['expert'],g['slot'],g['byte_class'],d[0][0] if d else None,g['first_use_event'],evict,
                          sum(n for ev,n in d if evict is not None and ev>=evict),sum(1 for x in lg if x['expert']==g['expert'] and x['generation']>0),
                          sum(n for ev,n in d)])
        initial_metrics.append({'layer':l,'device':int(l>=split),'byte_class':int(blobs[l]),'residents':len(init),'quality':quality})
        series=np.column_stack([event_changes[l,:,0:3],paths[l],event_changes[l,:,7:9],survivors[l],members[l],initused[l],initdem[l],protected[l],residents[l],jaccard[l]])
        # Retrospective full-tape frequency reference: fixed per-layer count, no performance claim.
        freq=collections.Counter({e:sum(n for _,n in ds) for (ll,e),ds in all_demands.items() if ll==l})
        ideal=sorted(range(512),key=lambda e:(-freq[e],e))[:len(init)]
        layer_data.append({'layer':l,'device':int(l>=split),'byte_class':int(blobs[l]),'columns':GEN_COLUMNS,
            'generations':[[g[k] for k in GEN_COLUMNS] for g in lg],'demand_columns':DEMAND_COLUMNS,'demand':demand[l],
            'series_columns':SERIES_COLUMNS,'series':series.tolist(),'startup_quality':quality,
            'startup_table_columns':['expert','slot','byte_class','first_demand','first_local_service','eviction','demand_entries_after_eviction','reloads','total_demand_entries'],
            'startup_table':worst,'future_frequency_reference':ideal})
    totals=paths.sum(axis=(0,1));published=[g for g in gens if g['generation']>0 and g['publish_event'] is not None]
    outcome=collections.defaultdict(lambda:{'transactions':0,'bytes':0})
    for x in copies:
        g=gens[x['uid']]
        if not x['completed']:name='incomplete_or_completion_unknown'
        elif g['publish_event'] is None:name='completed_unpublished'
        elif g['use_count']>0:name='published_used_before_eviction'
        elif g['eviction_event'] is not None:name='published_evicted_without_use'
        else:name='published_no_use_resident_at_end'
        outcome[name]['transactions']+=1;outcome[name]['bytes']+=g['copy_bytes']
    completed_bytes=sum(x['copy_bytes'] for x in copies if x['completed'])
    early=sum(g['copy_bytes'] for g in published if not g['use_count'] and g['eviction_event'] is not None and g['target'] is not None and g['eviction_event']<g['target'])
    bydev=[]
    for d in range(2):
        ls=range(0,split) if d==0 else range(split,48)
        slots=initial[list(ls)];class_counts=collections.Counter(int(blobs[l]) for l in ls for e in np.flatnonzero(initial[l]>=0))
        bydev.append({'device':d,'slots':int((slots>=0).sum()),'classes':dict(class_counts)})
    provenance=[reference(p) for p in sorted(set(refs)) if p.exists()]
    summary={'id':run['id'],'windows':W,'events':last_event,'entries':int(totals.sum()),'local':int(totals[0]),'cpu':int(totals[1]),
        'mapped':int(totals[2]),'unknown_nonlocal':int(totals[3]),'initial_residents':initial_count,'capacity':bydev,
        'admissions':len(copies),'publications':len(published),'evictions':sum(g['eviction_event'] is not None and g['status']!='initial_spare_donor' for g in gens),
        'copy_bytes':completed_bytes,'issued_bytes':sum(x['copy_bytes'] for x in copies),'partition':dict(outcome),
        'generations':len(gens),'evicted_before_intended_first_target_bytes':early,'spare_donors':sum(g['status']=='initial_spare_donor' for g in gens),
        'initial_quality':initial_metrics,'provenance':provenance,'generation_columns':GEN_COLUMNS,'series_columns':SERIES_COLUMNS,
        'native_boundary':'Issue withdraws victim; publication installs incoming. Native logical positions are first observed main service boundary at/after host milestone.',
        'observation_end':last_event,'restoration':'Mandatory restoration is outside routed-service observation; restoration residents not fabricated.',
        'unknowns':['MTP per-expert service paths','per-decision rejected-candidate timeline','DMA-only copy cost','exclusive saved CPU latency'],
        'validation':{'state':'PASS' if not errors else 'FAIL','service_slot_checks':slot_checks,'errors':sorted(set(errors))[:30]},
        'all_layer_series':np.stack([np.asarray(x['series'],float) for x in layer_data]).tolist()}
    if tape is not None:
        run.update(input=int(tape.h['prompt_count']),output=int(tape.h['output_count']))
    return summary,layer_data
