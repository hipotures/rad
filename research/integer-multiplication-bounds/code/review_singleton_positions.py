#!/usr/bin/env python3
"""Independent uncached promotion of arbitrary aligned singleton positions.

Every logical coefficient and physical copy is reconstructed independently.
The controller plan is checked using envelope equations, and small controls
also cover complete dirty invocation bases and shared three-stage exchanges.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from review_aligned_graph import check as logical_check
from review_envelopes import graph_envelope_check, matching_check
from review_frame_reuse import dirty_check
from review_singleton_witness import physical_coefficients

REFERENCE_COMMIT = 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'


def identity(h, base, positions):
    value = dict(h=h, base=base, positions=positions,
                 reference_commit=REFERENCE_COMMIT)
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def build(h, base, positions):
    from finite_block_search import GroupUnion
    from finite_singleton_search import singleton_class
    assert h >= 6 and h % 2 == 0
    assert len(positions) == h and all(type(p) is int and 0 <= p < h//2 for p in positions)
    cls = singleton_class()
    # Deliberately construct every local graph afresh; no throughput cache.
    return GroupUnion(h, lambda n, common: cls(n, positions[common], base), 'paired', 0, True)


def plan_check(circuit, frames, plan):
    users, descriptions, successor, predecessor, summary = plan
    assert len(successor) == len(predecessor) == summary['selected_links'] == summary['flow_value']
    parents = set()
    for first, second in successor.items():
        source, previous, _ = descriptions[first]
        source2, following, _ = descriptions[second]
        assert source == source2 and previous is not None and first < second
        assert predecessor[second] == first and previous not in parents
        parents.add(previous)
        before = frames[previous]
        after = frames[following if following is not None else source]
        assert not before.vertices & ~after.vertices
        assert not after.core & ~before.core
    uses = 0
    starts = 0
    for source, indices in users.items():
        assert indices == sorted(indices)
        for user in indices:
            assert descriptions[user][0] == source
            uses += 1
            starts += user not in predecessor
    assert uses == len(descriptions)
    # Each source node gets one initial slot. Each binary node reuses a
    # terminating input pivot; the remaining chain starts need fresh copies.
    roles = starts-circuit.additions
    assert roles == circuit.additions+len(circuit.outputs)-len(successor)
    return dict(selected_links=len(successor), separate_gate_capacity_checks=len(parents),
                directed_source_uses=uses, controller_chain_starts=starts,
                independently_counted_roles=roles,
                all_links_same_source_and_acyclic=True,
                all_retained_labels_nested_by_equations=True,
                optimum_scope='Optimizer maximizes links in this fixed schedule/ansatz; witness validity does not require optimality')


def compiled_digest(code):
    payload = dict(roles=code['roles'], gates=code['gates'],
                   sources=sorted(code['sources'].items()),
                   outputs=sorted(code['outputs'].items()))
    return sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()


def case(h, base, positions, small=False, expected=None):
    from frame_envelope import labels
    from frame_reuse import compile_reuse, optimize_chains
    begin = time.monotonic()
    circuit = build(h, base, positions)
    logical = logical_check(circuit)
    print('PASS logical', h, logical['nonzero_partial_coefficients'], flush=True)
    frames, metadata = labels(circuit, True)
    plan = optimize_chains(circuit, frames, 'rank')
    chain_audit = plan_check(circuit, frames, plan)
    compiled = compile_reuse(circuit, frames, plan)
    assert compiled['roles'] == chain_audit['independently_counted_roles']
    physical = physical_coefficients(circuit, compiled)
    rational = graph_envelope_check(circuit, frames, compiled, dense=small)
    digest = compiled_digest(compiled)
    result = dict(h=h, base=base, positions=positions, candidate_id=identity(h, base, positions),
                  roles=compiled['roles'], logical=logical, physical=physical,
                  rational_frames=rational, controller_plan=chain_audit,
                  optimizer_summary=compiled['chain_summary'], frame_metadata=metadata,
                  compiled_sha256=digest, stage_matching=matching_check(h))
    if expected is not None:
        assert result['candidate_id'] == expected['candidate_id']
        assert result['roles'] == expected['compiled_roles']
        assert digest == expected['checked']['compiled_sha256']
        assert circuit.additions == expected['original']['additions']
        assert len(circuit.outputs) == expected['original']['partial_outputs']
        assert chain_audit['selected_links'] == expected['chains']['selected_links']
        result['matches_immutable_producer_identity_and_compilation'] = True
    if small:
        from frame_reuse_certificate import program
        from dag_network import exact_invocation, shared_scalar_model
        scalar = program(circuit, compiled)
        result['complete_side_dirty_basis'] = dirty_check(circuit, frames, compiled)
        result['complete_invocation_dirty_basis_including_centers'] = [
            exact_invocation(h, inv, scalar) for inv in (False, True)]
        result['complete_shared_three_stage_exchange'] = [
            dict(seed=seed, **shared_scalar_model(h, seed, scalar)) for seed in (1, 109)]
    result['wall_seconds'] = time.monotonic()-begin
    result['process_peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print('PASS complete', h, 'roles', compiled['roles'], 'links', chain_audit['selected_links'], flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--small-controls', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh result path'
    actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.reference, text=True).strip()
    assert actual == REFERENCE_COMMIT
    sys.dont_write_bytecode = True
    from finite_block_search import install_reference
    install_reference(str(args.reference))
    producer = json.loads(args.candidate.read_text())
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    full = case(producer['h'], producer['base'], producer['positions'], expected=producer)
    small = []
    if args.small_controls:
        # The candidate's last global pair moves backwards. These controls
        # also vary both members of several pairs independently, rather than
        # relying on a uniform gap or a pairwise-constant position family.
        for h, positions in ((6, [1, 1, 1, 1, 0, 0]),
                             (8, [0, 3, 1, 2, 3, 0, 1, 1])):
            small.append(case(h, producer['base'], positions, small=True))
    dependencies = ('review_singleton_positions.py', 'review_aligned_graph.py',
                    'review_singleton_witness.py', 'review_envelopes.py', 'review_frame_reuse.py',
                    'review_rational_frames.py', 'finite_singleton_search.py',
                    'finite_block_search.py', 'frame_envelope.py', 'frame_reuse.py',
                    'frame_reuse_certificate.py')
    result = dict(status='PASS', started_utc=started,
                  completed_utc=datetime.now(timezone.utc).isoformat(),
                  candidate_file_sha256=sha256(args.candidate.read_bytes()).hexdigest(),
                  source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                 for name in dependencies},
                  original_script_sha256={name:sha256((args.reference/'scripts'/name).read_bytes()).hexdigest()
                                          for name in ('dag_network.py', 'reuse_network.py')},
                  python_version=sys.version, reference_commit=actual,
                  full=full, small_controls=small,
                  wall_seconds=time.monotonic()-start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Full uncached candidate coefficient, physical frame and controller witness; full dirty bases/exchanges are bounded small controls; central rank accounting and analytic composition are inherited separately reviewed interfaces')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS', args.output, flush=True)


if __name__ == '__main__':
    main()
