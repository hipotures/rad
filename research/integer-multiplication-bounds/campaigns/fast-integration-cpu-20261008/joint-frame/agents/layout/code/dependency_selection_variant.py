#!/usr/bin/env python3
"""Choose a clearing relation after inspecting every compatible retired carrier.

Only the ordering of compatible retired roles changes. Every physical XOR,
frame incidence, dirty vector and indexed scalar output remains checked.
Base sources live in a fresh task-owned execution copy, never immutable input.
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


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--execution-copy',required=True)
    parser.add_argument('--intake',required=True)
    parser.add_argument('--h',type=int,choices=[23,25],required=True)
    parser.add_argument('--policy',choices=['min-rank-growth','min-clearing-xors'],required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();root=Path(args.execution_copy).resolve()
    assert '/work/joint-frame/layout/' in str(root),'Fresh task-owned execution copy required'
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    intake=json.loads(Path(args.intake).read_text())
    original=root/'scripts/experiments/binary_frame_compiler.py'
    raw=original.read_bytes();assert hashlib.sha256(raw).hexdigest()==intake['compiler_sha256']
    text=raw.decode();old='for s in sorted(retired):'
    assert text.count(old)==1
    token='build(h);v=len(c.inputs)';assert text.count(token)==1
    setup='''
 core_index={};cover_index=[0]*h
 for position,g in enumerate(order):
  core,cover=blocks[g]['frame'];bit=1<<position
  core_index[core]=core_index.get(core,0)|bit
  for axis in range(h):
   if cover>>axis&1:cover_index[axis]|=bit
 compatible_frames=[];last_compatible=[];all_regions=(1<<len(order))-1
 for b in blocks:
  core,cover=b['frame'];allowed=0;subset=core
  while subset:
   allowed|=core_index.get(subset,0);subset=(subset-1)&core
  candidates=all_regions
  while cover:
   bit=cover&-cover;candidates&=cover_index[bit.bit_length()-1];cover^=bit
  candidates&=allowed;assert candidates
  compatible_frames.append(candidates);last_compatible.append(candidates.bit_length()-1)
'''
    text=text.replace(token,token+setup)
    priority="(last_compatible[frames[s]],-blocks[frames[s]]['rank'],s)"
    old_body="""   for s in sorted(retired):
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    e=ins(s)
    if e is None:continue
    assert e>>s&1;e^=1<<s;aa=[]
    while e:
     bit=e&-e;aa.append(bit.bit_length()-1);e^=bit
    for a in aa:xor(s,a,g)
    assert not slots[s];retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa);return s
"""
    assert text.count(old_body)==1
    if args.policy=='min-rank-growth':
        score="growth,len(aa),last_compatible[frames[s]],-blocks[frames[s]]['rank'],s"
    else:
        score="len(aa),growth,last_compatible[frames[s]],-blocks[frames[s]]['rank'],s"
    new_body="""   candidates=[]
   for s in sorted(retired,key=lambda s: "+priority+" ):
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    e=ins(s)
    if e is None:continue
    assert e>>s&1;e^=1<<s;aa=[]
    while e:
     bit=e&-e;aa.append(bit.bit_length()-1);e^=bit
    growth=blocks[g]['rank']-blocks[frames[s]]['rank']
    growth+=sum(blocks[g]['rank']-blocks[frames[a]]['rank'] for a in aa)
    stats['clearing_candidate_relations']+=1
    candidates.append((("+score+"),s,aa))
   if candidates:
    score,s,aa=min(candidates)
    for a in aa:xor(s,a,g)
    assert not slots[s];retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa)
    stats['selected_clearing_rank_growth']+=score[0] if CLEARING_POLICY=='min-rank-growth' else score[1]
    return s
"""
    new_body=new_body.replace('"+priority+"',priority).replace('"+score+"',score)
    assert '"+priority+"' not in new_body and '"+score+"' not in new_body
    changed=text.replace(old_body,new_body)
    variant=original.with_name('binary_frame_compiler_horizon.py');variant.write_text(changed)
    sys.path.insert(0,str(original.parent))
    compiler=load('binary_frame_compiler',variant)
    compiler.CLEARING_POLICY=args.policy
    producer=load('joint_dual_compiler',original.parent/'joint_dual_compiler.py')
    started=perf_counter();result,word=producer.compile_axis(args.h)
    result.update(policy='complete-basis-'+args.policy,seconds=perf_counter()-started,
        baseline_PR58_roles={23:30790,25:40446}[args.h],
        source_commit=intake['commit'],base_compiler_sha256=intake['compiler_sha256'],
        search_scope='All first-elimination dependent relations are inspected, not all linear circuits. Every selected clearing XOR and frame growth is executed and checked.',
        variant_compiler_sha256=hashlib.sha256(variant.read_bytes()).hexdigest(),
        wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limitation='Changed exact finite compiler only; independent word replay, fixed-I+J profiles and full conditional assembly remain required.')
    packed=(json.dumps(word,separators=(',',':'))+'\n').encode()
    result['physical_word_sha256']=hashlib.sha256(packed).hexdigest()
    result['physical_word_bytes']=len(packed)
    (out/'word.json').write_bytes(packed)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['h','policy','roles','baseline_PR58_roles','seconds','physical_word_sha256']}),flush=True)


if __name__=='__main__':main()
