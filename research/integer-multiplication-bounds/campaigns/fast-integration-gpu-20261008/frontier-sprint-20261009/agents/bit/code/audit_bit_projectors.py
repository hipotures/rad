#!/usr/bin/env python3
"""Exact finite prime-unit witnesses for every actual paired-bit frame.

The smaller primal or annihilator presentation is chosen. Integer kernel
identities and dimensions are checked afresh. A determinant is a unit for all
q>2^80 when division by explicitly recorded small prime powers leaves an
integer with magnitude below2^80; that last integer need not be factored.
All inherited finite source exclusions are retained regardless of this audit.
Prepared for RaD with OpenAI assistance. Inherited geometry is Apache-2.0.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from math import gcd
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True


def need(ok,msg):
    if not ok:raise ValueError(msg)


def det(matrix):
    """Fraction-free Bareiss determinant with exact division checks."""
    n=len(matrix)
    if not n:return 1
    a=[list(row) for row in matrix];sign=1;previous=1
    for k in range(n-1):
        if not a[k][k]:
            j=next((j for j in range(k+1,n) if a[j][k]),None)
            if j is None:return 0
            a[k],a[j]=a[j],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                x=a[i][j]*pivot-a[i][k]*a[k][j]
                need(x%previous==0,'exact Bareiss division')
                a[i][j]=x//previous
            a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]


def integer_rank(rows,h):
    """Independent forward elimination over Q, using primitive integer rows."""
    pivots={}
    for row in rows:
        r=list(row)
        for c,p in sorted(pivots.items()):
            if r[c]:
                a,b=p[c],r[c]
                r=[a*x-b*y for x,y in zip(r,p)]
                common=0
                for x in r:common=gcd(common,abs(x))
                if common>1:r=[x//common for x in r]
        c=next((i for i,x in enumerate(r) if x),None)
        if c is not None:pivots[c]=r
    return len(pivots)


def audit(experiment):
    c=experiment.c;h=c.h
    used=set(experiment.frames)|set(experiment.start)|set(experiment.rootframe.values())
    used.update(c.w['source_frame']);used.add(c.w['full_frame'])
    for entry in c.k['entries']:
        for key in ['mix_frame','deliver_frame','undo_frame']:used.add(entry[key])
        used.update(entry['carrier_chain']);used.update(entry['passive_chain'])
    # The zero endpoint is a valid rank-zero frame with determinant one.
    records=[];maximum=0;maxresidual=0
    for f in sorted(used):
        B,A=c.B[f],c.A[f]
        need(integer_rank(B,h)==len(B) and integer_rank(A,h)==len(A),
             'independent exact ranks of both frame presentations')
        need(len(A)+len(B)==h,'intended frame dimension from exact kernel')
        need(all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B),'exact A B^t=0')
        rows=B if len(B)<=len(A) else A
        sums=[sum(x) for x in rows]
        matrix=[[9*sum(x*y for x,y in zip(a,b))-sums[i]*sums[j] if rows is B else
                 (9-h)*sum(x*y for x,y in zip(a,b))+sums[i]*sums[j]
                 for j,b in enumerate(rows)] for i,a in enumerate(rows)]
        determinant=det(matrix);need(determinant!=0,'actual selected projector nondegenerate')
        residual=abs(determinant);powers={}
        for prime in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]:
            exponent=0
            while residual%prime==0:residual//=prime;exponent+=1
            if exponent:powers[str(prime)]=exponent
        need(residual<2**80,'remaining Gram factor below retained prime bound')
        maximum=max(maximum,abs(determinant).bit_length());maxresidual=max(maxresidual,residual.bit_length())
        records.append(dict(frame_id=f,dimension=len(B),representation='basis' if rows is B else 'annihilator',
                            defining_integer_rows=[list(x) for x in rows],cleared_gram_determinant=determinant,
                            stripped_prime_powers=powers,residual=residual,
                            rational_basis_sha256=hashlib.sha256(json.dumps([list(x) for x in B],separators=(',',':')).encode()).hexdigest(),
                            exact_ABt_zero=True,exact_dimensions_sum_to_h=True))
    return dict(status='PASS exact finite projector prime units',h=h,actual_used_frames=len(used),
                maximum_selected_Gram_determinant_bits=maximum,maximum_residual_bits=maxresidual,
                prime_lower_bound=2**80,inherited_finite_source_exclusions_retained=True,
                added_excluded_primes_above_retained_lower_bound=[],
                ambient_cleared_Gram_determinant=9**(h-1)*(9-h),
                independent_integer_ranks_checked_for_every_primal_and_annihilator=True,
                chosen_presentations=Counter(x['representation'] for x in records),frame_witnesses=records,
                proof='Each exact B frame equals ker A by ABt=0 and complementary ranks. All selected Gram factors are below2^80 after explicit small-prime divisions; thus determinants and9/(9-h) are units for every already-allowed q>2^80 at all local-ring depths. Primal or kernel projector formulas define the same rational frame, free split image, containment and nesting. All inherited exclusions persist.',
                scope='Finite projector compatibility; inherited uniform compiler and full final assembly remain separate.')


def main():
    need(not sys.flags.optimize,'assertions enabled')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source170',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();need(not args.output.exists(),'fresh audit directory');args.output.mkdir(parents=True)
    started=time.monotonic();source=args.source170.resolve()
    spec=importlib.util.spec_from_file_location('source170_lifetime',source/'research/paired-cube-lifetime/bit.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    experiment=module.Experiment(baseline=args.baseline,p=12,quiet=True)
    experiment.load(args.plan,require_pins=True)
    result=audit(experiment);result.update(verified_utc=datetime.now(timezone.utc).isoformat(),
        plan_sha256=hashlib.sha256(args.plan.read_bytes()).hexdigest(),
        audit_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        baseline_sha256=experiment.source_hashes(),wall_seconds=time.monotonic()-started)
    (args.output/'prime-witnesses.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    compact={k:v for k,v in result.items() if k!='frame_witnesses'}
    (args.output/'receipt.json').write_text(json.dumps(compact,indent=2,sort_keys=True)+'\n')
    print(json.dumps(compact),flush=True)


if __name__=='__main__':main()
