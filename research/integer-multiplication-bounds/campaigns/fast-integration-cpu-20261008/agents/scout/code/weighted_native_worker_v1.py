#!/usr/bin/env python3
"""One serial CPU worker for changed native ORIGINAL fixed-profile matchings.

Exact occurrence fingerprints deduplicate matchings before full five-prime
profiling. A one-field derivative proxy chooses ties; every retained saving
comes from the complete fixed-both controller and exact rational enclosure.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time

import fixed_controller_score as score
from check_changed_fixed_dag import parse_dag


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def occurrence_check(path, dag):
    data = path.read_bytes()
    n,count = struct.unpack_from('<2I',data)
    assert n == dag['n'] and len(data) == 8+count*8
    values = struct.unpack_from('<%dI' % (2*count),data,8)
    pairs = sorted(zip(values[::2],values[1::2]))
    assert len({a for a,b in pairs}) == count and len({b for a,b in pairs}) == count
    for donor,use in pairs:
        assert dag['active'][donor] and dag['args'][2*donor]
        if use >> 31:
            j = use & 0x7fffffff
            assert j < dag['q']
            target = value = dag['roots'][j]
            when = n+j
        else:
            target = use//2
            assert 0 < target < n and dag['active'][target] and dag['args'][2*target]
            value = dag['args'][2*target+(use&1)]
            when = target
        assert value in dag['args'][2*donor:2*donor+2]
        ru,rv,rt = (dag['ranks'][x] for x in (donor,value,target))
        assert rv <= ru <= rt and (ru < rt or donor < when)
        assert not dag['core'][target] & ~dag['core'][donor]
        assert not dag['cover'][donor] & ~dag['cover'][target]
    canonical = struct.pack('<2I',n,count)+b''.join(struct.pack('<2I',*pair) for pair in pairs)
    return dict(matched=count,canonical_exact_occurrence_sha256=hashlib.sha256(canonical).hexdigest(),
                distinct_donors=True,distinct_uses=True,all_original_nested_uses_valid=True)


def safe_search(counts):
    low,high = 0,10**12
    while high-low > 1:
        mid = (low+high)//2
        r = score.moment(counts['m'],counts['W'],counts['child_multiplicities'],F(mid,10**16))
        if r['strictly_passes']:
            low = mid
        else:
            high = mid
    saving = F(low-1000,10**16)
    assert saving > 0
    result = score.moment(counts['m'],counts['W'],counts['child_multiplicities'],saving)
    assert result['strictly_passes']
    return dict(safe_saving=str(saving),grid_denominator=10**16,margin_ticks=1000,
                lower_grid_tick=low,upper_grid_tick=high,verified_moment=result)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profiler',required=True,type=Path)
    ap.add_argument('--first-dag',required=True,type=Path)
    ap.add_argument('--second-dag',required=True,type=Path)
    ap.add_argument('--first-profile',required=True,type=Path)
    ap.add_argument('--second-profile',required=True,type=Path)
    ap.add_argument('--saving',required=True,type=F)
    ap.add_argument('--output',required=True,type=Path)
    args = ap.parse_args()
    assert __debug__
    args.output.mkdir(parents=True,exist_ok=False)
    copied,args_inputs = [],[]
    base = []
    for axis,(d,p) in enumerate(((args.first_dag,args.first_profile),(args.second_dag,args.second_profile))):
        local = args.output/('axis%d'%axis)
        local.mkdir()
        dag,profile = local/'input.bin',local/'base-profile.json'
        shutil.copyfile(d,dag)
        shutil.copyfile(p,profile)
        copied.append(dag)
        base.append(json.loads(profile.read_text()))
        args_inputs.extend([dict(role='axis%d_dag'%axis,source=str(d),local=str(dag),sha256=sha(dag)),
                            dict(role='axis%d_base_profile'%axis,source=str(p),local=str(profile),sha256=sha(profile))])
    assert [r['h'] for r in base] == [23,25]
    base_counts = score.profile(*base)
    assert score.moment(base_counts['m'],base_counts['W'],base_counts['child_multiplicities'],args.saving)['strictly_passes']
    seeds = [(0,0),(1,0),(17,100),(2,10),(3,100),(4,1000),(5,10000),(7,0)]
    protocol = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),worker_pid=os.getpid(),
                    worker_sha256=sha(Path(__file__)),profiler=str(args.profiler),profiler_sha256=sha(args.profiler),
                    score_sha256=sha(Path(score.__file__)),inputs=args_inputs,seed_noise_pairs=seeds,
                    native_geometry='UNCHANGED ordered23/25 fixed-both source/data/output families',
                    reference_saving=str(args.saving),threads=1,
                    matching='ORIGINAL frames; max-cardinality HK with one-field matrix surrogate tie order',
                    deduplication='canonical sorted donor/exact-use pairs, including operand/root tags',
                    scope='Finite exact witness search; all-size native machine hypotheses remain conditional')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    dags = [parse_dag(d) for d in copied]
    for axis in (0,1):
        assert dags[axis]['h'] == base[axis]['h'] and dags[axis]['loss'] == base[axis]['loss']
    seen,completed = [set(),set()],[]
    for seed,noise in seeds:
        for axis in (0,1):
            began = time.monotonic()
            label='axis%d-seed%d-noise%d'%(axis,seed,noise)
            match_links=args.output/(label+'.matching.links')
            with (args.output/(label+'.matching.json')).open('w') as out,(args.output/(label+'.matching.log')).open('w') as err:
                subprocess.run([str(args.profiler.resolve()),str(copied[axis]),str(match_links),str(seed),str(noise),'--matching-only'],check=True,stdout=out,stderr=err)
            matching=json.loads((args.output/(label+'.matching.json')).read_text())
            assert all(matching[k]==base[axis][k] for k in ('h','v','R','loss','rank_sum'))
            checked=occurrence_check(Path(str(match_links)+'.uses.bin'),dags[axis])
            identity=checked['canonical_exact_occurrence_sha256']
            row=dict(id=label,axis=axis,seed=seed,noise_milli=noise,matching=matching,
                     independent_occurrence_check=checked,duplicate_matching=identity in seen[axis])
            if identity not in seen[axis]:
                seen[axis].add(identity)
                full_links=args.output/(label+'.full.links')
                with (args.output/(label+'.full-matching.json')).open('w') as out,(args.output/(label+'.full.log')).open('w') as err:
                    subprocess.run([str(args.profiler.resolve()),str(copied[axis]),str(full_links),str(seed),str(noise)],check=True,stdout=out,stderr=err)
                assert occurrence_check(Path(str(full_links)+'.uses.bin'),dags[axis])['canonical_exact_occurrence_sha256']==identity
                profiled=Path(str(copied[axis])+'.fixed_ij_weighted_seed%d_noise%d.json'%(seed,noise))
                profile=json.loads(profiled.read_text())
                assert all(profile[k]==base[axis][k] for k in ('h','v','R','loss','rank_sum'))
                both=base[:]
                both[axis]=profile
                counts=score.profile(*both)
                searched=safe_search(counts)
                row.update(profile=profile,profile_sha256=sha(profiled),complete_controller=score.jsonable(counts),
                           **searched,reference_moment=score.moment(counts['m'],counts['W'],counts['child_multiplicities'],args.saving))
            row['elapsed_seconds']=time.monotonic()-began
            completed.append(row)
            (args.output/(label+'.json')).write_text(json.dumps(row,indent=2)+'\n')
            (args.output/'progress.json').write_text(json.dumps(dict(completed=len(completed),distinct_matchings=[len(s) for s in seen],rows=completed),indent=2)+'\n')
            print(json.dumps(dict(event='weighted_native_complete',pid=os.getpid(),id=label,duplicate=row['duplicate_matching'],saving=row.get('safe_saving'),seconds=row['elapsed_seconds'])),flush=True)
    summary=dict(status='completed_native_original_weighted_matching_family',cases=len(completed),
                 distinct_matchings=[len(s) for s in seen],profiles=sum('profile' in r for r in completed),
                 best_saving=max((r['safe_saving'] for r in completed if 'safe_saving' in r),key=F),
                 scope=protocol['scope'])
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()
