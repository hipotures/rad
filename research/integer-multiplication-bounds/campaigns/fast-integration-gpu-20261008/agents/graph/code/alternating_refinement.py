#!/usr/bin/env python3
"""Optimize common-specific reflection choices and multiscale pair blocks."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
from producer_search import digest,initialize,worker


def evaluate(c):
    import partial_swap.graph as graph
    def points(h,common):
        pairs=[(a,a+1)for a in range(0,h-1,2)if common not in(a,a+1)]
        flip=c['reflection_mask']>>common&1
        mode=c['reflection_mode']
        tail=[x for x in range(h)if x!=common and all(x not in pair for pair in pairs)]
        if flip:
            if mode=='whole':pairs.reverse()
            elif mode=='first-half':
                k=len(pairs)//2;pairs=pairs[:k][::-1]+pairs[k:]
            elif mode=='last-half':
                k=len(pairs)//2;pairs=pairs[:k]+pairs[k:][::-1]
            elif mode=='swap-halves':
                k=len(pairs)//2;pairs=pairs[k:]+pairs[:k]
            elif mode=='within-pairs':pairs=[pair[::-1]for pair in pairs]
            elif mode=='mirror-within':pairs=[pair[::-1]for pair in reversed(pairs)]
            elif mode=='tail-first':return tail+[x for pair in pairs for x in pair]
        return [x for pair in pairs for x in pair]+tail
    graph.aligned_points=points
    return worker(c)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=9)
    a=p.parse_args();assert not a.output.exists()and 1<=a.workers<=10
    (a.work/'builds').mkdir(parents=True,exist_ok=True)
    native=Path(__file__).with_name('moment_match_positive.cpp')
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(a.work/'builds'/'moment_match_positive')],check=True)
    subprocess.run(['c++','-O3','-std=c++17',str(a.source/'scripts/partial_swap/match_exported_dag.cpp'),
                    '-o',str(a.work/'builds'/'match_exported_dag')],check=True)
    configurations=[]
    for h in(21,23,25,27):
        base=sum(1<<i for i in range(h)if i%2)
        masks=[base^(1<<i)for i in range(h)]
        masks += [base^(3<<i)for i in range(0,h-1,2)]
        for mask in masks:
            configurations.append(dict(h=h,threshold=2,grouping='pairs',tree='support-right'if h==23 else'left',
                                       mode=2,seed=mask,reflection_mask=mask,reflection_mode='whole'))
        for j,mode in enumerate(('first-half','last-half','swap-halves','within-pairs','mirror-within','tail-first'),1):
            configurations.append(dict(h=h,threshold=2,grouping='pairs',tree='support-right'if h==23 else'left',
                                       mode=2,seed=base+100000000*j,reflection_mask=base,reflection_mode=mode))
    result=dict(status='running',command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),
                source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',workers=a.workers,
                source_sha256={p.name:digest(p)for p in(Path(__file__),native,Path(__file__).with_name('producer_search.py'))},
                configurations=configurations,rows=[])
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,
                             initargs=(a.source,a.work,a.work/'builds'/'moment_match_positive'))as pool:
        fs=[pool.submit(evaluate,c)for c in configurations]
        for f in as_completed(fs):
            row=f.result();result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps({k:row.get(k)for k in('case_id','status','R','matched','seconds','pid')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
