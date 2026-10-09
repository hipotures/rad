#!/usr/bin/env python3
"""Reproduce explicitly scoped current binary graph and scalar inspections.

This entrypoint does not accept a candidate exponent or moment certificate.
It reads pinned data and imports only independent reviewer functions. GRAPH_ONLY
and SCALAR_ONLY receipts cannot serve as a complete finite construction gate.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import time


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load_pinned(path, expected):
    raw = path.read_bytes()
    if path.name.endswith('.gz'):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == expected, 'pinned input bytes: ' + path.name)
    return json.loads(raw)


def verify_decoder(graph, support):
    v, h, labels = graph['v'], graph['h'], graph['labels']
    need((graph['p'], h, v) == (12, 24, 1760), 'retained graph dimensions')
    need(len(labels) == v and len({tuple(x) for x in labels}) == v,
         'complete distinct source labels')
    target = [0] * v
    stars = [set() for _ in range(v)]
    for root in graph['roots']:
        node = root['node']
        need(type(node) is int and 0 <= node < len(support), 'actual decoder node')
        need(root.get('coefficient', 1) == 1 and len(set(root['targets'])) == len(root['targets']),
             'unit unique decoder receivers')
        if root['kind'] == 'center':
            coordinate = root['coordinate']
            need(type(coordinate) is int and 0 <= coordinate < h, 'actual star coordinate')
            expected = sum(1 << i for i, label in enumerate(labels) if coordinate in label)
            need(support[node] == expected, 'exact copied star support')
        else:
            need(root['kind'] == 'side', 'actual graph root kind')
        for receiver in root['targets']:
            need(type(receiver) is int and 0 <= receiver < v, 'actual decoder receiver')
            target[receiver] ^= support[node]
            if root['kind'] == 'center':
                stars[receiver].add(root['coordinate'])
    members = Counter()
    for item in graph['partner_mix']:
        carrier, passive = item['carrier'], item['passive']
        need(type(carrier) is int and type(passive) is int and
             0 <= carrier < v and 0 <= passive < v and carrier != passive,
             'actual original-source K pair')
        need(len(set(labels[carrier]) & set(labels[passive])) == 1, 'K address intersection')
        members.update((carrier, passive))
        for receiver in item['receivers']:
            need(type(receiver) is int and 0 <= receiver < v, 'actual K receiver')
            target[receiver] ^= (1 << carrier) | (1 << passive)
    need(all(members[i] == 1 for i in range(v)), 'one K pair per source')
    need(all(target[i] == 1 << i and stars[i] == set(labels[i]) for i in range(v)),
         'complete graph decoder over F2')
    return dict(target_rows=v, exact_source_columns_per_row=v, copied_star_supports=True,
                full_original_source_partner_contribution=True)


def inspect_graph(args, pin):
    import independent_binary_inline_inputs as native
    import independent_binary_local_inputs as local
    import independent_binary_third_fusion_inputs as third
    record = pin['graphs'][args.case]
    actual = load_pinned(args.graph, record['graph_sha256'])
    config = record['config']
    mechanism = None
    if record['kind'] == 'local':
        graph, _, _, builder = local.graph_from_source(args.source, config)
        adapter = local
    elif record['kind'] == 'third':
        graph, _, _, builder, mechanism = third.graph_from_source(args.source, config)
        adapter = third
    else:
        need(record['kind'] == 'inline', 'explicit graph inspection kind')
        graph, _, _, builder = native.graph_from_source(args.source, config)
        adapter = native
    need(set(actual) == set(graph) | {'decoder'} and
         all(actual[name] == value for name, value in graph.items()) and
         actual['decoder'] == record['decoder_description'],
         'every actual graph node, label, root and partner contribution')
    decoder = verify_decoder(graph, builder.support)
    wrong = dict(config)
    if record['kind'] == 'local':
        wrong['diagonal_change'] = next(key for key in local.SETS if key != config['diagonal_change'])
        wrong_graph = local.graph_from_source(args.source, wrong)[0]
    elif record['kind'] == 'third':
        wrong_graph = native.graph_from_source(args.source, config)[0]
    else:
        wrong['local_association'] = 'L1' if config['local_association'] == 'L0' else 'L0'
        wrong_graph = native.graph_from_source(args.source, wrong)[0]
    need(wrong_graph['args'] != actual['args'], 'actual wrong producer policy rejected')
    result = dict(status='PASS_GRAPH_ONLY', case=args.case, source_revision=record['source_revision'],
                  config=config, graph_sha256=record['graph_sha256'],
                  nodes=len(graph['args']), roots=len(graph['roots']),
                  every_integer_graph_field_exact=True, decoder=decoder,
                  adapter_sha256=digest(Path(adapter.__file__)),
                  negative_controls=dict(wrong_producer_policy='actual graph arguments differ'),
                  scope='GRAPH_ONLY: complete integer local/module/global graph and defining F2 decoder. '
                        'No carrier/frame/alias/projector/prime/reflected physical/paid histogram/moment/bridge '
                        'or final exponent acceptance is claimed.')
    if mechanism:
        result['mechanism'] = mechanism
    if record['kind'] == 'local':
        result['exact_diagonal_set'] = sorted(builder.diagonals)
    if 'discovery' in record:
        result['author_discovery_not_independently_certified'] = record['discovery']
    return result


def inspect_scalar(args, pin):
    import independent_binary_copy_program as copy
    import independent_binary_lifetime as finite
    files = pin['scalar']['export_sha256']
    read = lambda name: load_pinned(args.export / name, files[name])
    graph, word, partner = [read(name + '_p12.json') for name in ('graph', 'word', 'kchron')]
    # Bind every retained export, although frame and profile hashes are only
    # identities here and are not a frame or paid-ledger proof.
    for name in files:
        read(name)
    clean = copy.bind_values(graph, word)
    events, chronology = copy.emit_scalar_program(graph, word, partner)
    v, roles = chronology['v'], chronology['physical_roles']
    formal = [finite.formal(events, v, roles, reflected=reflected) for reflected in (False, True)]
    compensated = chronology.pop('actual_compensation_events')
    read_positions = chronology.pop('read_positions')
    need(len(compensated) == chronology['aliases'], 'every actual aliased recipient is compensated')
    mutation = list(events)
    original = compensated[next(iter(compensated))]
    mutation.insert(0, mutation.pop(original))
    rejected = {}
    for reflected in (False, True):
        try:
            finite.formal(mutation, v, roles, reflected=reflected)
        except ValueError as error:
            rejected['reverse' if reflected else 'forward'] = str(error)
        else:
            raise ValueError('premature actual compensation mutation survived')
    return dict(status='PASS_SCALAR_ONLY', source_revision=pin['scalar']['source_revision'],
                clean_value_binding=clean, formal=formal, chronology=chronology,
                read_cut_histogram=dict(Counter(read_positions.values())),
                actual_compensated_recipient_count=len(compensated), export_sha256=files,
                scalar_adapter_sha256=digest(Path(copy.__file__)),
                formal_replay_code_sha256=digest(Path(finite.__file__)),
                negative_controls=dict(actual_premature_compensation=rejected),
                scope='SCALAR_ONLY: every clean opcode/root value and actual scalar cut/death/birth/read/K/cleanup '
                      'chronology, all source and arbitrary dirty F2 columns, literal time reversal and bank swap. '
                      'No G-frame, local-ring prime, copied-center physical representative, complemented physical '
                      'execution, paid histogram, moment, bridge or final exponent acceptance is claimed.')


def main():
    need(not sys.flags.optimize, 'assertion-disabled execution rejected')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pin', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    commands = parser.add_subparsers(dest='mode', required=True)
    graph = commands.add_parser('graph')
    graph.add_argument('--case', required=True)
    graph.add_argument('--source', type=Path, required=True)
    graph.add_argument('--graph', type=Path, required=True)
    scalar = commands.add_parser('scalar')
    scalar.add_argument('--export', type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'fresh partial-inspection receipt required')
    started = time.monotonic()
    pin = json.loads(args.pin.read_text())
    code = Path(__file__).parent
    required = {
        'independent_binary_lifetime.py', 'independent_binary_lifetime_inputs.py',
        'binary_exact_algebra.py', 'independent_binary_inline_inputs.py',
        'independent_binary_local_inputs.py', 'independent_binary_third_fusion_inputs.py',
        'independent_binary_copy_program.py',
    }
    need(set(pin['reviewer_dependencies']) == required, 'complete independent inspection code closure')
    for name, expected in pin['reviewer_dependencies'].items():
        need(Path(name).name == name and digest(code / name) == expected,
             'pinned independent reviewer code: ' + name)
    if args.mode == 'graph':
        record = pin['graphs'][args.case]
        for name, expected in pin['sources'][record['source_revision']]['files'].items():
            need(digest(args.source / name) == expected, 'pinned source input: ' + name)
        result = inspect_graph(args, pin)
    else:
        result = inspect_scalar(args, pin)
    result.update(inspection_entrypoint_sha256=digest(Path(__file__)),
                  pin_manifest_sha256=digest(args.pin),
                  reviewer_dependencies=pin['reviewer_dependencies'],
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  elapsed_seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in ('status', 'scope', 'elapsed_seconds')}, indent=2))


if __name__ == '__main__':
    main()
