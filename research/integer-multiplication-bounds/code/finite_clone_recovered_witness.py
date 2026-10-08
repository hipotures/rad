#!/usr/bin/env python3
"""Explicit compatible clones with a recovered feasible controller witness.

Whole output chains are moved to equal-value clones. Each unused original
gate P and unused earlier gate Q supply one new controller link. The old
flow is preserved; its optimality is not needed for the new finite witness.
The changed graph still receives all original coefficient, forward/reverse
frame and designated-target checks. A frozen baseline is reconstructed and
hash-compared, without rerunning its already recorded physical verification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

from finite_block_search import GroupUnion, install_reference
from finite_clone_batch import BatchCloneView, build, dirty_controls, serialized
from finite_clone_chain_bridge import bridge_compatible
from finite_clone_gate_screen import compile_checked
from finite_clone_unused_capacity import unused_opportunities
from fast_frame_envelope import labels
from frame_envelope import target_check
import frame_reuse


def compiled_hash(code):
    """The unchanged checker's exact serialization, without coefficient replay."""
    return sha256(json.dumps({"roles": code["roles"], "gates": code["gates"],
        "sources": sorted(code["sources"].items()),
        "outputs": sorted(code["outputs"].items())}, separators=(",", ":")).encode()).hexdigest()


def descriptions(circuit, spaces):
    order = sorted(circuit.active, key=lambda node: (spaces[node].dimension, node))
    positions = {node: index for index, node in enumerate(order)}
    users = {node: [] for node in circuit.active}; uses = []; index = {}
    for parent in order:
        if not circuit.args[parent]: continue
        assert all(positions[child] < positions[parent] for child in circuit.args[parent])
        for position, child in enumerate(circuit.args[parent]):
            user = len(uses); uses.append((child, parent, position))
            users[child].append(user); index[parent, position] = user
    for target, node in sorted(circuit.outputs.items()):
        user = len(uses); uses.append((node, None, target))
        users[node].append(user); index[None, target] = user
    return users, uses, index


def mapped_frames(original, old_frames, view, compare=False):
    values = {view.original_mapping[node]: old_frames[node] for node in original.active}
    values.update({clone: old_frames[node] for node, clone in view.clones.items()})
    assert set(values) == view.active
    for node, frame in values.items():
        assert frame.core == view.core[node] and frame.vertices == view.union[node]
        if view.args[node]:
            a, b = view.args[node]
            assert view.core[node] == (view.core[a] & view.core[b])
            assert view.union[node] == (view.union[a] | view.union[b])
    if compare:
        rebuilt, _ = labels(view, True)
        assert rebuilt == values, 'Mapped envelopes must equal every canonical Space field'
    return values


def recovered_plan(original, old_plan, view, frames, jobs):
    old_users, old_uses, old_successor, _, _ = old_plan
    users, uses, index = descriptions(view, frames)
    use_map = {}
    for old_user, (_, parent, position) in enumerate(old_uses):
        use_map[old_user] = index[view.original_mapping[parent] if parent is not None else None, position]
    successor = {}; predecessor = {}
    def link(first, second):
        assert first not in successor and second not in predecessor
        node, previous, _ = uses[first]; node2, following, _ = uses[second]
        assert node == node2 and first < second and previous is not None
        assert frame_reuse.included(frames[previous], frames[following if following is not None else node])
        successor[first] = second; predecessor[second] = first
    for first, second in old_successor.items(): link(use_map[first], use_map[second])
    for job in jobs:
        clone = view.clones[job['node']]
        a = job['same_gate_new_predecessor_input']; b = job['earlier_predecessor_input']
        assert (a, b) in ((0, 1), (1, 0))
        first_a, first_b = job['original_predecessor_users']
        assert old_uses[first_a][1:] == (job['node'], a)
        link(use_map[first_a], index[clone, a])
        link(use_map[first_b], index[clone, b])
    retained = set()
    for first in successor:
        parent = uses[first][1]
        assert parent not in retained; retained.add(parent)
    assert len(uses) == len(old_uses) + 2*len(jobs)
    assert len(successor) == len(old_successor) + 2*len(jobs)
    return users, uses, successor, predecessor, dict(
        schedule='rank', selected_links=len(successor), flow_value=len(successor),
        old_selected_links=len(old_successor), recovered_extra_links=2*len(jobs),
        scope='Explicit feasible controller chains; no maximum-flow optimality claimed',
        exact_chain_and_capacity_constraints_checked=True)


