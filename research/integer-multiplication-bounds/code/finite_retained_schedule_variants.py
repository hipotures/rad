#!/usr/bin/env python3
"""Fresh topological schedule experiment on the best singleton graph.

Only node ordering changes. Original scalar maps, positive E(C,V), all
physical coefficient/frame transitions and physical target checks remain
exact. A relabeling does not alter the side map or stage matching.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import gc
import json
import os
from pathlib import Path
import resource
import sys
import time

for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'

import finite_singleton_neighborhood as queue
from finite_singleton_successor import predecessor_workers, DIRECT_HASH
from finite_schedule_search import MODES, reordered

CONFIG = {}
real_write_json = queue.write_json


def identity(h, base, positions, mode, seed):
    value = dict(h=h, base=base, positions=positions, schedule_mode=mode,
                 schedule_seed=seed, reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
    return value, sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def candidates(anchor, prior):
    settings = [(mode, 0) for mode in MODES if mode != 'rank_random']
    settings += [('rank_random', seed) for seed in range(1, 129)]
    rows = []
    for mode, seed in settings:
        value, key = identity(anchor['h'], anchor['base'], anchor['positions'], mode, seed)
        rows.append(dict(value, candidate_id=key, neighborhood='topological-'+mode,
                         changed=[dict(field='topological_order', mode=mode, seed=seed)]))
    assert len({row['candidate_id'] for row in rows}) == len(rows)
    return rows, [anchor['candidate_id']]


def evaluate(job):
    from finite_block_search import GroupUnion, install_reference
    from finite_singleton_search import singleton_class
    from fast_frame_envelope import labels
    from frame_envelope import target_check
    from frame_reuse import optimize_chains, compile_reuse, check, included
    from singleton_sensitivity import VerifiedLocal, _LOCAL_CACHE
    assert sha256(Path(__file__).with_name('fast_frame_envelope.py').read_bytes()).hexdigest() == DIRECT_HASH
    install_reference(job['reference'])
    if job.get('worker_address_space_gib'):
        cap = job['worker_address_space_gib']*1024**3
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    assert datetime.now(timezone.utc) < datetime.fromisoformat(job['deadline'])
    start = time.monotonic(); cpu = time.process_time(); marks = {}
    cls = singleton_class(); counts = dict(local_builds=0, local_cache_hits=0)

    def factory(n, common):
        key = (str(Path(job['reference']).resolve()), n, job['positions'][common], job['base'])
        if key not in _LOCAL_CACHE:
            _LOCAL_CACHE[key] = VerifiedLocal(cls(n, job['positions'][common], job['base']))
            counts['local_builds'] += 1
        else:
            counts['local_cache_hits'] += 1
        return _LOCAL_CACHE[key]

    started = datetime.now(timezone.utc).isoformat()
    circuit = GroupUnion(job['h'], factory, 'paired', 0, True)
    marks['construction_and_local_checks'] = time.monotonic()-start
    at = time.monotonic(); original = circuit.verify(); marks['global_scalar_map'] = time.monotonic()-at
    at = time.monotonic(); frames, metadata = labels(circuit, True); marks['positive_envelopes'] = time.monotonic()-at
    at = time.monotonic(); targets = target_check(circuit, frames, True); marks['every_physical_target'] = time.monotonic()-at
    at = time.monotonic(); view, relabeled, schedule_hash = reordered(circuit, frames, job['schedule_mode'], job['schedule_seed'])
    marks['exact_topological_relabeling'] = time.monotonic()-at
    at = time.monotonic(); plan = optimize_chains(view, relabeled, 'id'); marks['controller_flow'] = time.monotonic()-at
    at = time.monotonic(); code = compile_reuse(view, relabeled, plan); checked = check(view, relabeled, code)
    marks['compile_and_physical_verification'] = time.monotonic()-at
    row = dict(candidate_id=job['candidate_id'], h=job['h'], base=job['base'], positions=job['positions'],
        schedule_mode=job['schedule_mode'], schedule_seed=job['schedule_seed'], schedule_sha256=schedule_hash,
        compiled_roles=code['roles'], original=original, frames=metadata, chains=code['chain_summary'], checked=checked,
        targets=targets, local_recipe_statistics=counts, local_cache=True, phase=job['phase'], pid=os.getpid(),
        started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-start,
        cpu_seconds=time.process_time()-cpu, phase_seconds=marks,
        process_lifetime_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        peak_rss_scope='Lifetime high water mark of reused worker',
        verification_scope='Unchanged original formal maps, exact topological relabeling, positive envelopes, every physical scalar/frame transition and targets; promotion separate')
    if job.get('dirty'):
        from frame_reuse_certificate import program
        from dag_network import exact_invocation
        row['dirty_basis'] = [exact_invocation(circuit.h, inverse, program(view, code)) for inverse in (False, True)]
    included.cache_clear(); GroupUnion.support_in.cache_clear(); gc.collect()
    return row


def write_json(path, value):
    if path.name == 'protocol.json' and 'candidate_definitions' in value:
        value = dict(value, topological_schedule_configuration=CONFIG)
    real_write_json(path, value)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--small-control', type=Path)
    ap.add_argument('--control', type=Path)
    ap.add_argument('--reference', required=True)
    args, remaining = ap.parse_known_args()
    if args.small_control:
        assert not args.small_control.exists()
        rows = []
        for h in (8, 12):
            positions = [0]*(h//2-1)+[h//2-2]*(h//2+1); positions[-2:] = [0, h//2-1]
            for mode in ('rank_id', 'rank_reverse_id', 'rank_random'):
                value, key = identity(h, 4, positions, mode, 109)
                rows.append(evaluate(dict(value, candidate_id=key, reference=args.reference,
                    deadline='2026-10-08T08:25:21+00:00', phase='small-topological-control', local_cache=True,
                    worker_address_space_gib=6, dirty=(h == 8))))
        result = dict(status='Terminal PASS', rows=rows, source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        args.small_control.parent.mkdir(parents=True, exist_ok=True)
        real_write_json(args.small_control, result)
        print(json.dumps(dict(status=result['status'], rows=len(rows), roles=[row['compiled_roles'] for row in rows])))
        return
    assert args.control
    control = json.loads(args.control.read_text())
    assert control['status'] == 'Terminal PASS' and len(control['rows']) == 6
    assert control['source_sha256'] == sha256(Path(__file__).read_bytes()).hexdigest()
    CONFIG.update(source_sha256=control['source_sha256'], control_path=str(args.control),
        control_sha256=sha256(args.control.read_bytes()).hexdigest(), direct_envelope_sha256=DIRECT_HASH,
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
            ('finite_schedule_search.py', 'frame_reuse.py', 'frame_envelope.py', 'finite_block_search.py', 'singleton_sensitivity.py')},
        scientific_scope='Change only exact topological node order; same graph/map and positive frame family; all verifier assertions unchanged')
    queue.neighborhood = candidates; queue.evaluate = evaluate
    queue.predecessor_workers = predecessor_workers; queue.write_json = write_json
    sys.argv = [sys.argv[0], '--reference', args.reference, *remaining]
    queue.main()


if __name__ == '__main__':
    main()
