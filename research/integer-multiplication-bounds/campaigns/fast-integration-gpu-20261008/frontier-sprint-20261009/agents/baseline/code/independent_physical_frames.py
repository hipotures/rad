#!/usr/bin/env python3
"""Independent exact forward geometry and paid-ledger audit of a physical word.

No candidate Python is imported. Integer signed supports, GF(2) elimination,
full backward intersections, actual compensation chronology, local K source
itinerary and every histogram term are reconstructed from the JSON inputs.
General-subspace Clifford transport and complemented reflection are separate
obligations. The upstream construction is due to icekylinx, eumemic, jamesyc
and its inherited contributors (Apache-2.0); this audit is authored by RaD
with OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import time


def need(condition, message):
    if not condition:
        raise ValueError(message)


def index(value, limit, message):
    need(type(value) is int and 0 <= value < limit, message)
    return value


def echelon(vectors):
    """Reduced rows from independent pivot elimination, highest pivot first."""
    rows = {}
    for value in vectors:
        need(type(value) is int and value >= 0, 'invalid binary vector')
        while value:
            pivot = value.bit_length() - 1
            if pivot not in rows:
                rows[pivot] = value
                break
            value ^= rows[pivot]
    for pivot in sorted(rows):
        for upper in sorted(rows):
            if upper > pivot and (rows[upper] >> pivot) & 1:
                rows[upper] ^= rows[pivot]
    return tuple(rows[pivot] for pivot in sorted(rows, reverse=True))


def frame(vectors, h, message):
    need(isinstance(vectors, (tuple, list)), message + ': frame type')
    need(all(type(x) is int and 0 < x < (1 << h) for x in vectors),
         message + ': coordinate domain')
    result = echelon(vectors)
    need(result == tuple(vectors), message + ': noncanonical frame')
    return result


@lru_cache(maxsize=150000)
def inside(left, right):
    for value in left:
        for row in right:
            if value & (1 << (row.bit_length() - 1)):
                value ^= row
        if value:
            return False
    return True


@lru_cache(maxsize=50000)
def orthogonal(rows, h):
    pivots = {row.bit_length() - 1: row for row in rows}
    vectors = []
    for free in range(h):
        if free not in pivots:
            vector = 1 << free
            for pivot, row in pivots.items():
                if row & (1 << free):
                    vector |= 1 << pivot
            vectors.append(vector)
    result = echelon(vectors)
    need(len(rows) + len(result) == h, 'orthogonal dimension')
    need(all(not ((x & y).bit_count() & 1) for x in rows for y in result),
         'orthogonal pairing')
    return result


def normalized_histogram(value):
    return {int(k): count for k, count in value.items() if int(k) and count}


def verify(g, witness, word, record, edits, pairs):
    h, v, roles = g['h'], g['v'], record['R']
    need(type(h) is int and h > 0 and type(v) is int and v > 0, 'dimensions')
    inputs = g['inputs']
    need(len(inputs) == v and len(set(inputs)) == v and
         all(type(q) is int and 0 < q < (1 << h) and q.bit_count() == 3 for q in inputs),
         'source addresses')
    need(g['labels'] == [[i for i in range(h) if q >> i & 1] for q in inputs],
         'source labels')
    args = [None] + [None if item is None else tuple(x + 1 for x in item) for item in g['args']]
    n = len(args)
    need(len(g['signs']) == n - 1 and len(witness['annihilators']) == n, 'node arrays')
    spans, positive, negative = [()] * n, [0] * n, [0] * n
    for node in range(1, n):
        if node <= v:
            need(args[node] is None, 'input node is not a leaf')
            spans[node], positive[node] = (inputs[node - 1],), 1 << (node - 1)
        else:
            need(isinstance(args[node], tuple) and len(args[node]) == 2, 'noninput leaf')
            a, b = args[node]
            need(type(a) is int and type(b) is int and 0 < a < node and 0 < b < node,
                 'DAG chronology')
            sign = g['signs'][node - 1]
            need(type(sign) is int and sign in (-1, 1), 'DAG sign')
            need(not (positive[a] | negative[a]) & (positive[b] | negative[b]),
                 'overlapping conservative signed operands')
            positive[node] = positive[a] | (positive[b] if sign == 1 else negative[b])
            negative[node] = negative[a] | (negative[b] if sign == 1 else positive[b])
            spans[node] = echelon(spans[a] + spans[b])
    full = tuple(1 << i for i in reversed(range(h)))
    roots = g['roots']
    need(len(roots) == len(word['rootroles']), 'root count')
    rootframe, rootann, rootkind, rootnodes = {}, {}, {}, {}
    for root, role in zip(roots, word['rootroles']):
        index(role, roles, 'root role')
        need(role not in rootframe, 'duplicate root role')
        node = index(root['node'], n - 1, 'root node') + 1
        targets = root['targets']
        need(all(type(t) is int and 0 <= t < v for t in targets) and
             len(set(targets)) == len(targets), 'root targets')
        need(len(targets) == len(root['coefficients']), 'root coefficient count')
        if root['kind'] == 'center':
            coordinate = index(root['coordinate'], h, 'center coordinate')
            need(not negative[node] and positive[node] == sum(1 << t for t, q in enumerate(inputs)
                                                            if q >> coordinate & 1),
                 'center signed support')
            need(targets == list(range(v)) and root['coefficients'] ==
                 ['1/3' if q >> coordinate & 1 else '-1/6' for q in inputs], 'center exact scatter')
            cap = spans[node]
            need(len(cap) == h - 2, 'center dimension')
            ann = orthogonal(cap, h)
        else:
            need(root['kind'] == 'side' and all(c in ('1/2', '-1/2') for c in root['coefficients']),
                 'side signed coefficients')
            ann = echelon(inputs[t] for t in targets)
            cap = orthogonal(ann, h)
        need(inside(spans[node], cap), 'root support containment')
        rootframe[role], rootann[role], rootkind[role], rootnodes[role] = cap, ann, root['kind'], node
    # Regenerate every full backward intersection, including frozen carrier arcs.
    order = witness['order']
    need(len(order) == len(set(order)) and all(type(x) is int and 0 < x < n for x in order),
         'active order')
    active, position = set(order), {x: i for i, x in enumerate(order)}
    need(set(range(1, v + 1)) <= active and set(rootnodes.values()) <= active, 'active endpoints')
    successors, caps = defaultdict(list), defaultdict(list)
    for node in order:
        if args[node] is not None:
            for operand in args[node]:
                need(operand in active and position[operand] < position[node], 'carrier DAG order')
                successors[operand].append(node)
    for role, node in rootnodes.items():
        caps[node].extend(rootann[role])
    arcs = witness['matching_arcs']
    need(len(arcs) == record['matched'] and len({x for x, _ in arcs}) == len(arcs) and
         len({code for _, code in arcs}) == len(arcs), 'matching arcs')
    for node, code in arcs:
        need(node in active and args[node] is not None and type(code) is int and code >= 0,
             'matching donor')
        if code >> 31:
            j = index(code & 0x7fffffff, len(roots), 'matching root code')
            need(code >> 31 == 1, 'matching root code high bits')
            role = word['rootroles'][j]
            value = rootnodes[role]
            caps[node].extend(rootann[role])
        else:
            target, operand_number = code // 2, code & 1
            need(target in active and args[target] is not None and position[node] < position[target],
                 'matching target order')
            value = args[target][operand_number]
            successors[node].append(target)
        need(value in args[node], 'matching value')
    ann = [None] * n
    for node in reversed(order):
        ann[node] = echelon(tuple(caps[node]) + tuple(x for child in successors[node] for x in ann[child]))
        need(ann[node] == frame(witness['annihilators'][node], h, 'backward annihilator'),
             'incomplete backward intersection')
        need(inside(spans[node], orthogonal(ann[node], h)), 'backward support containment')
    ops, coefficients = word['ops'], word['opcoeff']
    need(len(ops) == len(coefficients) == record['total_M_operations'], 'operation count')
    frames = []
    for (dst, src, node), (ca, cb) in zip(ops, coefficients):
        index(dst, roles, 'operation destination'); index(src, roles, 'operation source')
        need(dst != src and node in active and type(ca) is int and type(cb) is int and
             ca in (-1, 1) and cb in (-1, 1), 'signed operation domain')
        frames.append(orthogonal(ann[node], h))
    seen = set()
    for operation, vectors in edits:
        index(operation, len(ops), 'operation frame index')
        need(operation not in seen, 'duplicate operation frame')
        seen.add(operation)
        cap = frame(vectors, h, 'operation override')
        need(cap != frames[operation], 'unmoved override')
        frames[operation] = cap
    for i, (_, _, node) in enumerate(ops):
        need(inside(spans[node], frames[i]), 'value span outside operation frame %d' % i)
    phase = word['phase1']
    need(phase == sorted(set(phase)) and all(type(i) is int and 0 <= i < len(ops) for i in phase),
         'phase indices')
    phase_set = set(phase)
    rest = [i for i in range(len(ops)) if i not in phase_set]
    chronology = phase + rest
    clock = {i: k for k, i in enumerate(chronology)}
    sources = {int(node): role for node, role in word['sources'].items()}
    need(set(sources) == set(range(1, v + 1)) and len(set(sources.values())) == v, 'source roles')
    start, values = [()] * roles, [(0, 0)] * roles
    for node, role in sources.items():
        index(role, roles, 'source role')
        start[role], values[role] = (inputs[node - 1],), (positive[node], negative[node])
    role_ops, last = defaultdict(list), {}
    for i in chronology:
        (dst, src, node), (ca, cb) = ops[i], coefficients[i]
        if i in phase_set:
            need(all(s not in last or last[s] in phase_set for s in (dst, src)), 'phase dependency')
        for role in (dst, src):
            role_ops[role].append(i); last[role] = i
        pa, na = values[dst]; pb, nb = values[src]
        need(not (pa | na) & (pb | nb), 'physical operands overlap')
        if ca == -1: pa, na = na, pa
        if cb == -1: pb, nb = nb, pb
        values[dst] = (pa | pb, na | nb)
        need(values[dst] == (positive[node], negative[node]), 'physical signed value')
    for role, node in rootnodes.items():
        need(values[role] == (positive[node], negative[node]), 'physical root value')
        if rootkind[role] == 'center':
            need(role not in last or last[role] in phase_set, 'center phase closure')
    # Reach is a conservative support inventory, recomputed from every actual gate.
    reach = [0] * roles
    for root, role in zip(roots, word['rootroles']):
        reach[role] = sum(1 << t for t in root['targets'])
    for dst, src, _ in reversed(ops):
        reach[src] |= reach[dst]
    gauges, selected = {}, word['selected']
    for item in selected:
        role = index(item['role'], roles, 'selected role')
        need(role not in gauges and role not in sources.values() and role_ops[role] and
             all(i not in phase_set for i in role_ops[role]), 'selected role eligibility')
        annihilator = frame(item['annihilator'], h, 'gauge annihilator')
        gauge = orthogonal(annihilator, h)
        need(len(gauge) == item['rank'] > 0, 'gauge rank')
        targets = [t for t in range(v) if reach[role] >> t & 1]
        need(targets == item['targets'], 'selected target coverage')
        need(inside(gauge, frames[role_ops[role][0]]), 'gauge entrance containment')
        gauges[role], start[role] = gauge, gauge
    donors, recipient, deadlines = {}, {}, {}
    for a, b, when in pairs:
        index(a, roles, 'donor index'); index(b, roles, 'recipient index')
        need(a != b and a not in donors and b not in recipient, 'duplicate alias pair')
        donors[a], recipient[b], deadlines[b] = b, a, when
    need(not set(donors) & set(recipient), 'alias chain')
    for a, b in donors.items():
        need(a not in gauges and a not in rootframe and role_ops[a] and b in gauges and role_ops[b],
             'alias role kinds')
        end, beginning = role_ops[a][-1], role_ops[b][0]
        when = deadlines[b]
        if when is None:
            need(end in phase_set and beginning not in phase_set, 'early alias chronology')
        else:
            index(when, len(ops), 'alias deadline index')
            need(when == beginning and when not in phase_set and clock[end] < clock[when],
                 'late alias chronology')
        need(inside(frames[end], gauges[b]), 'alias frame handoff')
    def chain(role):
        return [start[role]] + [frames[i] for i in role_ops[role]] + \
               ([rootframe[role]] if role in rootframe else []) + [full]
    local, chain_edges = Counter(), 0
    for role in range(roles):
        seq = chain(role)
        need(all(inside(left, right) for left, right in zip(seq, seq[1:])), 'role chain nesting')
        if role in recipient:
            continue
        if role in sources.values(): local[1] += 1
        if role in donors: seq = seq[:-1] + chain(donors[role])
        for left, right in zip(seq, seq[1:]):
            need(inside(left, right), 'spliced chain nesting')
            chain_edges += 1
            if len(right) > len(left): local[len(right) - len(left)] += 1
        for endpoint in (role, donors.get(role)):
            if endpoint is not None and rootkind.get(endpoint) == 'center':
                local[len(rootframe[endpoint])] += 1
    # Read ordering is taken from the literal program, including pair insertion
    # order at equal deadlines; it is not inferred from frame dimensions.
    late = defaultdict(list)
    for _, role, when in pairs:
        if when is not None: late[when].append(role)
    read_order = [item['role'] for item in reversed(selected) if deadlines.get(item['role']) is None]
    for operation in rest: read_order.extend(late[operation])
    need(len(read_order) == len(gauges) and set(read_order) == set(gauges), 'old-value read inventory')
    selected_by_role = {item['role']: item for item in selected}
    current, target = [full] * v, Counter()
    for role in read_order:
        item = selected_by_role[role]
        cap = tuple(item['annihilator'])
        for t in item['targets']:
            need(inside(cap, current[t]), 'actual target read order')
            target[len(current[t]) - len(cap)] += 1; current[t] = cap
    for root, role in zip(roots, word['rootroles']):
        if root['kind'] == 'side':
            for t in root['targets']:
                cap = rootann[role]
                need(inside(cap, current[t]), 'side target order')
                target[len(current[t]) - len(cap)] += 1; current[t] = cap
    for t, q in enumerate(inputs):
        need(inside((q,), current[t]), 'target original-source cap')
        target[len(current[t]) - 1] += 1
    # Derive the destructive K source transitions from each actual eight-port
    # block and signed Hadamard identity, rather than copy a supplied histogram.
    source, cube_count = Counter(), 0
    need(v % 8 == 0, 'cube partition')
    for offset in range(0, v, 8):
        qs = inputs[offset:offset + 8]
        need(len({tuple(i // 2 for i in g['labels'][offset + j]) for j in range(8)}) == 1,
             'cube labels')
        matrix = [[1 if (x ^ y).bit_count() == 6 else -1 if (x ^ y).bit_count() == 2 else 0
                   for y in qs] for x in qs]
        need(all(sum(matrix[i][k] * matrix[k][j] for k in range(8)) == 4 * (i == j)
                 for i in range(8) for j in range(8)), 'exact K inverse')
        for parity in (0, 1):
            src = [i for i in range(8) if i.bit_count() % 2 == parity]
            dst = [i for i in range(8) if i not in src]
            common = echelon(qs[i] for i in src)
            need(len(common) == 3 and all(inside((qs[i],), common) for i in src), 'K common source frame')
            need(all(inside(common, orthogonal((qs[j],), h)) for j in dst), 'K destination cap')
            need(all(sum(matrix[i][k] * matrix[j][k] for k in src) == 4 * (i == j)
                     for i in dst for j in dst), 'signed K block inverse')
            for t in dst:
                cap = orthogonal((qs[t],), h)
                need(inside(cap, full), 'K final full frame')
                source[len(common) - 1] += 1
                source[len(cap) - len(common)] += 1
                source[h - len(cap)] += 1
        cube_count += 1
    need(dict(source) == {int(k): count for k, count in record['source_data_histogram'].items()},
         'source histogram differs from construction')
    need(dict(target) == {int(k): count for k, count in record['target_data_histogram'].items()},
         'target histogram differs from literal chronology')
    tails = Counter(len(cap) for role, cap in gauges.items() if role not in recipient)
    children = Counter({r: 3 * count for r, count in local.items() if r})
    children.update({r: 3 * count for r, count in source.items() if r})
    children.update({r: 3 * count for r, count in target.items() if r})
    children.update({3 * r: count for r, count in tails.items() if r})
    children[2] += 2 * v
    m, width = 3 * h, 2 * v + roles - len(pairs)
    mass = sum(r * count for r, count in children.items())
    center_loss = sum(len(cap) for role, cap in rootframe.items() if rootkind[role] == 'center')
    need(center_loss == record['loss'] and m * width - mass == 2 * v - 3 * center_loss ==
         record['deficit_per_vertex'], 'complete rank deficit')
    need(all(0 < r < m and type(count) is int and count > 0 for r, count in children.items()),
         'complete child domain')
    return dict(h=h, v=v, R=roles, physical_R=roles - len(pairs), pairs=len(pairs),
                late_pairs=sum(when is not None for when in deadlines.values()),
                changed_operation_frames=len(edits), m=m, W_per_vertex=width,
                rank_per_vertex=mass, deficit_per_vertex=m * width - mass, loss=center_loss,
                local_histogram=dict(sorted(local.items())), physical_gauge_histogram=dict(sorted(tails.items())),
                source_data_histogram=dict(sorted(source.items())), target_data_histogram=dict(sorted(target.items())),
                child_histogram=dict(sorted(children.items())), edge_count=sum(children.values()),
                max_child=max(children), checked_chain_edges=chain_edges,
                checked_signed_operations=len(ops), checked_backward_intersections=len(order),
                checked_K_blocks=2 * cube_count, actual_deferred_read_count=len(read_order))


def check_hashes(paths, expected):
    result = {key: sha256(path.read_bytes()).hexdigest() for key, path in paths.items()}
    for key, digest in expected.items():
        need(result[key] == digest, 'immutable scalar input changed: ' + key)
    return result


def compare_profile(result, profile):
    for key in ('h', 'v', 'R', 'physical_R', 'pairs', 'late_pairs', 'changed_operation_frames',
                'm', 'W_per_vertex', 'rank_per_vertex', 'deficit_per_vertex', 'loss'):
        need(result[key] == profile[key], 'independent profile differs: ' + key)
    for key in ('local_histogram', 'physical_gauge_histogram', 'source_data_histogram',
                'target_data_histogram', 'child_histogram'):
        need(result[key] == {int(k): count for k, count in profile[key].items()},
             'independent profile differs: ' + key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--frames', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--scalar-receipt', type=Path, required=True,
                        help='Only input_sha256 is read; verdicts are never used')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    sys.set_int_max_str_digits(0)
    started = time.monotonic()
    started_utc = datetime.now(timezone.utc).isoformat()
    paths = dict(graph=args.export / 'graph.json', witness=args.export / 'frames.json',
                 word=args.export / 'selection.json', pairs=args.tree / 'references/paired-cube/physical/pairs.json',
                 record=args.tree / 'certificates/paired-cube-complex-input.json', candidate_frames=args.frames)
    pinned = json.loads(args.scalar_receipt.read_text())['input_sha256']
    hashes = check_hashes(paths, pinned)
    cert = json.loads((args.tree / 'certificates/paired-cube-network.json').read_text())
    source_count = 0
    for name, digest in cert['source_sha256'].items():
        path = Path(name)
        need(not path.is_absolute() and '..' not in path.parts, 'unsafe source path')
        need(sha256((args.tree / path).read_bytes()).hexdigest() == digest, 'source fingerprint changed: ' + name)
        source_count += 1
    data = {key: json.loads(path.read_text()) for key, path in paths.items()}
    edits = data['candidate_frames']
    if isinstance(edits, dict): edits = edits['frames']
    pairs = data['pairs']['pairs']
    result = verify(data['graph'], data['witness'], data['word'], data['record'], edits, pairs)
    profile = json.loads(args.profile.read_text())
    compare_profile(result, profile)
    controls = {}
    def reject(name, function):
        try:
            function()
        except (ValueError, KeyError, IndexError, TypeError) as error:
            controls[name] = str(error)
        else:
            raise ValueError('negative control accepted: ' + name)
    broken = deepcopy(edits); broken[0][0] = -1
    reject('illegal_negative_frame_index', lambda: verify(data['graph'], data['witness'], data['word'], data['record'], broken, pairs))
    broken = deepcopy(edits); broken[0][1] = list(orthogonal(tuple(broken[0][1]), result['h']))
    reject('bad_frame_complement', lambda: verify(data['graph'], data['witness'], data['word'], data['record'], broken, pairs))
    broken_word = deepcopy(data['word']); broken_word['selected'][0]['targets'].pop()
    reject('omitted_selected_target', lambda: verify(data['graph'], data['witness'], broken_word, data['record'], edits, pairs))
    broken_pairs = deepcopy(pairs); broken_pairs[0][2] = 0
    reject('premature_compensation_deadline', lambda: verify(data['graph'], data['witness'], data['word'], data['record'], edits, broken_pairs))
    broken_word = deepcopy(data['word'])
    first = broken_word['ops'][0]
    broken_word['ops'].extend((first, first)); broken_word['opcoeff'].extend(([1, 1], [1, -1]))
    reject('unpaid_cancelling_operations', lambda: verify(data['graph'], data['witness'], broken_word, data['record'], edits, pairs))
    false_hashes = dict(pinned, graph='0' * 64)
    reject('source_pin_corruption', lambda: check_hashes(paths, false_hashes))
    with tempfile.TemporaryDirectory(prefix='independent-source-corruption-') as temporary:
        corrupt = Path(temporary) / 'graph.json'
        original = paths['graph'].read_bytes()
        corrupt.write_bytes(original[:-1] + b' ')
        corrupt_paths = dict(paths, graph=corrupt)
        reject('source_byte_corruption', lambda: check_hashes(corrupt_paths, pinned))
    H = Counter(result['child_histogram'])
    keys = sorted(H)
    a, b, c = next((a, b, c) for a in keys for b in keys for c in keys
                   if a < b < c and a + c == 2 * b and H[b] >= 2)
    false = H.copy(); false[a] += 1; false[b] -= 2; false[c] += 1
    need(sum(false.values()) == sum(H.values()) and sum(r * n for r, n in false.items()) ==
         sum(r * n for r, n in H.items()), 'mass-preserving control setup')
    false_profile = deepcopy(profile)
    false_profile['child_histogram'] = {str(r): count for r, count in false.items()}
    reject('mass_preserving_histogram', lambda: compare_profile(result, false_profile))
    result.update(status='PASS_INDEPENDENT_EXACT_FORWARD_FRAMES', input_sha256=hashes,
                  source_files_checked=source_count, negative_controls=controls,
                  started_utc=started_utc, finished_utc=datetime.now(timezone.utc).isoformat(),
                  checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  elapsed_seconds=time.monotonic() - started,
                  scope='Independent signed-support, full backward-intersection, actual role/pair/target chronology, '
                        'GF(2) containment, original K source itinerary and complete paid histogram audit. '
                        'Arbitrary-dirty scalar coefficients and signed cleanup are checked separately; '
                        'complemented time reversal and all-size Clifford/transfer contracts are separate.')
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
