#!/usr/bin/env python3
"""Independent exact reflected geometry for the frozen paired-cube complex word.

Authored by RaD with OpenAI Codex assistance. No imports from the producer.
The executable checks finite binary geometry and literal signed inverse algebra.
The exact operator proof and retained all-size boundaries are recorded separately.
Python 3.11+; standard library only; assertion-disabled execution is rejected.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import gzip
import heapq
from itertools import combinations
import json
from pathlib import Path
import resource
import sys
import time


def need(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    pivots = {}
    for original in vectors:
        value = original
        for pivot in sorted(pivots, reverse=True):
            if value & (1 << pivot):
                value ^= pivots[pivot]
        if value:
            pivot = value.bit_length() - 1
            for key in tuple(pivots):
                if pivots[key] & (1 << pivot):
                    pivots[key] ^= value
            pivots[pivot] = value
    return tuple(pivots[key] for key in sorted(pivots, reverse=True))


@lru_cache(None)
def annihilator(space, dimension):
    rows = span(space)
    pivots = {row.bit_length() - 1: row for row in rows}
    result = []
    for free in range(dimension):
        if free in pivots:
            continue
        vector = 1 << free
        for pivot, row in pivots.items():
            if row & (1 << free):
                vector |= 1 << pivot
        result.append(vector)
    return span(result)


@lru_cache(None)
def subset(smaller, larger):
    for vector in smaller:
        for row in larger:
            vector = min(vector, vector ^ row)
        if vector:
            return False
    return True


def members(bits):
    while bits:
        bit = bits & -bits
        yield bit.bit_length() - 1
        bits ^= bit


@lru_cache(None)
def lagrangian(space, dimension):
    return span(tuple(u | (u << dimension) for u in space)
                + tuple(v << dimension for v in annihilator(space, dimension)))


@lru_cache(None)
def distance(left, right, dimension):
    # Both Lagrangians have dimension h, so h - dim(intersection)
    # equals rank of the union minus h. No Gram nondegeneracy assumption.
    return len(span(lagrangian(left, dimension) + lagrangian(right, dimension))) - dimension


def apply(columns, vector):
    value = 0
    for index in members(vector):
        value ^= columns[index]
    return value


def transpose(columns):
    return tuple(sum(((columns[j] >> i) & 1) << j for j in range(len(columns)))
                 for i in range(len(columns)))


def inverse_matrix(columns):
    n = len(columns)
    rows = [transpose(columns)[i] | (1 << (n + i)) for i in range(n)]
    for i in range(n):
        pivot = next((j for j in range(i, n) if rows[j] >> i & 1), None)
        need(pivot is not None, 'singular completion matrix')
        rows[i], rows[pivot] = rows[pivot], rows[i]
        for j in range(n):
            if j != i and rows[j] >> i & 1:
                rows[j] ^= rows[i]
    need([r & ((1 << n)-1) for r in rows] == [1 << i for i in range(n)], 'inverse reduction')
    return transpose(tuple(row >> n for row in rows))


def representative(space, h):
    """Binary action of a specified exact Clifford circuit T_U.

    Generic lift: K_G C_[0:r] K_G^-1, where K_G is a linear address
    permutation followed by a diagonal quadratic phase. For norm-one
    lines use the inherited C along translation X_q, with T_q^2=X_q.
    """
    mask = (1 << h)-1
    if len(space) == 1 and space[0].bit_count() % 2:
        q = space[0]
        return tuple(1 << i for i in range(h)) + tuple((1 << (h+i)) ^ (q if q >> i & 1 else 0)
                                                        for i in range(h))
    if not space:
        return tuple(1 << i for i in range(2*h))
    if len(space) == h:
        return tuple(1 << i for i in range(h)) + tuple((1 << i) | (1 << (h+i)) for i in range(h))
    columns = list(space)
    accumulated = space
    for i in range(h):
        if not subset((1 << i,), accumulated):
            columns.append(1 << i)
            accumulated = span(accumulated + (1 << i,))
    need(len(columns) == h, 'incomplete canonical extension')
    G = tuple(columns)
    Gi = inverse_matrix(G)
    Git, Gt = transpose(Gi), transpose(G)
    K = tuple(G[i] | ((G[i] ^ Git[i]) << h) for i in range(h)) + tuple(v << h for v in Git)
    Ki = tuple(Gi[i] | ((Gi[i] ^ Gt[i]) << h) for i in range(h)) + tuple(v << h for v in Gt)
    rmask = (1 << len(space))-1
    def coordinate_C(vector):
        x, z = vector & mask, vector >> h
        return (x ^ (z & rmask)) | (z << h)
    return tuple(apply(K, coordinate_C(apply(Ki, 1 << i))) for i in range(2*h))


def verify_representatives(spaces, h):
    mask = (1 << h)-1
    L0 = span(1 << (h+i) for i in range(h))
    nondegenerate = 0
    for U in spaces:
        L = lagrangian(U, h)
        need(len(L) == h, 'L_U dimension')
        need(all((((a & mask) & (b >> h)).bit_count()
                  + ((b & mask) & (a >> h)).bit_count()) % 2 == 0 for a in L for b in L), 'L_U isotropy')
        FU = span(((row & mask) ^ (row >> h)) | ((row >> h) << h) for row in L)
        need(FU == lagrangian(annihilator(U, h), h), 'F L_U != L_(U perp)')
        T = representative(U, h)
        need(span(apply(T, row) for row in L0) == L, 'T_U preimage frame')
        need(all(apply(T, apply(T, 1 << i)) == 1 << i for i in range(2*h)), 'T_U binary square')
        need(len(span((col & mask) for col in T[h:])) == len(U), 'T_U Fourier rank')
        need(span(((apply(T, row) & mask) ^ (apply(T, row) >> h))
                  | ((apply(T, row) >> h) << h) for row in L0) == FU, 'D_U preimage frame')
        if len(U):
            gram = tuple(sum(((u & v).bit_count() % 2) << j for j, v in enumerate(U)) for u in U)
            nondegenerate += len(span(gram)) == len(U)
    return dict(distinct_frames=len(spaces), degenerate_nonzero_frames=sum(bool(U) for U in spaces)-nondegenerate,
                exact_binary_representatives_checked=len(spaces), phase_scope='Exact circuits are defined by K_G and C; binary checks are not substituted for exact phase equality.')


def verify_endpoint_adapters(inputs,h):
    mask=(1 << h)-1
    checked=0
    for q in inputs:
        U=annihilator((q,),h)
        T=representative(U,h)
        Tq=representative((q,),h)
        def F(x):return ((x & mask) ^ (x >> h)) | ((x >> h) << h)
        S=tuple(F(col) for col in Tq)  # Exact desired endpoint is F T_q^-1.
        ratio=tuple(apply(S,apply(T,1 << i)) for i in range(2*h))
        need(all((col & mask) == 0 for col in ratio[h:]), 'endpoint adapter positive Fourier rank')
        need(all(F(apply(Tq,1 << i)) == apply(Tq,F(1 << i)) for i in range(2*h)), 'norm-one source phase commutation')
        checked+=1
    return dict(target_endpoint_adapters_checked=checked,rank=0,
                exact_word='(F T_q^-1) T_(q perp)^-1; the inverse appears literally after complement/bank reversal.')


def unit_phase_check():
    # Exact Gaussian rationals represented by Python complex pairs of Fractions.
    def add(a, b): return (a[0]+b[0], a[1]+b[1])
    def mul(a, b): return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
    def mm(A, B):
        return tuple(tuple(add(mul(A[i][0], B[0][j]), mul(A[i][1], B[1][j])) for j in range(2)) for i in range(2))
    z, one = (Fraction(0), Fraction(0)), (Fraction(1), Fraction(0))
    alpha, beta = (Fraction(1,2), Fraction(1,2)), (Fraction(1,2), Fraction(-1,2))
    C = ((alpha,beta),(beta,alpha))
    Ci = tuple(tuple((x,-y) for x,y in row) for row in C)
    need(mm(C, Ci) == ((one,z),(z,one)), 'exact C inverse')
    need(mm(C,C) == ((z,one),(one,z)), 'exact C square is not X')
    return 'C^2=X exactly over Q(i); F^2 is a tensor Pauli, not an exact identity.'


@lru_cache(None)
def bank_swap(register):
    bank, index = register
    return ('y' if bank == 'x' else 'x' if bank == 'y' else bank, index)


def invert_event(event, h):
    event = dict(event)
    kind = event['kind']
    if kind == 'frame':
        event['from'], event['to'] = annihilator(event['to'], h), annihilator(event['from'], h)
        event['reg'] = bank_swap(event['reg'])
    elif kind == 'gate':
        event['regs'] = tuple(bank_swap(r) for r in event['regs'])
        event['ca'], event['cb'] = event['ca'], -event['ca']*event['cb']
        event['frame'] = annihilator(event['frame'], h)
    elif kind in ('read', 'inject'):
        event['regs'] = tuple(bank_swap(r) for r in event['regs'])
        event['sign'] = -event['sign']
        event['frame'] = annihilator(event['frame'], h)
    elif kind == 'copy_read':
        event['regs'] = tuple(bank_swap(r) for r in event['regs'])
        event['sign'] = -event['sign']
        event['source_frame'] = annihilator(event['source_frame'], h)
        event['read_frame'] = annihilator(event['read_frame'], h)
    elif kind == 'matrix':
        event['regs'] = tuple(bank_swap(r) for r in event['regs'])
        event['matrix'] = tuple(zip(*event['matrix']))
        event['frame'] = annihilator(event['frame'], h)
    elif kind == 'endpoint_adapter':
        event['regs'] = tuple(bank_swap(r) for r in event['regs'])
        event['frame'] = annihilator(event['frame'], h)
        event['direction'] = -event['direction']
    else:
        raise ValueError('unknown inverse event')
    return event


def verify_inverse_pairs(forward, reflected, h):
    """Check each signed inverse by its exact scalar matrix, independently of emission."""
    need(len(forward) == len(reflected), 'full inverse event count')
    for original, actual in zip(forward, reversed(reflected)):
        kind = original['kind']
        need(actual['kind'] == kind, 'inverse event kind')
        if kind == 'frame':
            need(actual['reg'] == bank_swap(original['reg'])
                 and actual['from'] == annihilator(original['to'],h)
                 and actual['to'] == annihilator(original['from'],h)
                 and actual['width'] == original['width'], 'inverse complemented frame')
            continue
        need(actual['regs'] == tuple(bank_swap(r) for r in original['regs']), 'inverse bank renaming')
        if kind == 'copy_read':
            need(actual['source_frame'] == annihilator(original['source_frame'],h)
                 and actual['read_frame'] == annihilator(original['read_frame'],h), 'inverse center copy complement')
        else:
            need(actual['frame'] == annihilator(original['frame'],h), 'inverse scalar frame complement')
        if kind == 'gate':
            # [[ca_r,cb_r],[0,1]] [[ca_f,cb_f],[0,1]] is the identity.
            need(actual['ca']*original['ca'] == 1
                 and actual['ca']*original['cb']+actual['cb'] == 0, 'signed inverse matrix product')
        elif kind in ('read','inject','copy_read'):
            need(actual['sign']+original['sign'] == 0, 'inverse shear sign')
            for key in ('decoder','source','center'):
                if key in original:
                    need(actual[key] == original[key], 'inverse scalar coefficient binding')
        elif kind == 'matrix':
            M,N = original['matrix'],actual['matrix']
            need(all(sum(N[i][k]*M[k][j] for k in range(4)) == 4*(i == j)
                     for i in range(4) for j in range(4)), 'exact K inverse product')
        elif kind == 'endpoint_adapter':
            need(actual['direction'] == -original['direction'] and actual['q'] == original['q'], 'exact endpoint adapter inverse')


def verify_cleanup(events, operation_count, injection_count):
    producer = [e for e in events if e['kind'] in ('gate','inject') and not e.get('cleanup')]
    inverse = [e for e in events if e.get('cleanup')]
    need(sum(e['kind'] == 'gate' for e in producer) == operation_count
         and sum(e['kind'] == 'inject' for e in producer) == injection_count, 'unpaid operation incidence')
    need(len(producer) == len(inverse), 'literal cleanup incidence missing')
    for original, actual in zip(producer,reversed(inverse)):
        need(original['kind'] == actual['kind'] and original['regs'] == actual['regs'], 'cleanup chronology')
        if original['kind'] == 'gate':
            need(original['operation'] == actual['operation'] and original['ca']*actual['ca'] == 1
                 and actual['ca']*original['cb']+actual['cb'] == 0, 'cleanup signed inverse')
        else:
            need(original['source'] == actual['source'] and original['sign']+actual['sign'] == 0, 'cleanup source subtraction')


def replay(events, start, final, h, v, live, *, reflected=False):
    current = dict(start)
    paid = defaultdict(Counter)
    scalar = Counter()
    incidences = Counter()
    for index, event in enumerate(events):
        kind = event['kind']
        regs = (event['reg'],) if kind == 'frame' else event['regs']
        for reg in regs:
            need(reg in current, 'illegal literal register at event %d' % index)
            bank, port = reg
            need(type(port) is int and port >= 0 and (port < v if bank in ('x','y') else port in live), 'illegal literal index')
        if kind == 'frame':
            a, b = event['from'], event['to']
            need(current[event['reg']] == a, 'frame chronology at event %d' % index)
            need(subset(a,b), 'non-nested frame transition')
            width = distance(a,b,h)
            need(width == len(b)-len(a) == event['width'], 'paid transition rank')
            paid[event['part']][width] += 1
            current[event['reg']] = b
        elif kind == 'copy_read':
            src, U, V = regs[0], event['source_frame'], event['read_frame']
            need(current[src] == U, 'center source frame')
            need(all(current[r] == V for r in regs[1:]), 'center scatter target frame')
            width = distance(U,V,h)
            need(width == event['width'], 'center copy rank')
            paid['local'][width] += 1
            scalar[kind] += 1
            incidences['center_scatter_targets'] += len(regs)-1
        else:
            F = event['frame']
            need(all(current[r] == F for r in regs), 'noncommon scalar frame at event %d' % index)
            if kind == 'gate':
                need(regs[0] != regs[1] and event['ca'] in (-1,1) and event['cb'] in (-1,1), 'illegal signed gate')
                incidences['signed_gate_ports'] += 2
            elif kind == 'matrix':
                M = event['matrix']
                need(all(sum(M[i][k]*M[j][k] for k in range(4)) == 4*(i == j)
                         for i in range(4) for j in range(4)), 'K block inverse')
                incidences['K_block_ports'] += len(regs)
            elif kind == 'read':
                need(event['sign'] in (-1,1), 'read sign')
                incidences['conservative_target_read_incidences'] += len(regs)-1
            elif kind == 'inject':
                need(event['sign'] in (-1,1), 'injection sign')
                incidences['source_injections'] += 1
            elif kind == 'endpoint_adapter':
                # Exact word: (F T_q^-1) T_(q perp)^-1. Its two preimages
                # coincide; its inverse is emitted in the reflected word.
                need(F == annihilator((event['q'],),h) or reflected, 'endpoint adapter label')
                need(event['direction'] in (-1,1), 'endpoint adapter direction')
                paid['endpoint_adapter'][0] += 1
            else:
                raise ValueError('unknown literal event')
            scalar[kind] += 1
    need(current == final, 'incomplete cleanup/frame endpoint')
    return dict(paid={k:dict(sorted(v.items())) for k,v in paid.items()}, scalar=dict(scalar), incidences=dict(incidences),
                event_count=len(events), orientation='complemented bank-swapped signed inverse' if reflected else 'forward')


def regenerate_closure_and_word(graph, witness, word, R):
    """Rebuild generalized dependency closure and literal carrier allocation.

    The frozen signed DAG is an input. Its module/fusion provenance and full
    scalar decoder are checked separately; no discovery/search is rerun here.
    """
    h, v = graph['h'], graph['v']
    raw = graph['args']
    args = [None] + [None if a is None else tuple(x + 1 for x in a) for a in raw]
    roots = [dict(r, node=r['node'] + 1) for r in graph['roots']]
    n = len(args)
    need(len(graph['signs']) == len(raw), 'DAG sign count')
    spans = [()] * n
    for node, a in enumerate(args[1:], 1):
        if a is None:
            need(node <= v, 'unexpected null DAG node')
            spans[node] = (graph['inputs'][node-1],)
        else:
            need(len(a) == 2 and all(type(x) is int and 0 < x < node for x in a), 'DAG operand indices')
            spans[node] = span(spans[a[0]] + spans[a[1]])
    active = set(range(1, v+1))
    todo = [r['node'] for r in roots]
    while todo:
        x = todo.pop()
        need(type(x) is int and 0 < x < n, 'root/ancestor DAG index')
        if x in active:
            continue
        active.add(x)
        if args[x]:
            todo.extend(args[x])
    order = witness['order']
    need(len(order) == len(active) and set(order) == active, 'active-node linear extension coverage')
    succ = [[] for _ in args]
    direct = [[] for _ in args]
    indegree = [0] * n
    for x in active:
        if args[x]:
            for y in args[x]:
                succ[y].append(x)
                indegree[x] += 1
    rootcaps = []
    for root in roots:
        x = root['node']
        cap = annihilator(spans[x], h) if root['kind'] == 'center' else span(graph['inputs'][t] for t in root['targets'])
        need(subset(spans[x], annihilator(cap, h)), 'root incidence for backward closure')
        rootcaps.append(cap)
        direct[x].extend(cap)
    arcs = {}
    uses_taken = set()
    for x, code in witness['matching_arcs']:
        need(type(x) is int and x in active and args[x] and x not in arcs, 'carrier donor node')
        need(type(code) is int and 0 <= code < 1 << 32 and code not in uses_taken, 'carrier use code')
        if code >> 31:
            j = code & ((1 << 31)-1)
            need(j < len(roots), 'carrier root use index')
            value = roots[j]['node']
            direct[x].extend(rootcaps[j])
        else:
            receiver = code // 2
            need(receiver in active and args[receiver] and receiver != x, 'carrier receiver node')
            value = args[receiver][code & 1]
            succ[x].append(receiver)
            indegree[receiver] += 1
        need(value in args[x], 'carrier donor operand compatibility')
        arcs[x] = code
        uses_taken.add(code)
    ready = [x for x in active if indegree[x] == 0]
    heapq.heapify(ready)
    topo = []
    while ready:
        x = heapq.heappop(ready)
        topo.append(x)
        for y in succ[x]:
            indegree[y] -= 1
            if not indegree[y]:
                heapq.heappush(ready, y)
    need(len(topo) == len(active), 'cyclic extended closure')
    pos = {x:i for i,x in enumerate(order)}
    need(all(pos[x] < pos[y] for x in active for y in succ[x]), 'extended-closure word order')
    anns = [None] * n
    for x in reversed(topo):
        anns[x] = span(direct[x] + [u for y in succ[x] for u in anns[y]])
        need(subset(spans[x], annihilator(anns[x], h)), 'extended closure excludes value span')
        need(list(anns[x]) == witness['annihilators'][x], 'full backward annihilator mismatch')
    need(len(witness['annihilators']) == n and witness['annihilators'][0] is None, 'annihilator index coverage')
    uses = [[] for _ in args]
    for x in order:
        if args[x]:
            for j,y in enumerate(args[x]):
                uses[y].append(2*x+j)
    for j,r in enumerate(roots):
        uses[r['node']].append((1 << 31) | j)
    assign, sources, ops, coeffs = {}, {}, [], []
    count = 0
    for x in order:
        if args[x]:
            aa, bb = args[x]
            dest, control = assign[2*x], assign[2*x+1]
            swapped = False
            if x in arcs:
                code = arcs[x]
                value = roots[code & ((1 << 31)-1)]['node'] if code >> 31 else args[code//2][code & 1]
                if value == aa:
                    dest, control = control, dest
                    swapped = True
                else:
                    need(value == bb, 'carrier operand allocation')
                need(code not in assign, 'carrier use already assigned')
                assign[code] = control
            sign = graph['signs'][x-1]
            need(sign in (-1,1), 'regenerated DAG sign')
            ops.append([dest, control, x])
            coeffs.append([sign,1] if swapped else [1,sign])
        else:
            dest = count
            count += 1
            sources[str(x)] = dest
        free = [u for u in uses[x] if u not in uses_taken]
        need(bool(free), 'carrier has no unassigned outgoing use')
        for j,u in enumerate(free):
            need(u not in assign, 'duplicate unpaired use allocation')
            if not j:
                assign[u] = dest
            else:
                target = count
                count += 1
                assign[u] = target
                ops.append([target,dest,x])
                coeffs.append([1,1])
    rootroles = [assign[(1 << 31) | j] for j in range(len(roots))]
    need((ops, coeffs, sources, rootroles, count) == (word['ops'], word['opcoeff'], word['sources'], word['rootroles'], R), 'literal carrier word regeneration mismatch')
    previous, pred = [-1]*R, []
    for i,(a,b,x) in enumerate(ops):
        pred.append((previous[a], previous[b]))
        previous[a] = previous[b] = i
    stack = [previous[role] for root,role in zip(roots,rootroles) if root['kind'] == 'center']
    phase = set()
    while stack:
        i = stack.pop()
        if i < 0 or i in phase:
            continue
        phase.add(i)
        stack.extend(pred[i])
    need(sorted(phase) == sorted(word['phase1']), 'center dependency phase regeneration mismatch')
    untouched = set(range(R)) - set(sources.values())
    for i in phase:
        untouched.difference_update(ops[i][:2])
    need(all(z['role'] in untouched for z in word['selected']), 'gauge not initially untouched')
    binding = dict(ops=ops, opcoeff=coeffs, sources=sources, rootroles=rootroles, phase1=sorted(phase))
    return dict(active_nodes=len(active), generalized_edges=sum(map(len,succ)), matching_arcs=len(arcs),
                annihilators_regenerated=len(active), carrier_operations_regenerated=len(ops),
                center_phase_regenerated=len(phase), allocated_roles=count,
                canonical_word_sha256=sha256(json.dumps(binding,sort_keys=True,separators=(',',':')).encode()).hexdigest())


def build(graph, witness, word, pairs, changed, R):
    h,v = graph['h'],graph['v']
    full = span(1 << i for i in range(h))
    inputs = graph['inputs']
    need(v == len(inputs) and h == 22 and v == 1320 and R == 14843, 'selected fused PR168 dimensions')
    args = graph['args']
    spans = []
    for node, operands in enumerate(args):
        if operands is None:
            need(node < v, 'noninput null node')
            spans.append((inputs[node],))
        else:
            need(all(type(x) is int and 0 <= x < node for x in operands), 'DAG indices')
            spans.append(span(spans[operands[0]]+spans[operands[1]]))
    ops = word['ops']
    coefficients = word['opcoeff']
    need(len(ops) == len(coefficients), 'coefficient count')
    frames = [annihilator(tuple(witness['annihilators'][node]), h) for a,b,node in ops]
    seen = set()
    for index,U in changed:
        need(type(index) is int and 0 <= index < len(ops) and index not in seen, 'changed frame index')
        need(U and all(type(u) is int and 0 < u < 1 << h for u in U), 'frame mask')
        U = tuple(U)
        need(span(U) == U and U != frames[index], 'noncanonical or unchanged frame')
        seen.add(index)
        frames[index] = U
    for (_,_,node),U in zip(ops,frames):
        need(1 <= node <= len(spans) and subset(spans[node-1],U), 'operation value incidence')
    roles = defaultdict(list)
    for index,(a,b,node) in enumerate(ops):
        need(all(type(r) is int and 0 <= r < R for r in (a,b)) and a != b, 'operation role index')
        roles[a].append(index); roles[b].append(index)
    selected = {z['role']:z for z in word['selected']}
    need(len(selected) == len(word['selected']), 'duplicate selection')
    merge,donors,deadlines = {},{},{}
    phase = sorted(word['phase1']); pset = set(phase)
    need(len(phase) == len(pset) and all(type(i) is int and 0 <= i < len(ops) for i in phase), 'phase index')
    order = phase+[i for i in range(len(ops)) if i not in pset]
    position = {i:k for k,i in enumerate(order)}
    for a,b,t in pairs:
        need(all(type(r) is int and 0 <= r < R for r in (a,b)) and a != b, 'pair index')
        need(a not in donors and b not in merge, 'duplicate pair')
        donors[a]=b; merge[b]=a; deadlines[b]=t
    need(not set(donors)&set(merge) and set(merge) == set(selected), 'paired physical zero gauges')
    need(all(z['rank'] == 18 for z in selected.values()), 'selected gauge rank')
    roots = graph['roots']; rootroles=word['rootroles']
    need(len(roots) == len(rootroles) and len(set(rootroles)) == len(rootroles), 'root roles')
    need(not set(donors)&set(rootroles), 'root donor')
    for a,b in donors.items():
        last, first = roles[a][-1], roles[b][0]
        t = deadlines[b]
        if t is None:
            need(last in pset and first not in pset and position[last] < len(phase) <= position[first], 'phase-cut pair chronology')
        else:
            need(t == first and t not in pset and position[last] < position[t], 'late pair chronology')
        U = annihilator(tuple(selected[b]['annihilator']),h)
        need(len(U) == 18 and subset(frames[last],U), 'donor gauge incidence')
    alias=lambda role:merge.get(role,role)
    live=set(range(R))-set(merge)
    need(len(live) == 12203, 'physical fused PR168 roles')
    co=[0]*R
    for root,role in zip(roots,rootroles):
        need(type(role) is int and 0 <= role < R, 'root index')
        targets=root['targets']
        need(len(targets) == len(set(targets)) and all(type(t) is int and 0 <= t < v for t in targets), 'root target index')
        co[role] |= sum(1 << t for t in targets)
    for a,b,node in reversed(ops): co[b] |= co[a]
    for role,z in selected.items():
        need(z['targets'] == list(members(co[role])), 'selected read target incidence')
    initial={('a',s):() for s in live}
    initial.update({('x',t):(q,) for t,q in enumerate(inputs)})
    initial.update({('y',t):() for t in range(v)})
    current=dict(initial)
    events=[]
    cleanup=[]
    spaces=set(initial.values())|{full}
    def move(reg,U,part):
        U=tuple(U);old=current[reg]
        need(subset(old,U), 'literal forward frame retreat '+str(reg))
        events.append(dict(kind='frame',reg=reg,part=part,**{'from':old,'to':U,'width':len(U)-len(old)}))
        current[reg]=U; spaces.add(U)
    def read(role,targets,U,sign,decoder):
        reg=('a',alias(role))
        move(reg,U,'local')
        for target in targets: move(('y',target),U,'target')
        regs=(reg,)+tuple(('y',t) for t in targets)
        events.append(dict(kind='read',regs=regs,frame=U,sign=sign,decoder=decoder))
    def gate(i):
        a,b,node=ops[i];ca,cb=coefficients[i]
        need(ca in (-1,1) and cb in (-1,1), 'signed coefficient')
        U=frames[i];regs=(('a',alias(a)),('a',alias(b)))
        need(regs[0] != regs[1], 'aliased gate ports')
        for reg in regs:move(reg,U,'local')
        event=dict(kind='gate',regs=regs,frame=U,ca=ca,cb=cb,operation=i,cleanup=False)
        events.append(event);cleanup.append(event)
    # Expanded old-value corrections occur at the common zero frame.
    for role in range(R):
        if role not in selected and role not in merge:
            targets=list(members(co[role]))
            events.append(dict(kind='read',regs=(('a',role),)+tuple(('y',t) for t in targets),frame=(),sign=-1,decoder=('adjoint',role)))
    sources={int(n):r for n,r in word['sources'].items()}
    need(set(sources) == set(range(1,v+1)), 'source set')
    for node,role in sources.items():
        q=inputs[node-1];reg=('a',alias(role))
        move(reg,(q,),'local')
        event=dict(kind='inject',regs=(reg,('x',node-1)),frame=(q,),sign=1,source=node-1,cleanup=False)
        events.append(event);cleanup.append(event)
    # Literal original-source K implementation, after all carrier injections.
    blocks=[];assignment={}
    for start in range(0,v,8):
        for parity in (0,1):
            source=[start+i for i in range(8) if i.bit_count()%2 == parity]
            target=[start+i for i in range(8) if i.bit_count()%2 != parity]
            U=span(inputs[s] for s in source)
            need(len(U) == 3 and all(subset(U,annihilator((inputs[t],),h)) for t in target), 'K frame incidence')
            M=tuple(tuple(1 if (inputs[t]^inputs[s]).bit_count() == 6 else -1 if (inputs[t]^inputs[s]).bit_count() == 2 else 0 for s in source) for t in target)
            need(all(sum(M[i][k]*M[j][k] for k in range(4)) == 4*(i == j) for i in range(4) for j in range(4)), 'exact K inverse')
            regs=tuple(('x',s) for s in source)
            for reg in regs:move(reg,U,'source')
            events.append(dict(kind='matrix',regs=regs,frame=U,matrix=M,denominator=2,operation='K'))
            blocks.append((regs,M))
            assignment.update(zip(source,target))
    for i in phase:gate(i)
    for root,role in zip(roots,rootroles):
        if root['kind'] == 'center':
            U=spans[root['node']]
            need(len(U) == h-2, 'center frame rank')
            move(('a',alias(role)),U,'local')
            need(all(current[('y',t)] == () for t in range(v)), 'center scatter before target advances')
            events.append(dict(kind='copy_read',regs=(('a',alias(role)),)+tuple(('y',t) for t in range(v)),
                               source_frame=U,read_frame=(),width=len(U),sign=1,center=root['coordinate']))
    late=defaultdict(list)
    for z in reversed(word['selected']):
        role=z['role']
        if deadlines[role] is None:
            U=annihilator(tuple(z['annihilator']),h)
            need(all(subset(U,annihilator((inputs[t],),h)) for t in z['targets']), 'phase-cut read target cap')
            read(role,z['targets'],U,-1,('adjoint',role))
    for a,b,t in pairs:
        if t is not None:late[t].append(b)
    for i in order[len(phase):]:
        for role in late[i]:
            z=selected[role];U=annihilator(tuple(z['annihilator']),h)
            need(all(subset(U,annihilator((inputs[t],),h)) for t in z['targets']), 'old read target cap')
            read(role,z['targets'],U,-1,('adjoint',role))
        gate(i)
    for root,role in zip(roots,rootroles):
        if root['kind'] == 'side':
            U=annihilator(span(inputs[t] for t in root['targets']),h)
            need(subset(spans[root['node']],U), 'side source/target incidence')
            read(role,root['targets'],U,1,('root',role))
    for target,q in enumerate(inputs):move(('y',target),annihilator((q,),h),'target')
    for source,target in assignment.items():
        U=annihilator((inputs[target],),h)
        move(('x',source),U,'source')
        events.append(dict(kind='read',regs=(('x',source),('y',target)),frame=U,sign=1,decoder=('K-output',source,target)))
    for port in range(v):move(('x',port),full,'source')
    for regs,M in blocks:
        events.append(dict(kind='matrix',regs=regs,frame=full,matrix=tuple(zip(*M)),denominator=2,operation='K-inverse'))
    for role in live:move(('a',role),full,'local')
    for original in reversed(cleanup):
        if original['kind'] == 'gate':
            event=dict(original,frame=full,cb=-original['ca']*original['cb'],cleanup=True)
        else:
            event=dict(original,frame=full,sign=-original['sign'],cleanup=True)
        events.append(event)
    for target,q in enumerate(inputs):
        events.append(dict(kind='endpoint_adapter',regs=(('y',target),),frame=annihilator((q,),h),q=q,direction=1,
                           exact_word='(F T_q^-1) T_(q perp)^-1',width=0))
    final=dict(current)
    need(all(U == full for (bank,port),U in final.items() if bank in ('x','a')), 'full-frame cleanup endpoint')
    return events,initial,final,live,spaces,dict(operation_frames=len(frames), changed_from_full_intersections=len(seen),
                paid_K_blocks=len(blocks), paired_handoffs=len(pairs), all_gauges_paired=True, phase_operations=len(phase),
                phase_cut_handoffs=sum(t is None for a,b,t in pairs), late_handoffs=sum(t is not None for a,b,t in pairs),
                signed_operations=len(ops), inverse_cleanup_events=len(cleanup))


def cover_check(inputs,h):
    # One representative per actual data port; ambient group elements are not enumerated.
    m=3*h;e=3*h-2
    A=span(1 << i for i in range(h))
    B=span(1 << i for i in range(h,2*h-1))
    C=span(1 << i for i in range(2*h-1,e))
    E=span(A+B+C);ambient=span(E+(1 << e,1 << (e+1)))
    checked=0
    for q in inputs:
        need(q.bit_count()%2 == 1,'cover source norm')
        cap=annihilator((q,),h)
        d=next(i for i in range(h) if not q >> i & 1)
        w=q^(1 << d)
        orth=tuple((1 << i) ^ (w if (w >> i)&1 else 0) for i in range(h) if i != d)
        need(span(orth) == cap, 'explicit orthonormal source cap')
        need(all((u&v).bit_count()%2 == (i == j) for i,u in enumerate(orth) for j,v in enumerate(orth)), 'cover cap orthonormality')
        for block in (B,C):
            # Exchange orth with the fixed coordinate basis; fix q and the other block.
            def exchange(x):
                result=x
                for u,v in zip(orth,block):
                    delta=((x&u).bit_count() ^ (x&v).bit_count())&1
                    if delta:result^=u^v
                return result
            cols=tuple(exchange(1 << i) for i in range(m))
            need(all((u&v).bit_count()%2 == (i == j) for i,u in enumerate(cols) for j,v in enumerate(cols)), 'ambient orthogonal exchange')
            need(all(exchange(exchange(1 << i)) == 1 << i for i in range(m)), 'ambient exchange involution')
            need(span(exchange(a) for a in A) == span(block+(q,)), 'cover active image')
            if block == C:
                need(span(exchange(a) for a in B+C) == span(B+cap), 'third offset independent of port')
        # Bank-specific boundary labels from the actual forward / complemented middle / forward table.
        table=((span((q,)),span(B+(q,)),(),B),
               (span(B+(q,)),span(A+B),B,span(cap+B)),
               (span(A+B),E,span(cap+B),span(cap+B+C)))
        need(table[0][1] == table[1][0] and table[0][3] == table[1][2]
             and table[1][1] == table[2][0] and table[1][3] == table[2][2], 'interstage data continuity')
        need(len(ambient)-len(table[2][1]) == 2
             and len(annihilator((q,),m))-len(table[2][3]) == 2, 'two paid ambient complement children')
        checked+=1
    return dict(actual_ports_checked=checked, orthogonal_involutions_checked=2*checked, ambient_dimension=m,
                data_cover_dimension=e, final_data_children=dict(width=2,count=2*len(inputs)),
                full_group='Parametric O(66,2) cover and routing are retained written hypotheses; the group is not materialized.')


def encode(events):
    for event in events:
        yield (json.dumps(event,sort_keys=True,separators=(',',':'))+'\n').encode()


def digest(events):
    result=sha256()
    for row in encode(events):result.update(row)
    return result.hexdigest()


def check_module_contract(module, n, paired):
    labels=list(combinations(range(n),2)) if paired else list(range(n))
    count=len(labels)
    need(module['input_count'] == count and len(module['roots']) == count, 'module dimensions')
    supports=[]
    for x, operands in enumerate(module['args']):
        if x < count:
            need(operands is None, 'module input definition')
            supports.append(1 << x)
        else:
            need(isinstance(operands,list) and len(operands) == 2
                 and all(type(y) is int and 0 <= y < x for y in operands), 'module operand indices')
            a,b=operands
            need(not supports[a]&supports[b], 'module overlap')
            supports.append(supports[a]|supports[b])
    for index,root in enumerate(module['roots']):
        need(type(root) is int and 0 <= root < len(supports), 'module root index')
        if paired:
            i,j=labels[index]
            expected=sum(1 << k for k,(a,b) in enumerate(labels) if i not in (a,b) and j not in (a,b))
        else:
            expected=((1 << count)-1)^(1 << index)
        need(supports[root] == expected, 'module exact root support')
    return dict(input_count=count, additions=len(supports)-count, output_count=len(labels),
                disjoint_positive_additions=True, exact_root_supports_checked=len(labels))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export',type=Path,required=True)
    parser.add_argument('--tree',type=Path,required=True)
    parser.add_argument('--frames',type=Path,required=True)
    parser.add_argument('--profile',type=Path,required=True)
    parser.add_argument('--pins',type=Path,required=True)
    parser.add_argument('--construction-code',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--events',type=Path)
    args=parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    started=time.monotonic()
    paths={'graph':args.export/'graph.json','witness':args.export/'frames.json','word':args.export/'word.json',
           'pairs':args.export/'physical-pairs.json','record':args.export/'profile-before.json',
           'candidate_frames':args.frames,'candidate_profile':args.profile,
           'physical_compiler':args.tree/'scripts/paired_cube_physical.py',
           'general_clifford_proof':args.tree/'notes/general-clifford-frames.tex',
           'local_word_proof':args.tree/'notes/paired-cube-construction.tex',
           'sharing_proof':args.tree/'notes/paired-cube-sharing.tex',
           'cover_proof':args.tree/'notes/three-stage-cover-complex.tex',
           'extended_closure_compiler':args.tree/'scripts/paired_cube/closure.py',
           'module_contracts':args.tree/'scripts/paired_cube/modules.py',
           'producer':args.tree/'scripts/paired_cube_producer.py',
           'nested_prefix_module':args.tree/'references/paired-cube/sources/qmod_nested_prefix.json',
           'annealed_pair_module':args.tree/'references/paired-cube/sources/pmod_G37_w02_5.6098194e-4.json',
           'module_pin_manifest':args.tree/'references/paired-cube/sources/SOURCE.json',
           'base_selected_pin_manifest':args.tree/'references/paired-cube/selected-module/SOURCE.json',
           'base_selected_matching_arcs':args.tree/'references/paired-cube/selected-module/matching-arcs.json',
           'base_selected_mechanism':args.tree/'references/paired-cube/selected-module/README.md',
           'fusion_construction_helper':args.construction_code,
           'fused_construction_protocol':args.export/'protocol.json'}
    pins=json.loads(args.pins.read_text())
    hashes={name:sha256(path.read_bytes()).hexdigest() for name,path in paths.items()}
    need(hashes == pins['sha256'], 'input/source corruption or candidate drift')
    data={name:json.loads(paths[name].read_text()) for name in ('graph','witness','word','pairs','record','candidate_frames','candidate_profile')}
    module_contracts={'nested_prefix_all_but_one':check_module_contract(json.loads(paths['nested_prefix_module'].read_text()),9,False),
                      'annealed_pair_disjoint':check_module_contract(json.loads(paths['annealed_pair_module'].read_text()),10,True)}
    regeneration=regenerate_closure_and_word(data['graph'],data['witness'],data['word'],data['record']['R'])
    events,start,final,live,spaces,structure=build(data['graph'],data['witness'],data['word'],data['pairs'],data['candidate_frames'],data['record']['R'])
    forward=replay(events,start,final,data['graph']['h'],data['graph']['v'],live)
    h,v=data['graph']['h'],data['graph']['v']
    reflected=[invert_event(event,h) for event in reversed(events)]
    rstart={bank_swap(reg):annihilator(U,h) for reg,U in final.items()}
    rfinal={bank_swap(reg):annihilator(U,h) for reg,U in start.items()}
    reverse=replay(reflected,rstart,rfinal,h,v,live,reflected=True)
    need(forward['paid'] == reverse['paid'] and forward['scalar'] == reverse['scalar'], 'reflected paid multiset')
    verify_inverse_pairs(events,reflected,h)
    verify_cleanup(events,structure['signed_operations'],v)
    paid={name:Counter({int(r):n for r,n in hist.items() if int(r)}) for name,hist in forward['paid'].items()}
    profile=data['candidate_profile']
    for name,key in (('local','local_histogram'),('source','source_data_histogram'),('target','target_data_histogram')):
        need(paid[name] == Counter({int(r):n for r,n in profile[key].items() if int(r)}), 'complete '+name+' histogram mismatch')
    children=Counter()
    for part in paid.values(): children.update({r:3*n for r,n in part.items()})
    children[2]+=2*v
    need(children == Counter({int(r):n for r,n in profile['child_histogram'].items()}), 'complete histogram mismatch')
    W=2*v+len(live);m=3*h;mass=sum(r*n for r,n in children.items())
    need((W,m,mass,W*m-mass,max(children)) == (14843,66,978318,1320,20), 'complete fused PR168 paid dimensions')
    frame_checks=verify_representatives(spaces|{annihilator(U,h) for U in spaces},h)
    endpoint_checks=verify_endpoint_adapters(data['graph']['inputs'],h)
    cover=cover_check(data['graph']['inputs'],h)
    controls={}
    def reject(name,action):
        try: action()
        except (ValueError,KeyError,IndexError) as error: controls[name]=str(error)
        else: raise ValueError('negative control accepted: '+name)
    proper=next(i for i,e in enumerate(reflected) if e['kind'] == 'gate' and e['frame'] != annihilator(e['frame'],h))
    corrupted=list(reflected);corrupted[proper]=dict(corrupted[proper],frame=annihilator(corrupted[proper]['frame'],h))
    reject('omitted_frame_complement',lambda:replay(corrupted,rstart,rfinal,h,v,live,reflected=True))
    corrupted=list(reflected);corrupted[proper]=dict(corrupted[proper],regs=(('a',-1),corrupted[proper]['regs'][1]))
    reject('negative_literal_index',lambda:replay(corrupted,rstart,rfinal,h,v,live,reflected=True))
    corrupted=list(reflected);corrupted[proper]=dict(corrupted[proper],cb=-corrupted[proper]['cb'])
    reject('wrong_inverse_sign',lambda:verify_inverse_pairs(events,corrupted,h))
    cleanup_index=next(i for i,e in enumerate(events) if e.get('cleanup'))
    omitted=events[:cleanup_index]+events[cleanup_index+1:]
    reject('omitted_cleanup',lambda:verify_cleanup(omitted,structure['signed_operations'],v))
    unpaid=dict(events[cleanup_index],cleanup=False,operation=-1,ca=1,cb=1)
    cancelling=dict(unpaid,cb=-1)
    mutated_events=events[:cleanup_index]+[unpaid,cancelling]+events[cleanup_index:]
    reject('unpaid_cancelling_pair',lambda:verify_cleanup(mutated_events,structure['signed_operations'],v))
    mutated=dict(children);mutated[1]+=2;mutated[2]-=1
    need(sum(r*n for r,n in mutated.items()) == mass,'mass-preserving control')
    reject('mass_preserving_histogram_mutation',lambda:need(Counter(mutated) == children,'histogram differs despite equal rank mass'))
    wrong_hashes=dict(hashes);wrong_hashes['word']='0'*64
    reject('source_corruption',lambda:need(wrong_hashes == pins['sha256'],'corrupted source hash'))
    result=dict(status='PASS_EXACT_REFLECTED_GEOMETRY_AND_INVERSE_ALGEBRA',input_sha256=hashes,
                checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),pins_sha256=sha256(args.pins.read_bytes()).hexdigest(),
                source_commit=pins['source_commit'],module_contracts=module_contracts,regeneration=regeneration,structure=structure,forward=forward,reflected=reverse,
                representatives=frame_checks,endpoint_adapters=endpoint_checks,phase_check=unit_phase_check(),cover=cover,
                histogram=dict(sorted(children.items())),children=sum(children.values()),m=m,W=W,rank=mass,deficit=W*m-mass,
                forward_literal_sha256=digest(events),reflected_literal_sha256=digest(reflected),negative_controls=controls,
                elapsed_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                python=sys.version,proof_scope='Finite full complemented chronology, all common-frame incidences and paid transitions, original-source K blocks, copied centers, inverse cleanup and bank renaming. Exact arbitrary-dirty/source coefficients are separately certified by the independent integer core checker. Exact Clifford lifts and the all-size/cover/streaming transfer remain stated written dependencies; no full O(66,2) group enumeration or unconditional multiplication theorem is claimed.')
    if args.events:
        with gzip.open(args.events,'xb') as stream:
            for row in encode(events):stream.write(row)
    with args.output.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({k:result[k] for k in ('status','elapsed_seconds','peak_rss_kib','children','rank','deficit')},sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
