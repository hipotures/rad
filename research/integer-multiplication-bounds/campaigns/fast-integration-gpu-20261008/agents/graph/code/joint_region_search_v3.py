#!/usr/bin/env python3
"""Terminal-safe contraction of actual joint compiler regions.

Joint synthesis and reclamation: eumemic PR57, OpenAI Codex assisted, retained
unchanged from pinned public PR62 snapshot. Interval scalar producer:
Avi Eisenberg PR62, Anthropic assisted. Task-owned change: merge a nonterminal,
non-source region into a containing consumer frame only when that enlarged
frame is contained in EVERY remaining consumer; terminal frames stay literal.
All roles are counted from the executed word and independently replayed.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time
from joint_word_check_v2 import check

SOURCE=None
WORK=None
COMPILER=None
GRAPH_MODULE=None
CACHE={}
LAST_DIAGNOSTIC={}


def fits(a,b):return not(b[0]&~a[0])and not(a[1]&~b[1])
def rank(frame):return 1 if frame[0]==frame[1]else frame[1].bit_count()-frame[0].bit_count()


def initialize(source,work):
    global SOURCE,WORK,COMPILER,GRAPH_MODULE
    SOURCE=Path(source);WORK=Path(work);sys.dont_write_bytecode=True
    sys.path.insert(0,str(SOURCE/'scripts/experiments'))
    import binary_frame_compiler
    COMPILER=binary_frame_compiler
    # Upstream restricts only a reporting dictionary to23/25. Extend that
    # metadata lookup for exact small controls, leaving synthesis unchanged.
    public_path=SOURCE/'scripts/experiments/binary_frame_compiler.py'
    adapted=public_path.read_text().replace('baseline_pr48_roles={23:36432,25:48329}[h]',
                                           'baseline_pr48_roles={23:36432,25:48329}.get(h)')
    exec(compile(adapted,str(public_path),'exec'),COMPILER.__dict__)
    path=SOURCE/'research/pair-assembly/pair_graph.py'
    assert sha256(path.read_bytes()).hexdigest()=='3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420'
    spec=importlib.util.spec_from_file_location('pinned_interval_pair_graph',path)
    GRAPH_MODULE=importlib.util.module_from_spec(spec);spec.loader.exec_module(GRAPH_MODULE)


def graph(h):
    if h not in CACHE:
        if h in(23,25):c=GRAPH_MODULE.graph(h)
        else:
            local=GRAPH_MODULE.circuit_class(h)(h-1);total=local.pair(list(range(h-1)))[0];local.outputs[()]=total;stack=[total]
            while stack:
                x=stack.pop()
                if not x or x in local.active:continue
                local.active.add(x)
                if local.args[x]:stack.extend(local.args[x])
            local.additions=sum(local.args[x]is not None for x in local.active)
            c=GRAPH_MODULE.SharedPointCircuit(h,local,point_order=GRAPH_MODULE.alternating_points)
        CACHE[h]=c
    return CACHE[h]


def assignments(c,config):
    assigned={x:(c.core[x],c.union[x])for x in c.active};groups=defaultdict(set);users=defaultdict(set)
    for x in sorted(c.active):
        groups[assigned[x]].add(x)
        for y in c.args[x]or():users[y].add(x)
    terminals=set(c.outputs.values());protected={assigned[x]for x in terminals}
    protected.update(assigned[x]for x in c.active if not c.args[x])
    count=0;changes=[]
    if config['policy']=='baseline':return assigned,dict(changed_regions=0,initial_regions=len(groups),final_regions=len(groups))
    initial=len(groups)
    for sweep in range(config['sweeps']):
        progress=0
        keys=sorted(groups,key=lambda f:(rank(f),min(groups[f])))
        if config['policy']=='late':keys.reverse()
        for frame in keys:
            if frame not in groups or frame in protected:continue
            nodes=groups[frame]
            successors={assigned[y]for x in nodes for y in users[x]if assigned[y]!=frame}
            if not successors:continue
            targets=[target for target in successors if fits(frame,target)and all(fits(target,other)for other in successors)
                     and(config['rank_delta']<0 or rank(target)-rank(frame)<=config['rank_delta'])]
            if not targets:continue
            if config['policy']=='largest':target=max(targets,key=lambda f:(rank(f),len(groups[f]),-min(groups[f])))
            elif config['policy']=='sparse':target=min(targets,key=lambda f:(len(groups[f]),rank(f),min(groups[f])))
            else:target=min(targets,key=lambda f:(rank(f),min(groups[f])))
            moved=sorted(nodes)
            for x in moved:assigned[x]=target
            groups[target].update(nodes);del groups[frame]
            changes.append(dict(old_frame=frame,new_frame=target,nodes=moved));count+=1;progress+=1
            if config['limit']and count>=config['limit']:break
        if not progress or(config['limit']and count>=config['limit']):break
    for x in c.active:
        for y in c.args[x]or():assert fits(assigned[y],assigned[x])
    for x in terminals:assert assigned[x]==(c.core[x],c.union[x])
    return assigned,dict(changed_regions=count,initial_regions=initial,final_regions=len(groups),literal_terminal_frames=True,changes=changes)


def build_regions(h,config):
    global LAST_DIAGNOSTIC
    c=graph(h);assigned,LAST_DIAGNOSTIC=assignments(c,config);groups={};owner={};signal={};blocks=[]
    for x in sorted(c.active):
        key=assigned[x]
        if key not in groups:groups[key]=len(blocks);blocks.append(dict(nodes=[],frame=key,inputs=set(),uses=[]))
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
    for b in blocks:b['rank']=rank(b['frame'])
    order=sorted(range(len(blocks)),key=lambda g:(blocks[g]['rank'],min(blocks[g]['nodes'])));place={g:i for i,g in enumerate(order)}
    for g,b in enumerate(blocks):
        coeff={y:1<<i for i,y in enumerate(b['inputs'])}
        if b['source']:coeff[b['nodes'][0]]=1
        for x in b['nodes']:
            if c.args[x]:coeff[x]=coeff[c.args[x][0]]^coeff[c.args[x][1]]
        b['coeff']=coeff;b['outvalues']=sorted({uses[u][0]for u in b['uses']})
        b['outbasis']=COMPILER.basis(coeff[x]for x in b['outvalues']);b['candidates']=[];b['selected']=set()
        if not b['source']:
            for i,y in enumerate(b['inputs']):
                if not COMPILER.independent(b['outbasis'],1<<i):continue
                for u in value_uses[y]:
                    _,target,terminal=uses[u]
                    if place[g]<place[target]and fits(b['frame'],blocks[target]['frame']):b['candidates'].append((u,i))
    return c,blocks,uses,value_uses,owner,signal,order,fits


def evaluate(config):
    at=time.monotonic();case='-'.join(str(config[k])for k in('h','policy','rank_delta','sweeps','limit'));target=WORK/'raw'/case;target.mkdir(parents=True,exist_ok=False)
    try:
        original=COMPILER.build;COMPILER.build=lambda h:build_regions(h,config)
        compiled,word=COMPILER.compile_(config['h'],matching=True,reclaim=True,dirty=True)
        COMPILER.build=original
        raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=target/'word.json.gz'
        if config['policy']=='baseline'and config['h']in(23,25):
            reference=SOURCE/f"research/pair-assembly/frame/frame-word-{config['h']}.json.gz"
            assert sha256(raw).hexdigest()==sha256(gzip.decompress(reference.read_bytes())).hexdigest(),'Fresh public baseline executed word differs'

        with path.open('wb')as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0)as gz:gz.write(raw)
        audit=check(path,target/'transitions.bin')
        scalar=graph(config['h']).verify()
        (target/'region-changes.json').write_text(json.dumps(LAST_DIAGNOSTIC,sort_keys=True)+'\n')
        result=dict(status='exact changed joint-word compiler and independent full dirty audit PASS',case_id=case,configuration=config,
                    compiled=compiled,independent=audit,scalar=scalar,word_path=str(path),word_sha256=sha256(raw).hexdigest(),
                    region_summary={k:v for k,v in LAST_DIAGNOSTIC.items()if k!='changes'},region_changes_path=str(target/'region-changes.json'),
                    seconds=time.monotonic()-at,completed_utc=datetime.now(timezone.utc).isoformat())
    except Exception as error:
        COMPILER.build=original
        result=dict(status='failed',case_id=case,configuration=config,error=repr(error),seconds=time.monotonic()-at)
    result['source_sha256']=sha256(Path(__file__).read_bytes()).hexdigest();(target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=case,status=result['status'],R=result.get('compiled',{}).get('roles'),regions=result.get('region_summary'),seconds=result['seconds'],error=result.get('error'))),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=6);p.add_argument('--dimensions',type=int,nargs='+',default=[23,25]);p.add_argument('--policies',nargs='+',default=['rank-first','largest','sparse','late'])
    p.add_argument('--rank-deltas',type=int,nargs='+',default=[1,2,4,-1]);p.add_argument('--sweeps',type=int,nargs='+',default=[1,3]);p.add_argument('--limit',type=int,default=0)
    p.add_argument('--previous-raw',type=Path);p.add_argument('--previous-total',type=int,default=2496)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True);initialize(a.source,a.work)
    configs=[dict(h=h,policy=policy,rank_delta=delta,sweeps=sweeps,limit=a.limit)for h in a.dimensions for policy in a.policies for delta in a.rank_deltas for sweeps in a.sweeps]
    result=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),command=sys.argv,configurations=configs,source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',rows=[])
    pending=list(configs);active={}
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.source,a.work))as pool:
        while pending or active:
            previous=max(0,a.previous_total-len(list(a.previous_raw.glob('*/result.json'))))if a.previous_raw else 0
            cap=a.workers-min(a.workers,previous)
            while pending and len(active)<cap:
                c=pending.pop(0);active[pool.submit(evaluate,c)]=c
            done,_=wait(active,timeout=.5,return_when=FIRST_COMPLETED)if active else(set(),set())
            if not active:time.sleep(.25)
            for future in done:
                active.pop(future);row=future.result();compact={k:v for k,v in row.items()if k not in('independent','scalar')};compact['full_result_path']=str(a.work/'raw'/row['case_id']/'result.json');result['rows'].append(compact)
                temp=a.output.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');temp.replace(a.output)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
