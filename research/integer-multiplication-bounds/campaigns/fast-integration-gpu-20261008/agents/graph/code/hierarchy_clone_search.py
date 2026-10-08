#!/usr/bin/env python3
"""Co-design distinct common-dependent pair hierarchies and cloned carriers.

Pair-order policies change recursive coarse graph sharing before the native
frame/matching build. A complete clone search follows each new graph in the
same process slot. The main cohort file is compact; complete chain edits and
native witnesses are kept per case in external execution storage.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from positive_clone_search import evaluate as clone_evaluate
from producer_search import digest, initialize, worker


def configure_points(config):
    import partial_swap.graph as graph
    def points(h, common):
        pairs = [(a,a+1) for a in range(0,h-1,2) if common not in (a,a+1)]
        policy = config['hierarchy_policy']
        if policy == 'local-rebalance':
            remaining = [a for a in range(h) if a != common]
            return remaining if common%2 == 0 else remaining[::-1]
        if policy == 'gray':
            pairs.sort(key=lambda pair: (pair[0]//2)^((pair[0]//2)>>1))
        elif policy == 'bit-reverse':
            width = (h//2-1).bit_length()
            pairs.sort(key=lambda pair: int(format(pair[0]//2, f'0{width}b')[::-1],2))
        elif policy == 'common-distance':
            pairs.sort(key=lambda pair: (abs(pair[0]+.5-common),pair[0]))
        elif policy == 'zigzag':
            pairs = [p for lr in zip(pairs[:(len(pairs)+1)//2], reversed(pairs[(len(pairs)+1)//2:])) for p in lr]
            if len(pairs)%2 and len(pairs) < sum(common not in (a,a+1) for a in range(0,h-1,2)):
                pairs.append((h//2//2*2,h//2//2*2+1))
            # Reconstruct the alternating ends exactly, including a central pair.
            base = [(a,a+1) for a in range(0,h-1,2) if common not in (a,a+1)]
            pairs = []
            while base:
                pairs.append(base.pop(0))
                if base: pairs.append(base.pop())
        elif policy == 'interleave-halves':
            k=(len(pairs)+1)//2
            a,b=pairs[:k],pairs[k:]
            pairs=[p for i in range(k) for p in (a[i:i+1]+b[i:i+1])]
        elif policy == 'modular-common':
            size=len(pairs);step=2+(common%(size-1))
            while math.gcd(step,size)!=1:step+=1
            pairs=[pairs[(step*i)%size] for i in range(size)]
        else:
            raise ValueError(policy)
        if policy != 'common-distance' and common%2:
            pairs.reverse()
        head=[a for pair in pairs for a in pair]
        return head+[a for a in range(h) if a!=common and a not in head]
    graph.aligned_points=points


def evaluate(config, work, matcher):
    configure_points(config)
    at=time.monotonic()
    initial=worker(config)
    if initial['status']=='failed':return initial
    parent=Path(initial['dag_path']).parent/'parent.json'
    parent.write_text(json.dumps(dict(producer=initial),indent=2,sort_keys=True)+'\n')
    result=clone_evaluate((parent,work,matcher,'wide',8,104729,4,config['hierarchy_policy']+'-'+initial['case_id']))
    compact=dict(status=result['status'],configuration=config,initial_producer=initial,
                 seconds=time.monotonic()-at,pid=os.getpid())
    if result['status']=='failed':
        compact['error']=result['error']
    else:
        compact.update(producer=result['producer'],case_id=result['case_id'],
                       role_saving=result['role_saving'],
                       full_witness_path=str(Path(work)/'raw'/f"{result['case_id']}.json"))
    return compact


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=9)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists()and 1<=a.workers<=10
    builds=a.work/'builds';builds.mkdir(parents=True)
    authored=Path(__file__).parent
    for src,name in ((a.source/'scripts'/'partial_swap'/'match_exported_dag.cpp','match_exported_dag'),
                     (authored/'moment_match_positive.cpp','moment_match_positive'),
                     (authored/'moment_match_rank_node.cpp','moment_match_rank_node')):
        subprocess.run(['c++','-O3','-std=c++17',str(src),'-o',str(builds/name)],check=True)
    configs=[]
    for h in range(21,36,2):
        for j,policy in enumerate(('gray','bit-reverse','common-distance','zigzag','interleave-halves','modular-common','local-rebalance')):
            for k,tree in enumerate(('left','support-right','support-left')):
                configs.append(dict(h=h,threshold=2,grouping='pairs',tree=tree,mode=2,
                                    seed=700000000+1000000*j+10000*k+h,hierarchy_policy=policy))
    result=dict(status='running',command=sys.argv,workers=a.workers,configurations=configs,rows=[],
                started_utc=datetime.now(timezone.utc).isoformat(),
                source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',
                source_sha256={p.name:digest(p) for p in authored.glob('*.py')})
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,
                             initargs=(a.source,a.work,builds/'moment_match_positive')) as pool:
        futures=[pool.submit(evaluate,c,a.work,builds/'moment_match_rank_node')for c in configs]
        for future in as_completed(futures):
            row=future.result();result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps(dict(completed=len(result['rows']),total=len(configs),pid=row.get('pid'),
                                  h=row['configuration']['h'],policy=row['configuration']['hierarchy_policy'],
                                  status=row['status'],R=row.get('producer',{}).get('R'),
                                  role_saving=row.get('role_saving'),seconds=row['seconds'])),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
