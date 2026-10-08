#!/usr/bin/env python3
"""Source-span coframes on one fixed, independently source-verified XOR word.

All source, two-core and copied-center spaces are protected. Every new space
is a SUBSPACE of the old actual frame, and every literal continuation remains
nested. A safe signed fallback is used where an incidence coframe cannot
contain the incoming address space. No terminal shrink is inserted for free.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
from functools import lru_cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
import math
from pathlib import Path
import subprocess
import sys
import time

GRAPH = Path(__file__).resolve().parents[2]/'graph'/'code'
sys.path.insert(0,str(GRAPH))
from co_signed_source_frames import TAG, FORMAT, normalize, edge_span, contained
from joint_word_check_v5 import check


@lru_cache(maxsize=300000)
def coframe(h,common,edges):
    if edges:
        return edge_span(h,common,edges)
    return 0,1 << common,TAG,tuple(1 if i==common else i+2 for i in range(h))


def select_fixed_word_coframes(word,policy='cap-if-needed'):
    assert policy in ('cap-if-needed','direct-only')
    assert word['frame_format']=='positive-signed-v1'
    h = word['h']
    old = [normalize(frame) for frame in word['frames']]
    pairs = list(combinations(range(h),2))
    pair_index = {pair:i for i,pair in enumerate(pairs)}
    def edge(a,b):
        return 1 << pair_index[tuple(sorted((a,b)))]
    successors = [set() for _ in old]
    for slot,a,b in word['events']:
        if a>=0 and a!=b:
            assert contained(old[a],old[b]) and old[a][0]<old[b][0]
            successors[a].add(b)
    protected = {i for i,frame in enumerate(old) if frame[1].bit_count()!=1}
    protected.update(frame for slot,frame,common,target in word['outputs'] if len(target)==1)
    caps = [0]*len(old)
    for i,frame in enumerate(old):
        if frame[1].bit_count()!=1:
            continue
        common = frame[1].bit_length()-1
        groups = {}
        for j,label in enumerate(frame[2]):
            if abs(label)>1:
                groups.setdefault(abs(label),[]).append(j)
        singletons = [indices[0] for indices in groups.values() if len(indices)==1]
        caps[i] = sum(edge(a,b) for a,b in combinations(singletons,2))
        for indices in groups.values():
            if len(indices)==2 and frame[2][indices[0]]==frame[2][indices[1]]:
                caps[i] |= edge(*indices)
        if caps[i]:
            assert contained(coframe(h,common,caps[i]),frame)
    active = [0]*len(old)
    fallback = set(protected)
    reasons = {'protected':len(protected),'no-safe-incidence-enclosure':0,
               'unseeded-address-region':0,'strict-positive-transition':0}
    def selected(i):
        return old[i] if i in fallback else coframe(h,old[i][1].bit_length()-1,active[i])
    def translate(edges,source_common,target_common):
        if source_common==target_common:
            return edges
        translated = 0
        while edges:
            bit = edges & -edges
            edges -= bit
            a,b = pairs[bit.bit_length()-1]
            triple = {source_common,a,b}
            assert target_common in triple
            a,b = sorted(triple-{target_common})
            translated |= edge(a,b)
        return translated
    queue = deque(range(len(old)))
    queued = set(queue)
    changed = 0
    def enqueue(i):
        if i not in queued:
            queue.append(i)
            queued.add(i)
    def restore(i,reason):
        nonlocal changed
        if i not in fallback:
            fallback.add(i)
            reasons[reason] += 1
            changed += 1
            enqueue(i)
    def drain():
        nonlocal changed
        while queue:
            a = queue.popleft()
            queued.remove(a)
            for b in successors[a]:
                if b in fallback:
                    assert contained(selected(a),old[b])
                    continue
                common = old[b][1].bit_length()-1
                source = selected(a)
                proposed = 0
                if len(source)==4:
                    proposed = translate(active[a],source[1].bit_length()-1,common)
                elif source[1].bit_count()==3:
                    triple = [i for i in range(h) if source[1] >> i & 1]
                    assert common in triple
                    proposed = edge(*(i for i in triple if i!=common))
                elif source[1].bit_count()==2 and source[1] >> common & 1:
                    other = next(i for i in range(h) if source[1] >> i & 1 and i!=common)
                    proposed = sum(edge(other,j) for j,label in enumerate(source[2]) if abs(label)>1)
                else:
                    proposed = caps[b]
                safe = not proposed & ~caps[b] and contained(source,coframe(h,common,proposed))
                if not safe and policy=='cap-if-needed':
                    proposed = caps[b]
                    safe = contained(source,coframe(h,common,proposed))
                if not safe:
                    restore(b,'no-safe-incidence-enclosure')
                    continue
                additions = proposed & ~active[b]
                if additions:
                    active[b] |= additions
                    changed += 1
                    enqueue(b)
    drain()
    # Empty address regions require a distinct zero-event compiler convention.
    # This controlled experiment keeps the already certified strict-growth
    # convention, rather than silently deleting their allocation events.
    for i in range(len(old)):
        if i not in fallback and not active[i]:
            restore(i,'unseeded-address-region')
    drain()
    while True:
        need = [b for a,targets in enumerate(successors) for b in targets
                if b not in fallback and selected(b)[0]<=selected(a)[0]]
        if not need:
            break
        for b in need:
            restore(b,'strict-positive-transition')
        drain()
    chosen = [selected(i) for i in range(len(old))]
    for before,after in zip(old,chosen):
        assert contained(after,before), 'New frame escaped the actual old upper bound'
    for a,targets in enumerate(successors):
        for b in targets:
            assert contained(chosen[a],chosen[b]) and chosen[a][0]<chosen[b][0]
    aliases,frames,lookup = [],[],{}
    for frame in chosen:
        if frame not in lookup:
            lookup[frame] = len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    fresh = dict(word,frames=frames,frame_format=FORMAT)
    prior = word.get('physical_region_address_aliases')
    fresh['physical_region_address_aliases'] = [aliases[i] for i in prior] if prior else aliases
    fresh['ops'] = [(a,b,aliases[g]) for a,b,g in word['ops']]
    fresh['events'] = [(slot,-1 if a<0 else aliases[a],aliases[b]) for slot,a,b in word['events']]
    fresh['outputs'] = [(slot,aliases[g],common,target) for slot,g,common,target in word['outputs']]
    fresh['fixed_word_source_coframes'] = dict(policy=policy,
        source_two_core_and_copied_center_protection=True,
        actual_old_upper_containment=True,preserved_strict_positive_growth=True)
    receipt = dict(unchanged_R=word['R'],unchanged_every_XOR=True,
        old_actual_space_is_upper_bound=True,every_actual_continuation_contained=True,
        source_two_core_and_copied_center_spaces_unchanged=True,
        signed_fallback_reasons=reasons,closure_updates=changed,
        actual_complemented_frames=sum(len(frame)==4 for frame in chosen),
        strictly_smaller_address_frames=sum(after[0]<before[0] for before,after in zip(old,chosen)),
        removed_address_dimensions=sum(before[0]-after[0] for before,after in zip(old,chosen)))
    return fresh,chosen,receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    rows = []
    started = time.monotonic()
    for config in json.loads(args.input.read_text()):
        parent = config['parent']
        raw = gzip.decompress(Path(parent['word_path']).read_bytes())
        assert sha256(raw).hexdigest()==parent['word_sha256']
        word = json.loads(raw)
        work = args.work/config['case_id']
        work.mkdir()
        fresh,selected,summary = select_fixed_word_coframes(word,config.get('policy','cap-if-needed'))
        raw = (json.dumps(fresh,separators=(',',':'))+'\n').encode()
        path = work/'word.json.gz'
        with path.open('wb') as stream:
            with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as output:
                output.write(raw)
        binary = work/'mixed-transitions.bin'
        independent = check(path,binary)
        profile_path,audit = work/'profile.json',work/'transitions.json'
        with (work/'native.log').open('wb') as log:
            subprocess.run([str(args.binary),str(binary),config['basis'],str(profile_path),str(audit)],
                           stdout=log,stderr=subprocess.STDOUT,check=True)
        profile = json.loads(profile_path.read_text())
        a = config['screen_a']
        phi = sum(t*n*math.expm1(a*math.log(575/t)) for t,n in enumerate(profile['blocks']) if t and n)
        row = dict(status='EXACT CANDIDATE FIXED MATCHING SOURCE COFRAMES',
            config=config,summary=summary,independent=independent,
            word_path=str(path),word_sha256=sha256(raw).hexdigest(),
            input_binary_sha256=sha256(binary.read_bytes()).hexdigest(),
            profile=profile,profile_path=str(profile_path),
            profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
            transition_audit=str(audit),transition_audit_sha256=sha256(audit.read_bytes()).hexdigest(),
            screen_Phi=phi,screen_a=a)
        rows.append(row)
        (args.work/'completed-rows.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps(dict(case=config['case_id'],Phi=phi,summary=summary,
                             elapsed_seconds=time.monotonic()-started)),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(status='COMPLETE FIXED WORD COFRAME COHORT',rows=rows,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Consistent whole-word address-frame substitution with actual source/dirty '
              'replay, old-upper containment and all paid transitions reconstructed. '
              'Fresh source regeneration, independent Fraction/DATA/stock and complete '
              'conditional moment/assembly acceptance remain separate.'),indent=2)+'\n')


if __name__=='__main__':
    main()
