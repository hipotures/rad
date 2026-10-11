#!/usr/bin/env python3
"""Joint region synthesis on actual backward signed positive address spaces.

Joint Gaussian/matroid/reclamation code: eumemic public PR57, unchanged from
pinned PR62. Scalar producer: Avi Eisenberg public PR62. Backward signed
constraint construction follows icekylinx public PR36 (Apache-2.0); here it
uses scalar dependencies only, and every new joint carrier is checked by
exact rational containment. This task-owned combination changes physical
regions BEFORE synthesis. No gatewise role formula is used.
"""
from __future__ import annotations
import argparse
from collections import defaultdict,deque
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys,time
import heapq
import joint_region_search_v3 as region
from check_compiled_witness import basis,contained
from joint_word_check_v3 import check

WORK=None
LABEL_CACHE={}
LAST={}


def initialize(source,work):
    global WORK
    WORK=Path(work);region.initialize(source,work)


def positive_labels(c,h):
    groups={};owner={};nodes=[]
    for x in sorted(c.active):
        key=(c.core[x],c.union[x])if c.args[x]else('source',x)
        if key not in groups:groups[key]=len(nodes);nodes.append([])
        g=groups[key];owner[x]=g;nodes[g].append(x)
    ng=len(nodes);forced=[0]*ng;edges=[set()for _ in nodes];successors=[set()for _ in nodes];predecessors=[set()for _ in nodes]
    full=(1<<h)-1
    for(common,triple),x in c.outputs.items():
        g=owner[x];forced[g]|=1<<common
        if len(triple)==3:
            omitted=tuple(j for j in triple if j!=common);assert len(omitted)==2
            edges[g].add(tuple(sorted(omitted)))
    for x in sorted(c.active):
        for y in c.args[x]or():
            a,b=owner[y],owner[x]
            if a!=b:successors[a].add(b);predecessors[b].add(a)
    pending=[len(z)for z in successors];ready=deque(g for g in range(ng)if not pending[g]);seen=0
    while ready:
        g=ready.popleft();seen+=1;assert forced[g]
        for a in predecessors[g]:
            forced[a]|=forced[g];edges[a].update(edges[g]);pending[a]-=1
            if not pending[a]:ready.append(a)
    assert seen==ng
    labels={}
    for g,xs in enumerate(nodes):
        if not c.args[xs[0]]:
            assert len(xs)==1
            F=c.core[xs[0]];label=(1,F,tuple(int(F>>j&1)for j in range(h)))
        else:
            F=forced[g];assert F.bit_count()in(1,2)
            key=(h,F,tuple(sorted(edges[g])))
            if key not in LABEL_CACHE:
                adjacency=[set()for _ in range(h)]
                for a,b in edges[g]:assert not(F>>a&1 or F>>b&1);adjacency[a].add(b);adjacency[b].add(a)
                colors=[-1]*h;symbols=[0]*h;parts=[]
                for a in range(h):
                    if F>>a&1:symbols[a]=1;continue
                    if colors[a]>=0:continue
                    colors[a]=0;todo=[a];positive=[];negative=[];bad=False
                    while todo:
                        b=todo.pop();(positive if colors[b]==0 else negative).append(b)
                        for j in sorted(adjacency[b]):
                            if colors[j]<0:colors[j]=1-colors[b];todo.append(j)
                            elif colors[j]==colors[b]:bad=True
                    if not bad:parts.append((positive,negative))
                for i,(positive,negative)in enumerate(parts,2):
                    for a in positive:symbols[a]=i
                    for a in negative:symbols[a]=-i
                LABEL_CACHE[key]=(len(parts),F,tuple(symbols))
            label=LABEL_CACHE[key]
        for x in xs:labels[x]=label
    # Each original address fits its new positive address. Sources and
    # terminal membership are checked independently in the executed word.
    for x in sorted(c.active):
        if c.args[x]:
            F,M=c.core[x],c.union[x];old=(M.bit_count()-F.bit_count(),F,tuple(1 if F>>j&1 else j+2 if M>>j&1 else 0 for j in range(h)))
            assert contained(old,labels[x])
            for y in c.args[x]:assert contained(labels[y],labels[x])
    return labels


