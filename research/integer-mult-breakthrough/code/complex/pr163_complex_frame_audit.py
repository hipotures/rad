#!/usr/bin/env python3
"""Import-free scalar/frame recount of the pinned PR163 complex candidate.

The full audit reads immutable external JSON as data. It checks conservative
source spans, signed singleton broadcasts, actual chronological nesting and
the complete child histogram. It does not import foreign producers or prove
their all-size phase/routing/transfer contracts.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import gzip
import json
from pathlib import Path
import time


PACKAGE = Path('research/paired-cube-balanced-161')
COMMIT = '15c702a929b7d640107a95e196186ad74e876c82'
FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures/complex/pr163-complex-frame-cases.json'


def rref(rows):
    pivots = {}
    for value in rows:
        for pivot in sorted(pivots, reverse=True):
            if value & (1 << pivot):
                value ^= pivots[pivot]
        if not value:
            continue
        pivot = value.bit_length() - 1
        for old in list(pivots):
            if pivots[old] & (1 << pivot):
                pivots[old] ^= value
        pivots[pivot] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def inside(rows, containing):
    reduced = rref(containing)
    for value in rows:
        for row in reduced:
            if value & (1 << (row.bit_length() - 1)):
                value ^= row
        if value:
            return False
    return True


def orthogonal(rows, h):
    rows = rref(rows)
    pivots = {row.bit_length() - 1: row for row in rows}
    result = []
    for coordinate in range(h):
        if coordinate in pivots:
            continue
        value = 1 << coordinate
        for pivot, row in pivots.items():
            if row & (1 << coordinate):
                value |= 1 << pivot
        result.append(value)
    result = rref(result)
    if len(result) + len(rows) != h or any((a & b).bit_count() % 2 for a in rows for b in result):
        raise AssertionError('independent orthogonal-complement construction failed')
    return result


def chain_case(case):
    sequence = [rref(rows) for rows in case['sequence']]
    if any(not inside(a, b) for a, b in zip(sequence, sequence[1:])):
        raise AssertionError('a physical role chain is not nested in its actual chronology')
    histogram = Counter(len(b) - len(a) for a, b in zip(sequence, sequence[1:]) if len(b) > len(a))
    if case['source_entrance']:
        histogram[1] += 1
    histogram.update(case['copied_center_widths'])
    return histogram


def block_case(cases):
    total = Counter()
    for case in cases:
        total.update(chain_case(case))
    return dict(total)


def scalar_audit(g):
    h, v, inputs = g['h'], g['v'], g['inputs']
    positive, negative, spans = [], [], []
    for index, operands in enumerate(g['args']):
        if operands is None:
            if index >= v:
                raise AssertionError('a noninput node has no defined operands')
            positive.append(1 << index)
            negative.append(0)
            spans.append((inputs[index],))
        else:
            a, b = operands
            if not 0 <= a < index or not 0 <= b < index:
                raise AssertionError('the source graph is not topological')
            if (positive[a] | negative[a]) & (positive[b] | negative[b]):
                raise AssertionError('fusion did not retain disjoint conservative source supports')
            sign = g['signs'][index]
            if sign not in (-1, 1):
                raise AssertionError('an undeclared signed producer coefficient occurred')
            positive.append(positive[a] | (positive[b] if sign == 1 else negative[b]))
            negative.append(negative[a] | (negative[b] if sign == 1 else positive[b]))
            spans.append(rref(spans[a] + spans[b]))
    # Balanced integer digits encode every source coefficient injectively.
    # At most one +/-1 side contribution comes from each root to a row.
    bound = len(g['roots']) + 4
    digit_bits = (2 * bound + 1).bit_length()
    base = 1 << digit_bits
    if base <= 2 * bound:
        raise AssertionError('balanced source digits are not injective')
    units = [1 << (digit_bits * source) for source in range(v)]
    pack_cache = {0: 0}

    def pack(support):
        if support not in pack_cache:
            result, rest = 0, support
            while rest:
                bit = rest & -rest
                result += units[bit.bit_length() - 1]
                rest ^= bit
            pack_cache[support] = result
        return pack_cache[support]

    rows = [0] * v
    singleton_roots = 0
    centers = []
    roots = []
    for root in g['roots']:
        node = root['node']
        support = pack(positive[node]) - pack(negative[node])
        if root['kind'] == 'center':
            coordinate = root['coordinate']
            expected = sum(1 << source for source, label in enumerate(inputs) if label & (1 << coordinate))
            if positive[node] != expected or negative[node]:
                raise AssertionError('a copied center is not the declared complete singleton star')
            if len(spans[node]) != h - 2:
                raise AssertionError('the paired singleton-star span has the wrong paid dimension')
            expected_coefficients = ['1/3' if label & (1 << coordinate) else '-1/6' for label in inputs]
            if root['coefficients'] != expected_coefficients:
                raise AssertionError('a center scatter changed its rational scalar map')
            U = spans[node]
            centers.append(dict(coordinate=coordinate, dimension=len(U),
                                radical_dimension=len(U) - gf2_gram_rank(U), basis=list(U)))
            A = orthogonal(U, h)
        else:
            if len(root['targets']) == 1:
                singleton_roots += 1
            for target, coefficient in zip(root['targets'], root['coefficients']):
                if coefficient not in ('1/2', '-1/2'):
                    raise AssertionError('a side broadcast has an uncharged scalar coefficient')
                rows[target] += support if coefficient == '1/2' else -support
            A = rref(inputs[target] for target in root['targets'])
            U = orthogonal(A, h)
        if not inside(spans[node], U):
            raise AssertionError('a scalar source support leaves its actual root frame')
        roots.append((root, U, A))
    all_sources = sum(units)
    point_packs = [sum(units[source] for source, label in enumerate(inputs) if label & (1 << coordinate))
                   for coordinate in range(h)]
    for target, label in enumerate(inputs):
        expected = all_sources - sum(point_packs[c] for c in range(h) if label & (1 << c))
        cube_start = (target // 8) * 8
        expected += sum(((label & inputs[source]).bit_count() - 1) * units[source]
                        for source in range(cube_start, cube_start + 8))
        if rows[target] != expected:
            raise AssertionError('signed fused broadcasts do not realize the full declared H matrix')
    # Exact K involution, requiring its paid original-source parity frames.
    for start in range(0, v, 8):
        labels = inputs[start:start + 8]
        K2 = [[1 if (a ^ b).bit_count() == 6 else -1 if (a ^ b).bit_count() == 2 else 0
               for b in labels] for a in labels]
        for i in range(8):
            for j in range(8):
                if sum(K2[i][k] * K2[k][j] for k in range(8)) != 4 * (i == j):
                    raise AssertionError('the original-source cube correction is not its exact inverse')
        for parity in (0, 1):
            source = [i for i in range(8) if i.bit_count() % 2 == parity]
            target = [i for i in range(8) if i.bit_count() % 2 != parity]
            U = rref(labels[i] for i in source)
            if len(U) != 3 or any(not inside(U, orthogonal((labels[t],), h)) for t in target):
                raise AssertionError('the rank-three cube correction does not fit its target caps')
    return spans, roots, dict(source_pairs=v * v, packed_digit_bits=digit_bits,
                              absolute_coefficient_bound=bound, signed_broadcasts_exact=True,
                              singleton_target_roots=singleton_roots, complete_coordinate_centers=centers,
                              K_involution_and_parity_frames=True,
                              scope='Exact signed H/B/K source-column identities, no aliased dirty-operator claim')


def gf2_gram_rank(rows):
    return len(rref(sum(((a & b).bit_count() % 2) << j for j, b in enumerate(rows)) for a in rows))


def full_audit(reference, workers):
    candidate = reference / PACKAGE / 'selected/complex'
    names = ('graph', 'frames', 'word', 'profile-before', 'physical-frames', 'physical-pairs', 'profile')
    inputs, data = {}, {}
    for name in names:
        path = candidate / (name + '.json.gz')
        raw = path.read_bytes()
        inputs[str(path.relative_to(reference))] = sha256(raw).hexdigest()
        data[name] = json.loads(gzip.decompress(raw))
    g, witness, word, before, expected = [data[name] for name in ('graph', 'frames', 'word', 'profile-before', 'profile')]
    h, v, R = g['h'], g['v'], before['R']
    spans, roots, scalar = scalar_audit(g)
    operations = word['ops']
    phase = sorted(word['phase1'])
    phase_set = set(phase)
    if len(phase) != len(phase_set):
        raise AssertionError('center chronology repeats an operation')
    chronology = phase + [i for i in range(len(operations)) if i not in phase_set]
    position = {operation: index for index, operation in enumerate(chronology)}
    frames = [orthogonal(witness['annihilators'][node], h) for a, b, node in operations]
    changed = set()
    for index, replacement in data['physical-frames']:
        frame = rref(replacement)
        if index in changed or frame != tuple(replacement) or frame == frames[index]:
            raise AssertionError('frame replacement is repeated, noncanonical or unchanged')
        frames[index] = frame
        changed.add(index)
    for (a, b, node), frame in zip(operations, frames):
        if a == b or not inside(spans[node - 1], frame):
            raise AssertionError('an operation leaves the complete conservative source span')
    source = {int(node): role for node, role in word['sources'].items()}
    gauge = {item['role']: orthogonal(item['annihilator'], h) for item in word['selected']}
    starts = [()] * R
    for node, role in source.items():
        starts[role] = (g['inputs'][node - 1],)
    for role, frame in gauge.items():
        starts[role] = frame
    role_operations = [[] for _ in range(R)]
    for index in chronology:
        a, b, unused = operations[index]
        role_operations[a].append(index)
        role_operations[b].append(index)
    root_role = {}
    for (root, U, A), role in zip(roots, word['rootroles']):
        if role in root_role:
            raise AssertionError('a physical root role is duplicated')
        root_role[role] = root, U, A
    donors, merge, deadlines = {}, {}, {}
    for donor, recipient, deadline in data['physical-pairs']:
        if donor in donors or recipient in merge:
            raise AssertionError('a physical handoff repeats its donor or recipient')
        donors[donor], merge[recipient], deadlines[recipient] = recipient, donor, deadline
    if set(donors) & set(merge):
        raise AssertionError('the declared disjoint physical handoffs overlap')
    pair_records = []
    for donor, recipient in donors.items():
        if donor in gauge or donor in root_role or recipient not in gauge:
            raise AssertionError('a handoff has the wrong donor/recipient boundary')
        last = role_operations[donor][-1]
        first = role_operations[recipient][0]
        deadline = deadlines[recipient]
        if deadline is None:
            if last not in phase_set or first in phase_set:
                raise AssertionError('an early handoff crosses the center phase incorrectly')
        elif deadline != first or deadline in phase_set or position[last] >= position[deadline]:
            raise AssertionError('late compensation occurs before the donor dies or after recipient use')
        if not inside(frames[last], gauge[recipient]):
            raise AssertionError('paid donor frame does not enter the recipient birth gauge')
        pair_records.append(dict(donor=donor, recipient=recipient, deadline=deadline,
                                 donor_last_position=position[last], recipient_first_position=position[first],
                                 donor_frame=list(frames[last]), recipient_gauge=list(gauge[recipient])))
    full = rref(1 << c for c in range(h))

    def sequence(role):
        return [starts[role]] + [frames[index] for index in role_operations[role]] + ([root_role[role][1]] if role in root_role else []) + [full]

    cases = []
    for role in range(R):
        seq = sequence(role)
        # Check every virtual chain before the physical splice too.
        if any(not inside(a, b) for a, b in zip(seq, seq[1:])):
            raise AssertionError('a virtual role chain is not nested in actual chronological order')
        if role in merge:
            continue
        center_widths = []
        for member in (role, donors.get(role)):
            if member is not None and member in root_role and root_role[member][0]['kind'] == 'center':
                center_widths.append(len(root_role[member][1]))
        if role in donors:
            seq = seq[:-1] + sequence(donors[role])
        cases.append(dict(role=role, source_entrance=role in source.values(),
                          copied_center_widths=center_widths, sequence=[list(U) for U in seq]))
    blocks = [cases[i::workers] for i in range(workers)]
    if workers == 1:
        pieces = [block_case(blocks[0])]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            pieces = list(pool.map(block_case, blocks))
    local = Counter()
    for piece in pieces:
        local.update(piece)
    current = [full] * v
    targets = Counter()
    read_order = sorted(reversed(word['selected']), key=lambda item:
                        (len(phase) if deadlines.get(item['role']) is None else position[deadlines[item['role']]],
                         -word['selected'].index(item)))
    for item in read_order:
        A = rref(item['annihilator'])
        for target in item['targets']:
            if not inside(A, current[target]):
                raise AssertionError('a deferred dirty compensation read violates the target chain')
            targets[len(current[target]) - len(A)] += 1
            current[target] = A
    for (root, U, A), role in zip(roots, word['rootroles']):
        if root['kind'] != 'side':
            continue
        for target in root['targets']:
            if not inside(A, current[target]):
                raise AssertionError('a fused scalar root violates the actual target read order')
            targets[len(current[target]) - len(A)] += 1
            current[target] = A
    for target, label in enumerate(g['inputs']):
        if not inside((label,), current[target]):
            raise AssertionError('the cube correction leaves the final target input frame')
        targets[len(current[target]) - 1] += 1
    source_histogram = Counter({2: v, h - 4: v, 1: v})
    tails = Counter(len(frame) for role, frame in gauge.items() if role not in merge)
    children = Counter()
    for component in (local, source_histogram, targets):
        children.update({width: 3 * count for width, count in component.items() if width})
    children.update({3 * width: count for width, count in tails.items() if width})
    children[2] += 2 * v
    W, m = 2 * v + R - len(donors), 3 * h
    rank = sum(width * count for width, count in children.items())
    reconstructed = dict(local_histogram=dict(local), source_data_histogram=dict(source_histogram),
                         target_data_histogram=dict(targets), physical_gauge_histogram=dict(tails),
                         child_histogram=dict(children))
    for name, value in reconstructed.items():
        if value != {int(k): count for k, count in expected[name].items()}:
            raise AssertionError('independent complete histogram mismatch: ' + name)
    if rank != expected['rank_per_vertex'] or W != expected['W_per_vertex'] or m * W - rank != 2 * v - 3 * before['loss']:
        raise AssertionError('paid persistent stock or telescoping rank deficit mismatch')
    if before['rank_per_vertex'] - rank != len(donors) * m or before['W_per_vertex'] - W != len(donors):
        raise AssertionError('gauge removal does not pay exactly the removed ambient role stock')
    chosen = []
    wanted_roles = [pair['donor'] for pair in pair_records[:2]]
    wanted_roles += [case['role'] for case in cases if case['copied_center_widths']][:1]
    wanted_roles += [case['role'] for case in cases if case['source_entrance']][:1]
    for role in wanted_roles:
        chosen.append(next(case for case in cases if case['role'] == role))
    fixture = dict(h=h, source_commit=COMMIT, chain_cases=chosen, pairs=pair_records[:2],
                   expected_local_histograms=[dict(chain_case(case)) for case in chosen],
                   scope='Small physical-chain/birth cases from the full frozen h22 candidate; not its whole paid profile')
    return dict(input_sha256=inputs, scalar=scalar, h=h, v=v, ambient=m,
                physical_roles=len(cases), virtual_scalar_roles=R, handoffs=len(donors),
                late_handoffs=sum(value is not None for value in deadlines.values()),
                changed_operation_frames=len(changed), complete_operations=len(operations),
                actual_chronology=True, persistent_W=W, complete_rank=rank, deficit=m * W - rank,
                removed_rank=before['rank_per_vertex'] - rank, maximum_child=max(children),
                complete_histograms=reconstructed,
                scope='Import-free finite scalar/geometry/chronology/paid-profile audit. No full dirty Gaussian phase operator or inherited all-size theorem.'), fixture


def bounded_audit():
    fixture = json.loads(FIXTURE.read_text())
    for case, expected in zip(fixture['chain_cases'], fixture['expected_local_histograms']):
        if dict(chain_case(case)) != {int(k): v for k, v in expected.items()}:
            raise AssertionError('bounded physical chain recount differs')
    for pair in fixture['pairs']:
        if pair['donor_last_position'] >= pair['recipient_first_position'] or not inside(pair['donor_frame'], pair['recipient_gauge']):
            raise AssertionError('bounded paid birth handoff is invalid')
    bad = dict(fixture['chain_cases'][0])
    bad['sequence'] = [list(rows) for rows in bad['sequence']]
    nonzero = next(i for i, rows in enumerate(bad['sequence']) if rows)
    if nonzero + 1 >= len(bad['sequence']):
        raise AssertionError('the retained negative has no later physical frame')
    bad['sequence'][nonzero + 1] = []
    try:
        chain_case(bad)
    except AssertionError:
        rejected = True
    else:
        raise AssertionError('cropped-frame negative did not reject')
    return dict(fixture_sha256=sha256(FIXTURE.read_bytes()).hexdigest(),
                chain_cases=len(fixture['chain_cases']), paid_handoffs=len(fixture['pairs']),
                cropped_frame_rejected=rejected,
                scope='Bounded actual physical-chain/birth cases only; full external profile requires the pinned input checkout.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-root', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--fixture-output', type=Path)
    args = parser.parse_args()
    if args.workers < 1 or not args.bounded and args.reference_root is None:
        parser.error('positive workers and either --bounded or --reference-root are required')
    source = Path(__file__)
    digest = sha256(source.read_bytes()).hexdigest()
    started_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    if args.bounded:
        evidence, fixture = bounded_audit(), None
    else:
        evidence, fixture = full_audit(args.reference_root, args.workers)
    if sha256(source.read_bytes()).hexdigest() != digest:
        raise AssertionError('independent audit source changed during execution')
    result = dict(status='PASS SCOPED PR163 COMPLEX FRAME AUDIT', source_sha256=digest,
                  started_utc=started_utc, completed_utc=datetime.now(timezone.utc).isoformat(),
                  bounded=args.bounded, workers=args.workers, evidence=evidence,
                  seconds=time.monotonic() - started,
                  scope='Exact finite scalar/frame/paid-profile audit, not a new multiplier theorem.')
    for path, value in ((args.output, result), (args.fixture_output, fixture)):
        if path is not None:
            if value is None:
                raise ValueError('no fixture is authored by a bounded input verifier')
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x') as stream:
                stream.write(json.dumps(value, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], bounded=args.bounded,
                          summary={k: evidence[k] for k in ('physical_roles', 'handoffs', 'complete_rank', 'deficit') if k in evidence},
                          seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
