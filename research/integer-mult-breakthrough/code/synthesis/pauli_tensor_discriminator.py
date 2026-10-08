#!/usr/bin/env python3
"""Literal finite Pauli expansion and its exact tensor-support obstruction.

C=(1+i)I/2+(1-i)X/2. A direct Pauli-sum shear uses no C child on
the two data banks, but C_h tensor f has exactly 2**(h*f) Pauli terms.
This is a different physical operator word, not the old common-frame
constant-scalar state model. No native cost or multiplication saving follows.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time

ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0));ALPHA=(Q(1,2),Q(1,2));BETA=(Q(1,2),Q(-1,2))


def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[0],-a[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def power(a,n):
    z=ONE
    for _ in range(n):z=mul(z,a)
    return z
def scale(a,n):return a[0]*n,a[1]*n
def text_complex(a):return [str(a[0]),str(a[1])]


def tensor_c(n):
    C=((ALPHA,BETA),(BETA,ALPHA));A=[[ONE]]
    for _ in range(n):
        d=len(A)
        A=[[mul(A[a//2][b//2],C[a%2][b%2]) for b in range(2*d)] for a in range(2*d)]
    return A


def pauli_coefficients(A):
    """Independent full Hilbert-Schmidt projection onto all X^u Z^v."""
    d=len(A);n=(d-1).bit_length();nonzero={};digest=sha256()
    for u in range(d):
        for v in range(d):
            z=ZERO
            for b in range(d):z=add(z,neg(A[b^u][b]) if (v&b).bit_count()%2 else A[b^u][b])
            z=(z[0]/d,z[1]/d)
            if z!=ZERO:nonzero[u,v]=z
            digest.update(json.dumps([u,v,text_complex(z)],separators=(',',':')).encode())
    return nonzero,dict(full_pauli_basis_elements=d*d,coefficient_sha256=digest.hexdigest(),nonzero_coefficients=len(nonzero))


def literal_shear(h,f,omit=None,include_helper=True):
    n=h*f;d=1<<n;A=tensor_c(n);weights={s:mul(power(ALPHA,n-s.bit_count()),power(BETA,s.bit_count())) for s in range(d)}
    # Full scalar/address rows include source, preexisting sink and arbitrary dirty helper.
    rows=[{j:ONE} for j in range(3*d if include_helper else 2*d)]
    current_mask=0;moves=[];shears=[]
    for j in range(d):
        mask=j^(j>>1);delta=current_mask^mask
        if delta:
            old=rows[:d];rows[:d]=[dict(old[a^delta]) for a in range(d)];moves.append(delta)
        current_mask=mask
        if mask==omit:continue
        coefficient=weights[mask]
        for a in range(d):
            for column,z in rows[a].items():
                new=add(rows[d+a].get(column,ZERO),mul(coefficient,z))
                if new==ZERO:rows[d+a].pop(column,None)
                else:rows[d+a][column]=new
        shears.append(mask)
    if current_mask:
        old=rows[:d];rows[:d]=[dict(old[a^current_mask]) for a in range(d)];moves.append(current_mask)
    if include_helper:
        # One preexisting full-width C_h tensor f call on the dirty helper;
        # this is counted rather than silently restoring it to identity.
        rows[2*d:]=[{2*d+b:A[a][b] for b in range(d) if A[a][b]!=ZERO} for a in range(d)]
    expected=[{j:ONE} for j in range(d)]+[
        {d+a:ONE,**{b:A[a][b] for b in range(d) if A[a][b]!=ZERO}} for a in range(d)]
    if include_helper:expected +=[{2*d+b:A[a][b] for b in range(d) if A[a][b]!=ZERO} for a in range(d)]
    bad=[a for a in range(len(rows)) if rows[a]!=expected[a]]
    if bool(bad)!=(omit is not None):raise ValueError('Complete finite source/sink/dirty operator replay failed')
    witness=None
    if bad:
        a=bad[0];b=next(b for b in sorted(set(rows[a])|set(expected[a])) if rows[a].get(b,ZERO)!=expected[a].get(b,ZERO))
        witness=dict(output_role=a//d,output_address=a%d,initial_role=b//d,initial_address=b%d,
                     expected=text_complex(expected[a].get(b,ZERO)),observed=text_complex(rows[a].get(b,ZERO)))
    digest=sha256()
    for a,row in enumerate(rows):
        digest.update(json.dumps([a,[[b,text_complex(z)] for b,z in sorted(row.items())]],separators=(',',':')).encode())
    return dict(h=h,f=f,active_bits=n,address_volume=d,payload_roles=3 if include_helper else 2,
                complete_initial_columns=len(rows),source_columns=d,sink_columns=d,arbitrary_dirty_columns=d if include_helper else 0,
                source_restored=omit is None,sink_C_h_tensor_f_shear_exact=omit is None,
                dirty_helper_C_h_tensor_f_exact=include_helper and omit is None,
                nonrecursive_coefficient_shears=len(shears),paid_address_X_permutations=len(moves),
                address_xor_masks=moves,omitted_term=omit,counterexample=witness,full_operator_rows_sha256=digest.hexdigest(),
                recursive_C_calls=int(include_helper),recursive_C_call_width=h if include_helper else None,
                max_coefficient_denominator=max(q.denominator for c in weights.values() for q in c),
                scope='Literal finite Gaussian-rational physical word and complete column replay. Coefficient shears and address XOR permutations are paid separate operations; no old common-frame rank certificate, uniform tensor cost, tape theorem or exponent is asserted.')


def tensor_probe(h,f):
    started=time.monotonic();n=h*f;d=1<<n;A=tensor_c(n);nonzero,receipt=pauli_coefficients(A)
    expected={(s,0):mul(power(ALPHA,n-s.bit_count()),power(BETA,s.bit_count())) for s in range(d)}
    if nonzero!=expected or any(z==ZERO for z in expected.values()):raise ValueError('Full Pauli projection or exponential support failed')
    if any(z[0]*z[0]+z[1]*z[1]!=Q(1,d) for z in expected.values()):raise ValueError('Exact tensor coefficient norm mismatch')
    positive=literal_shear(h,f);negative=literal_shear(h,f,omit=1)
    # Carrying only the two f=1 endpoint terms cannot implement f>1.
    two=[[ZERO]*d for _ in range(d)]
    for b in range(d):two[b][b]=power(ALPHA,n);two[b^(d-1)][b]=power(BETA,n)
    mismatch=[(a,b) for a in range(d) for b in range(d) if two[a][b]!=A[a][b]]
    if bool(mismatch)!=(n>1):raise ValueError('Two-term replication corruption control failed')
    witness=None
    if mismatch:
        a,b=mismatch[0];witness=dict(output_address=a,input_address=b,expected=text_complex(A[a][b]),
                                  two_term_observed=text_complex(two[a][b]))
    return dict(status='EXACT FINITE PAULI WORD AND TENSOR SUPPORT PASS',h=h,f=f,active_bits=n,
                complete_pauli_projection=receipt,necessary_terms_in_one_layer_Pauli_sum=d,
                positive=positive,matched_omitted_term=negative,
                two_endpoint_terms_tensor_control=dict(matches_only_single_active_bit=n==1,counterexample=witness),
                seconds=time.monotonic()-started,
                interpretation='Finite no-data-C-child operator construction uses 2^(h*f) coefficient shears. Pauli basis uniqueness makes this term count unavoidable in the direct linear-sum family. Tensor replication is not free; this family cannot be assigned a constant/poly(f) per-word overhead.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--bounded',action='store_true');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);specs=[(1,1),(1,2)] if a.bounded else [(1,1),(1,2),(2,2),(2,3)]
    source=Path(__file__);original=sha256(source.read_bytes()).hexdigest()
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=a.workers,native_threads_each=1,
                  specs=specs,seed=None,source_sha256={source.name:original},scalar_domain='Exact Gaussian rationals')
    (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');cases=[]
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        jobs={pool.submit(tensor_probe,*spec):spec for spec in specs}
        for future in as_completed(jobs):
            result=future.result();cases.append(result)
            print(json.dumps({k:result[k] for k in ('h','f','status','necessary_terms_in_one_layer_Pauli_sum','seconds')}),flush=True)
    if sha256(source.read_bytes()).hexdigest()!=original:raise ValueError('Source changed during exact experiment')
    (a.output/'certificate.json').write_text(json.dumps(dict(cases=cases),indent=2)+'\n')


if __name__=='__main__':main()
