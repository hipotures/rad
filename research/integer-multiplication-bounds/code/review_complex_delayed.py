#!/usr/bin/env python3
"""Independent binary delayed-clone theorem and changed finite witness.

The new cloner, binary closed-form predicates and selector are not imported.
Actual labels use independent Gram projectors. Original graph generation is
a pinned accepted input; only the changed physical program is replayed.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from math import comb
from pathlib import Path
import resource
import sys
import time
from unittest.mock import patch

import frame_reuse
from downstream_complex_circuit import TripleSideCircuit
from review_complex_controller import (GramFrame, admissible, complement_unit,
    contained, geometry, inverse, physical, unit, xor_selected)
from review_complex_frames import complete_scalar_matrix, dot, gram, rank, residual
from review_pivot_batching import stringify
from review_asymmetric_motif import independent_saving


def canonical(value):
    return tuple(canonical(x) for x in value) if isinstance(value,(tuple,list)) else value


def all_spaces(n):
    for d in range(n+1):
        for pivots in combinations(range(n),d):
            free=[(i,j) for i,p in enumerate(pivots) for j in range(p+1,n) if j not in pivots]
            for values in product(range(2),repeat=len(free)):
                rows=[1<<p for p in pivots]
                for (i,j),value in zip(free,values):rows[i]|=value<<j
                yield tuple(rows)


def projector(rows,n):
    inv=inverse(tuple(gram(rows)));cols=[]
    for i in range(n):
        rhs=sum(dot(1<<i,v)<<j for j,v in enumerate(rows))
        coefficient=sum(dot(v,rhs)<<j for j,v in enumerate(inv))
        cols.append(xor_selected(rows,coefficient))
    return tuple(cols)


def binary_composition_controls():
    records=[]
    for n in (3,4,5):
        spaces=[]
        for B in all_spaces(n):
            if rank(gram(B))!=len(B):continue
            P=projector(B,n);chi=xor_selected(P,(1<<n)-1)
            assert all(xor_selected(P,v)==v for v in B)
            assert all(xor_selected(P,x)==x for x in P)
            spaces.append((B,P,chi))
        included={};admitted={};pair_count=norm_units=zero_characteristic_units=0
        for i,(A,PA,ca) in enumerate(spaces):
            for j,(B,PB,cb) in enumerate(spaces):
                if rank(A+B)!=len(B):continue
                included[i,j]=True;pair_count+=1
                delta=len(B)-len(A);E=tuple(x^y for x,y in zip(PA,PB))
                assert all(xor_selected(E,x)==x for x in E)
                chi=ca^cb
                assert xor_selected(E,(1<<n)-1)==chi
                admitted[i,j]=not delta or bool(chi)
                explicit=residual(list(A),list(B))
                assert len(explicit)==rank(gram(explicit))==delta
                assert (not delta or any(dot(v,v) for v in explicit))==admitted[i,j]
                # Reverse complements have exactly the same residual projector.
                QA=tuple((1<<k)^PA[k] for k in range(n))
                QB=tuple((1<<k)^PB[k] for k in range(n))
                assert tuple(x^y for x,y in zip(QA,QB))==E
                if delta and chi:
                    coordinate=chi&-chi;w=xor_selected(E,coordinate)
                    assert dot(w,w)==1 and not xor_selected(PA,w) and xor_selected(PB,w)==w
                    norm_units+=1
                    zero_characteristic_units+=int(not dot(chi,chi))
        nested_chains=admitted_chains=0
        for j in range(len(spaces)):
            children=[i for i in range(len(spaces)) if (i,j) in included]
            parents=[k for k in range(len(spaces)) if (j,k) in included]
            for i in children:
                for k in parents:
                    nested_chains+=1
                    PA,PB,PC=[spaces[t][1] for t in (i,j,k)]
                    E1=tuple(a^b for a,b in zip(PA,PB));E2=tuple(a^b for a,b in zip(PB,PC))
                    assert all(not xor_selected(E1,x) for x in E2)
                    c1=spaces[i][2]^spaces[j][2];c2=spaces[j][2]^spaces[k][2]
                    assert not c1 or not c2 or c1!=c2
                    if admitted[i,j] and admitted[j,k]:
                        assert admitted[i,k];admitted_chains+=1
        records.append(dict(dimension=n,all_nondegenerate_spaces=len(spaces),
            exact_nested_pairs=pair_count,exact_nested_chains=nested_chains,
            admitted_transitivity_chains=admitted_chains,exact_norm_one_units=norm_units,
            nonzero_characteristic_even_norm_cases=zero_characteristic_units,
            reverse_complement_residuals_identical=True))
    # Nonalternating endpoints alone can contain an alternating interval.
    U=(7,);V=(1,2,4);E=residual(list(U),list(V))
    assert rank(gram(U))==1 and rank(gram(V))==3 and len(E)==rank(gram(E))==2
    assert all(not dot(x,x) for x in E) and projector(U,3)!=projector(V,3)
    assert xor_selected(projector(U,3),7)==xor_selected(projector(V,3),7)==7
    # A valid coarse interval need not validate each finer physical interval.
    A=(8,);B=(8,3,5);C=(1,2,4,8)
    assert all(rank(gram(X))==len(X) and any(dot(v,v) for v in X) for X in (A,B,C))
    ca,cb,cc=[xor_selected(projector(X,4),15) for X in (A,B,C)]
    assert ca==cb!=cc and rank(A+B)==len(B) and rank(B+C)==len(C)
    return dict(records=records,
        admitted_nested_interval_predicate_is_transitive=True,
        nonalternating_endpoints_do_not_suffice=dict(U=U,V=V,residual=E),
        coarse_admissibility_does_not_validate_hidden_interval=dict(U=A,V=B,W=C,
            characteristics=[ca,cb,cc],coarse_admitted=True,first_fine_interval_alternating=True))


def descriptors(circuit,frames):
    order=sorted(circuit.active,key=lambda n:(frames[n].dimension,n))
    positions={n:i for i,n in enumerate(order)};users={n:[] for n in circuit.active};uses=[];index={}
    for parent in order:
        for position,child in enumerate(circuit.args[parent] or ()):
            assert positions[child]<positions[parent]
            i=len(uses);uses.append((child,parent,position));users[child].append(i);index[parent,position]=i
    for target,node in sorted(circuit.outputs.items()):
        i=len(uses);uses.append((node,None,target));users[node].append(i);index[None,target]=i
    return order,users,uses,index


class Changed(TripleSideCircuit):
    def __init__(self,original,old_frames,jobs):
        self.h=original.h;self.inputs=original.inputs;self.variables=original.variables
        self.args=[None];self.core=[0];self.union=[0];self.support=[0];self.family=['zero']
        self.original_mapping={};self.clones={};before={};last=[]
        chosen={job['node']:{canonical(x) for x in job['selected']} for job in jobs}
        assert len(chosen)==len(jobs)
        for job in jobs:
            p=job['node'];assert list(original.args[p])==job['original_children']
            owner=job['clone_insertion_owner']
            if owner is None:last.append(job)
            else:before.setdefault(owner,[]).append(job)
        def append(old,args):
            new=len(self.args);self.args.append(args)
            for name in ('core','union','support','family'):
                getattr(self,name).append(getattr(original,name)[old])
            return new
        def clone(job):
            p=job['node'];assert p in self.original_mapping and p not in self.clones
            self.clones[p]=append(p,tuple(self.original_mapping[c] for c in original.args[p]))
        for old in sorted(original.active,key=lambda p:(old_frames[p].dimension,p)):
            for job in sorted(before.get(old,[]),key=lambda j:j['node']):clone(job)
            args=tuple(self.clones[c] if c in self.clones and ('gate',old) in chosen[c]
                       else self.original_mapping[c] for c in original.args[old]) if original.args[old] else None
            self.original_mapping[old]=append(old,args)
        for job in sorted(last,key=lambda j:j['node']):clone(job)
        self.outputs={t:self.clones[p] if p in self.clones and ('output',t) in chosen[p]
                      else self.original_mapping[p] for t,p in original.outputs.items()}
        self.special={self.original_mapping[p]:t for p,t in original.special.items() if p in self.original_mapping}
        self.special.update({self.clones[p]:t for p,t in original.special.items() if p in self.clones})
        self.active=set();stack=list(self.outputs.values())
        while stack:
            p=stack.pop()
            if p in self.active:continue
            self.active.add(p);stack.extend(self.args[p] or ())
        assert self.active==set(self.original_mapping.values())|set(self.clones.values())
        self.additions=sum(self.args[p] is not None for p in self.active)
        assert self.additions==original.additions+len(jobs)
        assert all(self.original_mapping[p]==p for p in range(1,len(self.inputs)+1))
        self.actual_frames={self.original_mapping[p]:old_frames[p] for p in original.active}
        for job in jobs:
            self.actual_frames[self.clones[job['node']]]=old_frames[job['clone_frame_owner']]


def complete_logical(circuit,frames):
    support={};unions={};cores={}
    for p in sorted(circuit.active):
        args=circuit.args[p]
        if args is None:
            assert p<=len(circuit.inputs);support[p]=1<<(p-1)
            unions[p]=cores[p]=sum(1<<i for i in circuit.inputs[p-1])
            assert frames[p].tag==('line',unions[p])
        else:
            a,b=args;assert a<p and b<p and not support[a]&support[b]
            support[p]=support[a]|support[b];unions[p]=unions[a]|unions[b];cores[p]=cores[a]&cores[b]
            for child in args:assert admissible(frames[child],frames[p]);unit(frames[child],frames[p])
        assert support[p]==circuit.support[p] and unions[p]==circuit.union[p] and cores[p]==circuit.core[p]
        unit(None,frames[p]);complement_unit(frames[p])
    stripes=[0]*circuit.h
    for p,t in enumerate(circuit.inputs):
        for j in t:stripes[j]|=1<<p
    full=(1<<len(circuit.inputs))-1;coefficients=0
    for (kind,t),p in circuit.outputs.items():
        a,b,c=t
        expected=full&~(stripes[a]|stripes[b]|stripes[c]) if kind=='D' else (
            (stripes[a]&stripes[b]&~stripes[c])|(stripes[a]&stripes[c]&~stripes[b])|
            (stripes[b]&stripes[c]&~stripes[a]))
        assert support[p]==expected
        mask=sum(1<<j for j in t);assert frames[p].tag==('kernel',mask) and not frames[p].project(mask)
        coefficients+=expected.bit_count()
    return support,dict(all_changed_formal_coefficients_and_zeros_exact=True,
        all_original_input_lines_and_actual_enlarged_frames_valid=True,
        all_formal_edges_admitted_by_independent_gram=True,
        nonzero_side_coefficients=coefficients,logical_frames=len(circuit.active),
        additions=circuit.additions,designated_outputs=len(circuit.outputs))


def compile_explicit(circuit,frames,links):
    order,users,uses,index=descriptors(circuit,frames);successor={};predecessor={};capacity=set()
    for first,second in links:
        assert first not in successor and second not in predecessor
        node,previous,_=uses[first];node2,following,_=uses[second]
        assert node==node2 and previous is not None and first<second
        assert previous not in capacity;capacity.add(previous)
        assert admissible(frames[previous],frames[following if following is not None else node])
        successor[first]=second;predecessor[second]=first
    plan=(users,uses,successor,predecessor,dict(schedule='rank',selected_links=len(successor),
        scope='Actual feasible saved plan independently checked; no optimizer optimality claim'))
    with patch.object(frame_reuse,'included',admissible):
        code=frame_reuse.compile_reuse(circuit,frames,plan)
    expected=circuit.additions+len(circuit.outputs)-len(links);assert code['roles']==expected
    return code,dict(links=len(links),separate_gate_capacities=len(capacity),
        all_equal_source_nondegenerate_nonalternating_intervals_exact=True,
        exact_roles=expected),uses,index


def small_links(original,old_frames,changed,jobs):
    # Derive only the old link data needed to construct the new witness.
    # No old compiled physical program is created or replayed.
    with patch.object(frame_reuse,'included',admissible):
        old_plan=frame_reuse.optimize_chains(original,old_frames,'rank')
    _,old_uses,old_next,_,_=old_plan
    _,_,_,index=descriptors(changed,changed.actual_frames)
    mapped={i:index[changed.original_mapping[p] if p is not None else None,k]
            for i,(_,p,k) in enumerate(old_uses)}
    links=[(mapped[a],mapped[b]) for a,b in old_next.items()]
    for job in jobs:
        clone=changed.clones[job['node']]
        a,b=job['same_gate_new_predecessor_input'],job['earlier_predecessor_input']
        first_a,first_b=job['original_predecessor_users']
        assert a+b==1 and old_uses[first_a][1:]==(job['node'],a)
        links.extend(((mapped[first_a],index[clone,a]),(mapped[first_b],index[clone,b])))
    assert len(links)==len(old_next)+2*len(jobs)
    return links


def digest(code):
    return sha256(json.dumps({'roles':code['roles'],'gates':code['gates'],
        'sources':sorted(code['sources'].items()),'outputs':sorted(code['outputs'].items())},
        separators=(',',':')).encode()).hexdigest()


def counts(h,R,additions):
    v=comb(h,3);m=h**3;N=v**3;W=2*N+2*v*v*(R+h+1)
    L=3*v*v*(h+1)*h;D=2*N-2*L;s=W*m-D
    G=3*v*v*(4*(additions+v)+4*v+4);E=64*(W+m+1)**3
    depth=2*G*W*W+4*s+4*W+4;assert depth<E
    return dict(h=h,v=v,m=m,N=N,R=R,W=W,L=L,D=D,s=s),dict(
        actual_grouped_scalar_gates=G,additive_E=E,exact_operation_depth_bound=depth,slack=E-depth)


def object_digest(value):
    return sha256(json.dumps(value,separators=(',',':'),sort_keys=True).encode()).hexdigest()


def changed_case(producer,links=None,dirty=False,shared=False,export=None):
    h=producer['h'];original=TripleSideCircuit(h)
    old_frames={p:GramFrame(h,original.frame(p)) for p in original.active}
    # This input generation is accepted, while all enlarged labels and
    # scalar maps below are reconstructed independently for the change.
    jobs=producer['chosen'];view=Changed(original,old_frames,jobs);frames=view.actual_frames
    order,_,actual_uses,_=descriptors(view,frames)
    artifact_checks=None
    if export is not None:
        assert export['chosen']==jobs and export['candidate_id']==producer['candidate_id']
        assert export['node_order']==order
        assert canonical(export['use_descriptions'])==canonical(actual_uses)
        assert canonical(export['original_mapping'])==canonical(sorted(view.original_mapping.items()))
        assert canonical(export['clone_mapping'])==canonical(sorted(view.clones.items()))
        by_old={job['node']:job for job in jobs}
        for record in export['frame_provenance']:
            p=record['original_node'];job=by_old[p];new=view.clones[p]
            assert record['clone_node']==new
            assert record['original_mapping']==view.original_mapping[p]
            assert record['frame_owner_original']==job['clone_frame_owner']
            assert record['frame_owner_mapping']==view.original_mapping[job['clone_frame_owner']]
            assert canonical(record['assigned_frame_tag'])==frames[new].tag
            assert record['insertion_owner_original']==job['clone_insertion_owner']
        identity=export['identity']
        for key,value in [('node_order',order),('use_descriptions',actual_uses),
                          ('selected_links',links),('frame_provenance',export['frame_provenance']),
                          ('original_mapping',sorted(view.original_mapping.items())),
                          ('clone_mapping',sorted(view.clones.items()))]:
            assert object_digest(value)==identity[key+'_sha256']
        assert object_digest(jobs)==identity['exact_chosen_jobs_sha256']
        assert object_digest(identity)==export['candidate_identity_sha256']
        artifact_checks=dict(actual_node_order=len(order),actual_descriptions=len(actual_uses),
            exact_original_and_clone_mappings=True,actual_frame_owner_tags=len(jobs),
            reconstruction_identity=export['candidate_identity_sha256'])
    support,logical=complete_logical(view,frames)
    if links is None:links=small_links(original,old_frames,view,jobs)
    code,plan,uses,index=compile_explicit(view,frames,links)
    assert code['roles']==producer['compiled_roles'] and digest(code)==producer['checked']['compiled_sha256']
    exact=physical(view,frames,support,code)
    assert exact['compiled_sha256']==digest(code)
    assert producer['baseline_roles']-code['roles']==len(jobs)
    c,g=counts(h,code['roles'],view.additions)
    assert all(int(producer['shared_complex_counts'][k])==x for k,x in c.items())
    assert all(int(producer['guard'][k])==x for k,x in g.items())
    assert len(links)==view.additions+len(view.outputs)-code['roles']
    # Closed actual role timelines give precisely h phase-rank units
    # per role after adding their terminal complements.
    previous=[None]*code['roles'];forward=0
    for p,ins,outs in code['gates']:
        current=frames[p]
        for role in set(ins+outs):
            forward+=current.dimension-(previous[role].dimension if previous[role] else 0)
            previous[role]=current
    closed_rank=forward+sum(h-frame.dimension for frame in previous)
    assert closed_rank==h*code['roles']
    clone_frame_checks=Counter()
    for job in jobs:
        old=job['node'];new=view.clones[old];owner=job['clone_frame_owner']
        assert frames[new]==old_frames[owner]
        assert contained(old_frames[old],frames[new])
        clone_frame_checks[frames[new].dimension-old_frames[old].dimension]+=1
    dirty_result=complete_scalar_matrix(view,code) if dirty else None
    shared_result=None
    from review_complex_controller import matching,shared_exchange
    pi,match=matching(view)
    if shared:
        shared_result=shared_exchange(view,code,pi,709)
    saving=None
    if c['D']>0:
        low,high=independent_saving(Q(c['D'],c['W']*c['m']),c['m'])
        explicit=Q((low.numerator*10**20//low.denominator)-1,10**20)
        assert 0<explicit<low and Q(producer['saving_enclosure']['chosen_saving'])<low
        saving=dict(lower=low,upper=high,explicit_strict_saving=explicit,
                    producer_explicit_saving_independently_accepted=True)
    return dict(h=h,clones=len(jobs),actual_clone_frame_increases=dict(clone_frame_checks),
        complete_changed_logical=logical,actual_plan=plan,physical=exact,
        complete_dirty_basis=dirty_result,complete_shared_exchange=shared_result,
        counts=c,guard=g,compiled_sha256=digest(code),saving=saving,
        exact_closed_forward_role_rank=closed_rank,matching=match,
        reconstruction_artifact=artifact_checks,
        all_actual_source_gates_sinks_and_reverse_complements_admitted=True)


def main():
    sys.set_int_max_str_digits(0)
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--links',type=Path,required=True)
    ap.add_argument('--small',type=Path,required=True)
    ap.add_argument('--accepted-original',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();start=time.monotonic()
    candidate=json.loads(args.candidate.read_text());small=json.loads(args.small.read_text())
    accepted=json.loads(args.accepted_original.read_text())
    assert accepted['status']=='Terminal independent complex controller finite/transfer PASS'
    accepted_rows={row['h']:row for row in accepted['rows']}
    assert candidate['original_compiled_sha256']==accepted_rows[28]['physical']['compiled_sha256']
    assert candidate['baseline_roles']==accepted_rows[28]['counts']['R']
    assert accepted['independent_source_sha256']['downstream_complex_circuit.py']==sha256(
        Path(__file__).with_name('downstream_complex_circuit.py').read_bytes()).hexdigest()
    assert (candidate['h'],candidate['compiled_roles'])==(28,88377)
    assert small['status']=='Terminal full finite nonalternating complex delayed-clone witness PASS'
    link_data=json.loads(args.links.read_text())
    assert link_data['candidate_input_sha256']==sha256(args.candidate.read_bytes()).hexdigest()
    print('Binary nested-interval theorem controls',flush=True)
    theorem=binary_composition_controls()
    print('Changed h8 dirty/full-bank controls',flush=True)
    smallrow=next(row for row in small['rows'] if row['h']==8)
    small_result=changed_case(smallrow,dirty=True,shared=True)
    print('Full changed h28 coefficients/actual frames/explicit links',flush=True)
    links=link_data['selected_links']
    full=changed_case(candidate,links=links,export=link_data)
    names=('review_complex_delayed.py','review_complex_controller.py','review_complex_frames.py',
           'downstream_complex_circuit.py','frame_reuse.py','review_pivot_batching.py')
    result=dict(status='PASS independent binary delayed-clone theorem and complete changed h28 witness',
        generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256={name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in names},
        input_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in
                      (args.candidate,args.links,args.small,args.accepted_original)},
        candidate_id=candidate['candidate_id'],binary_interval_theorem=theorem,small=small_result,full=full,
        original_accepted_physical_program_not_replayed=True,
        new_cloner_and_selector_not_imported=True,
        scope='New binary actual first-consumer labels; no rational-envelope substitution. Full actual saved plan, coefficients, both phase timelines, endpoints, dirty h8 Gaussian maps/sharing and literal G/E independently checked. No optimizer optimality or final parameter assembly claimed.',
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(stringify(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],full['counts']['R'],flush=True)


if __name__=='__main__':main()
