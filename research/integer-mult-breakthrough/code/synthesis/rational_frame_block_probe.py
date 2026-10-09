#!/usr/bin/env python3
"""Connected equal-frame block completion with all fixed chronological ports.

The scalar word is unchanged. One common rational frame is moved jointly at
all gates in a connected block. This is an ideal-cost discriminator; local-
ring compatibility, fallback and native fees are reported as obligations.
"""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import pr163_bit_frame_review as V
import pr163_paid_chain_probe as L
import rational_frame_completion as F
import rational_paid_chain_endpoints as P


def build_blocks(reference):
    L.initialize(reference, 999, 1000)
    s = L.STATE
    graph, word, frames = s['graph'], s['word'], s['frames']
    p1, events = set(word['phase1']), defaultdict(list)

    def operation(index):
        for role in word['ops'][index][:2]:
            events[role].append(('op', index, s['chosen'][index]))

    def root(index):
        events[word['rootroles'][index]].append(('root', index, word['root_frame'][index]))

    for i in sorted(p1):
        operation(i)
    for j, item in enumerate(graph['roots']):
        if item['kind'] == 'center':
            root(j)
    for i in range(len(word['ops'])):
        if i not in p1:
            operation(i)
    for j, item in enumerate(graph['roots']):
        if item['kind'] != 'center':
            root(j)
    parent = list(range(len(word['ops'])))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[max(a, b)] = min(a, b)

    for sequence in events.values():
        for first, second in zip(sequence, sequence[1:]):
            if first[0] == second[0] == 'op' and frames.B[first[2]] == frames.B[second[2]]:
                union(first[1], second[1])
    groups = defaultdict(list)
    for index in range(len(word['ops'])):
        groups[find(index)].append(index)
    changed = {index for index, basis in V.read_inputs(reference)[-1]['frames']}
    source_starts = {role: word['source_frame'][int(source)] for source, role in word['sources'].items()}
    starts = dict(source_starts)
    starts.update({g['role']: g['frame'] for g in word['gauges']})
    selected = [members for members in groups.values() if changed.intersection(members)]
    shapes, locked, specs = {}, 0, []
    for members in selected:
        membership = set(members)
        current = s['chosen'][members[0]]
        V.require(all(frames.B[s['chosen'][i]] == frames.B[current] for i in members), 'Uniform connected-block frame')
        roles = sorted({role for i in members for role in word['ops'][i][:2]})
        before, after, ports = [], [], []
        for role in roles:
            sequence = events[role]
            position = 0
            while position < len(sequence):
                event = sequence[position]
                if event[0] != 'op' or event[1] not in membership:
                    position += 1
                    continue
                first = position
                while position < len(sequence) and sequence[position][0] == 'op' and sequence[position][1] in membership:
                    position += 1
                previous = starts.get(role) if first == 0 else sequence[first - 1][2]
                following = word['full_frame'] if position == len(sequence) else sequence[position][2]
                before.append(previous); after.append(following)
                ports.append(dict(role=role, first_operation=sequence[first][1], last_operation=sequence[position - 1][1]))
        signals = 0
        for index in members:
            signals |= s['supports'][word['ops'][index][2]]
        lower_rows = [row for frame in before if frame is not None for row in frames.B[frame]]
        lower_rows.extend(s['chi'][source] for source in V.bits(signals))
        lower, unused = V.echelon(lower_rows, graph['h'])
        upper = V.annihilator([row for frame in after for row in frames.A[frame]], graph['h'])
        d = frames.dim[current]
        V.require(len(lower) <= d <= len(upper), 'Block contains all lower spans and future caps')
        before_dimensions = [0 if frame is None else frames.dim[frame] for frame in before]
        after_dimensions = [frames.dim[frame] for frame in after]
        signature = (len(members), d, len(lower), len(upper), tuple(sorted(zip(before_dimensions, after_dimensions))))
        if len(lower) == d == len(upper):
            locked += 1
            continue
        if signature in shapes:
            shapes[signature] += 1
            continue
        shapes[signature] = 1
        specs.append(dict(block_id=members[0], operation_indices=members, current_dimension=d,
                          lower=lower, upper=upper, previous_dimensions=before_dimensions,
                          following_dimensions=after_dimensions, chronological_ports=ports,
                          conservative_source_count=signals.bit_count(), current_basis=frames.B[current]))
    summary = dict(total_operation_components=len(groups), components_touching_retained_descents=len(selected),
                   retained_changed_operations=len(changed), covered_operations=sum(map(len, selected)),
                   completely_dimension_locked_components=locked, distinct_unlocked_port_shapes=len(specs),
                   largest_selected_block=max(map(len, selected), default=0),
                   symmetry_repeats_omitted=sum(count - 1 for count in shapes.values()))
    return summary, specs


