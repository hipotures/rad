#!/usr/bin/env python3
"""Joint-region choices by local formal output slack and seeded order.

Local counts guide proposals only; physical role savings and costs are
measured by the complete synthesized word, its literal dirty replay and
separate full matrix profiles. Formal incoming variables remain distinct,
including values whose clean source coefficient supports happen to agree.
"""
import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor,wait,FIRST_COMPLETED
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys,time
import joint_region_budget_search as budget
import joint_region_search_v3 as region


def assign(c,config):
    assigned={x:(c.core[x],c.union[x])for x in c.active};groups=defaultdict(set);users=defaultdict(set)
    for x in sorted(c.active):
        groups[assigned[x]].add(x)
        for y in c.args[x]or():users[y].add(x)
    protected={assigned[x]for x in c.outputs.values()};protected.update(assigned[x]for x in c.active if not c.args[x])
    initial=len(groups);changes=[];keys=sorted(groups,key=lambda f:(region.rank(f),min(groups[f])))
    policy=config['policy']
    if policy.startswith('seeded-'):
        seed=int(policy.split('-')[1]);keys.sort(key=lambda f:sha256(repr((seed,f,min(groups[f]))).encode()).digest())
    else:
        original=region.assignments;region.assignments=lambda circuit,configuration:(assigned,dict(changed_regions=0,initial_regions=initial,final_regions=initial))
        _,blocks,uses,_,_,_,_,_=region.build_regions(config['h'],dict(policy='baseline'))
        region.assignments=original;byframe={b['frame']:b for b in blocks};score={}
        for f in keys:
            b=byframe[f]
            if policy=='input-slack':score[f]=len(b['inputs'])-len(b['outbasis'])
            elif policy=='observation-slack':score[f]=len(b['uses'])-len(b['outvalues'])
            else:
                score[f]=-10**6
                if f in protected:continue
                targets={assigned[y]for x in groups[f]for y in users[x]if assigned[y]!=f}
                candidates=[t for t in targets if region.fits(f,t)and all(region.fits(t,z)for z in targets)
                            and(config['rank_delta']<0 or region.rank(t)-region.rank(f)<=config['rank_delta'])]
                for t in candidates:
                    other=byframe[t];nodes=groups[f]|groups[t]
                    inputs=sorted({y for x in nodes for y in c.args[x]or()if y not in nodes});coeff={y:1<<i for i,y in enumerate(inputs)}
                    for x in sorted(nodes):coeff[x]=coeff[c.args[x][0]]^coeff[c.args[x][1]]
                    observations=[u for u in b['uses']+other['uses']if uses[u][2]is not None or blocks[uses[u][1]]['frame']not in(f,t)]
                    values={uses[u][0]for u in observations};dim=len(region.COMPILER.basis(coeff[x]for x in sorted(values)))
                    proxy=len(b['uses'])-len(b['outbasis'])+len(other['uses'])-len(other['outbasis'])-len(observations)+dim
                    score[f]=max(score[f],proxy)
        keys.sort(key=lambda f:(-score[f],region.rank(f),min(groups[f])))
    for f in keys:
        if f not in groups or f in protected:continue
        nodes=groups[f];targets={assigned[y]for x in nodes for y in users[x]if assigned[y]!=f}
        candidates=[t for t in targets if region.fits(f,t)and all(region.fits(t,z)for z in targets)
                    and(config['rank_delta']<0 or region.rank(t)-region.rank(f)<=config['rank_delta'])]
        if not candidates:continue
        target=min(candidates,key=lambda t:(region.rank(t),min(groups[t])))
        moved=sorted(nodes)
        for x in moved:assigned[x]=target
        groups[target].update(nodes);del groups[f]
        changes.append(dict(old_frame=f,new_frame=target,nodes=moved))
        if config['limit']and len(changes)>=config['limit']:break
    for x in c.active:
        for y in c.args[x]or():assert region.fits(assigned[y],assigned[x])
    for x in c.outputs.values():assert assigned[x]==(c.core[x],c.union[x])
    return assigned,dict(changed_regions=len(changes),initial_regions=initial,final_regions=len(groups),literal_terminal_frames=True,ordering_policy=policy,changes=changes)


def initialize(source,work):budget.initialize(source,work);budget.ORIGINAL_ASSIGN=assign


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=6)
    p.add_argument('--dimensions',nargs='+',type=int,default=[23,25]);p.add_argument('--limits',nargs='+',type=int,default=[1,4,16,64,128,256]);p.add_argument('--rank-deltas',nargs='+',type=int,default=[1,2,4]);p.add_argument('--seeds',nargs='+',type=int,default=[104729,130363,2026100801]);p.add_argument('--previous-output',type=Path);p.add_argument('--previous-total',type=int,default=122);p.add_argument('--previous-claims',type=Path)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True)
    with sqlite3.connect(a.work/'assignment-claims.sqlite')as db:
        db.execute('CREATE TABLE claims(h INTEGER,digest TEXT,case_id TEXT,PRIMARY KEY(h,digest))')
        if a.previous_claims:
            with sqlite3.connect(a.previous_claims)as old:db.executemany('INSERT OR IGNORE INTO claims VALUES(?,?,?)',old.execute('SELECT h,digest,case_id FROM claims').fetchall())
    policies=['local-formal-slack','input-slack','observation-slack']+[f'seeded-{seed}'for seed in a.seeds]
    configs=[dict(h=h,kind='original',policy=policy,rank_delta=delta,sweeps=1,limit=limit)for limit in a.limits for h in a.dimensions for policy in policies for delta in a.rank_deltas]
    result=dict(status='running',command=sys.argv,source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',configurations=configs,rows=[]);pending=list(configs);active={}
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,initargs=(a.source,a.work))as pool:
        while pending or active:
            remaining=max(0,a.previous_total-len(json.loads(a.previous_output.read_text())['rows']))if a.previous_output else 0
            cap=a.workers-min(a.workers,remaining)
            while pending and len(active)<cap:
                c=pending.pop(0);active[pool.submit(budget.evaluate,c)]=c
            done,_=wait(active,timeout=.5,return_when=FIRST_COMPLETED)if active else(set(),set())
            if not active:time.sleep(.2)
            for f in done:
                active.pop(f);row=f.result();result['rows'].append({k:v for k,v in row.items()if k!='independent'});tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat());a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
