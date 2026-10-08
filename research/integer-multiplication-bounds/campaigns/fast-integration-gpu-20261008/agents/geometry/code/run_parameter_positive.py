#!/usr/bin/env python3
"""Finite rational-beta actual-profile triage; every new data family stays pending."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,math,time
from run_positive_profiles import run
from refresh_geometry_status import refresh

ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--binary',type=Path,required=True)
ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--live-output',type=Path)
a=ap.parse_args();assert not a.work.exists() and not a.output.exists();a.work.mkdir(parents=True)
configs=json.loads(a.input.read_text());start=time.monotonic();rows=[]
for config in configs:
    witness=Path(config['witness']);case=config['case_id'];out=a.work/f'{case}.json'
    binary=Path(config['binary']) if 'binary' in config else a.binary
    run(witness,binary,config['basis'],a.work/case,out)
    document=json.loads(out.read_text());original=json.loads(witness.read_text());h=document['producer']['h']
    if config.get('expected_same_histogram'):assert document['copied_blocks']==original['copied_blocks']
    document['configuration'].update(data_status=config.get('data_status','Changed source weights; complete all-source data certificate required'),parameter=config)
    out.write_text(json.dumps(document,indent=2)+'\n');alpha=document['local_phi']['alpha']
    exterior=h*math.expm1(alpha*math.log(575/h))+(575-2*h)*math.expm1(alpha*math.log(575/(575-2*h)))
    rows.append(dict(case_id=case,h=h,basis=config['basis'],R=document['producer']['R'],local_phi=document['local_phi']['value'],
                     complete_axis_phi=document['local_phi']['value']+document['producer']['R']*exterior,
                     profile=document['fixed_profile'],retained_witness=str(out),witness_sha256=sha256(out.read_bytes()).hexdigest(),
                     expected_same_histogram=config.get('expected_same_histogram',False),data_status=document['configuration']['data_status']))
    status=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(rows),total=len(configs),workers=1,elapsed_seconds=time.monotonic()-start)
    (a.work/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
    if a.live_output:refresh(a.work,a.live_output,'Continue1088 mapped-center profiles; exact rational-beta matching and independent Gram controls next')
result=dict(status='COMPLETE EXACT LOCAL RATIONAL-BETA TRIAGE',completed_utc=datetime.now(timezone.utc).isoformat(),rows=rows,
            input_sha256=sha256(a.input.read_bytes()).hexdigest(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-start)
a.output.write_text(json.dumps(result,indent=2)+'\n')