def case(h, base, positions, frozen=None, compare_frames=False, dirty=False):
    at = time.monotonic(); phases = {}; started = at
    original = build(h, base, positions)
    if frozen is None:
        baseline, old_frames, old_code = compile_checked(original)
        old_plan = frame_reuse.optimize_chains(original, old_frames, 'rank')
    else:
        logical = original.verify()
        assert logical == frozen['logical']
        old_frames, metadata = labels(original, True)
        old_plan = frame_reuse.optimize_chains(original, old_frames, 'rank')
        old_code = frame_reuse.compile_reuse(original, old_frames, old_plan)
        digest = compiled_hash(old_code)
        assert digest == frozen['checked']['compiled_sha256']
        assert old_code['roles'] == frozen['compiled_roles']
        assert len(old_plan[2]) == frozen['chains']['selected_links']
        baseline = dict(logical=logical, roles=old_code['roles'], links=len(old_plan[2]),
            checked=dict(compiled_sha256=digest, baseline_verification_reused_from_frozen_candidate=True),
            frames=metadata)
    phases['reconstruct_frozen_baseline'] = time.monotonic()-started
    started = time.monotonic()
    jobs, diagnostic = unused_opportunities(original, old_frames, old_plan)
    chosen, rejected = bridge_compatible(jobs)
    value = dict(h=h, base=base, positions=positions, baseline=baseline,
        opportunity_diagnostic=diagnostic, predicted_opportunities=len(jobs),
        chosen=[serialized(job) for job in chosen], conflict_rejected=len(rejected),
        frame_identity_control=compare_frames)
    if chosen:
        view = BatchCloneView(original, chosen)
        new_frames = mapped_frames(original, old_frames, view, compare_frames)
        plan = recovered_plan(original, old_plan, view, new_frames, chosen)
        phases['clone_graph_frames_and_feasible_plan'] = time.monotonic()-started
        started = time.monotonic()
        logical = view.verify(); code = frame_reuse.compile_reuse(view, new_frames, plan)
        checked = frame_reuse.check(view, new_frames, code)
        targets = target_check(view, new_frames, True)
        gain = baseline['roles']-code['roles']
        assert gain == len(chosen)
        value.update(duplicated=dict(logical=logical, roles=code['roles'],
            links=len(plan[2]), checked=checked, targets=targets, chains=plan[4]),
            delta_additions=len(chosen), delta_links=2*len(chosen), role_saving=gain)
        phases['complete_changed_coefficient_frame_target_checks'] = time.monotonic()-started
        if dirty:
            started = time.monotonic()
            value['complete_dirty_controls'] = dirty_controls(view, new_frames, code, shared=h <= 8 and h % 2 == 0)
            phases['complete_dirty_controls'] = time.monotonic()-started
        if h >= 40:
            from finite_residual_rank_histogram import histogram
            from downstream_parameter_optimum import as_strings, saving_enclosure
            started = time.monotonic(); counts = histogram(h, view, new_frames, code)
            value['exact_counts'] = as_strings(counts)
            assert counts['D'] > 0
            value['uniform_shrink_saving'] = as_strings(saving_enclosure(Fraction(counts['D'], counts['W']*counts['m']), counts['m']))
            v = len(view.inputs); c = view.additions; R = code['roles']; W = counts['W']; m = counts['m']; s = counts['s']
            G = 3*v*v*(4*(c+R-v)+20*v)
            depth = 2*G*W*W+4*s+4*W+4; E = 64*(W+m+1)**3
            assert E > depth
            value['literal_scalar_guard'] = as_strings(dict(G=G, E=E, depth=depth, slack=E-depth,
                invocation_scalar_operations=4*(c+R-v)+20*v,
                scope='Exact additions/copies for four mixers, target shears, centers and data paths; no unchanged G bound assumed'))
            phases['exact_rank_and_operation_guard'] = time.monotonic()-started
    else:
        phases['candidate_and_conflict_search'] = time.monotonic()-started
    value.update(phase_seconds=phases, elapsed_seconds=time.monotonic()-at,
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear(); GroupUnion.support_in.cache_clear()
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True); ap.add_argument('--h', type=int, nargs='+', default=[8,12,20])
    ap.add_argument('--base', type=int, default=2); ap.add_argument('--candidate', type=Path)
    ap.add_argument('--compare-frames', action='store_true'); ap.add_argument('--dirty-ground', type=int)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); assert not args.output.exists(); install_reference(args.reference)
    at = time.monotonic(); result = dict(status='Running', rows=[],
        started_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        dependency_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in (
            'finite_clone_unused_capacity.py','finite_clone_batch.py','finite_clone_chain_bridge.py',
            'fast_frame_envelope.py','frame_reuse.py','finite_odd_pair_positions.py')},
        scope='Recovered feasible flow with exact unchanged changed-graph checks; no flow optimality or final composition claimed')
    frozen = json.loads(args.candidate.read_text()) if args.candidate else None
    if frozen:
        result['candidate_input_sha256'] = sha256(args.candidate.read_bytes()).hexdigest()
        configs = [(frozen['h'], frozen['base'], frozen['positions'])]
    else: configs = [(h,args.base,[0]*(h//2-1)+[h//2-2]*(h//2+1)) for h in args.h]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h,base,positions in configs:
        row = case(h,base,positions,frozen,args.compare_frames,args.dirty_ground==h)
        result['rows'].append(row); args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=row['baseline']['roles'],roles=row.get('duplicated',{}).get('roles'),
            clones=len(row['chosen']),seconds=row['elapsed_seconds'])),flush=True)
    result.update(status='Terminal exact recovered clone witness PASS',elapsed_seconds=time.monotonic()-at,
        completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__': main()
