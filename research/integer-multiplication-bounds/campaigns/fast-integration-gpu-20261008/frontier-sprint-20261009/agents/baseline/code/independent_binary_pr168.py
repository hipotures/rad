#!/usr/bin/env python3
"""Independent PR168 native binary construction, placement and prime-unit review.

No upstream or discovery Python is imported. Exact integer elimination,
Gram/adjugate projector certificates, literal all-column replay, carrier and
actual target chronology, partner-pair K, and every paid child are rebuilt.
Fixed rational G=I-J/9 frames use unit primal/dual Gram denominators, so their
projectors and checked nesting identities extend to each permitted odd local
ring. The weighted all-size compiler/layout remain explicit inherited contracts.

The PR161/163 mathematical word is due to its retained contributors including
icekylinx, eumemic and chafreaky (Apache-2.0). Authored by RaD with OpenAI
GPT-6.1 Sol assistance; Gram formulas are the standard primal/dual projection
identities, not modular agreement at sampled primes.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys
import time


def need(ok, message):
    if not ok: raise ValueError(message)


def ix(value, limit, message):
    need(type(value) is int and 0 <= value < limit, message)
    return value


from binary_exact_algebra import reduce_rows, nullspace


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


class Frame:
    __slots__ = ('B', 'A', 'h', 'dim', 'presentation', 'gram', 'den', 'N')
    def __init__(self, h, *, B=None, A=None):
        self.h = h
        if B is not None:
            raw = tuple(tuple(row) for row in B)
            self.B = reduce_rows(raw, h)
            need(len(self.B) == len(raw), 'dependent basis rows')
            self.A = nullspace(self.B, h)
        else:
            raw = tuple(tuple(row) for row in A)
            self.A = reduce_rows(raw, h)
            need(len(self.A) == len(raw), 'dependent annihilator rows')
            self.B = nullspace(self.A, h)
        self.dim = len(self.B)
        need(self.dim + len(self.A) == h and all(dot(a, b) == 0 for a in self.A for b in self.B),
             'exact rank/dimension/A B^T certificate')
        self.presentation = 'primal_basis' if self.dim <= len(self.A) else 'dual_annihilator'
        rows = self.B if self.presentation == 'primal_basis' else self.A
        sums = list(map(sum, rows))
        self.gram = tuple(tuple((9 * dot(x, y) - sums[i] * sums[j])
                               if self.presentation == 'primal_basis'
                               else ((9 - h) * dot(x, y) + sums[i] * sums[j])
                               for j, y in enumerate(rows)) for i, x in enumerate(rows))
        self.den = determinant(self.gram)
        need(self.den != 0, 'G-degenerate frame')
        self.N = None


@lru_cache(maxsize=60000)
def determinant(matrix):
    if not matrix: return 1
    a = [list(row) for row in matrix]; size = len(a)
    previous, sign = 1, 1
    for k in range(size - 1):
        pivot = next((i for i in range(k, size) if a[i][k]), None)
        if pivot is None: return 0
        if pivot != k: a[k], a[pivot] = a[pivot], a[k]; sign = -sign
        value = a[k][k]
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                numerator = value * a[i][j] - a[i][k] * a[k][j]
                need(numerator % previous == 0, 'Bareiss exact division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = value
    return sign * a[-1][-1]


@lru_cache(maxsize=10000)
def adjugate(matrix):
    size = len(matrix)
    if not size: return ()
    determinant_value = determinant(matrix)
    rows = [[Q(x) for x in row] + [Q(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        need(pivot is not None, 'singular projector Gram')
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [x / divisor for x in rows[column]]
        for i in range(size):
            if i == column or not rows[i][column]: continue
            multiplier = rows[i][column]
            rows[i] = [x - multiplier * y for x, y in zip(rows[i], rows[column])]
    result = tuple(tuple(x * determinant_value for x in row[size:]) for row in rows)
    need(all(x.denominator == 1 for row in result for x in row), 'hidden adjugate denominator')
    result = tuple(tuple(int(x) for x in row) for row in result)
    need(all(sum(matrix[i][k] * result[k][j] for k in range(size)) ==
             determinant_value * (i == j) for i in range(size) for j in range(size)),
         'exact Gram adjugate identity')
    return result


def projector(frame):
    """Integral numerator and one proved unit denominator; no hidden fractions.

    Primal: P=B^T D^-1 B(9I-J), D=9B B^T-(B1)(B1)^T.
    Dual: P=I-H A^T D^-1 A, H=(9-h)I+J, D=A H A^T.
    These define the same rational projector and remain split idempotents
    whenever det(D), 9 and 9-h are units. For dual presentation the local
    module is ker(A), so a scaled B lattice is not mistaken for that module.
    """
    if frame.N is not None: return frame.N
    h, d = frame.h, frame.den
    rows = frame.B if frame.presentation == 'primal_basis' else frame.A
    adj = adjugate(frame.gram); size = len(rows)
    left = [[sum(rows[k][i] * adj[k][j] for k in range(size)) for j in range(size)]
            for i in range(h)]
    middle = [[sum(left[i][k] * rows[k][j] for k in range(size)) for j in range(h)]
              for i in range(h)]
    if frame.presentation == 'primal_basis':
        numerator = tuple(tuple(9 * middle[i][j] - sum(middle[i]) for j in range(h)) for i in range(h))
    else:
        column_sums = [sum(middle[i][j] for i in range(h)) for j in range(h)]
        numerator = tuple(tuple(d * (i == j) - (9 - h) * middle[i][j] - column_sums[j]
                                for j in range(h)) for i in range(h))
    need(all(sum(a[k] * numerator[k][j] for k in range(h)) == 0 for a in frame.A for j in range(h)),
         'projector image lies in exact annihilator kernel')
    need(all(sum(numerator[i][k] * b[k] for k in range(h)) == d * b[i]
             for b in frame.B for i in range(h)), 'projector fixes exact frame basis')
    need(all(sum(numerator[i][k] * numerator[k][j] for k in range(h)) == d * numerator[i][j]
             for i in range(h) for j in range(h)), 'cleared projector idempotence')
    column_sums = [sum(numerator[i][j] for i in range(h)) for j in range(h)]
    need(all(9*numerator[i][j]-column_sums[j] == 9*numerator[j][i]-column_sums[i]
             for i in range(h) for j in range(h)), 'cleared G-selfadjoint projector')
    need(sum(numerator[i][i] for i in range(h)) == d * frame.dim, 'exact projector rank trace')
    # All displayed identities are cleared integer polynomial identities.
    # Unit denominators therefore extend them to every permitted Z/q^w.
    frame.N = numerator
    return numerator


@lru_cache(maxsize=180000)
def contains(left_B, right_A):
    return all(dot(a, b) == 0 for a in right_A for b in left_B)


def inside(left, right):
    return left.dim <= right.dim and contains(left.B, right.A)


class ReflectedFrame:
    """G-orthogonal complement with the same exact representative denominator.

    Over the local ring its projector is I-P, so its split-module rank is
    h-dim(F). Integer B/A rows below describe its rational geometry only;
    their possibly scaled Gram determinants are not additional unit gates.
    """
    def __init__(self, original):
        self.h = original.h
        self.A = reduce_rows(tuple(tuple(9*x-sum(b) for x in b) for b in original.B), self.h)
        self.B = nullspace(self.A, self.h)
        self.dim = len(self.B)
        need(self.dim == self.h-original.dim and all(dot(a,b)==0 for a in self.A for b in self.B), 'exact G-complement dimension and annihilation')
        self.original = original


@lru_cache(maxsize=60000)
def complement(original):
    return ReflectedFrame(original)


def paid_program_binding(actual, canonical):
    need(actual == canonical, 'literal program differs from complete paid chronology')


def reflected_chronology(events, initial, final, v):
    """Literal inverse with complemented frames and both data banks renamed."""
    def swap(register): return (register+v) % (2*v) if register < 2*v else register
    reflected = []
    for event in reversed(events):
        kind = event[0]
        if kind == 'advance':
            _, register, before, after = event
            reflected.append((kind, swap(register), complement(after), complement(before)))
        elif kind == 'copy':
            _, source, targets, source_frame, read_frame = event
            reflected.append((kind, swap(source), tuple(swap(r) for r in targets),
                              complement(source_frame), complement(read_frame)))
        else:
            _, registers, frame = event
            reflected.append((kind, tuple(swap(r) for r in registers), complement(frame)))
    current = {swap(r):complement(f) for r,f in final.items()}
    expected = {swap(r):complement(f) for r,f in initial.items()}
    counts, stats = replay_geometry(reflected, current, expected)
    return reflected, counts, stats


def replay_geometry(events, initial, final):
    current = dict(initial); counts = Counter(); incidences = Counter()
    for event in events:
        kind = event[0]
        if kind == 'advance':
            _, register, before, after = event
            need(current[register].B == before.B, 'physical transition starts at actual frame')
            need(inside(before, after), 'physical chronological frame transition')
            width = after.dim-before.dim
            if width: counts[width] += 1
            current[register] = after; incidences['frame_transitions'] += 1
        elif kind == 'copy':
            _, source, targets, source_frame, read_frame = event
            need(current[source].B == source_frame.B and
                 all(current[r].B == read_frame.B for r in targets), 'copied-center actual incidence')
            # Forward copy: T_0 T_U^-1. Reflected copy:
            # D_0 D_U^-1=T_U^-1, D_U=T_U F^-1. Same paid width.
            need(inside(read_frame,source_frame) or inside(source_frame,read_frame), 'copied-center comparable endpoints')
            width = abs(source_frame.dim-read_frame.dim)
            if width: counts[width] += 1
            incidences['copied_centers'] += 1; incidences['center_scatter_targets'] += len(targets)
        else:
            _, registers, frame = event
            need(kind in ('xor','broadcast') and len(registers) >= 2 and len(set(registers))==len(registers),
                 'physical scalar event domain')
            need(all(current[r].B == frame.B for r in registers), 'physical common-frame scalar incidence')
            incidences[kind] += 1
    need(set(current)==set(final) and all(current[r].B==f.B for r,f in final.items()), 'complete physical endpoints')
    return counts, dict(incidences)


def bits(mask):
    while mask:
        low = mask & -mask; mask ^= low; yield low.bit_length() - 1


def formal(events, v, roles, *, reflected=False):
    total = 2 * v + roles
    data = [1 << i for i in range(total)]
    def mapped(i):
        return (i + v) % (2 * v) if reflected and i < 2 * v else i
    for event in reversed(events) if reflected else events:
        if event[0] == 'xor':
            _, destination, source = event
            ix(destination, total, 'literal destination index'); ix(source, total, 'literal source index')
            need(destination != source, 'literal self-port')
            data[mapped(destination)] ^= data[mapped(source)]
        else:
            need(event[0] == 'broadcast', 'literal event kind')
            _, source, targets = event
            ix(source, total, 'literal broadcast source')
            for target in bits(targets):
                ix(target, total, 'literal broadcast target')
                need(target != source, 'literal broadcast self-port')
                data[mapped(target)] ^= data[mapped(source)]
    for i, value in enumerate(data):
        expected = 1 << i
        if (0 <= i < v) if reflected else (v <= i < 2 * v):
            expected ^= 1 << (i + v if reflected else i - v)
        need(value == expected, 'complete formal F2 column identity at register %d' % i)
    return dict(formal_variables=total, exact_scalar_coefficients=total * total,
                orientation='inverse time reversal with bank swap' if reflected else 'forward',
                literal_events=len(events), all_dirty_and_source_columns_restored=True)


def reconstruct(source, export, plan, expected_profile):
    read = lambda name: json.loads((export / (name + '_p12.json')).read_text())
    g, w, fr, k = [read(name) for name in ('graph', 'word', 'frames', 'kchron')]
    h, v, args = g['h'], g['v'], g['args']
    need((h, v, g['p'], plan['p']) == (24, 1760, 12, 12), 'retained dimensions')
    frames = {}
    for key, record in fr['frames'].items():
        identity = int(key)
        need(identity >= 0, 'negative frame identity')
        obj = Frame(h, A=record['a']) if 'a' in record else Frame(h, B=record['b'])
        need(obj.dim == record['dim'], 'frozen frame dimension')
        frames[identity] = obj
    full = frames[w['full_frame']]
    need(full.dim == h, 'full active frame')
    labels = g['labels']
    need(len(labels) == v and len({tuple(x) for x in labels}) == v and
         all(len(x) == 3 and len(set(x)) == 3 and all(type(i) is int and 0 <= i < h for i in x) for x in labels),
         'actual subset source labels')
    chi = [tuple(int(i in label) for i in range(h)) for label in labels]
    cov = [tuple(3 * x - 1 for x in row) for row in chi]
    support = [1 << i for i in range(v)] + [0] * (len(args) - v)
    for node, item in enumerate(args):
        if node < v: need(item is None, 'source DAG leaf'); continue
        need(isinstance(item, list) and len(item) == 2, 'binary DAG node')
        a, b = item
        need(type(a) is int and type(b) is int and 0 <= a < node and 0 <= b < node,
             'DAG order')
        need(not support[a] & support[b], 'conservative supports overlap')
        support[node] = support[a] | support[b]
    nf = {int(node): frames[identity] for node, identity in w['node_frame'].items()}
    need(set(nf) == set(range(len(args))), 'complete node frame inventory')
    for node, obj in nf.items():
        if node < v: need(contains((chi[node],), obj.A), 'source node containment')
        else: need(all(inside(nf[operand], obj) for operand in args[node]), 'original node nesting')
    roots, root_roles, root_frames = g['roots'], w['rootroles'], [frames[i] for i in w['root_frame']]
    need(len(roots) == len(root_roles) == len(root_frames), 'root inventory')
    source_roles = {int(leaf): role for leaf, role in w['sources'].items()}
    ops = w['ops']; roles = 1 + max(max(a, b) for a, b, _ in ops)
    need(roles == expected_profile.get('virtual_R', expected_profile['R']) and set(source_roles) == set(range(v)) and
         len(set(source_roles.values())) == v, 'actual role/source inventory')
    opframes = [nf[node] for _, _, node in ops]
    new = {}; seen = set()
    for operation, basis in plan['frames']:
        ix(operation, len(ops), 'operation frame index')
        need(operation not in seen and basis, 'duplicate or empty frame override')
        seen.add(operation)
        obj = Frame(h, B=basis)
        need(not (inside(obj, opframes[operation]) and inside(opframes[operation], obj)), 'unmoved frame override')
        key = obj.B
        if key not in new: new[key] = obj
        opframes[operation] = new[key]
    for i, (a, b, node) in enumerate(ops):
        ix(a, roles, 'operation destination'); ix(b, roles, 'operation source'); ix(node, len(args), 'operation node')
        need(a != b and all(contains((chi[s],), opframes[i].A) for s in bits(support[node])),
             'value containment at operation %d' % i)
    # Exact decoder, copied stars and literal partner contribution.
    target_decoder, side_decoder, stars = [0] * v, [0] * v, [set() for _ in range(v)]
    center_loss = 0
    for j, (root, role, cap) in enumerate(zip(roots, root_roles, root_frames)):
        ix(role, roles, 'root role'); ix(root['node'], len(args), 'root node')
        need(root.get('coefficient', 1) == 1 and len(set(root['targets'])) == len(root['targets']), 'unit root readout')
        need(inside(nf[root['node']], cap), 'root physical node containment')
        if root['kind'] == 'center':
            coordinate = ix(root['coordinate'], h, 'star coordinate')
            source_set = [s for s in range(v) if coordinate in labels[s]]
            need(support[root['node']] == sum(1 << s for s in source_set), 'exact copied star support')
            need(len(reduce_rows(tuple(chi[s] for s in source_set), h)) == cap.dim and
                 all(contains((chi[s],), cap.A) for s in source_set), 'copied center exact span')
            center_loss += cap.dim
        else:
            need(root['kind'] == 'side' and all(dot(cov[t], b) == 0 for t in root['targets'] for b in cap.B),
                 'side frame in receiver caps')
            need(cap.dim == h - len(reduce_rows(tuple(cov[t] for t in root['targets']), h)), 'exact common side cap')
        for t in root['targets']:
            ix(t, v, 'root target'); target_decoder[t] ^= support[root['node']]
            if root['kind'] == 'center': stars[t].add(root['coordinate'])
            else: side_decoder[t] ^= support[root['node']]
    source_hist = Counter(); deliveries = defaultdict(list); members = Counter()
    for entry in k['entries']:
        c, d = entry['carrier'], entry['passive']
        ix(c, v, 'K carrier'); ix(d, v, 'K passive')
        need(c != d and len(set(labels[c]) & set(labels[d])) == 1, 'K orthogonal partner addresses')
        mix, cap = frames[entry['mix_frame']], frames[entry['deliver_frame']]
        need(mix.dim == 2 and contains((chi[c], chi[d]), mix.A) and inside(mix, cap), 'K exact mixing/common frame')
        need(all(dot(cov[t], b) == 0 for t in entry['receivers'] for b in cap.B), 'K delivery cap')
        j = ix(entry['deliver_after_root'], len(roots), 'K root deadline')
        need(roots[j]['kind'] == 'side' and sorted(entry['receivers']) == sorted(roots[j]['targets']), 'K actual delivery chronology')
        need(entry['undo_frame'] == w['full_frame'] and
             entry['carrier_chain'] == [w['source_frame'][c], entry['mix_frame'], entry['deliver_frame'], w['full_frame']] and
             entry['passive_chain'] == [w['source_frame'][d], entry['mix_frame'], w['full_frame']], 'K mix/unmix endpoint shape')
        for chain in (entry['carrier_chain'], entry['passive_chain']):
            for before, after in zip(chain, chain[1:]):
                need(inside(frames[before], frames[after]), 'K source chain nesting')
                source_hist[frames[after].dim - frames[before].dim] += 1
        deliveries[j].append(entry); members[c] += 1; members[d] += 1
        for t in entry['receivers']:
            target_decoder[t] ^= (1 << c) | (1 << d); side_decoder[t] ^= (1 << c) | (1 << d)
    need(all(members[s] == 1 for s in range(v)), 'one literal K pair per source')
    for t in range(v):
        need(target_decoder[t] == 1 << t and stars[t] == set(labels[t]), 'complete defining F2 decoder')
        need(side_decoder[t] == sum(1 << s for s in range(v) if len(set(labels[s]) & set(labels[t])) == 1),
             'complete side decoder support')
    # Regenerate phase closure and the true deadlines of untouched old reads.
    phase = set(w['phase1']); previous = {}; predecessors = []
    for i, (a, b, _) in enumerate(ops):
        predecessors.append((previous.get(a, -1), previous.get(b, -1))); previous[a] = previous[b] = i
    closure = set(); stack = [previous[role] for root, role in zip(roots, root_roles) if root['kind'] == 'center' and role in previous]
    while stack:
        i = stack.pop()
        if i not in closure: closure.add(i); stack.extend(j for j in predecessors[i] if j >= 0)
    need(closure == phase, 'actual center phase closure')
    phase_order = sorted(phase); rest = [i for i in range(len(ops)) if i not in phase]
    chronology = phase_order + rest; rest_clock = {i: j for j, i in enumerate(rest)}
    role_ops = defaultdict(list); first = {}
    for i in chronology:
        for role in ops[i][:2]: role_ops[role].append(i); first.setdefault(role, rest_clock.get(i, -1))
    gauges = {item['role']: item for item in w['gauges']}
    need(len(gauges) == len(w['gauges']), 'duplicate gauges')
    response = [0] * roles; conservative = [0] * roles
    for root, role in zip(roots, root_roles):
        for t in root['targets']: response[role] ^= 1 << t; conservative[role] |= 1 << t
    for a, b, _ in reversed(ops): response[b] ^= response[a]; conservative[b] |= conservative[a]
    old_order = [item['role'] for item in reversed(w['gauges'])]; readtime = {}; next_target = {}
    for role in reversed(old_order):
        item = gauges[role]; cap = frames[item['frame']]
        ix(role, roles, 'gauge role')
        need(role not in source_roles.values() and first[role] >= 0 and cap.dim == item['dim'] > 0 and
             sum(1 << t for t in item['targets']) == conservative[role], 'gauge eligibility and full response coverage')
        times = [first[role]] + [next_target[t][1] for t in item['targets'] if t in next_target and
                                not inside(next_target[t][0], cap)]
        readtime[role] = min(times)
        for t in item['targets']:
            if t not in next_target or not inside(next_target[t][0], cap): next_target[t] = (cap, readtime[role])
    at = defaultdict(list)
    for role in old_order: at[readtime[role]].append(role)
    actual_read_order = [role for when in range(len(rest) + 1) for role in at[when]]
    need(set(actual_read_order) == set(gauges) and len(actual_read_order) == len(gauges), 'actual old-read event inventory')
    zero = Frame(h, B=[]); starts = {role: frames[w['source_frame'][s]] for s, role in source_roles.items()}
    for s, role in source_roles.items(): need(starts[role].dim == 1 and contains((chi[s],), starts[role].A), 'actual source entrance')
    starts.update({role: frames[item['frame']] for role, item in gauges.items()})
    root_sequences = defaultdict(list)
    for role, cap in zip(root_roles, root_frames): root_sequences[role].append(cap)
    local, edges = Counter(), []
    for role in range(roles):
        chain = [starts.get(role, zero)] + [opframes[i] for i in role_ops[role]] + root_sequences[role] + [full]
        if role in source_roles.values(): local[1] += 1
        for before, after in zip(chain, chain[1:]):
            need(inside(before, after), 'actual physical role nesting')
            edges.append((before, after))
            if after.dim > before.dim: local[after.dim - before.dim] += 1
    for root, cap in zip(roots, root_frames):
        if root['kind'] == 'center': local[cap.dim] += 1
    current = [zero] * v; target_hist = Counter()
    def target_read(target, cap):
        need(inside(current[target], cap) and all(dot(cov[target], b) == 0 for b in cap.B), 'actual target frame chronology')
        edges.append((current[target], cap))
        if cap.dim > current[target].dim: target_hist[cap.dim - current[target].dim] += 1
        current[target] = cap
    for role in actual_read_order:
        for t in gauges[role]['targets']: target_read(t, frames[gauges[role]['frame']])
    for j, (root, cap) in enumerate(zip(roots, root_frames)):
        if root['kind'] != 'center':
            for t in root['targets']: target_read(t, cap)
        for entry in deliveries[j]:
            for t in entry['receivers']: target_read(t, frames[entry['deliver_frame']])
    for t in range(v):
        final = Frame(h, A=[cov[t]])
        need(inside(current[t], final), 'final target cap')
        edges.append((current[t], final))
        if final.dim > current[t].dim: target_hist[final.dim - current[t].dim] += 1
    children = Counter()
    for inventory in (local, target_hist, source_hist):
        for rank, count in inventory.items():
            if rank: children[rank] += 3 * count
    selected = Counter(item['dim'] for item in gauges.values())
    for rank, count in selected.items(): children[3 * rank] += count
    children[2] += 2 * v
    mass = sum(rank * count for rank, count in children.items())
    need(center_loss == 528 and 3 * h * (2 * v + roles) - mass == 2 * v - 3 * center_loss == 1936,
         'complete paid deficit')
    need(all(0 < rank < 3 * h and count > 0 for rank, count in children.items()), 'proper positive child ledger')
    actual_profile = dict(h=h, v=v, R=roles, virtual_R=roles, W_per_vertex=2 * v + roles, m=3*h,
        c=len(args)-v, q=len(roots), matched=len(w['arcs']), plain_frames=len(w['plain']),
        remaining_internal_histogram=dict(sorted(local.items())),
        loss=center_loss, rank_per_vertex=mass, deficit_per_vertex=1936,
        child_histogram=dict(sorted(children.items())), selected_rank_histogram=dict(selected),
        selected_roles=len(gauges), maxchild=max(children), edge_count=sum(children.values()),
        changed_operation_frames=len(plan['frames']), reused_registers=0,
        zero_rank_handoffs=0, foreign_producer_replays=0,
        local_histogram=dict(sorted(local.items())), source_data_histogram=dict(sorted(source_hist.items())),
        target_data_histogram=dict(sorted(target_hist.items())))
    for name, expected in expected_profile.items():
        actual = actual_profile[name]
        if isinstance(actual, dict): expected = {int(k): value for k, value in expected.items() if int(k) and value};actual={int(k):value for k,value in actual.items() if int(k) and value}
        need(actual == expected, 'fresh paid profile mismatch: ' + name)
    # Every displayed denominator is integral. Original frame exclusions are
    # retained; every new numerator/denominator is explicitly certified.
    witnesses = []
    for basis, obj in sorted(new.items()):
        need(abs(obj.den) < 2**80, 'new projector determinant exceeds retained prime threshold')
        N = projector(obj)
        witnesses.append(dict(basis_sha256=sha256(json.dumps(basis, separators=(',', ':')).encode()).hexdigest(),
            dimension=obj.dim, presentation=obj.presentation, defining_integer_rows=obj.B if obj.presentation == 'primal_basis' else obj.A,
            gram_determinant=obj.den, prime_unit_denominator=obj.den,
            projector_numerator_sha256=sha256(json.dumps(N, separators=(',', ':')).encode()).hexdigest()))
    # Clear A_V P_U=0 at each edge entering/leaving a changed frame. Original
    # projectors are constructed lazily by the identical certified formula.
    new_ids = {id(obj) for obj in new.values()}; projectors_checked = 0
    for before, after in edges:
        if id(before) not in new_ids and id(after) not in new_ids: continue
        N = projector(before)
        need(all(sum(a[k] * N[k][j] for k in range(h)) == 0 for a in after.A for j in range(h)),
             'cleared integral nested-projector identity')
        projectors_checked += 1
    # Emit every physical incidence and scalar mutation at actual deadlines.
    # Zero-rank advances are retained as paid finite scalar/router work.
    initial = {s:frames[w['source_frame'][s]] for s in range(v)}
    initial.update({v+t:zero for t in range(v)})
    initial.update({2*v+r:starts[r] if r in gauges else zero for r in range(roles)})
    physical, events, current = [], [], dict(initial)
    def advance(register, frame):
        old = current[register]
        need(inside(old,frame), 'emitted physical nesting')
        physical.append(('advance',register,old,frame)); current[register]=frame
    def xor(destination, source_register, frame):
        physical.append(('xor',(destination,source_register),frame))
        events.append(('xor',destination,source_register))
    def read(role, targets, frame, *, literal_targets=None, copied=False):
        reached = tuple(v+t for t in bits(targets))
        if copied:
            physical.append(('copy',2*v+role,reached,frame,zero))
        else:
            for target in reached: advance(target,frame)
            if reached: physical.append(('broadcast',(2*v+role,)+reached,frame))
        literal_targets = targets if literal_targets is None else literal_targets
        if literal_targets: events.append(('broadcast',2*v+role,literal_targets<<v))
    def old_read(role):
        frame=frames[gauges[role]['frame']] if role in gauges else zero
        read(role,conservative[role],frame,literal_targets=response[role])
    def operation(i):
        a,b,_=ops[i]; frame=opframes[i]
        advance(2*v+a,frame);advance(2*v+b,frame);xor(2*v+a,2*v+b,frame)
    for role in range(roles):
        if role not in gauges: old_read(role)
    for s,role in source_roles.items():
        frame=frames[w['source_frame'][s]];advance(2*v+role,frame);xor(2*v+role,s,frame)
    for i in phase_order: operation(i)
    for root,role,cap in zip(roots,root_roles,root_frames):
        if root['kind']=='center':
            advance(2*v+role,cap);read(role,sum(1<<t for t in root['targets']),cap,copied=True)
    for when,i in enumerate(rest):
        for role in at[when]: old_read(role)
        operation(i)
    for role in at[len(rest)]: old_read(role)
    for j,(root,role,cap) in enumerate(zip(roots,root_roles,root_frames)):
        if root['kind']!='center':
            advance(2*v+role,cap);read(role,sum(1<<t for t in root['targets']),cap)
        for entry in deliveries[j]:
            c,d=entry['carrier'],entry['passive'];mix=frames[entry['mix_frame']];delivery=frames[entry['deliver_frame']]
            advance(c,mix);advance(d,mix);xor(c,d,mix);advance(c,delivery)
            reached=tuple(v+t for t in entry['receivers'])
            for target in reached:advance(target,delivery)
            physical.append(('broadcast',(c,)+reached,delivery))
            events.append(('broadcast',c,sum(1<<t for t in entry['receivers'])<<v))
    for t in range(v):advance(v+t,Frame(h,A=[cov[t]]))
    for entry in k['entries']:
        c,d=entry['carrier'],entry['passive'];advance(c,full);advance(d,full);xor(c,d,full)
    for role in range(roles):advance(2*v+role,full)
    for i in reversed(chronology):a,b,_=ops[i];xor(2*v+a,2*v+b,full)
    for s,role in source_roles.items():xor(2*v+role,s,full)
    final=dict(current)
    forward_counts, forward_stats=replay_geometry(physical,initial,final)
    reflected, reflected_counts, reflected_stats=reflected_chronology(physical,initial,final,v)
    expected_counts=local+target_hist+source_hist
    need(forward_counts==expected_counts==reflected_counts, 'emitted forward/reflected complete positive-width ledger')
    full_reflected=Counter({r:3*n for r,n in reflected_counts.items()})
    for rank,count in selected.items():full_reflected[3*rank]+=count
    full_reflected[2]+=2*v
    need(full_reflected==children, 'complete reflected shared-core histogram')
    unique_edges={(before.B,after.B):(before,after) for before,after in edges
                  if id(before) in new_ids or id(after) in new_ids}
    for before,after in unique_edges.values():
        U,V=projector(before),projector(after);du,dv=before.den,after.den
        need(all(sum(V[i][k]*U[k][j] for k in range(h))==dv*U[i][j]
                 for i in range(h) for j in range(h)), 'cleared local-ring nested split projectors')
        # G-selfadjointness gives P_U P_V=P_U as well. The displayed
        # integer equality proves (I-P_U)(I-P_V)=I-P_V with no new units.
        need(all(sum(U[i][k]*V[k][j] for k in range(h))==dv*U[i][j]
                 for i in range(h) for j in range(h)), 'cleared complementary reverse projector nesting')
    reflection_record=dict(literal_physical_events=len(physical),forward_incidence=forward_stats,
        reflected_incidence=reflected_stats, complete_complemented_bank_reversal=True,
        copied_center_transition='D_0 D_U^-1 = F^-1 F T_U^-1 = T_U^-1; D_U=T_U F^-1',
        forward_positive_width_histogram=dict(sorted(forward_counts.items())),
        reflected_positive_width_histogram=dict(sorted(reflected_counts.items())),
        reflected_complete_child_histogram=dict(sorted(full_reflected.items())),
        explicit_cleared_projector_edge_pairs=len(unique_edges),
        rule='Every literal gate, compensated read, source mix/delivery/unmix, center copy and cleanup is reversed. '
             'Actual stream frames are complemented and data banks renamed. I-P uses the original unit denominator; '
             'reflected basis scaling is not a new prime test. Copy/read/discard implementation is the inherited paid interface.')
    prime_record = dict(ambient_cleared_gram_determinant=9**(h-1)*(9-h), prime_lower_bound=2**80,
        unchanged_frame_count=len(frames), new_unique_frames=len(witnesses), new_operation_frames=len(plan['frames']),
        maximum_new_determinant_bits=max((abs(obj.den).bit_length() for obj in new.values()), default=0),
        maximum_retained_chosen_determinant_bits=max(abs(obj.den).bit_length() for obj in frames.values()),
        exact_AB_and_rank_certificates=True, explicit_new_projectors=len(witnesses),
        cleared_nested_projector_edges=projectors_checked, frame_witnesses=witnesses,
        inherited_prime_exclusion_sources=['research/paired-cube-bit/LEMMA.md',
            'notes/stopped-product-factorization.tex:78', 'notes/stopped-product-note.tex:30'],
        original_frame_witnesses=[dict(frame_id=identity, dimension=obj.dim, presentation=obj.presentation,
            gram_determinant=obj.den, defining_rows_sha256=sha256(json.dumps(obj.B if obj.presentation=='primal_basis' else obj.A,separators=(',',':')).encode()).hexdigest()) for identity,obj in sorted(frames.items())],
        rule='For every retained permitted q>2^80, all new determinants, 9 and 9-h are units. '
             'Dual frames are ker(A), not a possibly nonsaturated B lattice. Cleared projector identities '
             'extend to every Z/q^w. Retain all original exclusions; no threshold, fallback or precision change.')
    return actual_profile, prime_record, events, dict(g=g, w=w, frames=frames, opframes=opframes,
        new=new, nf=nf, root_frames=root_frames, cov=cov, edges=edges, roles=roles, v=v, physical=physical, reflected=reflected,
        initial=initial,final=final,reflection_record=reflection_record)


def main():
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'export', 'plan', 'profile', 'pin', 'output'): ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args(); need(not args.output.exists(), 'fresh output directory required')
    started = time.monotonic(); started_utc = datetime.now(timezone.utc).isoformat()
    pin = json.loads(args.pin.read_text())
    for name, digest in pin['source_sha256'].items():
        p = Path(name); need(not p.is_absolute() and '..' not in p.parts, 'unsafe source pin')
        need(sha256((args.source/p).read_bytes()).hexdigest() == digest, 'immutable source corruption: '+name)
    for name,digest in pin['export_sha256'].items():
        need(sha256((args.export/name).read_bytes()).hexdigest()==digest,'regenerated export corruption: '+name)
    need(sha256(args.plan.read_bytes()).hexdigest() == pin['plan_sha256'], 'candidate plan corruption')
    plan, expected = json.loads(args.plan.read_text()), json.loads(args.profile.read_text())
    profile, prime_record, events, context = reconstruct(args.source, args.export, plan, expected)
    import independent_binary_native_inputs as native_inputs
    context['supplied_profile']=expected
    inputs_review=native_inputs.verify_inputs(args.source,context,pin.get('compiler_config',{}))
    replay = [formal(events, profile['v'], profile['R']), formal(events, profile['v'], profile['R'], reflected=True)]
    controls = {}
    def reject(name, function):
        try: function()
        except (ValueError, KeyError, IndexError, TypeError) as error: controls[name] = str(error)
        else: raise ValueError('negative control accepted: '+name)
    reject('omitted_cleanup', lambda: formal(events[:-1], profile['v'], profile['R']))
    broken = list(events); broken.append(('xor', -1, 0))
    reject('illegal_negative_index', lambda: formal(broken, profile['v'], profile['R']))
    broken = list(events); j = next(i for i, event in enumerate(broken) if event[0] == 'broadcast' and event[1] < profile['v'])
    del broken[j]
    reject('omitted_partner_delivery', lambda: formal(broken, profile['v'], profile['R']))
    broken = list(events); j = next(i for i, event in enumerate(broken) if event[0] == 'broadcast')
    del broken[j]
    reject('omitted_dirty_compensation', lambda: formal(broken, profile['v'], profile['R']))
    v=profile['v'];swap=lambda r:(r+v)%(2*v) if r<2*v else r
    reflected_initial={swap(r):complement(f) for r,f in context['final'].items()}
    reflected_final={swap(r):complement(f) for r,f in context['initial'].items()}
    bad_reflected=list(context['reflected'])
    j=next(i for i,e in enumerate(bad_reflected) if e[0] in ('xor','broadcast') and e[2].dim!=e[2].original.dim)
    event=bad_reflected[j];bad_reflected[j]=(event[0],event[1],event[2].original)
    reject('bad_complement',lambda:replay_geometry(bad_reflected,reflected_initial,reflected_final))
    H = Counter(profile['child_histogram']); a,b,c = next((a,b,c) for a in H for b in H for c in H if a<b<c and a+c==2*b and H[b]>=2)
    false = H.copy(); false[a]+=1; false[b]-=2; false[c]+=1
    need(sum(false.values()) == sum(H.values()) and sum(r*n for r,n in false.items()) == profile['rank_per_vertex'], 'mass control setup')
    reject('mass_preserving_histogram', lambda: need(false == H, 'literal paid incidence histogram differs'))
    unpaid=list(events)+[('xor',0,1),('xor',0,1)]
    # This altered program still has the correct exact scalar action. The
    # independently emitted paid chronology must reject its extra work.
    formal(unpaid,profile['v'],profile['R'])
    reject('unpaid_cancelling_operations',lambda:paid_program_binding(unpaid,events))
    reject('illegal_operation_frame_index',lambda:ix(-1,len(context['w']['ops']),'operation frame index'))
    pair=json.loads((args.source/'research/paired-cube-bit/data/pair_module_p12.json').read_text())
    bad_pair=deepcopy(pair);bad_pair['roots'][0]=0
    reject('wrong_pair_module_root',lambda:native_inputs.verify_pair_module(bad_pair,12))
    bad_word=deepcopy(context['w']);bad_word['arcs'][0][1]=['op',-1,0]
    reject('illegal_frozen_matching_arc',lambda:native_inputs.verify_compiler(context['g'],bad_word,
        context['nf'],context['root_frames'],pin.get('compiler_config',{}).get('plain_threshold',8)))
    reject('G_degenerate_address_frame',lambda:Frame(24,B=[[int(i<9) for i in range(24)]]))
    reject('source_corruption', lambda: need(sha256((args.source/'research/paired-cube-bit/out/word_p12.json').read_bytes()+b' ').hexdigest() ==
        pin['source_sha256']['research/paired-cube-bit/out/word_p12.json'], 'changed literal source bytes'))
    args.output.mkdir(parents=True)
    paid_program_binding(events,list(events))
    result = dict(status='PASS_INDEPENDENT_BINARY_FINITE', profile=profile, formal=replay,
        reflection=context['reflection_record'],
        independent_producer=inputs_review, regenerated_export_sha256=pin['export_sha256'],
        prime_summary={key:value for key,value in prime_record.items() if key not in ('frame_witnesses','original_frame_witnesses')},
        negative_controls=controls, source_revision=pin['source_revision'], source_sha256=pin['source_sha256'],
        plan_sha256=pin['plan_sha256'], supplied_profile_sha256=sha256(args.profile.read_bytes()).hexdigest(),
        pin_manifest_sha256=sha256(args.pin.read_bytes()).hexdigest(),
        literal_scalar_program_sha256=sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest(),
        checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        producer_reconstruction_code_sha256=sha256(Path(native_inputs.__file__).read_bytes()).hexdigest(),
        exact_algebra_sha256=sha256((Path(__file__).parent/'binary_exact_algebra.py').read_bytes()).hexdigest(),
        started_utc=started_utc, finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-started,
        scope='Independent complete literal F2 replay in both orientations, arbitrary dirty/source restoration, '
              'rational carrier/actual target/K chronology, exact G-Gram rank and prime-unit projector certificates, '
              'complete paid child histogram. All-size weighted Clifford/recurrence/ordinary wrapper and paid balanced '
              'layout remain explicitly inherited conditional contracts.')
    for name, value in [('receipt.json',result),('profile.json',profile),('prime-projectors.json',prime_record)]:
        with (args.output/name).open('x') as stream: json.dump(value,stream,indent=2);stream.write('\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ('profile','source_sha256')},indent=2))


if __name__ == '__main__': main()
