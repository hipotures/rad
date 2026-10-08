#!/usr/bin/env python3
"""Retirement priority using exact native child-profile moment slope.

Only the ordering of compatible retired roles changes. Every physical XOR,
frame incidence, dirty vector and indexed scalar output remains checked.
Base sources live in a fresh task-owned execution copy, never immutable input.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
import struct
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
    parser.add_argument('--profile-table',required=True)
    parser.add_argument('--frame-input',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();root=Path(args.execution_copy).resolve()
    assert '/work/joint-frame/layout/' in str(root),'Fresh task-owned execution copy required'
    out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
    intake=json.loads(Path(args.intake).read_text())
    original=root/'scripts/experiments/binary_frame_compiler.py'
    raw=original.read_bytes();assert hashlib.sha256(raw).hexdigest()==intake['compiler_sha256']
    text=raw.decode();old='for s in sorted(retired):'
    assert text.count(old)==1
    frame_raw=Path(args.frame_input).read_bytes();header=struct.unpack_from('<6I2Q',frame_raw)
    assert header[0]==args.h
    table_frames=[struct.unpack_from('<2QI',frame_raw,40+20*i) for i in range(header[3])]
    profile_raw=Path(args.profile_table).read_bytes();products={}
    for line in profile_raw.decode().splitlines():
        row=json.loads(line);blocks=row['blocks'];assert len(blocks)==args.h+1
        rank=sum(t*n for t,n in enumerate(blocks));product=1
        for t,n in enumerate(blocks):
            if t:product*=t**(t*n)
        pair=table_frames[row['a']]+table_frames[row['b']]
        products[pair]=(rank,product)
    token='build(h);v=len(c.inputs)';assert text.count(token)==1
    text=text.replace(token,token+';profile_priority_cache={}')
    token=' def acquire(g,anchors):\n  if reclaim:';assert text.count(token)==1
    priority=''' def acquire(g,anchors):
  def priority(s):
   old=frames[s];rank=blocks[g]['rank']-blocks[old]['rank']
   if not contains(blocks[old]['frame'],blocks[g]['frame']):return rank,0,s
   key=old,g
   if key not in profile_priority_cache:
    f=blocks[old];destination=blocks[g]
    pair=tuple(f['frame'])+(f['rank'],)+tuple(destination['frame'])+(destination['rank'],)
    if pair in PROFILE_GRADIENT:
     actual,product=PROFILE_GRADIENT[pair];assert actual==rank
     stats['profile_priority_known_pairs']+=1
    else:
     product=1;stats['profile_priority_unknown_pairs']+=1
    profile_priority_cache[key]=product
   return rank,-profile_priority_cache[key],s
  if reclaim:'''
    text=text.replace(token,priority)
    changed=text.replace(old,'for s in sorted(retired,key=priority):')
    variant=original.with_name('binary_frame_compiler_gradient.py');variant.write_text(changed)
    sys.path.insert(0,str(original.parent))
    compiler=load('binary_frame_compiler',variant)
    compiler.PROFILE_GRADIENT=products
    producer=load('joint_dual_compiler',original.parent/'joint_dual_compiler.py')
    started=perf_counter();result,word=producer.compile_axis(args.h)
    result.update(policy='rank-then-native-profile-gradient',seconds=perf_counter()-started,
        profile_table_sha256=hashlib.sha256(profile_raw).hexdigest(),frame_input_sha256=hashlib.sha256(frame_raw).hexdigest(),profile_pairs=len(products),
        search_scope='Exact rank-first and characteristic derivative tie rule; unknown profiles use the conservative all-singleton derivative. Final complete profile and finite-saving assembly remain required.',
        baseline_PR58_roles={23:30790,25:40446}[args.h],
        source_commit=intake['commit'],base_compiler_sha256=intake['compiler_sha256'],
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
