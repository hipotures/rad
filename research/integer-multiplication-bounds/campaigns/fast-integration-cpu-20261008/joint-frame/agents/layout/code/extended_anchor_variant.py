#!/usr/bin/env python3
"""Borrow compatible future-live carriers to clear retired components.

PR58/57 original-envelope compiler and PR55 scalar graph retain their notices.
The new rule is F_current <= G_now <= every remaining use frame H. Borrowed
signals are unchanged; every actual raise/XOR is charged in the physical word.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from time import perf_counter


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module);return module


def small_graph(producer,h):
    """Same attributed dual-strip family at a bounded validation dimension."""
    local=producer.circuit_class(h)(h-1)
    total=local.pair(list(range(h-1)))[0];local.outputs[()]=total;stack=[total]
    while stack:
        node=stack.pop()
        if not node or node in local.active:continue
        local.active.add(node)
        if local.args[node]:stack.extend(local.args[node])
    local.additions=sum(local.args[node] is not None for node in local.active)
    return producer.SharedPointCircuit(h,local,point_order=producer.alternating_points)


def main():
    parser=argparse.ArgumentParser()
    for key in ['execution-copy','intake','output']:parser.add_argument('--'+key,required=True)
    parser.add_argument('--h',type=int,required=True)
    args=parser.parse_args();root=Path(args.execution_copy).resolve()
    assert '/work/joint-frame/layout/' in str(root)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    intake=json.loads(Path(args.intake).read_text());original=root/'scripts/experiments/binary_frame_compiler.py'
    raw=original.read_bytes();assert hashlib.sha256(raw).hexdigest()==intake['compiler_sha256']
    text=raw.decode();token='build(h);v=len(c.inputs)';assert text.count(token)==1
    text=text.replace(token,token+';place={g:i for i,g in enumerate(order)}')
    token='   for s in anchors:ins(s)';assert text.count(token)==1
    replacement='''   future_frames={}
   for u,s in assign.items():
    _,target,terminal=uses[u]
    if terminal is None and place[target]<=step:continue
    future_frames.setdefault(s,set()).add(target)
   available=[]
   for s,targets in future_frames.items():
    if s in retired or s in anchors:continue
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    if not all(contains(blocks[g]['frame'],blocks[target]['frame']) for target in targets):continue
    available.append(s)
   stats['external_anchor_candidates']+=len(available)
   for s in anchors:ins(s)
   for s in sorted(available):ins(s)'''
    text=text.replace(token,replacement)
    token='    for a in aa:xor(s,a,g)';assert text.count(token)==1
    text=text.replace(token,"    for a in aa:\n     if a in available:stats['borrowed_live_anchor_xors']+=1\n     xor(s,a,g)")
    token='baseline_pr48_roles={23:36432,25:48329}[h]';assert text.count(token)==1
    text=text.replace(token,'baseline_pr48_roles={23:36432,25:48329}.get(h)')
    variant=original.with_name('binary_frame_compiler_extended.py');variant.write_text(text)
    sys.path.insert(0,str(original.parent));compiler=load('binary_frame_compiler',variant)
    joint=load('joint_dual_compiler',original.parent/'joint_dual_compiler.py')
    started=perf_counter()
    if args.h in (23,25):result,word=joint.compile_axis(args.h)
    else:
        assert 4<=args.h<=13
        compiler.graph=lambda h:small_graph(joint.producer,h)
        result,word=compiler.compile_(args.h,matching=True,reclaim=True,dirty=True)
        result['scalar']=compiler.graph(args.h).verify()
    result.update(policy='compatible-future-live-anchor-borrowing',seconds=perf_counter()-started,
        baseline_PR58_roles={23:30790,25:40446}.get(args.h),source_commit=intake['commit'],
        base_compiler_sha256=intake['compiler_sha256'],variant_compiler_sha256=hashlib.sha256(variant.read_bytes()).hexdigest(),
        wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limitation='New exact finite word. Every borrowed carrier raise is included; independent replay and complete fixed-basis profile/assembly checks still required.')
    packed=(json.dumps(word,separators=(',',':'))+'\n').encode()
    result['physical_word_sha256']=hashlib.sha256(packed).hexdigest();result['physical_word_bytes']=len(packed)
    (out/'word.json').write_bytes(packed);(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['h','policy','roles','baseline_PR58_roles','seconds','physical_word_sha256']}),flush=True)


if __name__=='__main__':main()
