#!/usr/bin/env python3
"""Select association by source-support scale, not one global tree policy."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from producer_search import digest,initialize,worker


def evaluate(c):
    from exclusion_circuit import ExclusionCircuit
    from partial_swap.paired import PairedExclusionCircuit
    def total(self,values):
        values=[x for x in values if x]
        support=0
        for node in values:
            assert not support & self.support[node]
            support|=self.support[node]
        policy=c['hybrid_policy'];cut=c['cut']
        if policy=='above-support':use_left=support.bit_count()>=cut
        elif policy=='below-support':use_left=support.bit_count()<=cut
        else:
            key=sha256(repr((c['seed'],support)).encode()).digest()
            use_left=int.from_bytes(key[:4],'little')%100<cut
        if not use_left:return ExclusionCircuit.total(self,values)
        result=0
        for node in values:result=self.add(result,node)
        return result
    PairedExclusionCircuit.total=total
    return worker(c)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=10)
    a=p.parse_args();assert not a.output.exists() and 1<=a.workers<=10
    (a.work/'builds').mkdir(parents=True,exist_ok=True)
    native=Path(__file__).with_name('moment_match_positive.cpp')
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(a.work/'builds'/'moment_match_positive')],check=True)
    subprocess.run(['c++','-O3','-std=c++17',str(a.source/'scripts/partial_swap/match_exported_dag.cpp'),
                    '-o',str(a.work/'builds'/'match_exported_dag')],check=True)
    configurations=[]
    grounds=[*range(17,36),37,39,41,43,45]
    for h in grounds:
        for index,policy in enumerate(('above-support','below-support')):
            for cut in (4,8,16,32,64,128):
                seed=330019+1009*cut+15485863*index
                configurations.append(dict(h=h,threshold=2,grouping='pairs',tree='balanced',mode=2,
                                           seed=seed,hybrid_policy=policy,cut=cut))
    for h in (21,23,25,27):
        for index,cut in enumerate((25,50,75)):
            for k in range(4):
                seed=413017+15485863*k+1000000007*index
                configurations.append(dict(h=h,threshold=2,grouping='pairs',tree='balanced',mode=4,
                                           seed=seed,hybrid_policy='hashed-support',cut=cut))
    result=dict(status='running',command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),
                source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',workers=a.workers,
                allocation_revision='Coordinator released GPU host slots; graph budget10, geometry6',
                source_sha256={p.name:digest(p) for p in (Path(__file__),native,Path(__file__).with_name('producer_search.py'))},
                configurations=configurations,rows=[])
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,
                             initargs=(a.source,a.work,a.work/'builds'/'moment_match_positive')) as pool:
        futures=[pool.submit(evaluate,c)for c in configurations]
        for f in as_completed(futures):
            row=f.result();result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps({k:row.get(k)for k in ('case_id','status','R','matched','seconds','pid')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
