#!/usr/bin/env python3
"""Search paid clearing circuits beyond one fundamental elimination relation.

Small connected nullspace components are enumerated exactly. Larger components
receive a bounded search over overlapping pairs. Every chosen relation is
checked on the current exact signal vectors before literal reversible XORs.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
from time import perf_counter


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SETUP = """
 core_index={};cover_index=[0]*h
 for position,g in enumerate(order):
  core,cover=blocks[g]['frame'];bit=1<<position
  core_index[core]=core_index.get(core,0)|bit
  for axis in range(h):
   if cover>>axis&1:cover_index[axis]|=bit
 last_compatible=[];all_regions=(1<<len(order))-1
 for block in blocks:
  core,cover=block['frame'];allowed=0;subset=core
  while subset:
   allowed|=core_index.get(subset,0);subset=(subset-1)&core
  candidates=all_regions
  while cover:
   bit=cover&-cover;candidates&=cover_index[bit.bit_length()-1];cover^=bit
  candidates&=allowed;assert candidates
  last_compatible.append(candidates.bit_length()-1)
 region_place={g:i for i,g in enumerate(order)}
"""

ACQUIRE = """ def acquire(g,anchors):
  if reclaim:
   bb={};relations=[]
   def ins(s):
    row=slots[s];expr=1<<s
    while row:
     pivot=row.bit_length()-1
     if pivot not in bb:bb[pivot]=(row,expr);return None
     old,e=bb[pivot];row^=old;expr^=e
    return expr
   future_frames={}
   for u,s in assign.items():
    _,target,terminal=uses[u]
    if terminal is None and region_place[target]<=step:continue
    future_frames.setdefault(s,set()).add(target)
   available=[]
   for s,targets in future_frames.items():
    if s in retired or s in anchors:continue
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    if not all(contains(blocks[g]['frame'],blocks[target]['frame']) for target in targets):continue
    available.append(s)
   stats['external_anchor_candidates']+=len(available)
   for s in anchors:ins(s)
   for s in sorted(available):ins(s)
   compatible=[s for s in retired if contains(blocks[frames[s]]['frame'],blocks[g]['frame'])]
   for s in sorted(compatible,key=lambda s:(last_compatible[frames[s]],-blocks[frames[s]]['rank'],s)):
    relation=ins(s)
    if relation is not None:
     assert relation>>s&1
     relations.append(relation)
   stats['fundamental_zero_relations']+=len(relations)
   if relations:
    # An edge exists when two fundamental dependencies share a physical role.
    parent=list(range(len(relations)));role_owner={}
    def find(i):
     while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
     return i
    for index,relation in enumerate(relations):
     bits=relation
     while bits:
      bit=bits&-bits;s=bit.bit_length()-1;bits^=bit
      if s in role_owner:
       a=find(index);b=find(role_owner[s]);parent[a]=b
      else:role_owner[s]=index
    components={}
    for index in range(len(relations)):components.setdefault(find(index),[]).append(index)
    best=None;seen=set();fundamental=set(relations)
    def consider(relation):
     nonlocal best
     if not relation or relation in seen:return
     seen.add(relation);roles=[];bits=relation
     while bits:
      bit=bits&-bits;roles.append(bit.bit_length()-1);bits^=bit
     targets=[s for s in roles if s in retired]
     if not targets:return
     s=min(targets,key=lambda s:(last_compatible[frames[s]],-blocks[frames[s]]['rank'],s))
     growth=sum(blocks[g]['rank']-blocks[frames[a]]['rank'] for a in roles)
     count=len(roles)-1;deadline=last_compatible[frames[s]]
     if CYCLE_POLICY=='deadline':score=(deadline,-blocks[frames[s]]['rank'],growth,count,s,relation)
     elif CYCLE_POLICY=='rank-growth':score=(growth,count,deadline,-blocks[frames[s]]['rank'],s,relation)
     else:score=(count,growth,deadline,-blocks[frames[s]]['rank'],s,relation)
     stats['zero_relation_candidates']+=1
     if best is None or score<best[0]:best=(score,s,roles,relation)
    for relation in relations:consider(relation)
    for component in components.values():
     stats['nullspace_components']+=1
     if len(component)<=CYCLE_EXACT_LIMIT:
      stats['exact_nullspace_components']+=1
      # Fundamental relations are linearly independent: each was emitted on a
      # newly inserted retired role. Gray traversal visits their whole span.
      relation=0;previous=0
      for state in range(1,1<<len(component)):
       gray=state^(state>>1);change=gray^previous;previous=gray
       relation^=relations[component[change.bit_length()-1]];consider(relation)
     else:
      stats['bounded_nullspace_components']+=1
      pairs=0
      for offset,index in enumerate(component):
       for other in component[offset+1:]:
        if relations[index]&relations[other]:
         consider(relations[index]^relations[other]);pairs+=1
         if pairs>=CYCLE_PAIR_LIMIT:break
       if pairs>=CYCLE_PAIR_LIMIT:break
    if best is not None:
     score,s,roles,relation=best;value=0
     for a in roles:value^=slots[a]
     assert value==0,'Proposed clearing relation is not an exact nullspace vector'
     assert s in retired and all(contains(blocks[frames[a]]['frame'],blocks[g]['frame']) for a in roles)
     stats['combined_zero_relations_selected']+=int(relation not in fundamental)
     for a in roles:
      if a==s:continue
      if a in available:stats['borrowed_live_anchor_xors']+=1
      xor(s,a,g)
     assert not slots[s]
     retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(roles)-1
     return s
  return new(g)
