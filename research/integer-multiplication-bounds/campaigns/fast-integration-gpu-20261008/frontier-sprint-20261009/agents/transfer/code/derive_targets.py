#!/usr/bin/env python3
"""Source-bound exact frontier floor and paid native supplier targets.

Arithmetic only. Independent finite word, prime and reflected-geometry gates
remain explicit prerequisites. GPT-6.1 Sol assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
from check_balanced_composition import BAD,OLD,ceil,js,moment,profile,require


def strict_grid(x,denominator):
    z=x*denominator
    return Q(z.numerator//z.denominator+1,denominator)


def native_requirements(k,eta,beta,weakening):
    require(0<k<1-eta and 0<eta<Q(1,2) and 0<beta<1, 'Parameter ranges')
    a=k/((1-2*eta)*(1-eta-k))
    b=(a+weakening)/(1-beta)
    coarse=a*(1-OLD)/(1-a)
    return dict(final_kappa=k,ordinary=a,complex=b,coarse_with_optimal_paid_atom=coarse,
        sufficient_1e12={name:strict_grid(x,10**12) for name,x in
            [('ordinary',a),('complex',b),('coarse_with_optimal_paid_atom',coarse)]})


def main():
    require(not sys.flags.optimize,'Assertion-disabled execution is unsupported')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();require(not args.output.exists(),'Output must be fresh')
    c=json.loads(args.config.read_bytes());data={}
    for key,pin in c['inputs'].items():
        raw=(args.sprint/pin['path']).read_bytes()
        require(sha256(raw).hexdigest()==pin['sha256'],'Source corruption: '+key)
        data[key]=json.loads(raw)
    peer=Q(data['frontier_certificate']['kappa'])
    require(peer==Q(c['frontier_kappa']),'Source claim mismatch')
    eta,beta,zeta=(Q(c[k]) for k in ('backoff','phase_stop','weakening'))
    target=Q(c['required_ratio'])*peer
    reported=Q(ceil(target*10**12),10**12)
    exact=native_requirements(target,eta,beta,zeta)
    reporting=native_requirements(reported,eta,beta,zeta)
    row=data['bit_profile'];H=Counter()
    for part in ('local_histogram','source_data_histogram','target_data_histogram'):
        for r,n in row[part].items():H[int(r)]+=3*n
    for r,n in row['physical_gauge_histogram'].items():H[3*int(r)]+=n
    H[2]+=2*row['v'];H.pop(0,None)
    require(dict(H)=={int(r):n for r,n in row['child_histogram'].items() if n},'Full physical bit histogram')
    bp=profile(row['m'],row['W_per_vertex'],H)
    require(bp['m']==3*row['h'] and bp['W']==2*row['v']+row['physical_R'],'Physical bit width')
    require(row['physical_R']==row['R']-row['pairs'],'Compensated physical stock')
    require(bp['mass']==row['rank_per_vertex'] and bp['m']*bp['W']-bp['mass']==2*row['v']-3*row['loss'],
            'Complete telescoping rank')
    coarse=Q(c['coarse_bit_saving']);bm=moment(bp,coarse,BAD);bn=moment(bp,coarse+Q(1,10**12),BAD)
    require(bm['upper']<1<bn['lower'],'Full fallback coarse/successor separation')
    require(bp['mass']+BAD*32*bp['m']**2*bp['edges']<bp['m']*bp['W'],'Contaminated rank contraction')
    require(Q(2*bp['m']**3,2**80)<BAD,'Retained bad-class fraction')
    theta=strict_grid(coarse/(1+coarse-OLD),10**12)
    ordinary=(1-theta)*coarse+theta*OLD
    require(ordinary<theta<1-ordinary,'Paid atom adapter/internal-row tolls')
    require(ordinary>reporting['ordinary'],'Provided binary supplier does not clear reported-grid floor')
    required_b=reporting['sufficient_1e12']['complex']
    a=min(ordinary,(1-beta)*required_b-zeta)
    q=a*(1-2*eta);g=(1-eta)*q/(1+q)
    require(g>reported>=target,'Sufficient complex trial does not support the final reported point')
    previous=required_b-Q(1,10**12)
    prev_a=min(ordinary,(1-beta)*previous-zeta);prev_q=prev_a*(1-2*eta)
    prev_g=(1-eta)*prev_q/(1+prev_q)
    require(prev_g<=reported,'Previous sufficient-grid trial unexpectedly qualifies')
    result=dict(status='PASS exact source-bound targets and supplied physical-bit arithmetic',source_pins=c,
        config_sha256=sha256(args.config.read_bytes()).hexdigest(),frontier=peer,
        exact_ratio_floor=target,deliberate_final_1e12_grid=reported,
        exact_floor_requirements=exact,reported_grid_requirements=reporting,
        supplied_bit=dict(profile=bp,coarse=coarse,moment=bm,next_grid=bn,atom=theta,
            ordinary=ordinary,adapter_gap=theta-ordinary,internal_row_gap=1-ordinary-theta,
            ordinary_headroom=ordinary-reporting['ordinary']),
        sufficient_trial=dict(complex_saving=required_b,common_transfer_saving=a,g=g,
            reported_margin_gap=g-reported,previous_complex_trial=previous,
            previous_trial_margin=prev_g,previous_trial_reported_gap=prev_g-reported),
        exclusions=['The hypothetical sufficient complex trial is a target, not an actual complex supplier.',
            'The profile/frame hashes bind the supplied bit arithmetic, not a substitute for independent finite/prime/reflected acceptance.',
            'All completed ordinary, restored-row, exact tensor, routing, balanced/bulk, analytic, recovery, precision and fixed-tape hypotheses remain inherited.',
            'The inherited finite excluded-prime set and selected new finite presentation exclusions remain explicit; no practical threshold is claimed.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS source floor='+str(target)+'; final1e12='+str(reported)+
        '; sufficient complex trial='+str(required_b)+'; previous trial fails reported grid')


if __name__=='__main__':main()
