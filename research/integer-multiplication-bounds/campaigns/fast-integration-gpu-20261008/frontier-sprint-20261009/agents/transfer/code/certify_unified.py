#!/usr/bin/env python3
"""Unified source-bound paid balanced certificate for separately reviewed words.

Uses this lane's independent rational interval, bridge and 47-condition
implementation. A secondary byte-pinned upstream checker is compared only
after those quantities have been reconstructed. It never establishes finite
word correctness by accepting a saved verification flag.
Prepared with OpenAI GPT-6.1 Sol assistance; Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import sys

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from check_balanced_composition import (BAD,OLD,PUBLIC,balanced,ceil,cutoffs,
    floor_strict,full_bridge,js,moment,profile,require)


def read_bytes(root,pin):
    data=(root/pin['path']).read_bytes()
    require(sha256(data).hexdigest()==pin['sha256'],'Source corruption: '+pin['path'])
    return data


def main():
    require(not sys.flags.optimize,'Assertion-disabled execution is unsupported')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();require(not args.output.exists(),'Output must be fresh')
    config=json.loads(args.config.read_text())
    source={k:json.loads(read_bytes(args.sprint,pin)) for k,pin in config['inputs'].items()}
    for pin in config['sources'].values():read_bytes(args.sprint,pin)
    coarse,atom,b,beta,eta,weakening=(Q(config[k]) for k in
        ('coarse','atom','complex_saving','phase_stop','backoff','strict_weakening'))
    require(atom==Q(1,1000) and beta==Q(1,10**9) and eta==Q(1,10**8),
            'First candidate must retain the frozen atom and stopping parameters')
    physical,scalar,bit=(source[k] for k in ('physical','scalar','bit'))
    cp=profile(physical['m'],physical['W_per_vertex'],physical['child_histogram'])
    bp=profile(bit['m'],bit['W_per_vertex'],bit['child_histogram'])
    require((bp['m'],bp['W'],bp['mass'],bp['m']*bp['W']-bp['mass'])==(72,26888,1934000,1936),
            'Binary construction inventory changed')
    require((cp['m'],cp['W'],cp['mass'],cp['maxchild'])==(66,15681,1033626,20),
            'Complex construction inventory changed')
    require(bit['R']==23368 and bit['v']==1760 and bit['loss']==528,
            'Binary supplier no longer has the selected shared-core inventory')
    bm=moment(bp,coarse,BAD);cm=moment(cp,b)
    require(bm['upper']<1 and cm['upper']<1,'A complete supplier moment failed')
    bn=moment(bp,coarse+Q(1,10**12),BAD);cn=moment(cp,b+Q(1,10**12))
    require(bn['lower']>1 and cn['lower']>1,'Supplier next-grid exclusion failed')
    require(Q(2*bp['m']**3,2**80)<BAD,'Bad-class prime threshold changed')
    rank=bp['mass']+BAD*32*bp['m']**2*bp['edges']
    require(rank<bp['m']*bp['W'],'Contaminated binary rank mass does not contract')
    bridge=full_bridge(physical,scalar,coarse,atom)
    result=balanced(bridge,b,beta,eta,weakening,kappa=Q(config['kappa']))
    require(result['a']==bridge['ordinary_saving'],'Unexpected complex limiting supplier')
    require(result['kappa']>PUBLIC,'Candidate does not beat the pinned public claim')

    # Compare to the pinned upstream bridge and 47-slack body using our ACTUAL
    # complex inventory and the new binary coarse certificate. No upstream
    # producer, discovery routine, saved PASS or old profile is imported.
    vendor=args.sprint/config['vendor_arithmetic']
    sys.path.insert(0,str(vendor))
    spec=importlib.util.spec_from_file_location('pinned_vendor_certificate',vendor/'certificate.py')
    upstream=importlib.util.module_from_spec(spec);spec.loader.exec_module(upstream)
    upstream.normalized_body_check()
    row=dict(scalar)
    for key in ('m','W_per_vertex','rank_per_vertex','deficit_per_vertex','child_histogram'):
        row[key]=physical[key]
    row.update(R=physical['physical_R'],scalar_role_reserve=scalar['R'],reuse_pairs=physical['pairs'])
    secondary_bridge=upstream.bridge(row,coarse,atom)
    from balanced_shared import assembly
    secondary=assembly(secondary_bridge,row,result['a'],result['kappa'],beta=beta,h=eta,a_complex=b)
    require(secondary['minimum_margin']==result['g'],'Independent minimum disagrees')
    require(sorted(secondary['constraints'].values())==sorted(result['slacks'].values()),
            'Independent 47 inequalities disagree')
    pairs={'W':('complex','W'),'s':('complex','s'),'N':('complex','N'),
        'local_scalar':('complex','local_group_upper'),'logical_scalar':('complex','logical_group_upper'),
        'router':('complex','scalar_group_upper'),'E':('semantic','E'),'B':('semantic','B'),
        'C0':('semantic','C0'),'literal':('semantic','literal_charge'),
        'row_coefficient':('rows','coefficient'),'row_gap':('rows','degree_gap')}
    for key,(section,name) in pairs.items():
        require(secondary_bridge[section][name]==bridge[key],'Independent bridge disagrees: '+key)

    controls=[]
    def reject(name,call):
        try:call()
        except (KeyError,ValueError,AssertionError,ZeroDivisionError):controls.append(name)
        else:raise ValueError('Negative control accepted: '+name)
    reject('first 1e-18 grid point above margin',lambda:balanced(bridge,b,beta,eta,weakening,
        kappa=floor_strict(result['g'],10**18)+Q(1,10**18)))
    reject('old prefix at balanced parameters',lambda:balanced(bridge,b,beta,eta,weakening,
        old_prefix=True,kappa=result['kappa']))
    reject('old nonlinear guard',lambda:balanced(bridge,b,beta,eta,weakening,
        old_guard=True,kappa=result['kappa']))
    reject('old separate movement charges',lambda:balanced(bridge,b,beta,eta,weakening,
        old_exposures=True,kappa=result['kappa']))
    bad=copy.deepcopy(secondary_bridge);bad['complex']['W']=physical['W_per_vertex']
    reject('full group W replaced by local W',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['ordinary_leaf_row_degree']=0
    reject('ordinary leaf reserve omitted',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['conservative_old_coarse_row_reserve']=0
    reject('old coarse reserve omitted',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['complex']['scalar_role_reserve']=physical['physical_R']
    reject('virtual scalar stock collapsed',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['semantic']['C0']=1
    reject('stale semantic C0',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['complex']['scalar_group_upper']=0
    reject('scalar group omitted',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['rows']['coefficient']=1
    reject('incorrect simultaneous row coefficient',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['rows']['degree']=1
    reject('insufficient external rows',lambda:upstream.validate_shared_bridge(bad,row))
    bad=copy.deepcopy(secondary_bridge);bad['bit_uniform']['ordinary_saving']+=Q(1,10**24)
    reject('ordinary saving overstated',lambda:upstream.validate_shared_bridge(bad,row))
    badpin=dict(config['inputs']['bit_frames'],sha256='0'*64)
    reject('source binding corrupted',lambda:read_bytes(args.sprint,badpin))
    output=dict(status='PASS unified conditional transfer arithmetic',candidate_id=config['candidate_id'],
        config_sha256=sha256(args.config.read_bytes()).hexdigest(),source_pins=config,
        kappa=result['kappa'],coarse_bit_saving=coarse,atom=atom,ordinary_bit_saving=bridge['ordinary_saving'],
        complex_saving=b,bit_profile=bp,complex_profile=cp,
        bit_moment=bm,bit_next_grid=bn,complex_moment=cm,complex_next_grid=cn,
        contaminated_bit_rank=rank,bridge=bridge,assembly=result,
        secondary_bridge=secondary_bridge,secondary_assembly=secondary,
        cutoffs=cutoffs(bridge,result),source_body_comparison='Identical retained PR141 47-slack body except bridge plumbing and actual-supplier support.',
        public_comparison=dict(pinned_head='15c702a929b7d640107a95e196186ad74e876c82',
            current_observed_head='e1813796ef5c3ca38c5dd7b9e8d81b3908ff5997',
            observation_utc='2026-10-09T07:55:55Z',public_kappa=PUBLIC,improvement=result['kappa']-PUBLIC,
            scope='Mathematical score unchanged at observed newer head; live refresh belongs to coordinator.'),
        rejected_controls=controls,
        finite_prerequisites=config['finite_prerequisites'],
        inherited_hypotheses=config['inherited_hypotheses'],
        exclusions=['This arithmetic does not prove scalar/frame/signed-reflection correctness from supplier histograms.',
            'No unconditional all-size theorem, practical input threshold or hosted-CI success is asserted.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(js(output),sort_keys=True,indent=2)+'\n')
    print('PASS unified kappa='+str(result['kappa'])+'; two independent 47-condition derivations; '+
          str(len(controls))+' rejected controls; exact improvement='+str(result['kappa']-PUBLIC))


if __name__=='__main__':main()
