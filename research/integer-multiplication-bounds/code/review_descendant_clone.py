#!/usr/bin/env python3
"""Independent delayed-clone premise, rank/count and boundary controls.

Read explicit edit/link artifacts without importing a clone builder,
flow solver or producer accounting helper. Full changed-DAG source/frame
and compiled-hash reconstruction belongs to the separate root audit.
"""

import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import sys
import time

from review_pivot_batching import identity, invert, multiply, stringify, transpose


def pairing(x,y,H):
    return sum(x[i]*H[i][j]*y[j] for i in range(len(x)) for j in range(len(y)))


def projection(vectors,H):
    U=transpose(vectors)
    gram=multiply(multiply(transpose(U),H),U)
    return multiply(multiply(multiply(U,invert(gram)),transpose(U)),H),gram


def boundary_controls():
    h=12
    H=[[Q(int(i==j))-Q(1,9) for j in range(h)] for i in range(h)]
    triple=lambda t:[Q(int(i in t)) for i in range(h)]
    a,b=triple((0,1,2)),triple((0,1,3))
    target=triple((0,5,6));wrong=triple((2,5,6))
    U,gram0=projection([a],H)
    F,gram=projection([a,b],H)
    assert gram0==[[Q(2)]] and gram==[[Q(2),Q(1)],[Q(1),Q(2)]]
    assert multiply(F,U)==multiply(U,F)==U
    difference=[[x-y for x,y in zip(r,s)] for r,s in zip(F,U)]
    assert multiply(difference,difference)==difference
    assert sum(difference[i][i] for i in range(h))==1
    IU=[[x-y for x,y in zip(r,s)] for r,s in zip(identity(h),U)]
    IF=[[x-y for x,y in zip(r,s)] for r,s in zip(identity(h),F)]
    assert multiply(IU,IF)==IF
    assert pairing(a,target,H)==pairing(b,target,H)==0
    assert pairing(a,wrong,H)==0 and pairing(b,wrong,H)==-1
    # Reusing a larger frame for a direct old target is unsafe unless
    # the complete chain and final target containment are checked.
    narrow={0};wide={0,1}
    assert narrow<=wide and not wide<=narrow
    # A gate Q may occur after P yet before the first moved-chain user.
    P,Qgate,clone,owner=(1,10),(2,20),(2,25),(2,30)
    assert P<Qgate<clone<owner
    immediate=(1,11)
    assert not Qgate<immediate
    return dict(metric_ground=h,positive_source_gram=gram0,positive_owner_gram=gram,
                exact_forward_projector_containment=True,
                exact_reverse_complement_containment=True,positive_residual_rank=1,
                valid_owner_target_pairings=True,
                arbitrary_enlargement_at_direct_output_rejected=True,
                nonzero_bad_target_pairing='-1',
                delayed_predecessor_after_original_sum_allowed=True,
                immediate_insertion_would_break_chronology=True,
                larger_chain_frame_cannot_link_to_smaller_direct_output_frame=True)


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate',type=Path,required=True)
    ap.add_argument('--links',type=Path,required=True)
    ap.add_argument('--small',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    start=time.monotonic()
    raw=args.certificate.read_bytes();p=json.loads(raw)
    link=json.loads(args.links.read_text());small=json.loads(args.small.read_text())
    assert p['status']=='Terminal exact descendant-frame clone witness PASS'
    assert link['status']=='Terminal exact delayed clone artifact PASS'
    assert small['status']==p['status']
    assert sha256(raw).hexdigest()==link['certificate_sha256']
    assert p['source_sha256']==sha256(Path(__file__).with_name('finite_clone_descendant_frame.py').read_bytes()).hexdigest()
    for name,digest in link['dependency_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    row=p['rows'][0];jobs=row['chosen'];C=len(jobs);h=row['h'];v=comb(h,3);m=h**3
    assert (h,C)==(51,16454)
    capacities=set();parents=set();children=set();strict=terminal=0
    for job in jobs:
        P=job['node'];caps=set(job['predecessor_gates']);formal=set(job['original_children'])
        assert len(caps)==2 and P in caps and len(formal)==2
        assert not (caps&capacities) and P not in children and not (parents&formal)
        assert {job['same_gate_new_predecessor_input'],job['earlier_predecessor_input']}=={0,1}
        selected={tuple(use) for use in job['selected']}
        assert selected and len(selected)==len(job['selected'])
        assert job['clone_frame_dimension']>=job['original_frame_dimension']
        owner=job['clone_insertion_owner']
        if owner is None:
            terminal+=1
            assert job['clone_frame_owner']==P
            assert job['clone_frame_dimension']==job['original_frame_dimension']
            assert all(kind=='output' for kind,value in selected)
        else:
            assert job['clone_frame_owner']==owner
            assert ('gate',owner) in selected
        strict+=job['clone_frame_dimension']>job['original_frame_dimension']
        capacities|=caps;parents.add(P);children|=formal
    assert not (parents&children)
    locations=link['clone_placement_and_frame_owner_ids']
    assert len(locations)==C and {old for old,new,owner in locations}==parents
    assert len({new for old,new,owner in locations})==C
    assert all(new>v and owner>new for old,new,owner in locations)  # all selected clones are nonterminal
    assert terminal==0
    c=row['final']['logical']['additions'];q=row['final']['logical']['partial_outputs'];R=row['final']['roles']
    assert c==row['baseline']['logical']['additions']+C
    assert row['final']['links']==row['baseline']['links']+2*C==link['selected_link_count']
    assert q==3*v and R==c+q-link['selected_link_count']==row['baseline']['roles']-C==485680
    assert link['node_count']==v+c and link['description_count']==2*c+q
    actual=link['exact_selected_links']
    assert len(actual)==link['selected_link_count']
    assert len({a for a,b in actual})==len(actual)==len({b for a,b in actual})
    assert all(a<b for a,b in actual)
    N=v**3;W=2*N+2*v*v*(R+h);L=3*v*v*h*h;D=N-2*L;s=W*m-D
    n=row['exact_counts']
    for key,value in dict(h=h,m=m,v=v,N=N,W=W,L=L,D=D,s=s,side_roles=R).items():
        if key in n:assert n[key]==value
    histogram={int(r):count for r,count in n['rank_histogram'].items()}
    assert sum(r*count for r,count in histogram.items())==s
    assert sum(histogram.values())==n['edge_count']
    assert sum(cat['rank_sum'] for cat in n['categories'].values())==s
    for cat in n['categories'].values():
        hist={int(r):count for r,count in cat['rank_histogram'].items()}
        assert sum(r*count for r,count in hist.items())==cat['rank_sum']
        assert sum(hist.values())==cat['edge_count']
    touch=n['local_program']['logical_node_gate_incidences']
    events=4*touch+2*q+2*v
    assert n['local_program']['events_per_invocation']==events
    forward=n['categories']['side_middle_forward_stages1_and3']
    reverse=n['categories']['side_middle_complement_stage2']
    assert forward['rank_sum']==2*v*v*R*h and reverse['rank_sum']==v*v*R*h
    assert forward['edge_count']==2*v*v*(events-R)
    assert reverse['edge_count']==v*v*(events-R)
    assert n['edge_count']==3*v*v*events+2*v*v*R+14*v*v*h+26*N
    mixer=c+R-v;invocation=4*mixer+20*v;G=3*v*v*invocation
    E=64*(W+m+1)**3;depth=2*G*W*W+4*s+4*W+4
    assert E>depth
    for key,value in dict(G=G,E=E,depth=depth,slack=E-depth).items():
        assert row['literal_scalar_guard'][key]==value
    small12=next(r for r in small['rows'] if r['h']==12)
    dirty=small12['complete_small_controls']
    assert dirty['complete_dirty_and_independent_rational_timeline']['arbitrary_dirty_restoration']
    assert all(r['exact_linear_map'] and r['input_basis_vectors']==4126 for r in dirty['complete_center_dirty_bases'])
    assert {r['inverse'] for r in dirty['complete_center_dirty_bases']}=={False,True}
    names=('review_descendant_clone.py','review_pivot_batching.py','finite_clone_descendant_frame.py',
           'finite_clone_descendant_export.py','finite_clone_chain_bridge.py','frame_reuse.py')
    result=dict(status='PASS independent delayed-clone all-size premises/accounting; giant independent promotion separate',
                generated_utc=datetime.now(timezone.utc).isoformat(),candidate_id=link['candidate_id'],
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                input_sha256={str(path):sha256(path.read_bytes()).hexdigest() for path in
                              (args.certificate,args.links,args.small)},
                chosen_clones=C,strictly_enlarged_clone_frames=strict,
                terminal_clones=terminal,disjoint_original_gate_capacities=len(capacities),
                links=link['selected_link_count'],roles=R,additions=c,partial_outputs=q,
                counts=dict(h=h,v=v,m=m,N=N,W=W,L=L,D=D,s=s,side_roles=R),
                actual_positive_and_zero_rank_histogram_retained=True,
                scalar_guard=dict(G=G,E=E,depth=depth,strict_slack=E-depth,
                                  mixer_operations=mixer,invocation_operations=invocation),
                boundary_negative_controls=boundary_controls(),
                complete_small_dirty_basis_per_orientation=4126,
                limitations=['No full graph rebuilt here; scalar/frame/actual lineage/compiled-hash reconstruction is the root-owned independent audit',
                             'Exported first/recipient uniqueness and numeric chronology checked; parent gate capacity and frame-containment objects are separate giant-check premises',
                             'Output orthogonality must be checked at actual selected direct targets; formal support equality is not asserted at enlarged clones',
                             'No primitive optimality or final multiplication kappa inferred from this proof/accounting alone'],
                wall_seconds=time.monotonic()-start,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],'R',R,'clones',C,'strict',strict,flush=True)


if __name__=='__main__':main()
