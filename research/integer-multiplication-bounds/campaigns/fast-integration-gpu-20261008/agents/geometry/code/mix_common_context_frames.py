#!/usr/bin/env python3
"""Compile independently selected signed frame families by common context.

Every positive f1-to-f1 executed address edge must retain the same forced
coordinate. No positive f1-to-f2/f3 edge is permitted. Frames outside f1 are
kept at their original spaces. The resulting full literal word is independently
checked; no separation or moment claim substitutes for that replay.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import time

from componentwise_signed_word_enlargement import (
    contained, enlarge_components, parent, check)


def core18_frames(ordinary, maximal, successors):
    changed = {i for i, frame in enumerate(ordinary)
               if frame[0] >= 18 and frame[1].bit_count() == 1
               and frame != maximal[i]}
    queue = deque(sorted(changed))
    while queue:
        old = queue.popleft()
        for new in sorted(successors[old]):
            if new not in changed and not contained(maximal[old], ordinary[new]):
                changed.add(new)
                queue.append(new)
    selected = [maximal[i] if i in changed else frame
                for i, frame in enumerate(ordinary)]
    for old, targets in enumerate(successors):
        for new in targets:
            assert contained(selected[old], selected[new])
    return selected


def select_common_frames(word, ordinary, maximal, successors, choices):
    h = word['h']
    assert len(choices) == h and set(choices) <= {'original', 'core18', 'balanced12'}
    _, _, balanced = enlarge_components(word, ordinary, maximal, successors,
                                         'balanced', 12, 'core-single')
    variants = dict(original=ordinary,
                    core18=core18_frames(ordinary, maximal, successors),
                    balanced12=balanced)
    one_to_one = 0
    for old, targets in enumerate(successors):
        for new in targets:
            A, B = ordinary[old], ordinary[new]
            if A[1].bit_count() == 1 and A[0]:
                assert B[1].bit_count() == 1 and A[1] == B[1], \
                    'A physical lifetime crosses selected common contexts'
                one_to_one += 1
    for frames in variants.values():
        for old, selected in zip(ordinary, frames):
            if old[1].bit_count() != 1:
                assert contained(old, selected) and contained(selected, old), \
                    'A variant changes an unselected source or pair-core space'
    chosen = []
    for i, old in enumerate(ordinary):
        if old[1].bit_count() == 1:
            common = old[1].bit_length() - 1
            chosen.append(variants[choices[common]][i])
        else:
            chosen.append(old)
    for old, maximum, selected in zip(ordinary, maximal, chosen):
        assert contained(old, selected) and contained(selected, maximum)
    for old, targets in enumerate(successors):
        for new in targets:
            assert contained(chosen[old], chosen[new])
    aliases, frames, lookup = [], [], {}
    for frame in chosen:
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    fresh = dict(word)
    fresh.update(frame_format='positive-signed-v1', frames=frames,
                 physical_region_address_aliases=aliases,
                 common_context_frame_choices=choices)
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['outputs'] = [(slot, aliases[g], c, target)
                        for slot, g, c, target in word['outputs']]
    fresh['events'] = [(slot, -1 if old < 0 else aliases[old], aliases[new])
                       for slot, old, new in word['events']]
    return fresh, chosen, dict(
        independently_checked_same_common_f1_edges=one_to_one,
        original_E_containment=True, maximal_signed_containment=True,
        every_actual_transition_containment=True,
        original_roles_and_XORs_unchanged=True, R=word['R'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    rows = []
    configs = json.loads(args.input.read_text())
    started = time.monotonic()
    for config in configs:
        word, ordinary, maximal, _, successors, _, _ = parent(config['parent'])
        fresh, selected, summary = select_common_frames(
            word, ordinary, maximal, successors, config['choices'])
        work = args.work / config['case_id']
        work.mkdir()
        raw = (json.dumps(fresh, separators=(',', ':')) + '\n').encode()
        word_path = work / 'word.json.gz'
        with word_path.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as output:
                output.write(raw)
        transition = work / 'signed-transitions.bin'
        independent = check(word_path, transition)
        profile_path, audit = work / 'profile.json', work / 'transitions.json'
        command = [str(args.binary), str(transition), config['basis'],
                   str(profile_path), str(audit)]
        with (work / 'native.log').open('wb') as log:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
        profile = json.loads(profile_path.read_text())
        a = config.get('screen_a', 1284995399 / 25000000000000)
        phi = sum(t * n * math.expm1(a * math.log(575 / t))
                  for t, n in enumerate(profile['blocks']) if t and n)
        rows.append(dict(status='EXACT CANDIDATE COMMON-CONTEXT SIGNED WORD',
            config=config, summary=summary, independent=independent, profile=profile,
            screen_Phi=phi, screen_a=a, word_path=str(word_path),
            word_sha256=sha256(raw).hexdigest(),
            assignment_sha256=sha256(json.dumps(selected, separators=(',', ':')).encode()).hexdigest(),
            input_binary_sha256=sha256(transition.read_bytes()).hexdigest(),
            profile_path=str(profile_path), profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
            transition_audit=str(audit), transition_audit_sha256=sha256(audit.read_bytes()).hexdigest()))
        status = dict(completed=len(rows), total=len(configs), workers=1,
                      elapsed_seconds=time.monotonic() - started,
                      utc=datetime.now(timezone.utc).isoformat())
        (args.work / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
        (args.work / 'completed-rows.json').write_text(json.dumps(rows, indent=2) + '\n')
        print(json.dumps(dict(status, case_id=config['case_id'], Phi=phi)), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS ACTUAL COMMON-CONTEXT SIGNED WORD COHORT', rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Literal common-context separation and all actual frame inclusions, '
              'full independently reconstructed source/output/both-dirty word, '
              'complete native CRT child profiles. Scalar-source regeneration, '
              'independent Fraction controls, DATA/stock/assembly binders and '
              'all-size assumptions remain separate acceptance gates.'), indent=2) + '\n')


if __name__ == '__main__':
    main()
