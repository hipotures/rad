#!/usr/bin/env python3
"""Self-contained exact checks of three retained PR163 rational operation cuts."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import pr163_bit_frame_review as V
import rational_frame_completion as F
import rational_paid_chain_endpoints as P


DEFAULT_FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures/synthesis/pr163-bit-frame-review-contract.json'


def check_case(case, h, tamper=None):
    basis = case['selected_basis']
    if tamper == 'zero_operation_frame':
        basis = []
    elif tamper == 'full_frame_outside_future_cap':
        basis = [tuple(int(i == j) for j in range(h)) for i in range(h)]
    reduced, unused = V.echelon(basis, h)
    V.require(len(reduced) == len(basis), 'Selected frame independence')
    vectors = [tuple(int(j in label) for j in range(h)) for label in case['source_labels']]
    lower, unused = V.echelon([row for rows in case['previous_bases'] for row in rows] + vectors, h)
    upper = V.annihilator([row for rows in case['following_bases'] for row in V.annihilator(rows, h)], h)
    V.require(F.contained(lower, basis, h), 'Complete source and previous-role span')
    V.require(F.contained(basis, upper, h), 'Both future role caps')
    V.require(F.contained(basis, case['old_basis'], h), 'Retained operation-frame descent')
    sums = list(map(sum, basis))
    gram = [[9 * V.dot(a, b) - sums[i] * sums[j] for j, b in enumerate(basis)] for i, a in enumerate(basis)]
    determinant = V.determinant(gram)
    V.require(determinant != 0, 'Exact characteristic-zero Gram determinant')
    endpoints = P.endpoint_frames(lower, upper, F.form(h))
    d = len(basis)
    V.require(endpoints['minimal_dimension'] <= d <= endpoints['maximum_dimension'], 'Constructive endpoint dimensions')
    return dict(operation=case['operation'], dimensions=[endpoints['minimal_dimension'], d, endpoints['maximum_dimension']],
                lower_radical_dimension=len(endpoints['lower_radical']), integer_Gram_determinant=determinant)


def probe(fixture):
    data = json.loads(Path(fixture).read_text())
    V.require(data['reference_head'] == V.REFERENCE_HEAD and data['input_sha256'] == V.INPUTS,
              'Frozen upstream and input closure')
    V.require(data['h'] == 24 and len(data['cases']) == 3, 'Complete bounded contract shape')
    rows = [check_case(case, data['h']) for case in data['cases']]
    controls = []
    for tamper in ('zero_operation_frame', 'full_frame_outside_future_cap'):
        try:
            check_case(data['cases'][0], data['h'], tamper)
        except ValueError:
            controls.append(tamper)
        else:
            raise AssertionError('Adverse bounded frame accepted: ' + tamper)
    return dict(status='PASS BOUNDED PR163 RATIONAL FRAME CONTRACT', cases=rows,
                negative_controls=controls, complete_scalar_word_not_replayed=True,
                rational_geometry_only=True, odd_local_ring_and_native_contracts_not_assumed=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    files = [Path(__file__).resolve(), Path(V.__file__).resolve(), Path(F.__file__).resolve(),
             Path(P.__file__).resolve(), args.fixture.resolve()]
    hashes = {file.name: sha256(file.read_bytes()).hexdigest() for file in files}
    result = probe(args.fixture)
    V.require(hashes == {file.name: sha256(file.read_bytes()).hexdigest() for file in files}, 'Bounded review source/input closure unchanged')
    result['source_closure'] = hashes
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
