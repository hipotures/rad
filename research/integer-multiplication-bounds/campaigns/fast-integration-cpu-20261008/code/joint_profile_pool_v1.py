#!/usr/bin/env python3
"""Exact joint controller search over a frozen pool of original I+J profiles.

At a fixed saving, each axis contributes independently to numerator minus mW.
Thus two linear pool scans replace a Cartesian scan of every pair. Positive
width weights are enclosed with rational logarithms and a common dyadic grid.
Only the ordered23/25 inherited data geometry is used.
"""
import argparse
from collections import Counter
import datetime
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
DYADIC = 1 << 128
DENOMINATOR = 10**16


def score_module():
    path = ROOT/'agents/scout/code/fixed_controller_score.py'
    spec = importlib.util.spec_from_file_location('score', path)
    score = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(score)
    return score


def load_pool(directory, h, extras):
    pool, sources = {}, []
    paths = list(directory.glob('*.bin.fixed_ij_profiles.json')) + extras
    for path in sorted(set(paths)):
        raw = path.read_bytes()
        row = json.loads(raw)
        if row.get('h') != h:
            continue
        assert row['v'] == comb(h, 3) and row['loss'] == h*(h-1)
        assert row['crt_disagreements'] == 0
        assert sum(t*n for t, n in enumerate(row['blocks'])) == row['rank_sum']
        assert row['rank_sum'] == h*row['R'] + 2*row['loss']
        signature = (row['R'], row['loss'], tuple(row['blocks']))
        identity = dict(path=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        sources.append(identity)
        if signature not in pool:
            pool[signature] = dict(profile=row, sources=[])
        pool[signature]['sources'].append(identity)
    assert pool
    return list(pool.values()), sources


def axis_terms(row, m, N):
    h, copies = row['h'], N//row['v']
    blocks = list(row['blocks'])
    blocks[h] -= h
    blocks[1] += h
    assert min(blocks) >= 0
    terms = Counter({t: n*copies for t,n in enumerate(blocks) if t and n})
    bank = copies*row['R']
    terms[h] += bank
    terms[m-2*h] += bank
    return terms, bank


def fixed_terms(N):
    terms = Counter({1: 19*N, 21: 2*N, 17: 2*N, 481: 2*N})
    # Data has eighteen N singleton blocks; paid endpoint adds N.
    for h in (23,25):
        terms[1] += 2*N
        terms[h-2] += 2*N
    return terms


def weights(score, widths, saving, m):
    low, high = {}, {}
    for t in widths:
        x,y = (saving*z for z in score.logarithms(Q(m,t)))
        assert 0 <= x <= y < 1
        a = t*(1+x+x*x/2+x*x*x/6)
        b = t*(1+y+y*y/(2*(1-y/3)))
        low[t] = (a.numerator*DYADIC)//a.denominator
        high[t] = (b.numerator*DYADIC+b.denominator-1)//b.denominator
    return low,high


def minimum(rows, axis, weight, m):
    values = [sum(n*weight[t] for t,n in terms.items())-m*bank*DYADIC
              for terms,bank in axis]
    index = min(range(len(rows)), key=lambda i: (values[i], rows[i]['sources'][0]['path']))
    return values[index], index


def scan(score, pools, axes, constant, tick, m, N):
    widths = set(constant)
    for axis in axes:
        for terms,_ in axis:
            widths.update(terms)
    low,high = weights(score,widths,Q(tick,DENOMINATOR),m)
    answer = dict(tick=tick)
    for label,weight in [('lower',low),('upper',high)]:
        values = [minimum(pool,axis,weight,m) for pool,axis in zip(pools,axes)]
        value = sum(n*weight[t] for t,n in constant.items())-2*m*N*DYADIC
        value += sum(v for v,_ in values)
        answer[label+'_numerator_minus_mW_dyadic'] = str(value)
        answer[label+'_indices'] = [i for _,i in values]
    answer['some_pair_strictly_passes'] = int(answer['upper_numerator_minus_mW_dyadic']) < 0
    answer['all_pairs_strictly_fail'] = int(answer['lower_numerator_minus_mW_dyadic']) >= 0
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--first-directory', required=True, type=Path)
    parser.add_argument('--second-directory', required=True, type=Path)
    parser.add_argument('--first-extra', action='append', type=Path, default=[])
    parser.add_argument('--second-extra', action='append', type=Path, default=[])
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--margin-ticks', type=int, default=1000)
    args = parser.parse_args()
    began = time.time()
    args.output.mkdir(parents=True,exist_ok=False)
    score = score_module()
    first,first_sources = load_pool(args.first_directory,23,args.first_extra)
    second,second_sources = load_pool(args.second_directory,25,args.second_extra)
    pools = [first,second]
    m,N = 575,comb(23,3)*comb(25,3)
    axes = [[axis_terms(row['profile'],m,N) for row in pool] for pool in pools]
    constant = fixed_terms(N)
    protocol = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    pool_sizes=[len(pool) for pool in pools],
                    input_files=[first_sources,second_sources],
                    grid_denominator=DENOMINATOR,weight_grid=DYADIC,
                    margin_ticks=args.margin_ticks,
                    source=Path(__file__).read_text(),
                    score_sha256=hashlib.sha256((ROOT/'agents/scout/code/fixed_controller_score.py').read_bytes()).hexdigest(),
                    selection='Frozen original-envelope fixed I+J moment pool; independent axis minima at each saving',
                    scope='Exact finite pool optimization; new producers require independent native/all-size review.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    # The separable expression must equal the complete controller at zero.
    zero = scan(score,pools,axes,constant,0,m,N)
    expected = score.profile(first[0]['profile'],second[0]['profile'])
    assert int(zero['lower_numerator_minus_mW_dyadic']) == -expected['deficit']*DYADIC
    assert zero['lower_numerator_minus_mW_dyadic'] == zero['upper_numerator_minus_mW_dyadic']
    trials = [zero]
    lo,hi = 0,10**12
    endpoint = scan(score,pools,axes,constant,hi,m,N)
    assert endpoint['all_pairs_strictly_fail'], 'Search ceiling must exclude the entire frozen pool'
    trials.append(endpoint)
    while hi-lo > 1:
        mid = (lo+hi)//2
        trial = scan(score,pools,axes,constant,mid,m,N)
        trials.append(trial)
        if trial['some_pair_strictly_passes']:
            lo = mid
        else:
            assert trial['all_pairs_strictly_fail'], 'Enclosure overlap: increase arithmetic accuracy before claiming a bracket'
            hi = mid
    assert lo > args.margin_ticks > 0
    safe_tick = lo-args.margin_ticks
    final = scan(score,pools,axes,constant,safe_tick,m,N)
    assert final['some_pair_strictly_passes']
    selected = [pool[i] for pool,i in zip(pools,final['upper_indices'])]
    counts = score.profile(*(row['profile'] for row in selected))
    saving = Q(safe_tick,DENOMINATOR)
    moment = score.moment(m,counts['W'],counts['child_multiplicities'],saving)
    assert moment['strictly_passes']
    upper_weights = weights(score,constant.keys() | counts['child_multiplicities'].keys(),saving,m)[1]
    complete_upper = sum(n*upper_weights[t] for t,n in counts['child_multiplicities'].items())-m*counts['W']*DYADIC
    assert complete_upper == int(final['upper_numerator_minus_mW_dyadic'])
    result = dict(status='exact_joint_frozen_pool_search',pool_sizes=protocol['pool_sizes'],
                  pair_combinations=len(first)*len(second),strict_threshold_grid=[lo,hi],
                  saving=str(saving),candidate_kappa=str(saving*Q(99999,100000)),
                  selected=selected,complete_controller=score.jsonable(counts),
                  independent_complete_expression_match=True,verified_moment=moment,
                  grid_trials=trials,final_trial=final,elapsed_seconds=time.time()-began,
                  scope=protocol['scope'])
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],pool_sizes=result['pool_sizes'],
                         pair_combinations=result['pair_combinations'],saving=result['saving'],
                         candidate_kappa=result['candidate_kappa'],
                         selected=[r['sources'][0]['path'] for r in selected],seconds=result['elapsed_seconds'])),flush=True)


if __name__ == '__main__':
    main()
