#!/usr/bin/env python3
"""One bounded CPU lane for distinct preconfigured scientific commands."""
import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from time import perf_counter

parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--output',required=True)
args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
env=os.environ.copy()
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:env[name]='1'
rows=[]
for i,job in enumerate(json.loads(Path(args.config).read_text())):
    started=perf_counter();utc=datetime.now(timezone.utc).isoformat()
    with (out/f'job-{i}.log').open('wb') as log:
        child=subprocess.Popen(job['command'],env=env,stdout=log,stderr=subprocess.STDOUT)
        print(json.dumps({'event':'start','job_id':job['id'],'pid':child.pid,'utc':utc}),flush=True)
        returncode=child.wait()
    row={'job':job,'start_utc':utc,'end_utc':datetime.now(timezone.utc).isoformat(),
         'returncode':returncode,'seconds':perf_counter()-started,
         'status':'completed command' if returncode==0 else 'failed command retained',
         'log':f'job-{i}.log'}
    (out/f'job-{i}.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
    print(json.dumps({'event':'done','job_id':job['id'],'returncode':returncode,'seconds':row['seconds']}),flush=True)
(out/'certificate.json').write_text(json.dumps({'rows':rows,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
