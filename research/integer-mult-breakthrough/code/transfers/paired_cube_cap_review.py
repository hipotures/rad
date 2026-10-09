#!/usr/bin/env python3
"""Import-free coefficient and support review of paid paired-cube channels.

The producer's literal words and native chronology are source-reviewed, not
executed here. These controls independently construct their small scalar maps,
dyadic completions, decoder supports and terminal-reader counting formula.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time


TOPIC = Path(__file__).resolve().parents[2]
REVIEWED = {
    'code/complex/paired_five_cube_discriminator.py': '720cf5d50d3afe4072a91ab013a5516e1cd28f3902b04edc608aefe5257c49c8',
    'code/complex/paired_cap_dirty_completion.py': 'e4b02d24bc93dd3f41279f07c312c637f9126da7f31191189448d4f49eaa87cf',
    'code/complex/paired_cap_fanout_flags.py': '5ebf72e309c42f9b654cff84f0c05585da3cbfdbfebc5d7b6156f6ce31ce41df',
}


def require(value, message):
    if not value:
        raise AssertionError(message)


def span(values):
    pivots = {}
    for value in values:
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            pivots[value.bit_length()-1] = value
    return tuple(pivots.values())


def multiply(left, right):
    columns = list(zip(*right))
    return [[sum(a*b for a, b in zip(row, col)) for col in columns]
            for row in left]


def inversion(matrix):
    n = len(matrix)
    rows = [list(row)+[F(i==j) for j in range(n)] for i, row in enumerate(matrix)]
    det = F(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, 'The independently assembled completion must be nonsingular')
        if pivot != j:
            rows[pivot], rows[j] = rows[j], rows[pivot]
            det = -det
        divisor = rows[j][j]
        det *= divisor
        rows[j] = [x/divisor for x in rows[j]]
        for i in range(n):
            if i != j:
                coefficient = rows[i][j]
                rows[i] = [a-coefficient*b for a, b in zip(rows[i], rows[j])]
    return [row[n:] for row in rows], det


def selector(bits, width, parity):
    return bits | (((bits.bit_count()+parity) % 2) << (width-1))


def label(pairs, bits):
    return sum(1 << (2*p+(bits >> j & 1)) for j, p in enumerate(pairs))


def side(overlap):
    return -F((overlap-1)*(overlap-3), 8)


def cap_case(task):
    j, parity = task
    n = 1 << (j-1)
    targets = [selector(t, j, parity) for t in range(n)]
    sources = [selector(s, j, (parity+j) % 2) for s in range(n)]
    matrix = [[side(j-(s ^ t).bit_count()) for s in sources] for t in targets]
    characters = [[F((-1)**((u&a).bit_count())) for u in range(n)] for a in range(n)]
    zero = [a for a, row in enumerate(characters)
            if all(not value[0] for value in multiply(matrix, [[x] for x in row]))]
    require(len(zero) == n-3, 'Both independently built parity blocks must have rank three')
    completion = matrix[:3]+[characters[a] for a in zero]
    inverse, determinant = inversion(completion)
    require(abs(determinant) == (F(1,8) if j==3 else F(32)),
            'The completion must have the stated power-two determinant')
    require(all(x.denominator & (x.denominator-1) == 0 for row in inverse for x in row),
            'The complete inverse must be dyadic')
    decoder = multiply(matrix, inverse)
    require(all(not x for row in decoder for x in row[3:]), 'Kernel coordinates cannot appear in a target read')
    require(all(x.denominator==1 for row in decoder for x in row[:3]), 'Actual-row reconstruction is integral')
    require(multiply([row[:3] for row in decoder], matrix[:3]) == matrix,
            'Every complete target row must be reconstructed')
    local_targets = [[label(tuple(range(j))+tuple(range(5, 10-j)),
                                  t | (outside << j))
                      for outside in range(1 << (5-j))] for t in targets]
    buckets = [[label(tuple(range(5)), s | (outside << j))
                for outside in range(1 << (5-j))] for s in sources]
    source_cap = span(x for bucket in buckets for x in bucket)
    require(len(source_cap)==5 and all(len(span(bucket))==6-j for bucket in buckets),
            'Actual aggregate input and common-cap dimensions must be charged')
    local_spans = []
    for root in range(3):
        fanout = [t for index, row in enumerate(decoder) if row[root] for t in local_targets[index]]
        local_spans.append(len(span(fanout)))
        require(all((x&t).bit_count()%2==0 for x in source_cap for t in fanout),
                'A common source cap must fit each actual target cap')
    require(local_spans==[4,4,4] and len(span(t for row in local_targets for t in row))==5,
            'Readable channel rank is not its target-label support rank')
    global_rows = []
    for p in (7,8,9,12):
        m = p-5
        fanouts = [[label(tuple(range(j))+outside_pairs, t | (outside << j))
                    for outside_pairs in combinations(range(5,p),5-j)
                    for t_index,t in enumerate(targets) if decoder[t_index][root]
                    for outside in range(1 << (5-j))] for root in range(3)]
        counts = [len(values) for values in fanouts]
        expected_count = 8*(comb(m,2) if j==3 else m)
        require(counts==[expected_count]*3, 'Every decoder target must be counted once')
        expected_span = (4 if m==2 else 2*m+1) if j==3 else 2*m+2
        require([len(span(values)) for values in fanouts]==[expected_span]*3,
                'The explicit global affine support formula must agree')
        global_rows.append({'p':p,'reads_per_channel':expected_count,'target_span':expected_span})
    cropped = [list(row) for row in completion]
    cropped[3] = [F(0)]*n
    require(any(multiply(inverse, cropped)[i][i]!=1 for i in range(n)),
            'Erasing a parked arbitrary dirty coordinate must destroy injectivity')
    return {'j':j,'parity':parity,'retained_banks':n,'readable_channels':3,
            'parked_banks':n-3,'determinant':str(determinant),
            'matrix':[[str(x) for x in row] for row in matrix],
            'decoder':[[str(x) for x in row[:3]] for row in decoder],
            'aggregate_input_rank':6-j,'closed_cap_entry_return_rank':2*n*(j-1),
            'local_actual_row_fanout_spans':local_spans,'global_fanout':global_rows,
            'erased_parked_coordinate_rejected':True}


def paired_checks():
    n = 16
    H = [[(-1)**((a&b).bit_count()) for b in range(n)] for a in range(n)]
    Q = [[F(sum(H[a][z]*(-1 if z.bit_count()<=2 else 1)*H[z][b]
                for z in range(n)), n) for b in range(n)] for a in range(n)]
    direct = [[side(5-(selector(a,5,1)^selector(b,5,0)).bit_count())
               for b in range(n)] for a in range(n)]
    require(Q==direct and multiply(Q,Q)==[[F(a==b) for b in range(n)] for a in range(n)],
            'The fixed-bank Walsh correction must be the actual involution')
    require({abs(x) for row in Q for x in row}=={F(1,8),F(3,8)},
            'This bank mixer is not a flat single-Clifford interface')
    require(all(sum(abs(x) for x in row)==F(7,2) for row in Q), 'The endpoint L1 charge must be explicit')
    for t in range(6):
        numerator = 16*comb(t,2)-9*t*(5-t)+6*comb(5-t,2)
        require(F(numerator,160)==-side(t), 'The pair-star decoder must include its odd divisor five')
    p = 7
    fixed = (1 << 0)|(1 << 2)
    candidate = [(1 << c)|fixed for c in range(2*p) if c not in (0,1,2,3)]
    require(all((x&y).bit_count()%2==(i==j) for i,x in enumerate(candidate) for j,y in enumerate(candidate)),
            'The explicit pair-star basis must be orthonormal')
    actual = [fixed | label(pairs,bits) for pairs in combinations(range(2,p),3) for bits in range(8)]
    require(len(span(actual))==len(candidate)==2*p-4 and len(span(actual+candidate))==len(candidate),
            'The source star must equal the asserted actual label subspace')
    counts=[]
    for pairs in (7,8,9,12):
        m=pairs-5
        excess=960*comb(m,2)+480*m-180
        v,q,h=32*comb(pairs,5),2*pairs*(pairs-1),2*pairs
        deficit=2*v-3*q*(h-4)
        counts.append({'pairs':pairs,'last_cube_excess_per_core':excess,
                       'retained_three_core_deficit':deficit,'after_last_cube_readers':deficit-3*excess})
    require([row['last_cube_excess_per_core'] for row in counts]==[1740,4140,7500,23340],
            'The independently counted terminal reader bound must match')
    return {'Q_entries_checked':256,'endpoint_row_L1':'7/2','fixed_odd_divisor':5,
            'orthonormal_star_rank':len(candidate),'terminal_closed_count_formula':counts}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    require(args.workers>0, 'A positive worker count is required')
    own=Path(__file__).resolve()
    closure={str(own.relative_to(TOPIC)):sha256(own.read_bytes()).hexdigest(),**REVIEWED}
    require(all(sha256((TOPIC/p).read_bytes()).hexdigest()==h for p,h in closure.items()),
            'Every reviewed source must match its immutable snapshot')
    started=datetime.now(timezone.utc).isoformat()
    tick=time.monotonic()
    tasks=[(j,p) for j in (3,4) for p in range(1 if args.bounded else 2)]
    if args.workers==1:
        rows=[cap_case(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows=list(pool.map(cap_case,tasks))
    paired=paired_checks()
    require(all(sha256((TOPIC/p).read_bytes()).hexdigest()==h for p,h in closure.items()),
            'Reviewed inputs must remain unchanged')
    result={'status':'PASS independent small paired-cube coefficient and cap-support review',
            'started_utc':started,'completed_utc':datetime.now(timezone.utc).isoformat(),
            'seconds':time.monotonic()-tick,'source_closure':closure,'workers':args.workers,
            'bounded':args.bounded,'cases':rows,'paired_controls':paired,
            'scope':'Import-free exact small scalar and support controls plus source-based analytic review; producer elementary words, previous-source witnesses, complete phase/native allocation and kappa are not independently executed or certified'}
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ('cases','paired_controls','source_closure')},sort_keys=True))


if __name__=='__main__':
    main()
