#!/usr/bin/env python3
"""Independent single-channel L1 association variants on the current producer.

Only the explicit three requested diagonal-set changes are admitted. Each
channel's exact integer support is checked. Full carrier/frame reconstruction
uses immutable reviewer code, not a saved candidate verdict or upstream code.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

import independent_binary_inline_inputs as native
import independent_binary_lifetime_inputs as inherited
from binary_exact_algebra import need

# The immutable finite core invokes these only for its real negative controls.
verify_pair_module = inherited.verify_pair_module
verify_compiler = inherited.verify_compiler


BASE = frozenset({(0, 1, 0), (0, 1, 1), (1, 2, 1)})
SETS = {
    'remove01_0': BASE - {(0, 1, 0)},
    'remove01_1': BASE - {(0, 1, 1)},
    'add02_0': BASE | {(0, 2, 0)},
}


class LocalBuilder(native.InlineBuilder):
    def __init__(self, p, change):
        super().__init__(p)
        need(change in SETS, 'explicit single-channel association change')
        self.diagonals = SETS[change]

    def local_channels(self, policy):
        need(policy == 'L1', 'native L1 channel order retained')
        for cube in self.cubes:
            def address(fixed):
                selectors = [0, 0, 0]
                for position, value in fixed.items():
                    selectors[position] = value
                return self.address[cube, tuple(selectors)]

            def edge(free, fixed):
                return self.add(address({**fixed, free: 0}), address({**fixed, free: 1}))

            for j, k in combinations(range(3), 2):
                free = 3-j-k
                for mode in range(2):
                    if (j, k, mode) in self.diagonals:
                        a = self.add(address({j: 0, k: mode, free: 0}), address({j: 1, k: 1-mode, free: 1}))
                        b = self.add(address({j: 0, k: mode, free: 1}), address({j: 1, k: 1-mode, free: 0}))
                        node = self.add(a, b)
                    else:
                        node = self.add(edge(free, {j: 0, k: mode}), edge(free, {j: 1, k: 1-mode}))
                    self.edges[cube, cube[j], cube[k], mode] = node
                    expected = sum(1 << self.address[cube, s] for s in self.selectors if s[j] ^ s[k] == mode)
                    need(self.support[node] == expected, 'every reassociated G channel has exact four-leaf support')
            for i in range(3):
                j, k = [q for q in range(3) if q != i]
                for bit in range(2):
                    node = self.add(edge(k, {i: bit, j: 0}), edge(k, {i: bit, j: 1}))
                    self.faces[cube, cube[i], bit] = node
                    expected = sum(1 << self.address[cube, s] for s in self.selectors if s[i] == bit)
                    need(self.support[node] == expected, 'every retained face channel has exact four-leaf support')


def graph_from_source(source, config):
    need(config.get('local_association') == 'L1' and config.get('broadcast_pairing') is False,
         'native inline L1 output policy retained')
    path = Path(source) / 'research/paired-cube-bit/data/pair_module_p12.json'
    pair = json.loads(path.read_text())
    inherited.verify_pair_module(pair, 12)
    allbut = inherited.nested_prefix(10, config.get('all_but_one', 'nested_prefix'))
    builder = LocalBuilder(12, config['diagonal_change'])
    graph = builder.build(pair, allbut, local='L1', broadcast_pairing=False)
    return graph, pair, allbut, builder


def verify_inputs(source, context, config):
    started = time.monotonic()
    graph, pair, allbut, builder = graph_from_source(source, config)
    g, w = context['g'], context['w']
    need(all(g[name] == value for name, value in graph.items()), 'complete changed local-module/global graph')
    need(config.get('require_source_arcs') is False, 'changed local graph requires its fresh pinned matching')
    compiler = inherited.verify_compiler(g, w, context['nf'], context['root_frames'], config.get('plain_threshold', 8))
    need(compiler['compact_remaining_internal_histogram'] ==
         {int(r): n for r, n in context['supplied_profile']['remaining_internal_histogram'].items() if n},
         'complete changed compact scalar ledger')
    target_hist = Counter()
    current = [()] * g['v']
    for item in reversed(w['gauges']):
        for target in item['targets']:
            cap = context['frames'][item['frame']]
            need(all(inherited.dot(a, b) == 0 for a in cap.A for b in current[target]), 'original compact gauge target chronology')
            target_hist[cap.dim-len(current[target])] += 1
            current[target] = cap.B
    for root, cap in zip(g['roots'], context['root_frames']):
        if root['kind'] != 'center':
            for target in root['targets']:
                need(all(inherited.dot(a, b) == 0 for a in cap.A for b in current[target]), 'compact root target chronology')
                target_hist[cap.dim-len(current[target])] += 1
                current[target] = cap.B
    for target in range(g['v']):
        target_hist[g['h']-1-len(current[target])] += 1
    need(dict(target_hist) == {int(r): n for r, n in context['supplied_profile']['target_data_histogram'].items() if n},
         'complete changed compact target ledger')
    compiler['compact_target_histogram'] = {r: n for r, n in sorted(target_hist.items()) if n}
    return dict(local_association='L1', diagonal_change=config['diagonal_change'],
                exact_diagonal_set=sorted(builder.diagonals), all_four_leaf_channel_supports_verified=True,
                native_inline_output_order=True, pair_module_all_roots_exact=True,
                all_but_one_all_roots_exact=True,
                rebuilt_graph_semantic_sha256=sha256(json.dumps(graph, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                compiler=compiler, elapsed_seconds=time.monotonic()-started,
                scope='Fresh complete integer graph and native carrier/padding/frame reconstruction for one explicit '
                      'local reassociation. Actual physical compensation, reflection and prime units are separate.')
