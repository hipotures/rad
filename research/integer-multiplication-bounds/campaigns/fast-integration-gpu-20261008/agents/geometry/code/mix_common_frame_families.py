#!/usr/bin/env python3
"""Mix distinct component policies using exact per-common matrix costs.

Global policies can be inferior even when useful on selected common contexts.
Every common choice is realized as an actual frame assignment and independently
checked against every original physical transition before profiling.
"""
import argparse
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
from mix_common_context_frames import core18_frames

VARIANT_CACHE = {}


def select_family_frames(word, ordinary, maximal, successors, choices):
    h = word['h']
    allowed = {'original', 'core18'} | {mode + '12' for mode in
        ('balanced', 'unbalanced', 'singleton', 'multi', 'boundary', 'interior')}
    assert len(choices) == h and set(choices) <= allowed
    key = (id(word), tuple(sorted(set(choices))))
    if key not in VARIANT_CACHE:
        variants = {}
        for name in sorted(set(choices)):
            if name == 'original':
                variants[name] = ordinary
            elif name == 'core18':
                variants[name] = core18_frames(ordinary, maximal, successors)
            else:
                _, _, variants[name] = enlarge_components(
                    word, ordinary, maximal, successors, name[:-2], 12, 'core-single')
        for frames in variants.values():
            for old, selected in zip(ordinary, frames):
                if old[1].bit_count() != 1:
                    assert contained(old, selected) and contained(selected, old)
        VARIANT_CACHE[key] = variants
    variants = VARIANT_CACHE[key]
    same_common_edges = 0
    for old, targets in enumerate(successors):
        for new in targets:
            if ordinary[old][0] and ordinary[old][1].bit_count() == 1:
                assert ordinary[new][1].bit_count() == 1
                assert ordinary[old][1] == ordinary[new][1]
                same_common_edges += 1
    chosen = [variants[choices[old[1].bit_length() - 1]][i]
              if old[1].bit_count() == 1 else old
              for i, old in enumerate(ordinary)]
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
                 common_context_frame_families=choices)
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['outputs'] = [(slot, aliases[g], c, target)
                        for slot, g, c, target in word['outputs']]
    fresh['events'] = [(slot, -1 if old < 0 else aliases[old], aliases[new])
                       for slot, old, new in word['events']]
    return fresh, chosen, dict(
        independently_checked_same_common_edges=same_common_edges,
        original_and_maximal_containment=True,
        every_actual_transition_containment=True,
        unchanged_R=word['R'], unchanged_XORs=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    configs = json.loads(args.input.read_text())
    rows = []
    started = time.monotonic()
    for config in configs:
        word, ordinary, maximal, _, successors, _, _ = parent(config['parent'])
        fresh, selected, summary = select_family_frames(
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
        with (work / 'native.log').open('wb') as log:
            subprocess.run([str(args.binary), str(transition), config['basis'],
                str(profile_path), str(audit)], check=True, stdout=log, stderr=subprocess.STDOUT)
        profile = json.loads(profile_path.read_text())
        a = config.get('screen_a', 1284995399 / 25000000000000)
        phi = sum(t * n * math.expm1(a * math.log(575 / t))
                  for t, n in enumerate(profile['blocks']) if t and n)
        rows.append(dict(status='EXACT CANDIDATE COMMON-CONTEXT FRAME FAMILY MIXTURE',
            config=config, summary=summary, independent=independent,
            profile=profile, screen_Phi=phi, screen_a=a,
            word_path=str(word_path), word_sha256=sha256(raw).hexdigest(),
            input_binary_sha256=sha256(transition.read_bytes()).hexdigest(),
            assignment_sha256=sha256(json.dumps(selected, separators=(',', ':')).encode()).hexdigest(),
            profile_path=str(profile_path), profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
            transition_audit=str(audit), transition_audit_sha256=sha256(audit.read_bytes()).hexdigest()))
        status = dict(completed=len(rows), total=len(configs), workers=1,
            elapsed_seconds=time.monotonic() - started, utc=datetime.now(timezone.utc).isoformat())
        (args.work / 'completed-rows.json').write_text(json.dumps(rows, indent=2) + '\n')
        (args.work / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
        print(json.dumps(dict(status, case_id=config['case_id'], Phi=phi)), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS ACTUAL COMMON-CONTEXT MULTIFAMILY WORD COHORT', rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Actual mutually compatible signed-frame families selected by common '
              'context, full both-dirty/source/output replay, all physical inclusions '
              'and full native CRT profiles. Fresh scalar-source regeneration, '
              'independent Fraction, DATA/stock/moment/assembly binding and inherited '
              'all-size interfaces remain separate acceptance gates.'), indent=2) + '\n')


if __name__ == '__main__':
    main()
