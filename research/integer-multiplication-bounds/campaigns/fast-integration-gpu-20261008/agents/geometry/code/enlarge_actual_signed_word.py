#!/usr/bin/env python3
"""Actual signed-word closure after a changed physical carrier matching.

The current signed spaces are mandatory lower bounds. No original-envelope
schedule is substituted for the new physical word. Every actual transition
and terminal annihilator constrains the newly computed upper partition.
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
import sys
import time

GRAPH = Path(__file__).resolve().parents[2] / 'graph' / 'code'
sys.path.insert(0, str(GRAPH))
from check_compiled_witness import contained
from joint_word_check_v4 import check

UPPER_CACHE = {}


def actual_upper_spaces(word, only_one_core=False):
    cache_key = id(word), only_one_core
    if cache_key in UPPER_CACHE:
        return UPPER_CACHE[cache_key]
    h = word['h']
    assert word['frame_format'] == 'positive-signed-v1'
    lower = [(r, forced, tuple(symbols)) for r, forced, symbols in word['frames']]
    n = len(lower)
    successors = [set() for _ in lower]
    predecessors = [set() for _ in lower]
    constraints = [set() for _ in lower]
    for slot, old, new in word['events']:
        if old >= 0 and old != new:
            assert contained(lower[old], lower[new])
            successors[old].add(new)
            predecessors[new].add(old)
    for slot, g, common, target in word['outputs']:
        assert lower[g][1] == 1 << common
        if len(target) == 3:
            constraints[g].add(tuple(sorted(i for i in target if i != common)))
    queue = deque(i for i in range(n) if constraints[i])
    queued = set(queue)
    while queue:
        new = queue.popleft()
        queued.remove(new)
        for old in predecessors[new]:
            additions = constraints[new] - constraints[old]
            if additions:
                constraints[old].update(additions)
                if old not in queued:
                    queue.append(old)
                    queued.add(old)
    upper = []
    for i, (rank, forced, symbols) in enumerate(lower):
        if forced.bit_count() == 3 or (only_one_core and forced.bit_count() != 1):
            upper.append(lower[i])
            continue
        assert forced.bit_count() in (1, 2)
        adjacency = [set() for _ in range(h)]
        for a, b in constraints[i]:
            assert not (forced >> a & 1 or forced >> b & 1)
            adjacency[a].add(b)
            adjacency[b].add(a)
        colors = [-1]*h
        parts = []
        for a in range(h):
            if forced >> a & 1 or colors[a] >= 0:
                continue
            colors[a] = 0
            todo = [a]
            positive, negative, odd = [], [], False
            while todo:
                b = todo.pop()
                (positive if colors[b] == 0 else negative).append(b)
                for j in sorted(adjacency[b]):
                    if colors[j] < 0:
                        colors[j] = 1-colors[b]
                        todo.append(j)
                    elif colors[j] == colors[b]:
                        odd = True
            if not odd:
                parts.append((positive, negative))
        labels = [int(forced >> j & 1) for j in range(h)]
        for label, (positive, negative) in enumerate(parts, 2):
            for j in positive:
                labels[j] = label
            for j in negative:
                labels[j] = -label
        frame = (len(parts), forced, tuple(labels))
        assert contained(lower[i], frame), 'Actual selected lower space escaped new upper closure'
        upper.append(frame)
    for old, targets in enumerate(successors):
        for new in targets:
            assert contained(upper[old], upper[new]), 'New upper spaces are not physically nested'
    result = lower, upper, successors, dict(
        actual_frame_classes=n,
        actual_transition_types=sum(map(len, successors)),
        current_signed_space_containment=True,
        every_new_upper_transition_containment=True,
        terminal_constraints_propagated_to_fixed_point=True,
        non_single_core_spaces_protected=only_one_core)
    UPPER_CACHE[cache_key] = result
    return result


def enlarge_actual(word, pairs, threshold=0, mode='all', core_mode='pair'):
    assert core_mode in ('pair', 'one-core', 'none')
    only_one_core = core_mode == 'one-core'
    lower, upper, successors, initial_receipt = actual_upper_spaces(word, only_one_core)
    receipt = dict(initial_receipt)
    h = word['h']
    assert mode in ('all', 'balanced', 'unbalanced')
    assert all(len(pair) == 2 and len(set(pair)) == 2 and
               all(0 <= i < h for i in pair) for pair in pairs)
    masks = {sum(1 << j for j in pair) for pair in pairs}
    classes, active = [], []
    initial_splits = 0
    for before, maximum in zip(lower, upper):
        grouped = {}
        for j, label in enumerate(maximum[2]):
            if abs(label) > 1:
                grouped.setdefault(abs(label), []).append(j)
        chosen = {abs(maximum[2][j]) for j in range(h) if abs(before[2][j]) > 1}
        assert chosen <= grouped.keys()
        assert all(all(abs(before[2][j]) > 1 for j in grouped[label]) for label in chosen)
        initial_splits += len(chosen)-before[0] if before[1].bit_count() != 3 else 0
        classes.append(grouped)
        active.append(chosen)
    seeded = 0
    for i, before in enumerate(lower):
        seed = ((core_mode == 'pair' and before[1] in masks) or
                (core_mode == 'one-core' and before[1].bit_count() == 1))
        if seed and before[0] >= threshold:
            additions = set(classes[i])-active[i]
            if mode != 'all':
                additions = {label for label in additions if
                    (sum(1 if upper[i][2][j] > 0 else -1 for j in classes[i][label]) == 0)
                    == (mode == 'balanced')}
            seeded += len(additions)
            active[i].update(additions)

    def frame(i):
        maximum = upper[i]
        if maximum[1].bit_count() == 3:
            return maximum
        return (len(active[i]), maximum[1], tuple(label if abs(label) <= 1 or
                abs(label) in active[i] else 0 for label in maximum[2]))

    def support(i):
        maximum = upper[i]
        if maximum[1].bit_count() == 3:
            return maximum[1]
        bits = 0
        unbalanced = False
        for label in active[i]:
            indices = classes[i][label]
            bits |= sum(1 << j for j in indices)
            unbalanced |= sum(1 if maximum[2][j] > 0 else -1 for j in indices) != 0
        return bits | (maximum[1] if unbalanced else 0)

    queue = deque(range(len(lower)))
    queued = set(queue)
    propagated = 0
    while queue:
        old = queue.popleft()
        queued.remove(old)
        source_support = support(old)
        for new in successors[old]:
            if upper[new][1].bit_count() == 3:
                assert contained(frame(old), frame(new))
                continue
            outside = source_support & ~upper[new][1]
            needed = {abs(upper[new][2][j]) for j in range(h) if outside >> j & 1}
            assert all(label > 1 for label in needed)
            additions = needed-active[new]
            if additions:
                assert not only_one_core or upper[new][1].bit_count() == 1, 'Protected non-single frame needed enlargement'
                active[new].update(additions)
                propagated += len(additions)
                if new not in queued:
                    queue.append(new)
                    queued.add(new)
    chosen = [frame(i) for i in range(len(lower))]
    for before, selected, maximum in zip(lower, chosen, upper):
        assert contained(before, selected) and contained(selected, maximum)
        if only_one_core and before[1].bit_count() != 1:
            assert contained(selected, before), 'Protected non-single-core space changed'
    for old, targets in enumerate(successors):
        for new in targets:
            assert contained(chosen[old], chosen[new])
    source_roles = set(word['sources'].values())
    for slot, before, after in word['events']:
        if before < 0 and slot in source_roles:
            assert contained(chosen[after], lower[after])
    for slot, g, c, target in word['outputs']:
        if len(target) == 1:
            assert contained(chosen[g], lower[g])
    aliases, frames, lookup = [], [], {}
    for selected in chosen:
        if selected not in lookup:
            lookup[selected] = len(frames)
            frames.append(selected)
        aliases.append(lookup[selected])
    fresh = dict(word)
    old_aliases = word.get('physical_region_address_aliases')
    fresh.update(frames=frames, physical_region_address_aliases=
                 [aliases[i] for i in old_aliases] if old_aliases is not None else aliases,
                 actual_signed_word_growth=dict(pairs=pairs, threshold=threshold,
                                                component_mode=mode,
                                                core_mode=core_mode))
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['events'] = [(slot, -1 if old < 0 else aliases[old], aliases[new])
                       for slot, old, new in word['events']]
    fresh['outputs'] = [(slot, aliases[g], c, target)
                       for slot, g, c, target in word['outputs']]
    receipt.update(initial_partition_split_classes=initial_splits,
                   seeded_pair_classes=seeded, forward_closure_classes=propagated,
                   unchanged_R=word['R'], unchanged_every_XOR=True,
                   source_and_copied_center_spaces_unchanged=True)
    return fresh, chosen, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    rows, seen = [], set()
    cache = {}
    started = time.monotonic()
    for config in json.loads(args.input.read_text()):
        parent = config['parent']
        key = parent['word_sha256']
        if key not in cache:
            raw = gzip.decompress(Path(parent['word_path']).read_bytes())
            assert sha256(raw).hexdigest() == key
            cache[key] = json.loads(raw)
        word = cache[key]
        work = args.work / config['case_id']
        work.mkdir()
        try:
            fresh, selected, summary = enlarge_actual(word, config.get('pairs', []),
                config.get('threshold', 0), config.get('component_mode', 'all'),
                config.get('core_mode', 'pair'))
            signature = sha256(json.dumps(selected, separators=(',', ':')).encode()).hexdigest()
            identity = key, signature, config['basis']
            if identity in seen:
                row = dict(status='NEGATIVE: DUPLICATE ACTUAL SIGNED ASSIGNMENT',
                           config=config, summary=summary, assignment_sha256=signature)
            else:
                seen.add(identity)
                raw = (json.dumps(fresh, separators=(',', ':'))+'\n').encode()
                word_path = work / 'word.json.gz'
                with word_path.open('wb') as stream:
                    with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as output:
                        output.write(raw)
                transition = work / 'signed-transitions.bin'
                independent = check(word_path, transition)
                profile_path, audit = work / 'profile.json', work / 'transitions.json'
                with (work / 'native.log').open('wb') as log:
                    subprocess.run([str(args.binary), str(transition), config['basis'],
                                    str(profile_path), str(audit)], check=True,
                                   stdout=log, stderr=subprocess.STDOUT)
                profile = json.loads(profile_path.read_text())
                a = config['screen_a']
                phi = sum(t*n*math.expm1(a*math.log(575/t))
                          for t, n in enumerate(profile['blocks']) if t and n)
                row = dict(status='EXACT CANDIDATE ACTUAL SIGNED MATCHING WORD GROWTH',
                           config=config, summary=summary, independent=independent,
                           assignment_sha256=signature, word_path=str(word_path),
                           word_sha256=sha256(raw).hexdigest(),
                           input_binary_sha256=sha256(transition.read_bytes()).hexdigest(),
                           profile=profile, profile_path=str(profile_path),
                           profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
                           transition_audit=str(audit),
                           transition_audit_sha256=sha256(audit.read_bytes()).hexdigest(),
                           screen_Phi=phi, screen_a=a)
        except AssertionError as error:
            row = dict(status='REJECTED ACTUAL SIGNED WORD GROWTH', config=config,
                       rejection=str(error), phase='Upper, lower, source/center or '
                       'literal transition/source/dirty checks; no accepted score.')
        rows.append(row)
        (args.work / 'completed-rows.json').write_text(json.dumps(rows, indent=2)+'\n')
        status = dict(completed=len(rows), utc=datetime.now(timezone.utc).isoformat(),
                      elapsed_seconds=time.monotonic()-started)
        (args.work / 'status.json').write_text(json.dumps(status, indent=2)+'\n')
        print(json.dumps(dict(status, case=config['case_id'],
                              outcome=row['status'], Phi=row.get('screen_Phi'))), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='COMPLETE ACTUAL SIGNED WORD GROWTH COHORT',
        rows=rows, source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Actual changed-matching signed lower spaces, newly derived literal-word '
              'upper partitions, physical/source/dirty replay and complete native CRT. '
              'Independent fresh-source generation, Fraction/data/stock/moment/assembly '
              'binding and inherited all-size assumptions remain separate.'), indent=2)+'\n')


if __name__ == '__main__':
    main()
