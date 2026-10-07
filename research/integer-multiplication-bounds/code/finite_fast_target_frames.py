#!/usr/bin/env python3
"""Equivalent fast constraint checks for descendant/selected target frames.

The original finite_target_frames predicate checks every basis column.
This version compares symbolic coordinate coefficient vectors at once.
The compiler/maxflow algorithm and all verification obligations are unedited.
Dense target graphs also stop once every incident vertex is forced to zero.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import argparse
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import random
import sys
from unittest.mock import patch

import finite_target_frames as original


ZERO=(0,)


def negated(key):
    if key[0]==0:return key
    if key[0]==1:return (1,key[1],-key[2])
    return (2,tuple(-value for value in key[1]))


@lru_cache(maxsize=500000)
def describe(frame):
    k=frame.core.bit_count()
    if k==3:
        assert not frame.components
        zkey=(1,0,1)
        keys=[ZERO]*frame.h
    else:
        scale=3-k
        d=[positive.bit_count()-negative.bit_count() for positive,negative in frame.components]
        nonzero=[index for index,value in enumerate(d) if value]
        if not nonzero:zkey=ZERO
        elif len(nonzero)==1:zkey=(1,nonzero[0],d[nonzero[0]])
        else:zkey=(2,tuple(d))
        keys=[ZERO]*frame.h
        for index,(positive,negative) in enumerate(frame.components):
            poskey=(1,index,scale)
            negkey=(1,index,-scale)
            for vertex in original.bits(positive):keys[vertex]=poskey
            for vertex in original.bits(negative):keys[vertex]=negkey
    for vertex in original.bits(frame.core):keys[vertex]=zkey
    masks={}
    for vertex,key in enumerate(keys):masks[key]=masks.get(key,0)|(1<<vertex)
    support=((1<<frame.h)-1)&~masks.get(ZERO,0)
    return tuple(keys),masks,zkey,support


@lru_cache(maxsize=500000)
def included(a,b):
    assert a.h==b.h
    keys,masks,zkey,support=describe(a)
    _,_,_,other_support=describe(b)
    if support&~other_support:return False
    if b.core&~masks.get(zkey,0):return False
    for positive,negative in b.components:
        vertex=(positive&-positive).bit_length()-1
        key=keys[vertex]
        if positive&~masks.get(key,0):return False
        if negative&~masks.get(negated(key),0):return False
    return True


@lru_cache(maxsize=16)
def incident_table(pairs):
    result=[]
    for offset in range(0,len(pairs),8):
        row=[0]*256
        for mask in range(1,256):
            bit=mask&-mask
            index=bit.bit_length()-1
            if offset+index<len(pairs):
                a,b=pairs[offset+index]
                row[mask]=row[mask^bit]|(1<<a)|(1<<b)
        result.append(row)
    return result


def signed_frame(h,core,edges,pairs):
    outside=((1<<h)-1)&~core
    parent=list(range(h))
    parity=[0]*h
    odd=[False]*h
    vertices=[1<<vertex for vertex in range(h)]
    table=incident_table(tuple(pairs))
    incident=0
    for index,byte in enumerate(edges.to_bytes((edges.bit_length()+7)//8,"little")):
        incident|=table[index][byte]
    assert not incident&core
    forced=0

    def find(v):
        if parent[v]!=v:
            previous=parent[v]
            parent[v],sign=find(previous)
            parity[v]^=sign
        return parent[v],parity[v]

    for index in original.bits(edges):
        a,b=pairs[index]
        ra,pa=find(a)
        rb,pb=find(b)
        if ra==rb:
            if pa^pb!=1:odd[ra]=True
        else:
            parent[rb]=ra
            parity[rb]=pa^pb^1
            odd[ra]=odd[ra] or odd[rb]
            vertices[ra]|=vertices[rb]
        if odd[ra]:forced|=vertices[ra]
        if forced&incident==incident:break
    groups={}
    for vertex in original.bits(outside):
        root,sign=find(vertex)
        if odd[root]:continue
        if root not in groups:groups[root]=[0,0,sign]
        groups[root][sign^groups[root][2]]|=1<<vertex
    components=tuple(sorted(((positive,negative) for positive,negative,_ in groups.values()),
                            key=lambda component:(component[0]&-component[0]).bit_length()))
    if core.bit_count()==3:assert not components
    return original.TargetSpace(h,core,components)


def equivalence_main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--reference",required=True)
    parser.add_argument("--seed",type=int,default=109)
    parser.add_argument("--samples",type=int,default=10000)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    from finite_block_search import GroupUnion,install_reference,make_block_class
    install_reference(args.reference)
    rng=random.Random(args.seed)
    checked=0
    for h in (6,8,12,50):
        pairs=list(combinations(range(h),2))
        for k in (1,2):
            core=sum(1<<v for v in range(k))
            outside=[i for i,pair in enumerate(pairs) if not any(core&(1<<v) for v in pair)]
            for probability in (0,0.01,0.1,0.5,0.9,1):
                for repeat in range(10):
                    edges=sum(1<<i for i in outside if rng.random()<probability)
                    assert original.signed_frame(h,core,edges,pairs)==signed_frame(h,core,edges,pairs)
                    checked+=1
    cls=make_block_class()
    circuit=GroupUnion(8,lambda n:cls(n,(2,),4,0),"paired")
    frames,_=original.labels(circuit)
    unique=list(set(frames.values()))
    for repeat in range(args.samples):
        a,b=rng.choice(unique),rng.choice(unique)
        assert original.included(a,b)==included(a,b)
    result={"completed_utc":datetime.now(timezone.utc).isoformat(),"settings":vars(args),
            "signed_component_equivalence_checks":checked,"symbolic_inclusion_equivalence_checks":args.samples,
            "h_for_inclusion":8,"component_ground_sizes":[6,8,12,50],
            "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in ("finite_fast_target_frames.py","finite_target_frames.py")}}
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result))


def main():
    if len(sys.argv)>1 and sys.argv[1]=="equivalence":
        sys.argv.pop(1)
        equivalence_main()
        return
    parser_mode="maximal"
    if len(sys.argv)>1 and sys.argv[1] in ("maximal","selected"):
        parser_mode=sys.argv.pop(1)
    if parser_mode=="selected":
        import finite_selected_target_frames as selected
        with patch.object(original,"included",included),patch.object(selected,"included",included):
            selected.main()
    else:
        with patch.object(original,"included",included),patch.object(original,"signed_frame",signed_frame):
            original.main()
    output=Path(sys.argv[sys.argv.index("--output")+1])
    result=json.loads(output.read_text())
    result["source_sha256"][Path(__file__).name]=sha256(Path(__file__).read_bytes()).hexdigest()
    result["equivalent_constraint_implementation"]={"family":parser_mode,"coordinate_inclusion":"simultaneous exact integer coefficient comparison","signed_components":"early stop only after every incident vertex is in an odd component"}
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":
    main()
