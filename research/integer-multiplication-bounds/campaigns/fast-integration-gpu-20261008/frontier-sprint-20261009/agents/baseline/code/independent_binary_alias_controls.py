#!/usr/bin/env python3
"""Actual compensated-alias scalar mutations, with complete F2 columns.

The literal program is rebuilt from pinned JSON, independently of the
author's Python. The previous full finite receipt supplies only its immutable
program/code hashes; its PASS flag is not used. Geometry and prime witnesses
remain the separately reconstructed finite checker's scope.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import independent_binary_lifetime as finite


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def rebuild(export, plan):
    word = json.loads((export / 'word_p12.json').read_text())
    graph = json.loads((export / 'graph_p12.json').read_text())
    partner = json.loads((export / 'kchron_p12.json').read_text())
    v = graph['v']
    ops = word['ops']
    roles = 1 + max(max(a, b) for a, b, _ in ops)
    phase = set(word['phase1'])
    phase_order = sorted(phase)
    rest = [i for i in range(len(ops)) if i not in phase]
    chronology = phase_order + rest
    position = {i: j for j, i in enumerate(chronology)}
    role_ops = defaultdict(list)
    for i in chronology:
        for role in ops[i][:2]:
            role_ops[role].append(i)
    sources = {int(s): r for s, r in word['sources'].items()}
    gauges = {item['role']: item for item in word['gauges']}
    root_kind = {r: root['kind'] for root, r in zip(graph['roots'], word['rootroles'])}
    donors, merge, deadline = {}, {}, {}
    for a, b, t in plan['pairs']:
        finite.ix(a, roles, 'actual donor index')
        finite.ix(b, roles, 'actual recipient index')
        finite.ix(t, len(ops), 'actual recipient first operation')
        finite.need(a != b and a not in donors and b not in merge, 'one-to-one physical alias')
        finite.need(a not in gauges and a not in root_kind, 'ungauged non-root donor')
        finite.need(b in gauges and root_kind.get(b) == 'side' and gauges[b]['dim'] == 21,
                    'actual terminal recipient')
        finite.need(t not in phase and role_ops[b][0] == t, 'actual first-use compensation')
        finite.need(position[role_ops[a][-1]] < position[t], 'donor dead before compensation')
        donors[a], merge[b], deadline[b] = b, a, t
    finite.need(not set(donors) & set(merge), 'disjoint alias families')
    live = [r for r in range(roles) if r not in merge]
    slots = {r: i for i, r in enumerate(live)}
    port = lambda r: 2 * v + slots[merge.get(r, r)]
    finite.need(all(port(a) != port(b) for a, b, _ in ops), 'distinct actual aliased ports')
    response = [0] * roles
    for root, r in zip(graph['roots'], word['rootroles']):
        for t in root['targets']:
            response[r] ^= 1 << t
    for a, b, _ in reversed(ops):
        response[b] ^= response[a]
    events, compensated, cleanup = [], {}, {}

    def old_read(r):
        if response[r]:
            if r in merge:
                compensated[r] = len(events)
            events.append(('broadcast', port(r), response[r] << v))

    def operation(i):
        a, b, _ = ops[i]
        events.append(('xor', port(a), port(b)))

    for r in live:
        if r not in gauges:
            old_read(r)
    for s, r in sources.items():
        events.append(('xor', port(r), s))
    for i in phase_order:
        operation(i)
    for root, r in zip(graph['roots'], word['rootroles']):
        if root['kind'] == 'center':
            targets = sum(1 << t for t in root['targets'])
            if targets:
                events.append(('broadcast', port(r), targets << v))
    for item in reversed(word['gauges']):
        if item['role'] not in merge:
            old_read(item['role'])
    at = defaultdict(list)
    for a, b, t in plan['pairs']:
        at[t].append(b)
    for i in rest:
        for r in at[i]:
            old_read(r)
        operation(i)
    deliveries = defaultdict(list)
    for entry in partner['entries']:
        events.append(('xor', entry['carrier'], entry['passive']))
        deliveries[entry['deliver_after_root']].append(entry)
    for j, (root, r) in enumerate(zip(graph['roots'], word['rootroles'])):
        if root['kind'] != 'center':
            targets = sum(1 << t for t in root['targets'])
            if targets:
                events.append(('broadcast', port(r), targets << v))
        for entry in deliveries[j]:
            targets = sum(1 << t for t in entry['receivers'])
            if targets:
                events.append(('broadcast', entry['carrier'], targets << v))
    for entry in partner['entries']:
        events.append(('xor', entry['carrier'], entry['passive']))
    for i in reversed(chronology):
        cleanup[i] = len(events)
        operation(i)
    for s, r in sources.items():
        events.append(('xor', port(r), s))
    finite.need(compensated and len(compensated) == len(plan['pairs']),
                'every actual terminal alias has a nonzero compensated response')
    a, b, t = plan['pairs'][0]
    return events, dict(v=v, physical_R=len(live), virtual_R=roles,
                        alias_count=len(merge), actual_pair=[a, b, t],
                        compensation_event=compensated[b],
                        recipient_cleanup_event=cleanup[t],
                        donor_last_operation=role_ops[a][-1],
                        donor_last_chronological_position=position[role_ops[a][-1]],
                        recipient_first_chronological_position=position[t])


def main():
    finite.need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'source170', 'export', 'plan', 'pin', 'finite-receipt', 'output'):
        ap.add_argument('--' + name, type=Path, required=True)
    args = ap.parse_args()
    finite.need(not args.output.exists(), 'fresh control output required')
    start = time.monotonic()
    pin = json.loads(args.pin.read_text())
    receipt = json.loads(args.finite_receipt.read_text())
    for section, base in [('source_sha256', args.source),
                          ('source170_sha256', args.source170),
                          ('export_sha256', args.export)]:
        for name, expected in pin[section].items():
            relative = Path(name)
            finite.need(not relative.is_absolute() and '..' not in relative.parts, 'safe input pin')
            finite.need(digest(base / relative) == expected, 'actual control input corruption: ' + name)
    finite.need(digest(args.plan) == pin['plan_sha256'] == receipt['plan_sha256'], 'frozen plan binding')
    finite.need(digest(args.pin) == receipt['pin_manifest_sha256'], 'finite source manifest binding')
    code = Path(__file__).parent
    finite.need(digest(Path(finite.__file__)) == receipt['checker_sha256'], 'unchanged full finite checker')
    finite.need(digest(code / 'binary_exact_algebra.py') == receipt['exact_algebra_sha256'], 'unchanged exact algebra')
    finite.need(digest(code / 'independent_binary_lifetime_inputs.py') == receipt['producer_reconstruction_code_sha256'],
                'unchanged complete producer reconstruction')
    events, context = rebuild(args.export, json.loads(args.plan.read_text()))
    program_hash = sha256(json.dumps(events, separators=(',', ':')).encode()).hexdigest()
    finite.need(program_hash == receipt['literal_scalar_program_sha256'], 'fresh exact literal program binding')
    v, roles = context['v'], context['physical_R']
    positives = [finite.formal(events, v, roles), finite.formal(events, v, roles, reflected=True)]
    controls = {}

    def reject(name, actual):
        failures = {}
        for reflected in (False, True):
            try:
                finite.formal(actual, v, roles, reflected=reflected)
            except ValueError as error:
                failures['reflected' if reflected else 'forward'] = str(error)
            else:
                raise ValueError('actual scalar mutation accepted: ' + name)
        controls[name] = dict(errors=failures, literal_events=len(actual))

    j = context['compensation_event']
    omitted = list(events)
    del omitted[j]
    reject('omitted_aliased_recipient_compensation', omitted)
    early = list(events)
    early.insert(0, early.pop(j))
    reject('compensation_before_donor_lifetime', early)
    missing_cleanup = list(events)
    del missing_cleanup[context['recipient_cleanup_event']]
    reject('omitted_aliased_recipient_cleanup', missing_cleanup)
    record = dict(status='PASS_INDEPENDENT_ACTUAL_ALIAS_MUTATIONS',
                  full_positive_replay=positives, actual_alias=context,
                  negative_controls=controls, plan_sha256=pin['plan_sha256'],
                  literal_scalar_program_sha256=program_hash,
                  full_finite_receipt_sha256=digest(args.finite_receipt),
                  pin_manifest_sha256=digest(args.pin),
                  checker_sha256=digest(Path(__file__)),
                  full_finite_checker_sha256=digest(Path(finite.__file__)),
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  elapsed_seconds=time.monotonic()-start,
                  scope='Fresh actual all-column physical F2 scalar replay and real alias-compensation/cleanup mutations, '
                        'both orientations. Source/producer/geometry/prime code and complete paid receipt hashes are bound; '
                        'the complete geometry and unit proof remain the separate finite reconstruction receipt.')
    with args.output.open('x') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
