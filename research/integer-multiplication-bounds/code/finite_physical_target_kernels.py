#!/usr/bin/env python3
"""Nondegenerate kernels of physically common descendant target spans.

An output's designated common point is not necessarily the only point
shared by its physical target family. This construction uses any actual
shared point. It propagates canonical target-span bases backwards through
the DAG, so no full triple-support bitset is required at ground50.
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

from finite_adaptive_complements import (Complement, included, target_span,
    target_check, frame_reuse_included, orthogonal_envelope_to_targets)
from finite_adaptive_cores import required_cores
from finite_block_search import GroupUnion, install_reference
from finite_label_milp import solve
from finite_schedule_search import reordered
from finite_singleton_search import singleton_class
from frame_envelope import labels as envelope_labels
import frame_reuse


def physical_intersections(circuit):
    full = (1 << circuit.h)-1
    result = {node:full for node in circuit.active}
    for (_, target), node in circuit.outputs.items():
        result[node] &= sum(1 << vertex for vertex in target)
    for node in sorted(circuit.active, reverse=True):
        assert result[node] != full, 'Every active node reaches an output'
        if circuit.args[node]:
            for child in circuit.args[node]:
                result[child] &= result[node]
    for node in circuit.active:
        if circuit.args[node]:
            assert all(not result[child] & ~result[node] for child in circuit.args[node])
    return result


def alternatives(circuit):
    h = circuit.h
    assert h > 9
    narrow, original = envelope_labels(circuit, True)
    intersections = physical_intersections(circuit)
    designated = required_cores(circuit)
    pairs = list(combinations(range(h), 2))
    pair_ids = {pair:index for index,pair in enumerate(pairs)}
    edges = {node:0 for node in circuit.active if intersections[node]}
    commons = {node:(mask & -mask).bit_length()-1
               for node,mask in intersections.items() if mask}

    def encode(node, triple):
        common = commons[node]
        assert triple & (1 << common)
        remaining = triple ^ (1 << common)
        assert remaining.bit_count() == 2
        a = (remaining & -remaining).bit_length()-1
        b = (remaining ^ (1 << a)).bit_length()-1
        return 1 << pair_ids[tuple(sorted((a,b)))]

    for (_, target), node in circuit.outputs.items():
        if intersections[node]:
            edges[node] |= encode(node, sum(1 << vertex for vertex in target))
    targets, intern = {}, {}
    propagation = 0
    for node in sorted(circuit.active, reverse=True):
        if not intersections[node]:
            assert all(not intersections[child] for child in circuit.args[node] or ())
            continue
        assert edges[node]
        key = commons[node], edges[node]
        if key not in intern:
            intern[key] = target_span(h, commons[node], edges[node], pairs)
        span = intern[key]
        assert span.core == intersections[node]
        targets[node] = span
        if circuit.args[node]:
            for child in circuit.args[node]:
                if child in edges:
                    for triple in span.basis:
                        edges[child] |= encode(child, triple)
                        propagation += 1

    choices = {}
    source_exclusions = 0
    for node in sorted(circuit.active):
        if node in targets and circuit.args[node]:
            wide = Complement(h, targets[node])
            assert included(narrow[node], wide)
        else:
            wide = narrow[node]
            source_exclusions += int(node in targets)
        choices[node] = narrow[node], wide
        if circuit.args[node]:
            for child in circuit.args[node]:
                assert included(choices[child][0], choices[node][0])
                assert included(choices[child][0], choices[node][1])
                assert included(choices[child][1], choices[node][1])
        else:
            assert wide == narrow[node] and narrow[node].dimension == 1
    extra = [node for node in targets if designated[node].bit_count() > 1 and circuit.args[node]]
    histogram = Counter((designated[node].bit_count(), intersections[node].bit_count())
                        for node in targets)
    metadata = dict(original, frame_family='Positive E(C,V) or T-perp when all physical descendant targets share a point',
                    unique_target_descriptors=len(intern), physically_common_nodes=len(targets),
                    additional_multiple_designated_common_nodes=len(extra),
                    source_wide_exclusions=source_exclusions, target_basis_propagations=propagation,
                    common_histogram={str(key):value for key,value in sorted(histogram.items())},
                    ambient_nondegeneracy='H=9I-J, h>9, exactly one negative direction',
                    frame_nondegeneracy='T is a positive actual common-point triple span; T-perp is nondegenerate Lorentzian')
    return choices, targets, intersections, metadata


def independent(circuit, choices, targets, seed=109):
    """Small dense rational check using original physical descendant triples."""
    import sympy as sp
    from finite_target_complements import inertia
    h = circuit.h; H = 9*sp.eye(h)-sp.ones(h)
    assert H.det() != 0
    descendants = {node:0 for node in circuit.active}
    for (_, target), node in circuit.outputs.items():
        descendants[node] |= 1 << (circuit.variables[target]-1)
    for node in sorted(circuit.active, reverse=True):
        if circuit.args[node]:
            for child in circuit.args[node]:
                descendants[child] |= descendants[node]

    def columns(frame):
        if isinstance(frame, Complement):
            T = columns(frame.target_span)
            return sp.Matrix.hstack(*(T.T*H).nullspace())
        return sp.Matrix(h, frame.dimension, lambda row,col:(frame.basis[col] >> row) & 1)

    unique = list({frame for options in choices.values() for frame in options})
    matrices = {frame:columns(frame) for frame in unique}
    for frame, matrix in matrices.items():
        signature = inertia(matrix.T*H*matrix)
        assert signature[2] == 0 and matrix.rank() == frame.dimension
        assert signature[1] == int(isinstance(frame, Complement))
    span_tests = 0
    for node, span in targets.items():
        triples = [triple for index,triple in enumerate(circuit.inputs)
                   if descendants[node] & (1 << index)]
        actual = sp.Matrix(h, len(triples), lambda row,col:int(row in triples[col]))
        canonical = columns(span)
        assert actual.rank() == span.dimension
        assert actual.row_join(canonical).rank() == span.dimension
        span_tests += 1
    decisions = set()
    for node in circuit.active:
        if circuit.args[node]:
            for child in circuit.args[node]:
                for a,b in ((0,0),(0,1),(1,1)):
                    decisions.add((choices[child][a],choices[node][b]))
    rng = random.Random(seed)
    for _ in range(1000):
        decisions.add((rng.choice(unique),rng.choice(unique)))
    for a,b in decisions:
        assert included(a,b) == (matrices[b].row_join(matrices[a]).rank() == b.dimension)
    return dict(independent_frame_grams=len(unique), original_target_span_checks=span_tests,
                independent_rational_inclusions=len(decisions), seed=seed)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True)
    ap.add_argument('--candidate', type=Path)
    ap.add_argument('--h', type=int, default=12)
    ap.add_argument('--gap', type=int)
    ap.add_argument('--time-limit', type=float, default=90)
    ap.add_argument('--independent', action='store_true')
    ap.add_argument('--dirty', action='store_true')
    ap.add_argument('--shear', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); install_reference(args.reference)
    assert not args.output.exists(), 'Use a fresh output path'
    started = datetime.now(timezone.utc).isoformat(); begin = time.monotonic()
    if args.candidate:
        candidate = json.loads(args.candidate.read_text())
        h, positions, base = candidate['h'], candidate['positions'], candidate['base']
        provenance = dict(path=str(args.candidate), sha256=sha256(args.candidate.read_bytes()).hexdigest(),
                          candidate_id=candidate['candidate_id'], positive_roles=candidate['compiled_roles'])
    else:
        h = args.h; gap = h//2-1 if args.gap is None else args.gap
        positions = [gap if common//2 <= gap else gap+1 for common in range(h)]
        base = 4; provenance = dict(generator='aligned singleton gap', h=h, gap=gap)
    assert len(positions) == h and all(0 <= p < h//2 for p in positions)
    cls = singleton_class()
    circuit = GroupUnion(h, lambda n,common:cls(n,positions[common],base), 'paired', 0, True)
    graph = circuit.verify(); phase = {}
    at = time.monotonic()
    choices, targets, intersections, metadata = alternatives(circuit)
    phase['target_and_frame_construction'] = time.monotonic()-at
    print(json.dumps(dict(h=h,phase='frames',**metadata)),flush=True)
    extra = independent(circuit,choices,targets) if args.independent else {}
    sorter = {node:options[0] for node,options in choices.items()}
    view,_,schedule_sha = reordered(circuit,sorter,'rank_id',109)
    order = sorted(circuit.active,key=lambda node:(sorter[node].dimension,node))
    mapping = {old:new for new,old in enumerate(order,1)}
    assert all(view.args[mapping[n]] == tuple(mapping[c] for c in circuit.args[n])
               for n in circuit.active if circuit.args[n])
    view_choices = {mapping[node]:options for node,options in choices.items()}
    at = time.monotonic(); frames,plan,milp = solve(view,view_choices,included,args.time_limit)
    phase['joint_integer_optimization'] = time.monotonic()-at
    at = time.monotonic()
    with patch.object(frame_reuse,'included',included):
        compiled = frame_reuse.compile_reuse(view,frames,plan)
        checked = frame_reuse.check(view,frames,compiled)
        flow = frame_reuse.optimize_chains(view,frames,'id')
        optimized = frame_reuse.compile_reuse(view,frames,flow)
        maxflow_checked = frame_reuse.check(view,frames,optimized)
    phase['physical_compile_and_check'] = time.monotonic()-at
    assert optimized['roles'] <= compiled['roles']
    if milp['solver_reported_optimal']:
        assert optimized['roles'] == compiled['roles']
    result = dict(started_utc=started, h=h, positions=positions, base=base, input=provenance,
                  graph=graph, roles=optimized['roles'], checked=checked, maxflow_checked=maxflow_checked,
                  physical_targets=target_check(view,frames), frame_metadata=metadata, milp=milp,
                  chosen_original_node_ids=[order[n-1] for n in milp['selected_relevant_wide_nodes']],
                  independent=extra, schedule_sha256=schedule_sha, phase_seconds=phase,
                  scope='Recovered exact finite physically common positive/indefinite witness; final rank/join transfer and analytic composition remain separate')
    if args.dirty or args.shear:
        from dag_network import exact_invocation,shared_scalar_model
        from frame_reuse_certificate import program
        scalar = program(view,optimized)
        if args.dirty:
            result['dirty_basis'] = [exact_invocation(h,inverse,scalar) for inverse in (False,True)]
        if args.shear:
            result['three_stage_exchange'] = [shared_scalar_model(h,seed,scalar) for seed in (1,109)]
    names = ('finite_physical_target_kernels.py','finite_adaptive_complements.py','finite_label_milp.py',
             'finite_singleton_search.py','finite_block_search.py','finite_schedule_search.py',
             'finite_fast_target_frames.py','frame_envelope.py','frame_reuse.py')
    result['source_sha256'] = {name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                              for name in names}
    result['reference_commit'] = 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    result['settings'] = {key:str(value) if isinstance(value,Path) else value for key,value in vars(args).items()}
    result['completed_utc'] = datetime.now(timezone.utc).isoformat()
    result['elapsed_seconds'] = time.monotonic()-begin
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(h=h,roles=result['roles'],wide=milp['propagated_wide_nodes'],
                         additional=metadata['additional_multiple_designated_common_nodes'],
                         seconds=result['elapsed_seconds'])),flush=True)


if __name__ == '__main__':
    main()
