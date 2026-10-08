#!/usr/bin/env python3
"""Exact physical edge-rank histogram for the shared bit motif.

This specifies one fixed gate grouping: a compiled node mixer is one
common-frame gate; J/V are grouped by data triple; each central gather or
scatter is one gate on the bank and its h centers. Identity input mixers
are retained. The resulting macro circuit has exactly the same scalar map,
roles, common frames and rank sum. Splitting any such gate adds only zero
residual edges, so it does not change the positive-rank histogram.

No batched-rank tape implementation or improved recurrence is asserted.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import comb,log
from pathlib import Path
import time


def side_middle_histograms(h,circuit,spaces,code):
    R=code['roles'];touches=sum(len(set(ins+outs)) for _,ins,outs in code['gates'])
    v=len(code['sources']);q=len(code['outputs'])
    assert v==comb(h,3) and q==3*v
    forward=Counter();reverse=Counter()
    values=[0]*R
    def transition(hist,role,value):
        difference=value-values[role]
        assert difference>=0,('Nonmonotone physical frame',role,values[role],value)
        hist[difference]+=1;values[role]=value
    # All early mixer and J incidences have common D0. Omit the first
    # incidence on each role: the global source/join category supplies it.
    forward[0]+=2*touches+q-R
    for role in code['sources'].values():transition(forward,role,1)
    for node,ins,outs in code['gates']:
        for role in set(ins+outs):transition(forward,role,spaces[node].dimension)
    for role in code['outputs'].values():transition(forward,role,h-1)
    # Every role participates in cleanup. Its first cleanup incidence
    # grows to D1; the remaining incidences and final V are zero residuals.
    for role in range(R):transition(forward,role,h)
    forward[0]+=touches+v-R
    assert sum(r*n for r,n in forward.items())==R*h
    assert sum(forward.values())==4*touches+2*q+2*v-R
    values=[0]*R
    reverse[0]+=v+touches-R
    # The reversed middle L^{-1} uses complements. Physical target lines
    # enter via the first J; original source complements leave via V.
    for role in code['outputs'].values():transition(reverse,role,1)
    for node,ins,outs in reversed(code['gates']):
        for role in set(ins+outs):transition(reverse,role,h-spaces[node].dimension)
    for role in code['sources'].values():transition(reverse,role,h-1)
    for role in range(R):transition(reverse,role,h)
    reverse[0]+=2*touches+q-R
    assert sum(r*n for r,n in reverse.items())==R*h
    assert sum(reverse.values())==4*touches+2*q+2*v-R
    return forward,reverse,dict(roles=R,logical_node_gate_incidences=touches,
        physical_sources=v,physical_partial_outputs=q,
        events_per_invocation=4*touches+2*q+2*v,
        first_role_incidence_omitted_from_middle=R)


def explicit_side_paths(h,spaces,code):
    """Independent small event replay, including all zero incidences.

    Unlike the aggregate construction this directly executes each of the
    four mixer passes and each source/output event at its chronological
    frame dimension. The shared join starts stage3 at dimension h.
    """
    R=code['roles'];result=Counter();events=0
    for stage in (1,2,3):
        base=(h**(stage-1)-1)*h
        values=[h if stage==3 else 0]*R
        def edge(role,dim):
            nonlocal events
            assert dim>=values[role]
            result[dim-values[role]]+=1;values[role]=dim;events+=1
        def mixer(order,dim):
            for node,ins,outs in order:
                label=base+(dim(node) if callable(dim) else dim)
                for role in set(ins+outs):edge(role,label)
        def source(dim):
            for role in code['sources'].values():edge(role,base+dim)
        def output(dim):
            for role in code['outputs'].values():edge(role,base+dim)
        if stage!=2:
            mixer(code['gates'],0);output(0);mixer(reversed(code['gates']),0)
            source(1);mixer(code['gates'],lambda node:spaces[node].dimension);output(h-1)
            mixer(reversed(code['gates']),h);source(h)
        else:
            source(0);mixer(code['gates'],0);output(1)
            mixer(reversed(code['gates']),lambda node:h-spaces[node].dimension);source(h-1)
            mixer(code['gates'],h);output(h);mixer(reversed(code['gates']),h)
        assert all(value==h**stage for value in values)
        if stage!=1:
            for role in range(R):edge(role,h**3)
    return result,events


def histogram(h,circuit,spaces,code):
    v=comb(h,3);N=v**3;m=h**3;R=code['roles'];W=2*N+2*v*v*(R+h)
    L=3*v*v*h*h;D=N-2*L;s=W*m-D
    forward,reverse,metadata=side_middle_histograms(h,circuit,spaces,code)
    categories={}
    def category(name,counter,multiplicity=1):
        counter=Counter({r:n*multiplicity for r,n in counter.items()})
        assert all(0<=r<=m and n>=0 for r,n in counter.items())
        categories[name]=dict(rank_histogram={str(r):n for r,n in sorted(counter.items())},
            edge_count=sum(counter.values()),rank_sum=sum(r*n for r,n in counter.items()),
            stated_multiplicity=multiplicity)
    category('side_middle_forward_stages1_and3',forward,2*v*v)
    category('side_middle_complement_stage2',reverse,v*v)
    # Each shared first/third role has initial edge0, one join m-2h,
    # and final edge0. Each middle-bank role has source h^2-h and final
    # m-h^2. The stage3 first-incidence edge IS the join, not an extra edge.
    boundary=Counter({0:2*R,m-2*h:R,h*h-h:R,m-h*h:R})
    category('side_sources_shared_stage_join_and_sinks',boundary,v*v)
    centers=Counter({0:2*h,m-2*h:h,h*h-h:h,m-h*h:h,h:9*h})
    category('centers_all_sources_three_returns_stage_join_and_sinks',centers,v*v)
    # Physical data matrices continue between stages. The inverse middle
    # invocation exchanges logical banks but retains these physical frames.
    for stage in (1,2,3):
        a=h**(stage-1)
        first=(a-1)*(h-1)
        x=Counter([1 if stage==1 else first,h-1,0,0])
        y=Counter([first,0,0,h-1])
        category('data_X_stage'+str(stage),x,N)
        category('data_Y_stage'+str(stage),y,N)
    category('data_sinks',Counter({0:2}),N)
    category('additional_identity_padding',Counter({0:0,m:0}))
    total=Counter()
    for item in categories.values():
        total.update({int(r):n for r,n in item['rank_histogram'].items()})
    total.setdefault(0,0);total.setdefault(m,0)
    assert sum(r*n for r,n in total.items())==s
    expected_edges=3*v*v*metadata['events_per_invocation']+2*v*v*R+14*v*v*h+26*N
    assert sum(total.values())==expected_edges
    assert sum(item['rank_sum'] for item in categories.values())==s
    explicit=None
    if h<=12:
        paths,events=explicit_side_paths(h,spaces,code)
        aggregate=Counter()
        for name in ('side_middle_forward_stages1_and3','side_middle_complement_stage2',
                     'side_sources_shared_stage_join_and_sinks'):
            aggregate.update({int(r):n//(v*v) for r,n in categories[name]['rank_histogram'].items()})
        assert paths==aggregate,('Explicit physical path histogram differs',paths,aggregate)
        assert events==sum(aggregate.values())
        explicit=dict(all_side_event_paths_replayed=True,edge_events=events,
            same_zero_and_positive_histogram=True,scope='Small chronological all-physical-role dimension replay, independent of aggregate zero-incidence formulas')
    # Floating exploration only, useful for discriminating a prospective
    # batching interface. The current proven recurrence still uses sum r/W.
    normalized_slope=sum(n*(r/m)*log(m/r) for r,n in total.items() if r)
    exploration=dict(scope='Hypothetical one-child rank-r batching; no tape implementation or theorem promotion',
        current_eta=D/(W*m),slope_at_exponent_one=normalized_slope/W,
        first_order_saving_estimate=D/(m*normalized_slope),
        pinned_uniform_shrink_saving_first_order=D/(W*m*log(m)))
    return dict(h=h,m=m,W=W,s=s,D=D,N=N,L=L,side_roles=R,edge_count=expected_edges,
        categories=categories,rank_histogram={str(r):n for r,n in sorted(total.items())},
        rank_sum_regression_exact=True,edge_count_regression_exact=True,
        negative_source_correction='The N stage1 X-source edges have rational matrix2P_U, rank1 despite zero positive-label dimension change',
        zero_and_full_rank_preserved=True,local_program=metadata,exploratory_batched_score=exploration,
        independent_small_event_replay=explicit,
        boundary_provenance='Shared first/third join E subset H has dimensions h and m-h; middle bank endpoints0/I; data negative source and complementary sink unchanged')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference',required=True)
    ap.add_argument('--h',type=int,nargs='+',default=[6,8,12,50])
    ap.add_argument('--base',type=int,default=4)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    from finite_block_search import install_reference,GroupUnion
    install_reference(args.reference)
    from finite_singleton_search import singleton_class
    from fast_frame_envelope import labels
    from frame_envelope import target_check
    from frame_reuse import optimize_chains,compile_reuse,check,included
    cls=singleton_class();rows=[];start=time.monotonic()
    for h in args.h:
        positions=([0]*6+[23]*26+[0]*18) if h==50 else [0]*(h//2-1)+[h//2-2]*(h//2+1)
        circuit=GroupUnion(h,lambda n,c:cls(n,positions[c],args.base),'paired',0,True)
        original=circuit.verify();spaces,metadata=labels(circuit,True)
        plan=optimize_chains(circuit,spaces,'rank');code=compile_reuse(circuit,spaces,plan)
        checked=check(circuit,spaces,code);targets=target_check(circuit,spaces,True)
        row=histogram(h,circuit,spaces,code)
        row.update(original=original,finite_checks=checked,frames=metadata,targets=targets,base=args.base,positions=positions)
        rows.append(row);included.cache_clear();GroupUnion.support_in.cache_clear()
        print(json.dumps(dict(h=h,roles=code['roles'],rank_sum=row['s'],edge_count=row['edge_count'],
            first_order_batched_saving=row['exploratory_batched_score']['first_order_saving_estimate'])),flush=True)
    result=dict(status='Terminal exact histogram',source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_dependencies={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in
          ('finite_singleton_search.py','finite_block_search.py','frame_reuse.py','frame_envelope.py','fast_frame_envelope.py')},
        upstream_revision='bcd4ebde8692383539f8a48734e5fbf3a18a32c2',started_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic()-start,rows=rows,
        interface_scope='Exact rational projector edge ranks for the stated finite grouped circuit, unchanged all-role endpoints; batching remains prospective')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
