#!/usr/bin/env python3
"""Rebuild an explicit cloned DAG and audit a saved feasible controller plan.

No clone constructor, opportunity generator, mapped-frame routine or plan
exporter is imported. The parent graph uses an independent odd/even builder.
Only the changed graph receives full coefficient and physical frame checks.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import subprocess
import time

from finite_block_search import GroupUnion, install_reference
from frame_envelope import labels
from frame_reuse import compile_reuse, optimize_chains
from frame_reuse_certificate import program
from review_aligned_graph import check as logical_check
from review_envelopes import graph_envelope_check
from review_frame_reuse import dirty_check
from review_odd_pair_witness import build as odd_build, matching
from review_singleton_positions import build as even_build, compiled_digest, plan_check
from review_singleton_witness import physical_coefficients


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def file_digest(path):
    return sha256(path.read_bytes()).hexdigest()


def nested_tuple(value):
    return tuple(nested_tuple(v) for v in value) if isinstance(value, list) else value


class ExplicitDAG(GroupUnion):
    def __init__(self, parent, edits):
        for field in ('h', 'inputs', 'variables', 'locals', 'pair_ids', 'points', 'merged'):
            setattr(self, field, getattr(parent, field))
        moved = {}
        for edit in edits:
            old = edit['node']
            assert old in parent.active and parent.args[old] and old not in moved
            moved[old] = {nested_tuple(use) for use in edit['selected']}
            assert moved[old]
        self.args, self.core, self.union, self.provenance = [None], [0], [0], [None]
        self.parent_map, self.duplicate_map = {}, {}
        for old in range(1, len(parent.args)):
            if parent.args[old] is None:
                children = None
            else:
                children = tuple(self.duplicate_map[child]
                    if child in moved and ('gate', old) in moved[child]
                    else self.parent_map[child] for child in parent.args[old])
            self.parent_map[old] = len(self.args)
            self.args.append(children)
            self.core.append(parent.core[old])
            self.union.append(parent.union[old])
            self.provenance.append(parent.provenance[old])
            if old in moved:
                self.duplicate_map[old] = len(self.args)
                self.args.append(children)
                self.core.append(parent.core[old])
                self.union.append(parent.union[old])
                self.provenance.append(parent.provenance[old])
        self.outputs = {}
        for target, old in parent.outputs.items():
            self.outputs[target] = self.duplicate_map[old] if (
                old in moved and ('output', target) in moved[old]) else self.parent_map[old]
        self.active = set()
        pending = list(self.outputs.values())
        while pending:
            node = pending.pop()
            if node in self.active:
                continue
            self.active.add(node)
            if self.args[node]:
                pending.extend(self.args[node])
        self.additions = sum(bool(self.args[node]) for node in self.active)
        assert self.additions == parent.additions+len(edits)
        assert all(self.parent_map[old] in self.active and duplicate in self.active
                   for old, duplicate in self.duplicate_map.items())


def canonical_frames(parent, view):
    old, metadata = labels(parent, True)
    frames = {new: old[previous] for previous, new in view.parent_map.items()
              if new in view.active}
    frames.update({new: old[previous] for previous, new in view.duplicate_map.items()})
    assert set(frames) == view.active
    for node in view.active:
        assert frames[node].core == view.core[node] and frames[node].vertices == view.union[node]
        if view.args[node]:
            a, b = view.args[node]
            assert view.core[node] == view.core[a] & view.core[b]
            assert view.union[node] == view.union[a] | view.union[b]
    return old, frames, metadata


def descriptions(view, frames):
    order = sorted(view.active, key=lambda node: (frames[node].dimension, node))
    positions = {node: i for i, node in enumerate(order)}
    uses = {node: [] for node in order}
    records = []
    index = {}
    for parent in order:
        if not view.args[parent]:
            continue
        for position, child in enumerate(view.args[parent]):
            assert positions[child] < positions[parent]
            user = len(records)
            records.append((child, parent, position))
            uses[child].append(user)
            index[parent, position] = user
    for target, source in sorted(view.outputs.items()):
        user = len(records)
        records.append((source, None, target))
        uses[source].append(user)
        index[None, target] = user
    return uses, records, index


def plan_from_links(view, frames, links, summary):
    uses, records, _ = descriptions(view, frames)
    successor, predecessor = {}, {}
    for first, second in links:
        assert type(first) is int and type(second) is int
        assert 0 <= first < second < len(records)
        assert first not in successor and second not in predecessor
        successor[first] = second
        predecessor[second] = first
    plan = uses, records, successor, predecessor, summary
    audited = plan_check(view, frames, plan)
    audited['optimum_scope'] = 'Explicit feasible saved plan; no optimality claim'
    return plan, audited


def small_plan(parent, old_frames, view, frames, edits):
    _, old_records, old_next, _, _ = optimize_chains(parent, old_frames, 'rank')
    _, _, index = descriptions(view, frames)
    mapped = {old: index[view.parent_map[p] if p is not None else None, position]
              for old, (_, p, position) in enumerate(old_records)}
    links = [(mapped[a], mapped[b]) for a, b in old_next.items()]
    for edit in edits:
        duplicate = view.duplicate_map[edit['node']]
        a, b = edit['same_gate_new_predecessor_input'], edit['earlier_predecessor_input']
        assert {a, b} == {0, 1}
        first_a, first_b = edit['original_predecessor_users']
        assert old_records[first_a][1:] == (edit['node'], a)
        links.extend(((mapped[first_a], index[duplicate, a]),
                      (mapped[first_b], index[duplicate, b])))
    summary = dict(schedule='rank', selected_links=len(links), flow_value=len(links),
                   scope='Independent reconstruction of the explicit small feasible plan')
    return plan_from_links(view, frames, links, summary)


def verify(row, exported=None, small=False):
    begin = time.monotonic()
    h, base, positions = row['h'], row['base'], row['positions']
    parent = (odd_build if h % 2 else even_build)(h, base, positions)
    view = ExplicitDAG(parent, row['chosen'])
    logical = logical_check(view)
    print('PASS independent changed logical', h, logical['nonzero_partial_coefficients'], flush=True)
    old_frames, frames, metadata = canonical_frames(parent, view)
    if exported is not None:
        plan, chains = plan_from_links(view, frames, exported['exact_selected_links'], exported['schedule'])
        assert len(plan[1]) == exported['description_count'] and digest(plan[1]) == exported['descriptions_sha256']
    else:
        plan, chains = small_plan(parent, old_frames, view, frames, row['chosen'])
    del old_frames
    code = compile_reuse(view, frames, plan)
    assert code['roles'] == chains['independently_counted_roles'] == row['duplicated']['roles']
    assert len(plan[2]) == row['duplicated']['links']
    assert compiled_digest(code) == row['duplicated']['checked']['compiled_sha256']
    assert view.additions == row['duplicated']['logical']['additions']
    assert len(view.outputs) == row['duplicated']['logical']['partial_outputs']
    physical = physical_coefficients(view, code)
    rational = graph_envelope_check(view, frames, code, dense=small)
    result = dict(h=h, roles=code['roles'], clones=len(row['chosen']), logical=logical,
                  controller_plan=chains, physical=physical, rational_frames=rational,
                  compiled_sha256=compiled_digest(code), frame_metadata=metadata,
                  every_mapped_frame_has_exact_canonical_core_and_support=True)
    if h % 2:
        _, result['stage_matching'] = matching(h)
    if small:
        from dag_network import exact_invocation
        scalar = program(view, code)
        result['complete_side_dirty_basis'] = dirty_check(view, frames, code)
        result['complete_invocation_dirty_basis'] = [exact_invocation(h, inverse, scalar)
                                                    for inverse in (False, True)]
    if h >= 40:
        v, m, R, c = comb(h, 3), h**3, code['roles'], view.additions
        N = v**3
        W = 2*N+2*v*v*(R+h)
        L = 3*v*v*h*h
        D, s = N-2*L, W*m-N+2*L
        assert D > 0 and 2 <= s < m**5
        G = 3*v*v*(4*(c+R-v)+20*v)
        E = 64*(W+m+1)**3
        depth = 2*G*W*W+4*s+4*W+4
        assert E > depth
        counts = dict(v=v, m=m, N=N, W=W, L=L, D=D, s=s)
        assert len(view.inputs) == v and row['exact_counts']['h'] == h
        assert all(int(row['exact_counts'][k]) == value for k, value in counts.items() if k != 'v')
        guard = row['literal_scalar_guard']
        assert all(int(guard[k]) == value for k, value in dict(G=G, E=E, depth=depth, slack=E-depth).items())
        result['exact_counts'] = counts
        result['literal_scalar_guard'] = dict(G=G, E=E, depth=depth, slack=E-depth)
    result['wall_seconds'] = time.monotonic()-begin
    result['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print('PASS independent changed physical', h, code['roles'], flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('reference', 'certificate', 'plan', 'parent', 'small-certificate', 'output'):
        ap.add_argument('--'+name, type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh result path'
    revision = subprocess.check_output(['git', '-C', str(args.reference), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    install_reference(str(args.reference))
    data = json.loads(args.certificate.read_text())
    exported = json.loads(args.plan.read_text())
    parent = json.loads(args.parent.read_text())
    small = json.loads(args.small_certificate.read_text())
    assert data['status'].endswith('PASS') and exported['status'].endswith('PASS')
    assert file_digest(args.certificate) == exported['certificate_sha256']
    assert file_digest(args.parent) == exported['baseline_sha256'] == data['candidate_input_sha256']
    identity = exported['identity']
    assert digest(identity) == exported['candidate_id'] and identity['parent_candidate_id'] == parent['candidate_id']
    assert digest(data['rows'][0]['chosen']) == identity['clone_edits_sha256']
    assert digest(exported['exact_selected_links']) == identity['selected_links_sha256']
    assert data['rows'][0]['positions'] == parent['positions'] and data['rows'][0]['h'] == parent['h']
    begin = time.monotonic()
    small_row = next(row for row in small['rows'] if row['h'] == 12)
    control = verify(small_row, small=True)
    full = verify(data['rows'][0], exported)
    assert full['compiled_sha256'] == identity['compiled_sha256'] and full['roles'] == identity['roles']
    dependencies = ('review_explicit_clone_witness_repair.py', 'review_explicit_clone_witness.py', 'review_odd_pair_witness.py',
                    'review_singleton_positions.py', 'review_aligned_graph.py',
                    'review_singleton_witness.py', 'review_envelopes.py', 'review_frame_reuse.py',
                    'frame_envelope.py', 'frame_reuse.py', 'finite_block_search.py')
    result = dict(status='PASS independent explicit clone finite witness',
        campaign='20261007T222521Z', completed_utc=datetime.now(timezone.utc).isoformat(),
        candidate_id=exported['candidate_id'], reference_commit=revision,
        input_sha256={str(p): file_digest(p) for p in
            (args.certificate, args.plan, args.parent, args.small_certificate)},
        source_sha256={name: file_digest(Path(__file__).with_name(name)) for name in dependencies},
        full=full, small_control=control, wall_seconds=time.monotonic()-begin,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Changed DAG and explicit feasible plan only; full new coefficients/physical frames and fresh small dirty bases. No accepted baseline physical replay or clone producer import. Complete rank and invocation transfer require the separate all-size proof.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