def assign(c,h,config):
    labels=positive_labels(c,h);original=dict(labels);groups=defaultdict(set);users=defaultdict(set)
    for x in sorted(c.active):
        groups[labels[x]].add(x)
        for y in c.args[x]or():users[y].add(x)
    protected={labels[x]for x in c.outputs.values()}
    protected.update(labels[x]for x in c.active if not c.args[x])
    before=len(groups);changes=[]
    if config['policy']!='positive':
        for sweep in range(config['sweeps']):
            progress=0;keys=sorted(groups,key=lambda f:(f[0],min(groups[f])))
            if config['policy']=='late':keys.reverse()
            for f in keys:
                if f not in groups or f in protected:continue
                nodes=groups[f];targets={labels[y]for x in nodes for y in users[x]if labels[y]!=f}
                candidates=[t for t in targets if contained(f,t)and all(contained(t,z)for z in targets)
                            and(config['rank_delta']<0 or t[0]-f[0]<=config['rank_delta'])]
                if not candidates:continue
                target=min(candidates,key=lambda z:(z[0],min(groups[z])))
                for x in nodes:labels[x]=target
                groups[target].update(nodes);del groups[f]
                changes.append(dict(old_frame=f,new_frame=target,nodes=sorted(nodes)));progress+=1
                if config['limit']and len(changes)>=config['limit']:break
            if not progress or(config['limit']and len(changes)>=config['limit']):break
    for x in c.active:
        for y in c.args[x]or():assert contained(labels[y],labels[x])
    for x in c.outputs.values():assert labels[x]==original[x]
    return labels,dict(initial_regions=before,final_regions=len(groups),changed_regions=len(changes),changes=changes)


def build(h,config):
    global LAST
    c=region.graph(h);assigned,LAST=assign(c,h,config);groups={};owner={};signal={};blocks=[]
    for x in sorted(c.active):
        frame=assigned[x]
        key=(c.core[x],c.union[x])if config.get('partition')=='original'and c.args[x]else('source',x)if config.get('partition')=='original'else frame
        if key not in groups:groups[key]=len(blocks);blocks.append(dict(nodes=[],frame=frame,inputs=set(),uses=[]))
        g=groups[key];owner[x]=g;blocks[g]['nodes'].append(x)
        signal[x]=signal[c.args[x][0]]^signal[c.args[x][1]]if c.args[x]else 1<<(x-1)
    for x in sorted(c.active):
        for y in c.args[x]or():
            if owner[y]!=owner[x]:blocks[owner[x]]['inputs'].add(y)
    uses=[];value_uses=defaultdict(list)
    for g,b in enumerate(blocks):
        b['inputs']=sorted(b['inputs']);b['source']=not c.args[b['nodes'][0]]
        for y in b['inputs']:
            u=len(uses);uses.append((y,g,None));value_uses[y].append(u);blocks[owner[y]]['uses'].append(u)
    for target,x in c.outputs.items():
        u=len(uses);uses.append((x,owner[x],target));value_uses[x].append(u);blocks[owner[x]]['uses'].append(u)
    for b in blocks:b['rank']=b['frame'][0]
    successors=[set()for _ in blocks];pending=[set()for _ in blocks]
    for g,b in enumerate(blocks):
        for y in b['inputs']:successors[owner[y]].add(g);pending[g].add(owner[y])
    def priority(g):
        b=blocks[g];x=b['nodes'][0];oldrank=1 if b['source']else c.union[x].bit_count()-c.core[x].bit_count()
        return b['rank'],oldrank,x,g
    ready=[priority(g)for g in range(len(blocks))if not pending[g]];heapq.heapify(ready);order=[]
    while ready:
        *_,g=heapq.heappop(ready);order.append(g)
        for target in sorted(successors[g]):
            pending[target].remove(g)
            if not pending[target]:heapq.heappush(ready,priority(target))
    assert len(order)==len(blocks);place={g:i for i,g in enumerate(order)}
    LAST.update(physical_regions=len(blocks),partition=config.get('partition','coalesced-positive'))
    for g,b in enumerate(blocks):
        coeff={y:1<<i for i,y in enumerate(b['inputs'])}
        if b['source']:coeff[b['nodes'][0]]=1
        for x in b['nodes']:
            if c.args[x]:coeff[x]=coeff[c.args[x][0]]^coeff[c.args[x][1]]
        b['coeff']=coeff;b['outvalues']=sorted({uses[u][0]for u in b['uses']});b['outbasis']=region.COMPILER.basis(coeff[x]for x in b['outvalues']);b['candidates']=[];b['selected']=set()
        if not b['source']:
            for i,y in enumerate(b['inputs']):
                if not region.COMPILER.independent(b['outbasis'],1<<i):continue
                for u in value_uses[y]:
                    _,target,terminal=uses[u]
                    if place[g]<place[target]and contained(b['frame'],blocks[target]['frame']):b['candidates'].append((u,i))
    return c,blocks,uses,value_uses,owner,signal,order,contained


