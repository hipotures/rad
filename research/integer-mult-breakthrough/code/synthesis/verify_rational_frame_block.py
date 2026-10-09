#!/usr/bin/env python3
"""Self-contained exact binding of one rational maximum-endpoint replacement."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import pr163_bit_frame_review as V
import rational_frame_completion as F
import rational_paid_chain_endpoints as P


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'fixtures/synthesis/rational-frame-block-23272.json'
BASELINE = ROOT / 'runs/20261009T081946Z-synthesis-pr163-bit-review/results/receipt.json'


def inspect(data, tamper=None):
    h = data['h']
    source = [tuple(int(j in label) for j in range(h)) for label in data['source_labels']]
    lower, unused = V.echelon([row for frame in data['previous_bases'] for row in frame] + source, h)
    upper = V.annihilator([row for frame in data['following_bases']
                          for row in V.annihilator(frame, h)], h)
    proposed = data['proposed_integer_basis']
    if tamper == 'zero_frame':
        proposed = []
    elif tamper == 'full_outside_future':
        proposed = [tuple(int(i == j) for j in range(h)) for i in range(h)]
    V.require(F.contained(lower, proposed, h), 'All actual predecessor and source directions')
    V.require(F.contained(proposed, upper, h), 'Both actual next frames')
    V.require(F.contained(proposed, data['retained_original_basis'], h), 'Proposed frame remains within retained original')
    sums = list(map(sum, proposed))
    gram = [[9 * V.dot(a, b) - sums[i] * sums[j] for j, b in enumerate(proposed)]
            for i, a in enumerate(proposed)]
    determinant = V.determinant(gram)
    V.require(determinant == data['cleared_Gram_determinant'] == 13947137604,
              'Exact integer new-basis Gram witness')
    endpoints = P.endpoint_frames(lower, upper, F.form(h))
    V.require(endpoints['minimal_dimension'] == 9 and endpoints['maximum_dimension'] == 10,
              'The constructed maximum is attainable')
    previous = [len(rows) for rows in data['previous_bases']]
    following = [len(rows) for rows in data['following_bases']]
    old = P.widths(len(data['current_basis']), previous, following)
    new = P.widths(len(proposed), previous, following)
    V.require(list(old) == data['current_local_widths'] and list(new) == data['proposed_local_widths'],
              'Every changed-chain positive edge')
    V.require(sum(old) == sum(new) == 22 and len(new) - len(old) == -1, 'Local rank and edge count')
    multiplier = data['three_block_multiplier']
    if tamper == 'omit_three_block_factor':
        multiplier = 1
    delta = Counter(new)
    delta.subtract(Counter(old))
    delta = {rank: multiplier * count for rank, count in sorted(delta.items()) if count}
    V.require(delta == {int(rank): count for rank, count in data['total_histogram_delta'].items()},
              'Three-block histogram multiplicity')
    power = Q(data['ideal_power'])
    before = P.moment_interval(old, power.numerator, power.denominator, 48)
    after = P.moment_interval(new, power.numerator, power.denominator, 48)
    gain = multiplier * (before[0] - after[1])
    V.require(gain == Q(data['ideal_gain_lower']) > 0, 'Exact strict ideal moment improvement')
    return dict(local_old_widths=old, local_new_widths=new, local_positive_edges=[len(old), len(new)],
                three_block_positive_children=[multiplier * len(old), multiplier * len(new)],
                conserved_three_block_rank=multiplier * sum(old), histogram_delta=delta,
                ideal_power=str(power), ideal_gain_lower=str(gain), Gram_determinant=determinant)


def probe(fixture=FIXTURE, baseline=BASELINE):
    data = json.loads(Path(fixture).read_text())
    receipt = inspect(data)
    controls = []
    for tamper in ('zero_frame', 'full_outside_future', 'omit_three_block_factor'):
        try:
            inspect(data, tamper)
        except ValueError:
            controls.append(tamper)
        else:
            raise AssertionError('Adverse candidate control accepted: ' + tamper)
    prior = json.loads(Path(baseline).read_text())['components'][0]
    histogram = Counter({int(rank): count for rank, count in prior['child_histogram'].items()})
    histogram.update(receipt['histogram_delta'])
    V.require(all(rank > 0 and count > 0 for rank, count in histogram.items()), 'All complete updated profile bins')
    rank = sum(width * count for width, count in histogram.items())
    V.require(rank == prior['rank'] == 1934000 and prior['W'] * prior['m'] - rank == prior['deficit'],
              'Complete updated profile preserves stock, first moment and deficit')
    receipt.update(status='PASS EXACT RATIONAL FRAME BLOCK REPLACEMENT', negative_controls=controls,
                   complete_updated_histogram=dict(sorted(histogram.items())), W=prior['W'], m=prior['m'],
                   rank=rank, deficit=prior['deficit'], scalar_word_unchanged=True,
                   fewer_fallback_edges=True, new_Gram_exclusions_below_retained_prime_bound=True,
                   full_local_ring_or_native_or_multiplier_exponent_claim=False)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=FIXTURE)
    parser.add_argument('--baseline', type=Path, default=BASELINE)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    files = [Path(__file__).resolve(), Path(V.__file__).resolve(), Path(F.__file__).resolve(),
             Path(P.__file__).resolve(), args.fixture.resolve(), args.baseline.resolve()]
    hashes = {str(file.relative_to(ROOT)) if file.is_relative_to(ROOT) else str(file):
              sha256(file.read_bytes()).hexdigest() for file in files}
    receipt = probe(args.fixture, args.baseline)
    V.require(hashes == {str(file.relative_to(ROOT)) if file.is_relative_to(ROOT) else str(file):
                        sha256(file.read_bytes()).hexdigest() for file in files}, 'Complete standalone closure unchanged')
    receipt['source_closure'] = hashes
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
