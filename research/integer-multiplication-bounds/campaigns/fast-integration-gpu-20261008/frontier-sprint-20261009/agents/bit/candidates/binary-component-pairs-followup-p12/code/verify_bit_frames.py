#!/usr/bin/env python3
"""Regenerate a paid bit profile and exact moment from an explicit frame plan.

Checks all formal F2 columns, optionally the defining integer decoder, and exact
finite Gram determinants. The source-specific all-size weighted compiler,
ordinary wrapper and stopping transfer remain inherited contracts. This script
does not promote its native ordinary supplier to a final multiplication kappa.

Inherited PR161/PR163 checker and moment code retain Apache-2.0 licensing and
their author/AI-assistance attribution. New glue prepared with OpenAI assistance.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

sys.dont_write_bytecode=True
from bit_frame_search import load_candidate, need, sha


def prime_witnesses(word,plan,source):
    path=source/'research/paired-cube-balanced-161/bit/prime_witnesses.py'
    spec=importlib.util.spec_from_file_location('retained_prime_witnesses',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    groups={}
    for i,B in plan['frames']:
        key=json.dumps(B,separators=(',',':'));groups.setdefault(key,[]).append(i)
    records=[]
    for key,ops in sorted(groups.items()):
        B=json.loads(key);A,_=word.module.kernel(B,word.h)
        need(len(A)+len(B)==word.h and all(sum(a*b for a,b in zip(x,y))==0 for x in A for y in B),
             'exact annihilator represents same rational frame')
        rows=B if len(B)<=len(A) else A;s=list(map(sum,rows))
        gram=[[9*sum(a*b for a,b in zip(x,y))-s[i]*s[j] if rows is B else
               (9-word.h)*sum(a*b for a,b in zip(x,y))+s[i]*s[j]
               for j,y in enumerate(rows)] for i,x in enumerate(rows)]
        determinant=module.det(gram)
        need(0<abs(determinant)<2**80,'every new Gram determinant nonzero and below retained prime threshold')
        records.append(dict(basis_sha256=hashlib.sha256(key.encode()).hexdigest(),operations=ops,
                            dimension=len(B),representation='basis' if rows is B else 'annihilator',
                            defining_integer_rows=rows,cleared_gram_determinant=determinant))
    return dict(status='PASS exact finite prime compatibility',frames=len(plan['frames']),unique_bases=len(records),
                maximum_determinant_bits=max(abs(r['cleared_gram_determinant']).bit_length() for r in records),
                ambient_cleared_gram_determinant=9**23*(9-word.h),mandatory_small_exclusions=[2,3],
                prime_lower_bound=2**80,all_new_Gram_determinants_below_threshold=True,frame_witnesses=records,
                inherited_exclusions_retained=True,
                projector_rule='B basis: 9BBt-(B1)(B1)t; ker A: (9-h)AAt+(A1)(A1)t. The ambient denominator 9-h is also a unit.',
                scope='Define each large frame as ker A. Every q>2^80 avoids the chosen nonzero determinants; original frame exclusions retained.')


def apply_plan(word,plan):
    need(type(plan)is dict and plan['p']==12,'p12 plan')
    word.opframe=[word.nf[x] for _,_,x in word.ops]
    seen=set()
    for i,B in plan['frames']:
        need(type(i)is int and 0<=i<len(word.ops) and i not in seen,'valid unique operation index')
        need(B and all(len(r)==word.h and all(type(x)is int for x in r) for r in B),'nonempty integer frame basis')
        seen.add(i);word.opframe[i]=word.register(B)
    word.changed_frames=sorted(seen)
    for i,(a,b,_) in enumerate(word.ops):
        word.endframe[a]=word.opframe[i];word.endframe[b]=word.opframe[i]


def main():
    need(not sys.flags.optimize,'assertions enabled')
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--source-pins',type=Path,default=Path(__file__).resolve().parents[1]/'source-inputs.json')
    ap.add_argument('--integer-decoder',action='store_true');args=ap.parse_args()
    need(not args.output.exists(),'fresh verification output required');args.output.mkdir(parents=True)
    word_source=args.source.resolve();started=time.monotonic();plan=json.loads(args.plan.read_text())
    pins=json.loads(args.source_pins.read_text())
    for name,record in pins['files'].items():
        need(sha(word_source/name)==record['sha256'],f'source fingerprint differs: {name}')
    word=load_candidate(word_source);apply_plan(word,plan)
    word.exact_frames();row=word.row()
    print(json.dumps(dict(stage='exact geometry and complete paid row',elapsed=time.monotonic()-started,
                         changed=len(plan['frames']),mass=row['rank_per_vertex'],deficit=row['deficit_per_vertex'])),flush=True)
    formal=[word.formal(2)]
    if args.integer_decoder:formal.append(word.formal(0))
    print(json.dumps(dict(stage='all formal variables',formal=formal,elapsed=time.monotonic()-started)),flush=True)
    controls={}
    for tamper in ('omit_compensation','missing_partner'):
        try:word.formal(2,tamper)
        except ValueError:controls[tamper]='REJECTED'
        else:raise ValueError('adverse formal control accepted: '+tamper)
    first=word.changed_frames[0];old=word.opframe[first];word.opframe[first]=word.register([])
    try:word.exact_frames()
    except ValueError:controls['zero_operation_frame']='REJECTED'
    else:raise ValueError('zero operation frame accepted')
    word.opframe[first]=old
    badplan=dict(p=12,frames=[[len(word.ops),plan['frames'][0][1]]])
    try:apply_plan(word,badplan)
    except ValueError:controls['out_of_range_index']='REJECTED'
    else:raise ValueError('invalid frame index accepted')
    apply_plan(word,plan)
    primes=prime_witnesses(word,plan,word_source)
    sys.path.insert(0,str(word_source/'research/paired-cube-balanced-161/bit'))
    sys.path.insert(0,str(word_source/'research/paired-cube-balanced-161/arithmetic'))
    from prove import certify,js
    cert=certify(row)
    fixed_atom=Fraction(1,1000);old=Fraction(384599,10**10)
    coarse_12=Fraction((cert['coarse_saving']*10**12).numerator//(cert['coarse_saving']*10**12).denominator,10**12)
    fixed_ordinary=(1-fixed_atom)*coarse_12+fixed_atom*old
    need(fixed_ordinary<fixed_atom<1-fixed_ordinary,'retained atom tolls paid')
    cert['retained_atom_supplier']=dict(coarse_saving=coarse_12,atom_beta=fixed_atom,old_atom_saving=old,
                                         ordinary_saving=fixed_ordinary,scope='Conservative 1e-12 coarse grid; retained atom1e-3.')
    print(json.dumps(dict(stage='rigorous paid moment and stopping',coarse=js(cert['coarse_saving']),
                         ordinary=js(cert['ordinary_saving']),elapsed=time.monotonic()-started)),flush=True)
    result=dict(status='EXACT_FINITE',verified_utc=datetime.now(timezone.utc).isoformat(),
                source_commit='15c702a929b7d640107a95e196186ad74e876c82',profile=row,formal=formal,controls=controls,
                prime_witnesses=primes,moment=cert,wall_seconds=time.monotonic()-started,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                plan_sha256=sha(args.plan),verifier_sha256=sha(Path(__file__)),
                source_pins_sha256=sha(args.source_pins),source_fingerprints_verified=True,
                inherited_all_size_contracts=['weighted local-ring uniform compiler','proper projector atom adapters',
                    'ordinary wrapper restoration','stopped recurrence','three-stage completed core sharing'],
                exclusions=['independent exported-word reflected replay','full multiplication assembly','accepted final kappa'])
    for name,value in [('result.json',result),('profile.json',row),('moment.json',cert),('prime-witnesses.json',primes)]:
        (args.output/name).write_text(json.dumps(js(value),indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status='EXACT_FINITE',coarse=js(cert['coarse_saving']),ordinary=js(cert['ordinary_saving']),
                         changed=len(plan['frames']),maximum_determinant_bits=primes['maximum_determinant_bits'],
                         wall_seconds=time.monotonic()-started,peak_rss_kib=result['peak_rss_kib'])),flush=True)


if __name__=='__main__':main()
