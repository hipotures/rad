#!/usr/bin/env python3
"""Compile scalar regions in their exact reachable-output kernel spaces.

Scalar source: Avi Eisenberg PR62. Invertible binary joint synthesis,
carrier capacities and paid reclamation: eumemic PR57. Unlike a producer
cover enlargement, the new one-core frame is constrained by every ordinary
output reachable in the actual scalar dependency DAG. Original source,
two-core and copied-center frames remain mandatory. No decreasing-frame
operation or restricted ridge-array contract is introduced.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
from check_compiled_witness import contained
from joint_word_check_v4 import check


def original_signed(h, frame):
    core, cover = frame
    if core == cover:
        return (1, core, tuple(int(core >> i & 1) for i in range(h)))
    return (cover.bit_count() - core.bit_count(), core,
            tuple(1 if core >> i & 1 else i + 2 if cover >> i & 1 else 0
                  for i in range(h)))


def future_kernel(h, common, pairs):
    adjacency = [set() for _ in range(h)]
    for a, b in pairs:
        assert a != b and common not in (a, b)
        adjacency[a].add(b)
        adjacency[b].add(a)
    symbols = [0] * h
    symbols[common] = 1
    visited = {common}
    rank = 0
    odd_components = 0
    for first in range(h):
        if first in visited:
            continue
        signs = {first: 1}
        pending = deque([first])
        odd = False
        while pending:
            x = pending.popleft()
            for y in sorted(adjacency[x]):
                if y not in signs:
                    signs[y] = -signs[x]
                    pending.append(y)
                elif signs[y] != -signs[x]:
                    odd = True
        visited.update(signs)
        if odd:
            odd_components += 1
        else:
            rank += 1
            for x, sign in signs.items():
                symbols[x] = sign * (first + 2)
    return (rank, 1 << common, tuple(symbols)), odd_components


def assign(c, blocks, owner, scope, threshold):
    h = c.h
    outgoing = [set() for _ in blocks]
    pairs = [set() for _ in blocks]
    for x in sorted(c.active):
        for y in c.args[x] or ():
            if owner[y] != owner[x]:
                outgoing[owner[y]].add(owner[x])
    for (common, target), x in c.outputs.items():
        if len(target) == 3:
            a, b = sorted(set(target) - {common})
            assert len(set(target)) == 3
            pairs[owner[x]].add((a, b))
    order = sorted(range(len(blocks)), key=lambda g: min(blocks[g]['nodes']), reverse=True)
    for g in order:
        for target in outgoing[g]:
            assert min(blocks[g]['nodes']) < min(blocks[target]['nodes'])
            pairs[g].update(pairs[target])
    ordinary = [original_signed(h, b['frame']) for b in blocks]
    labels = list(ordinary)
    changed = odd = 0
    for g, old in enumerate(ordinary):
        if old[1].bit_count() != 1 or old[0] < threshold:
            continue
        if scope == 'terminal-only' and not any(x in c.outputs.values() for x in blocks[g]['nodes']):
            continue
        common = old[1].bit_length() - 1
        labels[g], n_odd = future_kernel(h, common, pairs[g])
        odd += n_odd
        assert contained(old, labels[g]), ('Original scalar envelope escapes future kernel', g)
        changed += labels[g] != old
    # A partial selection must propagate the enlarged space through all
    # scalar recipients. Full selection already has this property by the
    # reversed union of reachable output constraints.
    pending = deque(g for g in range(len(blocks)) if labels[g] != ordinary[g])
    while pending:
        g = pending.popleft()
        for target in outgoing[g]:
            if contained(labels[g], labels[target]):
                continue
            old = ordinary[target]
            assert old[1].bit_count() == 1
            labels[target], n_odd = future_kernel(h, old[1].bit_length() - 1, pairs[target])
            odd += n_odd
            assert contained(old, labels[target]) and contained(labels[g], labels[target])
            pending.append(target)
    for g, targets in enumerate(outgoing):
        for target in targets:
            assert contained(labels[g], labels[target])
    for (common, target), x in c.outputs.items():
        if len(target) == 1:
            assert labels[owner[x]][0] == h - 1
    return labels, dict(initially_changed_regions=changed,
                       selected_changed_regions=sum(a != b for a, b in zip(labels, ordinary)),
                       odd_component_visits=odd,
                       scalar_dependencies=sum(map(len, outgoing)),
                       reachable_pair_constraints=sum(map(len, pairs)),
                       all_original_envelopes_contained=True,
                       all_scalar_dependencies_contained=True)


def write_word(path, word):
    raw = (json.dumps(word, separators=(',', ':')) + '\n').encode()
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as archive:
            archive.write(raw)
    return sha256(raw).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--parents', type=Path)
    p.add_argument('--small', action='store_true')
    p.add_argument('--h', type=int, nargs='+', default=[23, 25])
    p.add_argument('--scopes', nargs='+', choices=['all', 'terminal-only'], default=['all'])
    p.add_argument('--thresholds', type=int, nargs='+', default=[0])
    p.add_argument('--groupings', nargs='+', choices=['merge-aliases', 'preserve-regions'], default=['merge-aliases'])
    p.add_argument('--carriers', nargs='+', choices=['original', 'large-rise', 'small-rise', 'terminal-first'], default=['original'])
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    (args.work / 'process.json').write_text(json.dumps(dict(pid=__import__('os').getpid(), command=sys.argv,
        started_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    joint.initialize(args.source, args.work)
    if args.small:
        documents = [dict(id='small-h10', h=10, configuration=dict(h=10, policy='baseline', rank_delta=1, sweeps=1, limit=0), Q=list(range(10)))]
    else:
        assert args.parents
        documents = [d for d in json.loads(args.parents.read_text()) if d['h'] in args.h]
    rows = []
    for doc in documents:
        cfg = {k: v for k, v in doc['configuration'].items() if k != 'kind'}
        c, old_blocks, _, _, old_owner, _, _, _ = region.build_regions(doc['h'], cfg)
        scalar = c.verify()
        for scope in args.scopes:
            for threshold in args.thresholds:
                labels, summary = assign(c, old_blocks, old_owner, scope, threshold)
                for grouping in args.groupings:
                    for carrier in args.carriers:
                        case = f"{doc['id']}-future-{scope}-minrank{threshold}-{grouping}-{carrier}"
                        target = args.work / 'raw' / case
                        target.mkdir(parents=True)
                        start = time.monotonic()
                        config = dict(parent=doc, scope=scope, threshold=threshold, grouping=grouping, carrier=carrier)
                        try:
                            region.COMPILER.build = lambda h: joint.build(c, labels, old_owner, grouping, carrier)
                            compiled, word = region.COMPILER.compile_(doc['h'], matching=True, reclaim=True, dirty=True)
                            word = joint.canonicalize(word, doc.get('Q', list(range(doc['h']))))
                            word_path = target / 'word.json.gz'
                            word_sha = write_word(word_path, word)
                            independent = check(word_path, target / 'signed-transitions.bin')
                            result = dict(status='DISCOVERY exact scalar-future signed frames and new joint word PASS',
                                case_id=case, configuration=config, frame_assignment=summary,
                                assignment_sha256=sha256(json.dumps(labels, separators=(',', ':')).encode()).hexdigest(),
                                scalar=scalar, compiled=compiled, independent=independent,
                                old_regions=len(old_blocks), new_regions=compiled['stats']['regions'],
                                word_path=str(word_path), word_sha256=word_sha)
                        except Exception as error:
                            result = dict(status='REJECTED future-frame compiler configuration', case_id=case,
                                          configuration=config, error=repr(error), frame_assignment=summary)
                        result.update(seconds=time.monotonic()-start, source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
                            completed_utc=datetime.now(timezone.utc).isoformat(),
                            source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                            limitations='Finite scalar and actual-word discovery. Complete actual matrix CRT, source-pair DATA, stock, moments, assembly and inherited all-size address/tape transfer are separate gates.')
                        (target / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
                        rows.append(result)
                        args.output.parent.mkdir(parents=True, exist_ok=True)
                        args.output.write_text(json.dumps(dict(status='running', command=sys.argv, rows=rows), indent=2) + '\n')
                        print(json.dumps(dict(case_id=case, status=result['status'], R=result.get('compiled', {}).get('roles'),
                                             regions=result.get('new_regions'), error=result.get('error'))), flush=True)
    args.output.write_text(json.dumps(dict(status='complete', command=sys.argv, rows=rows,
        completed_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')


if __name__ == '__main__':
    main()
