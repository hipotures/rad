#!/usr/bin/env python3
"""Exact controls for a paid packed nonlinear permutation with full guards.

Four complete slots have width (f+1)K; only the first f K-axis chunks are
selected. The extra full range is an explicit input, never zero scratch.
Native fixed-tape time remains conditional on original stream primitives.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import time

import native_gl_review as r
TOPIC=Path(__file__).resolve().parents[2]
CONFIG=TOPIC/'configs/transfers/packed-toffoli.json'


def word(x,z,y,w,k,f,rho,inverse=False):
    c=x & z
    _,a,b=r.rotations(c,y,w,k,f+1,rho,inverse)
    return x,z,a,b


def corrected(x,z,y,w,k,f,rho):
    x,z,y,w=word(x,z,y,w,k,f,rho)
    _,y,w=r.repair(x & z,y,w,k,f+1,rho)
    return x,z,y,w


def ideal(x,z,y,w,k,f,rho):
    return x,z,y ^ r.toggle_mask(x & z,[rho+j*k for j in range(f)]),w


def native_case(pair):
    x,z=pair;k,f,rho=6,2,0;period=128;modulus=1<<18;wrong=0;witness=None
    for y in range(period):
        for w in range(period):
            actual=word(x,z,y,w,k,f,rho)
            if word(*actual,k,f,rho,True)!=(x,z,y,w):raise ValueError('Literal nonlinear inverse failed')
            wanted=ideal(x,z,y,w,k,f,rho)
            if actual!=wanted:wrong+=1;witness=witness or [x,z,y,w,list(actual),list(wanted)]
    seed=202610090400+4*x+z;randoms=random.Random(seed);safe=0
    for trial in range(256):
        x,z,y,w=[randoms.randrange(modulus) for _ in range(4)]
        if trial%2==0:
            for p in (0,6):
                mask=31 << (p+1)
                y=(y & ~mask)|(randoms.randrange(10,22) << (p+1))
                w=(w & ~mask)|(randoms.randrange(10,22) << (p+1))
        actual=word(x,z,y,w,k,f,rho)
        if not r.bad(y,w,k,f+1,rho):
            safe+=1
            if actual!=ideal(x,z,y,w,k,f,rho):raise ValueError('Nonlinear safe guard failed')
        if r.bad(actual[2],actual[3],k,f+1,rho)!=r.bad(y,w,k,f+1,rho):raise ValueError('Nonlinear exceptional set not invariant')
        if corrected(x,z,y,w,k,f,rho)!=ideal(x,z,y,w,k,f,rho):raise ValueError('Complete nonlinear repair or companion failed')
        dy,dw=[period*randoms.randrange(modulus//period) for _ in range(2)]
        shifted=word(x,z,(y+dy)%modulus,(w+dw)%modulus,k,f,rho)
        if shifted!=(actual[0],actual[1],(actual[2]+dy)%modulus,(actual[3]+dw)%modulus):raise ValueError('Nonlinear complete quotient lift failed')
    return dict(kind='native-four-slot-nonlinear-address-word',low_control_masks=list(pair),k=k,f=f,rho=rho,
        whole_slot_bits=(f+1)*k,selected_K_axis_chunks=f,complete_guard_chunks_per_slot=1,
        exact_quotient_representatives=period*period,unrepaired_wrong=wrong,omitted_repair_witness=witness,
        full_address_samples=256,forced_or_sampled_safe=safe,seed=seed,
        both_control_chunks_and_whole_arbitrary_companion_restored=True)


def decode(index):
    tail=index%2;index//=2;values=[0]*4
    for i in range(3,-1,-1):values[i]=index&7;index>>=3
    return index,values,tail


def encode(head,values,tail):
    for v in values:head=head*8+v
    return head*2+tail


def payload_case(_):
    count=2*(1<<12)*2;original=[r.payload(i) for i in range(count)];values=list(original)
    for target,sign,parity in r.ROTATIONS:
        def permutation(index):
            head,chunks,tail=decode(index);slot=2 if target==0 else 3;other=3 if target==0 else 2
            offset=sum(1<<p for p in (0,1) if chunks[0]>>p&1 and chunks[1]>>p&1 and (chunks[other]>>p&1)==parity)
            chunks[slot]=(chunks[slot]+sign*offset)%8
            return encode(head,chunks,tail)
        values=r.route(values,permutation)
    uncorrected=list(values);holes=[];exceptions=[]
    for index,value in enumerate(values):
        head,chunks,tail=decode(index)
        if r.bad(chunks[2],chunks[3],1,3,0):
            holes.append(index)
            x,z,y,w=chunks
            # Correction is T*S^-1 on CURRENT complete records, not T alone.
            a,b,c,d=word(x,z,y,w,1,2,0,True)
            chunks=list(ideal(a,b,c,d,1,2,0))
            exceptions.append((encode(head,chunks,tail),value))
    exceptions.sort()
    if [i for i,_ in exceptions]!=holes:raise ValueError('Nonlinear complete correction keys do not equal holes')
    for index,value in exceptions:values[index]=value
    def wanted(index):
        head,chunks,tail=decode(index);chunks=list(ideal(*chunks,1,2,0))
        return encode(head,chunks,tail)
    expected=r.route(original,wanted)
    if values!=expected:raise ValueError('Complete nonlinear payload or whole guard range failed')
    for before in range(count):
        head,chunks,tail=decode(before);after=wanted(before);other_head,other_chunks,other_tail=decode(after)
        if (head,tail,chunks[0],chunks[1],chunks[3])!=(other_head,other_tail,other_chunks[0],other_chunks[1],other_chunks[3]):
            raise ValueError('Row-prefix, suffix, controls or companion changed')
        if chunks[2]>>2 != other_chunks[2]>>2:raise ValueError('Target complete extra guard chunk changed')
    if uncorrected==expected:raise ValueError('Toy omitted-repair negative did not discriminate')
    return dict(kind='complete-four-field-payload-permutation',k=1,f=2,whole_slot_bits=3,
        complete_slots=4,complete_records=count,full_payload_fields=4,
        complete_prefix=2,complete_suffix=2,exceptional_complete_records=len(exceptions),
        explicit_extra_guard_address_bits=4,old_two_bit_slot_record_count=2*(1<<8)*2,
        new_guarded_slot_record_count=count,not_same_volume_without_existing_guard_chunks=True,
        native_guard_contract=False,all_guard_bits_and_controls_restored=True,
        full_rank_prefix_and_suffix_unchanged=True,omitted_repair_rejected=True,
        scope='K1 complete finite payload oracle; its sixteen-fold shape growth is explicitly paid unless guarded allocation uses existing active axes')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workers',type=int,default=4);parser.add_argument('--output',type=Path)
    args=parser.parse_args();config=json.loads(CONFIG.read_text());helper=Path(r.__file__).resolve()
    if sha256(helper.read_bytes()).hexdigest()!=config['independent_router_sha256']:raise ValueError('Frozen independent helper changed')
    paths=[Path(__file__).resolve(),CONFIG,helper];pins={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,source_config_sha256=pins,
        producer_imports=False,scope=config['scope'],seed_scheme='202610090400+4*xmask+zmask')
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False);(args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(native_case,(a,b)) for a in (0,1,64,65) for b in (0,1,64,65)]+[pool.submit(payload_case,None)]
        cases=[future.result() for future in futures]
    wrong=sum(c.get('unrepaired_wrong',0) for c in cases)
    if Q(wrong,262144)!=Q(1,512):raise ValueError('Complete nonlinear native quotient count differs')
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=value for p,value in pins.items()):raise ValueError('Source changed during immutable attempt')
    result=dict(status='EXACT PAID PACKED TOFFOLI CONTRACT CONTROLS PASS',cases=cases,
        exact_native_quotient_representatives=262144,unrepaired_native_failure_fraction=str(Q(wrong,262144)),
        full_address_samples=4096,full_payload_records=16384,seconds=time.monotonic()-started,
        scope=config['scope'],same_stock_application_proved=False,native_runtime_measured=False,new_exponent=False)
    if args.output:(args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':main()
