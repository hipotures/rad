#!/usr/bin/env python3
"""Continuously certify distinct actual mixed source-frame words, one slot.

Completed source rows are frozen before launching. Identity is the actual
transition binary SHA256 and basis, not a policy name or frame dimension.
Closed native profiles are discovery evidence until independent geometry,
source/stock, full recurrence and conditional acceptance are closed.
Credits: Avi Eisenberg, eumemic and the directly inherited contributors.
OpenAI Codex assisted implementation and mathematical review.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inputs', type=Path, required=True)
    ap.add_argument('--patterns', nargs='+', required=True)
    ap.add_argument('--native', type=Path, required=True)
    ap.add_argument('--exclude-results', type=Path, nargs='*', default=[])
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--idle-limit', type=int, default=300)
    args = ap.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    native_sha = sha(args.native)
    seen, rows, excluded = set(), [], []
    for path in args.exclude_results:
        for row in json.loads(path.read_text()).get('rows', []):
            if row.get('returncode') == 0:
                seen.add((row['input_binary_sha256'], row['basis']))
    last_work = time.monotonic()

    def save(active=None, closed=False):
        args.output.write_text(json.dumps(dict(
            status='CLOSED IDLE' if closed else 'RUNNING',
            utc=datetime.now(timezone.utc).isoformat(), workers=1,
            completed=len(rows), rows=rows, excluded=excluded,
            active=active, native_sha256=native_sha,
            driver_sha256=sha(__file__),
            scope='Exact actual-word local CRT/NE profiles; full DATA, stock, '
                  'recurrence and conditional acceptance remain separate.'),
            indent=2) + '\n')

    while True:
        jobs = []
        paths = sorted(set(p for pattern in args.patterns
                           for p in args.inputs.glob(pattern)))
        for path in paths:
            try:
                source = json.loads(path.read_text())
            except (OSError, ValueError):
                continue
            for source_row in source.get('rows', []):
                independent = source_row.get('independent', {})
                if not independent or 'PASS' not in independent.get('status', ''):
                    continue
                config = source_row.get('configuration', {})
                # This exact, separately proved policy recreates every
                # original core/cover space, so it supplies no new profile.
                if config.get('policy') == 'oddify' and config.get('threshold') == 4:
                    continue
                binary = Path(independent['transition_path'])
                basis = 'beta:1:15' if independent['h'] == 23 else 'beta:-1:15'
                key = (independent['transition_sha256'], basis)
                if key in seen:
                    continue
                seen.add(key)
                assert binary.read_bytes()[:8] == b'RADCOF01'
                assert sha(binary) == key[0]
                assert source_row['compiled']['complete_dirty_basis_both_orientations']
                assert source_row['compiled']['all_physical_frame_inclusions']
                jobs.append((path, source_row, binary, basis))
        for path, source_row, binary, basis in jobs:
            independent = source_row['independent']
            case_id = source_row['case_id'] + '-' + basis.replace(':', '-')
            work = args.work / case_id
            work.mkdir()
            frozen_source = work / 'source-row.json'
            frozen_source.write_text(json.dumps(source_row, indent=2) + '\n')
            profile, audit = work / 'profile.json', work / 'audit.json'
            command = [str(args.native), str(binary), basis, str(profile), str(audit)]
            job = dict(case_id=case_id, source_receipt=str(path),
                       frozen_source_row=str(frozen_source),
                       frozen_source_row_sha256=sha(frozen_source),
                       word_sha256=independent['word_sha256'], binary=str(binary),
                       input_binary_sha256=independent['transition_sha256'],
                       basis=basis, coordinate_order=independent['source_permutation'],
                       profile_path=str(profile), transition_audit=str(audit), command=command)
            with (work / 'native.log').open('w') as log:
                child = subprocess.Popen(command, stdout=log, stderr=log)
                save(dict(pid=child.pid, **job))
                print(json.dumps(dict(event='LAUNCHED', pid=child.pid,
                                      command=command)), flush=True)
                returncode = child.wait()
            assert sha(args.native) == native_sha
            job['returncode'] = returncode
            if returncode == 0:
                job.update(profile=json.loads(profile.read_text()),
                           profile_sha256=sha(profile), transition_audit_sha256=sha(audit))
            else:
                job['failure_tail'] = (work / 'native.log').read_text()[-2000:]
            rows.append(job)
            save()
            last_work = time.monotonic()
            print(json.dumps(dict(event='COMPLETED', case_id=case_id,
                                  returncode=returncode, completed=len(rows))), flush=True)
        if time.monotonic() - last_work >= args.idle_limit:
            save(closed=True)
            return
        if not jobs:
            time.sleep(5)


if __name__ == '__main__':
    main()
