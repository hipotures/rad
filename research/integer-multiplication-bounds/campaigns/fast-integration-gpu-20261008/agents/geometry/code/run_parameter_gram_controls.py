#!/usr/bin/env python3
"""Independent Gram controls on changed rational-beta physical matrices."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,time
from refresh_geometry_status import refresh

p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
p.add_argument('--output',type=Path,required=True);p.add_argument('--live-output',type=Path);a=p.parse_args()
assert not a.work.exists() and not a.output.exists();a.work.mkdir(parents=True);rows=[];start=time.monotonic();configs=json.loads(a.input.read_text())
for c in configs:
    case=a.work/c['case_id'];case.mkdir();receipt=case/'receipt.json'
    command=[sys.executable,'-u',str(Path(__file__).with_name('review_positive_physical_profiles.py')),'--witness',c['witness'],'--samples','12','--output',str(receipt)]
    with (case/'run.log').open('wb') as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        (case/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
        assert child.wait()==0,c
    d=json.loads(receipt.read_text());rows.append(dict(case_id=c['case_id'],h=d['h'],basis=d['basis'],status=d['status'],checks=len(d['checks']),receipt=str(receipt),receipt_sha256=sha256(receipt.read_bytes()).hexdigest()))
    status=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(rows),total=len(configs),workers=1,elapsed_seconds=time.monotonic()-start)
    (a.work/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
    if a.live_output:refresh(a.work,a.live_output,'Continue1088 mapped-center exact cases; next generic-beta SSP controller matching')
a.output.write_text(json.dumps(dict(status='PASS INDEPENDENT RATIONAL-BETA GRAM AND PROFILE CONTROLS',rows=rows,completed_utc=datetime.now(timezone.utc).isoformat(),
               elapsed_seconds=time.monotonic()-start,input_sha256=sha256(a.input.read_bytes()).hexdigest(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
