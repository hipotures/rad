#!/usr/bin/env python3
"""Independent executed joint-word, source coefficients and address transitions.

The serialized physical XOR word is authoritative. Region counts and DAG
edge matchings are not used to infer physical roles. Address spaces are the
pinned original E(C,M) families; payload restoration is exhaustively checked
on the complete F2 input/target/dirty basis. Actual transition matrices are
exported for separate exact fixed-basis profiling.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import time


def load(path):
    payload=path.read_bytes();raw=gzip.decompress(payload)if path.suffix=='.gz'else payload
    return json.loads(raw),sha256(payload).hexdigest(),sha256(raw).hexdigest()


def check(path,destination):
    started=time.monotonic();word,packed_sha,raw_sha=load(path)
    h,v,R=(int(word[k])for k in('h','v','R'));triples=list(combinations(range(h),3));assert len(triples)==v
    triple_index={t:i for i,t in enumerate(triples)};frames=[tuple(f)for f in word['frames']]
    assert len(set(frames))==len(frames)
    rank=[]
    for core,cover in frames:
        assert 0<core<=cover and not core&~cover and cover>>h==0
        size=core.bit_count()
        assert(size in(1,2)or(size==3 and core==cover))
        rank.append(1 if core==cover else cover.bit_count()-size)
    def fits(a,b):
        ca,ma=frames[a];cb,mb=frames[b]
        return cb&~ca==0 and ma&~mb==0
    occupancy=[-1]*R;support=[0]*R;transitions=Counter();events=[];hist=Counter()
    def enter(slot,frame):
        assert 0<=slot<R and 0<=frame<len(frames)
        previous=occupancy[slot]
        assert previous<0 or fits(previous,frame)
        hist[rank[frame]-(0 if previous<0 else rank[previous])]+=1
        if previous!=frame:transitions[(0 if previous<0 else previous+2,frame+2)]+=1
        events.append((slot,previous,frame));occupancy[slot]=frame
    frame_lookup={frame:i for i,frame in enumerate(frames)}
    sources={int(i):int(s)for i,s in word['sources'].items()}
    assert set(sources)==set(range(v))and len(set(sources.values()))==v
    for i,s in sources.items():
        mask=sum(1<<j for j in triples[i]);enter(s,frame_lookup[mask,mask]);support[s]=1<<i
    middle=[]
    for a,b,g in word['ops']:
        assert a!=b;enter(a,g);enter(b,g);support[a]^=support[b];middle.append((2*v+a,2*v+b))
    terminals=set();scatter=[];target_support=[0]*v;side_singles=0;centers=0
    for s,g,common,target in word['outputs']:
        assert s not in terminals;terminals.add(s);enter(s,g);target=tuple(target)
        omitted=set(target)-{common};expected=0
        for i,t in enumerate(triples):
            if common in t and not omitted.intersection(t):expected|=1<<i
        assert support[s]==expected,'Actual executed output coefficient support differs'
        c,m=frames[g];assert c==1<<common
        if len(target)==1:
            assert m==(1<<h)-1 and rank[g]==h-1;centers+=1
            transitions[0,g+2]+=1;transitions[g+2,1]+=1
            hist[rank[g]]+=1;hist[h-rank[g]]+=1
            targets=[i for i,t in enumerate(triples)if common in t]
        else:
            assert len(target)==3 and tuple(sorted(target))in triple_index
            assert m==((1<<h)-1)^sum(1<<j for j in omitted)
            side_singles+=h-rank[g];hist[1]+=1;hist[h-1-rank[g]]+=1
            targets=[triple_index[tuple(sorted(target))]]
        for i in targets:target_support[i]^=support[s];scatter.append((v+i,2*v+s))
    assert centers==h and target_support==[1<<i for i in range(v)]
    assert scatter==[tuple(p)for p in word['scatter']],'Serialized endpoint dispatch differs'
    # Allocation and rank-zero raises may occur earlier in the compiler's
    # auxiliary log. Validate that chronology independently, then compare
    # every positive transition and final physical frame to the executed word.
    logged_state=[-1]*R;logged_transitions=Counter()
    for slot,previous,current in word['events']:
        assert 0<=slot<R and logged_state[slot]==previous
        assert previous<0 or fits(previous,current)
        if previous!=current:logged_transitions[(0 if previous<0 else previous+2,current+2)]+=1
        logged_state[slot]=current
    before_closures=Counter(transitions)
    for s,g,common,target in word['outputs']:
        if len(target)==1:
            before_closures[0,g+2]-=1;before_closures[g+2,1]-=1
    before_closures=+before_closures
    assert logged_transitions==before_closures,'Actual positive transition multiset differs'
    assert logged_state==occupancy,'Final physical frame assignment differs'
    for s,g in enumerate(occupancy):
        assert g>=0
        if s not in terminals:transitions[g+2,1]+=1;hist[h-rank[g]]+=1
    full_frames=[(0,0,0),(0,0,h)]+[(c,m,r)for(c,m),r in zip(frames,rank)]
    mass=side_singles+sum((full_frames[b][2]-full_frames[a][2])*n for(a,b),n in transitions.items())
    assert mass==h*R+h*(h-1)==sum(r*n for r,n in hist.items())
    assert all(full_frames[b][2]>full_frames[a][2]for a,b in transitions)
    injection=[(2*v+s,i)for i,s in sources.items()]
    section=middle+scatter+middle[::-1]+injection
    # Stream both complete words from section twice, preserving exact
    # inverse chronology and exchanged endpoint orientation.
    initial=[1<<i for i in range(2*v+R)]
    for reverse in(False,True):
        bits=initial.copy()
        for _ in range(2):
            for a,b in(reversed(section)if reverse else section):
                if reverse:a,b=b,a
                bits[a]^=bits[b]
        assert bits[2*v:]==initial[2*v:],'Dirty physical role not restored'
        changed=range(v)if reverse else range(v,2*v)
        fixed=range(v,2*v)if reverse else range(v)
        assert all(bits[i]==initial[i]for i in fixed)
        assert all(bits[i]==(initial[i%v]^initial[v+i%v])for i in changed)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('wb')as stream:
        stream.write(struct.pack('<6I2Q',h,v,R,len(full_frames),len(transitions),side_singles,mass,h*(h-1)))
        for c,m,r in full_frames:stream.write(struct.pack('<2QI',c,m,r))
        for(a,b),n in sorted(transitions.items()):stream.write(struct.pack('<2Iq',a,b,n))
    result=dict(status='independent literal joint-word, exact source/target support, frames, chronology and all dirty basis PASS',
        h=h,v=v,R=R,output_roles=len(terminals),elementary_middle_xors=len(middle),complete_word_length=2*len(section),
        complete_basis_vectors=2*v+R,orientations=['forward','reverse-complement'],copied_centers=centers,
        exact_transition_multiset_from_word=True,distinct_transitions=len(transitions),rank_mass=mass,
        rank_histogram={str(r):n for r,n in sorted(hist.items())},side_growth_singletons=side_singles,
        word_path=str(path),word_gzip_sha256=packed_sha,word_sha256=raw_sha,transition_path=str(destination),
        transition_sha256=sha256(destination.read_bytes()).hexdigest(),seconds=time.monotonic()-started,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),completed_utc=datetime.now(timezone.utc).isoformat(),
        limitations='Finite F2 payload and original E(C,M) address audit. Fresh fixed-basis CRT profiles and general conditional transfer remain separate gates.')
    Path(str(destination)+'.review.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result),flush=True);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--word',type=Path,required=True);p.add_argument('--transitions',type=Path,required=True)
    a=p.parse_args();check(a.word,a.transitions)


if __name__=='__main__':main()
