#!/usr/bin/env python3
"""Recompute source-bound supplier moments and all paid balanced-transfer bills.

This is the standard-library arithmetic gate. Finite scalar/frame/reflection
and local-ring presentation verification remain separately required checks.
Apache-2.0; prepared with OpenAI GPT-6.1 Sol assistance.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

from transfer_math import (BAD,OLD,PUBLIC,balanced,cutoffs,floor_strict,
    full_bridge,js,moment,profile,require)


def verify(folder):
    require(not sys.flags.optimize,'Optimized Python execution is unsupported')
    inputs=json.loads((folder/'transfer-inputs.json').read_text())
    data={}
    for name,record in inputs['files'].items():
        path=folder/record['path'];raw=path.read_bytes()
        require(sha256(raw).hexdigest()==record['sha256'],'Changed input: '+record['path'])
        if name in ('bit','complex','scalar'):
            data[name]=json.loads(raw)
    coarse,atom,b,beta,eta,weakening,kappa=(Q(inputs[k]) for k in
        ('coarse_bit_saving','atom_exponent','complex_saving','phase_stop',
         'balanced_backoff','strict_weakening','kappa'))
    require((atom,beta,eta)==(Q(1,1000),Q(1,10**9),Q(1,10**8)),
            'Frozen stopping parameters changed')
    bit,physical,scalar=(data[k] for k in ('bit','complex','scalar'))
    bp=profile(bit['m'],bit['W_per_vertex'],bit['child_histogram'])
    cp=profile(physical['m'],physical['W_per_vertex'],physical['child_histogram'])
    require((bp['m'],bp['W'],bp['mass'],bp['maxchild'])==(72,26888,1934000,60),
            'Frozen binary inventory changed')
    require((cp['m'],cp['W'],cp['mass'],cp['maxchild'])==(66,15681,1033626,20),
            'Frozen complex inventory changed')
    bm=moment(bp,coarse,BAD);cm=moment(cp,b)
    bn=moment(bp,coarse+Q(1,10**12),BAD);cn=moment(cp,b+Q(1,10**12))
    require(bm['upper']<1<bn['lower'] and cm['upper']<1<cn['lower'],
            'Full supplier moment/grid inequality failed')
    rank=bp['mass']+BAD*32*bp['m']**2*bp['edges']
    require(rank<bp['m']*bp['W'] and Q(2*bp['m']**3,2**80)<BAD,
            'Full local-ring fallback allowance failed')
    f=full_bridge(physical,scalar,coarse,atom)
    result=balanced(f,b,beta,eta,weakening,kappa=kappa)
    require(result['a']==f['ordinary_saving'] and kappa>PUBLIC,
            'Actual supplier or frozen predecessor comparison failed')
    controls=[]
    def reject(name,call):
        try:call()
        except (KeyError,ValueError,ZeroDivisionError):controls.append(name)
        else:raise ValueError('Invalid control accepted: '+name)
    reject('unpaid old prefix at balanced parameters',lambda:balanced(f,b,beta,eta,weakening,
        old_prefix=True,kappa=kappa))
    reject('old nonlinear guard',lambda:balanced(f,b,beta,eta,weakening,old_guard=True,kappa=kappa))
    reject('old separate movement exposures',lambda:balanced(f,b,beta,eta,weakening,
        old_exposures=True,kappa=kappa))
    reject('first final grid above exact margin',lambda:balanced(f,b,beta,eta,weakening,
        kappa=floor_strict(result['g'],10**18)+Q(1,10**18)))
    reject('zero phase stop',lambda:balanced(f,b,Q(0),eta,weakening,kappa=kappa))
    reject('virtual scalar stock collapsed',lambda:full_bridge(physical,
        dict(scalar,R=physical['physical_R']),coarse,atom))
    reject('persistent stock shortened',lambda:full_bridge(
        dict(physical,W_per_vertex=physical['W_per_vertex']-1),scalar,coarse,atom))
    reject('literal scalar gap removed',lambda:balanced(dict(f,strict_literal_gap=0),
        b,beta,eta,weakening,kappa=kappa))
    reject('external rows removed',lambda:balanced(dict(f,row_gap=Q(-1)),
        b,beta,eta,weakening,kappa=kappa))
    return js(dict(status='PASS conditional paid balanced-transfer arithmetic',
        kappa=kappa,source_inputs=inputs,ordinary_bit_saving=f['ordinary_saving'],
        bit_profile=bp,complex_profile=cp,bit_moment=bm,bit_next_grid=bn,
        complex_moment=cm,complex_next_grid=cn,contaminated_bit_rank=rank,
        finite_bridge=f,assembly=result,numeric_cutoffs=cutoffs(f,result),
        pinned_predecessor_kappa=PUBLIC,exact_improvement=kappa-PUBLIC,
        rejected_controls=controls,
        scope='Source-bound arithmetic only. The finite signed words, both geometric orientations, eligible-prime frame implementation and all-size interfaces remain separate required inputs.'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs-root',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--check',type=Path,help='Compare every recomputed exact field with this derived certificate')
    parser.add_argument('--output',type=Path,help='Authoring: write a fresh derived certificate')
    args=parser.parse_args();result=verify(args.inputs_root)
    if args.check:
        require(result==json.loads(args.check.read_text()),'Derived certificate does not reproduce')
    if args.output:
        require(not args.output.exists(),'Output must be fresh')
        args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS kappa='+result['kappa']+'; complete moments, finite bills, 47 inequalities, seven margins; '+
          str(len(result['rejected_controls']))+' rejected arithmetic controls.')


if __name__=='__main__':main()
