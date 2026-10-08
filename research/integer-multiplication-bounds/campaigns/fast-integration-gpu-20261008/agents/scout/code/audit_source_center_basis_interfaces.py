#!/usr/bin/env python3
"""Exact common-basis source and copied-center interfaces for closed DATA cases."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import combinations
import json
from pathlib import Path


def record(path):
    data = path.read_bytes()
    return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def basis(h,beta):
    star = (1-9*beta)/(9*(1-h*beta))
    gamma = -3*star
    assert beta+star-h*beta*star == F(1,9)
    primal = (1-3*beta,-3*beta)
    dual = ((1+gamma)/2,gamma/2)
    products = tuple(a*b for a,b in zip(primal,dual))
    c = (2-3*beta*(h-3))/(h-9)
    k = F(h-9,4)
    v = F(h-9)*(1-3*beta)/(12*(1-h*beta))
    center_primal = (1+c,c)
    center_dual = (v-k,v)
    assert all(primal+dual+center_primal+center_dual)
    assert 3*products[0]+(h-3)*products[1] == 1
    assert center_primal[0]*center_dual[0]+(h-1)*center_primal[1]*center_dual[1] == 1
    # Direct H0-Gram checks on the unchanged unnormalized source and center.
    source_norm = F(3)-F(9,9)
    a = F(2,h-9)
    center_norm = 1+2*a+h*a*a-F(1,9)*(1+h*a)**2
    assert source_norm == 2 and center_norm == -1/k
    # L_star L_beta=H0 gives the stated normalized dual vectors directly.
    source_star = (1-3*star,-3*star)
    center_cstar = (2-3*star*(h-3))/(h-9)
    assert source_star == tuple(2*z for z in dual)
    assert (1+center_cstar,center_cstar) == tuple(-z/k for z in center_dual)
    return {'h':h,'beta':str(beta),'conjugate_beta':str(star),'gamma':str(gamma),
            'source_primal':list(map(str,primal)),'source_dual':list(map(str,dual)),
            'source_coordinate_products':list(map(str,products)),
            'source_H0_norm':str(source_norm),'center_H0_norm':str(center_norm),
            'center_primal':list(map(str,center_primal)),'center_dual':list(map(str,center_dual)),
            'all_source_and_center_coordinates_nonzero':True,
            'all_source_and_center_normalizations_exactly_one':True,
            'conjugate_DATA_products_identical':True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-interface-receipt',type=Path,required=True)
    ap.add_argument('--data-certificates',type=Path,nargs='+',required=True)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    source_interface = json.loads(args.source_interface_receipt.read_text())
    assert source_interface['full_DATA_sources'] == 4073300
    assert len(source_interface['actual_source_terminal_word_checks']) == 2
    for row in source_interface['actual_source_terminal_word_checks']:
        h = row['h']
        assert row['source_frames_checked'] == len(list(combinations(range(h),3)))
        assert row['ordinary_outputs_checked'] == 3*row['source_frames_checked']
        assert row['copied_centers_checked'] == h
    cases = []
    for path in args.data_certificates:
        data = json.loads(path.read_text())
        if 'beta23' in data:
            pair = (F(data['beta23']),F(data['beta25']))
            assert data['status'] == 'PASS COMPLETE RATIONAL UNIFORM DATA FAMILY'
        else:
            pair = (F(-1),F(-1,3))
            assert data['status'] == 'PASS MIXED FULL DATA INPUT, UNIVERSAL ZERO CUTS AND UNLUCKY-PAIR Q CONTROLS'
        assert data['pairs'] == 4073300
        profiles = [basis(h,b) for h,b in zip((23,25),pair)]
        inverse = [[str(1/F(z)) for z in x['source_coordinate_products']] for x in profiles]
        assert inverse == data['inverse_source_products']
        cases.append({'data_certificate':record(path),'basis_interfaces':profiles,
                      'complete_source_and_center_family':'All lexical triples and all singleton centers already bound to actual pinned scalar words by the source-interface receipt. Changing L_beta changes the common address realization while these full source/output families and scalar words stay fixed.',
                      'copied_center_transfer':'Source and center primal/dual coordinates are nonzero and normalized; same common invertible L_beta maps all local frames. Each actual full-cover center output retains its paid entrance and rank-one original cleanup. No charge is removed.',
                      'DATA_transfer':'The inverse source products equal the exact fullN certificate. Conjugating one or both beta roots preserves these products, so the identical full normalized DATA matrix is reused. Local NE profiles for the conjugate basis are separate.'})
    result = {'created_utc':datetime.now(timezone.utc).isoformat(),
              'status':'PASS COMMON-BASIS SOURCE, COPIED-CENTER AND CLOSED DATA INTERFACES',
              'source':record(Path(__file__)),'actual_source_interface':record(args.source_interface_receipt),
              'cases':cases,
              'remaining_gates':'Actual local projector profiles, full dirty scalar replay, physical carrier recovery, scalar overhead and final characteristic/bridge assembly remain independent gates. No multiplication bound is inferred from this interface alone.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'closed_basis_pairs':[[x['beta'] for x in case['basis_interfaces']] for case in cases]}))


if __name__ == '__main__':
    main()
