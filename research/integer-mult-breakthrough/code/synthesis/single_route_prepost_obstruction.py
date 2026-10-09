#!/usr/bin/env python3
"""Verify the unique-routed-path premise of a scoped all-size boundary lemma.

Reads completed evidence without changing it. The algebraic conclusion is
for a common missing-line quotient, not the distinct-label joint primitive.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path


TOPIC=Path(__file__).resolve().parents[2]


def identity(W):return [[int(i==j) for j in range(W)] for i in range(W)]


def inverse_mix(events,W):
    M=identity(W)
    for event in reversed(events):
        if event['kind']!='add':raise ValueError('A nonconstant event entered the bank mixer')
        s=event['source'];t=event['target'];c=event['coefficient']
        if not 0<=s<W or not 0<=t<W or s==t or c not in (-1,1):raise ValueError('Malformed paid unit shear')
        M[t]=[a-c*b for a,b in zip(M[t],M[s])]
    return M


def single_paths(A,B,W):
    paths={}
    for i in range(W):
        for j in range(W):
            selected=[k for k in range(W) if A[i][k] and B[k][j]]
            if len(selected)>1:raise ValueError('Multiple routes can interfere inside one bank block; the unique-path proof does not apply')
            if selected:
                k=selected[0];paths[i,j]=dict(route_bank=k,coefficient=A[i][k]*B[k][j])
    return paths


def route_image(address,columns,offset):
    out=offset
    for i,col in enumerate(columns):
        if address>>i&1:out^=col
    return out


def verify_case(case):
    f=case['selected_columns'];W=case['physical_banks'];D=1<<f;events=case['preword_events']
    if W!=6 or f not in (2,4):raise ValueError('Input is outside the bounded retained preflight')
    if len(events)!=36:raise ValueError('The two-stage word has the wrong complete event count')
    stages=[events[:6],events[6:15],events[15:21],events[21:27],events[27:]]
    if [[event['kind'] for event in stage] for stage in stages]!=[['amplitude']*6,['add']*9,['route']*6,['amplitude']*6,['add']*9]:
        raise ValueError('The path theorem requires two matching mixers separated by per-bank routes')
    for stage in (stages[0],stages[3]):
        if sorted(event['bank'] for event in stage)!=list(range(W)):raise ValueError('Amplitude bank stock is incomplete')
        if any(event['flip'] not in (0,1) for event in stage):raise ValueError('An amplitude rule is not the declared nonzero dyadic control')
    if sorted(event['bank'] for event in stages[2])!=list(range(W)):raise ValueError('Routing bank stock is incomplete')
    for event in stages[2]:
        if len(event['columns'])!=f or not 0<=event['offset']<D:raise ValueError('Malformed full-address route')
        images=[route_image(a,event['columns'],event['offset']) for a in range(D)]
        if sorted(images)!=list(range(D)):raise ValueError('A complete per-bank address route is not invertible')
    A=inverse_mix(stages[1],W);B=inverse_mix(stages[4],W);paths=single_paths(A,B,W)
    sources=(0,1);dense_blocks=[];dense_per_bank=[]
    for i in range(W):
        selected=[]
        for j in sources:
            if (i,j) in paths:
                selected.append(j);dense_blocks.append(dict(output_bank=i,source_bank=j,**paths[i,j]))
        if not selected:raise ValueError('This row lacks the retained dense source-block witness')
        dense_per_bank.append(len(selected))
    lower=max(dense_per_bank)*D;layers=0
    while W**layers<lower:layers+=1
    actual=case['required_post_support']['maximum_coordinate_support']
    if actual<lower:raise ValueError('The finite required post contradicts the proved dense source-block support')
    failed=False
    try:single_paths(A,A,W)
    except ValueError:failed=True
    if not failed:raise ValueError('Repeated matching must defeat the unique-path assumption')
    return dict(selected_columns=f,layout=case['layout'],physical_banks=W,first_inverse_mixer=A,second_inverse_mixer=B,
                source_block_paths=dense_blocks,dense_source_blocks_per_output_bank=dense_per_bank,
                finite_maximum_post_support_lower=lower,finite_recorded_maximum_post_support=actual,
                finite_necessary_post_layers=layers,all_size_lower='T>=log_W(2*2^f); in particular T=Omega(f) for fixedW',
                premise='Each source-bank block of B^-1 has exactly zero or one weighted route, and the amplitudes/routes are everywhere invertible.',
                algebra='R=Q*B^-1*P0^-1; source P0_j=I, hence R_ij=C_f*(B^-1)_ij. A nonzero weighted monomial maps each dense C_f row to another fully dense row.',
                negative_controls={'repeat_same_bank_matching':'UNIQUE-PATH PREMISE REJECTED'},
                scope='This is a scoped all-size unique-path preword obstruction. Several routes per same bank block, another quotient/core, fused implementations or a changed assembly remain open.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,default=TOPIC/'runs/20261009T033016Z-synthesis-nonunit-amplitude-preflight/results/certificate.json')
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError('A fresh output is required')
    source=Path(__file__);before_source=sha256(source.read_bytes()).hexdigest();input_bytes=args.certificate.read_bytes();input_hash=sha256(input_bytes).hexdigest()
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=1,seed=None,
                  source_sha256={source.name:before_source},input_certificate=str(args.certificate),input_sha256=input_hash,
                  input_bytes=len(input_bytes),stdlib_only=True,hypothesis='A preprocessor with at most one route per source bank block cannot remove dense required post rows, even with arbitrary nonunit address amplitudes.')
    results=[verify_case(case) for case in json.loads(input_bytes)['cases']]
    if len(results)!=4:raise ValueError('The complete four-case preflight input is required')
    if sha256(args.certificate.read_bytes()).hexdigest()!=input_hash or sha256(source.read_bytes()).hexdigest()!=before_source:raise ValueError('An immutable input/source changed during verification')
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (args.output/'certificate.json').write_text(json.dumps(dict(status='PASS SCOPED ALL-SIZE UNIQUE-PATH OBSTRUCTION',cases=results),indent=2)+'\n')
    print(json.dumps(dict(status='PASS SCOPED ALL-SIZE UNIQUE-PATH OBSTRUCTION',cases=len(results),source_block_paths=sum(len(r['source_block_paths']) for r in results))))


if __name__=='__main__':main()
