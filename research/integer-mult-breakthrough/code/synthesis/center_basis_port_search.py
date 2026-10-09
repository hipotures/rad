#!/usr/bin/env python3
"""Complete paid center-basis port permutations and common-frame discovery.

The identical-coordinate copy baseline has rank mass at least W*h by crossed
endpoint triangles. Orthogonal port matchings remove that local premise, but
their actual scalar swaps and inverses are included. Every data/source/sink
column is replayed. Many-label alpha expansion is heuristic; no native phase
word, precision guarantee, complete multiplier recurrence or kappa is claimed.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib
import json
from pathlib import Path
import random
import sys
import time

import global_word_frame_search as f

COMPLEX=Path(__file__).resolve().parents[1]/'complex'
sys.path.insert(0,str(COMPLEX))
center=importlib.import_module('center_basis_scalar_word')


def orthogonal_matching(labels,seed):
    rng=random.Random(seed);v=len(labels)
    adjacency=[[j for j,t in enumerate(labels) if (s&t).bit_count()%2==0] for s in labels]
    for row in adjacency:rng.shuffle(row)
    occupied=[None]*v
    def visit(a,seen):
        for b in adjacency[a]:
            if b in seen:continue
            seen.add(b)
            if occupied[b] is None or visit(occupied[b],seen):occupied[b]=a;return True
        return False
    for a in range(v):
        if not visit(a,set()):raise ValueError('Five-subset orthogonal port graph lacks a complete matching')
    permutation=[None]*v
    for b,a in enumerate(occupied):permutation[a]=b
    if sorted(permutation)!=list(range(v)) or any((labels[a]&labels[b]).bit_count()%2 for a,b in enumerate(permutation)):
        raise ValueError('Orthogonal port matching failed independent replay')
    return permutation


def expanded(word,offset=0):
    result=[]
    for kind,*args in word:
        if kind=='add':a,b,c=args;result.append(('add',offset+a,offset+b,Q(c)))
        elif kind=='scale':a,c=args;result.append(('scale',offset+a,Q(c)))
        elif kind=='swap':
            a,b=(offset+x for x in args)
            result.extend([('add',a,b,Q(1)),('add',b,a,Q(-1)),('add',a,b,Q(1)),('scale',b,Q(-1))])
        else:raise ValueError('Unknown center scalar primitive')
    return result


def inverted(word):
    return [
        ('add',event[1],event[2],-event[3]) if event[0]=='add'
        else ('scale',event[1],1/event[2]) for event in reversed(word)]


def permutation_swaps(permutation):
    arrangement=list(range(len(permutation)));swaps=[]
    target=[None]*len(permutation)
    for a,b in enumerate(permutation):target[b]=a
    for i,a in enumerate(target):
        if arrangement[i]!=a:
            j=arrangement.index(a);arrangement[i],arrangement[j]=arrangement[j],arrangement[i];swaps.append(('swap',i,j))
    if arrangement!=target:raise ValueError('Paid permutation word has incorrect direction')
    return swaps


def full_word(h,layout,seed):
    component=center.complete_word(h);labels=[sum(1<<j for j in s) for s in component['source_order']];v=len(labels)
    Bx=expanded(component['word']);By=expanded(component['word'],v)
    permutation=orthogonal_matching(labels,seed);swaps=permutation_swaps(permutation);P=expanded(swaps,v)
    before=Bx+By if layout=='batched' else [event for pair in zip(Bx,By) for event in pair]
    copies=[('add',v+permutation[j],j,Q(1)) for j in range(v)]
    word=before+P+copies+inverted(P)+inverted(before)
    return word,labels,permutation,dict(center_rank=component['center_rank'],basis_operations=dict(Counter(op[0] for op in component['word'])),
                                       paid_middle_role_swaps=len(swaps),layout=layout,extra_clean_banks=0)


def replay(word,w,copy_index=None):
    rows=[{j:Q(1)} for j in range(w)]
    for step,event in enumerate(word):
        if event[0]=='scale':
            _,a,c=event;rows[a]={j:c*z for j,z in rows[a].items() if c*z}
        else:
            _,a,b,c=event
            if step==copy_index:c=-c
            for j,z in list(rows[b].items()):
                value=rows[a].get(j,Q())+c*z
                if value:rows[a][j]=value
                else:rows[a].pop(j,None)
    v=w//2;expected=[{j:Q(1)} for j in range(w)]
    for j in range(v):expected[v+j][j]=Q(1)
    bad=[j for j in range(w) if rows[j]!=expected[j]]
    if bool(bad)!=(copy_index is not None):raise ValueError('Complete center-basis data columns failed')
    witness=None
    if bad:
        a=bad[0];j=next(j for j in sorted(set(rows[a])|set(expected[a])) if rows[a].get(j,Q())!=expected[a].get(j,Q()))
        witness=dict(output_role=a,initial_column=j,expected=str(expected[a].get(j,Q())),observed=str(rows[a].get(j,Q())))
    return dict(status='CORRUPTION DETECTED' if bad else 'EXACT COMPLETE SCALAR PASS',initial_columns=w,
                source_columns=v,arbitrary_sink_columns=v,witness=witness)


def domain_for(labels,h,limit,seed):
    zero=f.le((),h);full=f.le(tuple(1<<j for j in range(h)),h)
    required={zero,full}|{f.le((T,),h) for T in labels}|{f.le(f.perpendicular((T,),h),h) for T in labels}
    # Short shared centers and intersections create useful nonuniform labels;
    # no stationary or nondegenerate graph restriction is imposed on L_E.
    candidates={f.le((1<<i,1<<j),h) for i in range(h) for j in range(i)}
    for a,b in zip(labels,labels[1:]):
        candidates.add(f.le((a,b),h));candidates.add(f.le(f.perpendicular((a,b),h),h))
    rng=random.Random(seed)
    for _ in range(limit*2):
        vectors=tuple(rng.randrange(1,1<<h) for _ in range(rng.randrange(1,h)))
        candidates.add(f.le(vectors,h))
    extra=sorted(candidates-required);rng.shuffle(extra)
    return sorted(required|set(extra[:max(0,limit-len(required))]))


def probe(spec):
    h,layout,limit,rounds,seed=spec;started=time.monotonic();rng=random.Random(seed)
    operations,labels,permutation,component=full_word(h,layout,seed);v=len(labels);w=2*v
    middle=next(j for j,event in enumerate(operations) if event[0]=='add' and event[1]>=v and event[2]<v)
    positive=replay(operations,w);negative=replay(operations,w,middle)
    word=[(e[1],e[2],e[3]) for e in operations if e[0]=='add']
    sys.setrecursionlimit(max(10000,len(word)*3));domain=domain_for(labels,h,limit,seed);ids={L:j for j,L in enumerate(domain)}
    zero=f.le((),h);full=f.le(tuple(1<<j for j in range(h)),h)
    starts=[f.le((T,),h) for T in labels]+[zero]*v;ends=[full]*v+[f.le(f.perpendicular((T,),h),h) for T in labels]
    frames=len(domain);cache={}
    def dist(a,b):
        if a==b:return 0
        key=tuple(sorted((a,b)))
        if key not in cache:cache[key]=f.distance(domain[a],domain[b],h)
        return cache[key]
    edges,boundaries,constant=f.incidence_graph(word,w,starts,ends)
    unary=[[sum(dist(j,ids[F]) for F in bound) for j in range(frames)] for bound in boundaries]
    capacity=w*h;endpoint=sum(f.distance(a,b,h) for a,b in zip(starts,ends));best=None;best_labels=None;traces=[]
    for initial_name,initial in [('zero',[ids[zero]]*len(word)),('full',[ids[full]]*len(word))]:
        assignments=initial;cost=f.energy(assignments,edges,unary,dist,constant)
        if cost!=capacity:raise ValueError('Fixed common-frame stock baseline differs from Wh')
        trace=[cost];visited={tuple(assignments)}
        for sweep in range(rounds):
            moved=False;alphas=list(range(frames));rng.shuffle(alphas)
            for alpha in alphas:
                proposal=f.alpha_move(assignments,alpha,edges,unary,dist);new=f.energy(proposal,edges,unary,dist,constant)
                if new>cost:raise ValueError('Exact binary expansion increased rank cost')
                if new<cost or (new==cost and tuple(proposal) not in visited):
                    assignments=proposal;cost=new;visited.add(tuple(proposal));moved=True
            trace.append(cost)
            if not moved:break
        if best is None or cost<best:best=cost;best_labels=assignments
        traces.append(dict(initial=initial_name,cost_trace=trace,visited_assignments=len(visited)))
    current=list(starts);hist=Counter();chronology=[]
    for j,(a,b,c) in enumerate(word):
        common=domain[best_labels[j]]
        for role in (a,b):
            rank=f.distance(current[role],common,h)
            if rank:hist[rank]+=1
            current[role]=common
        chronology.append(dict(destination=a,source=b,coefficient=str(c),common_frame=best_labels[j]))
    for role,F in enumerate(ends):
        rank=f.distance(current[role],F,h)
        if rank:hist[rank]+=1
    if sum(r*c for r,c in hist.items())!=best or best<endpoint:raise ValueError('Actual chronological mass/endpoints fail graph replay')
    # Optimistic homogeneous rank-width moment only; polynomial overhead,
    # coefficient scales and a complete outer assembly are still unpaid.
    at_target=sum(c*r*2**(1e-4*(h-r)) for r,c in hist.items())/capacity
    return dict(status='FOUND ABSTRACT RANK DEFICIT' if best<capacity else 'NO DEFICIT FOUND BY HEURISTIC; NOT AN EXCLUSION',
                h=h,vertices=v,payload_stock=w,center_component=component,seed=seed,
                scalar_gate_counts=dict(Counter(e[0] for e in operations)),scalar_shear_incidences=len(word),
                searched_L_E_frames=frames,complete_endpoint_floor=endpoint,capacity=capacity,rank_charge=best,deficit=capacity-best,
                optimistic_homogeneous_moment_at_kappa_1e_4=at_target,chronological_rank_histogram=dict(sorted(hist.items())),
                scalar_replay=positive,scalar_corruption=negative,trajectories=traces,
                source_labels=labels,middle_port_permutation=permutation,common_frames=domain,word=chronology,
                scalar_operations=[list(e) for e in operations],seconds=time.monotonic()-started,
                scope='Exact complete scalar y+=x on arbitrary source/sink values; zero extra initialized banks; all basis/permutation swaps expanded and reversed. Supplied L_E frame chronology and endpoints are exactly rank-accounted. Optimization is heuristic, moment is optimistic. Literal Gaussian frame lifts, residual gauge, native row movement, coefficient precision and full recurrence are unproved.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--rounds',type=int,default=2);p.add_argument('--frames',type=int,default=128)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    specs=[(7,'batched',args.frames,args.rounds,20261008101),(7,'interleaved',args.frames,args.rounds,20261008102),
           (8,'batched',args.frames,args.rounds,20261008103),(8,'interleaved',args.frames,args.rounds,20261008104)]
    paths=[Path(__file__),Path(f.__file__),Path(f.__file__).with_name('lagrangian_graph_completion.py'),
           Path(f.__file__).with_name('trimmed_zeta_dirty_probe.py'),f.SIDE_SOURCE]+[
           COMPLEX/name for name in ('center_basis_scalar_word.py','structured_center_basis.py','center_null_basis.py')]
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,
                  source_sha256={p.name:v for p,v in hashes.items()},optimizer='Exact binary alpha moves, bounded many-label strict/plateau discovery')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');controls=f.binary_controls();cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({k:result[k] for k in ('status','h','deficit','rank_charge','capacity','seconds')}),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=v for p,v in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(controls=controls,cases=cases),indent=2,default=str)+'\n')


if __name__=='__main__':main()
