#!/usr/bin/env python3
"""Check complete arithmetic for the balanced lifetime/fused168-170 package.

Finite word, unit-prime and reflected physical geometry gates are separate.
Apache-2.0; prepared with OpenAI GPT-6.1 Sol assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import json
import sys

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from transfer_math import (BAD,balanced,cutoffs,floor_strict,full_bridge,js,moment,profile,require)


def reconstruct(row):
    hist=Counter()
    for name in ('local_histogram','source_data_histogram','target_data_histogram'):
        for rank,count in row[name].items():hist[int(rank)]+=3*int(count)
    for rank,count in row['physical_gauge_histogram'].items():hist[3*int(rank)]+=int(count)
    hist[2]+=2*row['v'];hist.pop(0,None)
    require(dict(hist)=={int(rank):count for rank,count in row['child_histogram'].items() if count},
            'Complete component histogram mismatch')
    result=profile(row['m'],row['W_per_vertex'],hist)
    require(result['m']==3*row['h'] and result['W']==2*row['v']+row['physical_R'],
            'Physical persistent role inventory mismatch')
    require(row['physical_R']==row['R']-row['pairs'] and result['mass']==row['rank_per_vertex'] and
            result['m']*result['W']-result['mass']==row['deficit_per_vertex']==2*row['v']-3*row['loss'],
            'Paid role/alias/rank inventory mismatch')
    return result


def verify(folder):
    require(not sys.flags.optimize,'Optimized Python execution is unsupported')
    inputs=json.loads((folder/'transfer-inputs.json').read_bytes())
    require(inputs['candidate_id']=='balanced-lifetime-fused-168-170-20261009','Wrong scientific identity')
    data={}
    for key,item in inputs['files'].items():
        raw=(folder/item['path']).read_bytes()
        require(len(raw)==item['bytes'] and sha256(raw).hexdigest()==item['sha256'],'Changed source/input: '+item['path'])
        if item['path'].endswith('.json'):data[key]=json.loads(raw)
    params=inputs['parameters']
    a0,theta,b,beta,eta,zeta,kappa=(Q(params[key]) for key in
        ('coarse','atom','complex_saving','phase_stop','backoff','strict_weakening','kappa'))
    bit,physical,scalar=(data[key] for key in ('bit','physical','scalar'))
    bp,cp=reconstruct(bit),reconstruct(physical)
    require((bp['m'],bp['W'],bp['mass'],bp['maxchild'])==tuple(inputs['expected_bit_inventory']),
            'Frozen binary inventory changed')
    require((bit['R'],bit['physical_R'],bit['pairs'],bit['v'],bit['loss'])==tuple(inputs['expected_bit_roles']),
            'Frozen binary persistent roles changed')
    require((cp['m'],cp['W'],cp['mass'],cp['maxchild'])==tuple(inputs['expected_complex_inventory']),
            'Frozen complex inventory changed')
    require(len(data['bit_frames']['pairs'])==bit['pairs'] and
            len(data['bit_frames']['frames'])==bit['changed_operation_frames'] and
            data['bit_frames']['source_sha256']==bit['source_sha256'], 'Binary selected plan/source binding')
    require(len(data['complex_frames'])==physical['changed_operation_frames'] and
            len(data['complex_pairs'])==physical['pairs'],'Complex selected plan/source binding')
    bm,cm=moment(bp,a0,BAD),moment(cp,b)
    bn=moment(bp,a0+Q(params['bit_next_grid_step']),BAD)
    cn=moment(cp,b+Q(params['complex_next_grid_step']))
    require(bm['upper']<1<bn['lower'] and cm['upper']<1<cn['lower'],'Complete moments or successor exclusions fail')
    rank=bp['mass']+BAD*32*bp['m']**2*bp['edges']
    require(rank<bp['m']*bp['W'] and Q(2*bp['m']**3,2**80)<BAD,'Complete bad-class bill fails')
    bridge=full_bridge(physical,scalar,a0,theta)
    assembly=balanced(bridge,b,beta,eta,zeta,kappa=kappa)
    require(kappa==floor_strict(assembly['g'],10**12),'Deliberate final grid is not exact')
    public=Q(params['comparison_public_kappa']);target=Q(params['required_publication_ratio'])*public
    require(kappa>=target,'Pinned one-percent publication condition fails')
    controls=[]
    def reject(name,call):
        try:call()
        except (KeyError,ValueError,ZeroDivisionError):controls.append(name)
        else:raise ValueError('Invalid control accepted: '+name)
    reject('previous unpaid atom grid',lambda:full_bridge(physical,scalar,a0,theta-Q(1,10**12)))
    reject('next final twelve-digit grid',lambda:balanced(bridge,b,beta,eta,zeta,kappa=kappa+Q(1,10**12)))
    reject('old prefix',lambda:balanced(bridge,b,beta,eta,zeta,kappa=kappa,old_prefix=True))
    reject('old nonlinear guard',lambda:balanced(bridge,b,beta,eta,zeta,kappa=kappa,old_guard=True))
    reject('old separate movement bills',lambda:balanced(bridge,b,beta,eta,zeta,kappa=kappa,old_exposures=True))
    reject('zero phase stop',lambda:balanced(bridge,b,Q(0),eta,zeta,kappa=kappa))
    reject('zero geometry reserve',lambda:balanced(bridge,b,beta,Q(0),zeta,kappa=kappa))
    reject('virtual scalar stock collapsed',lambda:full_bridge(physical,dict(scalar,R=physical['physical_R']),a0,theta))
    reject('persistent width shortened',lambda:full_bridge(dict(physical,W_per_vertex=physical['W_per_vertex']-1),scalar,a0,theta))
    reject('literal scalar bill omitted',lambda:balanced(dict(bridge,strict_literal_gap=0),b,beta,eta,zeta,kappa=kappa))
    reject('external rows omitted',lambda:balanced(dict(bridge,row_gap=Q(-1)),b,beta,eta,zeta,kappa=kappa))
    damaged=copy.deepcopy(bit);damaged['child_histogram']['1']+=1
    reject('unregenerated binary histogram',lambda:reconstruct(damaged))
    damaged=copy.deepcopy(physical);damaged['child_histogram']['1']+=1
    reject('unregenerated complex histogram',lambda:reconstruct(damaged))
    return js(dict(status='PASS conditional lifetime/fused paid balanced-transfer arithmetic',
        candidate_id=inputs['candidate_id'],kappa=kappa,source_inputs=inputs,
        bit_profile=bp,complex_profile=cp,bit_moment=bm,bit_next_grid=bn,complex_moment=cm,complex_next_grid=cn,
        contaminated_bit_rank=rank,finite_bridge=bridge,assembly=assembly,numeric_cutoffs=cutoffs(bridge,assembly),
        public_comparison=dict(pinned_head=params['comparison_public_head'],public_kappa=public,ratio=kappa/public,
            exact_improvement=kappa-public,publication_floor=target,surplus=kappa-target),
        rejected_controls=controls,
        scope='Exact source-bound arithmetic. Independent finite binary, signed/reflected complex and unit-prime checks, plus inherited all-size interfaces and live frontier refresh, remain required.'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs-root',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--check',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=verify(args.inputs_root)
    if args.check:require(result==json.loads(args.check.read_bytes()),'Derived certificate does not reproduce')
    if args.output:
        require(not args.output.exists(),'Output must be fresh')
        args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS '+result['candidate_id']+' kappa='+result['kappa']+'; complete moments/full bills/47+7; '+
          str(len(result['rejected_controls']))+' rejected controls')


if __name__=='__main__':main()
