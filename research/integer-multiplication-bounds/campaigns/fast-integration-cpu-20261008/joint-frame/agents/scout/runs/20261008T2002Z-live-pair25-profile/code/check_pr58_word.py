#!/usr/bin/env python3
"""Independent finite physical-word and per-role frame-path verification.

No upstream producer, compiler, replay, transition extractor or arithmetic
module is imported. The complete source, target and arbitrary dirty basis
are represented at once as rows of a binary matrix. Literal phase sequences
are applied directly in both orientations, rather than trusting compiler
flags or its recorded event multiset.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import gzip
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import struct
import time


def check(word, transitions_path):
    raw=word.read_bytes()
    decompressed=gzip.decompress(raw) if word.suffix=='.gz' else raw
    data=json.loads(decompressed)
    h,v,R=(data[k] for k in ('h','v','R'))
    assert h in (23,25) and v==comb(h,3) and R>0
    full=(1<<h)-1
    triples=list(combinations(range(h),3))
    triple_ids={triple:i for i,triple in enumerate(triples)}
    masks=[sum(1<<j for j in triple) for triple in triples]
    frames=[tuple(f) for f in data['frames']]
    assert len(set(frames))==len(frames)
    lookup={frame:i for i,frame in enumerate(frames)}
    ranks=[]
    for core,cover in frames:
        assert 0<core<=full and 0<cover<=full and core&~cover==0
        c=core.bit_count()
        assert c in (1,2) or c==3 and core==cover
        ranks.append(1 if core==cover else cover.bit_count()-c)
        assert 0<ranks[-1]<h
    source={int(k):s for k,s in data['sources'].items()}
    assert set(source)==set(range(v)) and len(set(source.values()))==v
    assert all(isinstance(s,int) and 0<=s<R for s in source.values())
    current=[None]*R
    paths=[[] for _ in range(R)]
    positive=Counter()
    symbols=[0]*R

    def incidence(s,g):
        assert isinstance(s,int) and 0<=s<R and isinstance(g,int) and 0<=g<len(frames)
        old=current[s]
        if old is not None:
            c,u=frames[old];cc,uu=frames[g]
            assert cc&~c==0 and u&~uu==0
            assert ranks[g]>=ranks[old]
        if old!=g:
            a=0 if old is None else old+2
            positive[a,g+2]+=1
            paths[s].append((a,g+2))
        current[s]=g

    for i,s in sorted(source.items()):
        incidence(s,lookup[masks[i],masks[i]])
        symbols[s]=1<<i
    M=[]
    for a,b,g in data['ops']:
        assert a!=b
        incidence(a,g);incidence(b,g)
        symbols[a]^=symbols[b]
        M.append((a,b))
    output_slots=set();scatter_expected=[];center_count=0;singles=0
    center_masks=[sum(1<<i for i,t in enumerate(triples) if common in t)
                  for common in range(h)]
    for slot,g,common,triple in data['outputs']:
        assert slot not in output_slots and 0<=common<h
        output_slots.add(slot)
        incidence(slot,g)
        core,cover=frames[g]
        assert core==1<<common
        if len(triple)==1:
            assert triple==[common] and cover==full and ranks[g]==h-1
            expected=center_masks[common]
            targets=[i for i,t in enumerate(triples) if common in t]
            positive[0,g+2]+=1
            positive[g+2,1]+=1
            center_count+=1
        else:
            assert len(triple)==3 and triple==sorted(triple) and tuple(triple) in triple_ids
            assert common in triple
            excluded=set(triple)-{common}
            assert cover==full^sum(1<<j for j in excluded)
            expected=sum(1<<i for i,t in enumerate(triples)
                         if common in t and not excluded.intersection(t))
            targets=[triple_ids[tuple(triple)]]
            # Ordinary side growth rank2 uses the inherited conservative
            # singleton split, together with its rank1 output line.
            assert h-1-ranks[g]==2
            singles+=h-ranks[g]
        assert symbols[slot]==expected
        scatter_expected.extend((v+i,2*v+slot) for i in targets)
    assert center_count==h
    assert len(output_slots)==h*(comb(h-1,2)+1)
    scatter=[tuple(gate) for gate in data['scatter']]
    assert scatter==scatter_expected and len(scatter)==6*v
    scatter_rows=[0]*v
    for a,b in scatter:
        assert v<=a<2*v and 2*v<=b<2*v+R
        scatter_rows[a-v]^=symbols[b-2*v]
    assert scatter_rows==[1<<i for i in range(v)]
    for s,g in enumerate(current):
        assert g is not None
        if s not in output_slots:positive[g+2,1]+=1
    # Compare the recorded event path role BY role, after removing zero
    # repeated-frame incidences; an aggregate counter alone is insufficient.
    event_current=[None]*R;event_paths=[[] for _ in range(R)]
    for slot,old,new in data['events']:
        assert isinstance(slot,int) and 0<=slot<R and -1<=old<len(frames) and 0<=new<len(frames)
        assert event_current[slot]==(None if old==-1 else old)
        if old!=-1:
            c,u=frames[old];cc,uu=frames[new]
            assert cc&~c==0 and u&~uu==0
        if old!=new:event_paths[slot].append((0 if old==-1 else old+2,new+2))
        event_current[slot]=new
    assert event_current==current and event_paths==paths
    frame_rows=[(0,0,0),(0,0,h)]+[(c,u,r) for (c,u),r in zip(frames,ranks)]
    histogram=Counter({1:singles})
    for (a,b),count in positive.items():
        increment=frame_rows[b][2]-frame_rows[a][2]
        assert count>0 and increment>0
        histogram[increment]+=count
    loss=h*(h-1)
    mass=sum(r*n for r,n in histogram.items())
    assert mass==h*R+loss
    if transitions_path:
        assert not transitions_path.exists()
        with transitions_path.open('wb') as stream:
            stream.write(struct.pack('<6I2Q',h,v,R,len(frame_rows),len(positive),singles,mass,loss))
            for row in frame_rows:stream.write(struct.pack('<2QI',*row))
            for (a,b),count in sorted(positive.items()):stream.write(struct.pack('<2Iq',a,b,count))
    # Full arbitrary dirty columns: execute the actual chronological phase
    # sequence directly; each XOR is its own inverse over the payload field.
    size=2*v+R
    initial=[1<<i for i in range(size)]
    injection=[(2*v+s,i) for i,s in sorted(source.items())]
    mixer=[(2*v+a,2*v+b) for a,b in M]
    phases=[mixer,scatter,list(reversed(mixer)),injection,
            mixer,scatter,list(reversed(mixer)),injection]
    full_checks=[]
    for dual in (False,True):
        values=list(initial)
        ordered=reversed(phases) if dual else phases
        count=0
        for phase in ordered:
            gates=reversed(phase) if dual else phase
            for a,b in gates:
                assert 0<=a<size and 0<=b<size and a!=b
                if dual:values[b]^=values[a]
                else:values[a]^=values[b]
                count+=1
        assert count==4*len(M)+14*v
        for i,row in enumerate(values):
            other=v+i if dual and i<v else i-v if not dual and v<=i<2*v else None
            expected=initial[i]^(initial[other] if other is not None else 0)
            assert row==expected,(dual,i)
        full_checks.append(dict(orientation='transposed reversed word' if dual else 'forward word',
                                basis_columns=size,physical_rows=size,elementary_xors=count,
                                every_source_target_dirty_row_exact=True))
    canonical=('\n'.join('%d %d %d'%(a,b,n) for (a,b),n in sorted(positive.items()))+'\n').encode()
    return dict(status='INDEPENDENT FULL DIRTY BASIS AND PER-ROLE FRAME PATH PASS',
                h=h,v=v,R=R,frames=len(frames),local_xors=len(M),scatter_xors=len(scatter),
                output_roles=len(output_slots),copied_centers=center_count,singles=singles,
                source_gzip_sha256=hashlib.sha256(raw).hexdigest(),
                decompressed_word_sha256=hashlib.sha256(decompressed).hexdigest(),
                full_basis_checks=full_checks,all_actual_output_symbols_exact=True,
                scatter_reconstructed_from_outputs=True,
                all_per_role_positive_frame_paths_equal_events=True,
                distinct_positive_transitions=len(positive),
                positive_transition_canonical_sha256=hashlib.sha256(canonical).hexdigest(),
                rank_histogram=dict(sorted(histogram.items())),rank_mass=mass,
                transitions_sha256=hashlib.sha256(transitions_path.read_bytes()).hexdigest() if transitions_path else None,
                scope='Finite XOR and rational-envelope frame-path certificate. Address residual execution, fixed-tape machine and all-size analytic transfer remain separate proof obligations.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',required=True,type=Path)
    ap.add_argument('--transitions',type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    assert __debug__ and not args.output.exists()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.transitions:args.transitions.parent.mkdir(parents=True,exist_ok=True)
    start=time.monotonic()
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  word=str(args.word),word_gzip_sha256=hashlib.sha256(args.word.read_bytes()).hexdigest(),
                  native_threads=1)
    args.output.with_suffix('.protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    result=check(args.word,args.transitions)
    result.update(completed_utc=datetime.now(timezone.utc).isoformat(),seconds=time.monotonic()-start,
                  source_sha256=protocol['source_sha256'],native_threads=1)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','h','R','rank_mass','distinct_positive_transitions','seconds')}),flush=True)


if __name__=='__main__':main()
