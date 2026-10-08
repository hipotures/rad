#!/usr/bin/env python3
"""Audit actual middle-bank endpoints; test the arbitrary dirty source gauge.

The final saved DAG is reconstructed and compiled without old coefficient
replay or a flow solver.  This changes source/sink matrices only.  The small
native control checks the endpoint-gauge contract on a complete two-generator
address orbit; it does not repeat the previously accepted interior frames.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path
import resource
import time

import review_early_compound_bit_witness as early
import review_compound_bit_witness as review


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def native_endpoint_contract(h=6, q=7):
    """Every dirty bit basis on a complete native q^2 address orbit.

Addresses a*D+b*P_D0*D are actual vectors in Fq^(h^3).  The logical
transparent invocation runs pointwise.  Source gauge and sink gauge are
literal address translations, and the missing-sink correction is rejected.
"""
    from finite_block_search import GroupUnion
    from paired_exclusion_circuit import PairedExclusionCircuit
    from dag_network import invoke
    circuit = GroupUnion(h, PairedExclusionCircuit, 'paired')
    code = circuit.program()
    v, R = len(code['triples']), code['roles']
    width = 2*v+R+h
    triple = (0,1,2)
    t = [Q(i in triple) for i in range(h)]
    dual = [(x-Q(1,3))/2 for x in t]
    assert sum(x*y for x,y in zip(t,dual)) == 1
    H = [[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
    P = [[t[i]*dual[j] for j in range(h)] for i in range(h)]
    assert all(sum(P[i][k]*P[k][j] for k in range(h)) == P[i][j]
               for i in range(h) for j in range(h))
    assert all(sum(H[i][k]*P[k][j] for k in range(h)) ==
               sum(P[k][i]*H[k][j] for k in range(h))
               for i in range(h) for j in range(h))
    assert sum(P[i][i] for i in range(h)) == 1
    unit = [Q(i==0) for i in range(h)]
    pt = [sum(P[i][j]*unit[j] for j in range(h)) for i in range(h)]
    bt = [a-b for a,b in zip(unit,pt)]
    middle = [Q(i==1) for i in range(h)]
    D = [a*b*c for a in unit for b in middle for c in unit]
    M = [a*b*c for a in bt for b in middle for c in pt]
    def mod(x): return x.numerator*pow(x.denominator,-1,q)%q
    Dm, Mm = list(map(mod,D)), list(map(mod,M))
    assert any((Dm[i]*Mm[j]-Dm[j]*Mm[i])%q for i in range(h**3) for j in range(i))
    addresses = list(product(range(q),repeat=2))
    physical = [[1 << (role*q*q+index) for index in range(q*q)] for role in range(width)]
    def shift(values,a,b):
        out=[0]*(q*q)
        for (x,y),bits in zip(addresses,values): out[((x+a)%q)*q+(y+b)%q]=bits
        return out
    controls=[]
    for inverse in (False,True):
        logical=[row.copy() if role<2*v else shift(row,0,-1)
                 for role,row in enumerate(physical)]
        expected=[row.copy() for row in physical]
        for index in range(q*q):
            parts=[list(z) for z in ( [row[index] for row in logical[:v]],
                  [row[index] for row in logical[v:2*v]],
                  [row[index] for row in logical[2*v:2*v+R]],
                  [row[index] for row in logical[2*v+R:]] )]
            invoke(*parts,code,inverse=inverse)
            for role,bits in enumerate(sum(parts,[])): logical[role][index]=bits
            parts=[list(z) for z in ( [row[index] for row in expected[:v]],
                  [row[index] for row in expected[v:2*v]],
                  [row[index] for row in expected[2*v:2*v+R]],
                  [row[index] for row in expected[2*v+R:]] )]
            invoke(*parts,code,inverse=inverse)
            for role,bits in enumerate(sum(parts,[])): expected[role][index]=bits
        result=[shift(row,1,0 if role<2*v else 1) for role,row in enumerate(logical)]
        expected=[shift(row,1,0) for row in expected]
        assert result==expected
        assert all(result[role]==shift(physical[role],1,0) for role in range(2*v,width))
        wrong=[shift(row,1,0) for row in logical]
        assert wrong!=expected
        controls.append(dict(inverse=inverse,complete_dirty_native_basis=width*q*q,
            all_side_and_central_inputs_arbitrary=True,auxiliaries_restored_up_to_required_I_shear=True,
            omitted_sink_M_rejected=True))
    return dict(h=h,address_prime=q,address_orbit=q*q,ambient_dimension=h**3,
        side_roles=R,center_roles=h,rank_D0=h*h-h,rank_D1=h*h,
        rank_new_exit=h**3-h,exit_kernel_dimension=h,
        exact_tensor_projector_idempotency_and_self_adjointness=True,
        orbit_generators_independent=True,controls=controls,
        scope='Endpoint conjugation of the accepted transparent invocation on every dirty basis; no old interior physical-frame replay')


def middle_endpoints(code,frames,h):
    R=code['roles'];first=[None]*R;last=[None]*R;first_kind=Counter();last_kind=Counter()
    def touches(slots,kind,rank):
        for role in slots:
            value=rank(role) if callable(rank) else rank
            if first[role] is None:first[role]=(kind,value)
            last[role]=(kind,value)
    touches(code['sources'].values(),'initial_V',0)
    for node,ins,outs in code['gates']:touches(set(ins+outs),'initial_L',0)
    touches(code['outputs'].values(),'first_J',1)
    for node,ins,outs in reversed(code['gates']):touches(set(ins+outs),'middle_L_inverse',h-frames[node].dimension)
    touches(code['sources'].values(),'middle_V',h-1)
    for node,ins,outs in code['gates']:touches(set(ins+outs),'cleanup_L',h)
    touches(code['outputs'].values(),'last_J',h)
    for node,ins,outs in reversed(code['gates']):touches(set(ins+outs),'last_L_inverse',h)
    assert all(x is not None and x[1]==0 for x in first)
    assert all(x is not None and x[1]==h for x in last)
    for kind,_ in first:first_kind[kind]+=1
    for kind,_ in last:last_kind[kind]+=1
    return dict(roles=R,first_incidence_kinds=dict(first_kind),last_incidence_kinds=dict(last_kind),
        first_frame_dimension=h*h-h,last_frame_dimension=h*h,
        early_or_late_retained_gate_exclusions=0,
        every_actual_physical_role_has_D0_first_and_D1_last=True)


def changed_histogram(row,protected=0):
    h=row['h'];R=row['compiled_roles'];v=comb(h,3);m=h**3;J=(R+h)*v*v
    hist=Counter({int(r):int(n) for r,n in row['residual_rank_histogram']['rank_histogram'].items()})
    old_mass=sum(r*n for r,n in hist.items());old_count=sum(hist.values())
    assert hist[h*h-h]>=J and hist[m-h*h]>=J
    hist[h*h-h]-=J;hist[m-h*h]-=J;hist[0]+=J;hist[m-h]+=J
    assert sum(r*n for r,n in hist.items())==old_mass and sum(hist.values())==old_count
    if protected:
        assert protected==2
        # Two disjoint protected first gathers cover every triple, adding
        # one data event per tensor-stage incidence. Center return ranks
        # replace six h increments by six h-1 increments per protected role.
        N=v**3
        assert hist[h]>=12*v*v and hist[h-1]>=3*N
        hist[h]-=12*v*v;hist[h-1]+=12*v*v
        hist[h-1]-=3*N;hist[h-2]+=3*N;hist[1]+=3*N
        assert sum(r*n for r,n in hist.items())==old_mass-12*v*v
        assert sum(hist.values())==old_count+3*N
    return dict(protected_centers=protected,eligible_roles_per_middle_invocation=R+h,
        side_roles=R,centers=h,multiplicity=v*v,eligible_physical_roles=J,
        removed_entrance_rank=h*h-h,removed_exit_rank=m-h*h,
        new_entrance_rank=0,new_exit_rank=m-h,
        rank_histogram={str(r):n for r,n in sorted(hist.items()) if n or r in (0,m)},
        rank_sum=sum(r*n for r,n in hist.items()),edge_count=sum(hist.values()),
        source_frame_rank_concentration_preserves_rank_sum=True,
        scope='Literal normal histogram; protected2 additionally uses separately reviewed disjoint-center chronology')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('reference','case','parent','export','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();start=time.monotonic()
    review.install_reference(str(a.reference))
    row=json.loads(a.case.read_text());parent=json.loads(a.parent.read_text());exp=json.loads(a.export.read_text())
    assert exp['identity']['compound_certificate_sha256']==digest(a.case)
    assert exp['identity']['initial_parent_sha256']==digest(a.parent)
    states=early.early_history(row,parent);final=states[-1]
    circuit,frames=final['circuit'],final['frames']
    plan,audit=review.preserved.plan_from_links(circuit,frames,exp['exact_selected_links'],dict(schedule='rank',selected_links=len(exp['exact_selected_links']),flow_value=len(exp['exact_selected_links'])))
    assert review.digest(plan[1])==exp['identity']['descriptions_sha256']
    code=review.compile_reuse(circuit,frames,plan)
    assert review.compiled_digest(code)==exp['identity']['compiled_sha256']==row['checked']['compiled_sha256']
    assert code['roles']==row['compiled_roles']
    print('PASS saved actual DAG and compiled identity',code['roles'],flush=True)
    endpoints=middle_endpoints(code,frames,row['h'])
    small=native_endpoint_contract()
    out=dict(status='PASS actual middle source-frame endpoints and native dirty gauge',
        completed_utc=datetime.now(timezone.utc).isoformat(),candidate_id=row['candidate_id'],
        compiled_sha256=review.compiled_digest(code),source_sha256=digest(__file__),
        inputs={str(path):digest(path) for path in (a.case,a.parent,a.export)},
        actual_side_endpoints=endpoints,centers=dict(roles=row['h'],exclusions=0,
            first='Undo the late full gather at D0 before the protected normal gathers',
            last='Full final scatter at D1; both protected and other roles participate'),
        saved_link_feasibility=audit,native_endpoint_contract=small,
        normal=changed_histogram(row),protected2=changed_histogram(row,2),
        upstream_source_frame_provenance=dict(repository='CrocSwap/integer-mult-bounds',PR=13,
            unchanged_snapshot_in_PR14='1fa5b9a9aaccbebb3eb29ac7ea55811f46464eee',
            path='research/source-frame-corners/pr13/notes/source-frame-bit.tex'),
        no_old_coefficient_replay=True,no_flow_solver=True,
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limitation='No common-basis batching proof or composed exponent is certified by this endpoint audit')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'],out['wall_seconds'],flush=True)


if __name__=='__main__':main()
