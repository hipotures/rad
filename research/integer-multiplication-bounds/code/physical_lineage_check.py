#!/usr/bin/env python3
"""Exact physical scalar verification by immutable logical-node lineage.

After the original full disjoint DAG verifier has established its scalar
map, exact child identities at every physical gate prove that map by
induction. Fresh copy destinations are required to be zero. All original
forward/reverse frame assertions and the program digest are retained.
This is a stronger sufficient check when different nodes have equal maps;
it is not a replacement for the independent mathematical transfer audit.
"""
from __future__ import annotations

import argparse
import gc
from hashlib import sha256
import json
from pathlib import Path
import time

from frame_reuse import included


def check_lineage(circuit, spaces, code, verified_map):
    """The DAG must remain unchanged between verified_map and this call."""
    assert verified_map['all_additions_disjoint']
    assert verified_map['all_partial_outputs_exact']
    assert verified_map['additions'] == circuit.additions
    assert verified_map['inputs'] == len(circuit.inputs)
    assert verified_map['partial_outputs'] == len(circuit.outputs)
    size = code['roles']
    values = [0] * size
    frames = [None] * size
    source_ids = circuit.variables
    assert len(set(code['sources'].values())) == len(code['sources'])
    assert len(code['gates']) == len(circuit.active)
    assert {row[0] for row in code['gates']} == circuit.active
    for key, slot in code['sources'].items():
        node = source_ids[key]
        assert 0 <= slot < size and circuit.args[node] is None
        values[slot] = node
        frames[slot] = spaces[node]
    for node, ins, outs in code['gates']:
        frame = spaces[node]
        assert ins and outs and outs[0] == ins[0]
        assert len(set(ins)) == len(ins) and len(set(outs)) == len(outs)
        assert set(ins) & set(outs) == {ins[0]}
        for slot in set(ins + outs):
            assert 0 <= slot < size
            assert frames[slot] is None or included(frames[slot], frame)
            frames[slot] = frame
        if circuit.args[node] is None:
            assert len(ins) == 1 and values[ins[0]] == node
        else:
            assert len(ins) == 2
            assert sorted(values[slot] for slot in ins) == sorted(circuit.args[node])
            values[ins[0]] = node
        for slot in outs[1:]:
            assert values[slot] == 0, 'A new physical copy must have a fresh zero scalar destination'
            values[slot] = node
        assert all(values[slot] == node for slot in outs)
    for target, slot in code['outputs'].items():
        assert values[slot] == circuit.outputs[target]
        assert included(frames[slot], spaces[circuit.outputs[target]])
    reverse = [None] * size
    for target, slot in code['outputs'].items():
        reverse[slot] = spaces[circuit.outputs[target]]
    for node, ins, outs in reversed(code['gates']):
        frame = spaces[node]
        for slot in set(ins + outs):
            assert reverse[slot] is None or included(frame, reverse[slot])
            reverse[slot] = frame
    for key, slot in code['sources'].items():
        assert reverse[slot] == spaces[source_ids[key]]
    digest = sha256(json.dumps({'roles': size, 'gates': code['gates'],
                               'sources': sorted(code['sources'].items()),
                               'outputs': sorted(code['outputs'].items())},
                              separators=(',', ':')).encode()).hexdigest()
    return {'all_scalar_coefficients_exact': True, 'forward_frames_nested': True,
            'reverse_complement_frames_nested': True,
            'nondegeneracy': 'Every retained frame has a common point',
            'compiled_sha256': digest}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True)
    ap.add_argument('--h', nargs='+', type=int, default=[8, 12])
    ap.add_argument('--positions-json', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    from finite_block_search import install_reference, GroupUnion
    from finite_singleton_search import singleton_class
    from fast_frame_envelope import labels
    from frame_reuse import optimize_chains, compile_reuse, check
    install_reference(args.reference)
    rows = []
    for h in args.h:
        positions = json.loads(args.positions_json.read_text())['positions'] if args.positions_json else [h//2-2]*h
        assert len(positions) == h
        cls = singleton_class()
        circuit = GroupUnion(h, lambda n, c: cls(n, positions[c], 4), 'paired', 0, True)
        original = circuit.verify()
        frames, metadata = labels(circuit, True)
        code = compile_reuse(circuit, frames, optimize_chains(circuit, frames, 'rank'))
        included.cache_clear(); gc.collect()
        at = time.monotonic(); old = check(circuit, frames, code)
        old_seconds = time.monotonic()-at
        included.cache_clear(); gc.collect()
        at = time.monotonic(); new = check_lineage(circuit, frames, code, original)
        new_seconds = time.monotonic()-at
        assert old == new
        if args.positions_json:
            expected = json.loads(args.positions_json.read_text())
            assert expected['original'] == original
            assert expected['compiled_roles'] == code['roles']
            assert expected['checked'] == new
        # A meaningful negative control: remove the consumed scalar pivot.
        bad = dict(code)
        gates = list(code['gates'])
        k = next(i for i, (node, ins, outs) in enumerate(gates) if circuit.args[node])
        node, ins, outs = gates[k]
        gates[k] = (node, (ins[0],), outs)
        bad['gates'] = gates
        try:
            check_lineage(circuit, frames, bad, original)
        except AssertionError:
            rejected = True
        else:
            raise AssertionError('Lineage checker accepted a missing scalar operand')
        rows.append(dict(h=h, roles=code['roles'], frames=metadata, checked=new,
                         original_map=original, old_seconds=old_seconds,
                         lineage_seconds=new_seconds, missing_operand_rejected=rejected,
                         scope='Full verified DAG plus exact physical child identities; unchanged frame assertions and digest'))
        included.cache_clear()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='PASS', rows=rows,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()), indent=2)+'\n')


if __name__ == '__main__':
    main()
