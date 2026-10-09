#!/usr/bin/env python3
"""Independent post-native face0/edge12 fusion and fresh carrier adapter.

This reconstructs the specific third output-family experiment. The native
inline/L1 graph is independently rebuilt first. New pair sums are appended to
its completed graph and replace the appropriate readouts in their original
root order. Neither a saved profile nor discovery Python defines the graph.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import time

import independent_binary_inline_inputs as native
import independent_binary_lifetime_inputs as inherited
from binary_exact_algebra import need


def fuse_broadcast_pairs(graph, builder):
    faces = [root for root in graph['roots'] if root.get('channel') == 'face0']
    need(len(faces) == 440 and all(len(root['targets']) == 4 for root in faces),
         'complete native four-target face0 family')
    by_target = {}
    for face in faces:
        for target in face['targets']:
            need(target not in by_target, 'one face0 contribution per target')
            by_target[target] = face
    need(set(by_target) == set(range(graph['v'])), 'all face0 receivers covered')
    roots, receiver_count, occurrences = [], 0, Counter()
    nodes_before = len(builder.args)
    for root in graph['roots']:
        channel = root.get('channel')
        if channel == 'face0':
            continue
        if channel == 'edge12':
            targets = root['targets']
            need(len(targets) == 2 and targets[0] != targets[1], 'actual receiver pair')
            first, second = (by_target[target] for target in targets)
            need(first is second and set(targets) < set(first['targets']), 'unique face0 over the receiver pair')
            a, b = first['node'], root['node']
            need(not builder.support[a] & builder.support[b], 'third-fusion exact disjoint operands')
            node = builder.add(a, b)
            need(builder.support[node] == builder.support[a] ^ builder.support[b], 'actual paired scalar sum')
            root = dict(root, node=node, channel='face0-edge12')
            occurrences.update(targets)
            receiver_count += 1
        roots.append(root)
    need(receiver_count == 880 and all(occurrences[t] == 1 for t in range(graph['v'])),
         'every face0/edge12 contribution retained once per receiver')
    result = dict(graph, args=builder.args, roots=roots)
    need(result['partner_mix'] == graph['partner_mix'], 'complete original-source mixer retained')
    return result, dict(receiver_pairs=receiver_count, removed_face0_roots=len(faces),
                        added_nodes=len(builder.args)-nodes_before,
                        root_order='Original native root order with face0 omitted and edge12 replaced in place; '
                                   'new disjoint sum nodes appended after the complete native graph.',
                        partner_delivery='Same receiver pair, with fresh actual root indices.')


def graph_from_source(source, config):
    need(config.get('local_association') == 'L1' and config.get('broadcast_pairing') is False,
         'explicit current native L1 base before post-fusion')
    graph, pair, allbut, builder = native.graph_from_source(source, config)
    fused, mechanism = fuse_broadcast_pairs(graph, builder)
    return fused, pair, allbut, builder, mechanism


def verify_inputs(source, context, config):
    started = time.monotonic()
    graph, pair, allbut, builder, mechanism = graph_from_source(source, config)
    g, w = context['g'], context['w']
    need(all(g[name] == value for name, value in graph.items()), 'whole independently rebuilt third-fusion graph')
    need(config.get('require_source_arcs') is False, 'new graph requires its own pinned carrier matching')
    compiler = inherited.verify_compiler(g, w, context['nf'], context['root_frames'], config.get('plain_threshold', 8))
    need(compiler['compact_remaining_internal_histogram'] ==
         {int(r): n for r, n in context['supplied_profile']['remaining_internal_histogram'].items() if n},
         'complete fresh carrier ledger including rank-zero terms')
    target_hist = Counter()
    current = [()] * g['v']

    def read(target, cap):
        need(all(inherited.dot(a, b) == 0 for a in cap.A for b in current[target]), 'fresh target-chain chronology')
        target_hist[cap.dim-len(current[target])] += 1
        current[target] = cap.B

    for item in reversed(w['gauges']):
        for target in item['targets']:
            read(target, context['frames'][item['frame']])
    for root, cap in zip(g['roots'], context['root_frames']):
        if root['kind'] != 'center':
            for target in root['targets']:
                read(target, cap)
    for target in range(g['v']):
        target_hist[g['h']-1-len(current[target])] += 1
    need(dict(target_hist) == {int(r): n for r, n in context['supplied_profile']['target_data_histogram'].items() if n},
         'complete fresh target ledger including rank-zero terms')
    compiler['compact_target_histogram'] = {r: n for r, n in sorted(target_hist.items()) if n}
    return dict(local_association='L1', native_inline_fusions=True, post_native_broadcast_fusion=mechanism,
                pair_module_additions=len(pair['args'])-pair['input_count'], pair_module_all_roots_exact=True,
                all_but_one_policy=config.get('all_but_one', 'nested_prefix'),
                all_but_one_additions=len(allbut['args'])-allbut['input_count'],
                rebuilt_graph_semantic_sha256=sha256(json.dumps(graph, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                compiler=compiler, elapsed_seconds=time.monotonic()-started,
                scope='Fresh independent exact local/module/global graph, post-native output fusion, '
                      'complete carriers/arcs/padding/spliced/plain frames and scalar source/root assignments. '
                      'Physical aliases, reflected execution and prime units are separate finite gates.')
