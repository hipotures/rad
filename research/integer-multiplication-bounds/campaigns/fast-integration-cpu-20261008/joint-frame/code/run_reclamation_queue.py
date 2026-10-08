#!/usr/bin/env python3
"""One bounded worker exploring distinct paid retired-carrier schedules."""
import argparse
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import subprocess,sys


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=(23,25))
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--wait-for-result',type=Path)
    args=ap.parse_args();assert not args.output.exists()
    args.output.mkdir(parents=True)
    script=Path(__file__).with_name('reclamation_order_family.py').resolve()
    config=Path(__file__).resolve().parents[1]/'configs/reclamation-fixed-dag.json'
    jobs=[dict(policy=p,seed=s) for p,s in [('seeded',7),('seeded',29),('seeded',43),('seeded',79),('seeded',101),('seeded',131),('seeded',173),('seeded',251)]]
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,jobs=jobs,
                  source_commit='bc2f7ed4c20dc18898305ab17165c0c995cbb804',
                  driver_source=script.read_text(),driver_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                  config=json.loads(config.read_text()),threads=1,
                  scope='Original pinned scalar graph; distinct deterministic high-rank tie schedules, full dirty word/frame/moment checks. No optimality claim.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    for index,job in enumerate(jobs):
        out=args.output/('job%02d'%index)
        cmd=[sys.executable,'-B',str(script),'--source-root',str(args.source_root),'--dimension',str(args.h),
             '--retired-policy',job['policy'],'--order-seed',str(job['seed']),
             '--config',str(config),'--output',str(out)]
        subprocess.run(cmd,check=True,env=env)
        print(json.dumps(dict(event='reclamation_queue_completed',h=args.h,index=index,job=job)),flush=True)
    (args.output/'complete.json').write_text(json.dumps(dict(status='COMPLETE',jobs=len(jobs)))+'\n')


if __name__=='__main__':main()
