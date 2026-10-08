#!/usr/bin/env python3
"""Prune controller-flow vertices with no admissible-link incidence.

The original optimizer is untouched. Source-use descriptions and candidate
links are identical. The compressed network retains precisely the gate
groups, outgoing ports and incoming ports occurring in some candidate link.
Its minimum cut independently certifies the maximum selected cardinality.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import gc
import json
from pathlib import Path
import resource
import sys
import time


def optimize_chains(circuit, spaces, schedule='rank'):
    import numpy as np
    from scipy.sparse import coo_array
    from scipy.sparse.csgraph import breadth_first_order, maximum_flow
    from frame_reuse import included

    start = time.monotonic()
    marks = {}
    order = sorted(circuit.active, key=(lambda node: (spaces[node].dimension, node))
                   if schedule == 'rank' else None)
    positions = {node: i for i, node in enumerate(order)}
    users = {node: [] for node in order}
    descriptions = []
    gate_order = {}
    for node in order:
        if circuit.args[node]:
            assert all(positions[child] < positions[node] for child in circuit.args[node])
            gate_order[node] = len(gate_order)
            for position, child in enumerate(circuit.args[node]):
                users[child].append(len(descriptions))
                descriptions.append((child, node, position))
    for target, node in sorted(circuit.outputs.items()):
        users[node].append(len(descriptions))
        descriptions.append((node, None, target))
    marks['source_use_descriptions'] = time.monotonic()-start

    at = time.monotonic()
    links = []
    for node, outgoing in users.items():
        for index, first in enumerate(outgoing):
            _, previous, _ = descriptions[first]
            if previous is None:
                continue
            for second in outgoing[index+1:]:
                _, following, _ = descriptions[second]
                frame = spaces[following if following is not None else node]
                if included(spaces[previous], frame):
                    links.append((first, second))
    marks['admissible_link_enumeration'] = time.monotonic()-at

    at = time.monotonic()
    # Preserve relative old vertex order. This can preserve Dinic tie
    # choices, but witness validity and the optimum need only equal value.
    first_ports = sorted({first for first, _ in links})
    second_ports = sorted({second for _, second in links})
    groups = sorted({descriptions[first][1] for first in first_ports}, key=gate_order.__getitem__)
    group_base = 2
    out_base = group_base+len(groups)
    in_base = out_base+len(first_ports)
    dimension = in_base+len(second_ports)
    group_ids = {node:group_base+i for i, node in enumerate(groups)}
    outgoing_ids = {user:out_base+i for i, user in enumerate(first_ports)}
    incoming_ids = {user:in_base+i for i, user in enumerate(second_ports)}
    rows, cols = [], []

    def connect(u, v):
        rows.append(u)
        cols.append(v)

    for node in groups:
        connect(0, group_ids[node])
    for first in first_ports:
        connect(group_ids[descriptions[first][1]], outgoing_ids[first])
    for second in second_ports:
        connect(incoming_ids[second], 1)
    for first, second in links:
        connect(outgoing_ids[first], incoming_ids[second])
    graph = coo_array((np.ones(len(rows), dtype=np.int32),
                      (np.asarray(rows, dtype=np.int32), np.asarray(cols, dtype=np.int32))),
                     shape=(dimension, dimension)).tocsr()
    marks['compressed_sparse_construction'] = time.monotonic()-at

    at = time.monotonic()
    flow = maximum_flow(graph, 0, 1, method='dinic')
    marks['maximum_flow'] = time.monotonic()-at
    at = time.monotonic()
    sparse = flow.flow.tocoo()
    successor, predecessor = {}, {}
    for row, col, value in zip(sparse.row, sparse.col, sparse.data):
        if value > 0 and out_base <= row < in_base and in_base <= col < dimension:
            first, second = first_ports[int(row-out_base)], second_ports[int(col-in_base)]
            assert first not in successor and second not in predecessor
            successor[first], predecessor[second] = second, first
    assert len(successor) == flow.flow_value
    retained_gates = set()
    for first, second in successor.items():
        node, previous, _ = descriptions[first]
        node2, following, _ = descriptions[second]
        assert node == node2 and first < second and previous is not None
        assert previous not in retained_gates
        retained_gates.add(previous)
        assert included(spaces[previous], spaces[following if following is not None else node])

    residual = graph-flow.flow
    assert np.all(residual.data >= 0)
    residual.eliminate_zeros()
    reached = np.zeros(dimension, dtype=bool)
    reached[breadth_first_order(residual, 0, directed=True, return_predecessors=False)] = True
    assert reached[0] and not reached[1]
    edges = graph.tocoo()
    cut_value = int(edges.data[reached[edges.row] & ~reached[edges.col]].sum(dtype=np.int64))
    assert cut_value == flow.flow_value
    marks['selection_and_minimum_cut_audit'] = time.monotonic()-at
    count = len(descriptions)
    summary = dict(candidate_links=len(links), selected_links=len(successor),
                   flow_value=int(flow.flow_value), flow_vertices=dimension, flow_edges=len(rows),
                   original_flow_vertices=2+len(gate_order)+2*count,
                   original_flow_edges=len(gate_order)+count+2*circuit.additions+len(links),
                   retained_gate_groups=len(groups), retained_outgoing_ports=len(first_ports),
                   retained_incoming_ports=len(second_ports), schedule=schedule,
                   minimum_cut_capacity=cut_value, independent_cut_equals_selected_links=True,
                   phase_seconds=marks,
                   scope='Same fixed-DAG and topological controller-chain optimum after deleting vertices on no admissible-link path')
    return users, descriptions, successor, predecessor, summary


def benchmark(reference, h, positions, base, label_implementation, expected=None):
    from finite_block_search import GroupUnion
    from finite_singleton_search import singleton_class
    from singleton_sensitivity import VerifiedLocal
    from frame_reuse import compile_reuse, check, included, optimize_chains as old_optimize
    from frame_envelope import target_check
    from frame_reuse_certificate import program
    from review_singleton_positions import plan_check
    from review_singleton_witness import physical_coefficients
    from review_envelopes import graph_envelope_check
    from review_aligned_graph import check as independent_logical
    from review_frame_reuse import dirty_check
    if label_implementation == 'direct':
        from fast_frame_envelope import labels
    else:
        from frame_envelope import labels
    start = time.monotonic()
    phases = {}
    cls = singleton_class()
    cache = {}
    counters = dict(builds=0, hits=0)

    def factory(n, common):
        key = n, positions[common], base
        if key not in cache:
            cache[key] = VerifiedLocal(cls(n, positions[common], base))
            counters['builds'] += 1
        else:
            counters['hits'] += 1
        return cache[key]

    at = time.monotonic()
    circuit = GroupUnion(h, factory, 'paired', 0, True)
    phases['construction_with_verified_local_cache'] = time.monotonic()-at
    at = time.monotonic(); original = circuit.verify()
    phases['unchanged_global_map_check'] = time.monotonic()-at
    at = time.monotonic(); frames, metadata = labels(circuit, True)
    phases['labels'] = time.monotonic()-at

    included.cache_clear()
    at = time.monotonic(); old_plan = old_optimize(circuit, frames, 'rank')
    phases['old_flow_cold_inclusion_cache'] = time.monotonic()-at
    old_selected = dict(old_plan[2])
    old_summary = old_plan[-1]
    old_code = compile_reuse(circuit, frames, old_plan)
    at = time.monotonic(); old_verified = check(circuit, frames, old_code)
    phases['old_unchanged_physical_check'] = time.monotonic()-at
    old_roles = old_code['roles']
    del old_plan, old_code
    gc.collect()

    included.cache_clear()
    at = time.monotonic(); new_plan = optimize_chains(circuit, frames, 'rank')
    phases['compressed_flow_cold_inclusion_cache'] = time.monotonic()-at
    chain = plan_check(circuit, frames, new_plan)
    identical = new_plan[2] == old_selected
    assert new_plan[-1]['selected_links'] == old_summary['selected_links']
    assert new_plan[-1]['candidate_links'] == old_summary['candidate_links']
    code = compile_reuse(circuit, frames, new_plan)
    assert code['roles'] == old_roles == chain['independently_counted_roles']
    at = time.monotonic(); verified = check(circuit, frames, code)
    phases['new_unchanged_physical_check'] = time.monotonic()-at
    targets = target_check(circuit, frames, True)
    at = time.monotonic(); independent_physical = physical_coefficients(circuit, code)
    independent_frames = graph_envelope_check(circuit, frames, code, dense=h <= 12)
    phases['independent_physical_and_envelope_checks'] = time.monotonic()-at
    small = None
    if h <= 12:
        small = dict(logical=independent_logical(circuit), dirty=dirty_check(circuit, frames, code))
    if expected is not None:
        assert original['circuit_sha256'] == expected['original']['circuit_sha256']
        assert old_roles == expected['compiled_roles']
        assert old_verified['compiled_sha256'] == expected['checked']['compiled_sha256']
    result = dict(h=h, base=base, positions=positions, roles=old_roles,
                  local_cache=counters, label_implementation=label_implementation,
                  old_flow=old_summary, compressed_flow=new_plan[-1],
                  old_physical_check=old_verified, compressed_physical_check=verified,
                  old_and_compressed_selected_links_identical=identical,
                  compiled_hash_identical=old_verified['compiled_sha256'] == verified['compiled_sha256'],
                  unchanged_global_map=original, targets=targets, frame_metadata=metadata,
                  independent_physical=independent_physical, independent_frames=independent_frames,
                  independent_chain=chain, small_control=small, phase_seconds=phases,
                  wall_seconds=time.monotonic()-start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print('PASS compressed flow', h, 'roles', old_roles,
          'vertices', old_summary['flow_vertices'], '->', new_plan[-1]['flow_vertices'], flush=True)
    included.cache_clear(); GroupUnion.support_in.cache_clear()
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--h', nargs='+', type=int, default=[8, 12])
    ap.add_argument('--candidate', type=Path)
    ap.add_argument('--labels', choices=['direct', 'original'], default='direct')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh result path'
    from finite_block_search import install_reference
    install_reference(str(args.reference))
    # Keep dependency initialization outside both compared flow timers.
    # The first small v1 baseline included SciPy's first import; that
    # positive control is retained but excluded from speed claims.
    import numpy
    from scipy.sparse.csgraph import breadth_first_order, maximum_flow
    started = datetime.now(timezone.utc).isoformat()
    rows = []
    if args.candidate:
        expected = json.loads(args.candidate.read_text())
        rows.append(benchmark(args.reference, expected['h'], expected['positions'],
                              expected['base'], args.labels, expected=expected))
    else:
        for h in args.h:
            assert h >= 6 and h % 2 == 0
            positions = [((i*7+3) % (h//2)) for i in range(h)]
            rows.append(benchmark(args.reference, h, positions, 4, args.labels))
    dependencies = ('review_compressed_flow.py', 'frame_reuse.py', 'frame_envelope.py',
                    'fast_frame_envelope.py', 'finite_block_search.py', 'finite_singleton_search.py',
                    'singleton_sensitivity.py', 'review_singleton_positions.py',
                    'review_singleton_witness.py', 'review_envelopes.py', 'review_frame_reuse.py')
    result = dict(status='PASS', started_utc=started,
                  completed_utc=datetime.now(timezone.utc).isoformat(), rows=rows,
                  source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                 for name in dependencies},
                  candidate_sha256=sha256(args.candidate.read_bytes()).hexdigest() if args.candidate else None,
                  python_version=sys.version,
                  scope='Performance experiment preserving all finite verifiers and fixed-graph maximum link count; no new integer multiplication exponent')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
