#!/usr/bin/env python3
"""Fresh, bounded singleton neighborhood around an exact retained-role witness.

The scientific evaluator and immutable local cache are imported unchanged
from singleton_sensitivity.py. This thin queue adds individual common-point
moves, paired moves conditional on the current best, and selected far moves.
It keeps at most max_workers minus the live predecessor batch in flight.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import statistics
import time

from singleton_sensitivity import evaluate, VerifiedLocal, write_json


def identity(h, base, positions):
    value = dict(h=h, base=base, positions=positions,
                 reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
    key = sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return value, key


def neighborhood(anchor, prior):
    h, base, starting = anchor['h'], anchor['base'], anchor['positions']
    assert h >= 8 and h % 2 == 0 and len(starting) == h
    excluded = {job['candidate_id'] for job in prior['candidate_definitions']}
    _, anchor_id = identity(h, base, starting)
    excluded.add(anchor_id)
    excluded.add(identity(h, base, prior['baseline_positions'])[1])
    seen, rows = set(), []

    def append(positions, kind, changed):
        assert all(0 <= p < h//2 for p in positions)
        value, key = identity(h, base, positions)
        if key in excluded or key in seen:
            return
        seen.add(key)
        rows.append(dict(value, candidate_id=key, neighborhood=kind, changed=changed))

    # A single common-point change can break the symmetry of a ground pair.
    # These cases are absent from the predecessor's paired perturbations.
    for common in range(h):
        old = starting[common]
        choices = [old-1, old+1] if old+1 < h//2 else [old-1, old-2]
        for new in choices:
            if new < 0:
                continue
            positions = list(starting); positions[common] = new
            append(positions, 'individual-near', [dict(common=common, old=old, new=new)])

    # These are two changes relative to the predecessor baseline, conditional
    # on retaining the anchor pair's improvement, rather than duplicate jobs.
    for pair in range(h//2):
        a, b = 2*pair, 2*pair+1
        assert starting[a] == starting[b]
        old = starting[a]
        choices = [old-1, old+1] if old+1 < h//2 else [old-1, old-2]
        for new in choices:
            if new < 0:
                continue
            positions = list(starting); positions[a:b+1] = [new, new]
            append(positions, 'paired-near', [dict(common=a, old=old, new=new),
                                             dict(common=b, old=old, new=new)])

    # A three-step backward move screens nonlocal order effects throughout
    # the ground. A middle and first gap are sampled in several separated
    # pairs; their exact identities are retained rather than a score proxy.
    for common in range(h):
        new = max(0, starting[common]-3)
        positions = list(starting); positions[common] = new
        append(positions, 'individual-far-three',
               [dict(common=common, old=starting[common], new=new)])
    selected = sorted(set([0, 1, 2, 3, h//4, h//4+1, h//2, h//2+1, h-2, h-1]))
    for common in selected:
        for new in [h//4, 0]:
            positions = list(starting); positions[common] = new
            append(positions, 'individual-far-control',
                   [dict(common=common, old=starting[common], new=new)])
    assert len(rows) == len(seen) and not seen.intersection(excluded)
    return rows, sorted(excluded)


def predecessor_workers(path, maximum):
    summary = path/'summary.json'
    if summary.exists():
        terminal = json.loads(summary.read_text())
        assert terminal['status'].startswith('Terminal')
        return 0
    checkpoint = json.loads((path/'checkpoint.json').read_text())
    protocol = json.loads((path/'protocol.json').read_text())
    remaining = checkpoint['planned_candidates']-checkpoint['completed_candidates']
    assert 0 <= remaining <= checkpoint['planned_candidates']
    # Completion is observed before the old process's final cleanup, so the
    # terminal summary is required before releasing its last worker slot.
    return max(1, min(int(protocol['settings']['workers']), remaining, maximum))


def phase_statistics(rows):
    names = sorted({name for row in rows for name in row['phase_seconds']})
    return {name:dict(mean_seconds=statistics.mean(row['phase_seconds'][name] for row in rows),
                      median_seconds=statistics.median(row['phase_seconds'][name] for row in rows))
            for name in names} if rows else {}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True)
    ap.add_argument('--anchor', type=Path, required=True)
    ap.add_argument('--predecessor', type=Path, required=True)
    ap.add_argument('--max-workers', type=int, default=16)
    ap.add_argument('--reserved-workers', type=int, default=0)
    ap.add_argument('--reserve-file', type=Path)
    ap.add_argument('--worker-address-space-gib', type=int, default=6)
    ap.add_argument('--deadline', required=True)
    ap.add_argument('--work-root', type=Path, required=True)
    ap.add_argument('--run-dir', type=Path, required=True)
    ap.add_argument('--plan-only', action='store_true')
    args = ap.parse_args()
    assert 1 <= args.max_workers <= 16 and 0 <= args.reserved_workers < args.max_workers
    assert args.worker_address_space_gib >= 1
    assert not args.run_dir.exists(), 'Use a fresh run output path'
    args.run_dir.mkdir(parents=True); (args.run_dir/'cases').mkdir()
    anchor = json.loads(args.anchor.read_text())
    prior = json.loads((args.predecessor/'protocol.json').read_text())
    jobs, excluded = neighborhood(anchor, prior)
    source_names = ('finite_singleton_neighborhood.py', 'singleton_sensitivity.py',
                    'finite_singleton_search.py', 'finite_block_search.py',
                    'frame_envelope.py', 'frame_reuse.py', 'campaign_telemetry.py')
    protocol = dict(campaign_id='20261007T222521Z', started_utc=datetime.now(timezone.utc).isoformat(),
                    settings={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},
                    anchor_id=anchor['candidate_id'], anchor_roles=anchor['compiled_roles'],
                    anchor_sha256=sha256(args.anchor.read_bytes()).hexdigest(),
                    predecessor_protocol_sha256=sha256((args.predecessor/'protocol.json').read_bytes()).hexdigest(),
                    planned_candidates=len(jobs), candidate_definitions=jobs, excluded_ids=excluded,
                    source_sha256={n:sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                                   for n in source_names},
                    worker_policy='At most16 active campaign cases, deducting predecessor and explicit reservations',
                    scientific_boundary='Every screened map/scalar/positive-frame/target check unchanged; dirty and three-stage promotion remain separate')
    write_json(args.run_dir/'protocol.json', protocol)
    if args.plan_only:
        print(json.dumps(dict(status='Plan PASS', candidates=len(jobs), excluded=len(excluded))))
        return
    from campaign_telemetry import snapshot
    start = time.monotonic(); results, errors, pending = [], [], {}
    next_job = 0; deadline = datetime.fromisoformat(args.deadline)
    assert deadline.tzinfo is not None
    previous, ticks = {}, os.sysconf('SC_CLK_TCK')
    changes, old_capacity = [], None
    lifetime_pid = os.getpid()

    def retain(row):
        write_json(args.run_dir/'cases'/(row['candidate_id']+'.json'), row)
        results.append(row)
        best = min(results, key=lambda r:r['compiled_roles'])
        write_json(args.run_dir/'checkpoint.json', dict(status='Running', dispatcher_pid=lifetime_pid,
                   completed_candidates=len(results), failed_candidates=len(errors),
                   planned_candidates=len(jobs), submitted_candidates=next_job,
                   elapsed_seconds=time.monotonic()-start, best_candidate_id=best['candidate_id'],
                   best_roles=best['compiled_roles'], active_capacity=old_capacity,
                   active_worker_pids=sorted({r['pid'] for r in results}),
                   completed_ids=[r['candidate_id'] for r in results]))
        print(json.dumps(dict(candidate=row['candidate_id'][:12], neighborhood=row['neighborhood'],
                              roles=row['compiled_roles'], seconds=row['elapsed_seconds'],
                              completed=len(results), best_roles=best['compiled_roles'])), flush=True)

    with (args.run_dir/'resource-snapshots.jsonl').open('x') as telemetry:
        with ProcessPoolExecutor(max_workers=args.max_workers) as pool:
            while pending or next_job < len(jobs):
                reserved = args.reserved_workers
                if args.reserve_file and args.reserve_file.exists():
                    reserved = int(json.loads(args.reserve_file.read_text())['reserved_workers'])
                assert 0 <= reserved < args.max_workers
                old_workers = predecessor_workers(args.predecessor, args.max_workers)
                capacity = max(0, args.max_workers-old_workers-reserved)
                if capacity != old_capacity:
                    changes.append(dict(utc=datetime.now(timezone.utc).isoformat(), capacity=capacity,
                                        predecessor_workers=old_workers, reserved_workers=reserved))
                    old_capacity = capacity
                    print(json.dumps(dict(worker_capacity=capacity, predecessor_workers=old_workers,
                                          reserved_workers=reserved)), flush=True)
                while len(pending) < capacity and next_job < len(jobs) and datetime.now(timezone.utc) < deadline:
                    definition = jobs[next_job]; next_job += 1
                    job = dict(definition, reference=args.reference, phase='neighborhood-cached', local_cache=True,
                               deadline=args.deadline, worker_address_space_gib=args.worker_address_space_gib)
                    pending[pool.submit(evaluate, job)] = definition
                if not pending and (next_job == len(jobs) or datetime.now(timezone.utc) >= deadline):
                    break
                done, _ = wait(pending, timeout=5, return_when=FIRST_COMPLETED)
                telemetry.write(json.dumps(snapshot(args.work_root, previous, ticks))+'\n'); telemetry.flush()
                for future in done:
                    definition = pending.pop(future)
                    try:
                        row = future.result()
                        row.update(neighborhood=definition['neighborhood'], changed=definition['changed'])
                        retain(row)
                    except Exception as exc:
                        error = dict(candidate_id=definition['candidate_id'], exception_type=type(exc).__name__,
                                     exception_message=str(exc), completed_utc=datetime.now(timezone.utc).isoformat())
                        errors.append(error); write_json(args.run_dir/'cases'/(definition['candidate_id']+'.error.json'), error)
                        print(json.dumps(dict(error=error)), flush=True)
    elapsed = time.monotonic()-start
    assert len(results) == len({r['candidate_id'] for r in results})
    terminal = 'Terminal PASS' if len(results) == len(jobs) and not errors else 'Terminal PARTIAL; checkpoints retained'
    best = min(results, key=lambda r:r['compiled_roles']) if results else None
    summary = dict(status=terminal, completed_utc=datetime.now(timezone.utc).isoformat(),
                   elapsed_seconds=elapsed, unique_verified_candidates=len(results), planned_candidates=len(jobs),
                   submitted_candidates=next_job, unsubmitted_ids=[j['candidate_id'] for j in jobs[next_job:]],
                   errors=errors, best=best, capacity_changes=changes,
                   verified_candidates_per_hour=3600*len(results)/elapsed, phase_statistics=phase_statistics(results),
                   worker_lifetime_peak_rss_kib=max((r['process_lifetime_peak_rss_kib'] for r in results), default=0),
                   ranking=[dict(candidate_id=r['candidate_id'], roles=r['compiled_roles'], neighborhood=r['neighborhood'])
                            for r in sorted(results, key=lambda r:r['compiled_roles'])], protocol=protocol)
    write_json(args.run_dir/'summary.json', summary)
    write_json(args.run_dir/'checkpoint.json', dict(status=terminal, completed_candidates=len(results),
               planned_candidates=len(jobs), failed_candidates=len(errors),
               best_candidate_id=best['candidate_id'] if best else None,
               best_roles=best['compiled_roles'] if best else None))
    print(json.dumps(dict(terminal=terminal, candidates=len(results), best_roles=best['compiled_roles'] if best else None,
                         elapsed_seconds=elapsed, verified_candidates_per_hour=3600*len(results)/elapsed)), flush=True)


if __name__ == '__main__':
    main()
