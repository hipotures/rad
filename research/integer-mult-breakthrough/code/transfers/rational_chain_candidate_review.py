#!/usr/bin/env python3
"""Independent exact review of one rational paid-chain frame replacement.

Imports only this track's frozen matrix arithmetic, never the synthesis or
external producers. The certificate is local geometry and a strict ideal
moment comparison, not a physical word or multiplier.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import time

import rational_completion_modular_review as M


TOPIC = Path(__file__).resolve().parents[2]
FIXTURE = TOPIC / 'fixtures/synthesis/rational-frame-block-23272.json'
FIXTURE_SHA = '5758611bb6bfb2478f6df6b7bc244a4a17e3bf1e03e3c9e8276f011e9f88830a'
MATRIX_SHA = '6297988b996bb76dc4e307abbf0dbef252e088b4c257866e381f2170a6c404fd'


def contains(large, small, g):
    return M.multiply(M.projector(large, g), M.transpose(small)) == M.transpose(small)


def power_bounds(value, numerator=999, denominator=1000, bits=48):
    if value == 0:
        return Q(0), Q(0)
    grid = 1 << bits
    target = value ** numerator * grid ** denominator
    low, high = 0, value * grid + 1
    while high-low > 1:
        middle = (low+high)//2
        if middle ** denominator <= target:
            low = middle
        else:
            high = middle
    if low ** denominator == target:
        return Q(low, grid), Q(low, grid)
    return Q(low, grid), Q(high, grid)


def star_inverse(q):
    return [[Q(q+1, 4)] + [Q(1, 2)]*q] + [
        [Q(1, 2)] + [Q(int(i == j)) for j in range(q)] for i in range(q)]


def star_gram(q):
    return [[Q(4)] + [Q(-2)]*q] + [
        [Q(-2)] + [Q(int(i == j)+1) for j in range(q)] for i in range(q)]


def star_controls():
    results = []
    for q in (0, 1, 2, 9, 22):
        h = max(10, q+2)
        rows = [[int(j == 0) + 2*int(j == h-1) for j in range(h)]]
        rows.extend([[int(j == i) - int(j == h-1) for j in range(h)] for i in range(1, q+1)])
        gram = M.gram(rows, M.form(h))
        M.require(gram == star_gram(q), 'The explicit integer star basis must have its complete stated Gram matrix')
        M.require(M.determinant(gram) == 4, 'Every rational star Gram determinant must equal four')
        M.require(M.multiply(gram, star_inverse(q)) == M.identity(q+1),
                  'The entire proposed star inverse must be literal and dyadic')
        results.append(dict(h=h, difference_rows=q, dimension=q+1, determinant=4,
                            inverse_denominator=lcm(*(entry.denominator for row in star_inverse(q) for entry in row))))
    return results


def probe(data):
    h, g = data['h'], M.form(data['h'])
    current, proposed = data['current_basis'], data['proposed_integer_basis']
    original = data['retained_original_basis']
    previous, following = data['previous_bases'], data['following_bases']
    M.require(h == 24 and len(previous) == len(following) == 2,
              'Both actual role ports of the retained dimension24 operation are required')
    all_rows = [current, proposed, original] + previous + following
    M.require(all(all(isinstance(x, int) for x in row) and len(row) == h for rows in all_rows for row in rows),
              'Complete integer coordinate rows are required')
    for rows in all_rows:
        M.require(M.determinant(M.gram(rows, g)) != 0, 'Every actual neighboring frame must be nondegenerate')
    M.require(contains(original, proposed, g), 'The proposed frame must stay inside the retained original frame')
    M.require(contains(proposed, current, g), 'The proposed frame must contain the current complete frame')
    for before, after in zip(previous, following):
        M.require(contains(proposed, before, g), 'Both preceding actual frames must be contained')
        M.require(contains(after, proposed, g), 'Both following actual frames must contain the proposal')
    source_rows = [[int(i in label) for i in range(h)] for label in data['source_labels']]
    M.require(contains(proposed, source_rows, g), 'All conservative source labels must be retained')
    q = len(proposed)-1
    explicit = [[int(j == 0) + 2*int(j == 23) for j in range(h)]] + [
        [int(j == i) - int(j == 23) for j in range(h)] for i in (2,3,4,5,6,7,8,9,22)]
    M.require(proposed == explicit, 'The proposed complete integer basis must match the retained fixture exactly')
    gram = M.gram(proposed, g)
    M.require(gram == star_gram(q), 'The actual Gram must match the star formula')
    M.require(M.inverse(gram) == star_inverse(q), 'The exact inverse must have the claimed dyadic entries')
    M.require(M.determinant(gram) == 4 and data['cleared_Gram_determinant'] == 4*9**len(proposed),
              'The actual and cleared Gram determinants must not be confused')
    projector = M.projector(proposed, g)
    projection_denominator = lcm(*(x.denominator for row in projector for x in row))
    M.require(projection_denominator == 6, 'The full coordinate projector still includes the ambient factor three')
    dimensions_before = [len(x) for x in previous]
    dimensions_after = [len(x) for x in following]
    def widths(d):
        return [width for a, b in zip(dimensions_before, dimensions_after) for width in (d-a,b-d) if width]
    old, new = widths(len(current)), widths(len(proposed))
    M.require(old == data['current_local_widths'] and new == data['proposed_local_widths'],
              'All four chronological transitions must be derived from the actual ports')
    multiplier = data['three_block_multiplier']
    M.require(multiplier == 3, 'The full three-block multiplicity is required')
    delta = Counter(new)
    delta.subtract(old)
    delta = {str(width):count*multiplier for width,count in sorted(delta.items()) if count}
    M.require(delta == data['total_histogram_delta'], 'The complete positive child delta must agree')
    M.require(sum(new)==sum(old)==22 and multiplier*(len(new)-len(old)) == data['total_positive_child_change']==-3,
              'Capacity/rank and positive child-count changes are separate ledgers')
    exponent = Q(data['ideal_power'])
    M.require(exponent == Q(999,1000), 'The supplied exact moment comparison point must match')
    bounds = {x:power_bounds(x,exponent.numerator,exponent.denominator) for x in set(old+new)}
    gain = multiplier*(sum(bounds[x][0] for x in old)-sum(bounds[x][1] for x in new))
    M.require(gain == Q(data['ideal_gain_lower']) and gain>0,
              'The exact independent finite moment bound must agree')
    ratio = Q(4**4 * 2**2 * 15**15, 5**5 * 3**3 * 14**14)
    M.require(ratio<Q(1,2), 'The exact endpoint derivative ratio must be below one half')
    # log 15<3 follows from the first five terms of exp(3)>15; log2>1/2
    # follows by integrating 1/x on [1,2]. Thus D'(1)<-1/2 and
    # |D''(p)|<9*(4+2+15+5+3+14)=387 for all 0<p<=1.
    exp_three_lower = sum(Q(3)**j / factorial(j) for j in range(5))
    M.require(exp_three_lower>15 and 9*sum(old+new)==396,
              'Curvature derivation must retain the constant-width-one contribution correctly')
    # The width-one term contributes zero logarithmic curvature.
    curvature = 9*sum(x for x in old+new if x>1)
    M.require(curvature == 387, 'Only the zero-curvature width-one term may be omitted')
    derivative_margin = Q(1,2)-Q(curvature,1000)
    M.require(derivative_margin == Q(113,1000)>0, 'The all-p near-one strict comparison must have an exact positive margin')
    negatives = []
    M.require(not contains(following[0][1:], proposed, g), 'A cropped following port must fail')
    negatives.append('cropped_actual_future_port')
    outside = [int(i in (0,11,22)) for i in range(h)]
    M.require(not contains(proposed, [outside], g), 'An unretained source direction must fail')
    negatives.append('unpaid_extra_source_direction')
    M.require(sum(delta.values()) != data['local_positive_edge_change'], 'Omitting three-block multiplicity must fail')
    negatives.append('omitted_three_block_multiplicity')
    M.require(data['cleared_Gram_determinant'] != 4, 'Cleared integer determinant is not the actual rational determinant')
    negatives.append('confused_cleared_and_actual_Gram')
    return dict(status='PASS INDEPENDENT RATIONAL CHAIN CANDIDATE', h=h,
                frame_dimensions=dict(original=len(original),current=len(current),proposed=len(proposed),
                                      previous=dimensions_before,following=dimensions_after),
                conservative_sources=len(source_rows), all_actual_ports_bound=True,
                actual_Gram_determinant=4, inverse_denominator=2,
                full_projector_denominator=projection_denominator,
                new_odd_Gram_primes=[], ambient_prime_and_basis_contract_retained=True,
                old_widths=old,new_widths=new,total_histogram_delta=delta,
                rank_before=multiplier*sum(old),rank_after=multiplier*sum(new),
                positive_children_before=multiplier*len(old),positive_children_after=multiplier*len(new),
                exact_moment_gain_lower=str(gain), exact_power=str(exponent),
                derivative_ratio=str(ratio), curvature_bound=curvature,
                all_power_interval=['999/1000','1 (excluded)'],
                uniform_local_gain_lower='(113/1000)*(1-p), strict',
                negative_controls=negatives, star_family_controls=star_controls(),
                physical_or_native_word=False, exponent_claim=False)


def factorial(n):
    result=1
    for i in range(2,n+1):
        result*=i
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    source=Path(__file__).resolve()
    module=Path(M.__file__).resolve()
    M.require(sha256(module.read_bytes()).hexdigest()==MATRIX_SHA,'The frozen independent matrix source must match')
    M.require(sha256(FIXTURE.read_bytes()).hexdigest()==FIXTURE_SHA,'The complete producer fixture must match')
    closure={str(path.relative_to(TOPIC)):sha256(path.read_bytes()).hexdigest() for path in (source,module,FIXTURE)}
    start=datetime.now(timezone.utc).isoformat()
    tick=time.monotonic()
    result=probe(json.loads(FIXTURE.read_text()))
    M.require(closure=={str(path.relative_to(TOPIC)):sha256(path.read_bytes()).hexdigest() for path in (source,module,FIXTURE)},
              'Every effective source and fixture must remain unchanged')
    result['seconds']=time.monotonic()-tick
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(dict(started_utc=start,source_closure=closure,
            worker_processes=1,scope='One independent exact fixed-port geometry and ideal moment; no physical/native/exponent'),indent=2)+'\n')
        (args.output/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
