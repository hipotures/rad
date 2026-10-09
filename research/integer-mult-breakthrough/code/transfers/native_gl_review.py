#!/usr/bin/env python3
"""Independent finite controls for the conditional complete packed GL bill.

Literal variable-control rotations, repaired complete dirty payloads, binary
row elimination, and column-dependent Gaussian units are authored here. Array
routing is a finite reference oracle and never a fixed-tape cost measurement.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import itertools
import json
from pathlib import Path
import random
import time

TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/native-gl-review.json'
ROTATIONS = ((0,-1,0),(1,-1,0),(0,1,0),(1,1,0),
             (1,1,1),(0,1,1),(1,-1,1),(0,-1,1))


def toggle_mask(x, positions): return sum(1 << p for p in positions if x >> p & 1)


def rotations(x,y,z,k,f,rho,inverse=False):
    positions = [rho+j*k for j in range(f-1)]; modulus=1 << (k*f)
    steps = reversed(ROTATIONS) if inverse else ROTATIONS
    for target,direction,parity in steps:
        sign = -direction if inverse else direction
        other = z if target==0 else y
        offset = sum(1 << p for p in positions if x >> p & 1 and (other >> p & 1)==parity)
        if target==0: y=(y+sign*offset)%modulus
        else: z=(z+sign*offset)%modulus
    return x,y,z


def bad(y,z,k,f,rho):
    mask=(1 << (k-1))-1
    return any(not 10 <= (v >> (rho+j*k+1) & mask) <= (1 << (k-1))-11
               for v in (y,z) for j in range(f-1))


def repair(x,y,z,k,f,rho):
    if not bad(y,z,k,f,rho): return x,y,z
    a,b,c=rotations(x,y,z,k,f,rho,True)
    return a,b ^ toggle_mask(a,[rho+j*k for j in range(f-1)]),c


def primitive(x,y,z,k,f,rho):
    a,b,c=repair(*rotations(x,y,z,k,f,rho),k,f,rho)
    top=rho+(f-1)*k
    return a,b ^ ((a >> top & 1) << top),c


def rank(columns):
    pivots={}
    for value in columns:
        while value:
            bit=value.bit_length()-1
            if bit in pivots:value ^= pivots[bit]
            else:pivots[bit]=value;break
    return len(pivots)


def binary_word(columns):
    n=len(columns);rows=[sum((columns[j]>>i&1)<<j for j in range(n)) for i in range(n)]
    reduction=[]
    for column in range(n):
        if not rows[column]>>column&1:
            partner=next(i for i in range(column+1,n) if rows[i]>>column&1)
            for a,b in ((column,partner),(partner,column),(column,partner)):
                rows[a]^=rows[b];reduction.append((a,b))
        for row in range(n):
            if row!=column and rows[row]>>column&1:
                rows[row]^=rows[column];reduction.append((row,column))
    if rows != [1<<j for j in range(n)]:raise ValueError('Independent elimination failed')
    return list(reversed(reduction))


def binary_map(x,columns):
    out=0
    for j,c in enumerate(columns):
        if x>>j&1:out ^= c
    return out


def apply_binary(x,word):
    for target,source in word: x ^= ((x >> source & 1) << target)
    return x


def selected_case(xmask):
    k,f,rho=6,3,0;period=128;modulus=1 << 18;wrong=0;witness=None
    for y in range(period):
        for z in range(period):
            actual=rotations(xmask,y,z,k,f,rho)
            if rotations(*actual,k,f,rho,True)!=(xmask,y,z):raise ValueError('Literal inverse failed')
            ideal=(xmask,y^xmask,z)
            if actual!=ideal:wrong+=1;witness=witness or [xmask,y,z,list(actual),list(ideal)]
    seed=202610090330+xmask;rng=random.Random(seed);safe=0
    for trial in range(512):
        x,y,z=[rng.randrange(modulus) for _ in range(3)]
        if trial%2==0:
            for p in (0,6):
                mask=31 << (p+1)
                y=(y & ~mask)|(rng.randrange(10,22) << (p+1))
                z=(z & ~mask)|(rng.randrange(10,22) << (p+1))
        actual=rotations(x,y,z,k,f,rho);goal=(x,y^toggle_mask(x,[0,6]),z)
        if not bad(y,z,k,f,rho):
            safe+=1
            if actual!=goal:raise ValueError('Forced carry-free guard failed')
        if bad(actual[1],actual[2],k,f,rho)!=bad(y,z,k,f,rho):raise ValueError('Complete exception set not preserved')
        if primitive(x,y,z,k,f,rho)!=(x,y^toggle_mask(x,[0,6,12]),z):raise ValueError('Complete repair or top bit failed')
        dy,dz=[period*rng.randrange(modulus//period) for _ in range(2)]
        lifted=rotations(x,(y+dy)%modulus,(z+dz)%modulus,k,f,rho)
        if lifted!=(actual[0],(actual[1]+dy)%modulus,(actual[2]+dz)%modulus):raise ValueError('Exact quotient lift failed')
    if not safe:raise ValueError('No safe guards tested')
    return dict(kind='native-six-bit-variable-control',control_mask=xmask,exact_quotient_representatives=period*period,
        unrepaired_wrong=wrong,omitted_repair_witness=witness,complete_address_samples=512,seed=seed,
        forced_or_sampled_safe=safe,whole_arbitrary_companion_restored=True)


def payload(index):return (3*index-5,7*index+11,-13*index-17,19*index+23)


def route(values,permutation):
    out=[None]*len(values)
    for before,value in enumerate(values):
        after=permutation(before)
        if out[after] is not None:raise ValueError('Finite complete payload permutation not injective')
        out[after]=value
    if any(x is None for x in out):raise ValueError('A complete field/record was dropped')
    return out


def chunks(index):
    tail=index%2;index//=2
    xyz=[(index >> (2*(2-j)))&3 for j in range(3)]
    return index>>6,xyz,tail


def address(head,xyz,tail):return (((head*4+xyz[0])*4+xyz[1])*4+xyz[2])*2+tail


def transvection(values,target,source):
    companion=next(j for j in range(3) if j not in (target,source));original=list(values)
    for changed,sign,parity in ROTATIONS:
        def perm(index):
            head,xyz,tail=chunks(index);slot=target if changed==0 else companion;other=companion if changed==0 else target
            if xyz[source]&1 and (xyz[other]&1)==parity:xyz[slot]=(xyz[slot]+sign)%4
            return address(head,xyz,tail)
        values=route(values,perm)
    holes=[];exceptions=[]
    for index,value in enumerate(values):
        head,xyz,tail=chunks(index)
        if bad(xyz[target],xyz[companion],1,2,0):
            holes.append(index)
            a,b,c=repair(xyz[source],xyz[target],xyz[companion],1,2,0)
            xyz[source],xyz[target],xyz[companion]=a,b,c
            exceptions.append((address(head,xyz,tail),value))
    exceptions.sort()
    if [i for i,_ in exceptions]!=holes:raise ValueError('Exceptional complete-record keys do not match holes')
    for index,value in exceptions:values[index]=value
    def top(index):
        head,xyz,tail=chunks(index);xyz[target]^=xyz[source]&2
        return address(head,xyz,tail)
    values=route(values,top)
    def wanted(index):
        head,xyz,tail=chunks(index);xyz[target]^=xyz[source]
        return address(head,xyz,tail)
    if values!=route(original,wanted):raise ValueError('Literal full-payload XOR or companion restoration failed')
    return values,len(exceptions)


def unit(value,q):
    a,b,c,d=value
    return ((a,b,c,d),(-b,a,-d,c),(-a,-b,-c,-d),(b,-a,d,-c))[q%4]


def payload_case(_):
    max_count=0;matrices=0
    for columns in itertools.product(range(8),repeat=3):
        if rank(columns)!=3:continue
        word=binary_word(columns);matrices+=1;max_count=max(max_count,len(word))
        if len(word)>12:raise ValueError('Uniform fixed-order GL bound failed')
        for x in range(8):
            if apply_binary(x,word)!=binary_map(x,columns) or apply_binary(binary_map(x,columns),list(reversed(word)))!=x:
                raise ValueError('Full GL basis or inverse orientation failed')
    columns=[3,6,4];word=binary_word(columns);original=[payload(i) for i in range(256)];values=original;exceptions=[]
    for target,source in word:
        values,count=transvection(values,target,source);exceptions.append(count)
    def wanted(index):
        head,xyz,tail=chunks(index)
        result=[0]*3
        for column in range(2):
            a=sum((x>>column&1)<<j for j,x in enumerate(xyz));b=binary_map(a,columns)
            for j in range(3):result[j]|=(b>>j&1)<<column
        return address(head,result,tail)
    if values!=route(original,wanted):raise ValueError('Complete GL payload map failed')
    for target,source in reversed(word):values,_=transvection(values,target,source)
    if values!=original:raise ValueError('Complete GL inverse failed')
    wrong_constant=False
    for index,value in enumerate(original):
        _,xyz,_=chunks(index);q=0
        for column in range(2):
            bits=[x>>column&1 for x in xyz]
            q+=3+bits[0]+2*bits[1]+3*bits[2]+2*bits[0]*bits[1]+2*bits[1]*bits[2]
        transformed=unit(value,q)
        if unit(transformed,-q)!=value or sum(x*x for x in transformed)!=sum(x*x for x in value):raise ValueError('Complete Gaussian unit chirp failed')
        wrong_constant|=unit(value,q-3)!=transformed
    if not wrong_constant:raise ValueError('Per-column constant negative failed')
    return dict(kind='complete-Gaussian-payload-reference',all_GL3_matrices=matrices,complete_basis_addresses=8*matrices,
        max_transvections=max_count,uniform_transvection_bound=12,retained_route_columns=columns,
        complete_payload_records=256,arbitrary_full_fields=4,forward_exception_counts=exceptions,
        full_prefix_and_suffix_restored=True,full_inverse_restored=True,chirp_column_constant=3,
        selected_columns=2,actual_global_constant=6,wrong_single_constant_rejected=True,
        native_K_guard_contract=False,scope='K1 toy complete payload control; native K6 address word is a separate case')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4);parser.add_argument('--output',type=Path)
    args=parser.parse_args();config=json.loads(CONFIG.read_text());paths=[Path(__file__).resolve(),CONFIG]
    pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_sha256=pins,
        scope=config['scope'],producer_imports=False,dependencies='Python standard library',primary_source=config['primary_source'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        jobs=[pool.submit(selected_case,x) for x in (0,1,64,65)]+[pool.submit(payload_case,None)]
        cases=[job.result() for job in jobs]
    wrong=sum(c.get('unrepaired_wrong',0) for c in cases)
    if Q(wrong,65536)!=Q(1,128):raise ValueError('Complete native quotient failure fraction differs')
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=value for p,value in pins.items()):raise ValueError('Source changed during immutable attempt')
    result=dict(status='INDEPENDENT CONDITIONAL GL CONTROLS PASS',cases=cases,
        exact_native_quotient_representatives=65536,complete_address_samples=2048,full_payload_records=256,
        unrepaired_native_failure_fraction=str(Q(wrong,65536)),seconds=time.monotonic()-started,
        scope=config['scope'],fixed_tape_cost_measured=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':main()
