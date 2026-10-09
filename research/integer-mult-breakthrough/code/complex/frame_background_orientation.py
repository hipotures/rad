#!/usr/bin/env python3
"""Exact distinction between left and right full backgrounds on nongraph frames.

This is a control for composing framed shears. It does not reject the valid
right-background signed-SWAP word or all possible joint chronologies.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import canonical_subspace_frames as f


def product(A, B, adjoint=False):
    size = len(A); result = [[(0, 0)] * size for _ in range(size)]
    for x in range(size):
        for y in range(size):
            value = (0, 0)
            for k in range(size):
                value = f.add(value, f.mul(A[x][k], f.conj(B[y][k]) if adjoint else B[k][y]))
            result[x][y] = value
    return result


def normalized_relative(A, B, denbits):
    numerator = product(A, B, True)
    size = len(A)
    support = [sum(numerator[x][y] != (0, 0) for x in range(size)) for y in range(size)]
    if len(set(support)) != 1 or support[0] != 1 << (support[0].bit_length() - 1):
        raise AssertionError('Clifford relative support is not uniformly flat')
    rank = support[0].bit_length() - 1
    divisor = 1 << (denbits - rank)
    if any(z % divisor for row in numerator for pair in row for z in pair):
        raise AssertionError('Exact relative grid disagrees with its mixing rank')
    return [[(z[0] // divisor, z[1] // divisor) for z in row] for row in numerator], rank


def probe(n, source, E):
    line = f.frame_matrix((source,), n); target = f.frame_matrix(E, n)
    full = f.frame_matrix(tuple(1 << j for j in range(n)), n)
    A = line['numerator']; B = target['numerator']; G = full['numerator']
    den = line['denominator_bits'] + target['denominator_bits']
    original, rank = normalized_relative(B, A, den)
    right, right_rank = normalized_relative(product(B, G), product(A, G), den + 2 * n)
    left, left_rank = normalized_relative(product(G, B), product(G, A), den + 2 * n)
    if original != right or right_rank != len(f.basis(E)) - 1:
        raise AssertionError('Right common background failed literal cancellation')
    right_nf = f.compile_matrix(right, n, right_rank)
    left_nf = f.compile_matrix(left, n, left_rank)
    columns = f.frame_spec(E, n)['routing_columns']
    complement = columns[len(f.basis(E)):]
    predicted_left = len(f.basis(E)) - 1 if all(not f.dot(source, c) for c in complement) else len(f.basis(E)) + 1
    if left_rank != predicted_left:
        raise AssertionError('Left-background complement obstruction formula failed')
    return dict(n=n, source=source, intermediate_subspace=f.basis(E),
                generic_routing_complement=complement,
                original_rank=rank, right_background_rank=right_rank,
                right_actual_relative_operator_unchanged=True,
                left_background_rank=left_rank, extra_left_rank=left_rank - right_rank,
                right_normal_form=right_nf, left_normal_form=left_nf)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    source = Path(__file__); dependency = Path(f.__file__)
    hashes = {source.name: sha256(source.read_bytes()).hexdigest(),
              dependency.name: sha256(dependency.read_bytes()).hexdigest()}
    cases = [probe(3, 4, (3, 4)), probe(3, 7, (3, 4)),
             probe(4, 1, (1, 7)), probe(4, 7, (1, 7))]
    if [c['extra_left_rank'] for c in cases] != [0, 2, 0, 2]:
        raise AssertionError('Required positive and negative orientation controls changed')
    receipt = dict(status='PASS EXACT COMMON-BACKGROUND ORIENTATION CONTROL',
                   started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
                   source_sha256=hashes, cases=cases,
                   scope='Actual left/right multiplication controls on canonical Gaussian frames. Right background is valid; three-shear helper traversal counts and all alternative SWAP/native recurrences remain separate.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(status=receipt['status'], cases=len(cases),
                          extra_left_ranks=[c['extra_left_rank'] for c in cases],
                          right_relative_operators_unchanged=True)))


if __name__ == '__main__':
    main()
