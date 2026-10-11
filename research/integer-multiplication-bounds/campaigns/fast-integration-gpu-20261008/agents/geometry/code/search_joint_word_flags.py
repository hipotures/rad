#!/usr/bin/env python3
"""Exact local profiles of coherent coordinate flags on an executed joint word.

Every retained frame mask is permuted by the same isometry. Scalar instructions,
frame IDs, transition counts, and physical bank allocation are unchanged. The
literal source/output relabeling and all-pair data-family bijection require a
separate compiler/transfer gate before promoting a selected order.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import os
import struct
import subprocess
import sys
import time


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--binary', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    configs=json.loads(args.input.read_text());start=time.monotonic();rows=[];cached={}
    (args.work/'process.json').write_text(json.dumps(dict(pid=os.getpid(),command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
    env=dict(os.environ)
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[key]='1'
    for config in configs:
        source=Path(config['transitions'])
        if source not in cached:cached[source]=source.read_bytes()
        original=cached[source];h,v,R,nf,nt,singles,mass,loss=struct.unpack_from('<6I2Q',original)
        order=config['order'];assert sorted(order)==list(range(h))
        inverse=[0]*h
        for i,j in enumerate(order):inverse[j]=i
        def permute(mask,order):return sum(1<<order[i] for i in range(h) if mask>>i&1)
        raw=bytearray(original)
        for fid in range(nf):
            core,cover,rank=struct.unpack_from('<2QI',original,40+fid*20)
            cc,uu=permute(core,order),permute(cover,order)
            assert permute(cc,inverse)==core and permute(uu,inverse)==cover
            struct.pack_into('<2QI',raw,40+fid*20,cc,uu,rank)
        work=args.work/config['case_id'];work.mkdir();packed=work/'transitions.bin';packed.write_bytes(raw)
        command=[str(args.binary),str(packed),'fixed-all']
        with (work/'run.log').open('wb') as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env)
            (work/'process.json').write_text(json.dumps(dict(pid=child.pid,command=command,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
            print(json.dumps(dict(status='EXACT NEW JOINT WORD COHERENT FLAG RUNNING',pid=child.pid,case=config['case_id'],h=h)),flush=True)
            assert child.wait()==0,config
        profile_path=Path(str(packed)+'.fixed-all.profiles.json');profile=json.loads(profile_path.read_text())
        assert profile['rank_sum']==mass and profile['R']==R
        Phi=sum(t*n*math.expm1(4e-5*math.log(575/t)) for t,n in enumerate(profile['blocks']) if t and n)
        rows.append(dict(config=config,profile=profile,Phi_at_a_4e_5=Phi,input_sha256=digest(source),
                         permuted_binary_sha256=digest(packed),profile_path=str(profile_path),profile_sha256=digest(profile_path)))
        status=dict(utc=datetime.now(timezone.utc).isoformat(),completed=len(rows),total=len(configs),elapsed_seconds=time.monotonic()-start,workers=1)
        (args.work/'status.json').write_text(json.dumps(status,indent=2)+'\n')
        (args.work/'completed-rows.json').write_text(json.dumps(rows)+'\n')
        print(json.dumps(status),flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(dict(status='COMPLETE EXACT JOINT WORD FLAG DISCOVERY',rows=rows,
        input_sha256=digest(args.input),driver_sha256=digest(Path(__file__)),native_sha256=digest(Path(__file__).with_name('joint_word_conjugate_profiles.cpp')),
        binary_sha256=digest(args.binary),elapsed_seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat(),
        scope='All frame masks share one invertible isometry; actual transition IDs/counts and rank mass retained. Exact bounded-minor local matrix profiles. Acceptance requires a coherent source/output literal compiler, unchanged data-family multiset proof, and complete moment/assembly.'),indent=2)+'\n')


if __name__=='__main__':
    main()
