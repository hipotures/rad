#!/usr/bin/env python3
"""Joint synthesis on selectively joined minimal source-edge frames.

Public scalar circuit: Avi Eisenberg PR62. Public binary compiler: eumemic
PR57. All added positive source directions, scalar containment and complete
literal words are reconstructed; there is no decreasing-frame operation.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import time

import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
import co_signed_source_frames as co
import hybrid_source_edge_frames as hybrid
from joint_scalar_future_frames import write_word
from joint_word_check_v5 import check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--parents', type=Path)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--h', type=int, required=True)
    parser.add_argument('--policies', nargs='+', required=True)
    parser.add_argument('--carrier', choices=['original', 'small-rise', 'large-rise', 'terminal-first'], default='original')
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    (args.work / 'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    joint.initialize(args.source, args.work)
    joint.contained = co.contained
    c = region.graph(args.h)
    scalar = c.verify()
    Q = list(range(args.h)) if args.small else next(d['Q'] for d in json.loads(args.parents.read_text()) if d['h'] == args.h)
    original_owner = {x: x for x in c.active}
    rows, known = [], {}
    for policy_name in args.policies:
        started = time.monotonic()
        policy, threshold = policy_name.split(':')
        threshold = int(threshold)
        case = f'h{args.h}-hybrid-source-{policy}-{threshold}-{args.carrier}'
        target = args.work / 'raw' / case
        target.mkdir(parents=True)
        try:
            labels, support, summary = hybrid.node_frames(c, policy, threshold)
            assignments = [(x, labels[x]) for x in sorted(c.active)]
            assignment_sha = sha256(json.dumps(assignments, separators=(',', ':')).encode()).hexdigest()
            fixture = target / 'source-frame-descriptors.json'
            fixture.write_text(json.dumps(dict(h=c.h, source_permutation=Q, node_frames=assignments,
                summary=summary), separators=(',', ':')) + '\n')
            if assignment_sha in known:
                result = dict(status='DEDUPLICATED exact complete hybrid frame assignment',
                    duplicate_of=known[assignment_sha], frame_summary=summary)
            else:
                known[assignment_sha] = case
                region.COMPILER.build = lambda dimension: joint.build(c, labels, original_owner, 'merge-aliases', args.carrier)
                compiled, word = region.COMPILER.compile_(args.h, matching=True, reclaim=True, dirty=True)
                word = co.canonicalize(word, Q)
                word_path = target / 'word.json.gz'
                word_sha = write_word(word_path, word)
                independent = check(word_path, target / 'mixed-transitions.bin')
                result = dict(status='DISCOVERY hybrid source-edge joins and mixed word full finite PASS',
                    scalar=scalar, compiled=compiled, independent=independent, frame_summary=summary,
                    word_path=str(word_path), word_sha256=word_sha,
                    source_frame_descriptors_path=str(fixture),
                    source_frame_descriptors_sha256=sha256(fixture.read_bytes()).hexdigest())
            result['frame_assignment_sha256'] = assignment_sha
        except Exception as error:
            result = dict(status='REJECTED hybrid source-edge configuration', error=repr(error), scalar=scalar)
        result.update(case_id=case, configuration=dict(h=args.h, policy=policy, threshold=threshold,
            carrier=args.carrier, source_permutation=Q, grouping='merge-aliases'),
            source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
            compiler_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
            frame_constructor_sha256=sha256(Path(hybrid.__file__).read_bytes()).hexdigest(),
            seconds=time.monotonic()-started, completed_utc=datetime.now(timezone.utc).isoformat(),
            limitations='New finite typed source/word construction; full actual CRT/NE profiles, independent source reproduction, DATA/stock/moments/47+7 assembly and inherited all-size gauge/tape realization remain separate.')
        (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        rows.append(result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(dict(status='running', command=sys.argv, rows=rows), indent=2) + '\n')
        print(json.dumps(dict(case_id=case, status=result['status'], R=result.get('compiled', {}).get('roles'),
            error=result.get('error'))), flush=True)
    args.output.write_text(json.dumps(dict(status='complete', command=sys.argv, rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')


if __name__ == '__main__':
    main()
