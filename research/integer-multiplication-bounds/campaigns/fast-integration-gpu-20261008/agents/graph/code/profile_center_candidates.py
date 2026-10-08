#!/usr/bin/env python3
"""Score new center DAGs using geometry's actual signed-frame CRT profiler.

The matrix profiler is an independently authored sibling campaign input.
This driver changes graph inputs, records source versions and includes the
exterior cost of actual paid roles. It does not certify a full exponent.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import subprocess
import sys
from producer_search import digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cohort',type=Path,nargs='+',required=True)
    p.add_argument('--geometry-code',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=1)
    a=p.parse_args();assert not a.work.exists()and not a.output.exists();a.work.mkdir(parents=True)
    sys.path.insert(0,str(a.geometry_code));from run_positive_profiles import run
    builds=a.work/'builds';builds.mkdir();binary=builds/'positive_frame_profiles'
    source=a.geometry_code/'positive_frame_profiles.cpp'
    source_hash=digest(source)
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True)
    assert digest(source)==source_hash
    jobs=[];seen=set()
    for cohort in a.cohort:
        for row in json.loads(cohort.read_text())['rows']:
            if not row.get('producer')or row.get('status')=='failed':continue
            producer=row['producer'];key=(producer['dag_sha256'],producer['positive_sha256'],producer['witness_sha256'])
            if key in seen:continue
            seen.add(key);case=row['case_id'];witness=Path(producer['dag_path']).parent/'result.json'
            jobs.append((case,witness))
    result=dict(status='running',command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),
                total_cases=len(jobs),rows=[],failures=[],source_sha256={
                    'driver':digest(__file__),'geometry_profile_cpp':source_hash,
                    'geometry_profile_driver':digest(a.geometry_code/'run_positive_profiles.py'),
                    'geometry_binary_io':digest(a.geometry_code/'binary_io.hpp')})
    def execute(job):
        case,witness=job;target=a.work/case;out=a.work/f'{case}.profile.json'
        run(witness,binary,'negative',target,out)
        retained=json.loads(out.read_text());h=retained['producer']['h'];R=retained['producer']['R'];alpha=retained['local_phi']['alpha']
        exterior=sum(t*math.expm1(alpha*math.log(575/t))for t in(h,575-2*h))
        return dict(case_id=case,h=h,R=R,local_phi=retained['local_phi']['value'],
                    complete_axis_excess=retained['local_phi']['value']+R*exterior,
                    retained_witness=str(out),retained_witness_sha256=digest(out),
                    dag_sha256=retained['producer']['dag_sha256'],positive_sha256=retained['producer']['positive_sha256'])
    with ThreadPoolExecutor(max_workers=a.workers)as pool:
        futures={pool.submit(execute,job):job for job in jobs}
        for future in as_completed(futures):
            try:row=future.result();result['rows'].append(row);print(json.dumps(row),flush=True)
            except Exception as error:result['failures'].append(dict(job=futures[future],error=repr(error)))
            tmp=a.output.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');tmp.replace(a.output)
    result.update(status='complete'if not result['failures']else'complete with failures',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
