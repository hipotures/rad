#!/usr/bin/env python3
"""Distinct actual signed-frame profiles; originals, frames and maps stay pinned."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,math,time
from run_positive_profiles import run


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--binary',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--workers',type=int,required=True);ap.add_argument('--bases',nargs='+',choices=['negative','fixed','negative-transpose','fixed-transpose'],default=['negative'])
    ap.add_argument('--dimensions',nargs='+',type=int);ap.add_argument('--skip',type=Path)
    ap.add_argument('--live-output',type=Path)
    a=ap.parse_args();assert 1<=a.workers<=6 and not a.work.exists() and not a.output.exists();a.work.mkdir(parents=True)
    original=json.loads(a.input.read_text());rows=original['rows'] if isinstance(original,dict) else original
    skipped=set()
    if a.skip:
        previous=json.loads(a.skip.read_text())
        for row in previous['rows']:skipped.add(tuple(row['input_sha256']))
    unique={}
    for row in rows:
        if row.get('status')=='failed' or not row.get('producer'):continue
        p=row['producer'];key=(p['dag_sha256'],p['positive_sha256'],p['witness_sha256'])
        if a.dimensions and p['h'] not in a.dimensions:continue
        if key in skipped:continue
        unique.setdefault(key,row)
    tasks=[]
    for index,(key,row) in enumerate(unique.items()):
        witness=a.work/f'input-{index:03d}.json';witness.write_text(json.dumps(row)+'\n')
        for basis in a.bases:tasks.append((index,row,basis,witness))
    started=datetime.now(timezone.utc).isoformat();begin=time.monotonic();completed=[];failures=[]
    def job(task):
        index,row,basis,witness=task;case=f'{basis}-h{row["producer"]["h"]}-{index:03d}'
        output=a.work/f'{case}.json';run(witness,a.binary,basis,a.work/case,output)
        retained=json.loads(output.read_text());p=retained['producer'];profile=retained['fixed_profile'];phi=retained['local_phi']['value']
        alpha=retained['local_phi']['alpha'];h=p['h'];exterior=h*math.expm1(alpha*math.log(575/h))+(575-2*h)*math.expm1(alpha*math.log(575/(575-2*h)))
        return dict(case_id=case,source_case_id=row.get('case_id'),h=h,basis=basis,R=p['R'],local_phi=phi,
                    complete_axis_phi=phi+p['R']*exterior,profile=profile,retained_witness=str(output),
                    input_sha256=[row['producer'][k] for k in ('dag_sha256','positive_sha256','witness_sha256')],witness_sha256=sha256(output.read_bytes()).hexdigest())
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        submitted={pool.submit(job,t):t for t in tasks}
        for future in as_completed(submitted):
            task=submitted[future]
            try:completed.append(future.result())
            except Exception as error:failures.append(dict(index=task[0],basis=task[2],error=repr(error)))
            status=dict(utc=datetime.now(timezone.utc).isoformat(),started_utc=started,completed=len(completed),failed=len(failures),total=len(tasks),
                        elapsed_seconds=time.monotonic()-begin,workers=a.workers)
            (a.work/'status.json').write_text(json.dumps(status,indent=2)+'\n');print(json.dumps(status),flush=True)
            if a.live_output:
                from refresh_geometry_status import refresh
                refresh(a.work,a.live_output,'Global weighted-positive matching components, then selected new-center CRT and literal compiler gates')
    result=dict(status='COMPLETE' if not failures else 'COMPLETE WITH FAILURES',started_utc=started,
                completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-begin,
                distinct_inputs=len(unique),input_rows=len(rows),bases=a.bases,workers=a.workers,
                source_input=str(a.input),source_input_sha256=sha256(a.input.read_bytes()).hexdigest(),
                authored_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),rows=completed,failures=failures)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','elapsed_seconds','distinct_inputs','bases')}),flush=True)
