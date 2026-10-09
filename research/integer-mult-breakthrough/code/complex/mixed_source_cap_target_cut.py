#!/usr/bin/env python3
"""Price a separate side bank and a direct target-cap cut after all centers.

This changed local chronology reuses the immutable mixed-splice definitions
as input. All complete center copies occur at Y0 before the side targets
grow. Four independent side helpers then read at the identical actual cap,
paying their whole stock but no additional copied-side child. It does not
implement a full paired universe, a global target clock or a native master.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import mixed_source_center_cap_splice as base


def build():
    original, meta = base.build(False)
    first_side = next(i for i, event in enumerate(original)
                      if event['stage'] == 'late side bucket')
    first_cleanup = next(i for i, event in enumerate(original)
                         if event['stage'] == 'helpers full after side inverse')
    first_K_sink = next(i for i, event in enumerate(original)
                        if event['stage'] == 'K target continuation')
    prefix = original[:first_side]
    helpers = original[first_cleanup:first_K_sink]
    side_roles = set(meta['side_helpers'])
    center = [event for event in helpers if event['kind'] != 'frame'
              or event['role'] not in side_roles]
    side_retirements = [event for event in helpers if event['kind'] == 'frame'
                        and event['role'] in side_roles]
    side = []
    cap = list(meta['side_cap'])
    for event in original[first_side:first_cleanup]:
        if event['stage'] != 'paid cap copy read':
            side.append(event)
            continue
        for target, c in event['decoder']:
            side.append({'kind': 'frame', 'role': target, 'from': [], 'to': cap,
                         'stage': 'direct side target common-cap entrance'})
            side.append({'kind': 'add', 'target': target, 'source': event['root'],
                         'coefficient': str(Q(c) * event['sign']),
                         'stage': 'direct side at common actual cap'})
    tail = original[first_K_sink:]
    for event in tail:
        if event['stage'] == 'outside target final kernel':
            event = dict(event, **{'from': cap})
        side.append(event)
    events = prefix + center + side[:len(side)-len(tail)] + side_retirements + side[-len(tail):]
    current = list(meta['initial_frames'])
    for event in events:
        if event['kind'] == 'frame':
            if current[event['role']] != tuple(event['from']):
                raise AssertionError('A changed target-cut transition starts at the wrong anchor')
            current[event['role']] = tuple(event['to'])
        elif event['kind'] == 'add':
            if current[event['target']] != current[event['source']]:
                raise AssertionError('A direct side/center gate lacks identical actual frames')
        elif event['kind'] == 'copy':
            if current[event['root']] != tuple(event['root_subspace']):
                raise AssertionError('A center/old side copy has a wrong source frame')
            if any(current[t] for t, c in event['decoder'] if Q(c)):
                raise AssertionError('A center copy left its common zero target cut')
    if current != meta['final_frames']:
        raise AssertionError('A target cut changed a persistent endpoint')
    return events, meta


def probe():
    events, meta = build()
    h, roles, n = meta['h'], meta['roles'], meta['n']
    expected = [[Q(i == j) for j in range(roles)] for i in range(roles)]
    for u in range(n):
        expected[n + u][u] += 1
    if base.scalar_matrix(events, roles) != expected:
        raise AssertionError('The changed cut failed complete scalar source/dirty columns')
    cache, profile = {}, Counter()
    for event in events:
        edges = [(tuple(event['from']), tuple(event['to']))] if event['kind'] == 'frame' else [(tuple(event['root_subspace']), ())] if event['kind'] == 'copy' else []
        for E, F in edges:
            rank = 2 * len(base.frames.basis(E + F)) - len(E) - len(F)
            if rank:
                profile[rank] += 1
            for A, B in ((E, F), (F, E)):
                if (A, B) not in cache:
                    normal = base.interfaces.compile_interface(A, B, h)
                    literal = base.interfaces.inverse_word(base.interfaces.literal_word(A, h)) + base.interfaces.literal_word(B, h)
                    paulis = base.interfaces.assert_complete_tableau(normal, literal)
                    cache[A, B] = {'normal': normal, 'word': base.interfaces.compiled_word(normal), 'Pauli_images': paulis}
    virtual = [base.Stream(4, [[(17 * role + 7 * address + 3 * component) % 37 - 18
                               for component in range(8)] for address in range(1 << h)])
               for role in range(roles)]
    initial = [base.apply_word(row, base.interfaces.literal_word(E, h), h)
               for row, E in zip(virtual, meta['initial_frames'])]
    desired_virtual = list(virtual)
    for u in range(n):
        desired_virtual[n + u] = desired_virtual[n + u].plus(virtual[u])
    desired = [base.apply_word(row, base.interfaces.literal_word(E, h), h)
               for row, E in zip(desired_virtual, meta['final_frames'])]
    actual = base.execute(events, initial, h, cache)
    restored = base.execute(events, actual, h, cache, reverse=True)
    if not all(a.same(b) for a, b in zip(actual, desired)) or not all(a.same(b) for a, b in zip(restored, initial)):
        raise AssertionError('The literal four-field target-cut word or inverse failed')
    negatives = {}
    for name in ('missing_K_inverse', 'missing_side_old', 'missing_side_unmix'):
        wrong = base.execute(events, initial, h, cache, negative=name)
        if all(a.same(b) for a, b in zip(wrong, desired)):
            raise AssertionError('A dirty/current-source omission was invisible')
        negatives[name] = True
    rank = sum(r * count for r, count in profile.items())
    if rank != h * roles - 18 + 7 * h:
        raise AssertionError('The independent side stock, target cut or center copy price is wrong')
    return {'metadata': meta, 'complete_forward_child_profile': dict(profile),
            'complete_forward_rank': rank, 'ambient_role_capacity_one_core': h * roles,
            'local_endpoint_discount': 18, 'center_copy_extra_rank': 49,
            'side_copy_extra_rank': 0, 'complete_scalar_column_entries_checked': roles * roles,
            'four_field_components_forward_and_reverse': 2 * 8 * roles * (1 << h),
            'unique_normal_forms': len(cache),
            'actual_Pauli_images': sum(row['Pauli_images'] for row in cache.values()),
            'negative_controls': negatives, 'events': events,
            'actual_normal_forms': [row['normal'] for row in cache.values()],
            'scope': 'Local component pays four independent side helper roles; center cut before actual-cap side cut. Not a global formation/readout/master or exponent.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    paths = [Path(__file__).resolve(), Path(base.__file__).resolve(), Path(base.frames.__file__).resolve(),
             Path(base.interfaces.__file__).resolve(), Path(base.paired.__file__).resolve()]
    frozen = {p: p.read_bytes() for p in paths}
    started, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    result = {'status': 'PASS paid independent-bank target-cap cut', 'case': probe()}
    if any(p.read_bytes() != content for p, content in frozen.items()):
        raise AssertionError('Changed target-cut source closure during execution')
    result.update(started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
                  seconds=time.perf_counter() - timer,
                  source_sha256={p.name: sha256(content).hexdigest() for p, content in frozen.items()})
    result = base.paired_serializable(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'roles': result['case']['metadata']['roles'], 'rank': result['case']['complete_forward_rank']}), flush=True)


if __name__ == '__main__':
    main()
