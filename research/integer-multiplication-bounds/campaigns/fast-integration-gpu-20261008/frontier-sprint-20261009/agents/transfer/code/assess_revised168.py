#!/usr/bin/env python3
"""Source-bound complete-profile ceilings and paid targets for revised PR168.

This is an arithmetic/source review, not the source producer or finite audit.
No upstream implementation is imported. Apache-2.0; OpenAI assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

from check_balanced_composition import BAD,OLD,balanced,ceil,cutoffs,full_bridge,js,moment,require
from certify_lifetime_fused import pinned,reconstruct
from assess_frontier import exact_root_bracket


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sprint',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();require(not sys.flags.optimize,'Optimized execution unsupported')
    require(not args.output.exists(),'Output must be fresh')
    config=json.loads(args.config.read_bytes())
    data={key:json.loads(pinned(args.sprint,item)) for key,item in config['inputs'].items()}
    for item in config['sources'].values():pinned(args.sprint,item)
    certificate=data['public_certificate']
    for name,digest in certificate['source_sha256'].items():
        require(any(item['path'].endswith('/'+name) and item['sha256']==digest
                    for item in config['sources'].values()),'Public declared source omitted: '+name)
    bit,physical,scalar=data['bit'],data['physical'],data['scalar']
    bp,cp=reconstruct(bit,True),reconstruct(physical)
    require((bp['m'],bp['W'],bp['mass'],bit['R'],bit['physical_R'],bit['pairs'])==
            (72,22252,1600208,20492,18732,1760),'Revised binary inventory')
    require((cp['m'],cp['W'],cp['mass'],scalar['R'],physical['physical_R'],physical['pairs'])==
            (66,13963,920238,13633,11323,2310),'Revised complex inventory')
    require((scalar['c'],scalar['q'],scalar['matched'],scalar['total_M_operations'])==
            (20714,3157,10238,33027),'Revised signed scalar inventory')
    coarse,atom,b,beta,eta,zeta,public=(Q(config[key]) for key in
        ('coarse','atom','complex_saving','phase_stop','backoff','strict_weakening','public_kappa'))
    bb,cb=exact_root_bracket(bp,BAD),exact_root_bracket(cp,Q(0))
    bridge=full_bridge(physical,scalar,coarse,atom)
    assembly=balanced(bridge,b,beta,eta,zeta,kappa=public)
    require(Q(certificate['kappa'])==public,'Source-confirmed leaderboard claim')
    require(sorted(Q(x) for x in certificate['assembly']['strict_constraints'].values())==
            sorted(assembly['slacks'].values()),'Full public47 inequalities do not reproduce')
    require(sorted(Q(x) for x in certificate['assembly']['margins'].values())==
            sorted(assembly['margins'].values()),'Public seven margins do not reproduce')
    for field,section,name in [
        ('W','complex','W'),('s','complex','s'),('N','complex','N'),
        ('local_scalar','complex','local_group_upper'),('logical_scalar','complex','logical_group_upper'),
        ('router','complex','scalar_group_upper'),('E','semantic','E'),('B','semantic','B'),
        ('C0','semantic','C0'),('literal','semantic','literal_charge'),
        ('row_coefficient','rows','coefficient'),('row_gap','rows','degree_gap')]:
        actual=certificate['finite_bridge'][section][name]
        if isinstance(bridge[field],Q):actual=Q(actual)
        require(actual==bridge[field],'Full revised scalar/precision/row bill mismatch: '+field)
    target=Q(config['required_ratio'])*public
    require(target==Q(163041371,250000000000),'Current exact one-percent floor')
    necessary=target/((1-2*eta)*(1-eta-target))
    requirements=dict(ideal_ordinary_complex=target/(1-target),ordinary=necessary,
        complex=(necessary+zeta)/(1-beta),optimized_coarse=necessary*(1-OLD)/(1-necessary))
    ordinary_upper=bb['upper']/(1+bb['upper']-OLD)
    native_upper=min(ordinary_upper,cb['upper']);ceiling=native_upper/(1+native_upper)
    require(ceiling<target,'Fixed-profile free-penalty obstruction fails')
    controls=[]
    def reject(name,call):
        try:call()
        except (KeyError,ValueError,ZeroDivisionError):controls.append(name)
        else:raise ValueError('Negative control accepted: '+name)
    reject('fixed-profile assembly advertised at latest1percentfloor',lambda:balanced(bridge,b,beta,eta,zeta,kappa=target))
    reject('preceding unpaid atom grid',lambda:full_bridge(physical,scalar,coarse,atom-Q(1,10**12)))
    reject('new physical slots substituted for virtual scalar roles',lambda:full_bridge(
        physical,dict(scalar,R=physical['physical_R']),coarse,atom))
    reject('old161 logical width grafted onto new word',lambda:full_bridge(
        dict(physical,W_per_vertex=15681),scalar,coarse,atom))
    reject('old separate prefix at balanced public parameters',lambda:balanced(
        bridge,b,beta,eta,zeta,kappa=public,old_prefix=True))
    reject('literal scalar bill omitted',lambda:balanced(
        dict(bridge,strict_literal_gap=0),b,beta,eta,zeta,kappa=public))
    reject('source hash corrupted',lambda:pinned(args.sprint,dict(config['inputs']['physical'],sha256='0'*64)))
    result=dict(status='PASS conditional revised168 exact arithmetic and fixed-profile obstruction',
        source_pins=config,config_sha256=sha256(args.config.read_bytes()).hexdigest(),
        bit_profile=bp,complex_profile=cp,bit_root=bb,complex_root=cb,
        bridge=bridge,assembly=assembly,numeric_cutoffs=cutoffs(bridge,assembly),
        target=dict(kappa=target,required_ratio=Q(config['required_ratio']),requirements=requirements,
            sufficient_1e12_points={key:Q(ceil(value*10**12),10**12) for key,value in requirements.items()}),
        fixed_profile_obstruction=dict(ordinary_upper=ordinary_upper,complex_upper=cb['upper'],
            controlling_upper=native_upper,balanced_upper=ceiling,shortfall=target-ceiling,
            scope='Every parameter choice in the retained paid balanced family on these fixed complete profiles. Does not rule out genuine frame, alias, local circuit or module changes.'),
        rejected_controls=controls,
        source_comparison=config['source_comparison'],
        exclusions=['No source producer, all-column scalar replay, local-ring prime audit or literal reflected geometry is performed by this arithmetic checker.',
            'General ordinary/restoration, Clifford/shared-core, routing/layout, analytic precision, recovery and fixed-tape interfaces remain inherited conditional hypotheses.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS revised168 κ='+str(public)+'; paid fixed-profile ceiling '+str(ceiling)+' below one-percent floor '+str(target))


if __name__=='__main__':main()
