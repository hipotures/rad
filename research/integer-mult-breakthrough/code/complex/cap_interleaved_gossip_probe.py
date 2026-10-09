#!/usr/bin/env python3
"""Exact zero-excess interleaving screen for a genuine four-cap incidence.

Each root is the selected j4 row at a different five-pair source cube.
The four targets contain four common paired points and one distinct point.
Root r contributes to every target except r. Frames grow only by same-frame
scalar read unions; no output mixing, copies or frame drops are allowed.
"""

import argparse
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import time


def basis(values):
    pivots = {}
    for value in values:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def source_label(cube, selector):
    return sum(1 << (2 * pair + ((selector >> i) & 1))
               for i, pair in enumerate(cube))


def instance(n):
    cubes = [tuple(range(4)) + (4 + r,) for r in range(n)]
    targets = [sum(1 << (2 * i) for i in cube) for cube in cubes]
    supports = [[source_label(cube, selector) for selector in range(32)
                 if not ((selector & 15).bit_count() & 1)] for cube in cubes]
    caps = [basis(values) for values in supports]
    if any(len(cap) != 5 for cap in caps):
        raise AssertionError('The concrete j4 cap has incorrect dimension')
    compatible = [[all(not ((value & target).bit_count() & 1) for value in cap)
                   for target in targets] for cap in caps]
    if compatible != [[r != t for t in range(n)] for r in range(n)]:
        raise AssertionError('The paired-five cap incidence is not complement identity')
    for r, values in enumerate(supports):
        for t, target in enumerate(targets):
            if r == t:
                continue
            weights = [-(int((value & target).bit_count()) - 1)
                       * (int((value & target).bit_count()) - 3) for value in values]
            if any(w not in (-3, 1) for w in weights):
                raise AssertionError('The genuine side row is not the selected j4 row')
    return cubes, targets, caps, compatible


def search(compatible):
    n = len(compatible)
    edges = [(r, t) for r in range(n) for t in range(n) if compatible[r][t]]
    outgoing = [sum(1 << i for i, (a, b) in enumerate(edges) if a == r) for r in range(n)]
    forbidden = [sum(1 << r for r in range(n) if not compatible[r][t]) for t in range(n)]
    full = (1 << len(edges)) - 1
    visited = 0

    @lru_cache(None)
    def solve(done, root_known, target_known):
        nonlocal visited
        visited += 1
        if done == full:
            return ()
        for r in range(n):
            for i, (a, t) in enumerate(edges):
                if a == r and not done & (1 << i) and root_known[r] & forbidden[t]:
                    return None
        for i, (r, t) in enumerate(edges):
            if done & (1 << i):
                continue
            known = root_known[r] | target_known[t]
            if known & forbidden[t]:
                continue
            changed_root, changed_target = list(root_known), list(target_known)
            changed_root[r] = changed_target[t] = known
            answer = solve(done | (1 << i), tuple(changed_root), tuple(changed_target))
            if answer is not None:
                return ((r, t),) + answer
        return None

    answer = solve(0, tuple(1 << r for r in range(n)), (0,) * n)
    return answer, visited, solve.cache_info()._asdict()


def replay(caps, targets, word):
    root_frames, target_frames = list(caps), [()] * len(caps)
    paid = sum(len(cap) for cap in caps)
    events = []
    for r, t in word:
        common = basis(root_frames[r] + target_frames[t])
        if any((value & targets[t]).bit_count() & 1 for value in common):
            raise AssertionError('The proposed interleaving crossed a target cap')
        charge = 2 * len(common) - len(root_frames[r]) - len(target_frames[t])
        paid += charge
        root_frames[r] = target_frames[t] = common
        events.append({'root': r, 'target': t, 'common_label_dimension': len(common),
                       'growth_rank_charge': charge})
    h = 2 * (4 + len(caps))
    # Finish roots and outputs at full. All changes were nested and the total
    # bill telescopes to h per complete stock role, with no extra frame credit.
    paid += sum(h - len(frame) for frame in root_frames + target_frames)
    if paid != 2 * len(caps) * h:
        raise AssertionError('A zero-excess monotone schedule did not telescope')
    return {'events': events, 'complete_root_and_target_stock': 2 * len(caps),
            'ambient_label_width': h, 'complete_geodesic_rank_bill': paid,
            'rank_excess': 0}


def probe(n):
    cubes, targets, caps, compatible = instance(n)
    word, visited, cache = search(compatible)
    result = {'root_count': n, 'target_count': n, 'five_pair_source_cubes': cubes,
              'actual_targets': targets, 'initial_cap_bases': caps,
              'required_compatible_reads': n * (n - 1),
              'initial_target_frames': 'zero (optimistic; central and external contributions omitted)',
              'complete_search_states': visited, 'memoization': cache,
              'zero_excess_schedule_exists': word is not None}
    if word is not None:
        result['zero_excess_schedule'] = word
        result['literal_nested_frame_replay'] = replay(caps, targets, word)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    path = Path(__file__).resolve(); frozen = path.read_bytes()
    start, timer = datetime.now(timezone.utc).isoformat(), time.perf_counter()
    rows = [probe(n) for n in (2, 3, 4)]
    if path.read_bytes() != frozen:
        raise AssertionError('Effective source changed')
    result = {'status': 'COMPLETE exact zero-excess paired-cap interleaving screen',
              'started_utc': start, 'completed_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': time.perf_counter() - timer, 'source_sha256': sha256(frozen).hexdigest(),
              'cases': rows,
              'scope': 'Exact nested common-frame growth schedules on concrete j4 paired-five incidences, with optimistic zero target frames. Scalar values, arbitrary-dirty core echo, copies, target mixing and a native supplier remain separate.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'seconds': result['seconds'],
                      'results': [(r['root_count'], r['zero_excess_schedule_exists'], r['complete_search_states']) for r in rows]}), flush=True)


if __name__ == '__main__':
    main()