def probe(task):
    spec, h, numerator, denominator = task
    started, G = time.monotonic(), F.form(h)
    result = P.endpoint_frames(spec['lower'], spec['upper'], G)
    V.require(result['minimal_dimension'] is not None, 'Existing block cannot have an impossible rational cut')
    current = spec['current_dimension']
    previous, following = spec['previous_dimensions'], spec['following_dimensions']
    old_widths = P.widths(current, previous, following)
    old_interval = P.moment_interval(old_widths, numerator, denominator, 48)
    candidates = []
    for name, dimension, basis in [('minimum', result['minimal_dimension'], result['completion']),
                                   ('maximum', result['maximum_dimension'], result['maximum_completion'])]:
        candidate_widths = P.widths(dimension, previous, following)
        interval = P.moment_interval(candidate_widths, numerator, denominator, 48)
        V.require(sum(candidate_widths) == sum(old_widths), 'Complete block rank telescopes unchanged')
        integer_basis, denominators = P.cleared_basis(basis)
        sums = list(map(sum, integer_basis))
        gram = [[9 * V.dot(a, b) - sums[i] * sums[j] for j, b in enumerate(integer_basis)]
                for i, a in enumerate(integer_basis)]
        det = V.determinant(gram)
        V.require(det != 0 and F.contained(spec['lower'], basis, h)
                  and F.contained(basis, spec['upper'], h), 'All block ports and exact Gram bound')
        gain = 3 * (old_interval[0] - interval[1])
        delta = Counter(candidate_widths)
        delta.subtract(Counter(old_widths))
        candidates.append(dict(endpoint=name, dimension=dimension,
                               ideal_moment_gain_lower=str(gain), strictly_improving_ideal=gain > 0,
                               histogram_delta={r: 3 * n for r, n in sorted(delta.items()) if n},
                               positive_edge_delta=3 * (len(candidate_widths) - len(old_widths)),
                               clearing_denominators=list(denominators), cleared_Gram_determinant=det,
                               cleared_Gram_bits=abs(det).bit_length(),
                               exact_basis=F.encoded(basis) if gain > 0 else None))
    return dict(block_id=spec['block_id'], operation_indices=spec['operation_indices'],
                old_dimension=current, attainable_dimensions=[result['minimal_dimension'], result['maximum_dimension']],
                lower_radical_dimension=len(result['lower_radical']), old_width_histogram=dict(Counter(old_widths)),
                ports=spec['chronological_ports'], source_count=spec['conservative_source_count'],
                candidates=candidates, seconds=time.monotonic() - started)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=12)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--power', type=Q, default=Q(999, 1000))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    V.require(args.limit > 0 and args.workers > 0 and 0 < args.power < 1, 'Bounded block experiment configuration')
    files = [Path(__file__).resolve(), Path(V.__file__).resolve(), Path(L.__file__).resolve(),
             Path(F.__file__).resolve(), Path(P.__file__).resolve()]
    hashes = {file.name: sha256(file.read_bytes()).hexdigest() for file in files}
    args.output.mkdir(parents=True, exist_ok=False)
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_closure=hashes,
                    reference_inputs=V.INPUTS, power=str(args.power), limit=args.limit, workers=args.workers,
                    scope='Connected equal-frame blocks at fixed outside ports, ideal moment only')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    started = time.monotonic()
    preflight, specs = build_blocks(args.reference)
    (args.output / 'preflight.json').write_text(json.dumps(preflight, indent=2) + '\n')
    print(json.dumps(dict(stage='PREFLIGHT', **preflight), sort_keys=True), flush=True)
    selected = specs[:args.limit]
    h = V.read_inputs(args.reference)[0]['h']
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(probe, [(spec, h, args.power.numerator, args.power.denominator) for spec in selected]))
    V.read_inputs(args.reference)
    V.require(hashes == {file.name: sha256(file.read_bytes()).hexdigest() for file in files}, 'Block source closure unchanged')
    summary = dict(status='PASS EXACT CONNECTED FRAME BLOCK PROBE', cases=len(rows),
                   strictly_improving_ideal_candidates=sum(c['strictly_improving_ideal'] for r in rows for c in r['candidates']),
                   maximum_block_size=max((len(r['operation_indices']) for r in rows), default=0),
                   arbitrary_simultaneous_composition_not_asserted=True,
                   full_paid_or_native_or_exponent_claim=False, seconds=time.monotonic() - started)
    (args.output / 'certificate.json').write_text(json.dumps(dict(summary=summary, preflight=preflight, cases=rows), indent=2) + '\n')
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
