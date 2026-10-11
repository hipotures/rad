#!/usr/bin/env python3
"""Profile distinct independently replayed interval joint-compiler words.

The public extractor reconstructs transitions from literal XOR operations and
checks the auxiliary event list. The native rational profiler then certifies
ordered northeast ranks. Candidate arithmetic remains a separate gate.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--case-glob', default='h*/result.json')
    parser.add_argument('--exclude-results', type=Path, nargs='*', default=[],
                        help='Completed exact profiles to exclude before launching any work.')
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    assert 1 <= args.workers <= 3
    args.work.mkdir(parents=True)
    selected = {}
    completed = set()
    for previous in args.exclude_results:
        completed.update((r['h'], r['word_sha256'])
                         for r in json.loads(previous.read_text())['rows']
                         if r.get('status') == 'EXACT WORD PROFILE')
    for path in sorted(args.input.glob(args.case_glob)):
        row = json.loads(path.read_text())
        if 'word_sha256' not in row:
            continue  # Duplicate-assignment receipts contain no new word.
        if 'h' not in row:
            row['h'] = row['compiled']['h']
            row['word'] = row['word_path']
        if row.get('configuration', {}).get('kind', 'original') != 'original':
            continue
        key = (row['h'], row['word_sha256'])
        if key not in completed:
            selected.setdefault(key, (path, row))
    jobs = list(selected.values())
    assert jobs, 'No compatible word inputs found; an empty queue is not an experiment.'
    (args.work/'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv), indent=2)+'\n')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    def execute(job):
        path, row = job
        work = args.work/f"h{row['h']}-{row['word_sha256'][:16]}"
        work.mkdir()
        transitions = work/'transitions.bin'
        prepare = [sys.executable, '-B', str(args.source/'scripts/experiments/binary_frame_profile_prepare.py'), row['word'], str(transitions)]
        native = [str(args.binary), str(transitions), 'beta:-1:1', str(work/'profile.json'), str(work/'matrix-audit.json')]
        for label, command in [('prepare', prepare), ('profile', native)]:
            with (work/(label+'.log')).open('wb') as log:
                child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
                (work/'process.json').write_text(json.dumps(dict(pid=child.pid, command=command, stage=label), indent=2)+'\n')
                print(json.dumps(dict(stage=label, pid=child.pid, command=command)), flush=True)
                rc = child.wait()
            if rc:
                return dict(status='REJECTED', exit_code=rc, stage=label, work=str(work), input=str(path))
        profile = json.loads((work/'profile.json').read_text())
        receipt = dict(status='EXACT WORD PROFILE', input=str(path), word_sha256=row['word_sha256'], h=row['h'],
                       config=dict(case_id=work.name, h=row['h'], basis='beta:-1:1', transitions=str(transitions)),
                       profile=profile, profile_path=str(work/'profile.json'),
                       profile_sha256=sha256((work/'profile.json').read_bytes()).hexdigest(),
                       transition_receipt=json.loads(Path(str(transitions)+'.json').read_text()),
                       input_binary_sha256=sha256(transitions.read_bytes()).hexdigest())
        (work/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
        return receipt
    start = time.monotonic()
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(execute, job) for job in jobs]):
            rows.append(future.result())
            status = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(rows), total=len(jobs), workers=args.workers,
                          elapsed_seconds=time.monotonic()-start, failed=sum(x['status']=='REJECTED' for x in rows))
            (args.work/'status.json').write_text(json.dumps(status, indent=2)+'\n')
            print(json.dumps(status), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='COMPLETE', distinct_words=len(jobs), rows=rows,
        source_revision='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
        driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        native_source_sha256=sha256(Path(__file__).parents[1].joinpath('agents/geometry/code/parameter_joint_word_profiles.cpp').read_bytes()).hexdigest()), indent=2)+'\n')


if __name__ == '__main__':
    main()
