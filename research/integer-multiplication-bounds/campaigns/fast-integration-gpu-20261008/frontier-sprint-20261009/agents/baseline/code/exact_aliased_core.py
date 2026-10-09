#!/usr/bin/env python3
"""Exact adjoint audit of PR160's compensated aliased complex core.

Independent integer propagation; no random vectors, modular inference or saved
verdicts. Input: exported graph/selection and frozen physical alias pairs.
Coefficients are represented by formal center coordinates and side targets;
the center map is expanded exactly when checking the resulting operator.

The emitted scalar chronology follows paired_cube_physical.py (eumemic,
icekylinx and inherited contributors, Apache-2.0). This checker is authored by
RaD with OpenAI Codex assistance. It does not establish the all-size compiler
or independently reconstruct geometric frames / global three-stage transfer.
"""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys
import time


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(dst, src, multiplier=1):
    for key, value in src.items():
        new = dst.get(key, 0) + multiplier * value
        if new:
            dst[key] = new
        else:
            dst.pop(key, None)


def scaled(src, multiplier):
    return {key: multiplier * value for key, value in src.items() if value}


def inverse(event):
    kind, *data = event
    if kind == 'gate':
        dst, src, ca, cb = data
        need(ca in (-1, 1), 'nonunit signed gate')
        return ('gate', dst, src, ca, -ca * cb)
    if kind == 'inject':
        dst, src, sign = data
        return ('inject', dst, src, -sign)
    raise ValueError('non-mutation event in cleanup')


def prepare(graph, word, pairs, roles):
    h, v = graph['h'], graph['v']
    need(len(graph['inputs']) == v, 'input count')
    need(len(word['ops']) == len(word['opcoeff']), 'operation coefficient count')
    sources = {int(key): value for key, value in word['sources'].items()}
    roots = graph['roots']
    need(len(roots) == len(word['rootroles']), 'root roles')
    root_response = {}
    for root, role in zip(roots, word['rootroles']):
        need(type(role) is int and 0 <= role < roles, 'illegal root role')
        need(role not in root_response, 'duplicate root role')
        if root['kind'] == 'center':
            coordinate = root['coordinate']
            need(0 <= coordinate < h, 'illegal center coordinate')
            need(root['coefficients'] == ['1/3' if q >> coordinate & 1 else '-1/6'
                                         for q in graph['inputs']], 'center coefficients')
            root_response[role] = {-1-coordinate: 1}
        else:
            row = {}
            for target, coefficient in zip(root['targets'], root['coefficients']):
                need(type(target) is int and 0 <= target < v, 'illegal target')
                need(coefficient in ('1/2', '-1/2'), 'side coefficient')
                row[target] = row.get(target, 0) + (3 if coefficient == '1/2' else -3)
            root_response[role] = row
    response = [dict(root_response.get(s, {})) for s in range(roles)]
    ops = []
    for (dst, src, node), (ca, cb) in zip(word['ops'], word['opcoeff']):
        need(all(type(s) is int and 0 <= s < roles for s in (dst, src)), 'illegal operation role')
        need(dst != src and ca in (-1, 1) and cb in (-1, 1), 'invalid signed operation')
        ops.append((dst, src, ca, cb))
    # Exact original adjoint, recomputed from every signed operation.
    for dst, src, ca, cb in reversed(ops):
        add(response[src], response[dst], cb)
        if ca == -1:
            response[dst] = scaled(response[dst], -1)
    merge, deadline, donors = {}, {}, set()
    for donor, recipient, when in pairs:
        need(all(type(s) is int and 0 <= s < roles for s in (donor, recipient)), 'illegal alias role')
        need(donor != recipient and donor not in donors and recipient not in merge, 'duplicate alias')
        donors.add(donor); merge[recipient] = donor; deadline[recipient] = when
    need(not donors.intersection(merge), 'alias chain')
    alias = lambda s: merge.get(s, s)
    selected = [item['role'] for item in word['selected']]
    deferred = set(selected)
    need(len(deferred) == len(selected) and set(merge) <= deferred, 'selected aliases')
    phase = sorted(word['phase1'])
    need(len(set(phase)) == len(phase) and all(0 <= i < len(ops) for i in phase), 'phase indices')
    phase_set = set(phase)
    rest = [i for i in range(len(ops)) if i not in phase_set]
    late_at = defaultdict(list)
    for recipient, when in deadline.items():
        if when is not None:
            need(type(when) is int and when in rest, 'late deadline')
            late_at[when].append(recipient)
    events, mutations = [], []
    def read(role, sign, root_only=False):
        events.append(('read', alias(role), sign, root_response[role] if root_only else response[role], role))
    def gate(index):
        dst, src, ca, cb = ops[index]
        need(alias(dst) != alias(src), 'aliased gate ports')
        event = ('gate', alias(dst), alias(src), ca, cb)
        events.append(event); mutations.append(event)
    for role in range(roles):
        if role not in deferred and role not in merge:
            read(role, -1)
    for node, role in sources.items():
        need(1 <= node <= v and 0 <= role < roles, 'illegal source')
        event = ('inject', alias(role), node-1, 1)
        events.append(event); mutations.append(event)
    for index in phase:
        gate(index)
    for root, role in zip(roots, word['rootroles']):
        if root['kind'] == 'center':
            read(role, 1, True)
    for role in reversed(selected):
        if deadline.get(role) is None:
            read(role, -1)
    for index in rest:
        for role in late_at.get(index, ()):
            read(role, -1)
        gate(index)
    for root, role in zip(roots, word['rootroles']):
        if root['kind'] == 'side':
            read(role, 1, True)
    cleanup = [inverse(event) for event in reversed(mutations)]
    return events, mutations, cleanup, sorted(set(range(roles))-set(merge)), response


