#!/usr/bin/env python3
"""Joint original-envelope carrier, backward frame and tree-order search."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from producer_search import digest,initialize,worker


def evaluate(configuration):
    os.environ['RAD_FRAME_SEED'] = str(configuration['frame_seed'])
    os.environ['RAD_FRAME_MODE'] = str(configuration['frame_mode'])
    return worker(configuration)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=7)
    p.add_argument('--family',choices=['frame','seed'],default='frame')
    a=p.parse_args();assert not a.output.exists() and 1<=a.workers<=8
    (a.work/'builds').mkdir(parents=True,exist_ok=True)
    native=Path(__file__).with_name('frame_match_envelope.cpp')
    positive=Path(__file__).with_name('moment_match_positive.cpp')
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(a.work/'builds'/'match_exported_dag')],check=True)
    subprocess.run(['c++','-O3','-std=c++17',str(positive),'-o',str(a.work/'builds'/'moment_match_positive')],check=True)
    configurations=[]
    if a.family=='frame':
        for h in (21,23,25,27):
            for tree in ('left','support-right','seeded-left'):
                for frame_mode in (1,2,3,4):
                    seed=130363+1009*frame_mode
                    configurations.append(dict(h=h,threshold=2,grouping='pairs',tree=tree,mode=2,seed=seed,
                                               frame_mode=frame_mode,frame_seed=seed))
    else:
        for h in (21,23,25,27):
            for k in range(24):
                seed=224737+15485863*k
                configurations.append(dict(h=h,threshold=2,grouping='pairs',tree='seeded-left',mode=4,seed=seed,
                                           frame_mode=0,frame_seed=seed))
    result=dict(status='running',family=a.family,command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),
                source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',workers=a.workers,
                source_sha256={f.name:digest(f) for f in (Path(__file__),native,positive,Path(__file__).with_name('producer_search.py'))},
                configurations=configurations,rows=[])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,
                             initargs=(a.source,a.work,a.work/'builds'/'moment_match_positive')) as pool:
        futures=[pool.submit(evaluate,c) for c in configurations]
        for f in as_completed(futures):
            row=f.result();result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps({k:row.get(k) for k in ('case_id','status','R','matched','seconds','pid')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
