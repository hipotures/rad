#!/usr/bin/env python3
"""Exact dyadic forward/inverse child interfaces and linear guard controls.

This tests the completed semantic precision argument, not a full large
finite phase network or a fixed-tape multiplication implementation.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import time


def require(condition,message):
    if not condition:raise AssertionError(message)


def add(a,b):return (a[0]+b[0],a[1]+b[1])
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def mul_i(a):return (-a[1],a[0])
def scale(a,q):return (a[0]*q,a[1]*q)


def c_pair(a,b,inverse=False):
    if inverse:
        # -i Z C Z, with the fourth-root phase once on the full pair.
        forward=c_pair(a,scale(b,-1))
        return tuple(scale(mul_i(scale(v,(-1 if j else 1))),-1)
                     for j,v in enumerate(forward))
    common=add(a,b);different=mul_i(sub(a,b))
    return (scale(add(common,different),Q(1,2)),scale(sub(common,different),Q(1,2)))


def child(values,selected,inverse=False,inflate=0):
    values=list(values);temporary_grid=0
    # An intentionally exact temporary fine-grid excursion demonstrates
    # why internal excess cannot be added to all completed outputs.
    if inflate:
        temp=[scale(v,Q(1,2**inflate)) for v in values]
        temporary_grid=inflate
        values=[scale(v,2**inflate) for v in temp]
    for bit in selected:
        mask=1<<bit
        for j in range(len(values)):
            if j&mask:continue
            a,b=c_pair(values[j],values[j|mask],inverse)
            values[j],values[j|mask]=a,b
    return values,temporary_grid


def grid_exponent(values):
    maximum=0
    for value in values:
        for x in value:
            den=x.denominator
            require(den&(den-1)==0,'Non-dyadic exact child output')
            maximum=max(maximum,den.bit_length()-1)
    return maximum


def interface_controls():
    entries=forward=inverse=probes=0
    excursions=[]
    for f in range(1,7):
        n=1<<f
        rows=[Q(0)]*n
        for j in range(n):
            rhs=[(Q(int(i==j)),Q(0)) for i in range(n)]
            output,_=child(rhs,range(f))
            recovered,_=child(output,range(f),inverse=True)
            require(recovered==rhs,'Exact corrected inverse does not undo child')
            require(grid_exponent(output)<=f,'Forward completed grid exceeds f')
            backward,_=child(rhs,range(f),inverse=True)
            require(grid_exponent(backward)<=f,'Inverse completed grid exceeds f')
            for i,(x,y) in enumerate(output):
                rows[i]+=abs(x)+abs(y);entries+=1
            forward+=1;inverse+=1
        require(max(rows)<=2**f,'Completed Gaussian-integer row bound exceeds 2^f')
        for input_depth,inflate in product((0,3,11),(0,7,29)):
            rhs=[(Q((13*i%17)-8,2**input_depth),Q((7*i%11)-5,2**input_depth)) for i in range(n)]
            output,tmp=child(rhs,range(f),inflate=inflate)
            reference,_=child(rhs,range(f))
            require(output==reference,'Exact temporary excursion changes completed child')
            require(grid_exponent(output)<=input_depth+f,'Completed grid fails semantic reset')
            in_bound=max(abs(a)+abs(b) for a,b in rhs)
            out_bound=max(abs(a)+abs(b) for a,b in output)
            require(out_bound<=2**f*in_bound,'Completed input/output norm bound failed')
            probes+=1
            if inflate and len(excursions)<8:
                excursions.append(dict(f=f,input_grid=input_depth,temporary_excess=tmp,
                      completed_grid=grid_exponent(output),semantic_upper=input_depth+f))
    return dict(exact_tensor_entries=entries,forward_basis_probes=forward,inverse_basis_probes=inverse,
                arbitrary_grid_probes=probes,temporary_excursion_examples=excursions)


def recurrences():
    checks=below=0;examples=[]
    for m,W,beta_num,beta_den in product((3,5,7),(4,11),(1,2),(3,5)):
        if beta_num>=beta_den:continue
        s=W*m-1;E=64*(W+m+1)**3;B=s+E
        C0=32*m*B*B
        require(C0>2*B+18,'Explicit linear whole-layer constant fails')
        for k in range(10):
            d=m**k
            threshold=d**beta_num
            def recurse(e):
                nonlocal below
                if e**beta_den<threshold or e<m:
                    below+=1;return 8*e,8*e,0
                new,old,j=recurse(e//m)
                return new+s*(e//m)+E,s*old+E,j+1
            new,old,j=recurse(d)
            exact=8*(d//m**j)+s*sum(d//m**(v+1) for v in range(j))+E*j
            require(new==exact and new<=2*B*d,'Linear internal recurrence bound fails')
            require(new+18*d<C0*d,'Linear complete guard bound fails')
            require(new<=old,'Semantic guard unexpectedly exceeds concatenated depth')
            checks+=1
            if k==9 and len(examples)<6:
                examples.append(dict(m=m,W=W,s=s,E=E,d=d,beta=f'{beta_num}/{beta_den}',
                    internal_levels=j,new_relative_bound=new,old_concatenated_depth=old,
                    linear_internal_upper=2*B*d,C0=C0,whole_layer_upper=C0*d))
    return dict(exact_stopped_cases=checks,leaf_cases=below,examples=examples)


def sequential_controls():
    # Parent child calls can use different selected address bits and inverse
    # directions. Scalar halves/additions are charged separately.
    size=64;p=7
    values=[(Q((5*i%13)-6,2**p),Q((7*i%17)-8,2**p)) for i in range(size)]
    incoming=max(abs(a)+abs(b) for a,b in values)
    semantic_increment=0;checked=0;temporary=0
    for step in range(24):
        selected=(step%6,(step+1)%6)
        old=list(values)
        values,extra=child(values,selected,inverse=bool(step%2),inflate=step+3)
        require(grid_exponent(values)<=p+semantic_increment+2,'Sequential semantic grid failed')
        semantic_increment+=2
        require(max(abs(a)+abs(b) for a,b in values)<=incoming*2**semantic_increment,
                'Sequential completed norm failed')
        # One saved-input grouped scalar sum followed by a half.
        values=[scale(add(v,old[i^1]),Q(1,2)) for i,v in enumerate(values)]
        semantic_increment+=2
        require(grid_exponent(values)<=p+semantic_increment,'Scalar grid charge failed')
        temporary=max(temporary,extra)
        checked+=size
    return dict(child_calls=24,selected_bits_per_call=2,exact_values_checked=checked,
                final_grid_exponent=grid_exponent(values),semantic_grid_upper=p+semantic_increment,
                largest_temporary_excursion=temporary,fine_grid_never_truncated=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--original-upstream',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();require(not args.output.exists(),'Use a fresh output path')
    started=time.monotonic()
    reference_commit=subprocess.run(['git','-C',str(args.original_upstream),'rev-parse','HEAD'],
        text=True,capture_output=True,check=True).stdout.strip()
    require(reference_commit=='bcd4ebde8692383539f8a48734e5fbf3a18a32c2','Original input revision differs')
    sections=['03-motifs.tex','05-layers.tex']
    hashes={name:hashlib.sha256((args.original_upstream/'upstream/build/sections'/name).read_bytes()).hexdigest()
            for name in sections}
    result=dict(status='PASS exact semantic child and linear stopped-guard controls; full transfer review required',
        campaign='20261007T222521Z',campaign_start='2026-10-07T22:25:21Z',campaign_deadline='2026-10-08T08:25:21Z',
        generated_at=datetime.now(timezone.utc).isoformat(),
        original_reference=dict(url='https://github.com/CrocSwap/integer-mult-bounds',commit='bcd4ebde8692383539f8a48734e5fbf3a18a32c2',section_sha256=hashes),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        interfaces=interface_controls(),recurrences=recurrences(),sequential=sequential_controls(),
        guard=dict(internal='A(e)<=A(e/m)+s*e/m+E',internal_upper='2*(s+E)*e',
                   C0='32*m*(s+E)^2',C1=1,strict_constant='C0>2*(s+E)+18'),
        limitations=['Exact finite surrogate checks, not a large phase-network replay',
                    'All-size proof relies on the retained exact untruncated completed child interface'],
        elapsed_seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS',result['interfaces']['exact_tensor_entries'],'dyadic tensor entries,',
          result['recurrences']['exact_stopped_cases'],'stopped guard cases',flush=True)


if __name__=='__main__':main()
