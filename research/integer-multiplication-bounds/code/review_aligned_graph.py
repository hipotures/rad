#!/usr/bin/env python3
"""Independent dense support expansion of the aligned common-point graph.

This checker reads only graph arguments, physical input triples, and output
labels. It does not use provenance support lookups or the builder's support
verifier. All global coefficients are reconstructed from those arguments.
"""

import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import resource
import sys
import time


def check(graph):
    begin = time.monotonic()
    inputs = list(graph.inputs)
    index = {triple: i for i, triple in enumerate(inputs)}
    masks = [0] + [1 << i for i in range(len(inputs))]
    cores = [0] + [sum(1 << x for x in triple) for triple in inputs]
    digest = sha256()
    additions = 0
    for node in range(len(masks), len(graph.args)):
        a, b = graph.args[node]
        assert 0 < a < node and 0 < b < node
        assert not masks[a] & masks[b], (node, 'overlapping inputs')
        masks.append(masks[a] | masks[b])
        cores.append(cores[a] & cores[b])
        assert cores[node], (node, 'no common point')
        if node in graph.active:
            additions += 1
            digest.update(json.dumps((node, a, b), separators=(',', ':')).encode() + b'\n')
    nonzero = 0
    for (common, target), node in sorted(graph.outputs.items()):
        assert common in target
        survivors = [x for x in range(graph.h) if x not in target]
        expected = sum(1 << index[tuple(sorted((common, a, b)))]
                       for a, b in combinations(survivors, 2))
        assert masks[node] == expected, (common, target, 'wrong coefficient map')
        nonzero += expected.bit_count()
        digest.update(json.dumps((common, target, node), separators=(',', ':')).encode() + b'\n')
    assert additions == graph.additions
    return dict(h=graph.h, additions=additions, outputs=len(graph.outputs),
                roles=additions + len(graph.outputs),
                all_global_coefficients_exact=True, all_additions_disjoint=True,
                all_source_spans_have_common_point=True,
                nonzero_partial_coefficients=nonzero,
                independent_graph_digest=digest.hexdigest(),
                wall_seconds=time.monotonic() - begin,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--h', type=int, default=50)
    parser.add_argument('--ordering', default='paired')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    from finite_block_search import install_reference, make_block_class, GroupUnion
    install_reference(str(args.reference))
    cls = make_block_class()
    graph = GroupUnion(args.h, lambda n: cls(n, (2,), 4, 0), args.ordering, 109)
    result = check(graph)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
