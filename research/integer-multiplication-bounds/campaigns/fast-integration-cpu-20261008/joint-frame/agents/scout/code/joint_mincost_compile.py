#!/usr/bin/env python3
"""Componentwise weighted joint-frame matroid augmentation and full review.

Weights are certified integer bins of actual fixed-I+J frame-profile moment
changes. They model the complete fixed-cardinality controller before paid
reclamation. Reclamation is nonlinear; only the independently replayed full
word and complete characteristic can accept its final result. This is a
finite search, with no global optimum claim for the reclaimed compiler.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import subprocess
import sys
import time

from check_joint_moment import logarithm
from joint_match_components import load_source,components


def reduce_basis(rows):
    basis={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p not in basis:basis[p]=row;break
            row^=basis[p]
    return basis


def reduce_vector(row,basis):
    for p in sorted(basis,reverse=True):
        if row>>p&1:row^=basis[p]
    return row


def mincost_component(group,edges,blocks,weights):
    """Shortest weighted augmenting paths, with linear/partition oracles."""
    n=len(group);quotients=[];uses=[];owners=[]
    for e in group:
        g,u,i=edges[e]
        quotients.append(reduce_vector(1<<i,reduce_basis(blocks[g]['outbasis'])))
        assert quotients[-1]
        uses.append(u);owners.append(g)
    local_weights=[weights[e] for e in group];valid_cache={0:True}
    def linear(mask):
        if mask in valid_cache:return valid_cache[mask]
        bases={};rest=mask
        while rest:
            bit=rest&-rest;rest^=bit;i=bit.bit_length()-1
            basis=bases.setdefault(owners[i],{});row=quotients[i]
            while row:
                p=row.bit_length()-1
                if p not in basis:basis[p]=row;break
                row^=basis[p]
            if not row:valid_cache[mask]=False;return False
        valid_cache[mask]=True;return True
    def partition(mask):
        seen=set();rest=mask
        while rest:
            bit=rest&-rest;rest^=bit;i=bit.bit_length()-1
            if uses[i] in seen:return False
            seen.add(uses[i])
        return True
    mask=0;costs=[0];source=n;sink=n+1
    while True:
        chosen=[i for i in range(n) if mask>>i&1]
        outside=[i for i in range(n) if not(mask>>i&1)]
        occupied={uses[i]:i for i in chosen};arcs=[]
        for x in outside:
            if linear(mask|(1<<x)):arcs.append((source,x,local_weights[x]))
            if uses[x] not in occupied:
                arcs.append((x,sink,0))
                for y in chosen:arcs.append((x,y,-local_weights[y]))
            else:arcs.append((x,occupied[uses[x]],-local_weights[occupied[uses[x]]]))
        for y in chosen:
            for x in outside:
                if linear((mask^(1<<y))|(1<<x)):arcs.append((y,x,local_weights[x]))
        distance=[None]*(n+2);distance[source]=(0,0);pred=[None]*(n+2)
        for iteration in range(n+2):
            changed=False
            for a,b,w in arcs:
                if distance[a] is None:continue
                proposal=(distance[a][0]+w,distance[a][1]+1)
                if distance[b] is None or proposal<distance[b]:
                    distance[b]=proposal;pred[b]=a;changed=True
            if not changed:break
        else:raise AssertionError('Negative exchange cycle in weighted augmentation')
        if distance[sink] is None:break
        path=[];node=pred[sink];visited=set()
        while node!=source:
            assert node is not None and node not in visited
            visited.add(node);path.append(node);node=pred[node]
        new=mask
        for node in path:new^=1<<node
        assert new.bit_count()==mask.bit_count()+1 and linear(new) and partition(new)
        value=sum(local_weights[i] for i in range(n) if new>>i&1)
        assert value==costs[-1]+distance[sink][0]
        mask=new;costs.append(value)
    # Exhaust every feasible set in bounded components; no sampled optimizer
    # test is substituted for these complete finite small-component checks.
    exhaustive=False
    if n<=12:
        best={}
        for candidate in range(1<<n):
            if not partition(candidate) or not linear(candidate):continue
            degree=candidate.bit_count();cost=sum(local_weights[i] for i in range(n) if candidate>>i&1)
            if degree not in best or cost<best[degree]:best[degree]=cost
        assert max(best)==mask.bit_count() and all(best[k]==value for k,value in enumerate(costs))
        exhaustive=True
    return {group[i] for i in range(n) if mask>>i&1},dict(edges=n,cardinality=mask.bit_count(),
        weighted_cost=costs[-1],every_cardinality_small_component_exhausted=exhaustive)


def moment_weights(cost_table,h,saving):
    scale=10**24;m=575
    intervals={}
    for t in range(1,h+1):
        lo,hi=logarithm(F(m,t));x,y=saving*lo,saving*hi
        low=sum((x**j/F(factorial(j)) for j in range(13)),F())
        high=sum((y**j/F(factorial(j)) for j in range(13)),F())+y**13/F(factorial(13))/(1-y/14)
        intervals[t]=(t*low,t*high)
    result={}
    for line in cost_table.read_text().splitlines():
        row=json.loads(line);lo,hi=F(),F()
        assert len(row['blocks'])==h+1
        for t,n in enumerate(row['blocks']):
            if n:lo+=n*intervals[t][0];hi+=n*intervals[t][1]
        result[row['a'],row['b']]=(lo,hi)
    return result,scale


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['source_root','costs','cost_protocol','output','binary','other_profile','other_physical']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    ap.add_argument('--h',required=True,type=int,choices=[23,25])
    ap.add_argument('--saving',type=F,default=F(2382370177,5*10**13))
    ap.add_argument('--reclaim',choices=['none','ordinary','high-rank'],default='high-rank')
    ap.add_argument('--objective',choices=['min','max'],default='min')
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();compiler=load_source(args.source_root.resolve())
    cost,scale=moment_weights(args.costs,args.h,args.saving)
    protocol=json.loads(args.cost_protocol.read_text());assert protocol['h']==args.h
    # A reproducible in-memory patch only changes retirement priority. Its
    # exact text is preserved in the execution area and base/wrapper are pinned.
    raw=(args.source_root/'scripts/experiments/binary_frame_compiler.py').read_text()
    variant=raw
    if args.reclaim=='high-rank':
        old='for s in sorted(retired):';assert raw.count(old)==1
        variant=raw.replace(old,"for s in sorted(retired,key=lambda s: (-blocks[frames[s]]['rank'],s)):")
        exec(compile(variant,str(args.output/'variant_compiler.py'),'exec'),compiler.__dict__)
    (args.output/'variant_compiler.py').write_text(variant)
    compiler.graph=sys.modules['joint_dual_compiler'].producer.graph
    original_match=compiler.match;selection={};selected_stream=[];summaries=[]
    def weighted_match(blocks,uses,enabled):
        assert enabled
        baseline_edges,baseline_chosen,baseline_right,baseline_stats=original_match(blocks,uses,True)
        for b in blocks:b['selected'].clear()
        edges,groups=components(blocks,uses);assert edges==baseline_edges
        assert protocol.get('model_version')==2
        owner={node:g for g,b in enumerate(blocks) for node in b['nodes']}
        identity=('\n'.join('%d %d %d'%edge for edge in edges)+'\n').encode()
        assert sha256(identity).hexdigest()==protocol['edge_stream_sha256']
        weights=[];intervals=[]
        for g,u,i in edges:
            value,target,_=uses[u];origin=owner[value]
            pos=cost[g+2,target+2];minus=cost[g+2,1]
            born=cost[0,origin+2];move=cost[origin+2,target+2]
            lo=scale*(pos[0]-minus[1]-born[1]-move[1]);hi=scale*(pos[1]-minus[0]-born[0]-move[0])
            low=lo.numerator//lo.denominator;high=hi.numerator//hi.denominator
            assert low==high,'Moment bin cannot be certified'
            weights.append(low if args.objective=='min' else -low);intervals.append((lo/scale,hi/scale))
        chosen=set()
        for j,group in enumerate(groups):
            local,receipt=mincost_component(group,edges,blocks,weights)
            chosen.update(local);summaries.append(receipt)
            if j%2000==0:print('components',j,'of',len(groups),flush=True)
        assert len(chosen)==len(baseline_chosen)
        right={}
        for e in chosen:
            g,u,i=edges[e];assert u not in right;right[u]=e;blocks[g]['selected'].add(e)
        assert all(len(reduce_basis(b['outbasis']+[1<<edges[e][2] for e in b['selected']]))==len(b['outbasis'])+len(b['selected']) for b in blocks)
        optimized=sum(weights[e] for e in chosen);base=sum(weights[e] for e in baseline_chosen)
        assert optimized<=base
        selected_stream.extend(dict(edge=e,block=edges[e][0],use=edges[e][1],input_index=edges[e][2]) for e in sorted(chosen))
        selection.update(cardinality=len(chosen),baseline_cardinality=len(baseline_chosen),
            optimized_integer_objective=optimized,baseline_integer_objective=base,
            changed_edges=len(chosen^baseline_chosen),components=len(groups),
            exhaustive_small_components=sum(row['every_cardinality_small_component_exhausted'] for row in summaries),
            complete_moment_integer_bin_scale=scale)
        return edges,chosen,right,Counter(weighted_components=len(groups),matched=len(chosen))
    compiler.match=weighted_match
    result,word=compiler.compile_(args.h,matching=True,reclaim=args.reclaim!='none',dirty=True)
    raw_word=(json.dumps(word,separators=(',',':'))+'\n').encode();(args.output/'word.json').write_bytes(raw_word)
    (args.output/'selected-exact-uses.json').write_text(json.dumps(selected_stream,separators=(',',':'))+'\n')
    receipt=dict(status='WEIGHTED JOINT COMPONENT COMPILE COMPLETE; FULL REVIEW FOLLOWS',
        recorded_utc=datetime.now(timezone.utc).isoformat(),h=args.h,objective=args.objective,
        saving=str(args.saving),reclamation=args.reclaim,selection=selection,compiled=result,
        model_version=2,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        base_compiler_sha256=sha256(raw.encode()).hexdigest(),variant_compiler_sha256=sha256(variant.encode()).hexdigest(),
        scalar_source_sha256=sha256((args.source_root/'references/frame-compiler/pr55/research/skip-suffix/skip_graph.py').read_bytes()).hexdigest(),
        cost_table_sha256=sha256(args.costs.read_bytes()).hexdigest(),cost_protocol_sha256=sha256(args.cost_protocol.read_bytes()).hexdigest(),
        selected_stream_sha256=sha256((args.output/'selected-exact-uses.json').read_bytes()).hexdigest(),
        word_sha256=sha256(raw_word).hexdigest(),seconds=time.monotonic()-start,native_threads=1,
        scope='Exact linear/partition feasibility and small-component exhaustive mincost tests. Certified moment weights model the pre-reclamation controller. Final reclaimed correctness and saving require the separate independent complete-word and profile review; no global reclaimed optimum is claimed.')
    (args.output/'result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (args.output/'component-results.json').write_text(json.dumps(summaries,separators=(',',':'))+'\n')
    base=args.source_root
    command=[sys.executable,'-B',str(Path(__file__).with_name('check_candidate_job.py')),
        '--word',str(args.output/'word.json'),'--h',str(args.h),'--output',str(args.output/'review'),
        '--binary',str(args.binary),'--other-profile',str(args.other_profile),'--other-physical',str(args.other_physical),
        '--inherited-certificate',str(base/'certificates/joint-dual-kappa.json'),
        '--assembly',str(base/'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py')]
    subprocess.run(command,check=True)
    print(json.dumps(dict(status='WEIGHTED JOINT COMPONENT AND COMPLETE REVIEW PASS',h=args.h,
        roles=result['roles'],changed_edges=selection['changed_edges'],seconds=time.monotonic()-start)),flush=True)


if __name__=='__main__':main()
