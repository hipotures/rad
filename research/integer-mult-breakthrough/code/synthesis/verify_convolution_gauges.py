#!/usr/bin/env python3
"""Bounded convolution boundary checks and solver-free padded witness replay."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

import convolution_gauge_screen as c

FIXTURE=Path(__file__).resolve().parents[2]/'fixtures/synthesis/padded-convolution-eight.json'


def replay_fixture(fixture,corrupt=False):
    model=fixture['exact_model'];n=fixture['active_bits'];d=1<<n
    inputs=model['input_positions'];outputs=model['output_positions']
    sources=[tuple(c.g.Q(x) for x in z) for z in model['input_diagonal_coefficients']]
    rows=[tuple(c.g.Q(x) for x in z) for z in model['output_diagonal_coefficients']]
    phases={int(t):q for t,q in model['kernel_phases'].items()};low=min(phases)
    units=[c.g.ONE,(c.g.Q(0),c.g.Q(1)),(c.g.Q(-1),c.g.Q(0)),(c.g.Q(0),c.g.Q(-1))]
    if len(set(inputs))!=d or len(set(outputs))!=d or sorted(phases)!=list(range(low,max(phases)+1)):
        raise ValueError('Fixture positions/kernel extent are invalid')
    kernel=[units[phases[t]] for t in range(low,max(phases)+1)]
    if corrupt:kernel[-low]=c.g.mul(units[1],kernel[-low])
    target=c.g.tensor_c(n);checks=0;bad=[];digest=sha256()
    for y in range(d):
        polynomial=[c.g.ZERO]*model['polynomial_product_extent']
        for j,z in enumerate(kernel):polynomial[inputs[y]+j]=c.g.mul(sources[y],z)
        for x in range(d):
            actual=c.g.mul(rows[x],polynomial[outputs[x]])
            if actual!=target[x][y]:bad.append((x,y))
            digest.update(json.dumps([x,y,c.g.text_complex(actual)],separators=(',',':')).encode());checks+=1
    if bool(bad)!=corrupt:raise ValueError('Padded phase fixture positive/corruption control failed')
    if not corrupt and digest.hexdigest()!=model['exact_matrix_sha256']:
        raise ValueError('Padded witness complete coefficient hash changed')
    return dict(status='CORRUPTION DETECTED' if corrupt else 'EXACT PADDED WITNESS PASS',
                all_target_entries=checks,first_bad_entry=bad[0] if bad else None,
                exact_matrix_sha256=digest.hexdigest())


def verify():
    scans=[c.toeplitz_scan(n) for n in (1,2,3)]
    affine=[c.affine_cycles(n) for n in (1,2,3)]
    padding=c.padding_probe(3);fixture=json.loads(FIXTURE.read_text())
    witnesses=[replay_fixture(fixture),replay_fixture(fixture,True)]
    for n in (1,2,3):
        D=1<<n;C=c.g.tensor_c(n)
        for x in range(D):
            for y in range(D):
                chirp=c.g.mul(c.g.power(c.g.ALPHA,n),c.g.power((c.g.Q(0),c.g.Q(-1)),x.bit_count()+y.bit_count()))
                if c.g.scale(chirp,(-1)**((x&y).bit_count()%2))!=C[x][y]:
                    raise ValueError('Gaussian tensor/Walsh chirp identity failed')
    return dict(status='PASS EXACT CONVOLUTION GAUGE BOUNDARY',recorded_utc=datetime.now(timezone.utc).isoformat(),
                finite_Toeplitz_scans=scans,finite_affine_cycles=affine,quadratic_padding_control=padding,
                compact_padded_witnesses=witnesses,Gaussian_chirp_identity=True,
                scope='Finite exact permutation/gauge boundary and clean padded polynomial witnesses. All-N theorem is a separate proof; arbitrary padded/native circuits and exponent improvements are not excluded or certified.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);args=p.parse_args()
    result=verify();files=[Path(__file__),Path(c.__file__),Path(c.g.__file__),Path(c.__file__).with_name('lagrangian_graph_completion.py'),FIXTURE]
    result['source_sha256']={p.name:sha256(p.read_bytes()).hexdigest() for p in files}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],N3_representative_cases=result['finite_Toeplitz_scans'][2]['representative_cases'],
                         padded_coefficients=result['compact_padded_witnesses'][0]['all_target_entries'],kernel_corruption_detected=True)))


if __name__=='__main__':main()
