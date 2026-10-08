#!/usr/bin/env python3
"""Independently replay every unlucky-prime fixed-geometry pair over Q.

The actual Cartesian nonvanishing certificates remain the complete proofs.
These distinct controls verify every preserved primary zero, its nonzero
rational pivot and the entire successful alternate-prime prefix sequence.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificates',nargs='+',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    args=ap.parse_args()
    assert __debug__ and not args.output.exists()
    args.output.mkdir(parents=True)
    rows=[]
    inputs=[]
    for path in args.certificates:
        raw=path.read_bytes()
        if path.suffix=='.gz':raw=gzip.decompress(raw)
        record=json.loads(raw)
        geometry,actual=record['analytic_geometry'],record['all_actual_pairs']
        a,b=geometry['dimensions'];d=geometry['d']
        primary=actual['primes'][0]
        assert actual['unresolved_failures']==0 and actual['primary_modular_failures']==len(actual['fallbacks'])
        inputs.append(dict(path=str(path),sha256_decompressed=hashlib.sha256(raw).hexdigest()))
        for case in actual['fallbacks']:
            left,right=set(case['left']),set(case['right'])
            def reciprocals(h,selected):
                inside=Q(6*h-14,3*(h+1));outside=-Q(5,h+1)
                assert 3*inside+(h-3)*outside==1
                return [1/(inside if i in selected else outside) for i in range(h)]
            x,y=reciprocals(a,left),reciprocals(b,right)
            R,C=geometry['row_edges'],geometry['column_edges']
            matrix=[[Q(r==c)*x[r]+Q(beta==gamma)*y[beta]-1 for c,gamma in C]
                    for r,beta in R]
            available=set(range(d));values=[];pivots=[]
            for i in range(d):
                col=max(j for j in available if matrix[i][j])
                assert col==geometry['prescribed_pivots'][i]
                value=matrix[i][col]
                assert value
                pivots.append(col);values.append(value);available.remove(col)
                active=[j for j in available if matrix[i][j]]
                for k in range(i+1,d):
                    if matrix[k][col]:
                        ratio=matrix[k][col]/value
                        for j in active:matrix[k][j]-=ratio*matrix[i][j]
                        matrix[k][col]=0
            i,col=case['primary_zero']
            assert pivots[i]==col
            failed=values[i]
            assert failed.denominator%primary and failed.numerator%primary==0
            alternate=case['successful_prime']
            assert all(v.numerator%alternate and v.denominator%alternate for v in values)
            canonical=('\n'.join(str(v) for v in values)+'\n').encode()
            row=dict(dimensions=[a,b],index=case['index'],left=case['left'],right=case['right'],
                     primary_prime=primary,primary_zero=case['primary_zero'],
                     exact_nonzero_failed_pivot=str(failed),successful_prime=alternate,
                     every_rational_pivot_nonzero=True,every_alternate_pivot_admissible=True,
                     ordered_rational_pivots_sha256=hashlib.sha256(canonical).hexdigest())
            rows.append(row)
            (args.output/'progress.json').write_text(json.dumps(dict(completed=len(rows),rows=rows),indent=2)+'\n')
    result=dict(status='all_preserved_unlucky_prime_pairs_replayed_exactly',
                completed_utc=datetime.now(timezone.utc).isoformat(),cases=len(rows),rows=rows,
                inputs=inputs,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='Independent exact rational fallback controls; complete Cartesian certificates and universal incidence proofs remain separate')
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],cases=len(rows))),flush=True)


if __name__=='__main__':
    main()
