#!/usr/bin/env python3
"""Per-common-point pair-block order variants with unchanged exact verifiers.

GroupUnion's construction is copied with only its point-order generation
changed. All formal-map methods are inherited from the frozen source. Every
global pair remains a local pair; its deleted common point leaves one mate.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random
import time
from unittest.mock import patch

import finite_block_search as original
from finite_singleton_successor import evaluate_direct
from downstream_parameter_optimum import as_strings


def point_order(h, common, kind, seed):
    pairs = [g for g in range(h//2) if g != common//2]
    if kind == 'canonical':
        pass
    elif kind == 'reverse':
        pairs.reverse()
    elif kind == 'common-reverse':
        if common//2 % 2:
            pairs.reverse()
    elif kind == 'parity':
        pairs = pairs[::2]+pairs[1::2]
    elif kind == 'common-parity':
        parity = common//2 % 2
        pairs = pairs[parity::2]+pairs[1-parity::2]
    elif kind == 'rotate':
        shift = seed % len(pairs)
        pairs = pairs[shift:]+pairs[:shift]
    elif kind == 'common-rotate':
        shift = (seed+common//2) % len(pairs)
        pairs = pairs[shift:]+pairs[:shift]
    elif kind == 'global-permutation':
        pairs = list(range(h//2))
        random.Random(seed).shuffle(pairs)
        pairs.remove(common//2)
    elif kind == 'pair-permutation':
        random.Random(seed+1000003*(common//2)).shuffle(pairs)
    elif kind == 'point-permutation':
        random.Random(seed+1000003*common).shuffle(pairs)
    else:
        raise ValueError(kind)
    points = [vertex for group in pairs for vertex in (2*group, 2*group+1)]+[common ^ 1]
    assert sorted(points) == [v for v in range(h) if v != common]
    return points


class OrderedGroupUnion(original.GroupUnion):
    """Frozen GroupUnion construction with explicit verified point orders."""

    def __init__(self, h, local_factory, ordering='paired', seed=0, common_aware=False,
                 *, block_order_kind='canonical', block_order_seed=0):
        assert h >= 6 and h % 2 == 0 and ordering == 'paired' and common_aware
        self.h = h
        self.inputs = list(combinations(range(h), 3))
        self.variables = {t: i+1 for i, t in enumerate(self.inputs)}
        self.args = [None]*(len(self.inputs)+1)
        self.core = [0]+[sum(1 << i for i in t) for t in self.inputs]
        self.union = list(self.core)
        self.provenance = [None]*len(self.args)
        self.points = [point_order(h, common, block_order_kind, block_order_seed)
                       for common in range(h)]
        self.locals = [local_factory(h-1, common) for common in range(h)]
        self.pair_ids = [{tuple(sorted(points[k] for k in pair)): i+1
                          for i, pair in enumerate(local.inputs)}
                         for points, local in zip(self.points, self.locals)]
        lookup = {}
        self.outputs = {}
        self.merged = 0
        for common in range(h):
            local = self.locals[common]
            local.verify()
            mapping = {}
            for node in sorted(local.active):
                if local.args[node] is None:
                    a, b = local.inputs[node-1]
                    target = tuple(sorted((common, self.points[common][a], self.points[common][b])))
                    mapping[node] = self.variables[target]
                    continue
                a, b = (mapping[x] for x in local.args[node])
                core, union = self.core[a] & self.core[b], self.union[a] | self.union[b]
                assert core & (1 << common)
                key = core, union
                if core.bit_count() >= 2 and key in lookup:
                    mapping[node] = lookup[key]
                    self.merged += 1
                    continue
                new = len(self.args)
                mapping[node] = new
                self.args.append((a, b)); self.core.append(core); self.union.append(union)
                self.provenance.append((common, node))
                if core.bit_count() >= 2:
                    lookup[key] = new
            for pair, node in sorted(local.outputs.items()):
                target = tuple(sorted((common, *(self.points[common][x] for x in pair))))
                self.outputs[common, target] = mapping[node]
        self.active = set()
        stack = list(self.outputs.values())
        while stack:
            node = stack.pop()
            if node in self.active:
                continue
            self.active.add(node)
            if self.args[node]:
                stack.extend(self.args[node])
        self.additions = sum(self.args[node] is not None for node in self.active)


def evaluate_ordered(job):
    kind, seed = job['block_order_kind'], job['block_order_seed']

    def configured(h, factory, ordering, unused_seed, common_aware):
        return OrderedGroupUnion(h, factory, ordering, unused_seed, common_aware,
                                 block_order_kind=kind, block_order_seed=seed)

    # The frozen evaluator also clears GroupUnion.support_in's cache.
    configured.support_in = original.GroupUnion.support_in
    with patch.object(original, 'GroupUnion', configured):
        row = evaluate_direct(job)
    row['block_order_kind'], row['block_order_seed'] = kind, seed
    row['block_order_source_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    row['verification_scope'] += '; inherited exact GroupUnion formal maps and unchanged physical/frame verifiers'
    return row


def identity(h, base, positions, kind, seed):
    data = dict(h=h, base=base, positions=positions, block_order_kind=kind, block_order_seed=seed,
                reference_commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2')
    return data, sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True)
    ap.add_argument('--h', type=int, nargs='+', default=[8, 12])
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    start = time.monotonic(); rows = []
    original.install_reference(args.reference)
    from finite_singleton_search import singleton_class
    from finite_singleton_neighborhood import identity as old_identity
    from singleton_sensitivity import evaluate as old_evaluate
    from frame_reuse_certificate import program
    from dag_network import exact_invocation
    names = [Path(__file__).name, 'finite_block_search.py', 'finite_singleton_successor.py',
             'singleton_sensitivity.py', 'fast_frame_envelope.py', 'frame_envelope.py', 'frame_reuse.py']
    result = dict(campaign_id='20261007T222521Z', source_sha256={name:
        sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
        started_utc=datetime.now(timezone.utc).isoformat(), rows=rows)
    for h in args.h:
        positions = [0]*(h//2-1)+[h//2-2]*(h//2+1)
        positions[-2:] = [0, h//2-1]
        cls = singleton_class(); factory = lambda n, common: cls(n, positions[common], 4)
        baseline = original.GroupUnion(h, factory, 'paired', 0, True)
        exact = OrderedGroupUnion(h, factory, block_order_kind='canonical', common_aware=True)
        for field in ['inputs', 'variables', 'args', 'core', 'union', 'provenance', 'points',
                      'pair_ids', 'outputs', 'active', 'additions', 'merged']:
            assert getattr(baseline, field) == getattr(exact, field), ('Canonical copy mismatch', field)
        kinds = ['canonical', 'reverse', 'common-reverse', 'parity', 'common-parity',
                 'rotate', 'common-rotate', 'global-permutation', 'pair-permutation', 'point-permutation']
        for kind in kinds:
            definition, key = identity(h, 4, positions, kind, 109)
            job = dict(definition, candidate_id=key, reference=args.reference, deadline='2026-10-08T08:25:21+00:00',
                       phase='small-block-order-control', local_cache=True, worker_address_space_gib=6)
            row = evaluate_ordered(job)
            if h == 8 and kind in ('canonical', 'common-rotate', 'pair-permutation'):
                circuit = OrderedGroupUnion(h, factory, block_order_kind=kind, block_order_seed=109, common_aware=True)
                from fast_frame_envelope import labels
                from frame_reuse import compile_reuse, optimize_chains
                frames, _ = labels(circuit, True)
                code = compile_reuse(circuit, frames, optimize_chains(circuit, frames, 'rank'))
                row['dirty_basis'] = [exact_invocation(h, inverse, program(circuit, code)) for inverse in (False, True)]
            rows.append(row)
            result['elapsed_seconds'] = time.monotonic()-start
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')
            print(json.dumps(dict(h=h, kind=kind, roles=row['compiled_roles'])), flush=True)
    result['status'] = 'Terminal PASS'
    result['elapsed_seconds'] = time.monotonic()-start
    args.output.write_text(json.dumps(as_strings(result), indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