"""


def prepare_acquire(include_anchor_relations=False):
    source = ACQUIRE
    if include_anchor_relations:
        anchor_lines = '   for s in anchors:ins(s)\n   for s in sorted(available):ins(s)\n'
        replacement = ('   for s in list(dict.fromkeys(anchors))+sorted(available):\n'
                       '    relation=ins(s)\n'
                       '    if relation:relations.append(relation);stats["anchor_zero_relations"]+=1\n')
        assert source.count(anchor_lines) == 1
        source = source.replace(anchor_lines, replacement)
        pair_line = '        if relations[index]&relations[other]:'
        pair_filter = ('        if relations[index]&relations[other] and '
                       '((relations[index]^relations[other])&retired_bits):')
        assert source.count(pair_line) == 1
        source = source.replace(pair_line, pair_filter)
        component_start = '   if relations:\n'
        assert source.count(component_start) == 1
        source = source.replace(component_start, component_start+
            '    retired_bits=0\n    for s in compatible:retired_bits|=1<<s\n')
    return source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execution-copy', required=True)
    parser.add_argument('--intake', required=True)
    parser.add_argument('--h', type=int, choices=[23, 25], required=True)
    parser.add_argument('--policy', choices=['deadline', 'rank-growth', 'short-word'], required=True)
    parser.add_argument('--exact-limit', type=int, default=8)
    parser.add_argument('--pair-limit', type=int, default=256)
    parser.add_argument('--include-anchor-relations', action='store_true')
    parser.add_argument('--schedule', choices=['original', 'rank-pressure'], default='original')
    parser.add_argument('--schedule-helper', type=Path)
    parser.add_argument('--record-cost-queries', action='store_true')
    parser.add_argument('--crt-cpp', type=Path)
    parser.add_argument('--crt-wrapper', type=Path)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    assert 1 <= args.exact_limit <= 10 and 1 <= args.pair_limit <= 4096
    root = Path(args.execution_copy).resolve()
    assert '/work/joint-frame/layout/' in str(root)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=False)
    intake = json.loads(Path(args.intake).read_text())
    original = root/'scripts/experiments/binary_frame_compiler.py'
    raw = original.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == intake['compiler_sha256']
    text = raw.decode()
    start = text.index(' def acquire(g,anchors):')
    end = text.index(' for step,g in enumerate(order):', start)
    acquire_source = prepare_acquire(args.include_anchor_relations)
    if args.record_cost_queries:
        marker = "     growth=sum(blocks[g]['rank']-blocks[frames[a]]['rank'] for a in roles)"
        queries = """     for a in roles:
      old=frames[a]
      if blocks[g]['rank']>blocks[old]['rank']:NATIVE_COST_QUERIES.add((old+2,g+2))
      NATIVE_COST_QUERIES.add((old+2,1))
     NATIVE_COST_QUERIES.add((0,g+2));NATIVE_COST_QUERIES.add((g+2,1))
