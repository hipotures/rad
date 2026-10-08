#!/usr/bin/env python3
"""Record a failed, no-longer-live coordinator without altering its evidence.

This specific recovery creates the missing terminal summary of the individually
bounded 065400 complex option attempt. The original coordinator/checkpoint and
every completed witness remain unchanged. The terminal record also releases a
stale predecessor allocation in the fresh dynamic continuation.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path


def identity(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=sha256(raw).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', type=Path, required=True)
    parser.add_argument('--calibration', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True)
    args = parser.parse_args()
    checkpoint = json.loads((args.attempt/'checkpoint.json').read_text())
    protocol = json.loads((args.attempt/'protocol.json').read_text())
    assert not (args.attempt/'summary.json').exists()
    recorded_pids = set(checkpoint.get('active_worker_pids', []))
    recorded_pids.add(checkpoint['dispatcher_pid'])
    live = [pid for pid in recorded_pids if Path(f'/proc/{pid}').exists()]
    assert not live, ('Recorded attempt processes remain live', live)
    cleanup = args.calibration/'guarded-cleanup'/'guarded-stop.json'
    assert cleanup.exists()
    rows = []
    best = {}
    for path in sorted((args.attempt/'cases').glob('*.json')):
        assert '.error.' not in path.name
        row = json.loads(path.read_text())
        assert row['candidate_id'] == path.stem
        assert 'compiled_roles' in row and 'checked' in row and 'guard' in row
        rows.append(dict(identity(path), candidate_id=row['candidate_id'],
                         h=row['h'], compiled_roles=row['compiled_roles'],
                         configuration=row['complex_option_configuration']))
        if row['h'] not in best or row['compiled_roles'] < best[row['h']]['compiled_roles']:
            best[row['h']] = rows[-1]
    planned = len(protocol['candidate_definitions'])
    submitted = checkpoint['submitted_candidates']
    assert len(rows) == checkpoint['completed_candidates'] == 32
    record = dict(
        status='Terminal PARTIAL: wrapper FAILED; 32 complete scientific witnesses preserved',
        record_kind='Fresh postmortem summary; original coordinator emitted no terminal summary',
        created_utc=datetime.now(timezone.utc).isoformat(),
        recovery_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scientific_completed_candidates=len(rows), completed_candidates=len(rows),
        planned_candidates=planned, submitted_candidates=submitted,
        bounded_native_attempts=submitted-len(rows), not_submitted_candidates=planned-submitted,
        active_capacity=0, active_worker_pids=[],
        original_wrapper_exit_code=1,
        wrapper_failure='JSONDecodeError while reading predecessor checkpoint concurrently with its terminal update',
        scientific_failure='No returned candidate from the bounded native HiGHS symmetry preprocessing attempts; no completed scalar or phase failure',
        preservation='Original protocol, stale checkpoint, completed case bytes and native failure logs remain unchanged',
        original_protocol=identity(args.attempt/'protocol.json'),
        original_checkpoint=identity(args.attempt/'checkpoint.json'),
        guarded_cleanup=identity(cleanup),
        best_by_ground={str(h): row for h,row in sorted(best.items())},
        all_terminal_candidates=rows,
        successor_admission='All originally recorded PIDs are absent; this new terminal record deducts zero predecessor workers')
    args.record.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(record, indent=2, sort_keys=True)+'\n').encode()
    assert not args.record.exists()
    args.record.write_bytes(raw)
    destination = args.attempt/'summary.json'
    temporary = destination.with_suffix('.postmortem.tmp')
    temporary.write_bytes(raw)
    os.replace(temporary, destination)
    print(json.dumps(dict(status=record['status'], completed=len(rows),
                          new_summary_sha256=sha256(raw).hexdigest(),
                          successor_predecessor_workers=0)))


if __name__ == '__main__':
    main()
