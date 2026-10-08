#!/usr/bin/env python3
"""Measured, bounded process-parallel actual-role singleton sensitivity.

This is a task-specific experiment, not a general orchestration service.
Two uncached and two cached serial candidates precede a dynamic process
pool over the remaining distinct candidates. Every full global verifier
remains unchanged. Local caching retains immutable, already verified DAGs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from hashlib import sha256
import gc
import json
import os
from pathlib import Path
import resource
import sys
import time
from types import MappingProxyType

# These graph/flow tasks each receive one CPU process, not a BLAS team.
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '1'

_LOCAL_CACHE = {}


class VerifiedLocal:
    """Immutable local inputs used read-only by GroupUnion.

    The original verifier executes before taking these snapshots. Only
    local DAG generation/rechecking is reused; global maps and all compiled
    scalar, source/target and forward/reverse frame checks execute afresh.
    """
    def __init__(self, circuit):
        checked = circuit.verify()
        self.inputs = tuple(circuit.inputs)
        self.args = tuple(circuit.args)
        self.active = frozenset(circuit.active)
        self.support = tuple(circuit.support)
        self.outputs = MappingProxyType(dict(circuit.outputs))
        self._checked = MappingProxyType(dict(checked))

    def verify(self):
        return dict(self._checked)


def write_json(path, value):
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    temp.replace(path)


def evaluate(job):
    from finite_block_search import GroupUnion, install_reference
    from finite_singleton_search import singleton_class
    from frame_envelope import labels, target_check
    from frame_reuse import optimize_chains, compile_reuse, check, included
    install_reference(job['reference'])
    assert datetime.now(timezone.utc) < datetime.fromisoformat(job['deadline'])
    if job['worker_address_space_gib']:
        cap = job['worker_address_space_gib']*1024**3
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    h, positions, base = job['h'], job['positions'], job['base']
    assert h >= 6 and h % 2 == 0 and len(positions) == h
    assert all(0 <= p < h//2 for p in positions)
    cls = singleton_class()
    counters = dict(local_builds=0, local_cache_hits=0)

    def factory(n, common):
        key = (str(Path(job['reference']).resolve()), n, positions[common], base)
        if not job['local_cache']:
            counters['local_builds'] += 1
            return cls(n, positions[common], base)
        if key not in _LOCAL_CACHE:
            _LOCAL_CACHE[key] = VerifiedLocal(cls(n, positions[common], base))
            counters['local_builds'] += 1
        else:
            counters['local_cache_hits'] += 1
        return _LOCAL_CACHE[key]

    started = datetime.now(timezone.utc).isoformat()
    t = time.monotonic()
    usage = resource.getrusage(resource.RUSAGE_SELF)
    marks = {}
    circuit = GroupUnion(h, factory, 'paired', 0, True)
    marks['construction_and_local_checks'] = time.monotonic()-t
    at = time.monotonic(); original = circuit.verify()
    marks['global_scalar_map'] = time.monotonic()-at
    at = time.monotonic(); frames, metadata = labels(circuit, True)
    marks['positive_envelopes'] = time.monotonic()-at
    at = time.monotonic(); plan = optimize_chains(circuit, frames, 'rank')
    marks['controller_flow'] = time.monotonic()-at
    at = time.monotonic(); code = compile_reuse(circuit, frames, plan)
    checked = check(circuit, frames, code)
    marks['compile_and_physical_verification'] = time.monotonic()-at
    at = time.monotonic(); targets = target_check(circuit, frames, True)
    marks['every_physical_target'] = time.monotonic()-at
    final = resource.getrusage(resource.RUSAGE_SELF)
    row = dict(candidate_id=job['candidate_id'], h=h, base=base, positions=positions,
               phase=job['phase'], local_cache=job['local_cache'], pid=os.getpid(),
               started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
               elapsed_seconds=time.monotonic()-t,
               cpu_seconds=final.ru_utime+final.ru_stime-usage.ru_utime-usage.ru_stime,
               process_lifetime_peak_rss_kib=final.ru_maxrss,
               peak_rss_scope='Lifetime high water mark; upper bound for this task in a reused process',
               phase_seconds=marks, local_recipe_statistics=counters,
               original=original, compiled_roles=code['roles'], chains=code['chain_summary'],
               checked=checked, frames=metadata, targets=targets,
               verification_scope='Full unchanged finite map, positive frames, physical scalar/frame compilation and targets; separate dirty/three-stage promotion required')
    included.cache_clear(); GroupUnion.support_in.cache_clear(); gc.collect()
    return row


def candidates(h, gap, base, reference):
    baseline = [gap if common//2 <= gap else gap+1 for common in range(h)]
    assert all(0 <= p < h//2 for p in baseline)
    rows, seen = [], set()
    for pair in range(h//2):
        old = baseline[2*pair]
        choices = [old-1, old+1] if old+1 < h//2 else [old-1, old-2]
        for new in choices:
            if new < 0:
                continue
            positions = list(baseline)
            positions[2*pair:2*pair+2] = [new, new]
            identity = dict(h=h, base=base, positions=positions,
                            reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
            key = sha256(json.dumps(identity, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            assert key not in seen and positions != baseline
            seen.add(key)
            rows.append(dict(identity, candidate_id=key, reference=reference,
                             changed_pair=pair, old_position=old, new_position=new))
    return baseline, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True)
    ap.add_argument('--h', type=int, default=50)
    ap.add_argument('--gap', type=int, default=23)
    ap.add_argument('--base', type=int, default=4)
    ap.add_argument('--workers', type=int, default=12)
    ap.add_argument('--worker-address-space-gib', type=int, default=6)
    ap.add_argument('--deadline', required=True)
    ap.add_argument('--work-root', type=Path, required=True)
    ap.add_argument('--run-dir', type=Path, required=True)
    args = ap.parse_args()
    assert 1 <= args.workers <= 14 and args.worker_address_space_gib >= 1
    assert not args.run_dir.exists(), 'Use a fresh output directory'
    args.run_dir.mkdir(parents=True); (args.run_dir/'cases').mkdir()
    baseline, jobs = candidates(args.h, args.gap, args.base, args.reference)
    assert len(jobs) >= 5
    start = time.monotonic()
    source_names = ('singleton_sensitivity.py', 'finite_singleton_search.py',
                    'finite_block_search.py', 'frame_envelope.py', 'frame_reuse.py')
    protocol = dict(campaign_id='20261007T222521Z', started_utc=datetime.now(timezone.utc).isoformat(),
                    settings={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},
                    baseline_positions=baseline,
                    source_sha256={n:sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
                                   for n in source_names},
                    planned_candidates=len(jobs), candidate_definitions=jobs,
                    scientific_boundary='Sensitivity candidates are screened exactly; no automatic theorem promotion',
                    benchmark_boundary='Serial and parallel phases use distinct structurally matched candidates; this is a useful throughput measurement, not an identical-input speedup')
    write_json(args.run_dir/'protocol.json', protocol)
    results, phases = [], []

    def retain(row):
        write_json(args.run_dir/'cases'/(row['candidate_id']+'.json'), row)
        results.append(row)
        best = min(results, key=lambda r:r['compiled_roles'])
        checkpoint = dict(status='Running', completed_candidates=len(results),
                          planned_candidates=len(jobs), elapsed_seconds=time.monotonic()-start,
                          best_candidate_id=best['candidate_id'], best_roles=best['compiled_roles'],
                          completed_ids=[r['candidate_id'] for r in results], phases=phases)
        write_json(args.run_dir/'checkpoint.json', checkpoint)
        print(json.dumps(dict(candidate=row['candidate_id'][:12], phase=row['phase'],
                              roles=row['compiled_roles'], seconds=row['elapsed_seconds'],
                              completed=len(results), best_roles=best['compiled_roles'])), flush=True)

    for name, subset, cache in [('serial-uncached', jobs[:2], False),
                                 ('serial-cached', jobs[2:4], True)]:
        phase_start = time.monotonic()
        for definition in subset:
            job = dict(definition, phase=name, local_cache=cache,
                       deadline=args.deadline, worker_address_space_gib=args.worker_address_space_gib)
            retain(evaluate(job))
        elapsed = time.monotonic()-phase_start
        phases.append(dict(name=name, unique_verified_candidates=len(subset), workers=1,
                           wall_seconds=elapsed, verified_candidates_per_hour=3600*len(subset)/elapsed))
    from campaign_telemetry import snapshot
    telemetry_previous, ticks = {}, os.sysconf('SC_CLK_TCK')
    phase_start = time.monotonic()
    with (args.run_dir/'resource-snapshots.jsonl').open('x') as telemetry:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            pending = {pool.submit(evaluate, dict(job, phase='parallel-cached', local_cache=True,
                       deadline=args.deadline, worker_address_space_gib=args.worker_address_space_gib))
                       for job in jobs[4:]}
            while pending:
                done, pending = wait(pending, timeout=5, return_when=FIRST_COMPLETED)
                telemetry.write(json.dumps(snapshot(args.work_root, telemetry_previous, ticks))+'\n')
                telemetry.flush()
                for future in done:
                    retain(future.result())
    elapsed = time.monotonic()-phase_start
    phases.append(dict(name='parallel-cached', unique_verified_candidates=len(jobs)-4,
                       workers=args.workers, wall_seconds=elapsed,
                       verified_candidates_per_hour=3600*(len(jobs)-4)/elapsed))
    best = min(results, key=lambda r:r['compiled_roles'])
    final = dict(status='Terminal PASS', completed_utc=datetime.now(timezone.utc).isoformat(),
                 unique_verified_candidates=len(results), elapsed_seconds=time.monotonic()-start,
                 best=best, phases=phases,
                 ranking=[dict(candidate_id=r['candidate_id'], roles=r['compiled_roles'])
                          for r in sorted(results, key=lambda r:r['compiled_roles'])],
                 protocol=protocol, throughput_ratio_parallel_over_uncached=
                 phases[-1]['verified_candidates_per_hour']/phases[0]['verified_candidates_per_hour'])
    assert len(results) == len(jobs) == len({r['candidate_id'] for r in results})
    write_json(args.run_dir/'summary.json', final)
    write_json(args.run_dir/'checkpoint.json', dict(status='Terminal PASS',
               completed_candidates=len(results), best_candidate_id=best['candidate_id'],
               best_roles=best['compiled_roles'], phases=phases))
    print(json.dumps(dict(terminal=True, cases=len(results), best_roles=best['compiled_roles'],
                         phases=phases)), flush=True)


if __name__ == '__main__':
    main()
