#!/usr/bin/env python3
"""Explicit independent PR168 inline-output and L1 producer adapter.

The frozen previous reviewer supplies integer module checks, builder primitives
and carrier reconstruction, not a verdict. This file independently specifies
the changed local associations and native inline output order. No upstream
producer code is imported. Full finite geometry and execution are separate.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import time

import independent_binary_lifetime_inputs as inherited
from binary_exact_algebra import need


L1_DIAGONALS = {(0, 1, 0), (0, 1, 1), (1, 2, 1)}


class InlineBuilder(inherited.Builder):
    def local_channels(self, policy):
        need(policy in ('L0', 'L1'), 'explicit local association policy')
        for cube in self.cubes:
            def address(fixed):
                selectors = [0, 0, 0]
                for position, value in fixed.items():
                    selectors[position] = value
                return self.address[cube, tuple(selectors)]

            def edge(free, fixed):
                return self.add(address({**fixed, free: 0}),
                                address({**fixed, free: 1}))

            if policy == 'L0':
                edges = {}
                for i, j in combinations(range(3), 2):
                    free = 3-i-j
                    for a, b in product(range(2), repeat=2):
                        edges[i, j, a, b] = edge(free, {i: a, j: b})
                    self.edges[cube, cube[i], cube[j], 0] = self.add(edges[i, j, 0, 0], edges[i, j, 1, 1])
                    self.edges[cube, cube[i], cube[j], 1] = self.add(edges[i, j, 0, 1], edges[i, j, 1, 0])
                for i in range(3):
                    j = next(x for x in range(3) if x != i)
                    for a in range(2):
                        ports = [edges[i, j, a, b] if i < j else edges[j, i, b, a] for b in range(2)]
                        self.faces[cube, cube[i], a] = self.add(*ports)
            else:
                for j, k in combinations(range(3), 2):
                    free = 3-j-k
                    for mode in range(2):
                        if (j, k, mode) in L1_DIAGONALS:
                            first = self.add(address({j: 0, k: mode, free: 0}),
                                             address({j: 1, k: 1-mode, free: 1}))
                            second = self.add(address({j: 0, k: mode, free: 1}),
                                              address({j: 1, k: 1-mode, free: 0}))
                            node = self.add(first, second)
                        else:
                            node = self.add(edge(free, {j: 0, k: mode}), edge(free, {j: 1, k: 1-mode}))
                        self.edges[cube, cube[j], cube[k], mode] = node
                for i in range(3):
                    j, k = [position for position in range(3) if position != i]
                    for a in range(2):
                        self.faces[cube, cube[i], a] = self.add(edge(k, {i: a, j: 0}), edge(k, {i: a, j: 1}))
            # Prove the integer support, separately from its association/order.
            for j, k in combinations(range(3), 2):
                for mode in range(2):
                    expected = sum(1 << self.address[cube, s] for s in self.selectors if s[j] ^ s[k] == mode)
                    need(self.support[self.edges[cube, cube[j], cube[k], mode]] == expected,
                         'complete local parity-channel integer support')
            for i in range(3):
                for a in range(2):
                    expected = sum(1 << self.address[cube, s] for s in self.selectors if s[i] == a)
                    need(self.support[self.faces[cube, cube[i], a]] == expected,
                         'complete local face-channel integer support')

    def build(self, pair, allbut, *, local='L0', broadcast_pairing=False):
        need(type(broadcast_pairing) is bool, 'explicit broadcast-fusion switch')
        self.local_channels(local)
        P, Q = {}, {}
        for i in range(self.p):
            opposite = list(combinations([x for x in range(self.p) if x != i], 2))
            for bit in range(2):
                values = [self.faces[tuple(sorted((i, *K))), i, bit] for K in opposite]
                for K, node in zip(opposite, self.instantiate(pair, values)):
                    P[tuple(sorted((i, *K))), i, bit] = node
        for i, j in combinations(range(self.p), 2):
            others = [x for x in range(self.p) if x not in (i, j)]
            for mode in range(2):
                values = [self.edges[tuple(sorted((i, j, k))), i, j, mode] for k in others]
                for k, node in zip(others, self.instantiate(allbut, values)):
                    Q[tuple(sorted((i, j, k))), i, j, mode] = node

        def emit(cube, selectors, node, channel):
            self.roots.append(dict(node=node, targets=[self.address[cube, s] for s in selectors],
                                   kind='side', channel=channel, coefficient=1))

        for cube in self.cubes:
            if broadcast_pairing:
                for a in range(2):
                    for parity in range(2):
                        node = self.add(P[cube, cube[0], a], Q[cube, cube[1], cube[2], 1-parity])
                        emit(cube, [s for s in self.selectors if s[0] == a and s[1] ^ s[2] == parity],
                             node, 'face0+edge12')
            else:
                for a in range(2):
                    emit(cube, [s for s in self.selectors if s[0] == a], P[cube, cube[0], a], 'face0')
                for a in range(2):
                    for parity in range(2):
                        emit(cube, [s for s in self.selectors if s[0] == a and s[1] ^ s[2] == parity],
                             Q[cube, cube[1], cube[2], 1-parity], 'edge12')
            # Native PR168 order: all four u nodes, all four w nodes, then
            # interleaved singleton u, w and partner reads within this cube.
            u = {(a, b): self.add(P[cube, cube[1], b], Q[cube, cube[0], cube[1], 1-(a ^ b)])
                 for a in range(2) for b in range(2)}
            w = {(a, b): self.add(P[cube, cube[2], b], Q[cube, cube[0], cube[2], 1-(a ^ b)])
                 for a in range(2) for b in range(2)}
            for s in self.selectors:
                emit(cube, [s], u[s[0], s[1]], 'u01')
                emit(cube, [s], w[s[0], s[2]], 'w02')
                emit(cube, [s], self.address[cube, (s[0], 1-s[1], 1-s[2])], 'partner')
            for parity in range(2):
                for first in range(2):
                    sources = sorted(s for s in self.selectors if sum(s) % 2 == parity and s[0] == first)
                    targets = sorted(s for s in self.selectors if sum(s) % 2 == parity and s[0] != first)
                    self.mix.append(dict(carrier=self.address[cube, sources[0]], passive=self.address[cube, sources[1]],
                                         receivers=[self.address[cube, s] for s in targets]))
        for coordinate in range(2*self.p):
            i, bit = divmod(coordinate, 2)
            node = self.balanced_sum(self.faces[cube, i, bit] for cube in self.cubes if i in cube)
            self.roots.append(dict(node=node, targets=[t for t, label in enumerate(self.labels) if coordinate in label],
                                   kind='center', coordinate=coordinate, coefficient=1))
        return dict(p=self.p, h=2*self.p, v=len(self.labels), labels=self.labels,
                    args=self.args, roots=self.roots, partner_mix=self.mix)


def graph_from_source(source, config):
    directory = Path(source) / 'research/paired-cube-bit/data'
    pair = json.loads((directory / 'pair_module_p12.json').read_text())
    inherited.verify_pair_module(pair, 12)
    policy = config.get('all_but_one', 'nested_prefix')
    allbut = inherited.nested_prefix(10, policy)
    builder = InlineBuilder(12)
    graph = builder.build(pair, allbut, local=config.get('local_association', 'L0'),
                          broadcast_pairing=config.get('broadcast_pairing', False))
    return graph, pair, allbut, builder


def verify_inputs(source, context, config):
    started = time.monotonic()
    graph, pair, allbut, builder = graph_from_source(source, config)
    g, w = context['g'], context['w']
    need(all(g[name] == value for name, value in graph.items()), 'whole inline/local-association producer graph')
    if config.get('require_source_arcs', True):
        arcs = json.loads((Path(source) / 'research/paired-cube-bit/data/arcs_p12.json').read_text())
        need(w['arcs'] == arcs, 'new frozen source matching arcs')
    compiler = inherited.verify_compiler(g, w, context['nf'], context['root_frames'], config.get('plain_threshold', 8))
    need(compiler['compact_remaining_internal_histogram'] ==
         {int(r): n for r, n in context['supplied_profile']['remaining_internal_histogram'].items() if n},
         'fresh complete compact carrier profile including zero-rank terms')
    target_hist = Counter()
    current = [()] * g['v']

    def read(target, cap):
        need(all(inherited.dot(a, b) == 0 for a in cap.A for b in current[target]), 'fresh compact target chronology')
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
         'fresh complete compact target profile including zero-rank terms')
    compiler['compact_target_histogram'] = {r: n for r, n in sorted(target_hist.items()) if n}
    return dict(local_association=config.get('local_association', 'L0'),
                broadcast_pairing=config.get('broadcast_pairing', False),
                native_inline_fusions=True,
                pair_module_additions=len(pair['args'])-pair['input_count'],
                pair_module_all_roots_exact=True,
                all_but_one_policy=config.get('all_but_one', 'nested_prefix'),
                all_but_one_additions=len(allbut['args'])-allbut['input_count'],
                rebuilt_graph_semantic_sha256=sha256(json.dumps(graph, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                compiler=compiler, elapsed_seconds=time.monotonic()-started,
                scope='Fresh exact integer modules/local channels/inline fusions, every graph node/root/partner label, '
                      'and complete carrier/matching/frame chronology. Physical execution and prime gates are separate.')
