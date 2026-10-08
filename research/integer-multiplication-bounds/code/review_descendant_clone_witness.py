#!/usr/bin/env python3
"""Rebuild delayed clones with first-consumer frames and an explicit plan.

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
from review_envelopes import constraint_basis, rational_inclusion, target_eligible, vector, analyze
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
    """Independent construction in the original positive-frame rank order."""
    def __init__(self,parent,edits):
        for field in ('h','inputs','variables','locals','pair_ids','points','merged'):
            setattr(self,field,getattr(parent,field))
        self.parent_frames,self.parent_frame_metadata=labels(parent,True)
        order=sorted(parent.active,key=lambda node:(self.parent_frames[node].dimension,node))
        old_positions={node:i for i,node in enumerate(order)}
        self.edits={};before={};terminal=[]
        for edit in edits:
            node=edit['node'];assert node in parent.active and parent.args[node] and node not in self.edits
            assert edit['original_children']==list(parent.args[node])
            moved={nested_tuple(use) for use in edit['selected']};assert moved
            self.edits[node]=dict(edit,selected=moved)
            owner=edit['clone_insertion_owner'];frame_owner=edit['clone_frame_owner']
            if owner is None:
                assert frame_owner==node
                terminal.append(self.edits[node])
            else:
                assert owner==frame_owner and owner in parent.active and ('gate',owner) in moved
                assert all(old_positions[previous]<old_positions[owner] for previous in edit['predecessor_gates'])
                before.setdefault(owner,[]).append(self.edits[node])
        self.args,self.core,self.union,self.provenance=[None],[0],[0],[None]
        self.parent_map,self.duplicate_map={},{}
        def duplicate(edit):
            old=edit['node'];assert old in self.parent_map and old not in self.duplicate_map
            assert all(previous in self.parent_map for previous in edit['predecessor_gates'])
            self.duplicate_map[old]=len(self.args)
            self.args.append(tuple(self.parent_map[child] for child in parent.args[old]))
            self.core.append(parent.core[old]);self.union.append(parent.union[old]);self.provenance.append(parent.provenance[old])
        for old in order:
            for edit in sorted(before.get(old,[]),key=lambda edit:edit['node']):duplicate(edit)
            original=parent.args[old]
            children=None if not original else tuple(
                self.duplicate_map[child] if child in self.duplicate_map and ('gate',old) in self.edits[child]['selected']
                else self.parent_map[child] for child in original)
            self.parent_map[old]=len(self.args);self.args.append(children)
            self.core.append(parent.core[old]);self.union.append(parent.union[old]);self.provenance.append(parent.provenance[old])
        for edit in sorted(terminal,key=lambda edit:edit['node']):duplicate(edit)
        self.outputs={target:self.duplicate_map[old] if old in self.edits and ('output',target) in self.edits[old]['selected']
                      else self.parent_map[old] for target,old in parent.outputs.items()}
        self.active=set();pending=list(self.outputs.values())
        while pending:
            node=pending.pop()
            if node in self.active:continue
            self.active.add(node)
            if self.args[node]:pending.extend(self.args[node])
        self.additions=sum(bool(self.args[node]) for node in self.active)
        assert self.additions==parent.additions+len(edits)
        assert set(self.parent_map.values())|set(self.duplicate_map.values())==self.active
        assert all(self.parent_map[node]==node for node in range(1,len(self.inputs)+1))


def canonical_frames(parent,view):
    old=view.parent_frames
    frames={new:old[previous] for previous,new in view.parent_map.items()}
    enlarged=0
    for previous,new in view.duplicate_map.items():
        edit=view.edits[previous];frame=old[edit['clone_frame_owner']]
        frames[new]=frame
        assert frame.dimension==edit['clone_frame_dimension']
        assert old[previous].dimension==edit['original_frame_dimension']
        assert not old[previous].vertices & ~frame.vertices and not frame.core & ~old[previous].core
        enlarged+=frame.dimension>old[previous].dimension
    assert set(frames)==view.active
    for node in view.active:
        current=frames[node]
        assert not view.union[node]&~current.vertices and not current.core&~view.core[node]
        if view.args[node]:
            a,b=view.args[node]
            assert view.core[node]==view.core[a]&view.core[b] and view.union[node]==view.union[a]|view.union[b]
            for child in (a,b):
                assert not frames[child].vertices&~current.vertices and not current.core&~frames[child].core
    metadata=dict(original_envelope_metadata=view.parent_frame_metadata,
                  enlarged_clones=enlarged,explicit_first_consumer_owners=len(view.edits),
                  all_source_spans_contained_in_actual_positive_frames=True,
                  clone_formal_core_equality_not_assumed=True)
    return old,frames,metadata


def graph_envelope_check(circuit,frames,compiled,dense=True):
    """Audit actual envelopes, separately from the unchanged formal source span."""
    formal={};assigned={};checked=set();sources=[sum(1<<i for i in t) for t in circuit.inputs]
    for node in sorted(circuit.active):
        if not circuit.args[node]:C=V=sources[node-1]
        else:
            a,b=(formal[child] for child in circuit.args[node]);C,V=a[0]&b[0],a[1]|b[1]
        assert C and (C,V)==(circuit.core[node],circuit.union[node]);formal[node]=(C,V)
        actual=frames[node];A,B=actual.core,actual.vertices
        assert A and not A&~B and not V&~B and not A&~C
        dimension=1 if A==B else (B&~A).bit_count()
        assert actual.dimension==dimension
        if not circuit.args[node]:assert dimension==1 and actual.basis==(C,)
        key=A,B
        if dense and key not in checked:
            rows=constraint_basis(A,B,circuit.h);given=[vector(t,circuit.h) for t in actual.basis]
            assert rational_inclusion(rows,given) and rational_inclusion(given,rows)
            assert analyze(rows)['signature']=='positive';checked.add(key)
        for triple in actual.basis:assert triple.bit_count()==3 and not triple&~B and triple&A==A
        assigned[node]=key
    for (_,target),node in circuit.outputs.items():
        mask=sum(1<<i for i in target);A,B=assigned[node]
        assert target_eligible(A,B,mask,circuit.h)
    physical=[None]*compiled['roles'];transitions=0
    for source,slot in compiled['sources'].items():physical[slot]=assigned[circuit.variables[source]]
    for node,ins,outs in compiled['gates']:
        C,V=assigned[node]
        for slot in set(ins+outs):
            if physical[slot] is not None:
                oldC,oldV=physical[slot];assert not oldV&~V and not C&~oldC
            physical[slot]=C,V;transitions+=1
    for target,slot in compiled['outputs'].items():assert physical[slot]==assigned[circuit.outputs[target]]
    reverse=[None]*compiled['roles']
    for target,slot in compiled['outputs'].items():reverse[slot]=assigned[circuit.outputs[target]]
    for node,ins,outs in reversed(compiled['gates']):
        C,V=assigned[node]
        for slot in set(ins+outs):
            if reverse[slot] is not None:
                nextC,nextV=reverse[slot];assert not V&~nextV and not nextC&~C
            reverse[slot]=C,V;transitions+=1
    for source,slot in compiled['sources'].items():assert reverse[slot]==assigned[circuit.variables[source]]
    return dict(logical_frames=len(formal),unique_dense_constraint_checks=len(checked),
                physical_frame_transitions=transitions,all_input_frames_original_lines=True,
                every_designated_target_orthogonal=True,all_output_frames_exact=True,
                all_source_spans_contained_in_actual_frames=True,forward_and_reverse_complement_nesting=True)


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
        order=sorted(view.active,key=lambda node:(frames[node].dimension,node))
        locations=[[edit['node'],view.duplicate_map[edit['node']],view.parent_map[edit['clone_frame_owner']]]
                   for edit in row['chosen']]
        assert digest(order)==exported['node_order_sha256'] and len(order)==exported['node_count']
        assert digest(sorted(view.parent_map.items()))==exported['original_node_mapping_sha256']
        assert locations==exported['clone_placement_and_frame_owner_ids']
    else:
        plan, chains = small_plan(parent, old_frames, view, frames, row['chosen'])
    del old_frames
    code = compile_reuse(view, frames, plan)
    assert code['roles'] == chains['independently_counted_roles'] == row['final']['roles']
    assert len(plan[2]) == row['final']['links']
    assert compiled_digest(code) == row['final']['checked']['compiled_sha256']
    assert view.additions == row['final']['logical']['additions']
    assert len(view.outputs) == row['final']['logical']['partial_outputs']
    physical = physical_coefficients(view, code)
    rational = graph_envelope_check(view, frames, code, dense=small)
    result = dict(h=h, roles=code['roles'], clones=len(row['chosen']), logical=logical,
                  controller_plan=chains, physical=physical, rational_frames=rational,
                  compiled_sha256=compiled_digest(code), frame_metadata=metadata,
                  every_actual_frame_contains_source_span=True,
                  enlarged_frames_checked_against_first_consumer=True)
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
    dependencies = ('review_descendant_clone_witness.py', 'review_explicit_clone_witness_repair.py', 'review_odd_pair_witness.py',
                    'review_singleton_positions.py', 'review_aligned_graph.py',
                    'review_singleton_witness.py', 'review_envelopes.py', 'review_frame_reuse.py',
                    'frame_envelope.py', 'frame_reuse.py', 'finite_block_search.py')
    result = dict(status='PASS independent delayed first-consumer-frame clone finite witness',
        campaign='20261007T222521Z', completed_utc=datetime.now(timezone.utc).isoformat(),
        candidate_id=exported['candidate_id'], reference_commit=revision,
        input_sha256={str(p): file_digest(p) for p in
            (args.certificate, args.plan, args.parent, args.small_certificate)},
        source_sha256={name: file_digest(Path(__file__).with_name(name)) for name in dependencies},
        full=full, small_control=control, wall_seconds=time.monotonic()-begin,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Changed DAG and explicit feasible plan only; full new coefficients/physical frames and fresh small dirty bases. Actual enlarged clone frames, full descriptor/node-order identities and direct-target orthogonality checked; no accepted baseline physical replay or clone producer import. Complete rank and invocation transfer require the separate all-size proof.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()
