#!/usr/bin/env python3
"""Exact physical-role study of recursion cutoffs and singleton patterns.

Earlier cutoff screens used additions/output proxies. This cohort scores
the retained-controller reversible compilation on the new early/late
singleton family. Only the original local recursion cutoff and positions
change; the frozen full evaluator and all checker obligations are reused.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import finite_singleton_neighborhood as queue
from finite_singleton_successor import evaluate_direct, predecessor_workers, DIRECT_HASH

CONFIG = {}
real_write_json = queue.write_json


def candidates(anchor, prior):
    h = anchor['h']; rows = []; seen = set()
    for base in (2, 3, 5, 6, 7, 8, 9, 10):
        vectors = [anchor['positions']]
        for count in (h//2-3, h//2-2, h//2-1, h//2, h//2+1, h//2+2, h//2+3):
            vectors.append([0]*count+[h//2-2]*(h-count))
        for start in range(1, 17):
            for count in (h//2-1, h//2+1):
                vectors.append([0 if (common-start) % h < count else h//2-2 for common in range(h)])
        for positions in vectors:
            value, key = queue.identity(h, base, positions)
            if key in seen:
                continue
            seen.add(key)
            rows.append(dict(value, candidate_id=key, neighborhood='actual-role-cutoff',
                changed=[dict(field='recursion_cutoff', old=anchor['base'], new=base)], cutoff=base))
    assert len(rows) == 320 and len(seen) == len(rows)
    CONFIG['cutoff_values'] = [2, 3, 5, 6, 7, 8, 9, 10]
    return rows, [anchor['candidate_id']]


def write_json(path, value):
    if path.name == 'protocol.json' and 'candidate_definitions' in value:
        value = dict(value, recursion_cutoff_configuration=CONFIG)
    real_write_json(path, value)


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--small-control', type=Path)
    ap.add_argument('--control', type=Path)
    ap.add_argument('--reference', required=True)
    args, remaining = ap.parse_known_args()
    source_hash = sha256(Path(__file__).read_bytes()).hexdigest()
    if args.small_control:
        assert not args.small_control.exists()
        rows = []
        for h in (8, 12):
            positions = [0]*(h//2-1)+[h//2-2]*(h//2+1); positions[-2:] = [0,h//2-1]
            for base in (2, 3, 5, 6, 8, 10):
                # GroupUnion expects normalized unordered output-pair keys.
                # The existing local direct-top-level shortcut retains its
                # input permutation when base>=n, which is outside this
                # global adapter's supported interface. No verifier is
                # changed: all ground50 candidates have base<n=49.
                if base >= h-1:
                    continue
                value, key = queue.identity(h, base, positions)
                row = evaluate_direct(dict(value, candidate_id=key, reference=args.reference,
                    phase='small-cutoff-control', local_cache=True, worker_address_space_gib=6,
                    deadline='2026-10-08T08:25:21+00:00'))
                if h == 8 and base in (2, 6):
                    from finite_block_search import GroupUnion
                    from finite_singleton_search import singleton_class
                    from fast_frame_envelope import labels
                    from frame_reuse import optimize_chains, compile_reuse
                    from frame_reuse_certificate import program
                    from dag_network import exact_invocation
                    cls = singleton_class()
                    circuit = GroupUnion(h,lambda n,c:cls(n,positions[c],base),'paired',0,True)
                    frames,_ = labels(circuit,True)
                    code = compile_reuse(circuit,frames,optimize_chains(circuit,frames,'rank'))
                    row['dirty_basis'] = [exact_invocation(h,inverse,program(circuit,code)) for inverse in (False,True)]
                rows.append(row)
        args.small_control.parent.mkdir(parents=True, exist_ok=True)
        real_write_json(args.small_control, dict(status='Terminal PASS',source_sha256=source_hash,rows=rows))
        print(json.dumps(dict(status='Terminal PASS',controls=len(rows),roles=[r['compiled_roles'] for r in rows])))
        return
    assert args.control
    control = json.loads(args.control.read_text())
    assert control['status'] == 'Terminal PASS' and len(control['rows']) == 10
    assert control['source_sha256'] == source_hash
    CONFIG.update(source_sha256=source_hash,direct_envelope_sha256=DIRECT_HASH,
        control_path=str(args.control),control_sha256=sha256(args.control.read_bytes()).hexdigest(),
        scientific_scope='Original local recursion cutoff and fresh position vectors; frozen exact evaluator and every map/physical/frame/target assertion unchanged',
        previous_cutoff_scope='Earlier proxy minimization does not optimize physical retained-controller roles on these graphs')
    queue.neighborhood=candidates;queue.evaluate=evaluate_direct
    queue.predecessor_workers=predecessor_workers;queue.write_json=write_json
    sys.argv=[sys.argv[0],'--reference',args.reference,*remaining]
    queue.main()


if __name__ == '__main__':
    main()
