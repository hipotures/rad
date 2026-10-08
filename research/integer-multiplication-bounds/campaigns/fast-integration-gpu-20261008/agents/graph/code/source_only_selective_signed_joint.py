#!/usr/bin/env python3
"""Reconstruct selective signed joint frames from pinned scalar source.

The interval circuit is Avi Eisenberg's PR62; invertible binary synthesis
and paid reclamation are eumemic's PR57. Their pinned compiler is retained.
Task-owned changes are selective region enlargement and signed positive
address spaces, with coherent coordinate relabeling. Every physical XOR,
source injection, copied center and arbitrary dirty component is replayed.
No archived word or claimed histogram is used as the construction input.
"""
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time

from check_compiled_witness import contained
import joint_region_search_v3 as region
import joint_positive_frontier as frontier


def write_word(path, word):
    raw = (json.dumps(word, separators=(',', ':')) + '\n').encode()
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as output:
            output.write(raw)
    return sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--h', type=int, required=True)
    parser.add_argument('--budget', type=int, required=True)
    parser.add_argument('--order', nargs='+', type=int, required=True)
    parser.add_argument('--mode', choices=('core-single', 'core-pair', 'rank-suffix', 'terminal-common'), required=True)
    parser.add_argument('--value', type=int, required=True)
    parser.add_argument('--expected-parent-sha256', required=True)
    parser.add_argument('--expected-word-sha256', required=True)
    parser.add_argument('--profile-transitions', type=Path)
    args = parser.parse_args()
    assert sorted(args.order) == list(range(args.h))
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    started = time.monotonic()
    region.initialize(args.source, args.work)
    config = dict(h=args.h, policy='rank-first', rank_delta=1, sweeps=1, limit=args.budget)
    region.COMPILER.build = lambda h: region.build_regions(h, config)
    compiled, word = region.COMPILER.compile_(args.h, matching=True, reclaim=True, dirty=True)
    scalar = region.graph(args.h).verify()
    parent_path = args.work / 'fresh-parent-word.json.gz'
    parent_digest = write_word(parent_path, word)
    assert parent_digest == args.expected_parent_sha256, 'Fresh source parent differs from selected source'
    document = dict(id=f'h{args.h}-budget{args.budget}-Q', word_path=str(parent_path),
                    word_sha256=parent_digest, Q=args.order)
    frontier.initialize(args.work)
    with sqlite3.connect(args.work / 'claims.sqlite') as db:
        db.execute('CREATE TABLE claims(scope TEXT,digest TEXT,case_id TEXT,PRIMARY KEY(scope,digest))')
    original, ordinary, signed, ranks, successors, terminals, closure = frontier.parent(document)
    result = frontier.evaluate(dict(parent=document, mode=args.mode, value=args.value))
    assert result['status'] == 'selective positive same-role word full dirty/address PASS'
    assert result['word_sha256'] == args.expected_word_sha256, 'Source-only signed word differs'
    produced = json.loads(gzip.decompress(Path(result['word_path']).read_bytes()))
    alias = produced['physical_region_address_aliases']
    frames = [tuple((f[0], f[1], tuple(f[2]))) for f in produced['frames']]
    for index, old in enumerate(ordinary):
        assert contained(old, frames[alias[index]]), 'Original scalar address escaped actual signed frame'
    for index, targets in enumerate(successors):
        for target in targets:
            assert contained(frames[alias[index]], frames[alias[target]])
    assert [(a,b) for a,b,g in produced['ops']] == [(a,b) for a,b,g in original['ops']]
    assert produced['sources'] == {str(k):v for k,v in original['sources'].items()}
    assert produced['scatter'] == [list(pair) for pair in original['scatter']]
    assert produced['R'] == original['R'] == compiled['roles']
    source_roles = set(produced['sources'].values())
    for role, before, after in original['events']:
        if before < 0 and role in source_roles:
            assert frames[alias[after]] == tuple((ordinary[after][0], ordinary[after][1], tuple(ordinary[after][2])))
    copied_centers = 0
    for role, block, common, target in original['outputs']:
        if len(target) == 1:
            copied_centers += 1
            old = tuple((ordinary[block][0], ordinary[block][1], tuple(ordinary[block][2])))
            actual = frames[alias[block]]
            assert actual[0] == old[0] and contained(old, actual) and contained(actual, old)
    assert copied_centers == args.h
    transitions = Path(result['independent']['transition_path'])
    if args.profile_transitions:
        assert transitions.read_bytes() == args.profile_transitions.read_bytes(), 'Actual signed profile transition bytes differ'
    result.update(source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
                  source_only=True, scalar=scalar, compiled=compiled,
                  source_parent_configuration=config, source_parent_sha256=parent_digest,
                  source_permutation=args.order, copied_center_spaces_unchanged=copied_centers,
                  copied_center_comparison='Equal exact rational spaces in both directions; canonical component labels can differ.',
                  source_injection_frames_unchanged=True, every_original_frame_contained=True,
                  every_original_xor_preserved=True, all_actual_word_transitions_contained=True,
                  profile_transition_sha256=sha256(transitions.read_bytes()).hexdigest(),
                  profile_transition_path=str(args.profile_transitions) if args.profile_transitions else None,
                  profile_bytes_independently_compared=bool(args.profile_transitions),
                  status=('source-only selective signed frames, coherent source labels, complete both-dirty word and actual profile bytes PASS'
                          if args.profile_transitions else 'source-only selective signed frames, coherent source labels, complete both-dirty word and actual transition reconstruction PASS'),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  seconds=time.monotonic()-started, completed_utc=datetime.now(timezone.utc).isoformat(),
                  limitations='Finite binary payload and actual rational address inclusions. Basis normalization, exact matrix CRT, all source-pair data geometry, complete moments, assembly and conditional all-size interfaces are separate checks.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],h=args.h,R=compiled['roles'],
                         word_sha256=result['word_sha256'],seconds=result['seconds'])),flush=True)


if __name__ == '__main__':
    main()
