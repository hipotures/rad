#!/usr/bin/env python3
"""Delayed clones with the actual nonalternating binary complex interface.

Inherited frames must admit every physical residual under the original
binary projector predicate. Rational positive-envelope assumptions are not
used. Original coefficient evidence is reused only after pinned source,
logical identity and exact compilation checks.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time
from unittest.mock import patch

import frame_reuse
import finite_complex_controller_reuse as binary
from downstream_complex_circuit import TripleSideCircuit,masks
from downstream_complex_certificate import stage_matching,global_exchange
from downstream_parameter_optimum import as_strings,saving_enclosure
from finite_clone_descendant_frame import opportunities
from finite_clone_batch import serialized
from finite_clone_recovered_witness import compiled_hash,recovered_plan
import finite_clone_compatibility_milp as selector


class ComplexCloneView(TripleSideCircuit):
    def __init__(self,original,old_frames,jobs):
        self.h=original.h;self.inputs=original.inputs;self.variables=original.variables
        self.args=[None];self.core=[0];self.union=[0];self.support=[0];self.family=['zero']
        selected={job['node']:job['selected'] for job in jobs};before={};terminal=[]
        for job in jobs:
            owner=job['clone_insertion_owner']
            (terminal if owner is None else before.setdefault(owner,[])).append(job)
        mapping={};clones={}
        def append(old,children):
            new=len(self.args);self.args.append(children)
            for name in ('core','union','support','family'):getattr(self,name).append(getattr(original,name)[old])
            return new
        def clone(job):
            old=job['node'];assert old in mapping and old not in clones
            clones[old]=append(old,tuple(mapping[child] for child in original.args[old]))
        for old in sorted(original.active,key=lambda node:(old_frames[node].dimension,node)):
            for job in sorted(before.get(old,[]),key=lambda job:job['node']):clone(job)
            children=(tuple(clones[child] if child in clones and ('gate',old) in selected[child] else mapping[child]
                for child in original.args[old]) if original.args[old] else None)
            mapping[old]=append(old,children)
        for job in sorted(terminal,key=lambda job:job['node']):clone(job)
        self.outputs={target:clones[node] if node in clones and ('output',target) in selected[node] else mapping[node]
            for target,node in original.outputs.items()}
        self.special={mapping[node]:target for node,target in original.special.items() if node in mapping}
        self.special.update({clones[node]:target for node,target in original.special.items() if node in clones})
        self.active=set();stack=list(self.outputs.values())
        while stack:
            node=stack.pop()
            if node in self.active:continue
            self.active.add(node)
            if self.args[node]:stack.extend(self.args[node])
        self.additions=sum(self.args[node] is not None for node in self.active)
        assert self.additions==original.additions+len(jobs)
        assert set(mapping.values())|set(clones.values())==self.active
        assert all(mapping[node]==node for node in range(1,len(self.inputs)+1))
        self.original_mapping=mapping;self.clones=clones


def logical_identity(circuit):
    digest=sha256()
    for node in sorted(circuit.active):digest.update(f'{node}:{circuit.args[node]}\n'.encode())
    for (kind,target),node in sorted(circuit.outputs.items()):digest.update(f'{kind}:{target}:{node}\n'.encode())
    return digest.hexdigest()


def independent_physical(view,frames,code):
    from review_complex_controller import GramFrame,geometry,physical
    actual={node:GramFrame(view.h,frame.tag) for node,frame in frames.items()}
    columns=0
    for frame in set(frames.values()):
        gram=GramFrame(view.h,frame.tag)
        assert gram.dimension==frame.dimension and gram.characteristic==frame.characteristic
        geometry(gram)
        for index in range(view.h):assert gram.project(1<<index)==frame.project(1<<index)
        columns+=view.h
    for (_,target),node in view.outputs.items():assert actual[node].project(masks(target))==0
    result=physical(view,actual,{node:view.support[node] for node in view.active},code)
    result['independent_actual_binary_projector_columns']=columns
    return result


def case(h,baseline,dirty=False,exchange=False):
    at=time.monotonic();original=TripleSideCircuit(h)
    assert logical_identity(original)==baseline['logical']['circuit_sha256']
    old_frames,_=binary.labels(original)
    with patch.object(frame_reuse,'included',binary.admissible):
        old_plan=frame_reuse.optimize_chains(original,old_frames,'rank')
        old_code=frame_reuse.compile_reuse(original,old_frames,old_plan)
        assert old_code['roles']==baseline['compiled_roles']
        assert compiled_hash(old_code)==baseline['checked']['compiled_sha256']
        jobs,diagnostic=opportunities(original,old_frames,old_plan)
        permitted=[];excluded=0
        for job in jobs:
            frame=old_frames[job['clone_frame_owner']]
            if all(binary.admissible(old_frames[child],frame) for child in original.args[job['node']]):permitted.append(job)
            else:excluded+=1
        chosen,rejected=selector.select(permitted)
        view=ComplexCloneView(original,old_frames,chosen)
        frames={view.original_mapping[node]:old_frames[node] for node in original.active}
        for job in chosen:frames[view.clones[job['node']]]=old_frames[job['clone_frame_owner']]
        for node in view.active:
            if view.args[node]:assert all(binary.admissible(frames[child],frames[node]) for child in view.args[node])
            else:assert frames[node].tag==('line',view.core[node])
        plan=recovered_plan(original,old_plan,view,frames,chosen)
        code=frame_reuse.compile_reuse(view,frames,plan)
        checked=frame_reuse.check(view,frames,code)
    assert old_code['roles']-code['roles']==len(chosen)
    logical=view.verify();physical=binary.physical_replay(view,code);phase=binary.phase_timeline(view,frames,code)
    for (_,target),node in view.outputs.items():
        assert frames[node].tag==('kernel',masks(target)) and frames[node].project(masks(target))==0
    independent=independent_physical(view,frames,code)
    from review_complex_frames import complete_scalar_matrix
    dirty_result=complete_scalar_matrix(view,code) if dirty else None
    pi,matching=stage_matching(view)
    stages=global_exchange(view,code,pi,[5]) if exchange else []
    v=comb(h,3);m=h**3;N=v**3;R=code['roles'];W=2*N+2*v*v*(R+h+1)
    L=3*v*v*(h+1)*h;D=2*N-2*L;s=W*m-D
    G=3*v*v*(4*(view.additions+v)+4*v+4);E=64*(W+m+1)**3;depth=2*G*W*W+4*s+4*W+4
    assert depth<E
    counts=dict(h=h,v=v,m=m,N=N,R=R,W=W,L=L,D=D,s=s,eta=Q(D,W*m))
    checked['nondegeneracy']='Exact binary nondegenerate inherited frames; every admitted nonzero physical residual nonalternating'
    row=dict(h=h,baseline_roles=baseline['compiled_roles'],compiled_roles=R,role_saving=len(chosen),
        original_coefficient_evidence_reused_by_pinned_identity=True,original_compiled_sha256=compiled_hash(old_code),
        original_logical_sha256=logical_identity(original),opportunity_diagnostic=diagnostic,
        excluded_alternating_formal_child_residuals=excluded,permitted_jobs=len(permitted),conflict_rejected=len(rejected),
        chosen=[serialized(job) for job in chosen],compatibility_selection=selector.LAST_SELECTION,
        logical=logical,checked=checked,physical=physical,phase=phase,independent_actual_frames=independent,
        complete_dirty_scalar_matrix=dirty_result,stage_matching=matching,complete_shared_three_stage=stages,
        shared_complex_counts=counts,guard=dict(actual_grouped_scalar_gates=G,additive_E=E,
            exact_operation_depth_bound=depth,slack=E-depth,cloned_logical_gates_included=True),
        saving_enclosure=saving_enclosure(counts['eta'],m) if D>0 else None,
        elapsed_seconds=time.monotonic()-at,
        scientific_scope='Inherited actual binary first-consumer frames; every phase residual separately checked nonalternating; independent global transfer review pending')
    binary.admissible.cache_clear();binary.contained.cache_clear();binary.basis.cache_clear()
    return as_strings(row)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h',type=int,nargs='+',default=[8,12]);ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--dirty-ground',type=int,default=8);ap.add_argument('--exchange-h8',action='store_true')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists()
    baseline=json.loads(args.baseline.read_text())
    for name in ('frame_reuse.py','downstream_complex_circuit.py','downstream_complex_certificate.py'):
        assert baseline['source_dependencies'][name]==sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
    assert baseline['source_sha256']==sha256(Path(binary.__file__).read_bytes()).hexdigest()
    saved={row['h']:row for row in baseline['rows']};at=time.monotonic()
    value=dict(status='Running',rows=[],source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        baseline_input_sha256=sha256(args.baseline.read_bytes()).hexdigest(),started_utc=datetime.now(timezone.utc).isoformat(),
        phase_interface='Existing even-ground nonalternating binary-frame complex family; no rational-envelope substitution')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for h in args.h:
        row=case(h,saved[h],args.dirty_ground==h,h==8 and args.exchange_h8);value['rows'].append(row)
        args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(h=h,baseline=row['baseline_roles'],roles=row['compiled_roles'],
            clones=row['role_saving'],excluded_alternating=row['excluded_alternating_formal_child_residuals'],seconds=row['elapsed_seconds'])),flush=True)
    value.update(status='Terminal full finite nonalternating complex delayed-clone witness PASS',
        completed_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-at)
    args.output.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
