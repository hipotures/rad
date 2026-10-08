#!/usr/bin/env python3
"""Combine explicit gate duplicates with certified controller role savings.

One duplicated sum costs one addition. Two unused earlier gate capacities
can connect its new input recipients, while moving an entire output chain
preserves existing links. The batch uses disjoint gate capacities and then
recomputes the complete unchanged maximum-flow/compiler/frame witness.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import resource
import time

from finite_block_search import GroupUnion, install_reference
from finite_clone_gate_residual import opportunities
from finite_clone_gate_screen import compile_checked
from finite_singleton_search import singleton_class
import frame_reuse


class BatchCloneView(GroupUnion):
    """Preserve explicit node identity; never intern duplicates by support."""
    def __init__(self, original, jobs):
        for name in ('h', 'inputs', 'variables', 'locals', 'pair_ids', 'points', 'merged'):
            setattr(self, name, getattr(original, name))
        selected = {job['node']: frozenset(tuple(use) for use in job['selected']) for job in jobs}
        assert len(selected) == len(jobs)
        self.args = [None]; self.core = [0]; self.union = [0]; self.provenance = [None]
        mapping = {}; clones = {}
        for old in range(1, len(original.args)):
            args = original.args[old]
            children = (tuple(clones[child] if child in clones and ('gate', old) in selected[child]
                              else mapping[child] for child in args) if args else None)
            new = len(self.args); mapping[old] = new
            self.args.append(children); self.core.append(original.core[old])
            self.union.append(original.union[old]); self.provenance.append(original.provenance[old])
            if old in selected:
                assert children and selected[old]
                clones[old] = len(self.args)
                self.args.append(children); self.core.append(original.core[old])
                self.union.append(original.union[old]); self.provenance.append(original.provenance[old])
        self.outputs = {
            target: clones[node] if node in clones and ('output', target) in selected[node] else mapping[node]
            for target, node in original.outputs.items()}
        self.active = set(); stack = list(self.outputs.values())
        while stack:
            value = stack.pop()
            if value in self.active: continue
            self.active.add(value)
            if self.args[value]: stack.extend(self.args[value])
        self.additions = sum(self.args[value] is not None for value in self.active)
        assert self.additions == original.additions + len(jobs)
        assert all(mapping[node] in self.active and clone in self.active for node, clone in clones.items())
        self.original_mapping = mapping; self.clones = clones


def compatible(jobs):
    """A sufficient conflict filter; maximality is not claimed."""
    used = set(); selected = []; rejected = []
    for job in jobs:
        capacities = {job['node'], *job['predecessor_gates']}
        if capacities & used: rejected.append(job); continue
        used.update(capacities); selected.append(job)
    return selected, rejected


def serialized(job):
    return {**job, 'selected': sorted(job['selected'], key=str)}


def build(h, base, positions):
    if h % 2:
        from finite_odd_pair_positions import build as odd_build
        return odd_build(h, positions, base)
    cls = singleton_class()
    return GroupUnion(h, lambda n, common: cls(n, positions[common], base), 'paired', 0, True)


def dirty_controls(circuit, frames, code, shared):
    from frame_reuse_certificate import program
    from dag_network import exact_invocation, shared_scalar_model
    from review_frame_reuse import dirty_check
    from review_singleton_witness import physical_coefficients
    from review_aligned_graph import check as logical_check
    from review_envelopes import graph_envelope_check
    scalar = program(circuit, code)
    value = dict(independent_logical=logical_check(circuit),
                 independent_physical=physical_coefficients(circuit, code),
                 independent_rational_frames=graph_envelope_check(circuit, frames, code, dense=True),
                 complete_side_dirty_basis=dirty_check(circuit, frames, code),
                 complete_invocation_dirty_basis=[exact_invocation(circuit.h, inverse, scalar)
                                                  for inverse in (False, True)])
    if shared:
        assert circuit.h <= 8 and circuit.h % 2 == 0
        value['complete_three_stage_exchange'] = [dict(seed=seed, **shared_scalar_model(circuit.h, seed, scalar))
                                                  for seed in (1, 109)]
    return value


def case(h, base, positions, small=False, single=False):
    at = time.monotonic(); original = build(h, base, positions)
    baseline, frames, _ = compile_checked(original)
    plan = frame_reuse.optimize_chains(original, frames, 'rank')
    jobs, diagnostic = opportunities(original, frames, plan)
    chosen, rejected = compatible(jobs)
    if single: chosen = chosen[:1]
    neutral = False
    if not chosen and small:
        from finite_clone_gate_screen import candidates
        candidate, _ = candidates(original, frames, 1)
        assert candidate
        node, uses = candidate[0]
        chosen = [dict(node=node, selected=uses, predecessor_gates=[], original_predecessor_users=[])]
        neutral = True
    result = dict(h=h, base=base, positions=positions, baseline=baseline,
                  opportunity_diagnostic=diagnostic, predicted_opportunities=len(jobs),
                  conflict_rejected=len(rejected), chosen=[serialized(job) for job in chosen],
                  neutral_small_mechanics_control=neutral)
    if chosen:
        view = BatchCloneView(original, chosen); checked, new_frames, code = compile_checked(view)
        delta_c = view.additions - original.additions
        delta_links = checked['links'] - baseline['links']
        assert checked['roles'] - baseline['roles'] == delta_c - delta_links
        result.update(duplicated=checked, delta_additions=delta_c,
                      delta_retained_links=delta_links, role_saving=baseline['roles']-checked['roles'],
                      predicted_two_links_each_achieved=delta_links >= 2*len(chosen) if not neutral else None)
        if small: result['small_controls'] = dirty_controls(view, new_frames, code, shared=h <= 8)
        if h >= 40:
            from finite_residual_rank_histogram import histogram
            from downstream_parameter_optimum import as_strings, saving_enclosure
            from fractions import Fraction
            ranks = histogram(h, view, new_frames, code)
            result['exact_counts'] = as_strings(ranks)
            if ranks['D'] > 0:
                result['uniform_shrink_saving'] = as_strings(saving_enclosure(Fraction(ranks['D'], ranks['W']*ranks['m']), ranks['m']))
    result.update(elapsed_seconds=time.monotonic()-at,
                  process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    frame_reuse.included.cache_clear(); GroupUnion.support_in.cache_clear()
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True); ap.add_argument('--h', nargs='+', type=int, default=[8, 12, 20])
    ap.add_argument('--base', type=int, default=2); ap.add_argument('--candidate', type=Path)
    ap.add_argument('--small', action='store_true'); ap.add_argument('--single', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(); assert not args.output.exists(); install_reference(args.reference)
    at = time.monotonic()
    value = dict(status='Running', source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                 started_utc=datetime.now(timezone.utc).isoformat(), rows=[],
                 scope='Exact explicit duplicated cancellation-free DAG; actual controller roles, unchanged positive envelope and rank verifier')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.candidate:
        candidate = json.loads(args.candidate.read_text())
        value['candidate_input_sha256'] = sha256(args.candidate.read_bytes()).hexdigest()
        jobs = [(candidate['h'], candidate['base'], candidate['positions'])]
    else:
        jobs = [(h, args.base, [0]*(h//2-1)+[h//2-2]*(h//2+1)) for h in args.h]
    for h, base, positions in jobs:
        assert len(positions) == h
        row = case(h, base, positions, args.small, args.single); value['rows'].append(row)
        args.output.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
        print(json.dumps(dict(h=h, baseline=row['baseline']['roles'],
                              cloned=row.get('duplicated', {}).get('roles'),
                              clones=len(row['chosen']), role_saving=row.get('role_saving'),
                              seconds=row['elapsed_seconds'])), flush=True)
    value.update(status='Terminal exact batch clone PASS', elapsed_seconds=time.monotonic()-at,
                 completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__': main()
