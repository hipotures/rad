#!/usr/bin/env python3
"""Sparse five-color center/side words with paid ports and radical frames.

For h7 weight5, complement pairs colored by four stars and a final triangle
give a rank5 fitting center. A class sum and I-J side coordinates form
unimodular scalar words. All physical source/sink operations, swaps and exact
columns are retained. Noncoordinate parity hyperplanes lift a restriction of
Boolean-coordinate frame searches; many-label discovery remains heuristic.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import random

import center_basis_port_search as p

GROUPS=None


def groups_and_labels(h):
    if h!=7:raise ValueError('The five-color complement-pair construction is specifically h7')
    labels=[sum(1<<j for j in s) for s in combinations(range(h),5)];groups=[[] for _ in range(5)]
    for index,T in enumerate(labels):
        pair=[j for j in range(h) if not T>>j&1];color=pair[0] if pair[0]<4 else 4;groups[color].append(index)
    if [len(group) for group in groups]!=[6,5,4,3,3]:raise ValueError('Star/triangle coloring is incomplete')
    for group in groups:
        if any((labels[a]&labels[b]).bit_count()%2 for a in group for b in group if a!=b):
            raise ValueError('A color contains a forbidden nonorthogonal pair')
    return labels,groups


def full_word(h,layout,seed):
    global GROUPS
    kind,placement=layout.split('-');labels,groups=groups_and_labels(h);GROUPS=groups;v=len(labels);component=[]
    for group in groups:
        pivot,*others=group
        component.extend(('add',pivot,j,p.Q(1)) for j in others)
        if kind=='side':component.extend(('add',j,pivot,p.Q(-1)) for j in others)
        elif kind!='sum':raise ValueError('Unknown color-basis kind')
    Bx=p.expanded(component);By=p.expanded(component,v)
    before=Bx+By if placement=='batched' else [event for pair in zip(Bx,By) for event in pair]
    permutation=list(range(v))
    for group in groups:
        for a,b in zip(group,group[1:]+group[:1]):permutation[a]=b
    if any((labels[a]&labels[b]).bit_count()%2 for a,b in enumerate(permutation)):
        raise ValueError('The fixed cyclic color matching is not orthogonal')
    swaps=p.permutation_swaps(permutation);P=p.expanded(swaps,v)
    copies=[('add',v+permutation[j],j,p.Q(1)) for j in range(v)]
    word=before+P+copies+p.inverted(P)+p.inverted(before)
    return word,labels,permutation,dict(center_rank=5,color_class_sizes=[len(g) for g in groups],
                color_classes=groups,basis_kind=kind,basis_scalar_additions=len(component),
                paid_middle_role_swaps=len(swaps),layout=placement,extra_clean_banks=0,
                radical_frames_in_domain=True)


def domain_for(labels,h,limit,seed):
    zero=p.f.le((),h);full=p.f.le(tuple(1<<j for j in range(h)),h)
    required={zero,full}|{p.f.le((T,),h) for T in labels}|{p.f.le(p.f.perpendicular((T,),h),h) for T in labels}
    priority=set(required);extra=set()
    for group in GROUPS:
        vectors=[labels[j] for j in group];m=len(vectors);U=p.f.basis(vectors,h)
        # Loss of a noncoordinate parity hyperplane can remove every odd
        # basis label jointly, unlike dropping one Boolean basis coordinate.
        normal=0
        for v in vectors:normal^=v
        parity=p.f.intersection(U,p.f.perpendicular((normal,),h),h)
        if len(U)!=m or len(parity)!=m-1:raise ValueError('Class parity hyperplane has wrong dimension')
        priority|={p.f.le(U,h),p.f.le(parity,h),p.f.le(p.f.perpendicular(U,h),h),p.f.le(p.f.perpendicular(parity,h),h)}
        for mask in range(1<<m):
            E=p.f.basis(tuple(vectors[j] for j in range(m) if mask>>j&1),h)
            extra.add(p.f.le(E,h));extra.add(p.f.le(p.f.perpendicular(E,h),h))
        for mask in range(1,1<<m):
            normal=0
            for j in range(m):
                if mask>>j&1:normal^=vectors[j]
            E=p.f.intersection(U,p.f.perpendicular((normal,),h),h)
            extra.add(p.f.le(E,h));extra.add(p.f.le(p.f.perpendicular(E,h),h))
    remainder=sorted(extra-priority);random.Random(seed).shuffle(remainder)
    return sorted(priority|set(remainder[:max(0,limit-len(priority))]))


def probe(spec):
    # Both replacements are explicit source-owned callbacks in this process;
    # the retained generic engine supplies independent scalar/rank replays.
    p.full_word=full_word;p.domain_for=domain_for
    result=p.probe(spec)
    result['scope']='Exact sparse color-sum/side complete scalar y+=x on arbitrary data, paid orthogonal port permutations and full inverse; all source/sink columns and actual frame-path rank replay. Five-color fitting center is exact. Many-label frame optimization is heuristic; Gaussian phase lifts, residual gauge adapters, native precision and complete multiplier moment remain unproved.'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);parser.add_argument('--rounds',type=int,default=4);parser.add_argument('--frames',type=int,default=192)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    specs=[(7,kind+'-'+layout,args.frames,args.rounds,2026100901+i)
           for i,(kind,layout) in enumerate([('sum','batched'),('sum','interleaved'),('side','batched'),('side','interleaved')])]
    paths=[Path(__file__),Path(p.__file__),Path(p.f.__file__),Path(p.f.__file__).with_name('lagrangian_graph_completion.py'),
           Path(p.f.__file__).with_name('trimmed_zeta_dirty_probe.py'),p.f.SIDE_SOURCE]+[
           p.COMPLEX/name for name in ('center_basis_scalar_word.py','structured_center_basis.py','center_null_basis.py')]
    hashes={path:sha256(path.read_bytes()).hexdigest() for path in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,specs=specs,
                  source_sha256={path.name:digest for path,digest in hashes.items()},
                  optimizer='Exact binary alpha moves, bounded many-label strict/plateau discovery',
                  hypothesis='Five shared color centers rather than 21 separately materialized self cancellations; noncoordinate/radical parity hyperplanes explicitly eligible.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');controls=p.f.binary_controls();cases=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({key:result[key] for key in ('status','h','deficit','rank_charge','capacity','seconds')}),flush=True)
    if any(sha256(path.read_bytes()).hexdigest()!=digest for path,digest in hashes.items()):raise ValueError('Effective source changed during experiment')
    (args.output/'certificate.json').write_text(json.dumps(dict(controls=controls,cases=cases),indent=2,default=str)+'\n')


if __name__=='__main__':main()
