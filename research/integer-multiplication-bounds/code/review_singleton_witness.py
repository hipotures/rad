#!/usr/bin/env python3
"""Independent dense coefficients and rational frames for singleton gaps.

Reads gate arguments and triples to reconstruct every coefficient, then
checks a separate physical execution with disjoint unions and fresh copies.
Does not call the producer's map or compiled-scalar verifier.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import resource
import sys
import time

from review_aligned_graph import check as dense_logical_check
from review_envelopes import graph_envelope_check, matching_check
from review_frame_reuse import dirty_check


def physical_coefficients(circuit, compiled):
    expected = {}
    for node in sorted(circuit.active):
        if circuit.args[node] is None:
            expected[node] = 1 << (node-1)
        else:
            a, b = circuit.args[node]
            assert not expected[a] & expected[b]
            expected[node] = expected[a] | expected[b]
    values = [0]*compiled['roles']
    for triple, slot in compiled['sources'].items():
        assert values[slot] == 0
        values[slot] = 1 << (circuit.variables[triple]-1)
    additions = copies = 0
    digest = sha256()
    for node, ins, outs in compiled['gates']:
        assert outs[0] == ins[0] and len(ins) in (1, 2)
        assert len(set(ins)) == len(ins) and len(set(outs)) == len(outs)
        assert set(ins) & set(outs) == {ins[0]}
        if len(ins) == 2:
            assert values[ins[0]] and values[ins[1]]
            assert not values[ins[0]] & values[ins[1]], (node, 'physical overlap')
            values[ins[0]] |= values[ins[1]]
            additions += 1
        assert values[ins[0]] == expected[node]
        for slot in outs[1:]:
            assert values[slot] == 0, (slot, 'copy destination not fresh')
            values[slot] = values[ins[0]]
            copies += 1
        assert all(values[slot] == expected[node] for slot in outs)
        digest.update(json.dumps((node, ins, outs), separators=(',', ':')).encode()+b'\n')
    for target, slot in compiled['outputs'].items():
        assert values[slot] == expected[circuit.outputs[target]]
    assert additions == circuit.additions
    assert compiled['roles'] == circuit.additions+len(circuit.outputs)-compiled['chain_summary']['selected_links']
    return dict(disjoint_physical_additions=additions, fresh_physical_copies=copies,
                every_gate_output_exact=True, every_physical_target_exact=True,
                cancellation_free_over_any_scalar_field=True,
                physical_schedule_digest=digest.hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', type=Path, required=True)
    ap.add_argument('--h', type=int, default=50)
    ap.add_argument('--gap', type=int, default=23)
    ap.add_argument('--small', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists(), 'Use a fresh result path'
    sys.dont_write_bytecode = True
    from finite_block_search import install_reference
    install_reference(str(args.reference))
    from finite_singleton_certificate import build
    from frame_envelope import labels
    from frame_reuse import compile_reuse, optimize_chains
    start = time.monotonic()
    circuit, positions = build(args.h, args.gap)
    logical = dense_logical_check(circuit)
    print('PASS independent logical map', args.h, logical['nonzero_partial_coefficients'], flush=True)
    frames, _ = labels(circuit, True)
    compiled = compile_reuse(circuit, frames, optimize_chains(circuit, frames, 'rank'))
    physical = physical_coefficients(circuit, compiled)
    rational = graph_envelope_check(circuit, frames, compiled, dense=args.small)
    dirty = dirty_check(circuit, frames, compiled) if args.small else None
    dependencies = ('review_singleton_witness.py', 'review_aligned_graph.py', 'review_envelopes.py',
                    'review_frame_reuse.py', 'finite_singleton_certificate.py', 'finite_singleton_search.py',
                    'finite_block_search.py', 'frame_envelope.py', 'frame_reuse.py')
    result = dict(h=args.h, gap=args.gap, positions=positions, roles=compiled['roles'],
                  retained_links=compiled['chain_summary']['selected_links'],
                  logical=logical, physical=physical, rational_frames=rational,
                  stage_matching=matching_check(args.h), complete_side_dirty_basis=dirty,
                  source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                 for name in dependencies},
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  wall_seconds=time.monotonic()-start,
                  scope='Independent full finite coefficient and envelope witness; full dirty side basis only for small flag, central ranks and downstream analytic lifting separately reviewed')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS', args.h, 'gap', args.gap, 'roles', compiled['roles'], 'links', result['retained_links'], flush=True)


if __name__ == '__main__':
    main()
