#!/usr/bin/env python3
"""Independent literal reflected geometry for PR168 fd25 target-backed terminal sinks.

Authored by RaD with OpenAI Codex assistance. No producer or sink-gate imports.
Reuses this lane's independently authored binary Clifford/closure utilities;
new exact sink reconstruction, rational inverses and literal export comparison
are distinct from the historical auxiliary-only reviewers. Python 3.11+.
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
    elif kind in ('sink_shear','sink_write'):
        event['regs'] = tuple(bank_swap(r) for r in event['regs'])
        event['numerator'] = -event['numerator']
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
        elif kind in ('sink_shear','sink_write'):
            need(actual['denominator'] == original['denominator']
                 and actual['numerator'] + original['numerator'] == 0, 'exact rational sink inverse')
            need(actual['sink'] == original['sink'], 'inverse sink binding')
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
            elif kind in ('sink_shear','sink_write'):
                bank = 'x' if reflected else 'y'
                need(regs[0][0] == bank and regs[0] != regs[1], 'sink target port')
                need(event['numerator'] in (-1,1), 'rational sink numerator')
                if kind == 'sink_write':
                    need(regs[1][0] == 'a' and event['denominator'] == 2, 'half sink write interface')
                else:
                    need(regs[1][0] == bank and event['denominator'] == 1, 'target-target sink shear interface')
                incidences['rational_sink_ports'] += 2
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


def check_triple_contract(module, p):
    labels = list(combinations(range(p), 3))
    count = len(labels)
    need(module['input_count'] == count and len(module['roots']) == count,
         'triple module dimensions')
    need([tuple(x) for x in module['input_labels']] == labels
         and [tuple(x) for x in module['target_labels']] == labels,
         'triple module label order')
    args = module['args']
    need(all(a == [0,0] for a in args[:count+1]), 'one-based triple inputs')
    supports = [0] + [1 << i for i in range(count)]
    for x, operands in enumerate(args[count+1:], count+1):
        need(len(operands) == 2 and all(type(y) is int and 0 < y < x for y in operands),
             'triple module operand')
        a,b = operands
        need(not supports[a] & supports[b], 'triple module overlap')
        supports.append(supports[a] | supports[b])
    for J, root in zip(labels, module['roots']):
        need(type(root) is int and 0 < root < len(supports), 'triple module root index')
        expected = sum(1 << i for i,I in enumerate(labels) if not set(I) & set(J))
        need(supports[root] == expected, 'triple module exact disjoint support')
    return dict(input_count=count, additions=len(args)-count-1,
                output_count=count, exact_root_supports_checked=count,
                disjoint_positive_additions=True)


def prepare(graph, witness, word, pairs, changed, R, chosen):
    """Independently derive physical aliases, frames, responses and sink eligibility."""
    h,v = graph['h'],graph['v']
    need(h == 22 and v == 1320 and R == 13606, 'fd25 body dimensions')
    full = span(1 << i for i in range(h))
    inputs = graph['inputs']
    need(len(inputs) == v and len(set(inputs)) == v, 'input label count')
    spans = []
    for node,a in enumerate(graph['args']):
        if a is None:
            need(node < v, 'null noninput node')
            spans.append((inputs[node],))
        else:
            need(len(a) == 2 and all(type(x) is int and 0 <= x < node for x in a), 'node operands')
            spans.append(span(spans[a[0]]+spans[a[1]]))
    ops,coef = word['ops'],word['opcoeff']
    need(len(ops) == len(coef) == 32972 and all(ca == 1 and cb in (-1,1) for ca,cb in coef),
         'fd25 signed shear word')
    frames = [annihilator(tuple(witness['annihilators'][x]),h) for a,b,x in ops]
    seen = set()
    for i,U in changed:
        need(type(i) is int and 0 <= i < len(ops) and i not in seen, 'changed frame index')
        U = tuple(U)
        need(U and all(type(u) is int and 0 < u < 1 << h for u in U)
             and span(U) == U and U != frames[i], 'noncanonical or unchanged operation frame')
        frames[i] = U
        seen.add(i)
    roles = defaultdict(list)
    for i,((a,b,x),U) in enumerate(zip(ops,frames)):
        need(all(type(r) is int and 0 <= r < R for r in (a,b)) and a != b, 'operation ports')
        need(0 < x <= len(spans) and subset(spans[x-1],U), 'operation value incidence')
        roles[a].append(i);roles[b].append(i)
    phase = sorted(word['phase1']);pset = set(phase)
    need(len(phase) == len(pset) and all(type(i) is int and 0 <= i < len(ops) for i in phase), 'phase index')
    rest = [i for i in range(len(ops)) if i not in pset]
    position = {i:k for k,i in enumerate(phase+rest)}
    selected = {z['role']:z for z in word['selected']}
    need(len(selected) == len(word['selected']) == 2310, 'gauge count')
    merge,donors,deadline = {},{},{}
    for a,b,t in pairs:
        need(all(type(r) is int and 0 <= r < R for r in (a,b)) and a != b, 'pair index')
        need(a not in donors and b not in merge, 'duplicate pair')
        donors[a] = b;merge[b] = a;deadline[b] = t
    need(not set(donors)&set(merge) and set(merge) == set(selected), 'all physical gauges paired')
    rootroles = word['rootroles']; roots = graph['roots']
    need(len(roots) == len(rootroles) == 3157 and len(set(rootroles)) == len(rootroles), 'root role coverage')
    need(not set(donors)&set(rootroles) and not set(donors)&set(selected), 'donor kind')
    sources = {int(x):s for x,s in word['sources'].items()}
    need(set(sources) == set(range(1,v+1)) and len(set(sources.values())) == v, 'source allocation')
    gauge = {s:annihilator(tuple(z['annihilator']),h) for s,z in selected.items()}
    for a,b in donors.items():
        need(roles[a] and roles[b], 'empty paired role')
        last,first = roles[a][-1],roles[b][0]
        t = deadline[b]
        if t is None:
            need(last in pset and first not in pset, 'phase-cut alias chronology')
        else:
            need(type(t) is int and t == first and t not in pset
                 and position[last] < position[t], 'late alias chronology')
        need(selected[b]['rank'] == len(gauge[b]) == 18 and subset(frames[last],gauge[b]),
             'donor into gauge frame')
    alias = lambda s:merge.get(s,s)
    live = sorted(set(range(R))-set(merge))
    need(len(live) == 11296, 'body physical auxiliary count')
    slot = {s:i for i,s in enumerate(live)}
    addr = lambda s:2*v+slot[alias(s)]
    rootframe,cseed,dseed = {},{},{}
    co = [0]*R
    for r,s in zip(roots,rootroles):
        need(type(s) is int and 0 <= s < R, 'root role index')
        targets = r['targets']
        need(len(targets) == len(set(targets)) and all(type(t) is int and 0 <= t < v for t in targets),
             'root target index')
        co[s] = sum(1 << t for t in targets)
        if r['kind'] == 'center':
            c = r['coordinate']
            need(type(c) is int and 0 <= c < h and targets == list(range(v)), 'center scatter ports')
            need([Fraction(q) for q in r['coefficients']] ==
                 [Fraction(1,3) if c in graph['labels'][t] else Fraction(-1,6) for t in range(v)],
                 'center scatter coefficients')
            cseed[s] = tuple(int(i == c) for i in range(h))
            rootframe[s] = spans[r['node']]
            need(len(rootframe[s]) == 20, 'center rank')
        else:
            need(r['kind'] == 'side' and len(r['coefficients']) == len(targets), 'side root coefficients')
            values = [Fraction(q) for q in r['coefficients']]
            need(all(q in (Fraction(1,2),Fraction(-1,2)) for q in values), 'half side root coefficient')
            dseed[s] = {t:int(2*q) for t,q in zip(targets,values)}
            rootframe[s] = annihilator(span(inputs[t] for t in targets),h)
            need(subset(spans[r['node']],rootframe[s]), 'side value inside target frame')
    cvec = [cseed.get(s) for s in range(R)]
    dpart = [dict(dseed.get(s,{})) for s in range(R)]
    for (a,b,x),(ca,cb) in zip(reversed(ops),reversed(coef)):
        co[b] |= co[a]
        if cvec[a] is not None:
            old = cvec[b] or (0,)*h
            cvec[b] = tuple(u+cb*w for u,w in zip(old,cvec[a]))
        for t,n in dpart[a].items():
            dpart[b][t] = dpart[b].get(t,0)+cb*n
    for s,z in selected.items():
        need(z['targets'] == list(members(co[s])), 'selected target incidence')
        need(all(subset(gauge[s],annihilator((inputs[t],),h)) for t in z['targets']), 'gauge target cap')
    read_at = defaultdict(list)
    first_read = {}
    for z in reversed(word['selected']):
        s = z['role'];t = deadline[s]
        actual = rest[0] if t is None else t
        need(actual not in pset, 'read in center phase')
        read_at[actual].append(s)
        for target in z['targets']:
            first_read[target] = min(first_read.get(target,1 << 60),position[actual])
    sink = {}
    need(len(chosen) == 42, 'fd25 sink count')
    root_by_role = dict(zip(rootroles,roots))
    for s,p in chosen:
        need(type(s) is int and type(p) is int and s not in sink, 'sink identity')
        need(s in root_by_role and root_by_role[s]['kind'] == 'side', 'sink side root')
        root = root_by_role[s]
        need(s not in selected and s not in donors and s not in merge and s not in sources.values(), 'sink zero frame interface')
        writes = [i for i in roles[s] if ops[i][0] == s]
        need(writes and len(writes) == len(roles[s]) and all(i not in pset for i in writes), 'destination-only post-phase sink')
        need(len(set(root['coefficients'])) == 1 and p in root['targets'], 'sink pivot and common coefficient')
        U = rootframe[s]
        path = [()] + [frames[i] for i in writes] + [U]
        need(all(subset(a,b) for a,b in zip(path,path[1:])), 'sink write chain into root')
        need(cvec[s] is None and dpart[s] == dseed[s], 'sink has no retained producer response')
        need(first_read.get(p,1 << 60) > max(position[i] for i in writes), 'pivot read before sink completion')
        need(len(root['targets']) == 8 and len(U) == 18, 'all-eight sink scope')
        sink[s] = dict(T=root['targets'],c=p,writes=writes,U=U,coeff=root['coefficients'][0])
    touched = [t for z in sink.values() for t in z['T']]
    need(len(touched) == len(set(touched)), 'overlapping sink target groups')
    return dict(h=h,v=v,R=R,full=full,inputs=inputs,spans=spans,ops=ops,coef=coef,frames=frames,
                phase=phase,rest=rest,selected=selected,merge=merge,donors=donors,deadline=deadline,
                sources=sources,gauge=gauge,live=live,slot=slot,addr=addr,roots=roots,rootroles=rootroles,
                rootframe=rootframe,cseed=cseed,dseed=dseed,cvec=cvec,dpart=dpart,read_at=read_at,
                sink=sink,changed=len(seen),first_read=first_read,position=position)


def compact_word(ctx, active):
    """Reconstruct the actual primitive order independently, with rational coefficients."""
    v,h,R = ctx['v'],ctx['h'],ctx['R']
    A = ctx['addr'];F = ctx['frames'];out = [];producers = []
    sink_write = {i:s for s,z in active.items() for i in z['writes']}
    last = {z['writes'][-1]:s for s,z in active.items()}
    reach = lambda s:list(range(v)) if ctx['cvec'][s] is not None else sorted(t for t,n in ctx['dpart'][s].items() if n)
    for s in range(R):
        if s not in ctx['selected'] and s not in active:
            out.append(dict(k='read',raw=['read',A(s),s,-1,'resp',(),'Y',reach(s)]))
    for node,s in sorted(ctx['sources'].items(),key=lambda x:x[1]):
        out.append(dict(k='inj',raw=['inj',A(s),node-1,1,(ctx['inputs'][node-1],)],source=node-1,cleanup=False))
    def operation(i):
        a,b,x = ctx['ops'][i]
        out.append(dict(k='op',raw=['op',A(a),A(b),ctx['coef'][i][1],F[i]],operation=i,cleanup=False))
        producers.append(i)
    for i in ctx['phase']:operation(i)
    for s in ctx['cseed']:
        out.append(dict(k='centre',raw=['centre',A(s),s,1,ctx['rootframe'][s],(),'Y']))
    for s,z in active.items():
        for t in z['T']:
            if t != z['c']:
                out.append(dict(k='ysh',raw=['ysh',v+t,v+z['c'],-1,()],sink=s,stage='pre'))
    for i in ctx['rest']:
        for s in ctx['read_at'][i]:
            out.append(dict(k='read',raw=['read',A(s),s,-1,'resp',ctx['gauge'][s],'Y',ctx['selected'][s]['targets']]))
        if i in sink_write:
            s = sink_write[i];z = active[s]
            q = Fraction(z['coeff'])*ctx['coef'][i][1]
            out.append(dict(k='yw',raw=['yw',v+z['c'],A(ctx['ops'][i][1]),q,F[i]],sink=s,operation=i))
        else:operation(i)
        if i in last:
            s = last[i];z = active[s]
            for t in z['T']:
                if t != z['c']:
                    out.append(dict(k='ysh',raw=['ysh',v+t,v+z['c'],1,z['U']],sink=s,stage='post'))
    for root,s in zip(ctx['roots'],ctx['rootroles']):
        if root['kind'] == 'side' and s not in active:
            out.append(dict(k='read',raw=['read',A(s),s,1,'seed',ctx['rootframe'][s],'Y',root['targets']]))
    for b in range(0,v,8):
        qs = ctx['inputs'][b:b+8]
        kernel = [[1 if (q^r).bit_count() == 6 else -1 if (q^r).bit_count() == 2 else 0 for r in qs] for q in qs]
        for parity in (0,1):
            source = [i for i in range(8) if i.bit_count()%2 == parity]
            target = [i^7 for i in source]
            matrix = [[Fraction(kernel[t][s],2) for s in source] for t in target]
            need(all(sum(matrix[i][k]*matrix[j][k] for k in range(4)) == (i == j)
                     for i in range(4) for j in range(4)), 'exact native K block inverse')
            U = span(qs[s] for s in source)
            need(len(U) == 3 and all(subset(U,annihilator((qs[t],),h)) for t in target), 'actual K value incidence')
            regs = [b+s for s in source]
            out.append(dict(k='ktr',raw=['ktr',regs,matrix,U,'X']))
            for s,t in zip(source,target):
                out.append(dict(k='kd',raw=['kd',v+b+t,b+s,1,annihilator((qs[t],),h)]))
            out.append(dict(k='ktr',raw=['ktr',regs,list(map(list,zip(*matrix))),ctx['full'],'X']))
    for i in reversed(producers):
        a,b,x = ctx['ops'][i]
        out.append(dict(k='op',raw=['op',A(a),A(b),-ctx['coef'][i][1],ctx['full']],operation=i,cleanup=True))
    for node,s in sorted(ctx['sources'].items(),key=lambda x:x[1],reverse=True):
        out.append(dict(k='inj',raw=['inj',A(s),node-1,-1,ctx['full']],source=node-1,cleanup=True))
    return out


def reflect_compact(word,h,v):
    def swap(r):return r+v if r < v else r-v if r < 2*v else r
    out = []
    for e in reversed(word):
        raw = e['raw']; k = raw[0]
        if k == 'read':
            row = ['read',raw[1],raw[2],-raw[3],raw[4],annihilator(tuple(raw[5]),h),'X' if raw[6] == 'Y' else 'Y',raw[7]]
        elif k == 'centre':
            row = ['centre',raw[1],raw[2],-raw[3],annihilator(tuple(raw[4]),h),annihilator(tuple(raw[5]),h),'X' if raw[6] == 'Y' else 'Y']
        elif k in ('inj','op','ysh','yw','kd'):
            dest = swap(raw[1]) if k in ('ysh','yw','kd') else raw[1]
            control = swap(raw[2]) if k in ('inj','ysh','kd') else raw[2]
            row = [k,dest,control,-raw[3],annihilator(tuple(raw[4]),h)]
        elif k == 'ktr':
            row = [k,[swap(r) for r in raw[1]],list(map(list,zip(*raw[2]))),annihilator(tuple(raw[3]),h),'Y' if raw[4] == 'X' else 'X']
        else:raise ValueError('unknown compact kind')
        out.append(dict(e,raw=row))
    return out


def native_row(row):
    """Only serialization uses the native prime encoding; proofs stay rational."""
    if isinstance(row,Fraction):
        return row.numerator*pow(row.denominator,-1,(1 << 61)-1) % ((1 << 61)-1)
    if isinstance(row,(list,tuple)):
        return [native_row(x) for x in row]
    return row


def compare_export(compact,path):
    original = json.loads(path.read_text())
    need(len(original) == len(compact), 'actual exported compact event count')
    for i,(e,row) in enumerate(zip(compact,original)):
        need(native_row(e['raw']) == row, 'actual exported compact event mismatch at '+str(i))
    return dict(events=len(original),all_events_reconstructed=True,sha256=sha256(path.read_bytes()).hexdigest())


def expand(compact,ctx,active):
    """Expose every exact scalar incidence and every positive or rank-zero frame step."""
    h,v = ctx['h'],ctx['v']
    live = set(ctx['live'])-set(active)
    unaddr = {2*v+i:('a',s) for s,i in ctx['slot'].items()}
    def reg(r):
        need(type(r) is int and r >= 0, 'compact negative register')
        return ('x',r) if r < v else ('y',r-v) if r < 2*v else unaddr[r]
    initial = {('a',s):() for s in live}
    initial.update({('x',t):(q,) for t,q in enumerate(ctx['inputs'])})
    initial.update({('y',t):() for t in range(v)})
    current = dict(initial);events = [];spaces = set(initial.values())|{ctx['full']}
    def move(r,U):
        U = tuple(U)
        need(r in current, 'deleted sink or absent register touched')
        old = current[r]
        # The chosen exact operator is identical, so this ratio is exactly I.
        # Scalar incidence remains explicit; there is no physical transition.
        if old == U:return
        need(subset(old,U), 'forward scalar frame retreat '+str(r))
        bank = r[0];part = 'local' if bank == 'a' else 'source' if bank == 'x' else 'target'
        events.append(dict(kind='frame',reg=r,part=part,**{'from':old,'to':U,'width':len(U)-len(old)}))
        current[r] = U;spaces.add(U)
    for e in compact:
        raw = e['raw'];k = e['k']
        if k == 'read':
            U = tuple(raw[5]);targets = tuple(('y',t) for t in raw[7]);source = reg(raw[1])
            need(all(subset(U,annihilator((ctx['inputs'][t],),h)) for t in raw[7]), 'read target cap')
            for r in (source,)+targets:move(r,U)
            events.append(dict(kind='read',regs=(source,)+targets,frame=U,sign=raw[3],
                               decoder=('adjoint' if raw[4] == 'resp' else 'root',raw[2])))
        elif k == 'centre':
            source = reg(raw[1]);U,V = tuple(raw[4]),tuple(raw[5]);targets = tuple(('y',t) for t in range(v))
            move(source,U)
            need(all(current[r] == V for r in targets), 'copied center scatter after target advance')
            center = next(i for i,n in enumerate(ctx['cseed'][raw[2]]) if n)
            events.append(dict(kind='copy_read',regs=(source,)+targets,source_frame=U,read_frame=V,
                               width=distance(U,V,h),sign=raw[3],center=center))
        elif k == 'ktr':
            regs = tuple(reg(r) for r in raw[1]);U = tuple(raw[3])
            for r in regs:move(r,U)
            matrix = tuple(tuple(int(2*q) for q in row) for row in raw[2])
            events.append(dict(kind='matrix',regs=regs,frame=U,matrix=matrix,denominator=2,operation='K'))
        else:
            regs = (reg(raw[1]),reg(raw[2]));U = tuple(raw[4])
            for r in regs:move(r,U)
            if k == 'op':
                events.append(dict(kind='gate',regs=regs,frame=U,ca=1,cb=raw[3],operation=e['operation'],cleanup=e['cleanup']))
            elif k == 'inj':
                events.append(dict(kind='inject',regs=regs,frame=U,sign=raw[3],source=e['source'],cleanup=e['cleanup']))
            elif k in ('ysh','yw'):
                q = Fraction(raw[3])
                extra = dict(operation=e['operation']) if k == 'yw' else dict(stage=e['stage'])
                events.append(dict(kind='sink_write' if k == 'yw' else 'sink_shear',regs=regs,frame=U,
                                   numerator=q.numerator,denominator=q.denominator,sink=e['sink'],**extra))
            elif k == 'kd':
                events.append(dict(kind='read',regs=regs,frame=U,sign=raw[3],decoder=('K-output',raw[2],raw[1]-v)))
            else:raise ValueError('unknown expanded scalar')
    for r in tuple(current):
        U = annihilator((ctx['inputs'][r[1]],),h) if r[0] == 'y' else ctx['full']
        move(r,U)
    for t,q in enumerate(ctx['inputs']):
        events.append(dict(kind='endpoint_adapter',regs=(('y',t),),frame=annihilator((q,),h),q=q,direction=1,
                           exact_word='(F T_q^-1) T_(q perp)^-1',width=0))
    return events,initial,dict(current),live,spaces


def sandwich_identity(ctx,omit_post=False):
    """Formal arbitrary pivot, target and independent write variables over Q."""
    checks = 0
    for s,z in ctx['sink'].items():
        variables = len(z['T'])+len(z['writes'])
        original = [[Fraction(int(i == j)) for j in range(variables)] for i in range(len(z['T']))]
        vals = [list(row) for row in original]
        p = z['T'].index(z['c'])
        for t in range(len(vals)):
            if t != p:vals[t] = [u-w for u,w in zip(vals[t],vals[p])]
        change = [Fraction(0)]*variables
        for k,i in enumerate(z['writes']):
            change[len(z['T'])+k] = Fraction(z['coeff'])*ctx['coef'][i][1]
        vals[p] = [u+w for u,w in zip(vals[p],change)]
        if not omit_post:
            for t in range(len(vals)):
                if t != p:vals[t] = [u+w for u,w in zip(vals[t],vals[p])]
        need(all(actual == [u+w for u,w in zip(start,change)] for actual,start in zip(vals,original)),
             'formal sink sandwich target spectator identity')
        checks += len(vals)*variables
    return dict(sinks_checked=len(ctx['sink']),formal_rational_coefficients_checked=checks,
                pivot_and_all_target_spectators_exact=True,independent_write_variables=True)


def verify_complete_incidence(events,ctx):
    producers = [e for e in events if e['kind'] == 'sink_write'
                 or e['kind'] == 'gate' and not e.get('cleanup')]
    need(sorted(e['operation'] for e in producers) == list(range(len(ctx['ops']))),
         'unpaid or missing original operation')
    inverse_count = len(ctx['ops'])-sum(len(z['writes']) for z in ctx['sink'].values())
    verify_cleanup(events,inverse_count,ctx['v'])
    writes = [e for e in producers if e['kind'] == 'sink_write']
    shears = [e for e in events if e['kind'] == 'sink_shear']
    need(len(writes) == 115 and len(shears) == 588, 'sink primitive incidence')
    expected = Counter((s,stage,t) for s,z in ctx['sink'].items()
                       for stage in ('pre','post') for t in z['T'] if t != z['c'])
    actual = Counter((e['sink'],e['stage'],e['regs'][0][1]) for e in shears)
    need(actual == expected, 'missing target pre/post shear')
    for e in producers:
        i = e['operation']
        need(e['frame'] == ctx['frames'][i], 'original operation frame binding')
        if e['kind'] == 'sink_write':
            z = ctx['sink'][e['sink']]
            q = Fraction(z['coeff'])*ctx['coef'][i][1]
            need(i in z['writes'] and e['numerator'] == q.numerator
                 and e['denominator'] == q.denominator and e['regs'][0] == ('y',z['c']),
                 'rational sink output coefficient binding')
        else:
            need(e['ca'] == 1 and e['cb'] == ctx['coef'][i][1], 'retained auxiliary signed coefficient')
    return dict(original_operations=len(producers),retained_operations=inverse_count,
                retained_auxiliary_inverse_pairs=inverse_count+ctx['v'],persistent_pivot_writes=len(writes),
                target_pre_post_shears=len(shears),deleted_sink_roles=len(ctx['sink']))


def paid_inventory(replayed,profile,v,auxiliary_count):
    paid = {name:Counter({int(r):n for r,n in hist.items() if int(r)})
            for name,hist in replayed['paid'].items()}
    for part,key in (('local','local_histogram'),('source','source_data_histogram'),('target','target_data_histogram')):
        need(paid[part] == Counter({int(r):n for r,n in profile[key].items() if int(r)}),
             'complete '+part+' paid histogram mismatch')
    children = Counter()
    for part in paid.values():children.update({r:3*n for r,n in part.items()})
    children[2] += 2*v
    need(children == Counter({int(r):n for r,n in profile['child_histogram'].items() if n}), 'complete paid child inventory')
    W,m = 2*v+auxiliary_count,66
    mass = sum(r*n for r,n in children.items())
    need(profile['physical_R'] == auxiliary_count and profile['W_per_vertex'] == W
         and profile['m'] == m and profile['rank_per_vertex'] == mass
         and profile['deficit_per_vertex'] == W*m-mass, 'physical paid dimensions')
    return children,dict(W=W,m=m,rank=mass,deficit=W*m-mass,children=sum(children.values()),maximum_width=max(children))


def input_paths(body,sinks,tree):
    paths = {name:body/file for name,file in {
        'graph':'graph.json','baseline':'baseline.json','witness':'frames.json','word':'word.json',
        'pairs':'physical-pairs.json','record':'profile-before.json','physical_frames':'physical-frames.json',
        'body_profile':'profile.json','body_protocol':'protocol.json'}.items()}
    paths.update({name:sinks/file for name,file in {
        'sinks':'sinks.json','sink_map':'sink-map.json','register_map':'register-map.json',
        'forward_export':'forward-events.json','reflected_export':'reflected-events.json',
        'unsubstituted_export':'unsubstituted-events.json','sink_profile':'profile.json',
        'sink_protocol':'protocol.json'}.items()})
    paths.update({name:tree/file for name,file in {
        'producer':'scripts/paired_cube_producer.py','physical_compiler':'scripts/paired_cube_physical.py',
        'graph_compiler':'scripts/paired_cube/graph.py','module_compiler':'scripts/paired_cube/modules.py',
        'closure_compiler':'scripts/paired_cube/closure.py','gauge_compiler':'scripts/paired_cube/gauges.py',
        'source_pin_manifest':'references/paired-cube/sources/SOURCE.json',
        'selected_pin_manifest':'references/paired-cube/selected-module/SOURCE.json',
        'matching_arcs':'references/paired-cube/selected-module/matching-arcs.json',
        'local_cube_config':'references/paired-cube/sources/local_L1.json',
        'all_but_one_module':'references/paired-cube/sources/qmod_anneal_best01.json',
        'pair_module':'references/paired-cube/sources/pmod_H56snap_w02_5.6251423e-4.json',
        'triple_module':'references/paired-cube/sources/tmod_TB31_L1f8_5.9717259e-4.json',
        'general_clifford_proof':'notes/general-clifford-frames.tex',
        'local_word_proof':'notes/paired-cube-construction.tex','sharing_proof':'notes/paired-cube-sharing.tex',
        'cover_proof':'notes/three-stage-cover-complex.tex',
        'sink_compiler':'research/terminal-sinks/sinks_gate.py',
        'source_sinks':'research/terminal-sinks/sinks.json',
        'sink_explanation':'research/terminal-sinks/README.md'}.items()})
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--body-export',type=Path,required=True)
    parser.add_argument('--sink-export',type=Path,required=True)
    parser.add_argument('--tree',type=Path,required=True)
    parser.add_argument('--pins',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--events',type=Path)
    args = parser.parse_args()
    need(not sys.flags.optimize,'assertion-disabled execution rejected')
    started = time.monotonic()
    paths = input_paths(args.body_export,args.sink_export,args.tree)
    pins = json.loads(args.pins.read_text())
    hashes = {key:sha256(path.read_bytes()).hexdigest() for key,path in paths.items()}
    need(hashes == pins['sha256'],'input/source corruption or candidate drift')
    data = {name:json.loads(paths[name].read_text()) for name in
            ('graph','witness','word','pairs','record','physical_frames','body_profile','sinks','sink_map','register_map','sink_profile')}
    need(data['sinks'] == json.loads(paths['source_sinks'].read_text())['sinks'],'source sink selection changed')
    modules = {
        'all_but_one':check_module_contract(json.loads(paths['all_but_one_module'].read_text()),9,False),
        'pair_disjoint':check_module_contract(json.loads(paths['pair_module'].read_text()),10,True),
        'triple_disjoint':check_triple_contract(json.loads(paths['triple_module'].read_text()),11)}
    regeneration = regenerate_closure_and_word(data['graph'],data['witness'],data['word'],data['record']['R'])
    ctx = prepare(data['graph'],data['witness'],data['word'],data['pairs'],data['physical_frames'],data['record']['R'],data['sinks'])
    sink_map = [dict(z,U=list(z['U']),role=s) for s,z in ctx['sink'].items()]
    need(sink_map == data['sink_map'],'actual sink interface map differs')
    registers = data['register_map']
    need(registers['body_live'] == ctx['live']
         and registers['body_slot'] == {str(s):i for s,i in ctx['slot'].items()}
         and set(registers['removed']) == {ctx['addr'](s) for s in ctx['sink']}, 'actual physical register map differs')
    body = compact_word(ctx,{})
    export_bindings = {'unsubstituted':compare_export(body,paths['unsubstituted_export'])}
    b_events,b_start,b_final,b_live,b_spaces = expand(body,ctx,{})
    b_forward = replay(b_events,b_start,b_final,ctx['h'],ctx['v'],b_live)
    body_children,body_counts = paid_inventory(b_forward,data['body_profile'],ctx['v'],len(b_live))
    verify_cleanup(b_events,len(ctx['ops']),ctx['v'])
    del body,b_events
    primitive = compact_word(ctx,ctx['sink'])
    export_bindings['forward'] = compare_export(primitive,paths['forward_export'])
    reflected_primitive = reflect_compact(primitive,ctx['h'],ctx['v'])
    export_bindings['reflected'] = compare_export(reflected_primitive,paths['reflected_export'])
    events,start,final,live,spaces = expand(primitive,ctx,ctx['sink'])
    forward = replay(events,start,final,ctx['h'],ctx['v'],live)
    reflected = [invert_event(e,ctx['h']) for e in reversed(events)]
    rstart = {bank_swap(r):annihilator(U,ctx['h']) for r,U in final.items()}
    rfinal = {bank_swap(r):annihilator(U,ctx['h']) for r,U in start.items()}
    reverse = replay(reflected,rstart,rfinal,ctx['h'],ctx['v'],live,reflected=True)
    need(forward['paid'] == reverse['paid'] and forward['scalar'] == reverse['scalar'],'full reflected paid multiset')
    verify_inverse_pairs(events,reflected,ctx['h'])
    incidence = verify_complete_incidence(events,ctx)
    sandwich = sandwich_identity(ctx)
    children,counts = paid_inventory(forward,data['sink_profile'],ctx['v'],len(live))
    need(counts == dict(W=13894,m=66,rank=915684,deficit=1320,children=sum(children.values()),maximum_width=20),
         'fd25 sink paid dimensions')
    removed = body_children-children
    need(removed == Counter({4:126,18:126}) and not children-body_children,
         'complete three-stage sink reduction')
    need(len(live) == data['sink_profile']['physical_R'] == 11254
         and data['sink_profile']['sinks'] == 42,'actual retained physical auxiliary bank')
    representative_checks = verify_representatives(spaces|b_spaces|{annihilator(U,ctx['h']) for U in spaces|b_spaces},ctx['h'])
    endpoint_checks = verify_endpoint_adapters(ctx['inputs'],ctx['h'])
    cover = cover_check(ctx['inputs'],ctx['h'])
    controls = {}
    def reject(name,action):
        try:action()
        except (ValueError,KeyError,IndexError) as error:controls[name] = str(error)
        else:raise ValueError('negative control accepted: '+name)
    p = next(i for i,e in enumerate(reflected) if e['kind'] == 'sink_write' and e['frame'] != annihilator(e['frame'],ctx['h']))
    bad = list(reflected);bad[p] = dict(bad[p],frame=annihilator(bad[p]['frame'],ctx['h']))
    reject('uncomplemented_reflected_pivot_write',lambda:replay(bad,rstart,rfinal,ctx['h'],ctx['v'],live,reflected=True))
    bad_sign = list(reflected);bad_sign[p] = dict(bad_sign[p],numerator=-bad_sign[p]['numerator'])
    reject('wrong_rational_inverse_sign',lambda:verify_inverse_pairs(events,bad_sign,ctx['h']))
    bad_index = list(reflected);bad_index[p] = dict(bad_index[p],regs=(('x',-1),bad_index[p]['regs'][1]))
    reject('negative_literal_index',lambda:replay(bad_index,rstart,rfinal,ctx['h'],ctx['v'],live,reflected=True))
    at = next(i for i,e in enumerate(events) if e.get('cleanup'))
    reject('omitted_retained_cleanup',lambda:verify_complete_incidence(events[:at]+events[at+1:],ctx))
    unpaid = dict(events[at],cleanup=False,operation=-1,cb=1)
    reject('unpaid_cancelling_pair',lambda:verify_complete_incidence(events[:at]+[unpaid,dict(unpaid,cb=-1)]+events[at:],ctx))
    reject('omitted_post_shear',lambda:sandwich_identity(ctx,omit_post=True))
    post = next(i for i,e in enumerate(events) if e['kind'] == 'sink_shear' and e['stage'] == 'post')
    reject('omitted_post_shear_incidence',lambda:verify_complete_incidence(events[:post]+events[post+1:],ctx))
    early = next(e for e in primitive if e['k'] == 'ysh' and e['stage'] == 'post')
    center = next(i for i,e in enumerate(primitive) if e['k'] == 'centre')
    reject('raised_target_before_center_scatter',lambda:expand(primitive[:center]+[early]+primitive[center:],ctx,ctx['sink']))
    mutated = Counter(children);mutated[1] += 2;mutated[2] -= 1
    need(sum(r*n for r,n in mutated.items()) == counts['rank'],'rank-mass control construction')
    reject('mass_preserving_histogram_mutation',lambda:need(mutated == children,'histogram differs at fixed mass'))
    wrong_hashes = dict(hashes,word='0'*64)
    reject('source_corruption',lambda:need(wrong_hashes == pins['sha256'],'corrupted source binding'))
    result = dict(status='PASS_EXACT_LITERAL_SINK_REFLECTED_GEOMETRY_AND_INVERSE_ALGEBRA',
        input_sha256=hashes,checker_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        pins_sha256=sha256(args.pins.read_bytes()).hexdigest(),source_commit=pins['source_commit'],
        module_contracts=modules,regeneration=regeneration,sink_map=sink_map,sandwich_identity=sandwich,
        actual_export_bindings=export_bindings,body_paid=body_counts,body_forward=b_forward,
        sink_incidence=incidence,forward=forward,reflected=reverse,representatives=representative_checks,
        endpoint_adapters=endpoint_checks,phase_check=unit_phase_check(),cover=cover,
        histogram=dict(sorted(children.items())),removed_three_stage_histogram=dict(removed),**counts,
        forward_literal_sha256=digest(events),reflected_literal_sha256=digest(reflected),negative_controls=controls,
        elapsed_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        python=sys.version,proof_scope='Fresh finite literal terminal-sink and retained-body geometry, exact rational primitive inverses, every target/source/auxiliary incidence and paid transition, full complemented reverse and bank renaming, retained auxiliary cleanup, exact formal target-spectator sandwiches and actual exported-event reconstruction. Exact full source/target/dirty coefficient identities are separately checked on this actual sink word by the signed lane. General Clifford child execution, paid complete-stream copy, all-size cover/routing, row-stock and analytic transfer remain the inherited written conditional interfaces.')
    if args.events:
        with gzip.open(args.events,'xb') as stream:
            for row in encode(events):stream.write(row)
    with args.output.open('x') as stream:
        json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({key:result[key] for key in ('status','elapsed_seconds','peak_rss_kib','children','rank','deficit')},sort_keys=True),flush=True)


if __name__ == '__main__':
    main()


