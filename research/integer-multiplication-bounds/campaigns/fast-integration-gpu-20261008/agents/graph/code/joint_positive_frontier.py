#!/usr/bin/env python3
"""Selective signed address enlargements on fixed literal joint words.

All original roles/XORs remain literal. Select a rank suffix, terminal
common subset, or core family; close forward only when needed for an actual
physical address inclusion. Complete signed assignment duplicates are
skipped before dirty replay. The maximal signed closure itself is computed
from ALL physical word transitions, not DAG or matching proxies.
"""
import argparse
from collections import deque
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sqlite3,sys,time
from joint_word_positive_closure import extend
from joint_word_check_v4 import check
from check_compiled_witness import contained
WORK=None
CACHE={}


def initialize(work):
    global WORK
    WORK=Path(work)


def parent(document):
    key=document['id']
    if key in CACHE:return CACHE[key]
    payload=Path(document['word_path']).read_bytes();raw=gzip.decompress(payload);word=json.loads(raw);h=word['h'];original_digest=sha256(raw).hexdigest();assert original_digest==document['word_sha256']
    Q=document.get('Q',list(range(h)))
    if Q!=list(range(h)):
        def mask(z):return sum(1<<Q[i]for i in range(h)if z>>i&1)
        word['frames']=[(mask(c),mask(m))for c,m in word['frames']];word['outputs']=[(s,g,Q[c],tuple(sorted(Q[j]for j in t)))for s,g,c,t in word['outputs']]
        triples=list(combinations(range(h),3));indices={t:i for i,t in enumerate(triples)};labels=[indices[tuple(sorted(Q[j]for j in t))]for t in triples];inverse=[0]*len(labels)
        for i,j in enumerate(labels):inverse[j]=i
        word.update(source_permutation=Q,source_label_permutation=labels,source_label_inverse=inverse)
    original=[tuple(f)for f in word['frames']];maximal,receipt=extend(word);signed=[maximal['frames'][j]for j in maximal['physical_region_address_aliases']];ranks=[1 if c==m else m.bit_count()-c.bit_count()for c,m in original];ordinary=[]
    for r,(c,m)in zip(ranks,original):ordinary.append((r,c,tuple(int(c>>j&1)for j in range(h)))if c==m else(r,c,tuple(1 if c>>j&1 else j+2 if m>>j&1 else 0 for j in range(h))))
    successors=[set()for _ in original]
    for slot,old,new in word['events']:
        if old>=0 and old!=new:successors[old].add(new)
    terminals={g for s,g,c,t in word['outputs']if len(t)==3}
    CACHE[key]=(word,ordinary,signed,ranks,successors,terminals,receipt)
    return CACHE[key]


def evaluate(config):
    at=time.monotonic();doc=config['parent'];word,ordinary,signed,ranks,successors,terminals,receipt=parent(doc);h=word['h'];n=len(ordinary);mode=config['mode'];value=config['value'];case=f"{doc['id']}-{mode}-{value}";target=WORK/'raw'/case;target.mkdir(parents=True,exist_ok=False)
    if mode=='rank-suffix':selected={g for g in range(n)if ranks[g]>=value}
    elif mode=='core-single':selected={g for g in range(n)if ranks[g]>=value and ordinary[g][1].bit_count()==1}
    elif mode=='core-pair':selected={g for g in range(n)if ranks[g]>=value and ordinary[g][1].bit_count()==2}
    else:
        commons=set(range(min(h,abs(value))))if value>0 else set(range(max(0,h-abs(value)),h))
        selected={g for g in terminals if(ordinary[g][1]&-ordinary[g][1]).bit_length()-1 in commons}
    changed={g for g in selected if signed[g]!=ordinary[g]};queue=deque(sorted(changed));closure=0
    while queue:
        old=queue.popleft()
        for new in successors[old]:
            if new in changed:continue
            if not contained(signed[old],ordinary[new]):changed.add(new);queue.append(new);closure+=1
    chosen=[signed[g]if g in changed else ordinary[g]for g in range(n)]
    signature=sha256(json.dumps(chosen,separators=(',',':')).encode()).hexdigest();scope=sha256(json.dumps((doc['word_sha256'],doc.get('Q')),separators=(',',':')).encode()).hexdigest()
    with sqlite3.connect(WORK/'claims.sqlite',timeout=30)as db:
        try:db.execute('INSERT INTO claims VALUES(?,?,?)',(scope,signature,case));db.commit();prior=None
        except sqlite3.IntegrityError:prior=db.execute('SELECT case_id FROM claims WHERE scope=? AND digest=?',(scope,signature)).fetchone()[0]
    if prior is not None:result=dict(status='deduplicated identical complete signed assignment',case_id=case,configuration=config,duplicate_of=prior,seconds=time.monotonic()-at)
    else:
        for old,targets in enumerate(successors):
            for new in targets:assert contained(chosen[old],chosen[new])
        aliases=[];lookup={};frames=[]
        for f in chosen:
            if f not in lookup:lookup[f]=len(frames);frames.append(f)
            aliases.append(lookup[f])
        fresh=dict(word);fresh.update(frame_format='positive-signed-v1',frames=frames,physical_region_address_aliases=aliases)
        fresh['ops']=[(a,b,aliases[g])for a,b,g in word['ops']];fresh['outputs']=[(s,aliases[g],c,t)for s,g,c,t in word['outputs']];fresh['events']=[(s,-1 if old<0 else aliases[old],aliases[new])for s,old,new in word['events']]
        raw=(json.dumps(fresh,separators=(',',':'))+'\n').encode();path=target/'word.json.gz'
        with path.open('wb')as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0)as out:out.write(raw)
        audit=check(path,target/'signed-transitions.bin')
        result=dict(status='selective positive same-role word full dirty/address PASS',case_id=case,configuration=config,h=h,R=word['R'],word_path=str(path),word_sha256=sha256(raw).hexdigest(),independent=audit,changed_address_classes=len(changed),forward_closure_additions=closure,original_roles_and_xors_unchanged=True,assignment_sha256=signature,seconds=time.monotonic()-at)
        result['producer']=dict(h=h,R=word['R'],dag_sha256=result['word_sha256'])
    result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest();result['completed_utc']=datetime.now(timezone.utc).isoformat();(target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=case,status=result['status'],R=result.get('R'),changed=result.get('changed_address_classes'),seconds=result['seconds'])),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parents',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=6);a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True)
    with sqlite3.connect(a.work/'claims.sqlite')as db:db.execute('CREATE TABLE claims(scope TEXT,digest TEXT,case_id TEXT,PRIMARY KEY(scope,digest))')
    parents=json.loads(a.parents.read_text());choices=[('terminal-common',v)for v in(1,-1,-2,-4,-8,25)]+[('rank-suffix',r)for r in(2,4,6,8,10,12,14,16,18,20,22)]+[(kind,r)for kind in('core-single','core-pair')for r in(4,12,18)]
    configs=[dict(parent=parent,mode=mode,value=value)for mode,value in choices for parent in parents];pending=list(configs);active={};result=dict(status='running',command=sys.argv,configurations=configs,rows=[])
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.work,))as pool:
        while pending or active:
            while pending and len(active)<a.workers:
                config=pending.pop(0);active[pool.submit(evaluate,config)]=config
            done,_=wait(active,return_when=FIRST_COMPLETED)
            for f in done:
                active.pop(f);row=f.result();result['rows'].append({k:v for k,v in row.items()if k!='independent'});tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