"""
        assert acquire_source.count(marker) == 1
        acquire_source = acquire_source.replace(marker, queries+marker)
    text = text[:start]+acquire_source+text[end:]
    token = 'build(h);v=len(c.inputs)'
    assert text.count(token) == 1
    text = text.replace(token, token+SETUP)
    if args.record_cost_queries:
        text = text.replace(token, token+";globals()['NATIVE_COST_FRAMES']=[tuple(b['frame'])+(b['rank'],) for b in blocks]")
    if args.schedule != 'original':
        assert args.schedule_helper
        marker = "order=sorted(range(len(blocks)),key=lambda g:(blocks[g]['rank'],min(blocks[g]['nodes'])))"
        assert text.count(marker) == 1
        text = text.replace(marker, 'order=scheduled_order(blocks,uses,owner,SCHEDULE_POLICY)')
    variant = original.with_name('binary_frame_compiler_nullspace.py')
    variant.write_text(text)
    sys.path.insert(0, str(original.parent))
    compiler = load('binary_frame_compiler', variant)
    compiler.CYCLE_POLICY = args.policy
    compiler.CYCLE_EXACT_LIMIT = args.exact_limit
    compiler.CYCLE_PAIR_LIMIT = args.pair_limit
    if args.record_cost_queries:
        compiler.NATIVE_COST_QUERIES = set()
    if args.schedule != 'original':
        helper = load('owned_causal_order', args.schedule_helper)
        compiler.scheduled_order = helper.scheduled_order
        compiler.SCHEDULE_POLICY = args.schedule
    producer = load('joint_dual_compiler', original.parent/'joint_dual_compiler.py')
    started = perf_counter()
    result, word = producer.compile_axis(args.h)
    result.update(policy='guarded-live-'+('complete-kernel-' if args.include_anchor_relations else 'nullspace-')+args.policy,
                  exact_component_limit=args.exact_limit,
                  includes_anchor_zero_relations=args.include_anchor_relations,
                  causal_schedule=args.schedule,
                  overlapping_pair_limit=args.pair_limit,
                  seconds=perf_counter()-started,
                  source_commit=intake['commit'],
                  base_compiler_sha256=intake['compiler_sha256'],
                  variant_compiler_sha256=hashlib.sha256(variant.read_bytes()).hexdigest(),
                  wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  search_scope=('Complete kernel of the explicitly admitted compatible physical-role pool is represented by independent fundamental dependencies. ' if args.include_anchor_relations else 'Only retired-dependency relations are recorded; anchor/live-only zero relations are omitted. ')+
                  'Exact spans within small connected recorded components; bounded overlapping pairs in larger components. All selected physical clearing XORs and frame growth are executed.',
                  limitation='FINITE PASS only. Independent complete-word replay, rational native profiles and assembly required for any exponent claim.')
    packed = (json.dumps(word, separators=(',', ':'))+'\n').encode()
    result['physical_word_sha256'] = hashlib.sha256(packed).hexdigest()
    result['physical_word_bytes'] = len(packed)
    (out/'word.json').write_bytes(packed)
    if args.schedule_helper:
        result['scheduling_helper_sha256'] = hashlib.sha256(args.schedule_helper.read_bytes()).hexdigest()
    if args.record_cost_queries:
        rows = [(0, 0, 0), (0, 0, args.h)]+compiler.NATIVE_COST_FRAMES
        pairs = sorted(compiler.NATIVE_COST_QUERIES)
        assert all(rows[b][2] > rows[a][2] for a, b in pairs)
        mass = sum(rows[b][2]-rows[a][2] for a, b in pairs)
        binary = out/'native-cost-query-input.bin'
        with binary.open('wb') as stream:
            stream.write(struct.pack('<6I2Q', args.h, word['v'], 0, len(rows), len(pairs), 0, mass, mass))
            for row in rows:
                stream.write(struct.pack('<2QI', *row))
            for a, b in pairs:
                stream.write(struct.pack('<2Iq', a, b, 1))
        result['native_cost_query_count'] = len(pairs)
        result['native_cost_query_input_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
        result['query_cost_scope'] = 'Actual considered zero-relation support raises, births and possible cleanup differences. These are local optimization data, not full recurrence deltas. Donor future paths, retained signals and future reclamation still require whole-word acceptance.'
        (out/'finite-result.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(dict(event='FINITE WORD PASS BEFORE QUERY PROFILING', h=args.h, roles=result['roles'], query_pairs=len(pairs), word_sha256=result['physical_word_sha256'])), flush=True)
        if args.crt_cpp or args.crt_wrapper:
            assert args.crt_cpp and args.crt_wrapper
            executable = out/'native-cost-profiler'
            subprocess.run(['c++', '-O3', '-std=c++17', str(args.crt_cpp), '-o', str(executable)], check=True)
            command = [sys.executable, '-B', str(args.crt_wrapper), '--binary', str(executable),
                       '--transitions', str(binary), '--profiles', str(out/'native-cost-profile.json'),
                       '--dump', str(out/'native-cost-queries.jsonl'), '--output', str(out/'native-cost-certificate.json')]
            with (out/'native-cost-profile.log').open('wb') as log:
                subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
            result['native_cost_profiles_status'] = 'TWELVE-PRIME ALL-CORNER PASS'
            result['native_cost_profiles_sha256'] = hashlib.sha256((out/'native-cost-queries.jsonl').read_bytes()).hexdigest()
            result['native_cost_certificate_sha256'] = hashlib.sha256((out/'native-cost-certificate.json').read_bytes()).hexdigest()
            result['query_cpp_sha256'] = hashlib.sha256(args.crt_cpp.read_bytes()).hexdigest()
            result['query_crt_wrapper_sha256'] = hashlib.sha256(args.crt_wrapper.read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ['h', 'policy', 'roles', 'seconds', 'physical_word_sha256']}), flush=True)


if __name__ == '__main__':
    main()
