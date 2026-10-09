#!/usr/bin/env python3
"""Exact encoding-loss obstruction and conditional encoding-reuse budgets.

Conditional profiles are immutable mathematical inputs, not implemented C
primitives. Rational log/exponential intervals test necessary abstract slack;
the literal pair-block control binds the actual canonical preencoder.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import conditioned_frame_review as gaussian


TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/encoding-slack.json'


def logarithm_interval(ratio, terms):
    if ratio < 1:
        raise ValueError('Log interval expects ratio>=1')
    x=(ratio-1)/(ratio+1); square=x*x; power=x; total=Q(0)
    for j in range(terms):
        total+=2*power/(2*j+1); power*=square
    return total,total+2*power/((2*terms+1)*(1-square))


def exponential_interval(value, terms):
    if not 0 <= value < 1:
        raise ValueError('Require0<=argument<1 for the stated tail bound')
    term=Q(1); total=term
    for j in range(1,terms+1):
        term*=value/j; total+=term
    omitted=term*value/(terms+1)
    return total,total+omitted/(1-value/(terms+2))


def power_factor_interval(ratio,b,log_terms,exp_terms):
    lower,upper=logarithm_interval(ratio,log_terms)
    return (exponential_interval(b*lower,exp_terms)[0],
            exponential_interval(b*upper,exp_terms)[1])


def ceil_fraction(value):
    return -((-value.numerator)//value.denominator)


def compact_interval(lower,upper):
    grid=10**15
    lo=(lower*grid).numerator//(lower*grid).denominator
    hi=ceil_fraction(upper*grid)
    return [str(Q(lo,grid)),str(Q(hi,grid))]


def profile_budget(payload):
    row,config=payload; p=row['profile']; m,W=p['m'],p['W']
    v,q=row['source_banks'],row['center_features']
    histogram={int(t):n for t,n in p['child_multiplicities'].items()}
    deficit=2*v-2*q*m
    if W != row['physical_stock'] or m != row['h'] or any(not 0<t<=m or n<0 for t,n in histogram.items()):
        raise ValueError('Invalid complete conditional profile')
    if sum(t*n for t,n in histogram.items()) != W*m-deficit or p['deficit'] != deficit:
        raise ValueError('Profile rank ledger differs from every charged call')
    b=Q(config['target_fraction']); phi_lower=phi_upper=Q(0)
    for t,n in histogram.items():
        lo,hi=power_factor_interval(Q(m,t),b,config['log_terms'],config['exponential_terms'])
        weight=Q(n*t,W*m); phi_lower+=weight*lo; phi_upper+=weight*hi
    lo,hi=power_factor_interval(Q(m),b,config['log_terms'],config['exponential_terms'])
    unit_lower,unit_upper=lo/(W*m),hi/(W*m)
    necessary=ceil_fraction((1-phi_lower)/unit_lower)-1
    sufficient=ceil_fraction((1-phi_upper)/unit_upper)-1
    canonical_first_moment=Q(sum(t*n for t,n in histogram.items())+2*v,W*m)
    if canonical_first_moment != 1+Q(2*q,W) or canonical_first_moment <= 1:
        raise ValueError('Canonical wrapper negative control failed')
    if sufficient>necessary or necessary>=2*v:
        raise ValueError('Encoding budget failed the complete wrapper obstruction')
    return dict(h=m,v=v,q=q,W=W,framed_rank_deficit=deficit,
        raw_framed_first_moment=str(Q(W*m-deficit,W*m)),canonical_first_moment=str(canonical_first_moment),
        naive_canonical_encoding_width1_calls=2*v,target_fraction=str(b),
        conditional_target_moment_outward_interval=compact_interval(phi_lower,phi_upper),
        unit_encoding_moment_outward_interval=compact_interval(unit_lower,unit_upper),
        maximum_additional_width1_calls_sufficient_in_abstract_profile=max(-1,sufficient),
        maximum_additional_width1_calls_necessary_in_abstract_profile=max(-1,necessary),
        interval_resolves_integer_budget=sufficient==necessary,
        minimum_naive_encoding_calls_to_eliminate=2*v-necessary,
        minimum_elimination_fraction=str(Q(2*v-necessary,2*v)),
        allowed_width1_calls_for_any_positive_root=max(-1,deficit-1),
        scope='Conditional profile arithmetic only; no circuit reusing encodings is certified')


def block(matrix00,matrix01,matrix10,matrix11):
    return [a+b for a,b in zip(matrix00,matrix01)]+[a+b for a,b in zip(matrix10,matrix11)]


def literal_preencoder():
    # One odd label of weight3 verifies affine/global phases are not silently
    # assumed homogeneous. Literal line/full coefficients use 2x2 products.
    h,T=3,7; size=1<<h
    zero=[[gaussian.ZERO]*size for _ in range(size)]
    ident=gaussian.identity(size)
    alpha,beta=(Q(1,2),Q(1,2)),(Q(1,2),Q(-1,2))
    A=[[alpha if i==j else beta if i==(j^T) else gaussian.ZERO for j in range(size)] for i in range(size)]
    Ai=gaussian.adjoint(A)
    F=[[gaussian.c_entry(h,i,j) for j in range(size)] for i in range(size)]
    X=[[gaussian.ONE if i==(j^T) else gaussian.ZERO for j in range(size)] for i in range(size)]
    if gaussian.matmul(A,A)!=X or gaussian.matmul(A,Ai)!=ident:
        raise ValueError('Literal line normalization failed')
    G=block(Ai,zero,X,Ai)
    minus_ident=[[(Q(-1),Q(0)) if i==j else gaussian.ZERO for j in range(size)] for i in range(size)]
    H=block(A,zero,minus_ident,A)
    full=block(F,zero,zero,F)
    P=gaussian.matmul(full,G)
    if gaussian.matmul(G,H)!=gaussian.identity(2*size) or gaussian.matmul(H,G)!=gaussian.identity(2*size):
        raise ValueError('Preencoder is not the exact pair-block inverse')
    if gaussian.matmul(P,H)!=full:
        raise ValueError('Paid preencoder fails the canonical endpoint')
    if P==full:
        raise ValueError('Omitted preencoder incorrectly accepted')
    if gaussian.matmul(P,block(A,zero,zero,A))==full:
        raise ValueError('Omitted raw negative cross shear incorrectly accepted')
    return dict(h=h,label=T,actual_pair_matrix_entries=4*size*size,
        encoded_block='F*[[A^-1,0],[X_T,A^-1]]',preencoder='[[A,0],[-I,A]]',
        literal_two_sided_inverse=True,canonical_output_exact=True,
        omitted_preencoder_rejected=True,omitted_cross_shear_rejected=True,
        native_encoding_child_calls_per_pair=2,child_selected_rank_per_call=1)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); config=json.loads(CONFIG.read_text())
    fixture=TOPIC/config['fixture']; helper=Path(gaussian.__file__).resolve()
    if sha256(fixture.read_bytes()).hexdigest()!=config['fixture_sha256'] or \
            sha256(helper.read_bytes()).hexdigest()!=config['arithmetic_sha256']:
        raise ValueError('Pinned profile/arithmetic input changed')
    data=json.loads(fixture.read_text()); cases=data['cases'][:1] if args.small else data['cases']
    paths=[Path(__file__).resolve(),CONFIG,fixture,helper]
    hashes={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
        effective_source_config_fixture_sha256=hashes,profile_source=data['source_input'],
        target_fraction=config['target_fraction'],log_terms=config['log_terms'],
        exponential_terms=config['exponential_terms'],seed=None,scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(profile_budget,[(row,config) for row in cases]))
    literal=literal_preencoder()
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=digest for p,digest in hashes.items()):
        raise ValueError('Source/input changed during immutable attempt')
    result=dict(status='CANONICAL ENCODING OBSTRUCTION AND CONDITIONAL SLACK PASS',
        cases=rows,literal_preencoder=literal,seconds=time.monotonic()-started,scope=config['scope'],
        new_native_primitive=False,new_transfer_or_kappa=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':
    main()
