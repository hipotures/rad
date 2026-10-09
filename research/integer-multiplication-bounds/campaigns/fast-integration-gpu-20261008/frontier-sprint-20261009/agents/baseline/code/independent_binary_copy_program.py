#!/usr/bin/env python3
"""Exact scalar/address adapter for a literal binary word with deferred copies.

JSON defines the actual word. Every clean opcode/root is checked against the
independently reconstructed graph, and compensation uses real chronological
read cuts and physical slots. No frame, prime, paid-ledger or all-size claim
is implied by this module. A winning word must receive those separate gates.
"""
from collections import defaultdict
from hashlib import sha256
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def index(value, limit, message):
    need(type(value) is int and 0 <= value < limit, message)
    return value


def layout(graph, word):
    v, nodes = graph['v'], len(graph['args'])
    operations = word['ops']
    need(operations, 'nonempty literal word')
    roles = 1+max(max(a, b) for a, b, _ in operations)
    phase = set(word['phase1'])
    need(len(phase) == len(word['phase1']), 'unique center phase operations')
    for i in phase:
        index(i, len(operations), 'actual phase operation')
    order = sorted(phase)+[i for i in range(len(operations)) if i not in phase]
    position = {i: t for t, i in enumerate(order)}
    role_operations = defaultdict(list)
    previous, predecessors = {}, []
    for i, (a, b, node) in enumerate(operations):
        index(a, roles, 'actual destination'); index(b, roles, 'actual control'); index(node, nodes, 'actual graph node')
        need(a != b, 'distinct actual virtual ports')
        predecessors.append((previous.get(a, -1), previous.get(b, -1)))
        previous[a] = previous[b] = i
    for i in order:
        for role in operations[i][:2]:
            role_operations[role].append(i)
    root_roles = word['rootroles']
    need(len(root_roles) == len(graph['roots']) and len(set(root_roles)) == len(root_roles), 'complete unique root roles')
    closure, stack = set(), []
    for root, role in zip(graph['roots'], root_roles):
        index(role, roles, 'actual root role')
        if root['kind'] == 'center' and role in previous:
            stack.append(previous[role])
    while stack:
        i = stack.pop()
        if i not in closure:
            closure.add(i)
            stack.extend(j for j in predecessors[i] if j >= 0)
    need(closure == phase, 'actual complete center phase closure')
    sources = {int(s): role for s, role in word['sources'].items()}
    need(set(sources) == set(range(v)) and len(set(sources.values())) == v, 'complete source entrances')
    gauges = {item['role']: item for item in word['gauges']}
    need(len(gauges) == len(word['gauges']) and not set(gauges) & set(sources.values()), 'unique non-source gauges')
    return dict(v=v, roles=roles, operations=operations, order=order, position=position,
                role_operations=role_operations, sources=sources, gauges=gauges, cut=len(phase))


def bind_values(graph, word):
    context = layout(graph, word)
    v, roles, args = context['v'], context['roles'], graph['args']
    support = [1 << s for s in range(v)]
    need(all(item is None for item in args[:v]), 'graph source leaves')
    for node, operands in enumerate(args[v:], v):
        need(isinstance(operands, list) and len(operands) == 2, 'integer graph addition')
        a, b = operands
        index(a, node, 'earlier graph operand'); index(b, node, 'earlier graph operand')
        need(not support[a] & support[b], 'graph operands have disjoint integer support')
        support.append(support[a] | support[b])
    fresh = [0] * roles
    for source, role in context['sources'].items():
        index(role, roles, 'source role'); fresh[role] = 1 << source
    copies = 0
    for i in context['order']:
        destination, control, node = context['operations'][i]
        need(not fresh[destination] & fresh[control], 'actual conservative opcode operands disjoint')
        copies += not fresh[destination]
        fresh[destination] ^= fresh[control]
        need(fresh[destination] == support[node], 'actual clean opcode has its tagged graph value')
    for root, role in zip(graph['roots'], word['rootroles']):
        need(fresh[role] == support[root['node']], 'actual clean root has its defining value')
    return dict(virtual_roles=roles, operations=len(context['operations']), exact_clean_copy_operations=copies,
                every_opcode_value_bound=True, every_root_value_bound=True, full_center_phase_closure=True,
                scope='All clean conservative graph/opcode/root values and phase closure. Arbitrary dirty restoration, '
                      'frames, prime units and complete paid accounting are separate checks.')


