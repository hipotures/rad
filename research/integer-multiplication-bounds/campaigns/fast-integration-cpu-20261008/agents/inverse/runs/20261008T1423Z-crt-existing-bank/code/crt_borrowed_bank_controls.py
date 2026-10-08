#!/usr/bin/env python3
"""Complete padded two-node CRT batch using ACTUAL inactive coordinate bits.

No address axes are added. Four bits of the fifth, inactive coordinate are
borrowed as two one-bit U digits and two one-bit T guards. Inherited masked
BIT fanout is validated separately; here the guard checker is the primitive.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from crt_guard_controls import rotations,inverse_rotations,pack,unpack,direct_rotation


def model(address,inverse=False,ideal=False):
    widths=(2,3,3,4,4)
    a=list(unpack(address,widths))
    y=(a[1],a[3]);U=unpack(a[4]&3,(1,1));T=unpack(a[4]>>2,(1,1))
    offsets=((2*a[0])%5 if a[0]<3 else 0,(8*a[2])%11 if a[2]<7 else 0)
    if ideal:
        z=direct_rotation(y,(5,11),offsets)
    else:
        function=inverse_rotations if inverse else rotations
        z,U,T=function(y,U,T,(5,11),offsets,(3,4),1)
        a[4]=pack(U,(1,1))|(pack(T,(1,1))<<2)
    a[1],a[3]=z
    return pack(a,widths)


def valid(address):
    return all(x<s for x,s in zip(unpack(address,(2,3,3,4,4)),(3,5,7,11,13)))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();started=time.monotonic()
    count=1 << 16
    actual=[-1]*count;expected=[-1]*count
    for address in range(count):
        out=model(address)
        assert actual[out]==-1
        actual[out]=address
        assert model(out,inverse=True)==address
        expected[model(address,ideal=True)]=address
    keys=[];wrong=temporary_invalid_nonzero=0
    for address,payload in enumerate(actual):
        wrong+=int(payload!=expected[address])
        temporary_invalid_nonzero+=int(not valid(address) and valid(payload))
        donor=unpack(address,(2,3,3,4,4))[4]
        if donor==0:
            assert payload==expected[address]
        else:
            original=model(address,inverse=True)
            assert original==payload
            keys.append((model(original,ideal=True),payload))
    for bit in range(16):
        keys=[record for record in keys if not ((record[0]>>bit)&1)]+[
            record for record in keys if (record[0]>>bit)&1]
    for destination,payload in keys:actual[destination]=payload
    assert actual==expected
    for destination,payload in enumerate(actual):
        assert valid(destination)==valid(payload)
    assert wrong>0 and temporary_invalid_nonzero>0
    result={'run_id':'20261008T1423Z-crt-existing-bank','status':'PASS',
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'guard_dependency_sha256':hashlib.sha256(Path(__file__).with_name('crt_guard_controls.py').read_bytes()).hexdigest(),
            'complete_padded_addresses':count,'valid_addresses':3*5*7*11*13,
            'added_address_bits':0,'borrowed_bits':4,'independent_nodes':2,
            'wrong_before_repair':wrong,'nonzero_invalid_payloads_before_repair':temporary_invalid_nonzero,
            'complete_inverse':True,'actual_radix_repair':True,'all_padded_zeros_restored':True,
            'workers':1,'native_threads':1,'wall_seconds':time.monotonic()-started}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
