#!/usr/bin/env python3
"""Create paid pair-star producers shared by different common-point circuits.

This changes the scalar DAG outside PR62's one-strip and nine-piece models.
A new positive sum is inserted into incomparable source-support regions
across two common-point circuits;
every residual sum, binary producer and physical role remains paid. Actual
original envelopes ensure monotone containment without downward retirement.
Baseline scalar construction: Avi Eisenberg PR62. Physical joint compiler,
matching and dirty reclamation: eumemic PR57. Apache-2.0; AI-assisted research.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import time

import joint_signed_word_recompile as joint
import joint_region_search_v3 as region
from joint_source_partition_relocation import ReconstructedCircuit
from joint_word_check_v4 import check


def transform(c, ordinary, old_owner, length, budget, tree, recipient_cap):
    signal={}
    by_common=defaultdict(list)
    lookup={}
    for x in sorted(c.active):
        signal[x]=signal[c.args[x][0]]|signal[c.args[x][1]] if c.args[x] else 1<<(x-1)
        lookup.setdefault(signal[x],x)
        if c.args[x] and c.core[x].bit_count()==1:
            by_common[c.core[x].bit_length()-1].append(x)
    for values in by_common.values():
        values.sort(key=lambda x:(signal[x].bit_count(),x))
    pair_sources=defaultdict(dict)
    for i,t in enumerate(c.inputs,1):
        for a,b in combinations(t,2):
            other=next(j for j in t if j not in (a,b))
            pair_sources[a,b][other]=i
    candidates=[]
    counters=Counter()
    for (a,b),values in sorted(pair_sources.items()):
        points=sorted(values)
        k=min(length,len(points))
        seen=set()
        for start in range(0,len(points),max(1,k//2)):
            chosen=tuple(points[(start+j)%len(points)] for j in range(k))
            form=sum(1<<(values[j]-1) for j in chosen)
            if form in seen:
                continue
            seen.add(form);counters['distinct_pair_star_proposals']+=1
            if form in lookup:
                counters['already_existing_exact_form']+=1
                continue
            recipients=[]
            reached=[]
            for common in (a,b):
                found=[]
                for x in by_common[common]:
                    S=signal[x]
                    if form&~S:
                        continue
                    left,right=c.args[x]
                    if not (form&signal[left] and form&signal[right]):
                        continue
                    if S==form:
                        continue
                    if any(not signal[y]&~S for y in found):
                        continue
                    found.append(x)
                    if len(found)>=recipient_cap:
                        break
                if found:
                    reached.append(common)
                    recipients.extend((common,x) for x in found)
            if len(reached)==2:
                counters['new_form_legal_in_two_common_partitions']+=1
                candidates.append((-len(recipients),sum(signal[x].bit_count() for _,x in recipients)/len(recipients),a,b,chosen,form,recipients))
            else:
                counters['no_two_cross_partition_recipients']+=1
    candidates.sort()
    parent=SimpleNamespace(inputs=c.inputs,outputs=c.outputs,args=list(c.args),
                           core=list(c.core),union=list(c.union))
    args=parent.args
    owner=dict(old_owner)
    labels=list(ordinary)
    label_lookup={frame:i for i,frame in enumerate(labels)}
    records=[]
    def frame_for(core,cover):
        if core==cover:
            return 1,core,tuple(int(core>>i&1) for i in range(c.h))
        return cover.bit_count()-core.bit_count(),core,tuple(1 if core>>i&1 else i+2 if cover>>i&1 else 0 for i in range(c.h))
    def add(left,right):
        assert signal[left]&signal[right]==0
        form=signal[left]|signal[right]
        if form in lookup:
            return lookup[form]
        x=len(args)
        args.append((left,right))
        parent.core.append(parent.core[left]&parent.core[right])
        parent.union.append(parent.union[left]|parent.union[right])
        signal[x]=form
        frame=frame_for(parent.core[x],parent.union[x])
        assert frame[1].bit_count() in (1,2)
        if frame not in label_lookup:
            label_lookup[frame]=len(labels);labels.append(frame)
        owner[x]=label_lookup[frame]
        lookup[form]=x
        return x
    def sum_nodes(nodes):
        assert nodes
        if tree=='balanced':
            while len(nodes)>1:
                nodes=[add(nodes[j],nodes[j+1]) if j+1<len(nodes) else nodes[j] for j in range(0,len(nodes),2)]
            return nodes[0]
        total=nodes[0]
        for x in nodes[1:]:
            total=add(total,x)
        return total
    def remainder(form,common):
        if form in lookup:
            return lookup[form]
        remaining=form;pieces=[]
        choices=sorted((x for x in c.active if c.core[x]>>common&1),
                       key=lambda x:(-signal[x].bit_count(),x))
        for x in choices:
            S=signal[x]
            if S and not S&~remaining:
                pieces.append(x);remaining^=S
                if not remaining:
                    break
        assert not remaining
        return sum_nodes(pieces)
    changed=set()
    for _,_,a,b,points,form,recipients in candidates:
        if any(x in changed for _,x in recipients):
            counters['recipient_already_repartitioned']+=1
            continue
        before=len(args)
        producer=sum_nodes([pair_sources[a,b][j] for j in points])
        assert signal[producer]==form
        replacements=[]
        for common,x in recipients:
            residual=remainder(signal[x]^form,common)
            assert not signal[producer]&signal[residual]
            assert (signal[producer]|signal[residual])==signal[x]
            old=args[x]
            args[x]=(producer,residual)
            changed.add(x)
            replacements.append(dict(common=common,value=x,old_args=old,new_args=args[x],
                                     source_count=signal[x].bit_count()))
        records.append(dict(pair=[a,b],other_points=points,producer=producer,
                            paid_new_binary_gates=len(args)-before,replacements=replacements))
        if len(records)>=budget:
            break
    fresh=ReconstructedCircuit(parent,args,owner,signal)
    scalar=fresh.verify()
    return fresh,labels,records,dict(counters),scalar


def evaluate(document, length, budget, tree, recipient_cap, work):
    started=time.monotonic()
    case=f"{document['id']}-new-pair{length}-{tree}-budget{budget}-antichain{recipient_cap}"
    target=work/'raw'/case
    target.mkdir(parents=True,exist_ok=False)
    c,old_blocks,old_owner,_,ordinary,*_=joint.prepare(document)
    fresh,labels,records,counters,scalar=transform(c,ordinary,old_owner,length,budget,tree,recipient_cap)
    saved=region.COMPILER.build
    try:
        region.COMPILER.build=lambda h:joint.build(fresh,labels,fresh.owner,'preserve-regions','original')
        compiled,word=region.COMPILER.compile_(document['h'],matching=True,reclaim=True,dirty=True)
    finally:
        region.COMPILER.build=saved
    word=joint.canonicalize(word,document.get('Q',list(range(document['h']))))
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    path=target/'word.json.gz'
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as archive:
            archive.write(raw)
    independent=check(path,target/'signed-transitions.bin')
    result=dict(status='DISCOVERY new cross-common paid pair producers exact scalar/monotone frames/both dirty PASS',
                case_id=case,configuration=dict(parent=document,length=length,budget=budget,tree=tree,recipient_cap=recipient_cap),
                original_active_nodes=len(c.active),changed_active_nodes=len(fresh.active),
                net_scalar_gate_change=fresh.additions-c.additions,new_pair_producers=records,
                counters=counters,scalar=scalar,compiled=compiled,independent=independent,
                word_path=str(path),word_sha256=sha256(raw).hexdigest(),
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                seconds=time.monotonic()-started,completed_utc=datetime.now(timezone.utc).isoformat(),
                limitations='Every added producer/residual is paid. Full actual CRT moments, source geometry, stock and all conditional transfer gates remain separate. No cardinality or exponent claim follows from new sharing alone.')
    (target/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(case=case,new_producers=len(records),net_scalar_gates=result['net_scalar_gate_change'],
                         R=compiled['roles'],seconds=result['seconds'],counters=counters)),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--parents',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--h',type=int,nargs='+',default=[23,25])
    p.add_argument('--lengths',type=int,nargs='+',default=[4,8])
    p.add_argument('--budget',type=int,default=4)
    p.add_argument('--recipient-cap',type=int,default=4)
    p.add_argument('--tree',choices=['balanced','chain'],default='balanced')
    args=p.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    joint.initialize(args.source,args.work)
    parents=[d for d in json.loads(args.parents.read_text()) if d['h'] in args.h]
    assert len(parents)==len(args.h)
    result=dict(status='running',command=sys.argv,rows=[])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for document in parents:
        for length in args.lengths:
            result['rows'].append(evaluate(document,length,args.budget,args.tree,args.recipient_cap,args.work))
            args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
