#!/usr/bin/env python3
"""Cheap exact controls for eliminating one complex central channel.

The old side graph and accepted source/certificates remain immutable.
No new full h50 side replay is necessary: the central factorization is
verified on every gather column and scatter row, and h8 has a complete
forward/inverse scalar basis check.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import time

from downstream_complex_circuit import TripleSideCircuit,mixer
from downstream_complex_assembly import compose
from downstream_gaussian import check_sources,require
from downstream_parameter_optimum import as_strings


def factorization(h):
    triples=list(combinations(range(h),3));gather=scatter=0
    for t in triples:
        retained=[int(j in t) for j in range(1,h)]+[1]
        reconstructed_zero=3*retained[-1]-sum(retained[:-1])
        require(reconstructed_zero==int(0 in t),'Deleted central gather column is not reconstructed')
        require(sum(int(j in t) for j in range(h))==3,'Original gather increment relation failed')
        gather+=1
    for s in triples:
        expected=[int(j in s)-int(0 in s) for j in range(1,h)] + [3*int(0 in s)-1]
        if 0 in s:actual=[-int(j not in s) for j in range(1,h)]+[2]
        else:actual=[int(j in s) for j in range(1,h)]+[-1]
        require(actual==expected,'Deleted-channel scatter row identity failed')
        require(all(c in (-1,0,1,2) for c in actual),'Scatter introduced non-Gaussian-dyadic coefficients')
        scatter+=1
    return dict(h=h,exact_gather_columns=gather,exact_scatter_rows=scatter,
                identity='R_reduced G_reduced = R_original G_original by exact column reconstruction and row substitution',
                central_channels=h,coefficients='0,+/-1,+/-1/2; no division by3')


def invoke(circuit,code,x,y,z,c,inverse=False):
    h=circuit.h
    def action(kind,sign):
        if kind=='mix':mixer(z,code,inverse=(sign<0))
        elif kind=='inject':
            for i,t in enumerate(circuit.inputs):
                value=z[code['outputs']['D',t]]-z[code['outputs']['E',t]]
                require(value%2==0,'Probe side half is not represented exactly')
                y[i]+=sign*(value//2)
        elif kind=='copy':
            for i,t in enumerate(circuit.inputs):z[code['sources'][t]]+=sign*x[i]
        elif kind=='gather':
            for i,t in enumerate(circuit.inputs):
                for j in t:
                    if j:c[j-1]+=sign*x[i]
                c[-1]+=sign*x[i]
        else:
            require(kind=='scatter','Unknown scalar action')
            for i,t in enumerate(circuit.inputs):
                if 0 in t:value=2*c[-1]-sum(c[j-1] for j in range(1,h) if j not in t)
                else:value=sum(c[j-1] for j in t)-c[-1]
                require(value%2==0,'Probe reduced central half is not represented exactly')
                y[i]+=sign*(value//2)
    schedule=[('mix',1),('inject',-1),('mix',-1),('scatter',-1),
              ('copy',1),('gather',1),('scatter',1),('mix',1),
              ('inject',1),('mix',-1),('gather',-1),('copy',-1)]
    if inverse:schedule=[(kind,-sign) for kind,sign in reversed(schedule)]
    for kind,sign in schedule:action(kind,sign)


def local_basis():
    circuit=TripleSideCircuit(8);code=circuit.compile();v=len(circuit.inputs);r=code['roles'];h=8
    dim=2*v+r+h;probes=0
    for inverse in [False,True]:
        for coordinate in range(dim+3):
            if coordinate<dim:
                flat=[0]*dim;flat[coordinate]=2
            else:flat=[2*(((j*97+(coordinate-dim)*31)%509)-254) for j in range(dim)]
            x=flat[:v];y=flat[v:2*v];z=flat[2*v:2*v+r];c=flat[2*v+r:]
            before=[a[:] for a in (x,y,z,c)]
            invoke(circuit,code,x,y,z,c,inverse)
            sign=-1 if inverse else 1
            require(x==before[0] and y==[a+sign*b for a,b in zip(before[1],before[0])]
                    and z==before[2] and c==before[3], 'Reduced-center dirty identity failed')
            probes+=1
    return dict(h=8,complete_scalar_dimension=dim,orientations=2,
                exact_basis_checks=2*dim,dirty_signed_checks=6,total_probes=probes,
                all_data_maps_and_arbitrary_scratch_restoration_exact=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--upstream',type=Path,required=True)
    ap.add_argument('--bit-certificate',type=Path,required=True)
    ap.add_argument('--complex-certificate',type=Path,required=True)
    ap.add_argument('--original-assembly',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    start=time.monotonic();provenance=check_sources(args.upstream)
    bit=json.loads(args.bit_certificate.read_text());cx=json.loads(args.complex_certificate.read_text())
    original=json.loads(args.original_assembly.read_text())
    require(bit['provenance']['commit']==cx['provenance']['commit']==original['provenance']['commit']==provenance['commit'],
            'Immutable certificate inputs disagree')
    row=next(r for r in cx['cases'] if r['h']==50)
    previous=row['shared_complex_counts'];h=50;v=comb(h,3);n=v**3;m=h**3;r=previous['R']
    w=2*n+2*v*v*(r+h);loss=3*v*v*h*h;deficit=2*n-2*loss;s=w*m-deficit
    nc=dict(h=h,v=v,m=m,N=n,R=r,W=w,L=loss,D=deficit,s=s,eta=Q(deficit,w*m))
    require(previous['W']-w==2*v*v and previous['L']-loss==3*v*v*h,
            'Central deletion role/rank count changed')
    require(deficit-previous['D']==6*v*v*h,'Central decrease improvement failed')
    require(3*v*v*(4*r+4)<6*w,'Old grouped gate charge is no longer valid')
    require(12*w**3+4*s+4*w+4<64*(w+m+1)**3,'Old additive guard failed')
    nbit={k:(Q(value) if k=='eta' else value) for k,value in original['witnesses'][0]['bit_counts'].items()}
    old_phase_kappa=Q(bit['best']['parameters']['kappa'])
    conservative=compose(nbit,nc,'conservative',old_phase_kappa)
    tight=compose(nbit,nc,'tight',old_phase_kappa)
    original_tight=next(r for r in original['witnesses'] if r['mode']=='tight' and r['complex_counts']['W']==previous['W'])
    require(tight['parameters']['kappa']==Q(original_tight['parameters']['kappa']),
            'Unexpected changed tight kappa after nonlimiting central refinement')
    require(tight['minimum_margin']==Q(original_tight['minimum_margin']),
            'The supposedly prefix-limited minimum changed')
    source=Path(__file__);names=['downstream_complex_reduced_center.py','downstream_complex_assembly.py',
                              'downstream_complex_circuit.py','downstream_gaussian.py','downstream_parameter_optimum.py']
    result=dict(campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',
                campaign_deadline='2026-10-08T08:25:21Z',provenance=provenance,
                source_sha256={name:hashlib.sha256((source.parent/name).read_bytes()).hexdigest() for name in names},
                input_certificates={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                    for p in [args.bit_certificate,args.complex_certificate,args.original_assembly]},
                central_factorization=[factorization(8),factorization(50)],local_scalar_basis=local_basis(),
                previous_complex_counts=previous,reduced_complex_counts=nc,
                compositions=[conservative,tight],tight_kappa_exactly_unchanged=True,
                common_cutoff_exactly_unchanged=tight['cutoff_log2_b']['common']==original_tight['cutoff_log2_b']['common'],
                generated_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-start,
                status='PASS cheap central elimination; scalar/frame/rank derivation needs separate independent review; no new tight kappa')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(as_strings(result),indent=2,sort_keys=True)+'\n')
    print('PASS reduced center',dict(W=w,L=loss,D=deficit,s=s,kappa=str(tight['parameters']['kappa']),
                                    common_cutoff=tight['cutoff_log2_b']['common']),flush=True)


if __name__=='__main__':main()
