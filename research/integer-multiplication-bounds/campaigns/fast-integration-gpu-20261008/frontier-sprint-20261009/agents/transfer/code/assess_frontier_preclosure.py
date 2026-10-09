#!/usr/bin/env python3
"""Independent paid-transfer ceiling and one-percent supplier requirements.

This reconstructs full histograms and finite bills from pinned files. Finite
word identities and inherited all-size interfaces are separate prerequisites.
Prepared with OpenAI GPT-6.1 Sol assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import exp, fsum, log
from pathlib import Path
import argparse
import copy
import json
import sys

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from check_balanced_composition import (BAD, OLD, balanced, ceil, cutoffs,
    full_bridge, js, moment, profile, require)


def pinned(root, pin):
    data=(root/pin['path']).read_bytes()
    require(sha256(data).hexdigest()==pin['sha256'], 'Source corruption: '+pin['path'])
    return json.loads(data)


def reconstruct_bit(row):
    H=Counter()
    for r,n in row['selected_rank_histogram'].items():
        H[3*int(r)]+=n
    for part in ('remaining_internal_histogram','source_data_histogram','target_data_histogram'):
        for r,n in row[part].items():H[int(r)]+=3*n
    H[2]+=2*row['v'];H.pop(0,None)
    require(dict(H)=={int(r):n for r,n in row['child_histogram'].items() if n},
            'Complete bit histogram does not reconstruct')
    p=profile(row['m'],row['W_per_vertex'],H)
    require(p['m']==3*row['h'] and p['W']==2*row['v']+row['R'], 'Bit local stock')
    require(p['mass']==row['rank_per_vertex'] and p['m']*p['W']-p['mass']==2*row['v']-3*row['loss'],
            'Bit telescoping rank')
    require(Q(2*p['m']**3,2**80)<BAD, 'Bit bad-class threshold')
    require(p['mass']+BAD*32*p['m']**2*p['edges']<p['m']*p['W'], 'Full fallback rank fails')
    return p


def reconstruct_complex(row):
    H=Counter()
    for part in ('local_histogram','source_data_histogram','target_data_histogram'):
        for r,n in row[part].items():H[int(r)]+=3*n
    for r,n in row['physical_gauge_histogram'].items():H[3*int(r)]+=n
    H[2]+=2*row['v'];H.pop(0,None)
    require(dict(H)=={int(r):n for r,n in row['child_histogram'].items() if n},
            'Complete physical complex histogram does not reconstruct')
    return profile(row['m'],row['W_per_vertex'],H)


def exact_root_bracket(p,bad):
    # Floating arithmetic locates two trial grid points only. The two rational
    # moment enclosures below are the accepted mathematical evidence.
    def discovered(x):
        ideal=fsum(n*r/(p['m']*p['W'])*exp(x*log(p['m']/r)) for r,n in p['hist'].items())
        fallback=float(bad)*32*p['m']**2*p['edges']/(p['m']*p['W'])*exp(x*log(p['m']))
        return ideal+fallback
    lo,hi=0.,.001
    require(discovered(lo)<1<discovered(hi), 'Discovery interval needs extension')
    for _ in range(70):
        mid=(lo+hi)/2
        if discovered(mid)<1:lo=mid
        else:hi=mid
    trial=int(lo*10**12)
    for _ in range(30):
        lower=Q(trial,10**12);upper=lower+Q(1,10**12)
        lm,um=moment(p,lower,bad),moment(p,upper,bad)
        if lm['upper']<1<um['lower']:
            return dict(lower=lower,upper=upper,accepted_moment=lm,rejected_moment=um,
                        scope='Exact rational complete moments; floating discovery is not certification.')
        if lm['lower']>=1:trial-=1
        elif um['upper']<=1:trial+=1
        else:raise ValueError('Grid separation is smaller than the rigorous enclosure')
    raise ValueError('Discovery did not locate a rational grid bracket')


def main():
    require(not sys.flags.optimize, 'Assertion-disabled execution is unsupported')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();require(not args.output.exists(), 'Output must be fresh')
    config=json.loads(args.config.read_bytes())
    inputs={k:pinned(args.sprint,pin) for k,pin in config['inputs'].items()}
    for pin in config['sources'].values():pinned_bytes=(args.sprint/pin['path']).read_bytes();require(
        sha256(pinned_bytes).hexdigest()==pin['sha256'], 'Written source pin mismatch: '+pin['path'])
    bit,physical,scalar=(inputs[k] for k in ('bit','physical','scalar'))
    bp,cp=reconstruct_bit(bit),reconstruct_complex(physical)
    require((bp['m'],bp['W'],bp['mass'],bit['R'])==(72,25772,1853648,22252), 'PR168 bit inventory')
    require((cp['m'],cp['W'],cp['mass'],scalar['R'],physical['physical_R'],physical['pairs'])==
            (66,14841,978186,15171,12201,2970), 'PR168 complex inventory')
    bb,cb=exact_root_bracket(bp,BAD),exact_root_bracket(cp,Q(0))
    coarse,b=Q(config['coarse']),Q(config['complex_saving'])
    atom,beta,eta,zeta=(Q(config[k]) for k in ('atom','phase_stop','backoff','strict_weakening'))
    bridge=full_bridge(physical,scalar,coarse,atom)
    assembly=balanced(bridge,b,beta,eta,zeta,kappa=Q(config['public_kappa']))
    require(moment(bp,coarse,BAD)['upper']<1 and moment(cp,b)['upper']<1, 'Pinned supplier moments')
    saved=inputs['public_certificate']
    require(saved['kappa']==str(assembly['kappa']), 'Public kappa pin')
    require(sorted(Q(v) for v in saved['assembly']['strict_constraints'].values())==
            sorted(assembly['slacks'].values()), 'Full public 47-slack arithmetic mismatch')
    require(sorted(Q(v) for v in saved['assembly']['margins'].values())==
            sorted(assembly['margins'].values()), 'Public seven margins mismatch')
    comparisons={'local_scalar':('complex','local_group_upper'),'logical_scalar':('complex','logical_group_upper'),
        'router':('complex','scalar_group_upper'),'W':('complex','W'),'s':('complex','s'),'N':('complex','N'),
        'E':('semantic','E'),'B':('semantic','B'),'C0':('semantic','C0'),'literal':('semantic','literal_charge'),
        'row_coefficient':('rows','coefficient')}
    for key,(section,name) in comparisons.items():require(
        saved['finite_bridge'][section][name]==bridge[key], 'Public full finite bill mismatch: '+key)
    ratio=Q(config['required_ratio'])
    frontier=Q(config.get('comparison_public_kappa',config['public_kappa']))
    if 'frontier_claim' in inputs:
        require(Q(inputs['frontier_claim']['kappa'])==frontier, 'Latest frontier claim source pin')
    bindings={}
    for live,saved_key in [('bit','saved_bit'),('physical','saved_physical'),('scalar','saved_scalar')]:
        if saved_key in inputs:
            require(inputs[live]==inputs[saved_key], 'Fresh rebuilt profile differs from fixed source: '+live)
            bindings[live]='Exact parsed equality of all fields; both original and regenerated bytes pinned.'
    target=ratio*frontier
    ideal=target/(1-target)
    needed_a=target/((1-2*eta)*(1-eta-target))
    needed_b=(needed_a+zeta)/(1-beta)
    needed_a0=needed_a*(1-OLD)/(1-needed_a)
    needed_fixed=(needed_a-atom*OLD)/(1-atom)
    # Strict paid-adapter condition theta>A forces theta>a0/(1+a0-OLD).
    # Hence A<a0/(1+a0-OLD). Combining q<A,b and eps(1+c)<1,
    # c>q, gives kappa<min(A,b)/(1+min(A,b)) for every parameter
    # choice in the retained paid balanced family, including eta,beta->0.
    ordinary_upper=bb['upper']/(1+bb['upper']-OLD)
    controlling_upper=min(ordinary_upper,cb['upper'])
    absolute_ceiling=controlling_upper/(1+controlling_upper)
    require(absolute_ceiling<target, 'The fixed-source one-percent obstruction did not hold')
    refined_theta=Q(ceil(bb['lower']/(1+bb['lower']-OLD)*10**12),10**12)
    if refined_theta==bb['lower']/(1+bb['lower']-OLD):refined_theta+=Q(1,10**12)
    refined_bridge=full_bridge(physical,scalar,bb['lower'],refined_theta)
    refined=balanced(refined_bridge,cb['lower'],beta,eta,zeta)
    refined['kappa_12_grid']=Q(ceil(refined['g']*10**12)-1,10**12)
    controls=[]
    def reject(name,call):
        try:call()
        except (KeyError,ValueError,ZeroDivisionError):controls.append(name)
        else:raise ValueError('Negative control accepted: '+name)
    reject('fixed source claimed at one-percent target',lambda:balanced(
        refined_bridge,cb['lower'],beta,eta,zeta,kappa=target))
    reject('unpaid preceding 1e-12 atom grid',lambda:full_bridge(
        physical,scalar,bb['lower'],refined_theta-Q(1,10**12)))
    reject('virtual scalar roles replaced by physical',lambda:full_bridge(
        physical,dict(scalar,R=physical['physical_R']),coarse,atom))
    reject('full literal bill removed',lambda:balanced(
        dict(bridge,strict_literal_gap=0),b,beta,eta,zeta,kappa=assembly['kappa']))
    reject('retained original prefix at balanced parameters',lambda:balanced(
        bridge,b,beta,eta,zeta,kappa=assembly['kappa'],old_prefix=True))
    reject('retained separate movement exposures',lambda:balanced(
        bridge,b,beta,eta,zeta,kappa=assembly['kappa'],old_exposures=True))
    damaged=copy.deepcopy(bit);damaged['child_histogram']['1']+=1
    reject('complete profile edited without word regeneration',lambda:reconstruct_bit(damaged))
    reject('source pin corrupted',lambda:pinned(args.sprint,dict(config['inputs']['bit'],sha256='0'*64)))
    result=dict(status='PASS conditional fixed-source ceiling and one-percent requirements',
        source_pins=config,config_sha256=sha256(args.config.read_bytes()).hexdigest(),
        bit_profile=bp,complex_profile=cp,bit_root=bb,complex_root=cb,bridge=bridge,public_assembly=assembly,
        refined_atom=refined_theta,refined_bridge=refined_bridge,refined_assembly=refined,
        public_cutoffs=cutoffs(bridge,assembly),refined_cutoffs=cutoffs(refined_bridge,refined),
        regenerated_profile_bindings=bindings,
        target=dict(required_ratio=ratio,comparison_frontier_kappa=frontier,
            comparison_frontier_head=config.get('comparison_public_head',config['source_head']),
            kappa=target,ideal_ordinary_and_complex_requirement=ideal,
            retained_ordinary_requirement=needed_a,retained_complex_requirement=needed_b,
            optimal_paid_atom_coarse_requirement=needed_a0,fixed_atom_coarse_requirement=needed_fixed,
            sufficient_1e12_points={k:Q(ceil(v*10**12),10**12) for k,v in
                [('ordinary',needed_a),('complex',needed_b),('optimized_coarse_bit',needed_a0),('fixed_atom_coarse_bit',needed_fixed)]}),
        obstruction=dict(bit_ordinary_upper=ordinary_upper,complex_upper=cb['upper'],
            controlling_upper=controlling_upper,balanced_upper=absolute_ceiling,
            target_shortfall=target-absolute_ceiling,limiting_supplier='bit' if ordinary_upper<cb['upper'] else 'complex',
            bit_coarse_gap=needed_a0-bb['upper'],complex_gap=needed_b-cb['upper'],
            scope='All parameters in the retained paid balanced family on these exact fixed profiles; no claim that frame or topology changes are impossible.'),
        rejected_controls=controls,conditional_prerequisites=config['conditional_prerequisites'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS fixed-source ceiling='+str(absolute_ceiling)+' < target='+str(target)+'; '
        +str(len(controls))+' negative controls; finite signed words remain separate prerequisites')


if __name__=='__main__':main()
