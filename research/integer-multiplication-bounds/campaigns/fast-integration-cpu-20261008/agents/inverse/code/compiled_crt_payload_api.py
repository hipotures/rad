#!/usr/bin/env python3
"""Arbitrary nonnegative coefficient payload through the actual guarded CRT.

Uses the frozen bank-leaf compiler's actual F_u, computed inverse-key radix
repairs, dirty existing banks, joint scans and complete optional inverse.
This finite model does not measure fixed-tape complexity. Inputs are scalar
coefficients of length S; output is the full padded binary leaf box of size T,
axis zero in least-significant bits, triangular normalization P_i^-1*k.
Zero padding remains numeric zero; legitimate coefficient zeros are allowed.
The public transform_payload API returns output plus complete compact ledger.
"""
import math
import time
from compiled_crt_pipeline_bankleaf import (
    Machine, shape, fields, compiled_rotation, ordinary_rotation, valid,
)

def transform_payload(primes, coefficients, *, reverse_check=True, emit_stdout=False,
                      _return_machine=False):
    started=time.monotonic();N=sum((s-1).bit_length() for s in primes);S=math.prod(primes);T=1<<N
    assert len(coefficients)==S, ('coefficient count',len(coefficients),S)
    assert all(isinstance(value,int) and value>=0 for value in coefficients)
    initial=list(coefficients)+[0]*(T-S)
    progress=[];machine=Machine(initial[:],N,progress);groups=[tuple(primes)];metrics=[];level=0
    if not emit_stdout:machine.emit=lambda value:progress.append(value)
    while any(len(group)>1 for group in groups):
        old=[shape(group) for group in groups];new_groups=[];nodes=[]
        for group in groups:
            if len(group)==1:new_groups.append(group)
            else:
                # Reserve the original last leaf after one ordinary root
                # split, then balance the remaining leaves. Depth stays
                # 1+O(log d); this is not a chain of d scalar splits.
                at=len(group)-1 if level==0 else len(group)//2
                left,right=group[:at],group[at:];i=len(new_groups)
                new_groups.extend((left,right));sl,_=shape(left);sr,_=shape(right)
                nodes.append((i,i+1,sl,sr,pow(sl,-1,sr)))
        new=[shape(group) for group in new_groups];machine.embedding('joint-split',old,new)
        fs=fields([width for s,width in new]);done=set()
        # Try all independent nodes together when there are enough inactive bits;
        # otherwise use inactive-node classes. No bank bit comes from an active
        # node's LEFT or RIGHT words.
        for batch in ([nodes] if len(nodes)>1 else [])+[[node] for node in nodes]:
            batch=[node for node in batch if node[0] not in done]
            if not batch:continue
            active={index for left,right,sl,sr,mu in batch for index in (left,right)}
            donors=[bit for i,field in enumerate(fs) if i not in active for bit in field.positions]
            if compiled_rotation(machine,batch,fs,donors,metrics):done.update(node[0] for node in batch)
        for node in nodes:
            if node[0] not in done:ordinary_rotation(machine,node,fs)
        assert all(value==0 or valid(address,new) for address,value in enumerate(machine.payload))
        level+=1;groups=new_groups
        machine.emit({'forward_CRT_level':level,'allocated_records':T,'valid_records':S,
                      'padding_restored':True,'compiled_batches':len(metrics)})
    caps=[1<<((s-1).bit_length()) for s in primes];expected=[0]*T;prefix=1;mus=[]
    for s in primes:mus.append(pow(prefix,-1,s));prefix*=s
    for k in range(S):
        digits=[mu*k%s for mu,s in zip(mus,primes)];target=0;stride=1
        for value,capacity in zip(digits,caps):target+=value*stride;stride*=capacity
        expected[target]=coefficients[k]
    assert machine.payload==expected,'full CRT leaf oracle mismatch'
    machine.emit({'full_CRT_leaf_oracle':'PASS','events':len(machine.events)})
    output=machine.payload[:]
    if reverse_check:
        machine.inverse();assert machine.payload==initial,'full reverse pipeline mismatch'
    result={'output':output,'primes':primes,'address_bits':N,'allocated_records':T,'valid_records':S,
            'initial_padding_provenance':'caller nonnegative coefficients at scalar k<S; all other payloads explicit zero',
            'added_address_bits':0,'compiled_batches':metrics,'full_leaf_oracle':True,
            'full_reverse_pipeline':reverse_check,'all_padding_boundaries_restored':True,
            'events':len(machine.events),'ledger':machine.ledger,'wall_seconds':time.monotonic()-started}
    if _return_machine:
        assert not reverse_check
        result['_machine']=machine
    return result


def inverse_payload(primes, leaf_coefficients, *, emit_stdout=False):
    """Execute actual reverse events on caller-supplied binary leaf records.

    A separately charged forward template uses positive provenance labels to
    compile and verify the exact current-address event program. The inverse
    replaces only the coefficient payload, then reverses every ordinary map,
    repaired F_u, repaired outer reflection and joint occupied-slot scan.
    Its independent oracle only checks the resulting scalar payload.
    """
    started=time.monotonic()
    S=math.prod(primes)
    N=sum((s-1).bit_length() for s in primes)
    T=1<<N
    assert len(leaf_coefficients)==T, ('leaf box size',len(leaf_coefficients),T)
    assert all(isinstance(value,int) and value>=0 for value in leaf_coefficients)
    shapes=[shape((s,)) for s in primes]
    assert all(value==0 or valid(address,shapes)
               for address,value in enumerate(leaf_coefficients)), 'nonzero leaf padding'
    template=transform_payload(primes,list(range(1,S+1)),reverse_check=False,
                               emit_stdout=emit_stdout,_return_machine=True)
    machine=template.pop('_machine')
    template.pop('output')
    machine.payload=list(leaf_coefficients)
    machine.inverse()
    caps=[1<<((s-1).bit_length()) for s in primes]
    prefix=1
    mus=[]
    for s in primes:
        mus.append(pow(prefix,-1,s))
        prefix*=s
    expected=[0]*T
    for k in range(S):
        address=0
        stride=1
        for mu,s,capacity in zip(mus,primes,caps):
            address+=(mu*k%s)*stride
            stride*=capacity
        expected[k]=leaf_coefficients[address]
    assert machine.payload==expected, 'caller inverse payload oracle mismatch'
    return {'output':machine.payload,'coefficients':machine.payload[:S],
            'primes':primes,'allocated_records':T,'valid_records':S,
            'actual_reverse_events':len(machine.events),'full_inverse_oracle':True,
            'added_address_bits':0,'all_scalar_padding_restored':True,
            'separately_charged_forward_template':template,
            'wall_seconds':time.monotonic()-started}
