#!/usr/bin/env python3
"""Distinct retained-center cover/frame experiments on complete parent DAGs.

Writes full individual witnesses externally and a compact aggregate. Parent
DAGs are deduplicated before jobs are submitted; final SHA equivalence is
reported separately. No matrix fixed-basis profile is reused after edits.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from producer_search import digest
from reconstruct_centers_inherited import evaluate


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,nargs='+',required=True)
    p.add_argument('--work',type=Path,required=True); p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=6)
    p.add_argument('--dimensions',type=int,nargs='+',default=[23,25])
    p.add_argument('--policies',nargs='+',choices=['largest','rank-first','reverse'],default=['largest','rank-first','reverse'])
    p.add_argument('--limit',type=int,default=64)
    a=p.parse_args(); assert not a.work.exists() and not a.output.exists()
    parents={}
    for path in a.input:
        document=json.loads(path.read_text())
        for row in document.get('rows',[document]):
            producer=row.get('producer',{})
            if producer.get('h') not in a.dimensions or row.get('status')=='failed': continue
            parents.setdefault(producer['dag_sha256'],row)
    builds=a.work/'builds'; builds.mkdir(parents=True)
    inputs=a.work/'inputs'; inputs.mkdir(); matcher=builds/'matcher'
    subprocess.run(['c++','-O3','-std=c++17',str(Path(__file__).with_name('moment_match_rank_node.cpp')),
                    '-o',str(matcher)],check=True)
    jobs=[]
    for sha,row in parents.items():
        parent=inputs/f"h{row['producer']['h']}-{sha[:16]}.json"
        parent.write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
        for policy in a.policies: jobs.append((parent,a.work,matcher,policy,a.limit))
    result=dict(status='running',command=sys.argv,workers=a.workers,parent_count=len(parents),
                total_cases=len(jobs),rows=[],started_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256={f:digest(Path(__file__).with_name(f)) for f in
                    ('center_frame_cohort.py','reconstruct_centers_inherited.py','moment_match_rank_node.cpp')})
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        futures=[pool.submit(evaluate,job) for job in jobs]
        for future in as_completed(futures):
            row=future.result()
            compact={k:row.get(k) for k in ('case_id','status','initial_R','role_saving','seconds','error')}
            compact['producer']=row.get('producer')
            if compact['producer']:
                compact['full_witness_path']=str(Path(compact['producer']['dag_path']).parent/'result.json')
            result['rows'].append(compact)
            tmp=a.output.with_suffix('.tmp'); tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
            print(json.dumps({k:compact.get(k) for k in ('case_id','status','role_saving','seconds','error')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat(),
                  unique_final_dags=len({r['producer']['dag_sha256'] for r in result['rows'] if r.get('producer')}))
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
