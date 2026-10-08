#!/usr/bin/env python3
"""Literal linear-depth Gaussian-dyadic tensor chronology, with no C calls.

This compresses the direct 2**(h*f) Pauli sum using conditional in-place
shears and dyadic scales. Its 9*h*f+1 whole-bank stages are paid, not
constant-cost residual gauges. It is a baseline/discriminator, not an
integer-multiplication improvement or a native fixed-tape theorem.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

import pauli_tensor_discriminator as p

MINUS_I=(Q(0),Q(-1));PLUS_I=(Q(0),Q(1));GAMMA=(Q(1),Q(1))
ALPHA_INVERSE=(Q(1),Q(-1));GAMMA_INVERSE=(Q(1,2),Q(-1,2))


def multiply(A,B):
    return [[sum_gaussian(p.mul(A[a][j],B[j][b]) for j in range(len(B))) for b in range(len(B[0]))] for a in range(len(A))]


def sum_gaussian(values):
    answer=p.ZERO
    for z in values:answer=p.add(answer,z)
    return answer


def adjoint(A):return [[(A[b][a][0],-A[b][a][1]) for b in range(len(A))] for a in range(len(A[0]))]


def determinant2(A):return p.add(p.mul(A[0][0],A[1][1]),p.neg(p.mul(A[0][1],A[1][0])))


def factor_controls():
    I=[[p.ONE,p.ZERO],[p.ZERO,p.ONE]]
    U=[[p.ONE,MINUS_I],[p.ZERO,p.ONE]];D=[[p.ALPHA,p.ZERO],[p.ZERO,GAMMA]];L=[[p.ONE,p.ZERO],[MINUS_I,p.ONE]]
    Ui=[[p.ONE,PLUS_I],[p.ZERO,p.ONE]];Di=[[ALPHA_INVERSE,p.ZERO],[p.ZERO,GAMMA_INVERSE]];Li=[[p.ONE,p.ZERO],[PLUS_I,p.ONE]]
    C=[[p.ALPHA,p.BETA],[p.BETA,p.ALPHA]]
    if multiply(L,multiply(D,U))!=C or multiply(Ui,multiply(Di,Li))!=adjoint(C):
        raise ValueError('Exact dyadic shear/scale factorization failed')
    if multiply(adjoint(C),C)!=I:raise ValueError('Target one-bit C is not unitary')
    copy=[[p.ONE,p.ZERO],[p.ONE,p.ONE]];controls=[]
    for name,A in [('upper',U),('scaled_upper',multiply(D,U)),('inverse_lower',Li),('scaled_inverse_lower',multiply(Di,Li)),('bank_copy',copy)]:
        G=multiply(adjoint(A),A);trace=p.add(G[0][0],G[1][1]);det=determinant2(G)
        if trace!=(Q(3),Q()) or det!=p.ONE:raise ValueError('Partial-factor singular-value certificate failed')
        controls.append(dict(name=name,Gram_trace=p.text_complex(trace),Gram_determinant=p.text_complex(det),
                             largest_squared_singular_value='(3+sqrt(5))/2 < 3',smallest_squared_singular_value='(3-sqrt(5))/2 > 1/3'))
    return controls


def word(h,f):
    n=h*f;events=[]
    def c(bank,inverse=False):
        for bit in reversed(range(n)) if inverse else range(n):
            if inverse:events.extend([('conditional_shear',bank,bit,1,PLUS_I),('conditional_scale',bank,bit,ALPHA_INVERSE,GAMMA_INVERSE),('conditional_shear',bank,bit,0,PLUS_I)])
            else:events.extend([('conditional_shear',bank,bit,0,MINUS_I),('conditional_scale',bank,bit,p.ALPHA,GAMMA),('conditional_shear',bank,bit,1,MINUS_I)])
    c(0);events.append(('bank_copy',1,0));c(0,True);c(2)
    return events


def replay(h,f,corruption=None):
    n=h*f;d=1<<n;events=word(h,f);rows=[{j:p.ONE} for j in range(3*d)];source_stages=0
    for step,event in enumerate(events):
        kind,bank,*data=event
        if kind=='conditional_shear':
            bit,dest_value,c=data;mask=1<<bit
            if corruption=='wrong first shear sign' and step==0:c=p.neg(c)
            for a in range(d):
                if (a>>bit&1)!=dest_value:continue
                dest=bank*d+a;source=bank*d+(a^mask)
                for j,z in rows[source].items():
                    new=p.add(rows[dest].get(j,p.ZERO),p.mul(c,z))
                    if new!=p.ZERO:rows[dest][j]=new
                    else:rows[dest].pop(j,None)
        elif kind=='conditional_scale':
            bit,lo,hi=data
            if corruption=='omit first scale' and step==1:continue
            for a in range(d):
                coefficient=hi if a>>bit&1 else lo
                rows[bank*d+a]={j:p.mul(coefficient,z) for j,z in rows[bank*d+a].items()}
        else:
            source=data[0]
            for a in range(d):
                for j,z in rows[source*d+a].items():
                    new=p.add(rows[bank*d+a].get(j,p.ZERO),z)
                    if new!=p.ZERO:rows[bank*d+a][j]=new
                    else:rows[bank*d+a].pop(j,None)
    C=p.tensor_c(n)
    expected=[{j:p.ONE} for j in range(d)]+[{d+a:p.ONE,**{b:C[a][b] for b in range(d)}} for a in range(d)]+[
        {2*d+b:C[a][b] for b in range(d)} for a in range(d)]
    bad=[a for a in range(3*d) if rows[a]!=expected[a]]
    if bool(bad)!=(corruption is not None):raise ValueError('Full in-place address/dirty operator replay failed')
    witness=None
    if bad:
        a=bad[0];b=next(b for b in sorted(set(rows[a])|set(expected[a])) if rows[a].get(b,p.ZERO)!=expected[a].get(b,p.ZERO))
        witness=dict(output_role=a//d,output_address=a%d,initial_role=b//d,initial_address=b%d,
                     expected=p.text_complex(expected[a].get(b,p.ZERO)),observed=p.text_complex(rows[a].get(b,p.ZERO)))
    encoded=[[e[0],*e[1:4],*[p.text_complex(z) for z in e[4:]]] if e[0]=='conditional_shear' else
             [e[0],e[1],e[2],*[p.text_complex(z) for z in e[3:]]] if e[0]=='conditional_scale' else list(e) for e in events]
    digest=sha256()
    for a,row in enumerate(rows):digest.update(json.dumps([a,[[j,p.text_complex(z)] for j,z in sorted(row.items())]],separators=(',',':')).encode())
    return dict(h=h,f=f,active_bits=n,address_volume=d,complete_initial_columns=3*d,
                source_columns=d,sink_columns=d,arbitrary_dirty_columns=d,all_columns_exact=corruption is None,
                source_restored=corruption is None,dirty_helper_required_C_tensor_exact=corruption is None,
                recursive_C_calls=0,whole_bank_stages=len(events),conditional_address_shears=6*n,
                conditional_address_diagonal_stages=3*n,ordinary_bank_copies=1,
                elementary_two_address_shears=3*n*d,elementary_address_diagonal_multiplications=3*n*d,
                corruption=corruption,single_payload_counterexample=witness,
                events=encoded,full_operator_rows_sha256=digest.hexdigest(),
                scope='Exact finite physical address-controlled Gaussian shear/scale word with every source, sink and dirty column. Whole-bank stages grow linearly in h*f; each stage scans many address pairs. No fixed-tape routing/precision cost or exponent is certified.')


def probe(h,f):
    start=time.monotonic();controls=factor_controls();cases=[replay(h,f,c) for c in (None,'wrong first shear sign','omit first scale')]
    return dict(status='EXACT COMPRESSED GAUSSIAN CHRONOLOGY PASS',h=h,f=f,cases=cases,partial_factor_controls=controls,
                whole_prefix_operator_norm_bound='strictly less than 3',whole_prefix_inverse_norm_bound='strictly less than 3',
                condition_bound_scope='Analytic factor composition: completed tensor factors are unitary; each prefix contains at most one partial-factor and one bank-copy block, each norm and inverse norm < sqrt(3). Not a native precision or absolute rounding guarantee.',
                seconds=time.monotonic()-start)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--workers',type=int,default=4);ap.add_argument('--bounded',action='store_true');a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    specs=[(1,1),(1,2)] if a.bounded else [(1,1),(1,2),(2,2),(2,3)]
    paths=[Path(__file__),Path(p.__file__)];hashes={q:sha256(q.read_bytes()).hexdigest() for q in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=a.workers,native_threads_each=1,
                  specs=specs,seed=None,source_sha256={q.name:v for q,v in hashes.items()})
    (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs={pool.submit(probe,*spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps(dict(h=result['h'],f=result['f'],status=result['status'],stages=result['cases'][0]['whole_bank_stages'],seconds=result['seconds'])),flush=True)
    if any(sha256(q.read_bytes()).hexdigest()!=v for q,v in hashes.items()):raise ValueError('Effective source changed during run')
    (a.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
