#!/usr/bin/env python3
"""Certify previously singleton-split rank-two transitions in a new word."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time
from integer_crt_certificate import certificate


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['binary','transitions','prior_profile','output']:
        ap.add_argument('--'+name.replace('_','-'),required=True,type=Path)
    args=ap.parse_args();assert __debug__;args.output.mkdir(parents=True,exist_ok=False)
    prior=json.loads(args.prior_profile.read_text());h=prior['h'];cert=certificate()
    command=[str(args.binary.resolve()),str(args.transitions.resolve()),str((args.output/'profiles.json').resolve()),
        str(cert['dimensions'][str(h)]['maximum_residual_integer_numerator'])]+[str(p['p']) for p in cert['primes']]
    started=time.monotonic()
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),command=command,
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        cpp_source_sha256=sha256(Path(__file__).with_name('integer_crt_rank2_profiles.cpp').read_bytes()).hexdigest(),
        binary_sha256=sha256(args.binary.read_bytes()).hexdigest(),
        input_sha256=sha256(args.transitions.read_bytes()).hexdigest(),
        prior_profile_sha256=sha256(args.prior_profile.read_bytes()).hexdigest(),certificate=cert,native_threads=1)
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    with (args.output/'profile.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    new=json.loads((args.output/'profiles.json').read_text())
    differences=[a-b for a,b in zip(new['blocks'],prior['blocks'])]
    assert sum(t*n for t,n in enumerate(differences))==0
    assert all(n==0 for n in differences[3:]) and differences[1]==-2*differences[2] and differences[2]>=0
    result=dict(status='EXACT RANK2 REFINEMENT PASS',h=h,R=new['R'],
        additional_consecutive_rank2_blocks=differences[2],block_differences=differences,
        seconds=time.monotonic()-started,scope='Exact finite consecutive corner-pivot refinement. Native consecutive-axis residual legality and the complete full-word framing law remain inherited; a new moment must use the entire refined controller.')
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
