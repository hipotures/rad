#!/usr/bin/env python3
"""Fresh source-only reconstruction of a changed carrier matching word.

Pinned scalar graph: Avi Eisenberg PR62. Invertible binary synthesis and
paid reclamation: eumemic PR57. Matching choices are explicit certificates,
not inferred from the candidate word. Every selected source/use/row, physical
capacity, chronology and actual signed frame is independently reconstructed.
Finite F2 payload checks and conditional all-array transfer remain distinct.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import time

import joint_region_search_v3 as region
import joint_signed_word_recompile as joint
import joint_positive_frontier as frontier
from joint_word_check_v4 import check
from matrix_weighted_joint_carriers import weighted_matcher

GEOMETRY=Path(__file__).resolve().parents[2]/'geometry'/'code'
sys.path.insert(0,str(GEOMETRY))
from mix_common_frame_families import select_family_frames


def write_word(path,word):
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as archive:
            archive.write(raw)
    return sha256(raw).hexdigest()


def selected_match(blocks,uses,order,selection):
    edges=[]
    for g,b in enumerate(blocks):
        b['selected']=set()
        edges.extend((g,u,i) for u,i in b['candidates'])
    lookup={edge:e for e,edge in enumerate(edges)}
    assert len(lookup)==len(edges)
    chosen=set();right={};position={g:i for i,g in enumerate(order)}
    for g,u,i in selection:
        assert (g,u,i) in lookup
        e=lookup[g,u,i]
        assert e not in chosen and u not in right
        value,target,terminal=uses[u]
        assert blocks[g]['inputs'][i]==value
        assert position[g]<position[target]
        assert region.COMPILER.independent(blocks[g]['outbasis'],1<<i)
        from check_compiled_witness import contained
        assert contained(blocks[g]['frame'],blocks[target]['frame'])
        chosen.add(e);right[u]=e;blocks[g]['selected'].add(e)
    for g,b in enumerate(blocks):
        carried=[1<<edges[e][2] for e in sorted(b['selected'])]
        assert len(region.COMPILER.basis(b['outbasis']+carried))==len(b['outbasis'])+len(carried)
    return edges,chosen,right,Counter()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--choices-file',type=Path,required=True)
    p.add_argument('--h',type=int,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--expected-word-sha256',required=True)
    p.add_argument('--profile-transitions',type=Path)
    choice=p.add_mutually_exclusive_group(required=True)
    choice.add_argument('--selected-matching',type=Path)
    choice.add_argument('--discovery-cost-receipt',type=Path)
    args=p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    started=time.monotonic()
    configs=[d for d in json.loads(args.choices_file.read_text()) if d['parent']['h']==args.h]
    assert len(configs)==1
    cfg=configs[0];parent=cfg['parent'];h=args.h;Q=parent['Q']
    config={k:v for k,v in parent['configuration'].items() if k!='kind'}
    joint.initialize(args.source,args.work)
    region.COMPILER.build=lambda dimension:region.build_regions(dimension,config)
    parent_compiled,original=region.COMPILER.compile_(h,matching=True,reclaim=True,dirty=True)
    c,old_blocks,_,_,old_owner,_,_,_=region.build_regions(h,config)
    scalar=c.verify()
    parent_path=args.work/'fresh-parent-word.json.gz'
    parent_digest=write_word(parent_path,original)
    assert parent_digest==parent['word_sha256']
    document=dict(id=f'fresh-h{h}-weighted',h=h,word_path=str(parent_path),word_sha256=parent_digest,Q=Q)
    frontier.initialize(args.work)
    old_word,ordinary,maximal,_,successors,_,_=frontier.parent(document)
    selected_word,selected,frame_summary=select_family_frames(old_word,ordinary,maximal,successors,cfg['choices'])
    selected_frame_path=args.work/'fresh-frame-family-word.json.gz'
    frame_digest=write_word(selected_frame_path,selected_word)
    def inverse_frame(frame):
        rank,forced,symbols=frame
        return rank,sum(1<<i for i in range(h) if forced>>Q[i]&1),tuple(symbols[Q[i]] for i in range(h))
    labels=[inverse_frame(frame) for frame in selected]
    built=joint.build(c,labels,old_owner,'preserve-regions','original')
    _,blocks,uses,_,owner,_,order,_=built
    if args.selected_matching:
        payload=args.selected_matching.read_bytes()
        matching=json.loads(gzip.decompress(payload) if args.selected_matching.suffix=='.gz' else payload)
        assert matching['h']==h and matching['source_parent_sha256']==parent_digest
        assert matching['frame_family_word_sha256']==frame_digest
        assert matching['source_permutation']==Q
        selection=[tuple(edge) for edge in matching['selected']]
    else:
        receipt=json.loads(args.discovery_cost_receipt.read_text())
        assert receipt['h']==h and receipt['source_word_sha256']==frame_digest
        assert receipt['basis']==cfg['basis']
        packed=Path(receipt['carrier_path']).read_bytes()
        assert sha256(packed).hexdigest()==receipt['carrier_sha256']
        cost_bytes=Path(receipt['matrix_cost_path']).read_bytes()
        table=json.loads(cost_bytes)
        costs={(r['a'],r['b']):r['screen_moment'] for r in table['rows']}
        weights={}
        for g,u,i,value,G,T,P in struct.iter_unpack('<7I',packed):
            assert uses[u][0]==value and blocks[g]['inputs'][i]==value
            assert (u,i) in blocks[g]['candidates']
            def cost(a,b):return 0.0 if a==b else costs[a,b]
            weights[g,u,i]=cost(G,1)+cost(0,P)+cost(P,T)-cost(G,T)
        assert len(weights)==receipt['carriers']
        edges,chosen,_,_=weighted_matcher(weights,'gain-first')(blocks,uses,True)
        selection=[edges[e] for e in sorted(chosen)]
        matching=dict(h=h,source_parent_sha256=parent_digest,frame_family_word_sha256=frame_digest,
                      source_permutation=Q,policy='gain-first',selected=selection,
                      discovery_cost_receipt_sha256=sha256(args.discovery_cost_receipt.read_bytes()).hexdigest(),
                      discovery_matrix_cost_sha256=sha256(cost_bytes).hexdigest())
    selection_path=args.work/'selected-matching.json'
    selection_path.write_text(json.dumps(matching,separators=(',',':'))+'\n')
    # Recheck each chosen carrier from fresh graph coefficients and use lists.
    # The compiler subsequently replays its actual physical role allocation.
    selected_match(blocks,uses,order,selection)
    region.COMPILER.build=lambda dimension:built
    region.COMPILER.match=lambda bs,us,enabled:selected_match(bs,us,order,selection)
    compiled,word=region.COMPILER.compile_(h,matching=True,reclaim=True,dirty=True)
    # Original envelopes are metadata for scalar regions, not an assertion
    # that this new physical word can execute under those smaller frames.
    region_envelopes=[]
    def mask(z):return sum(1<<Q[i] for i in range(h) if z>>i&1)
    for b in blocks:
        old=old_owner[b['nodes'][0]]
        assert all(old_owner[x]==old for x in b['nodes'])
        core,cover=old_blocks[old]['frame']
        region_envelopes.append([mask(core),mask(cover)])
    metadata=dict(h=h,source_parent_sha256=parent_digest,source_permutation=Q,
                  original_scalar_region_envelopes=region_envelopes,
                  preintern_selected_frames=word['frames'],
                  scope='Scalar-region envelope metadata only. These smaller envelopes are not an accepted physical schedule for the changed matching. New closure must contain the actual selected signed spaces.')
    metadata_path=args.work/'original-region-envelope-metadata.json'
    metadata_path.write_text(json.dumps(metadata,separators=(',',':'))+'\n')
    word=joint.canonicalize(word,Q)
    word_path=args.work/'word.json.gz'
    digest=write_word(word_path,word)
    assert digest==args.expected_word_sha256
    independent=check(word_path,args.work/'signed-transitions.bin')
    if args.profile_transitions:
        assert (args.work/'signed-transitions.bin').read_bytes()==args.profile_transitions.read_bytes()
    source_roles=set(word['sources'].values())
    for slot,before,after in word['events']:
        if before<0 and slot in source_roles:
            frame=word['frames'][after]
            assert frame[0]==1 and frame[1].bit_count()==3
    centers=[record for record in word['outputs'] if len(record[3])==1]
    assert len(centers)==h
    assert all(word['frames'][g][0]==h-1 for _,g,_,_ in centers)
    result=dict(status='source-only NEW carrier matching, source/use/capacity/chronology and full actual both-dirty word PASS',
                source_only=True,source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',h=h,R=compiled['roles'],
                scalar=scalar,compiled=compiled,compiled_parent=parent_compiled,
                source_parent_sha256=parent_digest,source_parent_configuration=config,
                source_permutation=Q,configuration=dict(parent=parent,choices=cfg['choices'],basis=cfg['basis'],matching_policy='gain-first'),
                selected_carriers=len(selection),selected_matching_path=str(selection_path),
                selected_matching_sha256=sha256(selection_path.read_bytes()).hexdigest(),
                every_selected_use_reconstructed=True,distinct_recipient_capacity=True,
                donor_row_capacity_exactly_independent=True,strict_carrier_chronology=True,
                source_injection_frames_unchanged=True,copied_center_spaces_unchanged=h,
                original_scalar_dag_outputs_preserved=True,physical_matching_and_literal_xors_changed=True,
                word_regenerated_from_source_and_selected_carriers=True,
                actual_frame_assignment_reconstructed=True,frame_summary=frame_summary,
                word_path=str(word_path),word_sha256=digest,independent=independent,
                profile_transition_sha256=independent['transition_sha256'],
                profile_bytes_independently_compared=bool(args.profile_transitions),
                original_region_metadata_path=str(metadata_path),original_region_metadata_sha256=sha256(metadata_path.read_bytes()).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                limitations='Finite F2 word and rational address inclusions. Matrix CRT, stock, all-source geometry, moments, assembly and all-size address/tape realization remain separately checked conditional interfaces.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=result['status'],h=h,R=compiled['roles'],selected_carriers=len(selection),word_sha256=digest,seconds=result['seconds'])),flush=True)


if __name__=='__main__':
    main()
