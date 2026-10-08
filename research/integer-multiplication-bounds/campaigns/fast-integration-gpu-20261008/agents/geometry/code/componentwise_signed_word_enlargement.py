#!/usr/bin/env python3
"""Componentwise positive-frame retention on an actual executed joint word.

Keep every class required by the original core/cover space. Select additional
signed classes individually, then propagate precisely the recipient classes
needed by every actual directed address transition. The final full rational
containment check is independent of the support propagation shortcut.
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
from joint_positive_frontier import parent
from joint_word_check_v4 import check


def enlarge_components(word, ordinary, maximal, successors, mode, threshold, scope):
    h = word['h']
    classes = []
    active = []
    required = []
    for old, maximum in zip(ordinary, maximal):
        _, forced, symbols = maximum
        grouped = {}
        for i, label in enumerate(symbols):
            if abs(label) > 1:
                grouped.setdefault(abs(label), []).append(i)
        needed = {abs(symbols[i]) for i in range(h) if abs(old[2][i]) > 1}
        assert needed <= grouped.keys()
        # Covered source coordinates were individually independent in E(C,M).
        assert all(len(grouped[label]) == 1 for label in needed)
        classes.append(grouped)
        required.append(set(needed))
        active.append(set(needed))

    seeded = 0
    for fid, (old, maximum, grouped) in enumerate(zip(ordinary, maximal, classes)):
        if old[1].bit_count() == 3 or old[0] < threshold:
            continue
        if scope == 'core-single' and old[1].bit_count() != 1:
            continue
        for label, indices in grouped.items():
            if label in required[fid]:
                continue
            signed_sum = sum(1 if maximum[2][i] > 0 else -1 for i in indices)
            choose = {
                'balanced': signed_sum == 0,
                'unbalanced': signed_sum != 0,
                'singleton': len(indices) == 1,
                'multi': len(indices) > 1,
                'boundary': max(indices) >= h - 3,
                'interior': max(indices) < h - 3,
            }[mode]
            if choose:
                active[fid].add(label)
                seeded += 1

    def frame(fid):
        maximum = maximal[fid]
        if maximum[1].bit_count() == 3:
            return maximum
        symbols = tuple(label if abs(label) <= 1 or abs(label) in active[fid]
            else 0 for label in maximum[2])
        return (len(active[fid]), maximum[1], symbols)

    def support(fid):
        maximum = maximal[fid]
        if maximum[1].bit_count() == 3:
            return maximum[1]
        result = 0
        unbalanced = False
        for label in active[fid]:
            indices = classes[fid][label]
            result |= sum(1 << i for i in indices)
            unbalanced |= sum(1 if maximum[2][i] > 0 else -1 for i in indices) != 0
        return result | (maximum[1] if unbalanced else 0)

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
            needed = set()
            outside = support_old & ~recipient[1]
            for i in range(h):
                if outside >> i & 1:
                    label = abs(recipient[2][i])
                    assert label > 1
                    needed.add(label)
            additions = needed - active[new]
            if additions:
                active[new].update(additions)
                propagated += len(additions)
                if new not in queued:
                    queue.append(new)
                    queued.add(new)
    chosen = [frame(fid) for fid in range(len(ordinary))]
    for old, maximum, selected in zip(ordinary, maximal, chosen):
        assert contained(old, selected) and contained(selected, maximum)
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
        componentwise_enlargement=dict(mode=mode, threshold=threshold, scope=scope))
    fresh['ops'] = [(a, b, aliases[g]) for a, b, g in word['ops']]
    fresh['outputs'] = [(slot, aliases[g], c, target) for slot, g, c, target in word['outputs']]
    fresh['events'] = [(slot, -1 if old < 0 else aliases[old], aliases[new])
        for slot, old, new in word['events']]
    summary = dict(seeded_components=seeded, propagated_components=propagated,
        extra_components=sum(len(a - r) for a, r in zip(active, required)),
        original_E_containment=True, maximal_signed_containment=True,
        every_actual_transition_containment=True,
        unchanged_all_XOR_instructions=True, unchanged_physical_roles=word['R'])
    return fresh, summary, chosen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    rows, claimed = [], set()
    started = time.monotonic()
    for config in json.loads(args.input.read_text()):
        word, ordinary, maximal, ranks, successors, terminals, inherited = parent(config['parent'])
        fresh, summary, selected = enlarge_components(word, ordinary, maximal,
            successors, config['mode'], config['threshold'], config['scope'])
        signature = sha256(json.dumps(selected, separators=(',', ':')).encode()).hexdigest()
        identity = (config['parent']['word_sha256'], tuple(config['parent']['Q']), signature, config['basis'])
        if identity in claimed:
            rows.append(dict(config=config, status='DUPLICATE COMPLETE COMPONENT ASSIGNMENT', assignment_sha256=signature))
            continue
        claimed.add(identity)
        work = args.work / config['case_id']
        work.mkdir()
        raw = (json.dumps(fresh, separators=(',', ':')) + '\n').encode()
        word_path = work / 'word.json.gz'
        with word_path.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as compressed:
                compressed.write(raw)
        transition = work / 'signed-transitions.bin'
        independent = check(word_path, transition)
        profile_path, audit = work / 'profile.json', work / 'transitions.json'
        command = [str(args.binary), str(transition), config['basis'], str(profile_path), str(audit)]
        with (work / 'native.log').open('wb') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        profile = json.loads(profile_path.read_text())
        phi = sum(t * n * math.expm1(4e-5 * math.log(575 / t))
            for t, n in enumerate(profile['blocks']) if t and n)
        row = dict(status='EXACT CANDIDATE COMPONENTWISE SIGNED WORD PROFILE', config=config,
            summary=summary, independent=independent, profile=profile, Phi_at_a_4e_5=phi,
            assignment_sha256=signature, word_path=str(word_path), word_sha256=sha256(raw).hexdigest(),
            input_binary_sha256=sha256(transition.read_bytes()).hexdigest(),
            profile_path=str(profile_path), profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
            transition_audit=str(audit), transition_audit_sha256=sha256(audit.read_bytes()).hexdigest())
        rows.append(row)
        status = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(rows),
            total=len(json.loads(args.input.read_text())), elapsed_seconds=time.monotonic() - started, workers=1)
        (args.work / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
        (args.work / 'completed-rows.json').write_text(json.dumps(rows, indent=2) + '\n')
        print(json.dumps(dict(**status, case_id=config['case_id'], Phi_at_a_4e_5=phi, **summary)), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='PASS EXACT COMPONENTWISE SIGNED WORD COHORT',
        rows=rows, completed_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic() - started,
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Actual partial signed positive frames with original/maximal containment, '
            'all physical transitions, source/target support and both full arbitrary-dirty '
            'orientations. All actual native matrices CRT-certified. Complete independent '
            'source-only regeneration, DATA, scalar stock, moments and assembly are separate.'
    ), indent=2) + '\n')


if __name__ == '__main__':
    main()