def evaluate(config):
    at=time.monotonic();case='-'.join(str(config[k])for k in('h','policy','rank_delta','sweeps','limit'))+'-'+config.get('partition','coalesced');target=WORK/'raw'/case;target.mkdir(parents=True,exist_ok=False)
    original=region.COMPILER.build
    try:
        region.COMPILER.build=lambda h:build(h,config)
        compiled,word=region.COMPILER.compile_(config['h'],matching=True,reclaim=True,dirty=True)
        region.COMPILER.build=original;word['frame_format']='positive-signed-v1'
        # Equal address spaces retain separate physical Gaussian regions.
        # Canonicalize only address IDs after synthesis, keeping every XOR,
        # source location, role and scalar observation literal.
        canonical={};unique=[];aliases=[]
        for frame in word['frames']:
            key=(frame[0],frame[1],tuple(frame[2]))
            if key not in canonical:canonical[key]=len(unique);unique.append(frame)
            aliases.append(canonical[key])
        word['frames']=unique;word['ops']=[(a,b,aliases[g])for a,b,g in word['ops']]
        word['outputs']=[(s,aliases[g],c,t)for s,g,c,t in word['outputs']]
        word['events']=[(s,-1 if before<0 else aliases[before],aliases[after])for s,before,after in word['events']]
        word['physical_region_address_aliases']=aliases
        raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=target/'word.json.gz'
        with path.open('wb')as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0)as gz:gz.write(raw)
        audit=check(path,target/'signed-transitions.bin')
        (target/'region-changes.json').write_text(json.dumps(LAST,sort_keys=True)+'\n')
        result=dict(status='signed positive actual joint word and independent full dirty PASS',case_id=case,configuration=config,compiled=compiled,independent=audit,word_path=str(path),word_sha256=sha256(raw).hexdigest(),region_summary={k:v for k,v in LAST.items()if k!='changes'},region_changes_path=str(target/'region-changes.json'),seconds=time.monotonic()-at)
    except Exception as error:
        region.COMPILER.build=original
        result=dict(status='failed',case_id=case,configuration=config,error=repr(error),seconds=time.monotonic()-at)
    result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest();result['completed_utc']=datetime.now(timezone.utc).isoformat()
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(case_id=case,status=result['status'],R=result.get('compiled',{}).get('roles'),error=result.get('error'),seconds=result['seconds'])),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=6)
    p.add_argument('--dimensions',nargs='+',type=int,default=[23,25]);p.add_argument('--policies',nargs='+',default=['positive']);p.add_argument('--rank-deltas',nargs='+',type=int,default=[1]);p.add_argument('--sweeps',nargs='+',type=int,default=[1]);p.add_argument('--limits',nargs='+',type=int,default=[0]);p.add_argument('--partitions',nargs='+',default=['original'])
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True);initialize(a.source,a.work)
    configs=[dict(h=h,policy=policy,rank_delta=delta,sweeps=sweep,limit=limit,partition=partition)for h in a.dimensions for partition in a.partitions for policy in a.policies for delta in a.rank_deltas for sweep in a.sweeps for limit in a.limits if policy!='positive'or(delta==a.rank_deltas[0]and sweep==a.sweeps[0]and limit==a.limits[0])]
    result=dict(status='running',command=sys.argv,configurations=configs,rows=[]);active={};pending=list(configs)
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.source,a.work))as pool:
        while active or pending:
            while pending and len(active)<a.workers:
                c=pending.pop(0);active[pool.submit(evaluate,c)]=c
            done,_=wait(active,return_when=FIRST_COMPLETED)
            for f in done:
                active.pop(f);row=f.result();compact={k:v for k,v in row.items()if k!='independent'};compact['full_result_path']=str(a.work/'raw'/row['case_id']/'result.json');result['rows'].append(compact)
                temp=a.output.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');temp.replace(a.output)
    result['status']='complete';a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
