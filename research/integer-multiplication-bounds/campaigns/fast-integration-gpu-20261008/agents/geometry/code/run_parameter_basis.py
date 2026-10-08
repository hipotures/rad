#!/usr/bin/env python3
"""Bounded I+tJ discovery at rational roots of actual envelope entries.

Changing t changes source geometry and coefficient bounds. Outputs are modular
discovery profiles; neither the old fixed-basis bounds nor its complete source
pair nonvanishing certificate is applied to these changed parameters.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import argparse
import json
import math
import shutil
import subprocess
import time


def exceptional_parameters(h):
    counts = Counter()
    bad = {Q(0),Q(-1,h),Q(-1,3),Q(-1,9),Q(-2,3*h-9),Q(-2,3*(h-3)),
           Q(-(h-7),3*(h-3)),Q(-2,3*(h-1))}
    for c in (1,2):
        s = 3-c
        for n in range(1,h-c+1):
            d = s*s+(c-1)*n
            for oi,ci in ((0,1),(1,0),(0,0)):
                for oj,cj in ((0,1),(1,0),(0,0)):
                    for diagonal in (0,1):
                        if diagonal and (oi,ci)!=(oj,cj):
                            continue
                        A = 3*d*diagonal*oi+3*s*oi*cj+3*s*ci*oj+3*n*ci*cj-3*(c-1)*oi*oj-s*oi-n*ci
                        B = h*A+3*(3*s*oj+3*n*cj-n)-(9-h)*(s*oi+n*ci)
                        C = 9*(h*(s*oj+n*cj)-3*n)
                        roots = []
                        if C:
                            discriminant = B*B-4*A*C
                            if discriminant >= 0 and isqrt(discriminant)**2 == discriminant:
                                roots = [Q(-B+isqrt(discriminant),2*C),Q(-B-isqrt(discriminant),2*C)]
                        elif B:
                            roots = [Q(-A,B)]
                        for t in set(roots)-bad:
                            counts[t] += 1
    return [(Q(1),0)]+counts.most_common()


def worker(task, executable, work):
    start = time.monotonic()
    directory = work/task['case_id']
    directory.mkdir(exist_ok=False)
    source = Path(task['dag_path'])
    selected = Path(task['selected_binary'])
    assert sha256(source.read_bytes()).hexdigest() == task['dag_sha256']
    assert sha256(selected.read_bytes()).hexdigest() == task['selected_sha256']
    dag = directory/'dag.bin'
    shutil.copy2(source,dag)
    command = [str(executable), str(dag), str(directory/'links.bin'), str(directory/'uses.json'),
               str(selected), str(task['numerator']), str(task['denominator'])]
    with (directory/'stdout.json').open('w') as out, (directory/'stderr.log').open('w') as err:
        process = subprocess.Popen(command,stdout=out,stderr=err)
        code = process.wait(timeout=180)
    result = dict(configuration=task,pid=process.pid,exit_code=code,command=command,
                  elapsed_seconds=time.monotonic()-start,status='failed native discovery' if code else 'modular discovery only')
    if code == 0:
        profile = json.loads(Path(str(dag)+'.parameter_basis_discovery_profiles.json').read_text())
        result.update(profile=profile, local_phi=sum(c*w*math.expm1(4e-5*math.log(575/w)) for w,c in enumerate(profile['blocks']) if w))
    (directory/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--executable',type=Path,required=True)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--workers',type=int,required=True)
    args = ap.parse_args()
    assert not args.work.exists() and not args.output.exists() and 1 <= args.workers <= 6
    args.work.mkdir(parents=True)
    tasks = []
    for source in json.loads(args.input.read_text()):
        h = source['h']
        for t, multiplicity in exceptional_parameters(h):
            task = dict(source,numerator=t.numerator,denominator=t.denominator,entry_root_occurrences=multiplicity,
                        case_id=f'h{h}-t{t.numerator}-over-{t.denominator}')
            tasks.append(task)
    result = dict(started_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,tasks=len(tasks),
                  status='running discovery', source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  executable_sha256=sha256(args.executable.read_bytes()).hexdigest(), rows=[],
                  limitations=['Changed rational-minor bounds are not yet applied',
                               'Changed full source-pair nonvanishing has not been certified',
                               'Only rational roots of individual envelope entries are screened'])
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker,t,args.executable,args.work) for t in tasks]
        for future in as_completed(futures):
            row = future.result()
            result['rows'].append(row)
            temporary = args.output.with_suffix('.tmp')
            temporary.write_text(json.dumps(result,indent=2)+'\n')
            temporary.replace(args.output)
            print(json.dumps(dict(case_id=row['configuration']['case_id'],status=row['status'],pid=row['pid'],
                                  local_phi=row.get('local_phi'),elapsed_seconds=row['elapsed_seconds'])),flush=True)
    result.update(status='complete discovery',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
