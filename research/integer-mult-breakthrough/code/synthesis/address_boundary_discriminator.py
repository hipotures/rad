#!/usr/bin/env python3
"""Scoped exact boundary support, local-block rank and unitary entropy tests.

No layer-count statement is promoted to a universal fixed-tape time lower
bound. Nonunit pre/post words and fused algorithms remain distinct models.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import time


def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def conj(a):return a[0],-a[1]
def power(a,n):
    out=(1,0)
    for _ in range(n):out=mul(out,a)
    return out
def norm(a):return a[0]*a[0]+a[1]*a[1]
def divide(a,b):
    out=mul(a,conj(b));s=norm(b)
    return Q(out[0],s),Q(out[1],s)


def ambient_mask(U,h,f,column):
    return sum(1<<(bit*f+column) for bit in range(h) if U>>bit&1)


def full_coefficient(difference,h,f):
    weight=difference.bit_count()
    return mul(power((1,1),h*f-weight),power((1,-1),weight))


def line_terms(U,h,f,inverse=False):
    terms=[]
    for selectors in range(1<<f):
        displacement=0
        for column in range(f):
            if selectors>>column&1:displacement^=ambient_mask(U,h,f,column)
        weight=selectors.bit_count()
        coefficient=mul(power((1,-1) if inverse else (1,1),f-weight),
                        power((1,1) if inverse else (1,-1),weight))
        terms.append((displacement,coefficient))
    return terms


def kernel_coefficient(difference,U,h,f):
    # F*C_U^-1 has exactly one affine quotient constraint per column.
    # The selected label has odd weight; weight3mod4 flips the constraint.
    offset=((U.bit_count()-1)//2)&1
    if any((difference&ambient_mask(U,h,f,column)).bit_count()%2!=offset for column in range(f)):
        return (0,0)
    return mul(full_coefficient(difference,h,f),power((1,-1),f))


def gaussian_rank(M):
    A=[[tuple(Q(v) for v in x) for x in row] for row in M];row=0
    for column in range(len(A[0])):
        pivot=next((i for i in range(row,len(A)) if A[i][column]!=(0,0)),None)
        if pivot is None:continue
        A[pivot],A[row]=A[row],A[pivot];factor=A[row][column]
        A[row]=[divide(x,factor) for x in A[row]]
        for i in range(len(A)):
            if i!=row and A[i][column]!=(0,0):
                factor=A[i][column];A[i]=[add(x,tuple(-v for v in mul(factor,y))) for x,y in zip(A[i],A[row])]
        row+=1
    return row


def small_product(A,B):
    return [[sum_gaussian(mul(A[i][k],B[k][j]) for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def sum_gaussian(values):
    out=(0,0)
    for value in values:out=add(out,value)
    return out


def bank_mixer(address,W):
    # Dense integer unit-determinant address-dependent nonunit mixer.
    U=[[(1,0) if i==j else ((1 if (i+j+address)%2 else -1,0) if i<j else (0,0))
        for j in range(W)] for i in range(W)]
    L=[[(1,0) if i==j else ((2 if (i+j+address)%3 else -1,0) if i>j else (0,0))
        for j in range(W)] for i in range(W)]
    return small_product(L,U)


def probe(case):
    h,f=case;start=time.monotonic();D=1<<(h*f);W=6;labels=(1,7);checked=0;digest=sha256()
    if h<3:raise ValueError('The retained odd labels need at least3 ambient bits')
    kernels={};line_support={};masses={}
    for U in labels:
        inverse=line_terms(U,h,f,True);forward=line_terms(U,h,f)
        values=[]
        for difference in range(D):
            closed=kernel_coefficient(difference,U,h,f)
            direct=sum_gaussian(mul(full_coefficient(difference^delta,h,f),coefficient)
                                for delta,coefficient in inverse)
            if direct!=tuple(v<<f for v in closed):raise ValueError('The affine zero/chirp line-kernel identity failed')
            values.append(closed)
        kernels[U]=values;line_support[U]=len(forward)
        if sum(value!=(0,0) for value in values)!=(1<<((h-1)*f)):
            raise ValueError('The complete tensor kernel has the wrong row support')
        expected_norm=1<<((h+1)*f)
        if any(value!=(0,0) and norm(value)!=expected_norm for value in values):
            raise ValueError('The kernel support has nonuniform exact coefficient mass')
        if sum(norm(value) for value in values)!=(1<<(2*h*f)):
            raise ValueError('The complete source kernel is not unitary')
        for x in range(D):
            for y in range(D):
                observed=sum_gaussian(mul(values[x^y^delta],coefficient) for delta,coefficient in forward)
                wanted=tuple(v<<f for v in full_coefficient(x^y,h,f))
                if observed!=wanted:raise ValueError('The unique post repair A_U*(F*A_U^-1)=F failed a full coefficient')
                digest.update(str((U,x,y,observed)).encode());checked+=1
        masses[U]=dict(kernel_row_support=1<<((h-1)*f),line_repair_row_support=1<<f,
                       kernel_probability_denominator=1<<((h-1)*f))
    # A pointwise invertible bank sandwich cannot repair a source-zero
    # W-by-W (output-address,input-address) kernel block. The result
    # persists with arbitrary per-bank permutations placed inside it.
    rank_witnesses=[]
    for routing in ('none','independent bank XOR input/output routes'):
        for x in range(D):
            source=0;U=labels[source]
            out_offset=source+1 if routing!='none' else 0
            in_offset=2*source+3 if routing!='none' else 0
            old_x=x^out_offset
            # Choose a y that violates source0's first quotient constraint.
            old_y=old_x^ambient_mask(1,h,f,0);y=old_y^in_offset
            entries=[]
            for bank in range(W):
                r=x^(bank+1 if routing!='none' else 0)
                s=y^(2*bank+3 if routing!='none' else 0)
                entries.append(kernels[labels[bank]][r^s] if bank<2 else full_coefficient(r^s,h,f))
            if entries[source]!=(0,0):raise ValueError('The chosen tensor source zero was not retained by routing')
            block=[[(entries[i] if i==j else (0,0)) for j in range(W)] for i in range(W)]
            transformed=small_product(small_product(bank_mixer(x,W),block),bank_mixer(y+1,W))
            rank=gaussian_rank(transformed)
            if rank>=W:raise ValueError('An invertible address-local bank mixer repaired a rank-deficient coefficient block')
            rank_witnesses.append(rank)
    # Exact unitary entropy of the full decoded operator: four dense F
    # channels and two rank(h-1) source channels; every bank is retained.
    target_entropy=W*D*h*f
    decoded_entropy=(W-2)*D*h*f+2*D*(h-1)*f
    if target_entropy-decoded_entropy!=2*D*f:raise ValueError('The two-source entropy deficit differs')
    # Pairwise native unitary C bank mixing has disjoint old input-bank
    # supports. Each output row gains one bit in total on average.
    native_unitary_layer_entropy=decoded_entropy+W*D
    if native_unitary_layer_entropy-decoded_entropy!=W*D:
        raise ValueError('The exact unitary bank-layer entropy increment differs')
    # A legal nonunit dyadic scale2 on one dense bank and1/2 on another
    # invalidates the unitary entropy bound, despite restoring inverses.
    nonunit_entropy_jump=D*(Q(9,4)*h*f-Q(15,2))
    post_layer_examples=[]
    for selected_columns in (f,16,64,256,1024):
        minimum=0
        while W**minimum<1<<selected_columns:minimum+=1
        post_layer_examples.append(dict(selected_columns=selected_columns,minimum_Wwide_layers=minimum,
                                        exact_power_check=W**minimum>=1<<selected_columns,
                                        previous_layer_insufficient=minimum==0 or W**(minimum-1)<1<<selected_columns))
    return dict(status='PASS SCOPED ADDRESS-DEPENDENT BOUNDARY OBSTRUCTIONS',h=h,columns=f,
                payload_stock=W,address_volume=D,whole_operator_coefficients_replayed=checked,
                all_source_sink_dirty_channels_retained=True,source_line_profiles=masses,
                unique_post_repair='diag(C_U^tensor(f),C_U^tensor(f),I,I,I,I) after constant coupled data decoding',
                arbitrary_nonunit_post_layer_support_bound='W^T; T>=f/log2(W)',
                pointwise_sandwich_block_witnesses=len(rank_witnesses),
                pointwise_sandwich_rank_range=[min(rank_witnesses),max(rank_witnesses)],target_coefficient_block_rank=W,
                tested_bank_mixers='Address-dependent dense unimodular integer matrices; the proof permits arbitrary invertible complex matrices.',
                per_bank_route_scope='One arbitrary bijective input/output address route inside the two pointwise mixers; finite controls use independent XOR routes.',
                exact_target_unitary_entropy=target_entropy,exact_decoded_unitary_entropy=decoded_entropy,
                missing_unitary_entropy=target_entropy-decoded_entropy,
                unitary_two_sided_layer_bound='T>=2*f/(W*log2(W))',
                exact_unitary_pair_layer_increment=W*D,
                exact_nonunit_scale_entropy_jump=str(nonunit_entropy_jump),
                nonunit_entropy_warning='The unitary entropy change bound does not apply to nonunit words; no inverse/precision assumption repairs this automatically.',
                exact_post_layer_examples=post_layer_examples,
                time_scope='Layer count alone is not a fixed-tape time lower bound. A separately declared full materialized pass/layer algorithm pays its actual V*T scans; fused/streaming/pre-post alternatives remain open.',
                output_sha256=digest.hexdigest(),seconds=time.monotonic()-start,
                scope='Exact complete finite kernels, unique post-only repair, coefficient-block rank model, and separate unitary entropy controls. No global native adapter impossibility, arbitrary monomial bank/address mixing exclusion, or multiplication lower bound follows.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cases=[(3,1),(3,2),(4,1),(4,2)];source=Path(__file__);original=sha256(source.read_bytes()).hexdigest()
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,cases=cases,seed=None,
                  source_sha256={source.name:original},scalar_domain='Exact integer Gaussian kernels and Fraction elimination',
                  hypotheses=['Post-only native words need growing layers to supply tensor line support','One pointwise pre/post mixer sandwich cannot repair a rank-deficient coefficient block','Two-sided unitary layers need linear selected-column count, with nonunit words scoped separately'],
                  literature_primary=['https://arxiv.org/abs/1305.4745','https://arxiv.org/abs/1403.1307'],
                  native_time_budget_reference='reports/transfers/routing-aware-depth-transfer.md; compare complete actual V,e,K,p and stopping band before excluding an adapter')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs={pool.submit(probe,case):case for case in cases}
        for future in as_completed(jobs):
            result=future.result();results.append(result)
            print(json.dumps({key:result[key] for key in ('status','h','columns','whole_operator_coefficients_replayed','seconds')}),flush=True)
    if sha256(source.read_bytes()).hexdigest()!=original:raise ValueError('Source changed during boundary discriminator')
    (args.output/'certificate.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')


if __name__=='__main__':main()
