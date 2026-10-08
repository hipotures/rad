#!/usr/bin/env python3
"""Cold-worker import repair for the frozen association experiment.

The original small control loaded the reference before constructing a
local class; fresh forkserver workers do not inherit that sys.path entry.
Install the immutable reference before calling the unchanged evaluator.
No graph, cache, frame or verifier logic is changed.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path
import sys

import finite_singleton_sum_rules as original
from finite_block_search import install_reference

frozen_evaluate = original.evaluate


def evaluate(job):
    install_reference(job['reference'])
    return frozen_evaluate(job)


def main():
    ap=argparse.ArgumentParser(add_help=False)
    ap.add_argument('--reference',required=True)
    ap.add_argument('--cold-control',type=Path)
    ap.add_argument('--cold-proof',type=Path)
    args,remaining=ap.parse_known_args();source_hash=sha256(Path(__file__).read_bytes()).hexdigest()
    if args.cold_control:
        assert not args.cold_control.exists()
        jobs=[]
        for h,early,late in ((8,1,1),(12,2,1)):
            positions=[0]*(h//2-1)+[h//2-2]*(h//2+1);positions[-2:]=[0,h//2-1]
            value,key=original.identity(h,2,positions,early,late)
            jobs.append(dict(value,candidate_id=key,reference=args.reference,phase='fresh-spawn-import-control',
                local_cache=True,worker_address_space_gib=6,deadline='2026-10-08T08:25:21+00:00'))
        with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
            rows=list(pool.map(evaluate,jobs))
        args.cold_control.parent.mkdir(parents=True,exist_ok=True)
        original.real_write_json(args.cold_control,dict(status='Terminal PASS',source_sha256=source_hash,
            frozen_evaluator_sha256=sha256(Path(original.__file__).read_bytes()).hexdigest(),rows=rows,
            control='Two fresh spawn workers install the reference before constructing the unchanged local class; no inherited sys.path'))
        print(json.dumps(dict(status='Terminal PASS',cold_worker_roles=[row['compiled_roles'] for row in rows])))
        return
    assert args.cold_proof
    control=json.loads(args.cold_proof.read_text())
    assert control['status']=='Terminal PASS' and len(control['rows'])==2 and control['source_sha256']==source_hash
    assert control['frozen_evaluator_sha256']==sha256(Path(original.__file__).read_bytes()).hexdigest()
    original.CONFIG.update(cold_worker_import_repair_source_sha256=source_hash,
        cold_worker_control=str(args.cold_proof),cold_worker_control_sha256=sha256(args.cold_proof.read_bytes()).hexdigest(),
        repair_scope='Only install_reference before frozen configured_class construction; previous400 import errors preserved; all graph/checker logic unchanged')
    original.evaluate=evaluate
    sys.argv=[sys.argv[0],'--reference',args.reference,*remaining]
    original.main()


if __name__=='__main__':main()
