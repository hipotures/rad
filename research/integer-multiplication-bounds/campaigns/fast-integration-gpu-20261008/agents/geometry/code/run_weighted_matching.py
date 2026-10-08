#!/usr/bin/env python3
"""Bounded matching discovery followed by complete exact local profiling.

Each task has fresh storage and stable input hashes. Native workers are single
threaded; the requested worker count is the CPU allocation for this batch.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import shutil
import subprocess
import time


def worker(task, matcher, profiler, root):
    started = time.monotonic()
    case = root/task['case_id']
    case.mkdir(parents=True, exist_ok=False)
    source = Path(task['dag_path'])
    assert sha256(source.read_bytes()).hexdigest() == task['dag_sha256']
    dag = case/'dag.bin'
    shutil.copy2(source, dag)
    prefix = case/'weighted'
    commands = [[str(matcher), str(dag), str(task['seed']), str(task['mode']), str(prefix)],
                [str(profiler), str(dag), str(prefix)+'.exact.links',
                 str(prefix)+'.exact.uses.json', str(prefix)+'.uses.bin']]
    pids = []
    for index, command in enumerate(commands):
        with (case/f'phase-{index}.stdout.json').open('w') as out, (case/f'phase-{index}.stderr.log').open('w') as err:
            process = subprocess.Popen(command, stdout=out, stderr=err)
            pids.append(process.pid)
            code = process.wait(timeout=180)
        if code:
            return dict(configuration=task, status='failed', exit_code=code, phase=index, pids=pids, commands=commands)
    producer = json.loads((case/'phase-1.stdout.json').read_text())
    profile = json.loads(Path(str(dag)+'.round3_rankone_certified_profiles.json').read_text())
    result = dict(configuration=task, status='complete exact local profile', pids=pids,
                  elapsed_seconds=time.monotonic()-started, commands=commands,
                  producer=producer, fixed_profile=profile,
                  discovery=json.loads((case/'phase-0.stdout.json').read_text()),
                  local_phi=sum(c*w*math.expm1(4e-5*math.log(575/w)) for w, c in enumerate(profile['blocks']) if w),
                  dag_path=str(dag), dag_sha256=task['dag_sha256'],
                  witness_path=str(prefix)+'.exact.uses.json',
                  witness_sha256=sha256(Path(str(prefix)+'.exact.uses.json').read_bytes()).hexdigest())
    (case/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--matcher', type=Path, required=True)
    ap.add_argument('--profiler', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--workers', type=int, required=True)
    args = ap.parse_args()
    assert 1 <= args.workers <= 6 and not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    tasks = json.loads(args.input.read_text())
    assert len(set(t['case_id'] for t in tasks)) == len(tasks)
    result = dict(started_utc=datetime.now(timezone.utc).isoformat(),
                  input_sha256=sha256(args.input.read_bytes()).hexdigest(),
                  executable_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in (args.matcher, args.profiler)},
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  workers=args.workers, tasks=len(tasks), rows=[])
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(worker, task, args.matcher, args.profiler, args.work) for task in tasks]
        for future in as_completed(futures):
            row = future.result()
            result['rows'].append(row)
            temporary = args.output.with_suffix('.tmp')
            temporary.write_text(json.dumps(result, indent=2)+'\n')
            temporary.replace(args.output)
            print(json.dumps(dict(case_id=row['configuration']['case_id'], status=row['status'],
                                  pids=row['pids'], elapsed_seconds=row.get('elapsed_seconds'), local_phi=row.get('local_phi'))), flush=True)
    result.update(status='complete', completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
