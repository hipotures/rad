#!/usr/bin/env python3
"""Separate raw-basis determinant witness for the unchanged PR163 review.

The first completed review used the smaller-side dual determinant for high-
dimensional frames. This entrypoint retains that witness with its normalization
explicit and independently adds every raw 9*B*G*B^T determinant.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import pr163_bit_frame_review as V


def prime_witness(reference):
    graph, word, records, partners, profile, descent = V.read_inputs(reference)
    h = graph['h']
    determinants = []
    for i, basis in descent['frames']:
        sums = list(map(sum, basis))
        matrix = [[9 * V.dot(a, b) - sums[row] * sums[column]
                   for column, b in enumerate(basis)] for row, a in enumerate(basis)]
        value = V.determinant(matrix)
        V.require(0 < abs(value) < 2 ** 80, 'Every raw new-basis Gram exclusion is below 2^80')
        determinants.append(value)
    ambient = 9 ** (h - 1) * (9 - h)
    V.require(0 < abs(ambient) < 2 ** 80, 'Ambient exclusion below 2^80')
    unique = {json.dumps(basis, separators=(',', ':')) for i, basis in descent['frames']}
    return dict(status='PASS RAW BASIS PRIME WITNESSES', new_operations=len(determinants),
                unique_raw_bases=len(unique), maximum_raw_Gram_determinant_bits=max(abs(x).bit_length() for x in determinants),
                ambient_cleared_Gram_determinant=ambient, ambient_bits=abs(ambient).bit_length(),
                all_basis_denominators_one=True, all_new_nonzero_exclusions_below_2_to_80=True,
                inherited_unchanged_frame_exclusions_required=True,
                local_ring_compiler_and_native_fees_not_verified=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve()
    original = Path(V.__file__).resolve()
    hashes = {path.name: sha256(path.read_bytes()).hexdigest() for path in (source, original)}
    receipt = prime_witness(args.reference)
    V.read_inputs(args.reference)
    V.require(hashes == {path.name: sha256(path.read_bytes()).hexdigest() for path in (source, original)},
              'Prime review runtime source unchanged')
    receipt['source_closure'] = hashes
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
