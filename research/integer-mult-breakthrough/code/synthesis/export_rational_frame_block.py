#!/usr/bin/env python3
"""Export the complete ports of one retained single-operation block candidate."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import pr163_paid_chain_probe as L
import pr163_bit_frame_review as V


ROOT = Path(__file__).resolve().parents[2]


def export(reference, certificate, operation=23272):
    L.initialize(reference, 999, 1000)
    s = L.STATE
    graph, word, frames = s['graph'], s['word'], s['frames']
    a, b, node = word['ops'][operation]
    certificate = Path(certificate).resolve()
    rows = json.loads(certificate.read_text())['cases']
    case = next(row for row in rows if row['block_id'] == operation)
    V.require(case['operation_indices'] == [operation], 'This exporter binds one complete operation cut')
    candidate = next(item for item in case['candidates'] if item['strictly_improving_ideal'])
    basis = [[Q(*pair) for pair in row] for row in candidate['exact_basis']]
    V.require(all(x.denominator == 1 for row in basis for x in row), 'Explicit integer candidate basis')
    basis = [[int(x) for x in row] for row in basis]
    previous = [s['before'][operation, role] for role in (a, b)]
    following = [s['after'][operation, role] for role in (a, b)]
    old = frames.B[int(word['node_frame'][str(node)])]
    return dict(h=graph['h'], operation_indices=[operation], role_ids=[a, b],
                current_basis=frames.B[s['chosen'][operation]], retained_original_basis=old,
                previous_bases=[[] if frame is None else frames.B[frame] for frame in previous],
                following_bases=[frames.B[frame] for frame in following],
                source_labels=[graph['labels'][source] for source in V.bits(s['supports'][node])],
                proposed_integer_basis=basis, current_local_widths=[4, 1, 2, 15],
                proposed_local_widths=[5, 3, 14], local_positive_edge_change=-1,
                three_block_multiplier=3, total_positive_child_change=-3,
                total_histogram_delta=candidate['histogram_delta'], ideal_power='999/1000',
                ideal_gain_lower=candidate['ideal_moment_gain_lower'],
                cleared_Gram_determinant=candidate['cleared_Gram_determinant'],
                new_basis_denominators_one=True, reference_head=V.REFERENCE_HEAD,
                reference_inputs=V.INPUTS,
                complete_original_raw=dict(path=str(certificate.relative_to(ROOT)),
                                           sha256=sha256(certificate.read_bytes()).hexdigest()),
                scope='One exact rational operation-frame replacement with fixed actual ports and unchanged scalar word; ideal moment only')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--certificate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = export(args.reference, args.certificate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(sha256(args.output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