def emit_scalar_program(graph, word, partner, pairs=None):
    context = layout(graph, word)
    v, roles, gauges = context['v'], context['roles'], context['gauges']
    order, position, cut = context['order'], context['position'], context['cut']
    operations, role_operations = context['operations'], context['role_operations']
    reads = {int(role): value for role, value in word.get('reads', {}).items()}
    need(set(reads) <= set(gauges), 'only actual gauges have read cuts')
    when = {role: reads.get(role, cut) for role in gauges}
    pairs = word.get('pairs', []) if pairs is None else pairs
    donors, merge = {}, {}
    for pair in pairs:
        need(len(pair) in (2, 3), 'actual physical alias tuple')
        a, b = pair[:2]
        index(a, roles, 'actual donor'); index(b, roles, 'actual recipient')
        need(a != b and a not in donors and b not in merge, 'one-to-one physical alias matching')
        need(a not in gauges and a not in word['rootroles'] and b in gauges, 'ungauged non-root donor and gauged recipient')
        donors[a], merge[b] = b, a
        if len(pair) == 3:
            operation = index(pair[2], len(operations), 'actual recipient opcode deadline')
            when[b] = position[operation]
    need(not set(donors) & set(merge), 'disjoint donor/recipient families')
    for role, at in when.items():
        index(at, len(order)+1, 'actual read cut')
        need(role_operations[role] and cut <= at <= position[role_operations[role][0]], 'read before first use and after centers')
    for a, b in donors.items():
        need(role_operations[a] and position[role_operations[a][-1]] < when[b], 'donor dead before actual compensation')
    live = [r for r in range(roles) if r not in merge]
    slots = {r: i for i, r in enumerate(live)}
    port = lambda role: 2*v+slots[merge.get(role, role)]
    need(all(port(a) != port(b) for a, b, _ in operations), 'distinct physical scalar ports')
    response = [0] * roles
    for root, role in zip(graph['roots'], word['rootroles']):
        for target in root['targets']:
            index(target, v, 'actual root receiver'); response[role] ^= 1 << target
    for i in reversed(order):
        a, b, _ = operations[i]; response[b] ^= response[a]
    at = defaultdict(list)
    for item in reversed(word['gauges']):
        at[when[item['role']]].append(item['role'])
    events, compensated = [], {}

    def old_read(role):
        if response[role]:
            if role in merge:
                compensated[role] = len(events)
            events.append(('broadcast', port(role), response[role] << v))

    def operation(i):
        a, b, _ = operations[i]; events.append(('xor', port(a), port(b)))

    for role in live:
        if role not in gauges:
            old_read(role)
    for source, role in context['sources'].items():
        events.append(('xor', port(role), source))
    for i in order[:cut]:
        operation(i)
    for root, role in zip(graph['roots'], word['rootroles']):
        if root['kind'] == 'center':
            events.append(('broadcast', port(role), sum(1 << t for t in root['targets']) << v))
    for clock in range(cut, len(order)):
        for role in at[clock]:
            old_read(role)
        operation(order[clock])
    for role in at[len(order)]:
        old_read(role)
    deliveries = defaultdict(list)
    for entry in partner['entries']:
        index(entry['carrier'], v, 'K carrier'); index(entry['passive'], v, 'K passive')
        events.append(('xor', entry['carrier'], entry['passive']))
        anchor = index(entry['deliver_after_root'], len(graph['roots']), 'actual K delivery root')
        need(sorted(entry['receivers']) == sorted(graph['roots'][anchor]['targets']), 'actual receiver-pair K anchor')
        deliveries[anchor].append(entry)
    for j, (root, role) in enumerate(zip(graph['roots'], word['rootroles'])):
        if root['kind'] != 'center':
            events.append(('broadcast', port(role), sum(1 << t for t in root['targets']) << v))
        for entry in deliveries[j]:
            events.append(('broadcast', entry['carrier'], sum(1 << t for t in entry['receivers']) << v))
    for entry in partner['entries']:
        events.append(('xor', entry['carrier'], entry['passive']))
    for i in reversed(order):
        operation(i)
    for source, role in context['sources'].items():
        events.append(('xor', port(role), source))
    return events, dict(v=v, virtual_roles=roles, physical_roles=len(live), aliases=len(merge),
                        actual_compensation_events=compensated, read_positions=when,
                        program_sha256=sha256(json.dumps(events, separators=(',', ':')).encode()).hexdigest(),
                        scope='Complete literal scalar chronology only. Local-ring frame/copy representatives and '
                              'paid child/scalar/router ledgers must be checked independently.')
