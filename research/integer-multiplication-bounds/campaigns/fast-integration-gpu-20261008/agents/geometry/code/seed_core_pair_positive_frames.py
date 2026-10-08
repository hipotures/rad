#!/usr/bin/env python3
"""Selective two-core frame growth with paid actual downstream profiles.

Seed distinct pair-core contexts into their actual maximal signed spaces.
Propagate only recipient signed classes needed by their supports. Preserve a
previously selected one-core family allocation, all roles and every XOR. No
score is accepted before complete source/dirty/frame/native reconstruction.
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

from componentwise_signed_word_enlargement import contained, parent, check
from mix_common_frame_families import select_family_frames


def enlarge_pair_contexts(word, ordinary, maximal, successors, choices, pairs,
                          threshold=0, component_mode='all'):
    _, base, _ = select_family_frames(word, ordinary, maximal, successors, choices)
    h = word['h']
    masks = {sum(1 << i for i in pair) for pair in pairs}
    assert all(len(pair) == 2 and len(set(pair)) == 2
               and all(0 <= i < h for i in pair) for pair in pairs)
    assert component_mode in ('all', 'balanced', 'unbalanced')
    classes, active = [], []
    for selected, maximum in zip(base, maximal):
        grouped = {}
        for i, label in enumerate(maximum[2]):
            if abs(label) > 1:
                grouped.setdefault(abs(label), []).append(i)
        chosen = {abs(maximum[2][i]) for i in range(h) if abs(selected[2][i]) > 1}
        assert chosen <= grouped.keys()
        assert all(all(abs(selected[2][i]) > 1 for i in grouped[label])
                   for label in chosen)
        classes.append(grouped)
        active.append(chosen)
    seeded = 0
    seeded_frames = 0
    for i, old in enumerate(ordinary):
        if old[1].bit_count() == 2 and old[1] in masks and old[0] >= threshold:
            additions = set(classes[i].keys() - active[i])
            if component_mode != 'all':
                additions = {label for label in additions if
                    (sum(1 if maximal[i][2][j] > 0 else -1
                         for j in classes[i][label]) == 0) == (component_mode == 'balanced')}
            seeded += len(additions)
            seeded_frames += bool(additions)
            active[i].update(additions)

    def frame(i):
        maximum = maximal[i]
        if maximum[1].bit_count() == 3:
            return maximum
        return (len(active[i]), maximum[1], tuple(label if abs(label) <= 1
            or abs(label) in active[i] else 0 for label in maximum[2]))

    def support(i):
        maximum = maximal[i]
        if maximum[1].bit_count() == 3:
            return maximum[1]
        bits = 0
        unbalanced = False
        for label in active[i]:
            indices = classes[i][label]
            bits |= sum(1 << j for j in indices)
            unbalanced |= sum(1 if maximum[2][j] > 0 else -1 for j in indices) != 0
        return bits | (maximum[1] if unbalanced else 0)

    queue = deque(range(len(ordinary)))
    queued = set(queue)
    propagated = 0
    while queue:
        old = queue.popleft()
        queued.remove(old)
        support_old = support(old)
        for new in sorted(successors[old]):
            recipient = maximal[new]
            if recipient[1].bit_count() == 3:
                assert contained(frame(old), frame(new))
                continue
            outside = support_old & ~recipient[1]
            needed = {abs(recipient[2][j]) for j in range(h) if outside >> j & 1}
            assert all(label > 1 for label in needed)
            additions = needed - active[new]
            if additions:
                active[new].update(additions)
                propagated += len(additions)
                if new not in queued:
                    queue.append(new)
                    queued.add(new)
    chosen = [frame(i) for i in range(len(ordinary))]
    for original, before, selected, maximum in zip(ordinary, base, chosen, maximal):
        assert contained(original, selected) and contained(before, selected)
        assert contained(selected, maximum)
    for old, targets in enumerate(successors):
        for new in targets:
            assert contained(chosen[old], chosen[new])
    aliases, frames, lookup = [], [], {}
    for selected in chosen:
        if selected not in lookup:
            lookup[selected] = len(frames)
            frames.append(selected)
        aliases.append(lookup[selected])
    fresh = dict(word)
    fresh.update(frame_format='positive-signed-v1', frames=frames,
        physical_region_address_aliases=aliases,
        core_pair_enlargement=dict(pairs=pairs, threshold=threshold,
                                  component_mode=component_mode, base_choices=choices))
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['outputs'] = [(slot, aliases[g], c, target)
                        for slot, g, c, target in word['outputs']]
    fresh['events'] = [(slot, -1 if old < 0 else aliases[old], aliases[new])
                       for slot, old, new in word['events']]
    return fresh, chosen, dict(seeded_pair_classes=seeded,
        seeded_pair_frames=seeded_frames, propagated_classes=propagated,
        original_base_and_maximal_containment=True,
        every_actual_transition_containment=True, unchanged_R=word['R'], unchanged_XORs=True)


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
    rows, seen = [], set()
    started = time.monotonic()
    for config in configs:
        word, ordinary, maximal, _, successors, _, _ = parent(config['parent'])
        fresh, selected, summary = enlarge_pair_contexts(
            word, ordinary, maximal, successors, config['choices'], config['pairs'],
            config.get('threshold', 0), config.get('component_mode', 'all'))
        signature = sha256(json.dumps(selected, separators=(',', ':')).encode()).hexdigest()
        identity = (config['parent']['word_sha256'], tuple(config['parent']['Q']),
                    signature, config['basis'])
        if not summary['seeded_pair_classes'] or identity in seen:
            rows.append(dict(config=config, summary=summary,
                status='NEGATIVE: NO NEW PAIR CAPACITY OR DUPLICATE ACTUAL ASSIGNMENT',
                assignment_sha256=signature))
        else:
            seen.add(identity)
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
            a = config.get('screen_a', 2570182773 / 50000000000000)
            phi = sum(t * n * math.expm1(a * math.log(575 / t))
                      for t, n in enumerate(profile['blocks']) if t and n)
            rows.append(dict(status='EXACT CANDIDATE SELECTIVE PAIR-CORE POSITIVE WORD',
                config=config, summary=summary, independent=independent,
                profile=profile, screen_a=a, screen_Phi=phi,
                word_path=str(word_path), word_sha256=sha256(raw).hexdigest(),
                assignment_sha256=signature,
                input_binary_sha256=sha256(transition.read_bytes()).hexdigest(),
                profile_path=str(profile_path), profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
                transition_audit=str(audit), transition_audit_sha256=sha256(audit.read_bytes()).hexdigest()))
        status = dict(completed=len(rows), total=len(configs), workers=1,
            elapsed_seconds=time.monotonic() - started, utc=datetime.now(timezone.utc).isoformat())
        (args.work / 'completed-rows.json').write_text(json.dumps(rows, indent=2) + '\n')
        (args.work / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
        print(json.dumps(dict(status, case_id=config['case_id'], **summary)), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        status='PASS SELECTIVE PAIR-CORE POSITIVE WORD COHORT', rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Actual selected two-core signed enlargement and its minimal class '
              'closure, all physical transitions and full source/output/dirty replay, '
              'complete native CRT profiles. Fresh source, independent Fraction, '
              'DATA/stock/moment/assembly and all-size interfaces remain separate.'), indent=2) + '\n')


if __name__ == '__main__':
    main()
