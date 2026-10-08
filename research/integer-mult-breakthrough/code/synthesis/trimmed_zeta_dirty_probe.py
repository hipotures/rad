#!/usr/bin/env python3
"""Dirty SSA realization and a monotone L_E audit of trimmed odd-side DAGs.

Four mixer passes reuse one physical SSA stock. Exact scalar echo removes
all arbitrary dirty columns. The L_E audit permits every binary support
subspace, including radicals, but retains monotone common-frame unions.
Its output descent charges must not be mistaken for a general phase bound.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import time

from lagrangian_graph_completion import basis,intersection

SIDE_SOURCE=Path(__file__).resolve().parents[1]/'obstructions'/'trimmed_side_transform.py'
spec=importlib.util.spec_from_file_location('trimmed_side_reference',SIDE_SOURCE)
side=importlib.util.module_from_spec(spec);spec.loader.exec_module(side)


def mixer_edges(dag):
    edges=[]
    for role,node in enumerate(dag['nodes']):
        if node[0]=='input':continue
        if node[0]=='add':edges.extend(((role,node[1],Q(1)),(role,node[2],Q(1))))
        else:edges.append((role,node[1],Q(node[2],node[3])))
    return edges


def dirty_scalar(dag,negative=None):
    h,k=dag['h'],dag['k'];v=len(dag['top']);r=len(dag['nodes']);w=2*v+r
    x=list(range(v));y=list(range(v,2*v));aux=list(range(2*v,w));edges=mixer_edges(dag)
    rows=[{i:Q(1)} for i in range(w)]
    def add(dest,source,c):
        for column,value in rows[source].items():
            new=rows[dest].get(column,Q())+c*value
            if new:rows[dest][column]=new
            else:rows[dest].pop(column,None)
    def mix(reverse=False):
        for dest,source,c in reversed(edges) if reverse else edges:
            add(aux[dest],aux[source],-c if reverse else c)
    def scatter(c):
        for j,node in enumerate(dag['outputs']):
            if node>=0:add(y[j],aux[node],c)
    mix();scatter(Q(1) if negative=='wrong first echo sign' else Q(-1));mix(True)
    for j in range(v):add(aux[j],x[j],Q(1))
    mix();scatter(Q(1));mix(True)
    if negative!='omit source subtraction':
        for j in range(v):add(aux[j],x[j],Q(-1))
    expected=[{i:Q(1)} for i in range(w)]
    for target,T in enumerate(dag['top']):
        for source,U in enumerate(dag['top']):
            coefficient=side.side_value(k,(T&U).bit_count())
            if coefficient:expected[y[target]][source]=coefficient
    differing=[i for i in range(w) if rows[i]!=expected[i]]
    witness=None
    if differing:
        role=differing[0]
        column=next(c for c in sorted(set(rows[role])|set(expected[role]))
                    if rows[role].get(c,Q())!=expected[role].get(c,Q()))
        witness=dict(scalar_output_slot=role,single_nonzero_initial_column=column,
                     expected_value=str(expected[role].get(column,Q())),
                     corrupted_value=str(rows[role].get(column,Q())))
    if negative is None and differing:raise ValueError('Complete arbitrary-dirty scalar replay failed')
    if negative is not None and not differing:raise ValueError('Matched dirty scalar corruption was not detected')
    return dict(h=h,k=k,scalar_payload_slots=w,source_columns=v,sink_columns=v,arbitrary_dirty_columns=r,
                invertible_shear_edges_per_mixer=len(edges),four_mixer_passes_reuse_one_SSA_stock=True,
                paid_scalar_shears=4*len(edges)+4*v,negative=negative,differing_rows=differing,
                exact_single_payload_counterexample=witness,
                all_dirty_and_source_columns_restored=negative is None,
                scope='Exact characteristic-zero scalar map only. No Gaussian address frame/phase word or recursive cost is asserted.')


def le_audit(dag):
    h,k=dag['h'],dag['k'];v=len(dag['top']);r=len(dag['nodes']);w=2*v+r
    if len(set(dag['outputs']))!=v or any(n<0 for n in dag['outputs']):
        raise ValueError('Declared compiler requires distinct nonzero side outputs')
    full=tuple(1<<j for j in range(h));frames=[() for _ in range(r)];ranks=Counter()
    for j,T in enumerate(dag['top']):frames[j]=(T,);ranks[1]+=1
    def grow(role,new):
        delta=len(new)-len(frames[role])
        if delta<0:raise ValueError('Middle mixer is not monotone in this audit')
        if delta:ranks[delta]+=1
        frames[role]=new
    for dest,source,_ in mixer_edges(dag):
        if frames[dest]==frames[source]:continue
        if len(frames[dest])==h or len(frames[source])==h:common=full
        else:common=basis(frames[dest]+frames[source],h)
        grow(dest,common);grow(source,common)
    outputs=[];descents=0
    for T,node in zip(dag['top'],dag['outputs']):
        old=frames[node]
        # Kernel of dot(T,-), constructed without requiring nondegenerate
        # restriction to the kernel or any intermediate subspace.
        pivot=(T&-T).bit_length()-1
        kernel=basis(tuple((1<<j)^((1<<pivot) if T>>j&1 else 0)
                           for j in range(h) if j!=pivot),h)
        common=intersection(old,kernel,h);drop=len(old)-len(common)
        if not drop or len(basis(old+(T,),h))!=len(old):
            raise ValueError('Top identity route did not retain its nonorthogonal self label')
        charge=len(old)+len(kernel)-2*len(common)
        if charge:ranks[charge]+=1
        frames[node]=kernel;descents+=drop
        outputs.append((len(old),drop))
    for j in range(r):grow(j,full)
    # Source and destination boundary completion, each rank h-1.
    ranks[h-1]+=2*v
    mass=sum(a*b for a,b in ranks.items());capacity=w*h
    if mass!=capacity-2*v+2*descents:
        raise ValueError('Complete L_E rank telescope does not match chronology')
    if descents<v or mass<capacity:
        raise ValueError('This monotone identity-route compiler falsely claims a deficit')
    return dict(h=h,k=k,vertices=v,SSA_auxiliary_roles=r,complete_stock=w,
                SSA_roles_per_vertex=str(Q(r,v)),histogram=dict(sorted(ranks.items())),rank_mass=mass,capacity=capacity,
                output_frame_rank_and_drop_histogram={str(key):outputs.count(key) for key in sorted(set(outputs))},
                output_descent_total=descents,minimum_identity_route_descent=v,
                deficit=capacity-mass,all_support_subspaces_including_radicals_allowed=True,
                self_label_containment_checked_for_every_output=True,
                same_width_calls=ranks.get(h,0),same_width_stock_ratio=str(Q(ranks.get(h,0),w)),
                scope='Exact complete local rank ledger for this retained-SSA monotone-union L_E compiler. Arbitrary nonmonotone Lagrangian gate choices, rewired identity cancellation or changed endpoints are outside this negative.')


def probe(spec):
    kind,h,k=spec;dag=side.build_dag(h,k);result=dict(kind=kind,scalar_cost=side.cost_record(dag),L_E_audit=le_audit(dag))
    if kind=='full':result['arbitrary_dirty_scalar_replays']=[dirty_scalar(dag,n) for n in (None,'wrong first echo sign','omit source subtraction')]
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--workers',type=int,default=4);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(__file__).with_name('lagrangian_graph_completion.py'),SIDE_SOURCE]
    initial_hashes={str(p):sha256(p.read_bytes()).hexdigest() for p in sources}
    specs=[('full',8,5),('full',9,5),('frames',20,5),('frames',24,5)]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,seed=None,
                  specs=specs,source_sha256={p.name:initial_hashes[str(p)] for p in sources})
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');receipts=[];start=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();receipts.append(result)
            a=result['L_E_audit']
            print(json.dumps(dict(h=a['h'],k=a['k'],kind=result['kind'],deficit=a['deficit'],output_descents=a['output_descent_total'],status='EXACT DIRTY SCALAR AND MONOTONE L_E NEGATIVE PASS',seconds=time.monotonic()-start)),flush=True)
    if any(sha256(p.read_bytes()).hexdigest()!=initial_hashes[str(p)] for p in sources):
        raise ValueError('An effective source changed during the run')
    certificate=dict(status='EXACT DIRTY SCALAR AND MONOTONE L_E NEGATIVE PASS',cases=receipts,
                     seconds=time.monotonic()-start,
                     interpretation='Four scalar mixer passes reuse one SSA stock, so cost is not four times R. Monotone L_E framing preserves each top self label until final cancellation; its output decreases spend the endpoint rank saving. Changed nonmonotone compiler/chronology remains open.')
    (args.output/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')


if __name__=='__main__':main()
