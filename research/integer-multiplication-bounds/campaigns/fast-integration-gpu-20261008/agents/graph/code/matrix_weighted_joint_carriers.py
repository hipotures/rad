#!/usr/bin/env python3
"""Compile physical words using exact actual-frame matrix costs as guidance.

Scalar graph: Avi Eisenberg PR62. Binary word synthesis, matroid matching
and paid reclamation: eumemic PR57. Actual signed frames and rational bases
are campaign extensions. Floating costs guide discovery only; every output
has an independent literal F2 word replay and freshly certified CRT profiles.
No optimality of the weighted allocation is claimed.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import inspect
import json
from pathlib import Path
import struct
import sys
import time

import joint_signed_word_recompile as joint
import joint_region_search_v3 as region
from joint_word_check_v4 import check


def labels_from_receipt(receipt, document, old_blocks):
    assert receipt['source_only'] and receipt['h']==document['h']
    assert receipt['source_parent_sha256']==document['word_sha256']
    assert receipt['source_permutation']==document['Q']
    raw=gzip.decompress(Path(receipt['word_path']).read_bytes())
    assert sha256(raw).hexdigest()==receipt['word_sha256']
    word=json.loads(raw)
    aliases=word['physical_region_address_aliases']
    assert len(aliases)==len(old_blocks)
    Q=document['Q']
    def inverse_frame(frame):
        rank,forced,symbols=frame
        return rank,sum(1<<i for i in range(len(Q)) if forced>>Q[i]&1),tuple(symbols[Q[i]] for i in range(len(Q)))
    return [inverse_frame(word['frames'][i]) for i in aliases]


def weighted_matcher(weights, policy):
    # Change the exploration order of PR57's independently valid matroid
    # algorithm, retaining all its capacity/linear independence checks.
    text=inspect.getsource(region.COMPILER.match)
    text=text.replace('def match(blocks,uses,enabled):','def weighted_match(blocks,uses,enabled):')
    original='for e,(g,u,i)in enumerate(edges):\n  if u not in right and can(e):'
    replacement='for e in exploration_order(edges):\n  g,u,i=edges[e]\n  if u not in right and can(e):'
    assert original in text
    text=text.replace(original,replacement,1)
    if policy=='positive-only':
        text=text.replace('while True:\n  prev={};queue=deque()', 'while False:\n  prev={};queue=deque()',1)
    namespace=dict(region.COMPILER.__dict__)
    def exploration_order(edges):
        def score(e):
            g,u,i=edges[e]
            gain=weights[g,u,i]
            return (-gain,e) if policy!='least-gain-first' else (gain,e)
        ordered=sorted(range(len(edges)),key=score)
        return [e for e in ordered if weights[edges[e]]>0] if policy=='positive-only' else ordered
    namespace['exploration_order']=exploration_order
    exec(compile(text,'<matrix-weighted-joint-match>','exec'),namespace)
    return namespace['weighted_match']


def evaluate(args, document, cost_receipt, policy):
    started=time.monotonic()
    h=document['h']
    target=args.work/'raw'/f'h{h}-{policy}'
    target.mkdir(parents=True,exist_ok=False)
    frame_receipt=json.loads(Path(cost_receipt['frame_receipt']).read_text())
    assert sha256(Path(cost_receipt['frame_receipt']).read_bytes()).hexdigest()==cost_receipt['frame_receipt_sha256']
    assert cost_receipt['source_word_sha256']==frame_receipt['word_sha256']
    c,old_blocks,old_owner,*_=joint.prepare(document)
    labels=labels_from_receipt(frame_receipt,document,old_blocks)
    built=joint.build(c,labels,old_owner,'preserve-regions','original')
    _,blocks,uses,_,owner,_,_,_=built
    probe=Path(cost_receipt['probe_path']).read_bytes()
    assert sha256(probe).hexdigest()==cost_receipt['probe_sha256']
    ph,pv,pR,nf,nt,ps,pmass,ploss=struct.unpack_from('<6I2Q',probe)
    assert (ph,pv,pR,ps,ploss)==(h,len(c.inputs),0,0,0)
    table=json.loads(Path(cost_receipt['matrix_cost_path']).read_text())
    assert table['basis']==args.basis
    costs={(r['a'],r['b']):r['screen_moment'] for r in table['rows']}
    assert len(costs)==nt
    packed=Path(cost_receipt['carrier_path']).read_bytes()
    assert sha256(packed).hexdigest()==cost_receipt['carrier_sha256']
    assert len(packed)%28==0
    weights={}
    for g,u,i,value,G,T,P in struct.iter_unpack('<7I',packed):
        assert (u,i) in blocks[g]['candidates']
        assert uses[u][0]==value and owner[value]>=0
        def cost(a,b):
            return 0.0 if a==b else costs[a,b]
        # A guidance surrogate only. Paid reclamation and every actual final
        # allocation are measured from the subsequently executed word.
        gain=cost(G,1)+cost(0,P)+cost(P,T)-cost(G,T)
        assert (g,u,i) not in weights
        weights[g,u,i]=gain
    assert len(weights)==cost_receipt['carriers']
    saved_build,saved_match=region.COMPILER.build,region.COMPILER.match
    try:
        region.COMPILER.build=lambda dimension:built
        region.COMPILER.match=weighted_matcher(weights,policy)
        compiled,word=region.COMPILER.compile_(h,matching=True,reclaim=True,dirty=True)
    finally:
        region.COMPILER.build,region.COMPILER.match=saved_build,saved_match
    word=joint.canonicalize(word,document['Q'])
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    path=target/'word.json.gz'
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as archive:
            archive.write(raw)
    independent=check(path,target/'signed-transitions.bin')
    result=dict(status='DISCOVERY weighted actual-frame carrier word exact both-dirty PASS',
                case_id=f'h{h}-{policy}',configuration=dict(h=h,policy=policy,basis=args.basis,parent=document),
                parent_frame_word_sha256=frame_receipt['word_sha256'],
                cost_receipt=str(args.cost_receipt),cost_receipt_sha256=sha256(args.cost_receipt.read_bytes()).hexdigest(),
                matrix_cost_surrogate=dict(positive_edges=sum(v>0 for v in weights.values()),
                                           negative_edges=sum(v<0 for v in weights.values()),
                                           zero_edges=sum(v==0 for v in weights.values())),
                compiled=compiled,independent=independent,word_path=str(path),word_sha256=sha256(raw).hexdigest(),
                seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                limitations='Exact costs guide discovery; no weighted optimum or exponent claim. Native full profiles, scalar stock and conditional address transfer remain separate acceptance gates.')
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case_id=result['case_id'],R=compiled['roles'],seconds=result['seconds'],
                         transition_path=independent['transition_path'])),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--parents',type=Path,required=True)
    p.add_argument('--cost-receipt',type=Path,required=True)
    p.add_argument('--h',type=int,required=True)
    p.add_argument('--basis',required=True)
    p.add_argument('--policies',nargs='+',choices=['gain-first','least-gain-first','positive-only'],default=['gain-first','positive-only'])
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    joint.initialize(args.source,args.work)
    documents=[d for d in json.loads(args.parents.read_text()) if d['h']==args.h]
    assert len(documents)==1
    receipt=json.loads(args.cost_receipt.read_text())
    assert receipt['basis']==args.basis and receipt['h']==args.h
    result=dict(status='running',command=sys.argv,rows=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for policy in args.policies:
        result['rows'].append(evaluate(args,documents[0],receipt,policy))
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
