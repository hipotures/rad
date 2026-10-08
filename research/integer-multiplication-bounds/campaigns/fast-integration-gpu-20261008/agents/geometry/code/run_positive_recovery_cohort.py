#!/usr/bin/env python3
"""Sequential source-only replays, reserving exactly one compute slot."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,os,subprocess,sys,time
from refresh_geometry_status import refresh

p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
p.add_argument('--output',type=Path,required=True);p.add_argument('--live-output',type=Path);a=p.parse_args()
assert not a.work.exists() and not a.output.exists();a.work.mkdir(parents=True);rows=[];start=time.monotonic()
for c in json.loads(a.input.read_text()):
    case=a.work/c['case_id'];case.mkdir();receipt=case/'receipt.json'
    command=[sys.executable,'-u',str(Path(__file__).with_name('reproduce_positive_weighted.py')),'--dag',c['dag'],'--expected',c['expected'],
             '--work',str(case/'source-replay'),'--output',str(receipt)]
    with (case/'run.log').open('wb') as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        (case/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
        assert child.wait()==0,c
    result=json.loads(receipt.read_text());rows.append(dict(case_id=c['case_id'],status=result['status'],h=result['h'],basis=result['basis'],mode=result['mode'],
                  scalar_dag_sha256=result['scalar_dag_sha256'],positive_labels_sha256=result['positive_labels_sha256'],selected_map_sha256=result['selected_map_sha256'],
                  receipt=str(receipt),receipt_sha256=sha256(receipt.read_bytes()).hexdigest(),elapsed_seconds=result['elapsed_seconds']))
    status=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(rows),total=len(json.loads(a.input.read_text())),workers=1,elapsed_seconds=time.monotonic()-start)
    (a.work/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
    if a.live_output:refresh(a.work,a.live_output,'Continue mapped-center profiles; next beta1/6 conjugate and generic-beta matching/Gram controls')
result=dict(status='PASS SOURCE-ONLY SELECTED GLOBAL MATCHING REPLAYS',rows=rows,completed_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=time.monotonic()-start,input_sha256=sha256(a.input.read_bytes()).hexdigest(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
a.output.write_text(json.dumps(result,indent=2)+'\n')
