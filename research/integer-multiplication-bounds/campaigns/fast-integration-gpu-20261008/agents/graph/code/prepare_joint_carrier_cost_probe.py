#!/usr/bin/env python3
"""Certify actual ordered matrix costs for legal joint carrier alternatives.

Frames come from an immutable source-reconstructed physical word. The scalar
parent is rebuilt from pinned PR62. Probe transitions are not a computation
network; R=0 and the positive mass is explicit. Per-edge moments guide search,
while every selected physical word must be independently compiled and scored.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import time

from check_compiled_witness import contained
import joint_signed_word_recompile as joint
import joint_region_search_v3 as region
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'geometry' / 'code'))
from decompose_common_context_profiles import pivot_run_histogram


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--parents',type=Path,required=True)
    parser.add_argument('--frame-receipt',type=Path,required=True)
    parser.add_argument('--h',type=int,required=True)
    parser.add_argument('--basis',required=True)
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--resume-prepared',action='store_true',
                        help='Validate and finish an existing immutable prepared probe without repeating native ranks')
    args = parser.parse_args()
    assert not args.output.exists()
    if args.resume_prepared:
        assert args.work.is_dir()
    else:
        assert not args.work.exists()
        args.work.mkdir(parents=True)
    started = time.monotonic()
    joint.initialize(args.source,args.work)
    parents = [p for p in json.loads(args.parents.read_text()) if p['h']==args.h]
    assert len(parents)==1
    document = parents[0]
    receipt = json.loads(args.frame_receipt.read_text())
    assert receipt['source_only'] and receipt['h']==args.h
    assert receipt['source_parent_sha256']==document['word_sha256']
    assert receipt['source_permutation']==document['Q']
    raw = gzip.decompress(Path(receipt['word_path']).read_bytes())
    assert sha256(raw).hexdigest()==receipt['word_sha256']
    actual_word = json.loads(raw)
    c,old_blocks,old_owner,old_word,ordinary,maximal,successors,closure,parent_digest = joint.prepare(document)
    aliases = actual_word['physical_region_address_aliases']
    frames = [(int(f[0]),int(f[1]),tuple(f[2])) for f in actual_word['frames']]
    labels = [frames[i] for i in aliases]
    assert len(labels)==len(old_blocks)
    built = joint.build(c,labels,old_owner,'preserve-regions','original')
    _,blocks,uses,value_uses,owner,signal,order,_ = built
    all_frames = [(0,0,(0,)*args.h),(args.h,0,(0,)*args.h)]
    lookup = {frame:i for i,frame in enumerate(all_frames)}
    ids = []
    for block in blocks:
        frame = block['frame']
        if frame not in lookup:
            lookup[frame]=len(all_frames)
            all_frames.append(frame)
        ids.append(lookup[frame])
    pairs,zero_pairs = set(),set()
    def add(a,b):
        A,B = all_frames[a],all_frames[b]
        if A[0]==B[0]:
            assert a==b or (contained(A,B) and contained(B,A))
            zero_pairs.add((a,b))
        else:
            assert A[0]<B[0]
            assert a==0 or b==1 or contained(A,B)
            pairs.add((a,b))
    carrier_path = args.work/'carriers.bin'
    carriers = 0
    with carrier_path.open('rb' if args.resume_prepared else 'wb') as stream:
        for g,block in enumerate(blocks):
            for u,i in block['candidates']:
                value,target,terminal = uses[u]
                provider = owner[value]
                G,T,P = ids[g],ids[target],ids[provider]
                for a,b in [(G,T),(G,1),(0,P),(P,T),(T,1)]:
                    add(a,b)
                # Exact source region/use/row index plus actual frame IDs.
                packed = struct.pack('<7I',g,u,i,value,G,T,P)
                if args.resume_prepared:
                    assert stream.read(len(packed)) == packed
                else:
                    stream.write(packed)
                carriers += 1
        if args.resume_prepared:
            assert stream.read(1) == b''
    pairs = sorted(pairs)
    mass = sum(all_frames[b][0]-all_frames[a][0] for a,b in pairs)
    probe = args.work/'carrier-cost-probe.bin'
    with probe.open('rb' if args.resume_prepared else 'wb') as stream:
        def emit(packed):
            if args.resume_prepared:
                assert stream.read(len(packed)) == packed
            else:
                stream.write(packed)
        emit(struct.pack('<6I2Q',args.h,len(c.inputs),0,len(all_frames),len(pairs),0,mass,0))
        for rank,forced,symbols in all_frames:
            emit(struct.pack('<QI',forced,rank))
            emit(struct.pack('<'+str(args.h)+'b',*symbols))
        for a,b in pairs:
            emit(struct.pack('<2Iq',a,b,1))
        if args.resume_prepared:
            assert stream.read(1) == b''
    print(json.dumps(dict(status='actual carrier-cost probe prepared',h=args.h,
                         carriers=carriers,positive_pairs=len(pairs),zero_pairs=len(zero_pairs),
                         rank_mass=mass,probe_sha256=sha256(probe.read_bytes()).hexdigest())),flush=True)
    profile,audit = args.work/'profile.json',args.work/'transitions.json'
    if not args.resume_prepared:
        with (args.work/'native.log').open('wb') as log:
            subprocess.run([str(args.binary),str(probe),args.basis,str(profile),str(audit)],
                           check=True,stdout=log,stderr=subprocess.STDOUT)
    certified = json.loads(profile.read_text())
    assert certified['h']==args.h and certified['basis']==args.basis
    assert certified['R']==0 and certified['rank_sum']==mass and certified['frames']==len(all_frames)
    rows = json.loads(audit.read_text())['transitions']
    audit_pairs = {(a,b) for a,b in pairs if all_frames[b][0]-all_frames[a][0]>1 and (a,b)!=(0,1)}
    assert {(r['a'],r['b']) for r in rows}==audit_pairs
    costs = []
    a = 1284995399/25000000000000
    for row in rows:
        histogram = pivot_run_histogram(row['pivots'],1)
        assert sum(t*n for t,n in histogram.items())==row['rank']
        cost = sum(t*n*math.expm1(a*math.log(575/t)) for t,n in histogram.items())
        costs.append(dict(a=row['a'],b=row['b'],histogram=histogram,screen_moment=cost))
    for donor,target in pairs:
        if (donor,target) not in audit_pairs:
            rank = all_frames[target][0]-all_frames[donor][0]
            assert rank==1 or (donor,target)==(0,1)
            costs.append(dict(a=donor,b=target,histogram={rank:1},
                              screen_moment=rank*math.expm1(a*math.log(575/rank)),
                              analytic_profile='rank-one' if rank==1 else 'literal-identity'))
    assert len(costs)==len(pairs)
    total = Counter()
    for cost in costs:
        total.update(cost['histogram'])
    assert [total[t] for t in range(args.h+1)]==certified['blocks']
    (args.work/'matrix-costs.json').write_text(json.dumps(dict(basis=args.basis,screen_a=a,rows=costs),separators=(',',':'))+'\n')
    result = dict(status='DISCOVERY exact CRT ordered carrier-cost table PASS',
                  h=args.h,basis=args.basis,parent=document,source_word_sha256=receipt['word_sha256'],
                  frame_receipt=str(args.frame_receipt),frame_receipt_sha256=sha256(args.frame_receipt.read_bytes()).hexdigest(),
                  carriers=carriers,positive_transition_pairs=len(pairs),exact_zero_pairs=len(zero_pairs),
                  probe_rank_mass=mass,probe_path=str(probe),probe_sha256=sha256(probe.read_bytes()).hexdigest(),
                  carrier_path=str(carrier_path),carrier_sha256=sha256(carrier_path.read_bytes()).hexdigest(),
                  matrix_cost_path=str(args.work/'matrix-costs.json'),
                  profile_path=str(profile),profile_sha256=sha256(profile.read_bytes()).hexdigest(),
                  transition_audit_path=str(audit),transition_audit_sha256=sha256(audit.read_bytes()).hexdigest(),
                  native_binary_sha256=sha256(args.binary.read_bytes()).hexdigest(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                  scope='A cost probe is not an accepted network. Floating moments only order discovery. Matrix costs are exact profiles; all selected matching, reclamation and full physical words must be rebuilt and scored before accepting any exponent.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
