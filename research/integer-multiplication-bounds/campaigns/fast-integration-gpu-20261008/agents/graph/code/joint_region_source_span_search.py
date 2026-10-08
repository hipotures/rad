#!/usr/bin/env python3
"""Resynthesize paid joint regions in actual incoming-source span joins."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import time

import co_signed_source_frames as co
import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
import joint_region_source_spans as source_regions
from joint_scalar_future_frames import write_word
from joint_word_check_v5 import check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--parents', type=Path)
    parser.add_argument('--small', action='store_true')
    parser.add_argument('--h', type=int, required=True)
    parser.add_argument('--budgets', type=int, nargs='+', required=True)
    parser.add_argument('--groupings', nargs='+', choices=['preserve-regions', 'merge-aliases'], default=['preserve-regions'])
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
    Q = list(range(args.h)) if args.small else next(d['Q'] for d in json.loads(args.parents.read_text()) if d['h'] == args.h)
    rows = []
    for budget in args.budgets:
        cfg = dict(h=args.h, policy='rank-first', rank_delta=1, sweeps=1, limit=budget)
        c, blocks, _, _, owner, _, order, _ = region.build_regions(args.h, cfg)
        scalar = c.verify()
        labels, summary = source_regions.assign(c, blocks, owner, order)
        fixture = args.work / f'region-source-frames-budget{budget}.json'
        fixture.write_text(json.dumps(dict(h=args.h, source_permutation=Q,
            scalar_region_config=cfg, node_regions=[(x, owner[x]) for x in sorted(c.active)],
            region_frames=labels, summary=summary), separators=(',', ':')) + '\n')
        for grouping in args.groupings:
            started = time.monotonic()
            case = f'h{args.h}-region-source-budget{budget}-{grouping}-{args.carrier}'
            target = args.work / 'raw' / case
            target.mkdir(parents=True)
            try:
                region.COMPILER.build = lambda dimension: joint.build(c, labels, owner, grouping, args.carrier)
                compiled, word = region.COMPILER.compile_(args.h, matching=True, reclaim=True, dirty=True)
                word = co.canonicalize(word, Q)
                path = target / 'word.json.gz'
                digest = write_word(path, word)
                independent = check(path, target / 'mixed-transitions.bin')
                result = dict(status='DISCOVERY joint region source-span word full finite PASS',
                    scalar=scalar, compiled=compiled, independent=independent,
                    word_path=str(path), word_sha256=digest)
            except Exception as error:
                result = dict(status='REJECTED joint region source-span synthesis', error=repr(error), scalar=scalar)
            result.update(case_id=case, frame_summary=summary,
                configuration=dict(h=args.h, budget=budget, scalar_regions=cfg,
                    carrier=args.carrier, grouping=grouping, source_permutation=Q),
                source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
                region_source_frames_path=str(fixture), region_source_frames_sha256=sha256(fixture.read_bytes()).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                frame_constructor_sha256=sha256(Path(source_regions.__file__).read_bytes()).hexdigest(),
                seconds=time.monotonic()-started, completed_utc=datetime.now(timezone.utc).isoformat(),
                limitations='Fresh source/region span joins, all scalar containment and independent full finite mixed word. Native actual CRT/NE profiles, independent incidence/Gram, DATA/stock/moments/47+7 assembly and inherited all-size gauge/tape transfer are separate acceptance gates.')
            (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
            rows.append(result)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(dict(status='running', command=sys.argv, rows=rows), indent=2) + '\n')
            print(json.dumps(dict(case_id=case, status=result['status'], R=result.get('compiled', {}).get('roles'),
                smaller_regions=summary['strictly_smaller_region_spaces'], error=result.get('error'))), flush=True)
    args.output.write_text(json.dumps(dict(status='complete', command=sys.argv, rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')


if __name__ == '__main__':
    main()
