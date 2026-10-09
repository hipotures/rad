#!/usr/bin/env python3
"""Small exact search for ordinary-product encodings with XOR-compatible sums.

Every distinct complete ordinary coefficient sum must have one XOR output
label. This is a nonhomomorphic bilinear encoding, outside the full-ring
embedding obstruction. Only f=2,3 are searched; no all-size packing is claimed.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import time

TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/xor-compatible-packing.json'


def labelings(f):
    # Translate the label at exponent zero to zero. Quotient by GL(f,2):
    # the first two distinct nonzero labels are 1,2; the third is 3 or 4.
    # For f=3 a first independent third label can be fixed to4. This gives
    # all7!/168=30 inequivalent injective labelings, not a random sample.
    if f==2:return [(0,1,2,3)]
    if f!=3:raise ValueError('Only the complete f2/f3 canonical classes are implemented')
    rows=[(0,1,2,4)+p for p in permutations((3,5,6,7))]
    rows.extend((0,1,2,3,4)+p for p in permutations((5,6,7)))
    if len(rows)!=30:raise ValueError('Canonical GL3 orbit count is wrong')
    return rows


def compatible(exponents,labels):
    outputs={};pairs={}
    for a in range(len(exponents)):
        for b in range(a,len(exponents)):
            s=exponents[a]+exponents[b];c=labels[a]^labels[b]
            if s in outputs and outputs[s]!=c:return None
            outputs[s]=c;pairs.setdefault(s,[]).append((a,b))
    return outputs,pairs


def product_control(exponents,labels,outputs):
    size=len(labels);a=[j-3 for j in range(size)];b=[5-2*j for j in range(size)]
    ordinary=[0]*(2*max(exponents)+1)
    for j,x in enumerate(a):
        for k,y in enumerate(b):ordinary[exponents[j]+exponents[k]]+=x*y
    decoded=[0]*size;wanted=[0]*size
    for s,c in outputs.items():decoded[c]+=ordinary[s]
    for j,x in enumerate(a):
        for k,y in enumerate(b):wanted[labels[j]^labels[k]]+=x*y
    if decoded!=wanted:raise ValueError('Complete integer bilinear coefficient decoder failed')
    return dict(full_ordinary_product_coefficients=len(ordinary),decoded_all_XOR_coefficients=True,
                encoding_homomorphic=False,complete_operand_fields_checked=2*size,
                encoding_and_decoder_cost_not_supplied=True)


def probe(case):
    started=time.monotonic();f,maximum=case['f'],case['maximum_exponent'];size=1<<f
    labels=labelings(f);sets=0;rejected_progressions=0;classes=0;witness=None
    for tail in combinations(range(1,maximum+1),size-1):
        exponents=(0,)+tail;sets+=1;points=set(exponents)
        # A nontrivial three-term progression would equate a cross-pair to
        # a self-pair and force two distinct input labels to be identical.
        if any((a+b)%2==0 and (a+b)//2 in points for a,b in combinations(exponents,2)):
            rejected_progressions+=1;continue
        for word in labels:
            classes+=1;result=compatible(exponents,word)
            if result is not None:
                outputs,pairs=result
                witness=dict(exponents=exponents,input_binary_labels=word,
                             distinct_complete_product_sums=len(outputs),
                             sum_to_XOR_output=sorted(outputs.items()),
                             full_product_control=product_control(exponents,word,outputs))
                break
        if witness is not None:break
    return dict(f=f,input_dimension=size,maximum_exponent=maximum,canonical_labelings_per_set=len(labels),
                exponent_sets_examined=sets,three_progression_sets_rejected=rejected_progressions,
                canonical_labelings_examined=classes,complete_search_if_infeasible=witness is None,
                initial_hypothesis_feasible=case['initial_hypothesis_feasible'],
                initial_hypothesis_matches=(witness is not None)==case['initial_hypothesis_feasible'],
                feasible=witness is not None,witness=witness,seconds=time.monotonic()-started)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true');parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.workers<1 or (args.output and args.output.exists()):raise ValueError('Positive workers and fresh output required')
    config=json.loads(CONFIG.read_text());source=Path(__file__).resolve()
    pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in (source,CONFIG)}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_sha256=pins,
                  input='All exponent sets within declared span and complete f2/f3 labelings modulo affine GL',
                  scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    cases=config['cases'][:2] if args.small else config['cases'];started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(probe,cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=value for p,value in pins.items()):raise ValueError('Source changed during attempt')
    summary=dict(status='EXACT SMALL NONHOMOMORPHIC XOR PACKING SEARCH PASS',cases=rows,
                 seconds=time.monotonic()-started,scope=config['scope'],all_size_packing=False,native_cost_supplied=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ('status','seconds','scope')}))


if __name__=='__main__':main()
