#!/usr/bin/env python3
"""Adversarial unrestricted arrays for the actual bit address shear Phi_M.

The pinned public motif contract permits arbitrary physical wire arrays.
A source-support orthogonality identity does not impose a ridge restriction.
This falsifies the proposed uncharged terminal substitution under that contract.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

from source_ridge_terminal_defect_controls import center, dot, residue, source


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert not args.output.exists()
    p=257
    assert all(p%d for d in range(2,17))
    rows=[]
    for h,beta in [(23,Q(1,15)),(25,Q(7,207))]:
        t=(0,1,2);u=(0,3,4);c=0
        wt,dt=source(h,t,beta);wu,du=source(h,u,beta);wc,dc=center(h,c,beta)
        assert dot(dt,wt)==dot(dc,wc)==1
        assert dot(dt,wc)==dot(dc,wt)==dot(du,wt)==0
        pg=[[Q(i==j)-wc[i]*dc[j] for j in range(h)] for i in range(h)]
        pk=[[pg[i][j]-wt[i]*dt[j] for j in range(h)] for i in range(h)]
        assert all(pg[i][j]-pk[i][j]==wt[i]*dt[j] for i in range(h) for j in range(h))
        for orientation in ('forward','transposed'):
            # The literal address primitive translates H by M D and fixes D.
            # Choose D=e0 and an unrestricted delta at the K image of H=0.
            g=[residue(pg[i][0] if orientation=='forward' else pg[0][i],p) for i in range(h)]
            k=[residue(pk[i][0] if orientation=='forward' else pk[0][i],p) for i in range(h)]
            assert g!=k
            delta=lambda address:int(address==k)
            assert delta(k)==1 and delta(g)==0
            # Invertible source gauges are bijections on arbitrary arrays;
            # precomposing this delta with a source gauge remains admissible.
            rows.append(dict(h=h,beta=str(beta),orientation=orientation,
                             target=t,active_scalar_source=u,common=c,
                             legal_scalar_coefficient=1,digit_vector=[1]+[0]*(h-1),
                             gamma_image=g,kernel_image=k,
                             expected_delta_value=1,uncharged_substitution_value=0,
                             unrestricted_array_failure=True))
    d=dict(status='FAIL UNCHARGED GAMMA-TO-K TERMINAL SUBSTITUTION FOR UNRESTRICTED ARRAYS',
           classification='DISCOVERY NEGATIVE RESULT',created_utc=datetime.now(timezone.utc).isoformat(),
           source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
           source_revision='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
           contract={'path':'upstream/build/sections/03-motifs.tex',
                     'arbitrary_array_lines':[154,180],'bit_shear_lines':[474,486],
                     'operator':'Phi_M(H,D)=(H+MD,D)'},
           proven_prime=p,rows=rows,
           conclusion='Exact source covector orthogonality proves invariance of hypothetical ridges only. The inherited arbitrary-array contract admits delta inputs on which the actual terminal gauge substitution changes an output.',
           scope='Rejects the proposed free terminal substitution. It does not rule out newly proved restricted-source producers, explicitly paid transfers, or a different joint compilation architecture.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(status=d['status'],counterexamples=len(rows))))


if __name__=='__main__':
    main()
