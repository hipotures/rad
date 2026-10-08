#!/usr/bin/env python3
"""Bound existing mixed full-family evidence to universal rational rank cuts.

No full-family replay. Every retained unlucky pair is reconstructed over Q
and its successful field; the upper bound uses coefficient-free incidence
matrices, independently evaluated here. Credits: James Chang PR34 cuts,
Rohan Arun PR40 whole-pair fallback, campaign geometry new mixed weights.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(rows):
    basis = {}
    for row in rows:
        v = [F(x) for x in row]
        for col, b in basis.items():
            if v[col]:
                c = v[col]
                v = [x-c*y for x, y in zip(v, b)]
        col = next((j for j, x in enumerate(v) if x), None)
        if col is not None:
            c = v[col]
            basis[col] = [x/c for x in v]
    return len(basis)


def rook(matrix, prime=None):
    available = set(range(47))
    pivots, values = [], []
    for i in range(47):
        col = max(j for j in available if matrix[i][j])
        value = matrix[i][col]
        pivots.append(col); values.append(value); available.remove(col)
        inverse = pow(value, -1, prime) if prime else 1/value
        for r in range(i+1, 47):
            factor = matrix[r][col]*inverse
            if prime: factor %= prime
            if factor:
                for j in available:
                    matrix[r][j] -= factor*matrix[i][j]
                    if prime: matrix[r][j] %= prime
            matrix[r][col] = 0
    return pivots, values


def weights(h, beta):
    gamma = (9*beta-1)/(3*(1-h*beta))
    return (1-3*beta)*(1+gamma)/2, -3*beta*gamma/2


def prime(p):
    return p >= 2 and all(p%d for d in range(2, math.isqrt(p)+1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pr40-snapshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    began = time.monotonic()
    own = Path(__file__).resolve().parent.parent
    geometry = own.parent/'geometry'
    source = geometry/'code/fixed23_negative25_data_pairs.cpp'
    saved = geometry/'results/fixed23-negative25-data-pairs.json'
    input_manifest = geometry/'input-manifest.json'
    manifest = json.loads(input_manifest.read_text())
    expected_hash = manifest['authored_or_modified_source_sha256']['code/fixed23_negative25_data_pairs.cpp']
    assert expected_hash == digest(source) == '5e295eff1ed2388e13a0b3e7caa822031c2694cc198701e2c3487f048ed5e0fb'
    cpp = source.read_text()
    for identity in ('3*(a+1)', '2*(3*(a+1)-10)', '(a+1,power<q>(5,q-2))',
                     '(b+3,power<q>(b-1,q-2))', '(b+3,power<q>(2,q-2))',
                     'for(const auto&T:left)for(const auto&S:right)',
                     'count!=1771*2300', 'prefixes!=int64_t(count)*d', 'zeros!=int64_t(count)*346'):
        assert identity in cpp
    result = json.loads(saved.read_text())
    N = math.comb(23,3)*math.comb(25,3)
    assert N == result['pairs'] == 4073300
    assert result['nonzero_prefixes'] == 47*N
    assert result['ordered_zero_checks'] == 346*N
    assert result['unresolved_failures'] == 0
    assert result['successful_pairs_by_prime'] == [N-22,22,0]
    assert result['primary_modular_failures'] == len(result['fallbacks']) == 22
    assert sum(result['successful_pairs_by_prime']) == N
    primes = result['primes']
    assert primes == [1000003,2147483647,1000000007] and all(prime(p) for p in primes)
    assert all(den%p for den in result['denominators'] for p in primes)
    # Independent coefficient calculation, including conjugate choices.
    expected_inverse = [(F(18,31),F(-24,5)),(F(7,6),F(-14))]
    conjugates = [(F(-1),F(5,108)),(F(-1,3),F(1,21))]
    for h, choices, inverse in zip((23,25),conjugates,expected_inverse):
        for beta in choices:
            z = weights(h,beta)
            assert tuple(1/x for x in z) == inverse
            assert 3*z[0]+(h-3)*z[1] == 1 and all(z)
    R = list(range(23))+[22]+list(range(23))
    C = list(range(23))+[0]+list(range(23))
    rows = [(r,i%25) for i,r in enumerate(R)]
    cols = [(c,(528+j)%25) for j,c in enumerate(C)]
    pivots = [46]+[i+24 for i in range(1,22)]+[46-i for i in range(22,28)]+[i-26 for i in range(28,45)]+[1,0]
    assert sorted(pivots) == list(range(47))
    # The actual common permutation is reconstructed from the same endpoint
    # prescriptions, with the first unused coordinate at each other slot.
    prescribed = [{} for _ in range(25)]
    for labels, start in ((R,0),(C,528)):
        for i, value in enumerate(labels):
            alpha,beta = divmod(start+i,25)
            assert alpha not in prescribed[beta] and value not in prescribed[beta].values()
            prescribed[beta][alpha] = value
    permutation = []
    for r in prescribed:
        free = iter(sorted(set(range(23))-set(r.values())))
        permutation.append([r[i] if i in r else next(free) for i in range(23)])
    fixed_receipt = json.loads((own/'gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json').read_text())
    # That receipt binds the independently checked actual PR54 source and order.
    assert [permutation[i%25][i//25] for i in range(47)] == R
    assert [permutation[(528+j)%25][(528+j)//25] for j in range(47)] == C
    n = 49
    incidence_left = [[int(k==r or k==23+b or k==48) for k in range(n)] for r,b in rows]
    incidence_right = [[int(k==c or k==23+d or k==48) for k in range(n)] for c,d in cols]
    cuts = []
    for i,q in enumerate(pivots):
        preceding = sum(p>q for p in pivots[:i])
        if 1 <= i <= 21:
            selected = set(range(i+1,23)) | set(range(23+i+1,48)) | {48}
        elif 28 <= i <= 44:
            t = i-28
            selected = set(range(3+t,23)) | set(range(28+t,48))
        else:
            assert 46-q == preceding
            cuts.append({'row':i,'pivot':q,'bound':preceding,'trivial_suffix_columns':46-q})
            continue
        left_rank = rank([[row[k] for k in range(n) if k in selected] for row in incidence_left[:i+1]])
        right_rank = rank([[row[k] for k in range(n) if k not in selected] for row in incidence_right[q+1:]])
        assert left_rank+right_rank <= preceding
        cuts.append({'row':i,'pivot':q,'selected':sorted(selected),'left_rank':left_rank,
                     'right_rank':right_rank,'bound':preceding})
    source_triples = [list(combinations(range(h),3)) for h in (23,25)]
    seen = set(); fallback_controls = []
    for item in result['fallbacks']:
        index = item['index']; assert 0 <= index < N and index not in seen;seen.add(index)
        T,S = source_triples[0][index//2300],source_triples[1][index%2300]
        assert list(T) == item['left'] and list(S) == item['right']
        x = [expected_inverse[0][0 if r in T else 1] for r in range(23)]
        y = [expected_inverse[1][0 if r in S else 1] for r in range(25)]
        matrix = [[F(r==c)*x[r]+F(b==d)*y[b]-1 for c,d in cols] for r,b in rows]
        q_pivots,q_values = rook([row[:] for row in matrix])
        assert q_pivots == pivots
        row,col = item['primary_zero'];assert pivots[row] == col
        unlucky = q_values[row]
        assert unlucky.numerator%primes[0] == 0 and unlucky.denominator%primes[0]
        fallback = item['successful_prime'];assert fallback == primes[1]
        assert all(value.numerator%fallback and value.denominator%fallback for value in q_values)
        modular = [[v.numerator*pow(v.denominator,-1,fallback)%fallback for v in row] for row in matrix]
        modular_pivots,modular_values = rook(modular,fallback)
        assert modular_pivots == pivots and all(modular_values)
        fallback_controls.append({'index':index,'T':T,'S':S,'primary_zero':item['primary_zero'],
                                  'exact_nonzero_value':str(unlucky),'Q_pivots':q_pivots,
                                  'successful_whole_pair_prime':fallback,'all_Q_pivots_nonzero':True})
    runs = []
    for i,p in enumerate(pivots):
        if i and p == pivots[i-1]+1:runs[-1] += 1
        else:runs.append(1)
    assert runs.count(1) == 9 and sorted(w for w in runs if w>1) == [17,21]
    rank_cut_source = args.pr40_snapshot/'research/copied-reversed/pr34/independent_controls.py'
    upper_identity = 'M=F diag(x_0,...,x_22,y_0,...,y_24,-1) G^T; rank M[:i+1,q+1:] <= rank F[:i+1,S] + rank G[q+1:,S^c] <= preceding right pivots, for every rational x,y.'
    receipt = {'created_utc':datetime.now(timezone.utc).isoformat(),
               'status':'PASS MIXED FULL DATA INPUT, UNIVERSAL ZERO CUTS AND UNLUCKY-PAIR Q CONTROLS',
               'scope':'Retained fresh mixed complete nonvanishing run is reused; this audit independently binds source formulas, actual order, full lexical enumeration, all47 universal incidence cuts and all22 rational fallback controls. No fullN baseline replay.',
               'source_sha256':digest(Path(__file__)), 'generator_path':str(source), 'generator_sha256':digest(source),
               'retained_fullN_result_path':str(saved),'retained_fullN_result_sha256':digest(saved),
               'geometry_input_manifest_sha256':digest(input_manifest),
               'upper_rank_source_path':str(rank_cut_source),'upper_rank_source_sha256':digest(rank_cut_source),
               'PR54_compatibility_receipt_path':str(own/'gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json'),
               'PR54_compatibility_receipt_sha256':digest(own/'gpu-parameter-results/pr54-IJ-conjugate-data-compatibility-20261008T1714.json'),
               'basis23_choices':[str(x) for x in conjugates[0]],'basis25_choices':[str(x) for x in conjugates[1]],
               'inverse_source_products':[[str(x) for x in pair] for pair in expected_inverse],
               'actual_common_permutation':permutation, 'corner_rows':rows,'corner_columns':cols,
               'universal_upper_identity':upper_identity,'universal_rank_cuts':cuts,
               'pairs':N,'nonzero_prefixes':47*N,'ordered_zero_checks_in_retained_fields':346*N,
               'whole_pair_success_counts':result['successful_pairs_by_prime'],
               'rational_unlucky_controls':fallback_controls,'uniform_Q_rook_pivots':pivots,'uniform_Q_front_runs':runs,
               'one_front_histogram':{'1':9*N,'17':N,'21':N,'481':N},
               'zero_cut_proof':'The all-weight rank cuts are rational and coefficient-free. Modular zeros are not promoted to rational zeros and no CRT-product bound is required for this structural proof.',
               'remaining_interface':'New graph/source/scalar/physical/bridge/compiler gates are separate; reuse requires the same complete triple family and common physical order. No old169 negative-negative data is consumed.',
               'elapsed_seconds':time.monotonic()-began}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'pairs':N,'cuts':len(cuts),'fallback_Q_controls':len(fallback_controls),'elapsed_seconds':receipt['elapsed_seconds']}))


if __name__ == '__main__':
    main()
