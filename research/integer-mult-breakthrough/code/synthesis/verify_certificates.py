#!/usr/bin/env python3
"""Bounded stdlib replay of auxiliary scalar and frozen-ledger certificates."""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import json
from pathlib import Path
import time

from frozen_ledger_bound import bound_moment, full_scalar_center_replay
from global_incidence import dirty_word, replay_dirty_word


DEFAULT_FIXTURE=Path(__file__).resolve().parents[2]/'fixtures/synthesis/auxiliary-scalar-and-ledger.json'


def verify(fixture, small_only=False):
    if fixture.get('schema_version')!=1:
        raise ValueError('Wrong fixture schema')
    checked=[]
    for expected in fixture['center_maps']:
        if small_only and expected['h']>7:
            continue
        actual=full_scalar_center_replay(expected['h'],expected['separate_sides'])
        for key,value in expected.items():
            if actual.get(key)!=value:
                raise ValueError(f'Certificate mismatch: {key}')
        checked.append(actual)
    root=fixture['zero_role_root']
    lo,hi=Q(root['lower']),Q(root['upper'])
    if not 0<lo<hi<Q(1,500):
        raise ValueError('Wrong strict root interval')
    if not bound_moment(lo)[1]<1 or not bound_moment(hi)[0]>1:
        raise ValueError('Root endpoints do not certify the stated bound')
    if bound_moment(Q(root['forbidden_binary_target']))[0]<=1:
        raise ValueError('Forbidden target is not excluded')
    return dict(scope=fixture['scope'],checked_center_maps=checked,
                strict_root_bracket=[str(lo),str(hi)],forbidden_target=root['forbidden_binary_target'])


def controls(fixture):
    bad=deepcopy(fixture)
    bad['center_maps'][0]['roles']+=1
    try:
        verify(bad,True)
    except ValueError:
        pass
    else:
        raise ValueError('A wrong capacity fixture was accepted')
    bad=deepcopy(fixture)
    bad['zero_role_root']['upper']=bad['zero_role_root']['lower']
    try:
        verify(bad,True)
    except ValueError:
        pass
    else:
        raise ValueError('A nonstrict root interval was accepted')
    for separate in [False,True]:
        word=dirty_word(6,separate)
        word['cnot_word']=word['cnot_word'][:-1]
        try:
            replay_dirty_word(word)
        except ValueError:
            pass
        else:
            raise ValueError('A corrupted literal word was accepted')
    return dict(wrong_capacity_rejected=True,nonstrict_interval_rejected=True,
                corrupted_literal_words_rejected=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture',type=Path,default=DEFAULT_FIXTURE)
    parser.add_argument('--small-only',action='store_true')
    args=parser.parse_args()
    start=time.monotonic()
    data=json.loads(args.fixture.read_text())
    receipt=verify(data,args.small_only)
    receipt['negative_controls']=controls(data)
    receipt['status']='EXACT AUXILIARY CERTIFICATE REPLAY PASS'
    receipt['seconds']=time.monotonic()-start
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
