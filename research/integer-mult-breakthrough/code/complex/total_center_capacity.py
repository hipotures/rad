#!/usr/bin/env python3
"""Exact capacity discriminator for a single-total five-subset center basis.

Counts use a literal finite Smith word and conservative unit-add expansion.
The declared child profiles are hypotheses, not a native compiler output.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
from time import perf_counter

from center_basis_scalar_word import factor_word
from center_native_leverage import profile, TARGET
from characteristic import moment_interval, rational_root_bracket, serializable


def feature(pair, source):
    return 1 if pair == (0, 1) else int(set(pair) <= set(source))


def local_contract():
    pairs = [(i, j) for j in range(1, 7) for i in range(j)]
    columns = list(combinations(range(7), 5))
    base = [[feature(pair, source) for source in columns] for pair in pairs]
    base_word = factor_word(base)
    border_word = factor_word([[int(i != j) for j in range(5)] for i in range(5)])
    def counts(word):
        scales = [abs(gate[2]) for gate in word if gate[0] == 'scale']
        assert all(x in (1, 4) for x in scales)
        assert all(gate[3].denominator == 1 for gate in word if gate[0] == 'add')
        return dict(operations=dict(Counter(gate[0] for gate in word)),
            unit_additions=sum(int(abs(gate[3])) for gate in word if gate[0] == 'add'),
            scalar_scale_charges=sum(1 if x == 1 else 2 for x in scales))
    return dict(base_matrix=base, base_word=base_word, border_word=border_word,
                base_nonzeros=sum(bool(x) for row in base for x in row),
                base_counts=counts(base_word), border_counts=counts(border_word))


def counts(h):
    if h < 7:
        raise ValueError('The exact base uses seven labels')
    contract = local_contract()
    base, border = contract['base_counts'], contract['border_counts']
    stages = h-7
    volume = comb(h, 5)
    total_nonzeros = 11*volume-comb(h-2, 3)
    # Each new border has 4j nonzeros and a5+3(j-5) additions.
    additions = total_nonzeros + base['operations']['add']-contract['base_nonzeros']
    additions += sum(border['operations']['add']+3*(j-5)-4*j for j in range(7, h))
    unit_additions = additions + base['unit_additions']-base['operations']['add']
    unit_additions += stages*(border['unit_additions']-border['operations']['add'])
    swaps = base['operations']['swap']+stages*border['operations']['swap']
    scales = base['operations']['scale']+stages*border['operations']['scale']
    scale_charges = base['scalar_scale_charges']+stages*border['scalar_scale_charges']
    # A swap is three signed shears plus one sign scalar. Fixed integer
    # scales ±4 retain two bit-position/precision charges, rather than one.
    proxy = unit_additions+4*swaps+scale_charges
    return dict(h=h, volume=volume, center_rank=comb(h, 2),
        total_feature_nonzeros=total_nonzeros, additions=additions,
        expanded_unit_additions=unit_additions, swaps=swaps, scales=scales,
        scalar_scale_charges=scale_charges, expanded_scalar_proxy=proxy,
        proxy_per_source=Q(proxy, volume),
        base_counts=base, border_counts=border,
        source_gather_coefficients=[1],
        scope='Exact scalar word count formula. Proxy R is a paid optimistic helper hypothesis, not an actual native auxiliary count.')


def run(h):
    started = perf_counter()
    word_counts = counts(h)
    v, q = word_counts['volume'], word_counts['center_rank']
    R = word_counts['expanded_scalar_proxy']
    baseline = q*(h-2)+2
    losses = [('single-total copied-frame analogy', baseline),
              ('replace center cost by one full-width traversal', q*h),
              ('replace center cost by closed full-width release', 2*q*h),
              ('add closed full-width release to existing analogy', baseline+2*q*h)]
    rows = []
    for hypothesis, loss in losses:
        p = profile(h, R, loss, 'rank1')
        interval = moment_interval(p, TARGET)
        # Some conservative additive ledgers have no positive root at all.
        root = rational_root_bracket(p) if p['deficit'] > 0 else None
        rows.append(dict(center_cost_hypothesis=hypothesis, profile=p,
            target=TARGET, target_moment_interval=interval,
            target_status='below1' if interval[1] < 1 else 'above1' if interval[0] > 1 else 'unresolved',
            root_bracket=root))
    return dict(status='CONDITIONAL SINGLE-TOTAL CAPACITY DISCRIMINATOR',
        h=h, scalar_counts=word_counts, rows=rows,
        elapsed_seconds=perf_counter()-started,
        obligations=['All native source and sink adapters are paid',
                     'Actual auxiliary count does not exceed the declared expanded scalar proxy',
                     'The proposed center loss replaces the old cost only if that old chronology is removed',
                     'Every residual call is included in the worst rank-one placement',
                     'Fixed scalar guard, all dirty restoration, routing, binary transfer and outer multiplication remain verified separately'],
        scope='Exact moments of unattained complete profiles. A positive capacity result is not an exponent certificate or evidence that a native frame chronology attains the profile.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, choices=(24, 28, 30, 32, 34), required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Use a fresh attempt path')
    result = run(args.h)
    result['source_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(serializable(result), indent=2)+'\n')
    print(json.dumps(dict(h=args.h, proxy_per_source=str(result['scalar_counts']['proxy_per_source']),
        target=[dict(cost=row['center_cost_hypothesis'], status=row['target_status']) for row in result['rows']])), flush=True)


if __name__ == '__main__':
    main()
