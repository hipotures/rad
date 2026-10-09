#!/usr/bin/env python3
"""Independent compact arithmetic review of pinned conditional draft PR127.

No external script is executed/imported. Immutable derived inputs retain full
histograms, birth-rank aggregates, scalar bill and expected assembly values.
This source does not prove the retained supplier or all-size native contracts.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

import encoding_slack as bounds


TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/pr127-transfer-review.json'


def log_interval(ratio):
    scale=0
    while ratio>=2:
        ratio/=2;scale+=1
    lo,hi=bounds.logarithm_interval(ratio,40)
    two_lo,two_hi=bounds.logarithm_interval(Q(2),40)
    return lo+scale*two_lo,hi+scale*two_hi


def moment(payload):
    name,profile,saving,required=payload;m,W=profile['m'],profile['W']
    lo=hi=Q(0);mass=0
    for raw_t,n in profile['children'].items():
        t=int(raw_t)
        if not 0<t<m or n<=0:
            raise ValueError('Invalid strict child/stock profile')
        log_lo,log_hi=log_interval(Q(m,t))
        factor_lo=bounds.exponential_interval(saving*log_lo,8)[0]
        factor_hi=bounds.exponential_interval(saving*log_hi,8)[1]
        weight=Q(n*t,m*W);lo+=weight*factor_lo;hi+=weight*factor_hi;mass+=n*t
    passing=hi<1;failing=lo>1
    if (required=='pass' and not passing) or (required=='fail' and not failing):
        raise ValueError('Independent exact moment comparison is unresolved or wrong')
    return dict(name=name,m=m,W=W,saving=str(saving),rank=mass,
        first_moment=str(Q(mass,m*W)),outward_interval=bounds.compact_interval(lo,hi),
        strict_target_status='below1' if passing else 'above1' if failing else 'unresolved',
        log_range_reduced=True,log_terms=40,exponential_degree=8)


def halving_depth(m,r):
    if not 0<r<m:
        raise ValueError('Halving depth requires a strict width decrease')
    a,b=m,r;depth=1
    while a<=2*b:
        a*=m;b*=r;depth+=1
    return depth


def assembly(data):
    v=comb(24,3);N=v*v;base=data['base_complex'];birth=data['birth'];bill=data['scalar_bill']
    histogram=Counter({int(t):n for t,n in base['child_multiplicities'].items()})
    count=0
    for rank_pair,number in birth['match_ranks'].items():
        e,s=map(int,rank_pair.split('->'))
        if not 0<=e<=s<24 or number<=0:
            raise ValueError('Invalid contained birth-rank aggregate')
        histogram[24-e]-=2*v*number;histogram[552+s]-=2*v*number
        if s>e:histogram[s-e]+=2*v*number
        count+=number
    histogram={t:n for t,n in histogram.items() if n}
    wanted={int(t):n for t,n in data['profiles']['birth_complex']['children'].items()}
    if min(histogram.values())<=0 or histogram!=wanted or count!=birth['matched'] or count!=2108:
        raise ValueError('Whole rebilled child histogram mismatch')
    W=2*N+2*v*birth['R'];mass=sum(t*n for t,n in histogram.items())
    if W!=birth['W'] or W!=115857808 or mass!=birth['rank'] or 576*W-mass!=1862080:
        raise ValueError('Stock/rank/deficit differs from compact retained profile')
    virtualR=birth['R']+count
    if virtualR!=28705:
        raise ValueError('Virtual/physical role bill mismatch')
    read=bill['readout_numerator_L1']+bill['terminal_numerator_L1']+8*(virtualR+4*v+24)
    local=read+2*(bill['source_injection_count']+bill['workspace_gate_count'])+16*virtualR+16*24
    G=16*(2*v*local+8*N)
    if read!=bill['readout_copy_scan_bill'] or local!=bill['local_scalar_upper'] or G!=bill['global_scalar_group_upper']:
        raise ValueError('Complete signed scalar/copy bill mismatch')
    m,rmax=576,max(histogram);E=64*(W+m+G+1)**3
    charge=2*G*W*W+8*mass+4*W+4+32*m;B=mass+E;C0=32*m*B*B
    if not charge<E or not 2*B*(m-rmax)>=mass+E or not 2*B+18<C0:
        raise ValueError('Finite guard induction inequalities failed')
    stock=[]
    for name in ['coarse_bit','old_ordinary','birth_complex']:
        profile=data['profiles'][name];rr=max(map(int,profile['children']))
        stock.append(dict(m=profile['m'],W=profile['W'],maxchild=rr,
            depth=halving_depth(profile['m'],rr),wire_bits=profile['W'].bit_length()))
    rows=sum(row['depth']*row['wire_bits'] for row in stock);rowgap=Q(32000)-Q(51,25)*rows
    if rows!=15561 or rowgap!=Q(6389,25):
        raise ValueError('Complete three-supplier row-stock arithmetic failed')
    a0=Q(620523,5000000000);ordinary=Q(384599,10**10);alpha=Q(1,1000)
    actual=(1-alpha)*a0+alpha*ordinary;b=Q(11242073,10**11);beta=Q(1,10**6);buffer=Q(1,10**12)
    a=min(actual,(1-beta)*b-buffer);eta=Q(1,10**8)
    q=a*(1-2*eta);c=q*(1+eta);epsilon=(1-eta)/(1+c+q)
    g=epsilon*q;r=(g+1-epsilon)/2;delta=eta/8
    margins=dict(original_prefix=1-epsilon*(1+c),coordinate_movement=a,
        compact_phase_layer=g,bulk_exposure=a,
        Gaussian_arithmetic=min(1-epsilon-delta,r-delta),
        scalar_work=1-epsilon-delta,dimension=epsilon)
    grid=10**17;kappa=Q((g*grid).numerator//(g*grid).denominator,grid)
    if kappa==g:kappa-=Q(1,grid)
    expected=data['expected']
    if kappa!=Q(expected['kappa']) or a!=Q(expected['supported_bit_parameter']) or actual!=Q(expected['actual_bit_saving']):
        raise ValueError('Independent selected exponent/bit parameter differs')
    if any(value!=Q(expected['assembly']['margins'][name]) or value<=kappa for name,value in margins.items()):
        raise ValueError('Independent seven final margins differ')
    if g>=kappa+Q(1,grid) or g-kappa<=0:
        raise ValueError('Strict next kappa-grid rejection failed')
    bridge=expected['finite_bridge']
    for name,value in [('W',W),('rank',mass),('R',birth['R']),('maxchild',rmax),('G',G),('E',E),('literal_charge',charge),('B',B),('C0',C0),('rows',rows)]:
        if bridge[name]!=value:
            raise ValueError('Independent finite bridge constant differs: '+name)
    return dict(birth_reuses=count,virtual_roles=virtualR,physical_roles=birth['R'],W=W,
        weighted_rank=mass,unchanged_deficit=576*W-mass,maxchild=rmax,
        scalar_bill=dict(readout_copy_scan_bill=read,local_scalar_upper=local,G=G,
            maximum_literal_numerator=bill['max_abs_numerator'],denominator=bill['denominator']),
        guard_inequalities_pass=True,row_stock=stock,row_coefficient=rows,row_degree=32000,row_gap=str(rowgap),
        coarse_bit_saving=str(a0),ordinary_leaf_saving=str(ordinary),actual_bit_saving=str(actual),
        complex_saving=str(b),supported_bit_parameter=str(a),selected_conditional_kappa=str(kappa),
        all_seven_exact_margin_identities=True,strict_next_kappa_rejected=True,
        independently_rechecked_all_47_constraints=False,
        bit_supplier_already_exceeds_1e_4=actual>Q(1,10000),
        all_size_supplier_native_proved=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();config=json.loads(CONFIG.read_text());fixture=TOPIC/config['fixture']
    interval=Path(bounds.__file__).resolve();gaussian=Path(bounds.gaussian.__file__).resolve()
    for path,digest in [(fixture,config['fixture_sha256']),(interval,config['interval_helper_sha256']),
                         (gaussian,config['gaussian_arithmetic_sha256'])]:
        if sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Pinned independent input/helper changed')
    paths=[Path(__file__).resolve(),CONFIG,fixture,interval,gaussian]
    hashes={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    data=json.loads(fixture.read_text());b=Q(11242073,10**11)
    tasks=[('coarse_bit',data['profiles']['coarse_bit'],Q(620523,5000000000),'pass'),
           ('ordinary_leaf',data['profiles']['old_ordinary'],Q(384599,10**10),'pass'),
           ('new_complex',data['profiles']['birth_complex'],b,'pass'),
           ('next_complex',data['profiles']['birth_complex'],b+Q(1,10**11),'fail')]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
        effective_source_config_fixture_sha256=hashes,external_url=data['input_url'],head=data['head'],
        seed=None,scope=config['scope'],external_scripts_executed=False)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(moment,tasks))
    arithmetic=assembly(data)
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=digest for p,digest in hashes.items()):
        raise ValueError('Source/input changed during immutable attempt')
    result=dict(status='INDEPENDENT COMPACT PR127 TRANSFER ARITHMETIC PASS',moments=rows,
        assembly=arithmetic,seconds=time.monotonic()-started,scope=config['scope'],
        full_external_birth_word_replayed=False,stopped_bit_word_replayed=False,
        formal_or_unconditional_exponent=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':main()
