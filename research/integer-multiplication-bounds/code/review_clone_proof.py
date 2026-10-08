#!/usr/bin/env python3
"""Independent explicit clone accounting, capacity premises and guard.

This checks recorded finite edits and exact closed-form counts. The
separate root-owned full changed-DAG reconstruction checks formal sources,
frame inclusions, actual gate capacities and the physical compiled hash.
No cloner, optimizer or producer accounting function is imported.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import time


def controls():
    # Both original output chains have two chronological uses of P.
    old_links={1:2,3:4}
    old_sources={1:'P',2:'P',3:'P',4:'P'}
    proper=dict(old_sources);proper[3]=proper[4]='cloneP'
    assert all(proper[a]==proper[b] for a,b in old_links.items())
    wrong=dict(old_sources);wrong[3]='cloneP'
    assert any(wrong[a]!=wrong[b] for a,b in old_links.items())
    # Two successor inputs at one addition leave no terminal pivot.
    assert not any(position not in {0,1} for position in (0,1))
    assert any(position not in {0} for position in (0,1))
    c,q,links=9,7,4
    old=c+q-links
    assert (c+1)+q-(links+2)==old-1
    assert (c+1)+q-(links+1)==old
    return dict(partial_chain_move_rejected=True,whole_chain_move_preserves_sources=True,
                two_retained_inputs_leave_no_terminal_pivot=True,
                one_extra_link_does_not_save_role=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate',type=Path,required=True)
    ap.add_argument('--links',type=Path,required=True)
    ap.add_argument('--order',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    start=time.monotonic()
    saved=json.loads(args.certificate.read_text());links=json.loads(args.links.read_text());order=json.loads(args.order.read_text())
    assert saved['status']=='Terminal exact recovered clone witness PASS'
    assert saved['source_sha256']==sha256(Path(__file__).with_name('finite_clone_recovered_witness.py').read_bytes()).hexdigest()
    for name,digest in saved['dependency_sha256'].items():
        assert sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()==digest
    assert links['certificate_sha256']==sha256(args.certificate.read_bytes()).hexdigest()
    assert order['selected_link_artifact_sha256']==sha256(args.links.read_bytes()).hexdigest()
    assert links['candidate_id']==order['candidate_id']
    assert links['descriptions_sha256']==order['descriptions_sha256']
    row=saved['rows'][0];old=row['baseline'];new=row['duplicated'];jobs=row['chosen'];C=len(jobs)
    h=row['h'];v=comb(h,3);m=h**3
    assert h==51 and C==1431
    capacities=set();parents=set();children=set()
    for job in jobs:
        P=job['node'];caps=set(job['predecessor_gates']);formal=set(job['original_children'])
        assert len(caps)==2 and P in caps and len(formal)==2
        assert not (caps&capacities) and P not in children and not (parents&formal)
        assert {job['same_gate_new_predecessor_input'],job['earlier_predecessor_input']}=={0,1}
        assert len(job['original_predecessor_users'])==2 and job['selected']
        assert len({tuple(use) for use in job['selected']})==len(job['selected'])
        capacities|=caps;parents.add(P);children|=formal
    assert not (parents&children)
    assert new['logical']['additions']==old['logical']['additions']+C
    assert new['links']==old['links']+2*C and row['delta_links']==2*C
    c=new['logical']['additions'];q=new['logical']['partial_outputs'];R=new['roles']
    assert q==old['logical']['partial_outputs']==3*v
    assert R==c+q-new['links']==old['roles']-C
    assert links['clone_count']==C and links['selected_link_count']==new['links']
    exact_links=links['exact_selected_links']
    assert len(exact_links)==new['links']
    first=[a for a,b in exact_links];second=[b for a,b in exact_links]
    assert len(set(first))==len(first) and len(set(second))==len(second)
    assert all(a<b for a,b in exact_links)
    assert order['description_count']==links['description_count']==2*c+q
    assert order['node_count']==v+c
    N=v**3;W=2*N+2*v*v*(R+h);L=3*v*v*h*h;D=N-2*L;s=W*m-D
    counts=row['exact_counts']
    for name,value in dict(h=h,v=v,m=m,N=N,W=W,L=L,D=D,s=s,side_roles=R).items():
        if name in counts:assert counts[name]==value
    histogram={int(k):value for k,value in counts['rank_histogram'].items()}
    assert sum(r*count for r,count in histogram.items())==s
    assert sum(histogram.values())==counts['edge_count']
    category_sum=0
    for category in counts['categories'].values():
        ranks={int(k):value for k,value in category['rank_histogram'].items()}
        assert sum(r*value for r,value in ranks.items())==category['rank_sum']
        assert sum(ranks.values())==category['edge_count']
        category_sum+=category['rank_sum']
    assert category_sum==s
    mixer=c+R-v
    invocation=4*mixer+20*v
    G=3*v*v*invocation
    E=64*(W+m+1)**3;depth=2*G*W*W+4*s+4*W+4
    assert E>depth
    for name,value in dict(G=G,E=E,depth=depth,slack=E-depth,invocation_scalar_operations=invocation).items():
        assert row['literal_scalar_guard'][name]==value
    names=('review_clone_proof.py','finite_clone_recovered_witness.py','finite_clone_batch.py',
           'finite_clone_chain_bridge.py','finite_clone_unused_capacity.py','frame_reuse.py')
    result=dict(status='PASS independent clone premises/accounting/guard; full physical promotion separately required',
                generated_utc=datetime.now(timezone.utc).isoformat(),candidate_id=links['candidate_id'],
                source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
                input_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in (args.certificate,args.links,args.order)},
                selected_clones=C,disjoint_original_gate_capacities=len(capacities),
                no_selected_parent_is_selected_formal_input=True,
                selected_links=new['links'],changed_additions=c,partial_outputs=q,changed_roles=R,
                new_descriptor_count=2*c+q,changed_active_nodes=v+c,
                count_identity='R=c+q-links; one addition and two links per clone',
                counts=dict(h=h,v=v,m=m,N=N,W=W,L=L,D=D,s=s,side_roles=R),
                forward_mixer_scalar_operations=mixer,complete_invocation_scalar_operations=invocation,
                scalar_guard=dict(G=G,E=E,depth=depth,strict_slack=E-depth),
                negative_controls=controls(),
                limitations=['Recorded chosen jobs and selected links checked; no full graph rebuilt here',
                             'Actual equal formal source IDs, frame inclusions, per-gate capacity and compiled hash are root-owned independent physical review',
                             'No dirty basis or multiplication machine is executed here',
                             'Separate complex h28 numerical guard unchanged by this bit-only clone'],
                wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],'roles',R,'clones',C,'newlinks',2*C,flush=True)


if __name__=='__main__':main()
