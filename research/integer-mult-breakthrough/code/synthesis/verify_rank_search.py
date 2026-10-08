#!/usr/bin/env python3
"""Bounded stdlib replay of complete rank searches and relevant controls.

Runs the actual n2 graph/full models over GF2 and Gaussian F9, compares
unquotiented/projective F3 state counts, and checks field, metric pruning,
strict capacity and full dirty-helper columns. No larger sweep is needed.
"""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time

from dirty_helper_rank_search import frame_domain,search as binary_search
from lagrangian_graph_completion import distance
from scalar_field_rank_search import Field,search as ordinary_search
from scalar_projective_rank_search import search as projective_search


def require(condition,message):
    if not condition:raise ValueError(message)


def rejected(fn,label):
    try:fn()
    except ValueError:return label
    raise ValueError('Corruption control was accepted: '+label)


def field_contract(field):
    q=field.q
    require(all(field.mul[a][0]==0 and field.mul[a][1]==a and field.add[a][0]==a for a in range(q)),
            'Residue field lacks zero/identity laws')
    if q==9:require(field.mul[3][3]==2,'Gaussian residue i^2 must equal -1')
    for a in range(1,q):require(any(field.mul[a][b]==1 for b in range(1,q)),'Nonzero residue lacks an inverse')
    for a in range(q):
        for b in range(q):
            require(field.add[a][b]==field.add[b][a] and field.mul[a][b]==field.mul[b][a],'Field operations are not commutative')
            for c in range(q):
                require(field.mul[field.mul[a][b]][c]==field.mul[a][field.mul[b][c]],'Residue multiplication is not associative')
                require(field.mul[a][field.add[b][c]]==field.add[field.mul[a][b]][field.mul[a][c]],'Residue distributivity failed')


def metric_contract(table):
    n=len(table)
    for a in range(n):
        require(table[a][a]==0,'Metric self-distance is nonzero')
        for b in range(n):
            require(table[a][b]==table[b][a] and (a==b or table[a][b]>0),'Distance is not a metric')
            for c in range(n):
                require(table[a][c]<=table[a][b]+table[b][c],'Endpoint-distance pruning lacks a valid triangle bound')


def bank_map_contract(rows):
    require(rows==[2,1,4],'Complete scalar SWAP/dirty-helper columns are incorrect')


def capacity_contract(capacity,strict_budget):
    require(strict_budget==capacity-1,'Rank budget does not impose strict complete-stock contraction')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path);args=ap.parse_args()
    if args.output and args.output.exists():raise FileExistsError('Use a fresh output')
    start=time.monotonic();receipts=[]
    for kind in ('graph','full'):
        binary=binary_search(2,kind,30,100000)
        require(binary['status']=='EXCLUDED BELOW CAPACITY IN COMPLETE FINITE MODEL','Bounded binary search was inconclusive')
        require(binary['discovered_states']==120,'Bounded binary complete-state count changed')
        gaussian=projective_search(2,kind,9,30,100000)
        require(gaussian['status']=='EXCLUDED BELOW CAPACITY IN COMPLETE FINITE MODEL','Bounded Gaussian-residue search was inconclusive')
        require(gaussian['discovered_projective_states']==24480,'Bounded Gaussian-residue complete-state count changed')
        plain=ordinary_search(2,kind,3,30,100000);quotient=projective_search(2,kind,3,30,100000)
        require(plain['status']==quotient['status']=='EXCLUDED BELOW CAPACITY IN COMPLETE FINITE MODEL','Unit-quotient controls were inconclusive')
        require(plain['discovered_states']==3648 and quotient['discovered_projective_states']==456,
                'Bounded F3 unit-quotient state counts changed')
        require(plain['discovered_states']==8*quotient['discovered_projective_states'],'Free row-unit quotient lost state classes')
        capacity_contract(binary['capacity'],binary['searched_strict_budget']);bank_map_contract(binary['scalar_target_rows'])
        receipts.append(dict(domain=kind,binary_states=120,gaussian_projective_states=24480,
                             F3_states=3648,F3_projective_states=456,
                             binary_state_sha256=binary['explored_state_sha256'],
                             gaussian_state_sha256=gaussian['projective_state_sha256'],
                             exact_no_strict_rank_word=True,complete_helper_columns=True))
    fields=[Field(3),Field(9)]
    for field in fields:field_contract(field)
    broken=Field(9);broken.mul[3][3]=1
    frames=frame_domain(2,'full');table=[[distance(a,b,2) for b in frames] for a in frames];metric_contract(table)
    corrupt=[list(row) for row in table];corrupt[0][0]=1
    negatives=[rejected(lambda:field_contract(broken),'Gaussian field corruption rejected'),
               rejected(lambda:metric_contract(corrupt),'Invalid endpoint-pruning metric rejected'),
               rejected(lambda:bank_map_contract([2,1,5]),'Missing dirty-helper source column rejected'),
               rejected(lambda:capacity_contract(6,6),'Nonstrict capacity budget rejected'),
               rejected(lambda:require(3648==456,'Units were silently identified without their quotient'),
                        'Incorrect unquotiented/quotiented count equality rejected')]
    sources=[Path(__file__),Path(__file__).with_name('dirty_helper_rank_search.py'),
             Path(__file__).with_name('lagrangian_graph_completion.py'),Path(__file__).with_name('scalar_field_rank_search.py'),
             Path(__file__).with_name('scalar_projective_rank_search.py')]
    result=dict(status='PASS BOUNDED COMPLETE RANK SEARCH CERTIFICATES',created_utc=datetime.now(timezone.utc).isoformat(),
                cases=receipts,field_contracts=['F3','F3[i] with i^2=-1'],full_n2_metric_triangle_controls=15**3,
                negative_controls=negatives,source_sha256={p.name:sha256(p.read_bytes()).hexdigest() for p in sources},
                seconds=time.monotonic()-start,
                scope='Bounded actual finite scalar/frame searches and corruption controls. No physical Gaussian lift, larger sweep, recurrence or integer-multiplication exponent is certified.')
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
