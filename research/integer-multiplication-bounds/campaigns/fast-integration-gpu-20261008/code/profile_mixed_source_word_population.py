#!/usr/bin/env python3
"""Bounded exact CRT population for independently reconstructed mixed words.

Different bases are discovery profiles until compatible complete DATA is proved.
Credits: Avi Eisenberg, eumemic and inherited source/frame contributors.
Authored with OpenAI Codex assistance.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--receipts', type=Path, nargs='+', required=True)
    p.add_argument('--native', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--workers', type=int, default=3)
    p.add_argument('--selected-data-bases', action='store_true',
                   help='Close existing networks only at the proven 1/15 and -1/15 DATA bases.')
    a = p.parse_args()
    assert 1 <= a.workers <= 3 and not a.output.exists()
    a.work.mkdir(parents=True, exist_ok=False)
    jobs, seen = [], set()
    for receipt in a.receipts:
        for source in json.loads(receipt.read_text())['rows']:
            r = source['independent']
            binary = Path(r['transition_path'])
            assert binary.read_bytes()[:8] == b'RADCOF01'
            assert sha(binary) == r['transition_sha256']
            bases = ['beta:1:15', 'beta:-1:12'] if r['h'] == 23 else [
                'beta:7:207', 'beta:-1:15', 'beta:1:15', 'beta:1:2']
            if a.selected_data_bases:
                bases = ['beta:1:15' if r['h'] == 23 else 'beta:-1:15']
            for basis in bases:
                key = (r['transition_sha256'], basis)
                if key in seen:
                    continue
                seen.add(key)
                jobs.append(dict(case_id=source['case_id'] + '-' + basis.replace(':', '-'),
                                 source_receipt=str(receipt), source_receipt_sha256=sha(receipt),
                                 word_sha256=r['word_sha256'], binary=str(binary),
                                 input_binary_sha256=r['transition_sha256'], basis=basis,
                                 coordinate_order=r['source_permutation']))

    def run(job):
        work = a.work / job['case_id']
        work.mkdir()
        profile, audit = work / 'profile.json', work / 'audit.json'
        command = [str(a.native), job['binary'], job['basis'], str(profile), str(audit)]
        with (work / 'native.log').open('w') as log:
            child = subprocess.Popen(command, stdout=log, stderr=log)
            print(json.dumps(dict(event='LAUNCHED', pid=child.pid, command=command)), flush=True)
            code = child.wait()
        result = dict(**job, returncode=code, profile_path=str(profile),
                      transition_audit=str(audit), command=command)
        if code == 0:
            result.update(profile=json.loads(profile.read_text()),
                          profile_sha256=sha(profile), transition_audit_sha256=sha(audit))
        else:
            result['failure_tail'] = (work / 'native.log').read_text()[-2000:]
        return result

    rows = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        pending = [pool.submit(run, job) for job in jobs]
        for future in as_completed(pending):
            row = future.result()
            rows.append(row)
            result = dict(status='RUNNING' if len(rows) < len(jobs) else 'COMPLETE',
                          utc=datetime.now(timezone.utc).isoformat(),
                          completed=len(rows), total=len(jobs), workers=a.workers,
                          rows=rows, native_sha256=sha(a.native),
                          native_source_sha256=sha(Path(__file__).with_name('mixed_coframe_word_profiles.cpp')),
                          driver_sha256=sha(__file__),
                          scope='Exact executed mixed-word local profiles; source/DATA/stock/assembly acceptance remains separate.')
            a.output.write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps(dict(event='COMPLETED', case_id=row['case_id'],
                                  returncode=row['returncode'], completed=len(rows),
                                  total=len(jobs))), flush=True)


if __name__ == '__main__':
    main()
