#!/usr/bin/env python3
"""Actual-role early/late singleton vectors across even bit grounds.

All frozen scalar, frame, physical and target verifiers execute for each
candidate. Equal and asymmetric motifs are ranked by exact saving enclosures;
the compact composition is separately marked as a conditional arithmetic
calculation rather than an independently promoted transfer.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import time

from finite_singleton_neighborhood import identity
from finite_singleton_successor import evaluate_direct, DIRECT_HASH
from singleton_sensitivity import write_json
from downstream_parameter_optimum import as_strings, saving_enclosure


def motif(p, q, rp, rq):
    vp, vq = comb(p, 3), comb(q, 3)
    n, m = vp*vp*vq, p*p*q
    w = 2*n+vp*vq*(rp+p)+vp*vp*(rq+q)
    loss = 2*vp*vq*p*p+vp*vp*q*q
    deficit = n-2*loss
    return dict(p=p, q=q, vp=vp, vq=vq, m=m, N=n, Rp=rp, Rq=rq,
                W=w, L=loss, D=deficit, s=w*m-deficit, eta=Q(deficit, w*m))


def worker(job):
    row = evaluate_direct(job)
    from review_envelopes import matching_check
    from reuse_network import triple_matching
    triples, images = triple_matching(job['h'])
    assert len(set(images)) == len(triples)
    assert all(len(set(t) & set(triples[j])) == 1 for t, j in zip(triples, images))
    row['stage_matching'] = matching_check(job['h'])
    row['stage_matching']['exact_pinned_matching_checked'] = True
    n = motif(job['h'], job['h'], row['compiled_roles'], row['compiled_roles'])
    row['equal_motif'] = n
    row['saving_enclosure'] = saving_enclosure(n['eta'], n['m']) if n['D'] > 0 else None
    return as_strings(row)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True)
    ap.add_argument('--grounds', type=int, nargs='+', default=[48, 52, 46, 54, 50, 44, 56, 42, 58, 40, 38])
    ap.add_argument('--anchor', type=Path, required=True)
    ap.add_argument('--complex-case', type=Path, required=True)
    ap.add_argument('--exclude-run', type=Path, action='append', default=[])
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--worker-address-space-gib', type=int, default=12)
    ap.add_argument('--deadline', required=True)
    ap.add_argument('--run-dir', type=Path, required=True)
    args = ap.parse_args()
    assert 1 <= args.workers <= 16 and len(args.grounds) == len(set(args.grounds))
    assert all(h >= 8 and h % 2 == 0 for h in args.grounds)
    assert not args.run_dir.exists(), 'Use a fresh run output directory'
    args.run_dir.mkdir(parents=True); (args.run_dir/'cases').mkdir()
    anchor = json.loads(args.anchor.read_text()); excluded = {anchor['candidate_id']}
    exclusions = []
    for path in args.exclude_run:
        data = (path/'protocol.json').read_bytes(); protocol = json.loads(data)
        excluded.update(row['candidate_id'] for row in protocol['candidate_definitions'])
        exclusions.append(dict(path=str(path/'protocol.json'), sha256=sha256(data).hexdigest()))
    jobs, seen = [], set()
    for h in args.grounds:
        for prefix in [h//2-1, h//2+1, h//2+3]:
            positions = [0]*prefix+[h//2-2]*(h-prefix)
            positions[-2:] = [0, h//2-1]
            value, key = identity(h, 4, positions)
            if key in seen or key in excluded:
                continue
            seen.add(key)
            jobs.append(dict(value, candidate_id=key, prefix=prefix, neighborhood='ground-early-prefix',
                reference=args.reference, phase='ground-vector-cached', local_cache=True,
                deadline=args.deadline, worker_address_space_gib=args.worker_address_space_gib))
    names = [Path(__file__).name, 'finite_singleton_successor.py', 'finite_singleton_neighborhood.py',
             'singleton_sensitivity.py', 'fast_frame_envelope.py', 'frame_envelope.py', 'frame_reuse.py',
             'downstream_compact_control_assembly.py', 'downstream_parameter_optimum.py']
    protocol = dict(campaign_id='20261007T222521Z', started_utc=datetime.now(timezone.utc).isoformat(),
        campaign_deadline='2026-10-08T08:25:21Z', settings={k: str(v) if isinstance(v, Path)
            else [str(x) if isinstance(x, Path) else x for x in v] if isinstance(v, list) else v
            for k,v in vars(args).items()},
        source_sha256={name: sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
        anchor_sha256=sha256(args.anchor.read_bytes()).hexdigest(),
        complex_case_sha256=sha256(args.complex_case.read_bytes()).hexdigest(), excluded_protocols=exclusions,
        candidate_definitions=jobs, planned_candidates=len(jobs), excluded_ids=sorted(excluded),
        scientific_scope='Complete exact finite candidates and exact even-ground matching; compact arithmetic and dirty/stage promotion remain separate.')
    assert protocol['source_sha256']['fast_frame_envelope.py'] == DIRECT_HASH
    write_json(args.run_dir/'protocol.json', protocol)
    start = time.monotonic(); rows, errors = [], []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(worker, job): job for job in jobs}
        for future in as_completed(pending):
            job = pending[future]
            try:
                row = future.result(); row['prefix'] = job['prefix']; rows.append(row)
                write_json(args.run_dir/'cases'/(row['candidate_id']+'.json'), row)
                print(json.dumps(dict(h=row['h'], prefix=job['prefix'], roles=row['compiled_roles'],
                    completed=len(rows), seconds=row['elapsed_seconds'])), flush=True)
            except Exception as exc:
                error = dict(candidate_id=job['candidate_id'], h=job['h'], prefix=job['prefix'],
                    exception_type=type(exc).__name__, exception_message=str(exc))
                errors.append(error); write_json(args.run_dir/'cases'/(job['candidate_id']+'.error.json'), error)
            write_json(args.run_dir/'checkpoint.json', dict(status='Running', completed=len(rows),
                errors=len(errors), planned=len(jobs), elapsed_seconds=time.monotonic()-start))
    best_by_ground = {anchor['h']: anchor}
    for row in rows:
        if row['h'] not in best_by_ground or row['compiled_roles'] < best_by_ground[row['h']]['compiled_roles']:
            best_by_ground[row['h']] = row
    ranked = []
    for p, first in best_by_ground.items():
        for q, middle in best_by_ground.items():
            n = motif(p, q, first['compiled_roles'], middle['compiled_roles'])
            if n['D'] > 0:
                enclosure = saving_enclosure(n['eta'], n['m'])
                ranked.append(dict(counts=n, saving_enclosure=enclosure,
                    p_candidate=first['candidate_id'], q_candidate=middle['candidate_id']))
    ranked.sort(key=lambda row: row['saving_enclosure']['saving_lower'], reverse=True)
    best = ranked[0]
    nc = json.loads(args.complex_case.read_text())['shared_complex_counts']
    nc['eta'] = Q(nc['eta'])
    from downstream_compact_control_assembly import compose
    arithmetic = compose(best['counts'], nc, 'tight', Q(83, 10**12))
    result = dict(status='Terminal PASS' if len(rows) == len(jobs) and not errors else 'Terminal PARTIAL; exact completed candidates retained',
        completed_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-start,
        completed_candidates=len(rows), planned_candidates=len(jobs), errors=errors,
        best_by_ground={h: dict(candidate_id=row['candidate_id'], roles=row['compiled_roles'], positions=row['positions'])
                        for h,row in sorted(best_by_ground.items())},
        best_asymmetric=best, asymmetric_ranking=ranked, conditional_compact_arithmetic=arithmetic,
        scope='Finite candidate checks exact; independently accepted compact assembly and changed-vector dirty/stage promotion required for a theorem claim.')
    write_json(args.run_dir/'summary.json', as_strings(result))
    print(json.dumps(dict(terminal=result['status'], cases=len(rows), errors=len(errors),
        best_p=best['counts']['p'], best_q=best['counts']['q'], seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
