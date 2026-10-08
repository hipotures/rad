#!/usr/bin/env python3
"""Joint compile exact minimal source-edge spans, including co-signed frames.

Scalar circuit: Avi Eisenberg PR62. Binary compiler and paid reclamation:
eumemic PR57. Smaller frames are justified by actual primitive source lines
and exact support partitions, never by an original-envelope floor. No
decreasing-frame operation or ridge-array input restriction is introduced.
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
from joint_scalar_future_frames import write_word
from joint_word_check_v5 import check


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--parents', type=Path)
    p.add_argument('--small', action='store_true')
    p.add_argument('--h', type=int, required=True)
    p.add_argument('--carriers', nargs='+', choices=['original', 'small-rise', 'large-rise', 'terminal-first'], default=['original'])
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    (args.work / 'process.json').write_text(json.dumps(dict(pid=os.getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    joint.initialize(args.source, args.work)
    joint.contained = co.contained
    c = region.graph(args.h)
    scalar = c.verify()
    if args.small:
        Q = list(range(args.h))
    else:
        assert args.parents
        Q = next(d['Q'] for d in json.loads(args.parents.read_text()) if d['h'] == args.h)
    start = time.monotonic()
    labels, source_support, summary = co.node_frames(c)
    original_owner = {x: x for x in c.active}
    basis_fixture = args.work / 'source-frame-descriptors.json'
    basis_fixture.write_text(json.dumps(dict(h=c.h, source_permutation=Q,
        node_frames=[(x, labels[x]) for x in sorted(c.active)], summary=summary), separators=(',', ':')) + '\n')
    rows = []
    for carrier in args.carriers:
        case = f'h{args.h}-minimal-source-edge-spans-{carrier}'
        target = args.work / 'raw' / case
        target.mkdir(parents=True)
        try:
            region.COMPILER.build = lambda dimension: joint.build(c, labels, original_owner, 'merge-aliases', carrier)
            compiled, word = region.COMPILER.compile_(args.h, matching=True, reclaim=True, dirty=True)
            word = co.canonicalize(word, Q)
            word_path = target / 'word.json.gz'
            word_sha = write_word(word_path, word)
            independent = check(word_path, target / 'mixed-transitions.bin')
            result = dict(status='DISCOVERY minimal actual source-edge spans and mixed word full finite PASS',
                case_id=case, scalar=scalar, compiled=compiled, independent=independent,
                frame_summary=summary, word_path=str(word_path), word_sha256=word_sha,
                source_frame_descriptors_path=str(basis_fixture),
                source_frame_descriptors_sha256=sha256(basis_fixture.read_bytes()).hexdigest())
        except Exception as error:
            result = dict(status='REJECTED minimal source-span compiler configuration',
                          case_id=case, error=repr(error), scalar=scalar, frame_summary=summary)
        result.update(configuration=dict(h=args.h, carrier=carrier, exact_source_spans=True,
                                         source_permutation=Q, grouping='merge-aliases'),
            source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
            source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
            seconds=time.monotonic()-start, completed_utc=datetime.now(timezone.utc).isoformat(),
            limitations='New typed finite source/word construction. Actual complemented-normal projectors and full CRT/NE profiles, independent fresh source reproduction, DATA/stock/moments/47+7 assembly and inherited all-size gauge/tape realization remain separate.')
        (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        rows.append(result)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(dict(status='running', command=sys.argv, rows=rows), indent=2) + '\n')
        print(json.dumps(dict(case_id=case, status=result['status'], R=result.get('compiled', {}).get('roles'),
                             regions=result.get('compiled', {}).get('stats', {}).get('regions'), error=result.get('error'))), flush=True)
    args.output.write_text(json.dumps(dict(status='complete', command=sys.argv, rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')


if __name__ == '__main__':
    main()
