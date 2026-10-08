#!/usr/bin/env python3
"""Fresh pinned scalar reconstruction with independently selected common frames.

Interval producer: Avi Eisenberg PR62. Binary joint synthesis and paid
reclamation: eumemic PR57. Selected containing-region assignments and
per-common signed positive frame choices are task-owned developments. The
independent literal-word checker reconstructs all source and target supports,
addresses, paid roles and F2 role dirty restoration in both orientations.
The all-array conclusion uses the inherited common-gauge telescoping lemma.
"""
import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import joint_region_search_v3 as region
import joint_positive_frontier as frontier
from check_compiled_witness import contained
from joint_word_check_v4 import check

GEOMETRY = Path(__file__).resolve().parents[2] / 'geometry' / 'code'
sys.path.insert(0, str(GEOMETRY))
from mix_common_frame_families import select_family_frames


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
    parser.add_argument('--choices-file', type=Path, required=True)
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
    compiled, original = region.COMPILER.compile_(args.h, matching=True, reclaim=True, dirty=True)
    scalar = region.graph(args.h).verify()
    parent_path = args.work / 'fresh-parent-word.json.gz'
    parent_digest = write_word(parent_path, original)
    assert parent_digest == args.expected_parent_sha256
    document = dict(id=f'h{args.h}-budget{args.budget}-Q', word_path=str(parent_path),
                    word_sha256=parent_digest, Q=args.order)
    frontier.initialize(args.work)
    original, ordinary, maximal, ranks, successors, terminals, inherited = frontier.parent(document)
    choices_config = [item for item in json.loads(args.choices_file.read_text())
                      if item['parent']['h'] == args.h]
    assert len(choices_config) == 1
    choices_config = choices_config[0]
    assert choices_config['parent']['word_sha256'] == parent_digest
    assert choices_config['parent']['Q'] == args.order
    fresh, selected, summary = select_family_frames(original, ordinary, maximal,
        successors, choices_config['choices'])
    word_path = args.work / 'word.json.gz'
    word_digest = write_word(word_path, fresh)
    assert word_digest == args.expected_word_sha256
    transitions = args.work / 'signed-transitions.bin'
    independent = check(word_path, transitions)
    actual = [tuple((f[0], f[1], tuple(f[2]))) for f in fresh['frames']]
    aliases = fresh['physical_region_address_aliases']
    for index, old in enumerate(ordinary):
        assert contained(old, actual[aliases[index]])
        assert contained(actual[aliases[index]], maximal[index])
    for index, targets in enumerate(successors):
        for target in targets:
            assert contained(actual[aliases[index]], actual[aliases[target]])
    assert [(a,b) for a,b,g in fresh['ops']] == [(a,b) for a,b,g in original['ops']]
    assert fresh['sources'] == original['sources'] and fresh['scatter'] == original['scatter']
    assert fresh['R'] == original['R'] == compiled['roles']
    source_roles = set(fresh['sources'].values())
    for role, before, after in original['events']:
        if before < 0 and role in source_roles:
            assert actual[aliases[after]] == ordinary[after]
    copied_centers = 0
    for role, block, common, target in original['outputs']:
        if len(target) == 1:
            copied_centers += 1
            old, new = ordinary[block], actual[aliases[block]]
            assert old[0] == new[0] and contained(old, new) and contained(new, old)
    assert copied_centers == args.h
    if args.profile_transitions:
        assert transitions.read_bytes() == args.profile_transitions.read_bytes()
    result = dict(
        status='source-only common-context multifamily signed frames, coherent labels and complete F2 both-dirty word PASS',
        source_only=True, source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
        h=args.h, R=compiled['roles'], scalar=scalar, compiled=compiled,
        configuration=dict(parent=document,choices=choices_config['choices'],basis=choices_config['basis']),
        source_parent_configuration=config, source_parent_sha256=parent_digest,
        source_permutation=args.order, summary=summary, independent=independent,
        word_path=str(word_path),word_sha256=word_digest,
        copied_center_spaces_unchanged=copied_centers, source_injection_frames_unchanged=True,
        every_original_frame_contained=True, every_selected_frame_inside_maximal=True,
        every_original_xor_preserved=True, all_actual_word_transitions_contained=True,
        profile_transition_sha256=sha256(transitions.read_bytes()).hexdigest(),
        profile_transition_path=str(args.profile_transitions) if args.profile_transitions else None,
        profile_bytes_independently_compared=bool(args.profile_transitions),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        component_constructor_sha256=sha256((GEOMETRY/'componentwise_signed_word_enlargement.py').read_bytes()).hexdigest(),
        common_constructor_sha256=sha256((GEOMETRY/'mix_common_context_frames.py').read_bytes()).hexdigest(),
        multifamily_constructor_sha256=sha256((GEOMETRY/'mix_common_frame_families.py').read_bytes()).hexdigest(),
        choices_file_sha256=sha256(args.choices_file.read_bytes()).hexdigest(),
        seconds=time.monotonic()-started, completed_utc=datetime.now(timezone.utc).isoformat(),
        limitations='Finite binary payload and actual rational address inclusions. Exact basis normalization, matrix CRT, all source-pair geometry, moments, assembly and inherited conditional all-size assumptions remain separate.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],h=args.h,R=compiled['roles'],
                         word_sha256=word_digest,seconds=result['seconds'])),flush=True)


if __name__ == '__main__':
    main()