def expanded(row, graph):
    h = graph['h']
    center = [row.get(-1-c, 0) for c in range(h)]
    total = sum(center)
    return [row.get(t, 0)-total+3*sum(center[c] for c in graph['labels'][t])
            for t in range(graph['v'])]


def check(graph, events, mutations, cleanup, live, *, mutation=None):
    need(len(cleanup) == len(mutations), 'cleanup length')
    need(all(actual == inverse(original) for actual, original in zip(cleanup, reversed(mutations))),
         'cleanup is not the exact signed inverse')
    if mutation == 'omit_cleanup':
        check(graph, events, mutations, cleanup[:-1], live)
        raise ValueError('cleanup control not rejected')
    adj = {role: {} for role in live}
    source = [{} for _ in range(graph['v'])]
    event_list = list(events)
    if mutation == 'omitted_read':
        i = next(i for i, event in enumerate(event_list) if event[0] == 'read' and event[2] == -1)
        del event_list[i]
    if mutation == 'bad_sign':
        i = next(i for i, event in enumerate(event_list) if event[0] == 'gate' and event[-1] == -1)
        event_list[i] = (*event_list[i][:-1], 1)
    if mutation == 'illegal_index':
        event_list.append(('read', -1, 1, {0: 1}, -1))
    for event in reversed(event_list):
        kind = event[0]
        if kind == 'read':
            _, role, sign, response, _ = event
            need(role in adj, 'illegal literal role')
            add(adj[role], response, sign)
        elif kind == 'gate':
            _, dst, src, ca, cb = event
            need(dst in adj and src in adj and dst != src, 'illegal literal gate')
            add(adj[src], adj[dst], cb)
            if ca == -1:
                adj[dst] = scaled(adj[dst], -1)
        elif kind == 'inject':
            _, role, x, sign = event
            need(role in adj and 0 <= x < len(source), 'illegal literal source')
            add(source[x], adj[role], sign)
        else:
            raise ValueError('unknown event')
    for role, row in adj.items():
        need(not row or not any(expanded(row, graph)), 'arbitrary dirty response at role %d' % role)
    v = graph['v']
    for s, row in enumerate(source):
        result = expanded(row, graph)
        cube = (s//8)*8
        for t in range(cube, cube+8):
            distance = (graph['inputs'][s] ^ graph['inputs'][t]).bit_count()
            result[t] += 3 if distance == 6 else -3 if distance == 2 else 0
        need(all(value == 6*(t == s) for t, value in enumerate(result)),
             'exact scalar source response %d' % s)
    # Every elementary inverse is checked, so the reversed literal word is
    # exactly the inverse operator. The explicit bank swap preserves indices.
    need(all(inverse(inverse(event)) == event for event in mutations), 'inverse round trip')
    return dict(exact_source_output_coefficients=v*v,
                exact_dirty_output_coefficients=len(live)*v,
                dirty_slots=len(live), literal_read_and_mutation_events=len(events),
                cleanup_events=len(cleanup), reflected_inverse_roundtrip=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    started = time.monotonic()
    paths = dict(graph=args.export/'graph.json', word=args.export/'selection.json',
                 pairs=args.tree/'references/paired-cube/physical/pairs.json',
                 record=args.tree/'certificates/paired-cube-complex-input.json')
    data = {name: json.loads(path.read_text()) for name, path in paths.items()}
    prepared = prepare(data['graph'], data['word'], data['pairs']['pairs'], data['record']['R'])
    events, mutations, cleanup, live, response = prepared
    result = check(data['graph'], events, mutations, cleanup, live)
    controls = {}
    for mutation in ('omitted_read', 'bad_sign', 'illegal_index', 'omit_cleanup'):
        try:
            check(data['graph'], events, mutations, cleanup, live, mutation=mutation)
        except (ValueError, KeyError) as error:
            controls[mutation] = str(error)
        else:
            raise ValueError('negative control accepted: '+mutation)
    result.update(status='PASS_EXACT_LOCAL_SCALAR_CORE', negative_controls=controls,
                  elapsed_seconds=time.monotonic()-started,
                  input_sha256={name: sha256(path.read_bytes()).hexdigest() for name, path in paths.items()},
                  scope='Exact integer response of the emitted compensated aliased local core; arbitrary dirty inputs, '
                        'all source/target coefficients, and exact signed cleanup inverse. Reflected scalar identity '
                        'follows from checked literal inverse and bank renaming; geometric frame complementation and '
                        'global stopped transfer are separate obligations. No sampling or modular inference.')
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
