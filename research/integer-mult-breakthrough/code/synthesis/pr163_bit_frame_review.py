#!/usr/bin/env python3
"""Import-free PR163 bit chronology, geometry and paid-profile review.

The reference checkout is immutable input, not an imported executable dependency.
This checks rational frames and every formal F2 column. The odd-local-ring
weighted compiler and native routing contracts remain separate premises.
"""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import subprocess
import sys
import time


REFERENCE_HEAD = '15c702a929b7d640107a95e196186ad74e876c82'
INPUTS = {
    'research/paired-cube-bit/out/graph_p12.json': '3d52f8143a3dce21b19a7193b502951e22413e6321e6e632947c6d896dda317e',
    'research/paired-cube-bit/out/word_p12.json': '6aff0e89b3f98fa9c6e187ab5b2ff57e6cbcc360447283dfdb29d4012ad05813',
    'research/paired-cube-bit/out/frames_p12.json': '2559a436b17e65b03859ee19154a1e1c81e5c44344908884bcfb6bce8bd89821',
    'research/paired-cube-bit/out/kchron_p12.json': 'd77f7b3541be144bed7cd5577a0638330b1b57a8ec082e6a71f448130768169f',
    'research/paired-cube-bit/out/profile_p12.json': '239d60f0bbb10c478a243fb82961e908497dceee7f44c7584a187992a8302fa9',
    'research/paired-cube-balanced-161/bit/descent.json': 'eb9f0694b937ffa2f6747bbb22d5f76bf0c7da7a6678946aa9ceb5ba75cc389e',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def primitive(row):
    common = 0
    for value in row:
        common = gcd(common, abs(value))
    if common > 1:
        row = [value // common for value in row]
    first = next((value for value in row if value), 0)
    return tuple(-value for value in row) if first < 0 else tuple(row)


def echelon(rows, width):
    """Independent exact fraction-free Gauss-Jordan elimination."""
    matrix = [list(map(int, row)) for row in rows]
    require(all(len(row) == width for row in matrix), 'Integer row width')
    pivot_row, columns = 0, []
    for column in range(width):
        source = next((i for i in range(pivot_row, len(matrix)) if matrix[i][column]), None)
        if source is None:
            continue
        matrix[pivot_row], matrix[source] = matrix[source], matrix[pivot_row]
        matrix[pivot_row] = list(primitive(matrix[pivot_row]))
        pivot = matrix[pivot_row][column]
        for i in range(len(matrix)):
            if i != pivot_row and matrix[i][column]:
                factor = matrix[i][column]
                matrix[i] = list(primitive([pivot * a - factor * b
                                          for a, b in zip(matrix[i], matrix[pivot_row])]))
        columns.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return tuple(tuple(row) for row in matrix[:pivot_row]), tuple(columns)


def annihilator(rows, width):
    rows, columns = echelon(rows, width)
    result = []
    for free in range(width):
        if free in columns:
            continue
        denominator = 1
        for row, column in zip(rows, columns):
            denominator = lcm(denominator, abs(row[column]))
        value = [0] * width
        value[free] = denominator
        for row, column in zip(rows, columns):
            value[column] = -row[free] * denominator // row[column]
        result.append(primitive(value))
    return tuple(result)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def determinant(rows):
    """Bareiss determinant, with exact divisibility checked at every step."""
    n = len(rows)
    if not n:
        return 1
    require(all(len(row) == n for row in rows), 'Square determinant input')
    matrix = [list(row) for row in rows]
    previous, sign = 1, 1
    for k in range(n - 1):
        source = next((i for i in range(k, n) if matrix[i][k]), None)
        if source is None:
            return 0
        if source != k:
            matrix[k], matrix[source] = matrix[source], matrix[k]
            sign = -sign
        pivot = matrix[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = pivot * matrix[i][j] - matrix[i][k] * matrix[k][j]
                require(numerator % previous == 0, 'Bareiss exact division')
                matrix[i][j] = numerator // previous
            matrix[i][k] = 0
        previous = pivot
    return sign * matrix[-1][-1]


def read_inputs(reference):
    reference = Path(reference)
    values = {}
    for name, expected in INPUTS.items():
        data = (reference / name).read_bytes()
        require(sha256(data).hexdigest() == expected, 'Reference input SHA: ' + name)
        values[Path(name).name] = json.loads(data)
    return (values['graph_p12.json'], values['word_p12.json'], values['frames_p12.json'],
            values['kchron_p12.json'], values['profile_p12.json'], values['descent.json'])


class Frames:
    def __init__(self, records, h):
        self.h, self.B, self.A, self.dim, self.cache = h, {}, {}, {}, {}
        for key, record in records.items():
            f = int(key)
            given = record.get('a', record.get('b'))
            rows, unused = echelon(given, h)
            require(len(rows) == len(given), 'Independent frame rows')
            other = annihilator(rows, h)
            A, B = (rows, other) if 'a' in record else (other, rows)
            require(len(B) == record['dim'] and len(A) + len(B) == h, 'Frame dimensions')
            require(all(dot(a, b) == 0 for a in A for b in B), 'Frame annihilator binding')
            self.A[f], self.B[f], self.dim[f] = A, B, len(B)

    def add(self, rows):
        f = max(self.B) + 1
        B, unused = echelon(rows, self.h)
        require(len(B) == len(rows), 'Independent descent basis')
        self.B[f], self.A[f], self.dim[f] = B, annihilator(B, self.h), len(B)
        return f

    def sub(self, a, b):
        if a == b:
            return True
        key = (a, b)
        if key not in self.cache:
            self.cache[key] = self.dim[a] <= self.dim[b] and all(
                dot(x, y) == 0 for x in self.B[a] for y in self.A[b])
        return self.cache[key]

    def has(self, f, x):
        return all(dot(a, x) == 0 for a in self.A[f])

    def nondegenerate(self, f):
        B, A, h = self.B[f], self.A[f], self.h
        if len(B) <= len(A):
            sums = list(map(sum, B))
            G = [[9 * dot(a, b) - sums[i] * sums[j]
                  for j, b in enumerate(B)] for i, a in enumerate(B)]
        else:
            sums = list(map(sum, A))
            G = [[(9 - h) * dot(a, b) + sums[i] * sums[j]
                  for j, b in enumerate(A)] for i, a in enumerate(A)]
        return determinant(G)


def supports(graph):
    v, args = graph['v'], graph['args']
    result = [1 << i for i in range(v)]
    for node, pair in enumerate(args[v:], v):
        a, b = pair
        require(0 <= a < node and 0 <= b < node, 'Topological graph input')
        require(not result[a] & result[b], 'Disjoint scalar support')
        result.append(result[a] | result[b])
    return result


def bits(value):
    while value:
        low = value & -value
        yield low.bit_length() - 1
        value ^= low


def adjoints(graph, word, R):
    parity, conservative = [0] * R, [0] * R
    for root, role in zip(graph['roots'], word['rootroles']):
        for t in root['targets']:
            parity[role] ^= 1 << t
            conservative[role] |= 1 << t
    for receiver, donor, unused in reversed(word['ops']):
        parity[donor] ^= parity[receiver]
        conservative[donor] |= conservative[receiver]
    return parity, conservative


def scheduling(word, frames):
    gauge = {item['role']: item for item in word['gauges']}
    p1 = set(word['phase1'])
    rest = [i for i in range(len(word['ops'])) if i not in p1]
    positions = {i: j for j, i in enumerate(rest)}
    first = {}
    for i, (a, b, unused) in enumerate(word['ops']):
        first.setdefault(a, positions.get(i, -1))
        first.setdefault(b, positions.get(i, -1))
    times, next_target = {}, {}
    # Reconstruct the birth-response deadline from immutable future target caps.
    for item in word['gauges']:
        role, frame, targets = item['role'], item['frame'], item['targets']
        deadline = min([first[role]] + [next_target[t][1] for t in targets
                       if t in next_target and not frames.sub(next_target[t][0], frame)])
        require(deadline >= 0, 'Gauge role untouched in centre closure')
        times[role] = deadline
        for t in targets:
            if t not in next_target or not frames.sub(next_target[t][0], frame):
                next_target[t] = (frame, deadline)
    return p1, rest, gauge, times


def geometry(reference):
    started = time.monotonic()
    graph, word, records, partners, profile, descent = read_inputs(reference)
    h, v, R = graph['h'], graph['v'], profile['R']
    require((h, v, R) == (24, 1760, 23368), 'Selected bit input shape')
    frames = Frames(records['frames'], h)
    nf = {int(key): value for key, value in word['node_frame'].items()}
    op_frames = [nf[node] for a, b, node in word['ops']]
    changed, new_determinants = [], []
    for i, rows in descent['frames']:
        require(i not in changed, 'Distinct operation descent')
        new = frames.add(rows)
        require(frames.sub(new, op_frames[i]), 'New frame inside retained old frame')
        det = frames.nondegenerate(new)
        require(det != 0, 'Rational new-frame Gram determinant')
        new_determinants.append(det)
        op_frames[i] = new
        changed.append(i)
    require(len(changed) == 1296, 'Complete descent coverage')
    sup = supports(graph)
    chi = [tuple(int(j in label) for j in range(h)) for label in graph['labels']]
    cov = [tuple(3 * entry - 1 for entry in vector) for vector in chi]
    for i in changed:
        for s in bits(sup[word['ops'][i][2]]):
            require(frames.has(op_frames[i], chi[s]), 'Complete conservative source span in descent')
    full = word['full_frame']
    require(frames.dim[full] == h, 'Full endpoint dimension')
    for s, frame in enumerate(word['source_frame']):
        require(frames.dim[frame] == 1 and frames.has(frame, chi[s]), 'Source line binding')
    loss = 0
    for root, frame in zip(graph['roots'], word['root_frame']):
        require(frames.sub(nf[root['node']], frame), 'Original root-node containment')
        if root['kind'] == 'center':
            rows = [chi[s] for s, label in enumerate(graph['labels']) if root['coordinate'] in label]
            require(len(echelon(rows, h)[0]) == frames.dim[frame], 'Centre-star rank')
            require(all(frames.has(frame, row) for row in rows), 'Centre-star source span')
            loss += frames.dim[frame]
        else:
            require(all(dot(cov[t], row) == 0 for t in root['targets'] for row in frames.B[frame]),
                    'Side root inside every target cap')
            require(frames.dim[frame] == h - len(echelon([cov[t] for t in root['targets']], h)[0]),
                    'Side-root complete joint cap')
    require(loss == profile['loss'], 'Copied centre loss')
    parity, conservative = adjoints(graph, word, R)
    p1, rest, gauge, times = scheduling(word, frames)
    # Verify the actual phase cut, rather than accepting a supplied phase list.
    previous, predecessors = {}, []
    for i, (a, b, unused) in enumerate(word['ops']):
        predecessors.append((previous.get(a, -1), previous.get(b, -1)))
        previous[a] = previous[b] = i
    stack = [previous[role] for root, role in zip(graph['roots'], word['rootroles'])
             if root['kind'] == 'center' and role in previous]
    closure = set()
    while stack:
        i = stack.pop()
        if i not in closure:
            closure.add(i)
            stack.extend(j for j in predecessors[i] if j >= 0)
    require(p1 == closure, 'Exact centre predecessor closure')
    source_roles = {int(s): r for s, r in word['sources'].items()}
    start_frames = {r: word['source_frame'][s] for s, r in source_roles.items()}
    for role, item in gauge.items():
        require(role not in start_frames, 'Gauge is not an injected source role')
        require(sum(1 << t for t in item['targets']) == conservative[role], 'Complete dirty response support')
        require(frames.dim[item['frame']] == item['dim'], 'Gauge frame dimension')
        start_frames[role] = item['frame']

    def role_profile(chosen):
        sequences = defaultdict(list)
        # Literal chronology: centre roots are read between the two op phases.
        for i in sorted(p1):
            a, b, unused = word['ops'][i]
            sequences[a].append(chosen[i]); sequences[b].append(chosen[i])
        for root, role, frame in zip(graph['roots'], word['rootroles'], word['root_frame']):
            if root['kind'] == 'center':
                sequences[role].append(frame)
        for i in rest:
            a, b, unused = word['ops'][i]
            sequences[a].append(chosen[i]); sequences[b].append(chosen[i])
        for root, role, frame in zip(graph['roots'], word['rootroles'], word['root_frame']):
            if root['kind'] != 'center':
                sequences[role].append(frame)
        H = Counter()
        for role in range(R):
            prev = start_frames.get(role)
            previous_dimension = 0 if prev is None else frames.dim[prev]
            if role in source_roles.values():
                H[1] += 1
            for frame in sequences[role] + [full]:
                require(prev is None or frames.sub(prev, frame), 'Both surrounding literal role chains')
                current_dimension = frames.dim[frame]
                require(current_dimension >= previous_dimension, 'Ascending rational frame dimension')
                if current_dimension > previous_dimension:
                    H[current_dimension - previous_dimension] += 1
                prev, previous_dimension = frame, current_dimension
        for root, frame in zip(graph['roots'], word['root_frame']):
            if root['kind'] == 'center':
                H[frames.dim[frame]] += 1
        return H

    oldH = role_profile([nf[node] for a, b, node in word['ops']])
    H = role_profile(op_frames)
    require(sum(r * n for r, n in H.items()) == sum(r * n for r, n in oldH.items()),
            'Descent preserves every-role first moment')
    entries, membership, src, deliveries = partners['entries'], Counter(), Counter(), defaultdict(list)
    for e in entries:
        a, b, mix, delivery = e['carrier'], e['passive'], e['mix_frame'], e['deliver_frame']
        membership[a] += 1; membership[b] += 1
        require(len(set(graph['labels'][a]) & set(graph['labels'][b])) == 1, 'Orthogonal partner pair')
        require(frames.dim[mix] == 2 and frames.has(mix, chi[a]) and frames.has(mix, chi[b]), 'Pair mixing span')
        require(frames.sub(mix, delivery), 'Pair mix before shared delivery cap')
        require(all(dot(cov[t], row) == 0 for t in e['receivers'] for row in frames.B[delivery]), 'Pair target caps')
        require(e['carrier_chain'] == [word['source_frame'][a], mix, delivery, full]
                and e['passive_chain'] == [word['source_frame'][b], mix, full]
                and e['undo_frame'] == full, 'Source-pair chronology and final undo frame')
        for chain in (e['carrier_chain'], e['passive_chain']):
            for first, second in zip(chain, chain[1:]):
                require(frames.sub(first, second), 'Source-pair nested chain')
                width = frames.dim[second] - frames.dim[first]
                if width:
                    src[width] += 1
        root = graph['roots'][e['deliver_after_root']]
        require(root['kind'] != 'center' and sorted(root['targets']) == sorted(e['receivers']), 'Actual delivery root')
        deliveries[e['deliver_after_root']].append(e)
    require(all(membership[s] == 1 for s in range(v)), 'Every source has exactly one partner')
    target_frames = defaultdict(list)
    for role in sorted(gauge, key=lambda r: (times[r], -list(gauge).index(r))):
        for target in gauge[role]['targets']:
            target_frames[target].append(gauge[role]['frame'])
    for j, (root, frame) in enumerate(zip(graph['roots'], word['root_frame'])):
        if root['kind'] != 'center':
            for target in root['targets']:
                target_frames[target].append(frame)
            for e in deliveries[j]:
                for target in e['receivers']:
                    target_frames[target].append(e['deliver_frame'])
    Y = Counter()
    for target in range(v):
        prev, dimension = None, 0
        for frame in target_frames[target]:
            require(prev is None or frames.sub(prev, frame), 'Chronological target frame chain')
            require(all(dot(cov[target], row) == 0 for row in frames.B[frame]), 'Target frame in sink cap')
            width = frames.dim[frame] - dimension
            if width:
                Y[width] += 1
            prev, dimension = frame, frames.dim[frame]
        require(dimension <= h - 1, 'Final sink cap')
        if dimension < h - 1:
            Y[h - 1 - dimension] += 1
    used = set(op_frames) | set(nf.values()) | set(word['root_frame']) | set(word['source_frame'])
    used |= {item['frame'] for item in gauge.values()} | {e['mix_frame'] for e in entries} | {e['deliver_frame'] for e in entries}
    for frame in used:
        require(frames.nondegenerate(frame) != 0, 'Used rational frame nondegenerate')

    def histogram(role_bins):
        result = Counter()
        for part in (role_bins, Y, src):
            for width, count in part.items():
                result[width] += 3 * count
        for item in gauge.values():
            result[3 * item['dim']] += 1
        result[2] += 2 * v
        return {r: n for r, n in sorted(result.items()) if n}

    baseline, selected = histogram(oldH), histogram(H)
    require(baseline == {int(r): n for r, n in profile['child_histogram'].items()}, 'Independent baseline histogram')
    rank = sum(r * n for r, n in selected.items())
    require(rank == 1934000 and profile['W_per_vertex'] * profile['m'] - rank == 1936, 'Complete selected rank and deficit')
    return dict(status='PASS INDEPENDENT RATIONAL BIT GEOMETRY', h=h, v=v, R=R,
                W=2 * v + R, m=3 * h, modified_operation_frames=len(changed),
                workspace_reuse_pairs=0, child_histogram=selected, rank=rank, deficit=1936,
                copied_centre_loss=loss, new_Gram_determinant_max_bits=max(abs(x).bit_length() for x in new_determinants),
                all_used_rational_frames=len(used), conservative_support_and_both_literal_chains=True,
                local_ring_or_native_claim=False, seconds=time.monotonic() - started)


def formal(reference):
    started = time.monotonic()
    graph, word, records, partners, profile, descent = read_inputs(reference)
    v, R = graph['v'], profile['R']
    # The scheduling needs only the original gauge frames; eliminate exactly.
    needed = {item['frame'] for item in word['gauges']}
    frames = Frames({key: value for key, value in records['frames'].items() if int(key) in needed}, graph['h'])
    p1, rest, gauge, times = scheduling(word, frames)
    adjoint, unused = adjoints(graph, word, R)
    at = defaultdict(list)
    # Preserve reverse-selection tie order, rather than recomputing at a stale value.
    for item in reversed(word['gauges']):
        at[times[item['role']]].append(item['role'])
    deliveries = defaultdict(list)
    for e in partners['entries']:
        deliveries[e['deliver_after_root']].append(e)

    def replay(tamper=None):
        x = [1 << s for s in range(v)]
        y = [1 << (v + t) for t in range(v)]
        registers = [1 << (2 * v + r) for r in range(R)]
        omitted = False

        def debit(role):
            nonlocal omitted
            if tamper == 'omit_live_compensation' and adjoint[role] and not omitted:
                omitted = True
                return
            value = registers[role]
            for t in bits(adjoint[role]):
                y[t] ^= value

        for role in range(R):
            if role not in gauge:
                debit(role)
        for source, role in word['sources'].items():
            registers[role] ^= x[int(source)]
        executed = []
        for i in sorted(p1):
            receiver, donor, unused = word['ops'][i]
            registers[receiver] ^= registers[donor]
            executed.append(i)
        for root, role in zip(graph['roots'], word['rootroles']):
            if root['kind'] == 'center':
                for t in root['targets']:
                    y[t] ^= registers[role]
        for j, i in enumerate(rest):
            for role in at[j]:
                debit(role)
            receiver, donor, unused = word['ops'][i]
            registers[receiver] ^= registers[donor]
            executed.append(i)
        for role in at[len(rest)]:
            debit(role)
        partner_omitted = False
        for j, (root, role) in enumerate(zip(graph['roots'], word['rootroles'])):
            if root['kind'] != 'center':
                for t in root['targets']:
                    y[t] ^= registers[role]
            for e in deliveries[j]:
                x[e['carrier']] ^= x[e['passive']]
                for t in e['receivers']:
                    if tamper == 'omit_partner_output' and not partner_omitted:
                        partner_omitted = True
                        continue
                    y[t] ^= x[e['carrier']]
        # Deliberately wrong source cleanup is a separate negative control.
        if tamper == 'uninject_before_source_undo':
            for source, role in word['sources'].items():
                registers[role] ^= x[int(source)]
        for e in partners['entries']:
            x[e['carrier']] ^= x[e['passive']]
        for i in reversed(executed):
            receiver, donor, unused = word['ops'][i]
            registers[receiver] ^= registers[donor]
        if tamper != 'uninject_before_source_undo':
            for source, role in word['sources'].items():
                registers[role] ^= x[int(source)]
        require(all(value == 1 << (2 * v + r) for r, value in enumerate(registers)), 'Every dirty-column endpoint')
        require(all(value == 1 << s for s, value in enumerate(x)), 'Every source-column endpoint')
        require(all(value == (1 << (v + t)) ^ (1 << t) for t, value in enumerate(y)), 'Every sink-column endpoint')
        return dict(formal_variables=2 * v + R, all_F2_columns=True)

    positive = replay()
    controls = []
    for tamper in ('omit_live_compensation', 'omit_partner_output', 'uninject_before_source_undo'):
        try:
            replay(tamper)
        except ValueError:
            controls.append(tamper)
        else:
            raise ValueError('Adverse chronology accepted: ' + tamper)
    return dict(status='PASS INDEPENDENT COMPLETE F2 CHRONOLOGY', **positive,
                negative_controls=controls, integer_identity_not_asserted=True,
                foreign_source_imports=0, seconds=time.monotonic() - started)


def run_task(task):
    component, reference = task
    return geometry(reference) if component == 'geometry' else formal(reference)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--component', choices=('geometry', 'formal', 'all'), default='all')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Exact controls require normal Python execution')
    require(args.workers >= 1, 'Positive workers')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.reference, text=True).strip()
    require(head == REFERENCE_HEAD, 'Pinned immutable reference commit')
    source = Path(__file__).resolve()
    source_hash = sha256(source.read_bytes()).hexdigest()
    read_inputs(args.reference)
    args.output.mkdir(parents=True, exist_ok=False)
    components = ['geometry', 'formal'] if args.component == 'all' else [args.component]
    protocol = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=source_hash,
                    reference_head=head, inputs=INPUTS, component=args.component,
                    requested_workers=args.workers, actual_workers=min(args.workers, len(components)),
                    stdlib_only=True, foreign_source_imports=0,
                    scope='Rational nested-frame and complete F2 word audit, not a native or asymptotic proof')
    (args.output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    with ProcessPoolExecutor(max_workers=protocol['actual_workers']) as pool:
        rows = list(pool.map(run_task, [(c, str(args.reference.resolve())) for c in components]))
    read_inputs(args.reference)
    require(sha256(source.read_bytes()).hexdigest() == source_hash, 'Review source unchanged')
    receipt = dict(status='PASS INDEPENDENT PR163 BIT REVIEW', components=rows,
                   source_sha256=source_hash, reference_head=head, inputs_unchanged=True)
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
