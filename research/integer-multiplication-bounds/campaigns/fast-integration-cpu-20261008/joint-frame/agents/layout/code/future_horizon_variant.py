#!/usr/bin/env python3
"""Preserve compatible retired carriers with longer future frame reuse horizons.

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
    parser.add_argument('--policy',choices=['last-compatible','remaining-compatible'],required=True)
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
    if args.policy=='last-compatible':
        priority="last_compatible[frames[s]]"
    else:
        priority="(compatible_frames[frames[s]]>>step).bit_count()"
    changed=text.replace(old,"for s in sorted(retired,key=lambda s: ("+priority+",-blocks[frames[s]]['rank'],s)):")
    variant=original.with_name('binary_frame_compiler_horizon.py');variant.write_text(changed)
    sys.path.insert(0,str(original.parent))
    compiler=load('binary_frame_compiler',variant)
    producer=load('joint_dual_compiler',original.parent/'joint_dual_compiler.py')
    started=perf_counter();result,word=producer.compile_axis(args.h)
    result.update(policy=args.policy,seconds=perf_counter()-started,
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
