#!/usr/bin/env python3
"""Test new source partitions on distinct paid-clone descendants of seeded DAGs."""
import argparse,json,multiprocessing,sys,time
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cohort',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--code',type=Path,required=True)
    p.add_argument('--matcher',type=Path,required=True)
    p.add_argument('--workers',type=int,required=True)
    p.add_argument('--per-dimension',type=int,default=32)
    a=p.parse_args();assert not a.work.exists();a.work.mkdir(parents=True)
    sys.path.insert(0,str(a.code))
    from alternative_producer_clones import evaluate
    obj=json.loads(a.cohort.read_text());assert obj['status']=='complete'
    rows=[r for r in obj['rows']if r.get('status')!='failed'];inputs=a.work/'inputs';inputs.mkdir();parents=[]
    for h in (23,25):
        seen=set()
        for r in sorted([r for r in rows if r['producer']['h']==h],key=lambda r:r['producer']['R']):
            key=(r['producer']['dag_sha256'],r['producer']['positive_sha256'],r['producer']['witness_sha256'])
            if key in seen:continue
            seen.add(key);parent=inputs/f'h{h}-{len(seen):03d}.json'
            parent.write_text(json.dumps(dict(producer=r['producer']))+'\n');parents.append(parent)
            if len(seen)==a.per_dimension:break
    (a.work/'raw').mkdir()
    tasks=[(parent,a.work,a.matcher,128,2,policy)for parent in parents for policy in ['conservative','mapped-moment','mapped-scarce']]
    protocol=dict(status='running',started_utc=datetime.now(timezone.utc).isoformat(),command=sys.argv,
                  source_input=str(a.cohort),source_input_sha256=sha256(a.cohort.read_bytes()).hexdigest(),
                  parents=len(parents),planned=len(tasks),workers=a.workers,rows=[],
                  authored_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  mechanism_source_sha256=sha256((a.code/'alternative_producer_clones.py').read_bytes()).hexdigest(),
                  scope='Changed actual source-coefficient partitions and paid whole-controller clones; full matrix profiles are separate')
    with ProcessPoolExecutor(max_workers=a.workers,mp_context=multiprocessing.get_context('fork'))as pool:
        futures=[pool.submit(evaluate,t)for t in tasks]
        for future in as_completed(futures):
            r=future.result();summary={k:r[k]for k in ['status','case_id','producer','initial_roles','role_saving','seconds','error']if k in r}
            summary['full_result']=str(a.work/'raw'/f'{r["case_id"]}.json')
            protocol['rows'].append(summary)
            (a.work/'results.json').write_text(json.dumps(protocol,indent=2)+'\n')
            print(json.dumps({k:summary.get(k)for k in ['case_id','status','role_saving','seconds','error']}),flush=True)
    protocol.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    (a.work/'results.json').write_text(json.dumps(protocol,indent=2)+'\n')

if __name__=='__main__':main()
