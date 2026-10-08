#!/usr/bin/env python3
"""Independent compound bit DAG/actual-frame/controller-history promotion.

The original graph uses the independent odd/even builder. A preserved
independent clone reconstructor receives the current actual frames at every
round. No producer cloner, selector, plan exporter or full flow is imported.
Only the new final graph receives coefficient/physical checks. Saved final
links are unrolled to verify every exact capacity and whole-chain edit.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import comb
from itertools import combinations
from pathlib import Path
import resource
import subprocess
import sys
import time
from unittest.mock import patch

import review_descendant_clone_witness as preserved
from fast_frame_envelope import labels
from finite_block_search import install_reference
from frame_reuse import compile_reuse, optimize_chains
from frame_reuse_certificate import program
from review_aligned_graph import check as logical_check
from review_envelopes import target_eligible
from review_frame_reuse import dirty_check
from review_odd_pair_witness import build as odd_build, matching, shared_exchange
from review_singleton_positions import build as even_build, compiled_digest
from review_singleton_witness import physical_coefficients


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def file_digest(path):
    return sha256(path.read_bytes()).hexdigest()


def sequence_digest(rows):
    value=sha256()
    for row in rows:
        value.update(json.dumps(row,separators=(',',':')).encode()+b'\n')
    return value.hexdigest()


def frame_digest(frames,circuit):
    return sequence_digest([node,[frames[node].common,list(frames[node].tags),
        list(frames[node].basis),frames[node].core,frames[node].vertices]]
        for node in sorted(circuit.active))


def even_matching(h):
    triples=list(combinations(range(h),3));indices={t:i for i,t in enumerate(triples)}
    def image(triple,direction):
        occupied={}
        for point in triple:occupied.setdefault(point//2,[]).append(point)
        if len(occupied)==3:
            first=min(occupied)
            result=[x if x//2==first else x^1 for x in triple]
        else:
            full=next(p for p,x in occupied.items() if len(x)==2)
            singleton=next(x[0] for x in occupied.values() if len(x)==1)
            cycle=[p for p in range(h//2) if p!=singleton//2]
            group=cycle[(cycle.index(full)+direction)%len(cycle)]
            result=[2*group,2*group+1,singleton]
        return tuple(sorted(result))
    images=[]
    for triple in triples:
        target=image(triple,1)
        assert len(set(triple)&set(target))==1 and image(target,-1)==triple
        images.append(indices[target])
    assert sorted(images)==list(range(len(triples)))
    return images,dict(h=h,triples=len(triples),intersection_one=True,
        explicit_inverse_and_bijection=True,image_sha256=digest(images))


def logical_identity(circuit):
    value=sha256()
    for node in sorted(circuit.active):
        value.update(json.dumps((node,circuit.args[node],circuit.provenance[node]),separators=(',',':')).encode()+b'\n')
    for (common,target),node in sorted(circuit.outputs.items()):
        value.update(json.dumps((common,target,node),separators=(',',':')).encode()+b'\n')
    return value.hexdigest()


def read_row(path,h=None):
    data=json.loads(path.read_text())
    if 'rows' in data:
        row=next(x for x in data['rows'] if h is None or x['h']==h)
    else:
        row=data
    return data,row


def target_frames(circuit,frames):
    for (_,target),node in circuit.outputs.items():
        mask=sum(1<<i for i in target);frame=frames[node]
        assert target_eligible(frame.core,frame.vertices,mask,circuit.h)
    return len(circuit.outputs)


def reconstruct_round(circuit,frames,edits):
    # The old independent constructor normally constructs canonical base
    # frames. Supply ACTUAL current frames explicitly and locally instead.
    # No prior widened clone is relabeled from its formal core/support.
    def actual_input(_circuit,_global):
        assert _circuit is circuit
        return frames,dict(scope='Literal previous-stage actual positive envelopes; no canonical reconstruction')
    with patch.object(preserved,'labels',actual_input):
        view=preserved.ExplicitDAG(circuit,edits)
    old,new,metadata=preserved.canonical_frames(circuit,view)
    assert old is frames
    assert all(new[mapped] is frames[previous] for previous,mapped in view.parent_map.items())
    for node,clone in view.duplicate_map.items():
        owner=view.edits[node]['clone_frame_owner']
        assert new[clone] is frames[owner]
    assert all(view.parent_map[i]==i for i in range(1,len(circuit.inputs)+1))
    targets=target_frames(view,new)
    return view,new,dict(frame_metadata=metadata,target_frames_checked=targets,
                         old_frames_retained_literally=True,all_input_lines_unchanged=True)


def history(row,parent_row):
    h=row['h'];assert (h,row['base'],row['positions'])==(parent_row['h'],parent_row['base'],parent_row['positions'])
    base=(odd_build if h%2 else even_build)(h,row['base'],row['positions'])
    frames,_=labels(base,True)
    base_identity=logical_identity(base)
    assert base_identity==parent_row['baseline']['circuit_sha256']
    states=[dict(circuit=base,frames=frames,edits=[],expected_roles=parent_row['baseline']['roles'],
        expected_compiled=parent_row['baseline']['compiled_sha256'],expected_logical=base_identity,
        label='base')]
    view,new,metadata=reconstruct_round(base,frames,parent_row['chosen'])
    value=logical_identity(view)
    assert value==parent_row['final']['logical']['circuit_sha256']
    states.append(dict(circuit=view,frames=new,edits=parent_row['chosen'],
        expected_roles=parent_row['compiled_roles'],expected_compiled=parent_row['checked']['compiled_sha256'],
        expected_logical=value,label='initial-multiple-option',metadata=metadata))
    assert row['parent_roles']==parent_row['compiled_roles']
    assert row['parent_roles']-row['compiled_roles']==row['role_saving']
    for item in row['rounds']:
        old=states[-1]
        assert item['old_roles']==old['expected_roles']
        assert item['old_compiled_sha256']==old['expected_compiled']
        assert item['old_logical_sha256']==old['expected_logical']
        if not item['chosen']:
            assert item['new_roles']==old['expected_roles']
            continue
        view,new,metadata=reconstruct_round(old['circuit'],old['frames'],item['chosen'])
        value=logical_identity(view)
        assert value==item['new_logical_sha256']
        assert item['old_roles']-item['new_roles']==len(item['chosen'])
        states.append(dict(circuit=view,frames=new,edits=item['chosen'],
            expected_roles=item['new_roles'],expected_compiled=item['new_compiled_sha256'],
            expected_logical=value,label='successive-'+str(item['round']),metadata=metadata,
            prior_clone_child_statistics=dict(
                chosen_parents_with_previous_cloned_original_child=item['chosen_parents_with_previous_cloned_original_child'],
                chosen_parents_with_previous_clone_child=item['chosen_parents_with_previous_clone_child'],
                borrowed_previous_clone_providers=item['borrowed_previous_clone_providers'])))
    assert states[-1]['expected_roles']==row['compiled_roles']
    assert states[-1]['expected_compiled']==row['final']['checked']['compiled_sha256']
    return states


def validate_edit_batch(old,new,old_plan,new_plan):
    circuit,frames=old['circuit'],old['frames'];view=new['circuit'];edits=new['edits']
    users,records,successor,predecessor,_=old_plan
    new_records=new_plan[1]
    retained={records[user][1] for user in successor}
    parents={job['node'] for job in edits};capacities=set();selected_count=0
    assert len(parents)==len(edits)
    position={node:i for i,node in enumerate(sorted(circuit.active,key=lambda n:(frames[n].dimension,n)))}
    for job in edits:
        node=job['node'];provider=job['predecessor_gates'][1]
        assert job['predecessor_gates'][0]==node and node!=provider
        assert node not in retained and provider not in retained
        assert node not in capacities and provider not in capacities
        capacities.update((node,provider))
        assert not parents.intersection(circuit.args[node])
        assert job['original_children']==list(circuit.args[node])
        a,b=job['same_gate_new_predecessor_input'],job['earlier_predecessor_input']
        assert {a,b}=={0,1}
        first_a,first_b=job['original_predecessor_users']
        assert records[first_a]==(circuit.args[node][a],node,a)
        assert records[first_b][0]==circuit.args[node][b] and records[first_b][1]==provider
        chains=[]
        for first in users[node]:
            if first in predecessor:
                continue
            current=first;chain=[]
            while True:
                _,gate,target=records[current]
                chain.append(('gate',gate) if gate is not None else ('output',target))
                if current not in successor:
                    break
                current=successor[current]
            chains.append((first,chain))
        assert len(chains)>=2
        moved={preserved.nested_tuple(use) for use in job['selected']}
        chosen=[pair for pair in chains if set(pair[1])==moved]
        assert len(chosen)==1
        first,chain=chosen[0]
        if 'chain_first_user' in job:
            assert job['chain_first_user']==first
        owner=job['clone_insertion_owner'];frame_owner=job['clone_frame_owner']
        kind,target=chain[0]
        assert (owner is None and kind=='output' and frame_owner==node) or (kind=='gate' and owner==frame_owner==target)
        if owner is not None:
            assert position[node]<position[owner] and position[provider]<position[owner]
        clone=view.duplicate_map[node]
        assert new['frames'][clone] is frames[frame_owner]
        # The unchanged independent frame check verifies actual containment,
        # while final native timelines verify every physical source/target.
        for previous in (node,provider,*circuit.args[node]):
            F,G=frames[previous],frames[frame_owner]
            assert not F.vertices&~G.vertices and not G.core&~F.core
        assert frames[node].dimension==job['original_frame_dimension']
        assert frames[frame_owner].dimension==job['clone_frame_dimension']
        selected_count+=len(chain)
    assert len(capacities)==2*len(edits)
    assert len(new_records)==len(records)+2*len(edits)
    assert len(new_plan[2])==len(old_plan[2])+2*len(edits)
    return dict(clones=len(edits),distinct_unused_gate_capacities=len(capacities),
                whole_moved_chain_uses=selected_count,actual_operands_and_frames_used=True,
                formal_parent_child_conflicts_absent_in_this_batch=True,
                previous_round_clone_children_allowed=True,
                retained_input_pivot_capacity_preserved=True)


def reverse_plan(old,new,new_plan):
    old_c,old_f=old['circuit'],old['frames'];view,new_f=new['circuit'],new['frames']
    old_users,old_records,_=preserved.descriptions(old_c,old_f)
    _,records,index=preserved.descriptions(view,new_f)
    assert records==new_plan[1]
    mapped={i:index[view.parent_map[gate] if gate is not None else None,target]
            for i,(_,gate,target) in enumerate(old_records)}
    inverse={new_id:old_id for old_id,new_id in mapped.items()}
    assert len(inverse)==len(mapped)
    added=set()
    for job in new['edits']:
        clone=view.duplicate_map[job['node']]
        for predecessor,position in zip(job['original_predecessor_users'],
            (job['same_gate_new_predecessor_input'],job['earlier_predecessor_input'])):
            pair=mapped[predecessor],index[clone,position]
            assert new_plan[2].get(pair[0])==pair[1] and pair not in added
            added.add(pair)
    links=[]
    for pair in new_plan[2].items():
        if pair not in added:
            assert pair[0] in inverse and pair[1] in inverse
            links.append((inverse[pair[0]],inverse[pair[1]]))
    summary=dict(schedule='rank',selected_links=len(links),flow_value=len(links),
        scope='Independently unrolled explicit feasible saved links; no flow solver or optimality claim')
    old_plan,audit=preserved.plan_from_links(old_c,old_f,links,summary)
    edit_audit=validate_edit_batch(old,new,old_plan,new_plan)
    return old_plan,dict(controller_audit=audit,edit_audit=edit_audit)


def forward_plan(old,new,old_plan):
    _,records,_,_,_=old_plan;view,frames=new['circuit'],new['frames']
    _,_,index=preserved.descriptions(view,frames)
    mapped={i:index[view.parent_map[gate] if gate is not None else None,target]
            for i,(_,gate,target) in enumerate(records)}
    links=[(mapped[a],mapped[b]) for a,b in old_plan[2].items()]
    for job in new['edits']:
        clone=view.duplicate_map[job['node']]
        for predecessor,position in zip(job['original_predecessor_users'],
            (job['same_gate_new_predecessor_input'],job['earlier_predecessor_input'])):
            links.append((mapped[predecessor],index[clone,position]))
    summary=dict(schedule='rank',selected_links=len(links),flow_value=len(links),
        scope='Independent small exact retained-chain extension')
    plan,audit=preserved.plan_from_links(view,frames,links,summary)
    return plan,dict(controller_audit=audit,edit_audit=validate_edit_batch(old,new,old_plan,plan))


def exported_history(states,exported):
    baseline=states[0]
    assert frame_digest(baseline['frames'],baseline['circuit'])==exported['canonical_original_frames_sha256']
    canonical={}
    for node in sorted(baseline['circuit'].active):
        canonical.setdefault(baseline['frames'][node],node)
    stages=[stage for stage in exported['stages'] if not stage.get('empty_stage')]
    assert len(stages)==len(states)-1
    for old,new,stage in zip(states,states[1:],stages):
        circuit,view=old['circuit'],new['circuit'];frames=new['frames']
        assert stage['chosen']==new['edits']
        for prefix,state in (('old',old),('new',new)):
            assert stage[prefix+'_roles']==state['expected_roles']
            assert stage[prefix+'_compiled_sha256']==state['expected_compiled']
            assert stage[prefix+'_logical_sha256']==state['expected_logical']
        previous=sorted(circuit.active)
        assert [view.parent_map[node] for node in previous]==stage['original_mapping_values']
        assert digest([[node,view.parent_map[node]] for node in previous])==stage['original_mapping_pairs_sha256']
        places=[[job['node'],view.duplicate_map[job['node']],job['clone_frame_owner'],
            view.parent_map[job['clone_frame_owner']],canonical[old['frames'][job['clone_frame_owner']]]]
            for job in new['edits']]
        assert places==stage['clone_placement_and_frame_owners']
        assert frame_digest(frames,view)==stage['inherited_frames_sha256']
        assert len(view.active)==stage['new_node_count'] and len(previous)==stage['old_node_count']
    final=states[-1]
    owners=[canonical[final['frames'][node]] for node in sorted(final['circuit'].active)]
    assert owners==exported['node_frame_original_owner_values']
    assert digest(owners)==exported['identity']['actual_frame_owners_sha256']
    assert frame_digest(final['frames'],final['circuit'])==exported['identity']['actual_frame_fields_sha256']
    assert digest(exported['stages'])==exported['identity']['stages_sha256']
    return stages


def stage_plan_identity(state,plan,stage):
    assert len(plan[1])==stage['description_count'] and digest(plan[1])==stage['descriptions_sha256']
    assert len(plan[2])==stage['selected_link_count']
    assert digest(sorted([a,b] for a,b in plan[2].items()))==stage['selected_links_sha256']
    order=sorted(state['circuit'].active,key=lambda n:(state['frames'][n].dimension,n))
    assert digest(order)==stage['node_order_sha256']


def independent_rank_timeline(circuit,frames,code,expected):
    """Walk every actual local side event; do not import aggregate producer formulas."""
    h,R=circuit.h,code['roles'];v=len(circuit.inputs);m=h**3;N=v**3
    side=Counter();events=0
    for stage in range(1,4):
        current=[h if stage==3 else 0]*R
        baseline=h**stage-h
        def edge(slot,label):
            nonlocal events
            assert label>=current[slot]
            side[label-current[slot]]+=1;current[slot]=label;events+=1
        def gates(backward,local):
            sequence=reversed(code['gates']) if backward else code['gates']
            for node,ins,outs in sequence:
                value=local(frames[node].dimension) if callable(local) else local
                for slot in set(ins+outs):edge(slot,baseline+value)
        def sources(local):
            for slot in code['sources'].values():edge(slot,baseline+local)
        def outputs(local):
            for slot in code['outputs'].values():edge(slot,baseline+local)
        if stage==2:
            sources(0);gates(False,0);outputs(1);gates(True,lambda rank:h-rank)
            sources(h-1);gates(False,h);outputs(h);gates(True,h)
        else:
            gates(False,0);outputs(0);gates(True,0);sources(1)
            gates(False,lambda rank:rank);outputs(h-1);gates(True,h);sources(h)
        assert all(rank==h**stage for rank in current)
        if stage>=2:
            for slot in range(R):edge(slot,m)
    supplied=Counter()
    for name in ('side_middle_forward_stages1_and3','side_middle_complement_stage2',
                 'side_sources_shared_stage_join_and_sinks'):
        supplied.update({int(rank):int(count) for rank,count in expected['categories'][name]['rank_histogram'].items()})
    assert Counter({rank:count*v*v for rank,count in side.items()})==supplied
    centers=Counter({0:2*h,m-2*h:h,h*h-h:h,m-h*h:h,h:9*h})
    total=Counter(supplied)
    total.update({rank:count*v*v for rank,count in centers.items()})
    for stage in range(1,4):
        earlier=(h**(stage-1)-1)*(h-1)
        total.update({rank:count*N for rank,count in Counter([1 if stage==1 else earlier,h-1,0,0]).items()})
        total.update({rank:count*N for rank,count in Counter([earlier,0,0,h-1]).items()})
    total[0]+=2*N;total.setdefault(m,0)
    exact={str(rank):count for rank,count in sorted(total.items())}
    assert exact=={rank:int(count) for rank,count in expected['rank_histogram'].items()}
    assert sum(rank*count for rank,count in total.items())==int(expected['s'])
    assert sum(total.values())==int(expected['edge_count'])
    return dict(all_actual_side_events=events,all_side_slots_per_stage=R,
        exact_aggregate_rank_histogram=exact,rank_sum=sum(rank*count for rank,count in total.items()),
        edge_count=sum(total.values()),producer_aggregate_rank_functions_imported=False)


def edit_negative_controls(old,new,old_plan,new_plan):
    checked=[]
    # A valid byte plan must contain both new retained links. Removing one
    # remains a graph modification, but it fails the claimed role-saving
    # construction and must not inherit the original certificate.
    successor=dict(new_plan[2]);predecessor=dict(new_plan[3])
    job=new['edits'][0]
    _,old_records,_=preserved.descriptions(old['circuit'],old['frames'])
    _,_,index=preserved.descriptions(new['circuit'],new['frames'])
    first=job['original_predecessor_users'][0]
    _,gate,position=old_records[first]
    mapped=index[new['circuit'].parent_map[gate],position]
    second=successor.pop(mapped);predecessor.pop(second)
    bad=(new_plan[0],new_plan[1],successor,predecessor,new_plan[4])
    try:reverse_plan(old,new,bad)
    except AssertionError:checked.append('Missing required new clone-input retention rejected')
    else:raise AssertionError('Missing-link negative control was not rejected')
    for number,job in enumerate(new['edits']):
        if len(job['selected'])>=2:
            edits=list(new['edits']);bad_job=dict(job,selected=job['selected'][:-1]);edits[number]=bad_job
            bad_new=dict(new,edits=edits)
            try:validate_edit_batch(old,bad_new,old_plan,new_plan)
            except AssertionError:checked.append('Moving a proper subset of a recovered whole chain rejected')
            else:raise AssertionError('Partial-chain negative control was not rejected')
            break
    # The h8 selector chooses only one-use chains. The h12 fixture has a
    # genuine two-use chain and additionally exercises the partial-chain
    # rejection; never fabricate that negative for a one-use chain.
    assert checked and (len(checked)==2 or old['circuit'].h==8)
    return checked


def verify(row,parent_row,exported=None,small=False):
    start=time.monotonic();states=history(row,parent_row);final=states[-1]
    circuit,frames=final['circuit'],final['frames'];h=circuit.h
    print('PASS own compound actual-frame DAG reconstruction',h,len(states)-1,flush=True)
    audits=[]
    if exported is not None:
        stages=exported_history(states,exported)
        summary=dict(schedule='rank',selected_links=len(exported['exact_selected_links']),
            flow_value=len(exported['exact_selected_links']),scope='Explicit saved final plan; no optimizer')
        plan,plan_audit=preserved.plan_from_links(circuit,frames,exported['exact_selected_links'],summary)
        assert len(plan[1])==exported['description_count'] and digest(plan[1])==exported['identity']['descriptions_sha256']
        assert digest(exported['exact_selected_links'])==exported['identity']['selected_links_sha256']
        order=sorted(circuit.active,key=lambda n:(frames[n].dimension,n))
        assert order==exported['node_order'] and len(order)==exported['node_count']
        assert digest(order)==exported['identity']['node_order_sha256']
        current=plan
        for index in range(len(states)-1,0,-1):
            stage_plan_identity(states[index],current,stages[index-1])
            old_plan,audit=reverse_plan(states[index-1],states[index],current)
            audits.append(dict(stage=states[index]['label'],**audit))
            code=compile_reuse(states[index-1]['circuit'],states[index-1]['frames'],old_plan)
            assert code['roles']==states[index-1]['expected_roles']
            assert compiled_digest(code)==states[index-1]['expected_compiled']
            current=old_plan
        del code,current
    else:
        base=states[0]
        current=optimize_chains(base['circuit'],base['frames'],'rank')
        code=compile_reuse(base['circuit'],base['frames'],current)
        assert code['roles']==base['expected_roles'] and compiled_digest(code)==base['expected_compiled']
        for old,new in zip(states,states[1:]):
            current,audit=forward_plan(old,new,current);audits.append(dict(stage=new['label'],**audit))
            code=compile_reuse(new['circuit'],new['frames'],current)
            assert code['roles']==new['expected_roles'] and compiled_digest(code)==new['expected_compiled']
        plan=current;del code,current
        # The first changed small-stage plan can be recovered from the final
        # plan, so both negatives use the same exact saved history.
        if small:
            final_plan=plan
            for index in range(len(states)-1,1,-1):
                final_plan,_=reverse_plan(states[index-1],states[index],final_plan)
            initial_plan,_=reverse_plan(states[0],states[1],final_plan)
            negatives=edit_negative_controls(states[0],states[1],initial_plan,final_plan)
    code=compile_reuse(circuit,frames,plan)
    assert code['roles']==row['compiled_roles'] and compiled_digest(code)==row['final']['checked']['compiled_sha256']
    assert len(plan[2])==row['final']['links']
    # Only the selected final changed graph receives full coefficient/native
    # timeline verification. Prior levels are byte/plan identities, not an
    # accepted-baseline physical replay.
    logical=logical_check(circuit)
    print('PASS all changed final coefficients',h,logical['nonzero_partial_coefficients'],flush=True)
    physical=physical_coefficients(circuit,code)
    rational=preserved.graph_envelope_check(circuit,frames,code,dense=small)
    result=dict(h=h,roles=code['roles'],base=row['base'],positions=row['positions'],
        input_roles=len(circuit.inputs),logical=logical,physical=physical,rational_frames=rational,
        final_compiled_sha256=compiled_digest(code),history=audits,
        old_baseline_physical_replayed=False,producer_cloner_selector_imported=False,
        current_actual_frames_retained_at_all_stages=True,
        intermediate_states=[dict(label=s['label'],roles=s['expected_roles'],
            compiled_sha256=s['expected_compiled'],logical_sha256=s['expected_logical'],
            additions=s['circuit'].additions,clones=len(s['edits'])) for s in states])
    if small:
        from dag_network import exact_invocation
        result['complete_side_dirty_basis']=dirty_check(circuit,frames,code)
        result['complete_invocation_dirty_basis']=[exact_invocation(h,inverse,program(circuit,code)) for inverse in (False,True)]
        result['edit_negative_controls']=negatives
    if h%2:
        images,record=matching(h);result['matching']=record
    elif h==8 and small:
        images,record=even_matching(h);result['matching']=record
        result['complete_shared_three_stage_exchange']=shared_exchange(circuit,code,images,109)
        result['shared_matching_scope']='Fresh changed h8 multi-option DAG, complete three-stage exchange with two dirty auxiliary banks'
    if h>=40:
        v=comb(h,3);m=h**3;N=v**3;R=code['roles'];c=circuit.additions
        W=2*N+2*v*v*(R+h);L=3*v*v*h*h;D=N-2*L;s=W*m-D
        assert D>0 and 2<=s<m**5
        counts=dict(h=h,R=R,v=v,m=m,N=N,W=W,L=L,D=D,s=s)
        assert all(int(row['exact_counts'][key])==value for key,value in counts.items() if key not in ('R','v'))
        G=3*v*v*(4*(c+R-v)+20*v);E=64*(W+m+1)**3;depth=2*G*W*W+4*s+4*W+4
        assert E>depth
        assert all(int(row['literal_scalar_guard'][key])==value for key,value in dict(G=G,E=E,depth=depth,slack=E-depth).items())
        result.update(exact_counts=counts,literal_scalar_guard=dict(G=G,E=E,depth=depth,slack=E-depth))
        result['independent_actual_rank_timeline']=independent_rank_timeline(circuit,frames,code,row['residual_rank_histogram'])
    result.update(wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print('PASS independent compound physical/target/native frames',h,code['roles'],flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('reference','certificate','parent','plan','small-certificate','small-parent','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    revision=subprocess.check_output(['git','-C',str(args.reference),'rev-parse','HEAD'],text=True).strip()
    assert revision=='bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    install_reference(str(args.reference))
    full_data,full_row=read_row(args.certificate)
    parent_data,parent_row=read_row(args.parent,full_row['h'])
    small_data,small_row=read_row(args.small_certificate,12)
    _,small_parent=read_row(args.small_parent,12)
    exported=json.loads(args.plan.read_text())
    assert file_digest(args.parent)==full_row['parent_sha256']
    assert file_digest(args.small_parent)==small_row['parent_sha256']
    assert full_row['h']==53
    assert exported['identity']['compound_candidate_id']==full_data['candidate_id']
    assert exported['identity']['compound_certificate_sha256']==file_digest(args.certificate)
    assert exported['identity']['initial_parent_sha256']==file_digest(args.parent)
    assert exported['identity']['roles']==full_row['compiled_roles']
    assert exported['identity']['compiled_sha256']==full_row['checked']['compiled_sha256']
    assert exported['identity']['residual_rank_histogram_sha256']==digest(full_row['residual_rank_histogram'])
    assert exported['identity']['literal_scalar_guard_sha256']==digest(full_row['literal_scalar_guard'])
    assert exported['candidate_id']==digest(exported['identity'])
    _,eight_parent=read_row(args.small_parent,8)
    eight_row=dict(h=8,base=eight_parent['base'],positions=eight_parent['positions'],
        compiled_roles=eight_parent['compiled_roles'],parent_roles=eight_parent['compiled_roles'],
        role_saving=0,rounds=[],final=eight_parent['final'])
    start=time.monotonic();small=verify(small_row,small_parent,small=True)
    eight=verify(eight_row,eight_parent,small=True)
    full=verify(full_row,parent_row,exported=exported)
    result=dict(status='PASS independent compound actual-frame h53 finite witness',
        completed_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,
        reference_commit=revision,candidate_id=full_data['candidate_id'],full=full,
        small_control=small,small_shared_control=eight,
        input_sha256={str(p):file_digest(p) for p in (args.certificate,args.parent,args.plan,args.small_certificate,args.small_parent)},
        source_sha256={name:file_digest(Path(__file__).with_name(name)) for name in (
            Path(__file__).name,'review_descendant_clone_witness.py','review_singleton_positions.py',
            'review_odd_pair_witness.py','review_aligned_graph.py','review_singleton_witness.py',
            'review_frame_reuse.py','review_envelopes.py','frame_reuse.py','fast_frame_envelope.py')},
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='One final changed compound h53 DAG; actual enlarged frames at every round, independently recovered feasible controller history, all final coefficients/physical frames/targets and actual side rank timelines; fresh whole h12 dirty bases and changed h8 complete shared exchange. No producer selector or cloner imported; no accepted baseline physical replay.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
