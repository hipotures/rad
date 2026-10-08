#!/usr/bin/env python3
"""Core-preserving backward signed closure of a literal executed joint word.

Retains every physical role and XOR. Unlike scalar-only positive labels,
constraints propagate along EVERY actual physical address transition,
including selected controller retention and reclaimed-role clearing.
Each original E(C,M) fits the new signed space, every actual transition
remains rationally nested, and each output annihilator is checked literally.
"""
import argparse
from datetime import datetime,timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import time
import joint_region_search_v3 as region
from check_compiled_witness import contained
from joint_word_check_v4 import check


def extend(word):
    h=word['h'];original=[tuple(z)for z in word['frames']];n=len(original);edges=[set()for _ in range(n)];pending=[set()for _ in range(n)];constraints=[set()for _ in range(n)]
    ranks=[1 if c==m else m.bit_count()-c.bit_count()for c,m in original]
    for slot,old,new in word['events']:
        if old>=0 and old!=new:
            assert region.fits(original[old],original[new])and ranks[old]<ranks[new]
            edges[old].add(new);pending[new].add(old)
    for slot,g,common,target in word['outputs']:
        assert original[g][0]==1<<common
        if len(target)==3:constraints[g].add(tuple(sorted(j for j in target if j!=common)))
    for g in sorted(range(n),key=lambda g:(-ranks[g],g)):
        for old in pending[g]:constraints[old].update(constraints[g])
    signed=[]
    for g,(F,M)in enumerate(original):
        if F==M:
            assert F.bit_count()==3;signed.append((1,F,tuple(int(F>>j&1)for j in range(h))));continue
        assert F.bit_count()in(1,2);adj=[set()for _ in range(h)];symbols=[0]*h;colors=[-1]*h;parts=[]
        for a,b in constraints[g]:
            assert not(F>>a&1 or F>>b&1);adj[a].add(b);adj[b].add(a)
        for a in range(h):
            if F>>a&1:symbols[a]=1;continue
            if colors[a]>=0:continue
            colors[a]=0;todo=[a];positive=[];negative=[];odd=False
            while todo:
                b=todo.pop();(positive if colors[b]==0 else negative).append(b)
                for j in sorted(adj[b]):
                    if colors[j]<0:colors[j]=1-colors[b];todo.append(j)
                    elif colors[j]==colors[b]:odd=True
            if not odd:parts.append((positive,negative))
        for label,(positive,negative)in enumerate(parts,2):
            for a in positive:symbols[a]=label
            for a in negative:symbols[a]=-label
        frame=(len(parts),F,tuple(symbols));old=(ranks[g],F,tuple(1 if F>>j&1 else j+2 if M>>j&1 else 0 for j in range(h)))
        assert contained(old,frame),'Original address escaped signed enlargement';signed.append(frame)
    for old,targets in enumerate(edges):
        for new in targets:assert contained(signed[old],signed[new]),'Actual word transition escaped closure'
    aliases=[];lookup={};frames=[]
    for f in signed:
        if f not in lookup:lookup[f]=len(frames);frames.append(f)
        aliases.append(lookup[f])
    converted=dict(word);converted.update(frames=frames,frame_format='positive-signed-v1',positive_closure='original forced core; all physical address transitions; terminal annihilators',physical_region_address_aliases=aliases)
    converted['ops']=[(a,b,aliases[g])for a,b,g in word['ops']];converted['outputs']=[(s,aliases[g],c,t)for s,g,c,t in word['outputs']]
    converted['events']=[(s,-1 if before<0 else aliases[before],aliases[after])for s,before,after in word['events']]
    return converted,dict(original_address_classes=n,positive_address_classes=len(frames),actual_directed_transition_types=sum(map(len,edges)),strict_rank_enlargements=sum(signed[g][0]>ranks[g]for g in range(n)),unchanged_physical_roles=word['R'],unchanged_every_xor=True,original_E_containment=True,all_actual_word_containments=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--h',type=int,required=True);p.add_argument('--word',type=Path)
    a=p.parse_args();assert not a.work.exists();a.work.mkdir(parents=True);at=time.monotonic();region.initialize(a.source,a.work)
    if a.word:
        raw=a.word.read_bytes();raw=gzip.decompress(raw)if a.word.suffix=='.gz'else raw;word=json.loads(raw);assert word['h']==a.h;scalar=None;source_only=False
    else:
        config=dict(h=a.h,policy='baseline',rank_delta=1,sweeps=1,limit=0);region.COMPILER.build=lambda h:region.build_regions(h,config)
        compiled,word=region.COMPILER.compile_(a.h,matching=True,reclaim=True,dirty=True);raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
        if a.h in(23,25):assert sha256(raw).hexdigest()==sha256(gzip.decompress((a.source/f'research/pair-assembly/frame/frame-word-{a.h}.json.gz').read_bytes())).hexdigest()
        scalar=region.graph(a.h).verify();source_only=True
    original_sha=sha256(raw).hexdigest();word,summary=extend(word);raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=a.work/'word.json.gz'
    with path.open('wb')as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0)as gz:gz.write(raw)
    audit=check(path,a.work/'signed-transitions.bin')
    result=dict(status='same physical executed word with core-preserving signed enlargement full dirty/address PASS',h=a.h,R=word['R'],source_only=source_only,source_head='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',source_word_sha256=original_sha,word_path=str(path),word_sha256=sha256(raw).hexdigest(),scalar=scalar,independent=audit,closure=summary,command=__import__('sys').argv,seconds=time.monotonic()-at,completed_utc=datetime.now(timezone.utc).isoformat(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),limitations='Changed actual signed residual matrices require fresh complete bounded-minor profiles. Same role count is not itself a moment gain.')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status=result['status'],h=a.h,R=word['R'],closure=summary,seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
