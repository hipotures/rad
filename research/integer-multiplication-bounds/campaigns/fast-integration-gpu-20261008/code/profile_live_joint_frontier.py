#!/usr/bin/env python3
"""Replenish exact physical-word/basis experiments from completed live receipts.

Only completed independently replayed words enter the bounded queue. Frozen
transition bytes and rational basis identify a case. Failed native checks are
retained. This is discovery, never automatic conditional acceptance.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'agents/geometry/code'))
from signature_signed_word_spaces import signature


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs', type=Path, nargs='+', required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--original-native', type=Path, required=True)
    p.add_argument('--signed-native', type=Path, required=True)
    p.add_argument('--exclude-results', type=Path, nargs='*', default=[])
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--slot-limit-file', type=Path)
    a = p.parse_args()
    assert not a.work.exists()
    a.work.mkdir(parents=True)
    assert 1 <= a.workers <= 3
    seen, hashes, active, results = set(), {}, {}, []
    canonical_cache, space_seen, aliases, alias_seen = {}, set(), [], set()
    def digest(path):
        key = str(path)
        if key not in hashes:
            hashes[key] = sha256(Path(path).read_bytes()).hexdigest()
        return hashes[key]
    def space_key(h, path, basis):
        fingerprint = digest(path)
        if fingerprint not in canonical_cache:
            canonical_cache[fingerprint] = signature(path)['canonical_signature_sha256']
        return h, canonical_cache[fingerprint], basis
    for file in a.exclude_results:
        for row in json.loads(file.read_text()).get('rows', []):
            cfg = row.get('config', {})
            if cfg.get('transitions') and cfg.get('basis') and row.get('profile'):
                seen.add((row['profile']['h'], digest(cfg['transitions']), cfg['basis']))
                if str(cfg['transitions']).endswith('signed-transitions.bin'):
                    space_seen.add(space_key(row['profile']['h'], cfg['transitions'], cfg['basis']))
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    def run(case):
        h, fingerprint, basis, binary, native, source = case
        directory = a.work/f'h{h}-{fingerprint[:16]}-{basis.replace(":", "_")}'
        directory.mkdir()
        command = [str(native), str(binary), basis, str(directory/'profile.json'), str(directory/'matrix-audit.json')]
        with (directory/'run.log').open('wb') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
            launch = dict(pid=child.pid, command=command, source_receipt=str(source), input_binary_sha256=fingerprint,
                          utc=datetime.now(timezone.utc).isoformat())
            (directory/'process.json').write_text(json.dumps(launch, indent=2)+'\n')
            print(json.dumps(dict(stage='EXACT ACTUAL WORD/BASIS RUNNING', **launch)), flush=True)
            code = child.wait()
        row = dict(status='EXACT DISCOVERY PROFILE' if code == 0 else 'REJECTED NATIVE CHECK', exit_code=code,
                   source_receipt=str(source), config=dict(h=h,basis=basis,transitions=str(binary)),
                   input_binary_sha256=fingerprint, profile_path=str(directory/'profile.json'),
                   transition_audit=str(directory/'matrix-audit.json'))
        if code == 0:
            row['profile'] = json.loads((directory/'profile.json').read_text())
            row['profile_sha256'] = digest(directory/'profile.json')
            row['transition_audit_sha256'] = digest(directory/'matrix-audit.json')
        (directory/'receipt.json').write_text(json.dumps(row, indent=2)+'\n')
        return row
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        while True:
            for future in list(active):
                if future.done():
                    try:
                        results.append(future.result())
                    except Exception as error:
                        case = active[future]
                        results.append(dict(status='REJECTED ORCHESTRATION CHECK', exit_code=-1,
                                            source_receipt=str(case[5]),
                                            config=dict(h=case[0],basis=case[2],transitions=str(case[3])),
                                            input_binary_sha256=case[1],
                                            error_type=type(error).__name__,error=str(error)))
                    del active[future]
            pending = {}
            # Earlier inputs receive priority; new signed structures precede
            # the remaining independently replayed Gaussian control words.
            for root in a.inputs:
                for file in sorted(root.glob('raw/*/result.json')):
                    try:
                        row = json.loads(file.read_text())
                        g = row['independent']; h = row['compiled']['h']
                        if not g['status'].endswith('PASS'):
                            continue
                        binary = Path(g['transition_path'])
                        fingerprint = digest(binary)
                        native = a.signed_native if g['frame_format'] == 'positive-signed-v1' else a.original_native
                        bases = ['beta:1:15','beta:169:261','beta:1:51'] if h == 23 else ['beta:1:21','beta:75:131','beta:7:207']
                        for basis in bases:
                            key = (h,fingerprint,basis)
                            if key not in seen:
                                if g['frame_format'] == 'positive-signed-v1':
                                    canonical_key = space_key(h, binary, basis)
                                    if canonical_key in space_seen:
                                        if key not in alias_seen:
                                            alias_seen.add(key)
                                            aliases.append(dict(status='SKIPPED EQUAL PROJECTOR TRANSITION MULTISET',
                                                                h=h, basis=basis, binary_sha256=fingerprint,
                                                                canonical_signature=canonical_key[1],
                                                                source_receipt=str(file)))
                                        continue
                                pending.setdefault(key, (h,fingerprint,basis,binary,native,file))
                    except (KeyError, ValueError, OSError):
                        continue  # A partially written receipt is retried.
            slots = a.workers
            if a.slot_limit_file:
                slots = min(slots, max(0, int(a.slot_limit_file.read_text().strip())))
            for case in list(pending.values()):
                if len(active) >= slots:
                    break
                canonical_key = space_key(case[0], case[3], case[2]) if case[4] == a.signed_native else None
                if canonical_key is not None:
                    if canonical_key in space_seen:
                        continue
                    space_seen.add(canonical_key)
                seen.add(case[:3]); active[pool.submit(run,case)] = case
            status = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(results), active=len(active),
                          discovered_pending=len(pending), workers=a.workers, current_slot_limit=slots,
                          skipped_space_aliases=len(aliases), failures=sum(r['exit_code'] != 0 for r in results))
            (a.work/'status.json').write_text(json.dumps(status, indent=2)+'\n')
            (a.work/'results.json').write_text(json.dumps(dict(status='LIVE DISCOVERY QUEUE',rows=results), indent=2)+'\n')
            (a.work/'space-aliases.json').write_text(json.dumps(dict(status='EXACT SPACE-EQUIVALENT DISCOVERY SKIPS',
                                                                 rows=aliases), indent=2)+'\n')
            time.sleep(2)


if __name__ == '__main__':
    main()
