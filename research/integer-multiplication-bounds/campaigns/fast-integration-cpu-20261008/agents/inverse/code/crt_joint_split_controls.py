#!/usr/bin/env python3
"""Independent payload-level checker for balanced CRT with joint splitting.

All current padded node intervals are explicitly traversed; invalid zeros
are deleted and reinserted by the actual monotone scan. The separate guard
checker certifies the node rotations; here ideal node rotations isolate
the CRT recursion/padding interface and retain malformed-padding negatives.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time


def decode(address, capacities):
    values=[]
    for capacity in capacities:
        values.append(address%capacity)
        address//=capacity
    return values


def encode(values, capacities):
    result=stride=0
    stride=1
    for value,capacity in zip(values,capacities):
        result+=value*stride
        stride*=capacity
    return result


def shape(primes):
    return math.prod(primes), math.prod(1 << (s-1).bit_length() for s in primes)


def run(primes):
    started=time.monotonic()
    S,T=shape(primes)
    payload=[k+1 if k<S else 0 for k in range(T)]
    groups=[tuple(primes)]
    levels=[]
    malformed_reinterpretation=0
    while any(len(group)>1 for group in groups):
        old_shapes=[shape(group) for group in groups]
        new_groups=[];pairs=[]
        for group in groups:
            if len(group)==1:
                new_groups.append(group)
            else:
                at=len(group)//2
                left,right=group[:at],group[at:]
                i=len(new_groups);new_groups.extend((left,right))
                sl,_=shape(left);sr,_=shape(right)
                pairs.append((i,i+1,sl,sr,pow(sl,-1,sr)))
        new_shapes=[shape(group) for group in new_groups]
        old_caps=[t for s,t in old_shapes]
        new_caps=[t for s,t in new_shapes]
        assert math.prod(old_caps)==T==math.prod(new_caps)
        def next_occupied():
            for address,value in enumerate(payload):
                digits=decode(address,old_caps)
                valid=all(digit<s for digit,(s,t) in zip(digits,old_shapes))
                if valid:
                    yield value
                else:
                    assert value==0
        source=next_occupied()
        embedded=[0]*T;copied=0
        for address in range(T):
            digits=decode(address,new_caps)
            if all(digit<s for digit,(s,t) in zip(digits,new_shapes)):
                embedded[address]=next(source);copied+=1
            elif payload[address]:
                malformed_reinterpretation+=1
        assert next(source,None) is None and copied==S
        rotated=[0]*T
        for address,value in enumerate(embedded):
            digits=decode(address,new_caps)
            for i,j,sl,sr,inverse in pairs:
                if digits[i]<sl and digits[j]<sr:
                    digits[j]=(digits[j]+inverse*digits[i])%sr
            destination=encode(digits,new_caps)
            assert not (value and rotated[destination])
            rotated[destination]=value
        invalid=0
        for address,value in enumerate(rotated):
            digits=decode(address,new_caps)
            if any(digit>=s for digit,(s,t) in zip(digits,new_shapes)):
                assert value==0;invalid+=1
        levels.append({"nodes_before":len(groups),"nodes_after":len(new_groups),
                       "joint_source_records":copied,"allocated_records":T,
                       "invalid_zero_records":invalid,"independent_rotations":len(pairs)})
        payload=rotated;groups=new_groups
    capacities=[shape(group)[1] for group in groups]
    expected=[0]*T
    prefix=1;multipliers=[]
    for s in primes:
        multipliers.append(pow(prefix,-1,s));prefix*=s
    for k in range(S):
        digits=[mu*k%s for mu,s in zip(multipliers,primes)]
        expected[encode(digits,capacities)]=k+1
    assert payload==expected
    # A bit reinterpretation before leaf CRT cannot silently replace the
    # mandatory mixed-radix embedding; all invalid holes contain zero only
    # after the real monotone splitting scan.
    assert malformed_reinterpretation>0
    return {"primes":primes,"source_records":S,"allocated_records":T,
            "levels":levels,"leaf_oracle_exact":True,"invalid_zeros_preserved":True,
            "malformed_reinterpretation_negative_records":malformed_reinterpretation,
            "wall_seconds":time.monotonic()-started}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",required=True)
    parser.add_argument("--six-prime",action="store_true")
    args=parser.parse_args();started=time.monotonic()
    cases=[(3,5,7),(3,5,7,11),(3,5,7,11,13)]
    if args.six_prime:cases.append((3,5,7,11,13,17))
    results=[]
    for primes in cases:
        result=run(primes);results.append(result)
        print(json.dumps({"completed":result}),flush=True)
    output={"run_id":"20261008T1416Z-crt-joint-splits","status":"PASS",
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope":"Complete padded payload scans and recursive CRT leaf map; node rotation guard identity separately checked",
            "cases":results,"workers":1,"native_threads":1,
            "wall_seconds":time.monotonic()-started}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({"status":"PASS","wall_seconds":output["wall_seconds"]}),flush=True)


if __name__=="__main__":main()
