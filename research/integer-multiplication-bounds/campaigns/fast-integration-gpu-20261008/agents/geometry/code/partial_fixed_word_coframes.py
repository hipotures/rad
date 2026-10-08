#!/usr/bin/env python3
"""Partial source-coframe choices with exact forward restoration closure."""
import argparse
from collections import deque
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess

from fixed_word_source_coframes import (select_fixed_word_coframes, contained,
                                      normalize, FORMAT, check)
from co_signed_source_frames import basis, vector_in


def removed_direction_balances(old,minimum):
    result = []
    for before,after in zip(old,minimum):
        if before[0]==after[0]:
            result.append(None)
            continue
        assert before[0]-after[0]==1 and len(after)==4
        common = after[1].bit_length()-1
        normal = after[3]
        groups = {}
        for i,label in enumerate(normal):
            if abs(label)>1:
                groups.setdefault(abs(label),[]).append(i)
        vector = next(v for v in basis(before) if not vector_in(v,after))
        total = Q(0)
        for indices in groups.values():
            signs = [1 if normal[i]>0 else -1 for i in indices]
            total += Q(sum(sign*v for sign,v in zip(signs,[vector[i] for i in indices]))
                       *sum(signs),len(indices))
        result.append(total==0)
    return result


def select_partial(word,minimum,balances,protect_ordinary=False,restore_rank_below=0,
                   restore_removed_direction=None):
    old = [normalize(frame) for frame in word['frames']]
    successors = [set() for _ in old]
    for slot,a,b in word['events']:
        if a>=0 and a!=b:
            successors[a].add(b)
    restored = {i for i,frame in enumerate(old) if frame[0]==minimum[i][0]}
    if protect_ordinary:
        restored.update(g for slot,g,c,target in word['outputs'] if len(target)==3)
    restored.update(i for i,frame in enumerate(old) if frame[0]<restore_rank_below)
    if restore_removed_direction:
        assert restore_removed_direction in ('balanced','unbalanced')
        restored.update(i for i,balance in enumerate(balances) if balance is not None
                        and balance==(restore_removed_direction=='balanced'))
    seeded = len(restored)
    queue = deque(restored)
    while queue:
        a = queue.popleft()
        for b in successors[a]:
            if b not in restored and (not contained(old[a],minimum[b])
                                       or old[a][0]>=minimum[b][0]):
                restored.add(b)
                queue.append(b)
    chosen = [old[i] if i in restored else minimum[i] for i in range(len(old))]
    for i,after in enumerate(chosen):
        assert contained(minimum[i],after) and contained(after,old[i])
    for a,targets in enumerate(successors):
        for b in targets:
            assert contained(chosen[a],chosen[b]) and chosen[a][0]<chosen[b][0]
    aliases,frames,lookup = [],[],{}
    for frame in chosen:
        if frame not in lookup:
            lookup[frame]=len(frames)
            frames.append(frame)
        aliases.append(lookup[frame])
    fresh = dict(word,frames=frames,frame_format=FORMAT)
    prior = word.get('physical_region_address_aliases')
    fresh['physical_region_address_aliases']=[aliases[i] for i in prior] if prior else aliases
    fresh['ops']=[(a,b,aliases[g]) for a,b,g in word['ops']]
    fresh['events']=[(s,-1 if a<0 else aliases[a],aliases[b]) for s,a,b in word['events']]
    fresh['outputs']=[(s,aliases[g],c,target) for s,g,c,target in word['outputs']]
    fresh['partial_fixed_word_coframes']=dict(protect_ordinary=protect_ordinary,
        restore_rank_below=restore_rank_below,restore_removed_direction=restore_removed_direction)
    summary=dict(unchanged_R=word['R'],unchanged_every_XOR=True,
        minimum_contained_in_selected_contained_in_old=True,
        all_actual_continuations_strictly_nested=True,
        seeded_restored_frames=seeded,forward_restored_frames=len(restored)-seeded,
        strictly_smaller_frames=sum(a[0]<b[0] for a,b in zip(chosen,old)),
        removed_address_dimensions=sum(b[0]-a[0] for a,b in zip(chosen,old)))
    return fresh,chosen,summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    cache,seen,rows={},set(),[]
    for config in json.loads(args.input.read_text()):
        parent=config['parent'];key=parent['word_sha256']
        if key not in cache:
            raw=gzip.decompress(Path(parent['word_path']).read_bytes())
            assert sha256(raw).hexdigest()==key
            word=json.loads(raw)
            _,minimum,receipt=select_fixed_word_coframes(word)
            old=[normalize(frame) for frame in word['frames']]
            cache[key]=word,minimum,removed_direction_balances(old,minimum),receipt
        word,minimum,balances,minimum_receipt=cache[key]
        fresh,selected,summary=select_partial(word,minimum,balances,
            config.get('protect_ordinary',False),config.get('restore_rank_below',0),
            config.get('restore_removed_direction'))
        signature=sha256(json.dumps(selected,separators=(',',':')).encode()).hexdigest()
        identity=key,signature,config['basis']
        if identity in seen:
            row=dict(status='NEGATIVE: DUPLICATE EXACT PARTIAL FRAME ASSIGNMENT',
                     config=config,summary=summary,assignment_sha256=signature)
        else:
            seen.add(identity)
            work=args.work/config['case_id'];work.mkdir()
            raw=(json.dumps(fresh,separators=(',',':'))+'\n').encode()
            path=work/'word.json.gz'
            with path.open('wb') as stream:
                with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0) as output:
                    output.write(raw)
            binary=work/'mixed-transitions.bin';independent=check(path,binary)
            profile_path,audit=work/'profile.json',work/'transitions.json'
            with (work/'native.log').open('wb') as log:
                subprocess.run([str(args.binary),str(binary),config['basis'],str(profile_path),str(audit)],
                               stdout=log,stderr=subprocess.STDOUT,check=True)
            profile=json.loads(profile_path.read_text());a=config['screen_a']
            phi=sum(t*n*math.expm1(a*math.log(575/t)) for t,n in enumerate(profile['blocks']) if t and n)
            row=dict(status='EXACT CANDIDATE PARTIAL FIXED-WORD COFRAMES',config=config,
                summary=summary,minimum_receipt=minimum_receipt,independent=independent,
                assignment_sha256=signature,word_path=str(path),word_sha256=sha256(raw).hexdigest(),
                input_binary_sha256=sha256(binary.read_bytes()).hexdigest(),
                profile=profile,profile_path=str(profile_path),profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
                transition_audit=str(audit),transition_audit_sha256=sha256(audit.read_bytes()).hexdigest(),
                screen_Phi=phi,screen_a=a)
        rows.append(row)
        (args.work/'completed-rows.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps(dict(case=config['case_id'],completed=len(rows),status=row['status'],
                              Phi=row.get('screen_Phi'),summary=summary)),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(status='COMPLETE PARTIAL FIXED-WORD COFRAME COHORT',
        rows=rows,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        minimum_constructor_sha256=sha256(Path(__file__).with_name('fixed_word_source_coframes.py').read_bytes()).hexdigest(),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        scope='Whole source-bound actual-word substitutions with exact restoration closure. '
              'Physical/source/dirty and full native profiles checked; independent source '
              'regeneration, Fraction/DATA/stock and recurrence assembly remain acceptance gates.'),indent=2)+'\n')


if __name__=='__main__':main()
