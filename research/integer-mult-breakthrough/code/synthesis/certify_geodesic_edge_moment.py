#!/usr/bin/env python3
"""Exact outward moments for declared side-edge rank-ledger profiles only."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import time

COMPLEX = Path(__file__).resolve().parents[1] / 'complex'
sys.path.insert(0, str(COMPLEX))
import characteristic as intervals


def certify(ledger):
    h = ledger['h']
    profile = dict(m=h, W=ledger['payload_stock'],
                   child_multiplicities={int(width): count for width, count in ledger['child_width_histogram'].items()})
    if sum(width * count for width, count in profile['child_multiplicities'].items()) != ledger['rank_charge']:
        raise ValueError('The recorded child multiplicities do not match the ledger')
    saving = Q(1, 5000)
    moment = intervals.moment_interval(profile, saving)
    if moment[1] >= 1:
        raise ValueError('The selected larger ledger fails the exact b=2e-4 moment')
    bracket = intervals.rational_root_bracket(profile)
    return dict(h=h, k=ledger['k'], vertices=ledger['vertices'], center_rank=ledger['center_rank'],
                profile=profile, declared_saving=saving, exact_normalized_moment_interval=moment,
                exact_upper_slack=1-moment[1], strict_rational_root_bracket=bracket,
                source_scope=ledger['scope'],
                scope='Exact finite characteristic arithmetic for the recorded abstract L_E rank ledger. Actual noncoordinate Gaussian chronology, native local fees/precision, full primitive assembly and integer-multiplication transfer are not supplied by this certificate.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=4);args=parser.parse_args()
    if args.workers<1:parser.error('Positive worker count required')
    args.output.mkdir(parents=True,exist_ok=False)
    data=json.loads(args.input.read_text());ledgers=[case['rank_ledger'] for case in data['cases'] if case['kind']=='rank']
    if sorted((x['h'],x['k']) for x in ledgers)!=[(9,3),(12,3),(16,3)]:
        raise ValueError('This recorded discriminator expects the three declared k3 cases')
    sources=(Path(__file__),Path(intervals.__file__))
    hashes={p:sha256(p.read_bytes()).hexdigest() for p in sources}
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,native_threads_each=1,
                  input_path=str(args.input),input_sha256=sha256(args.input.read_bytes()).hexdigest(),
                  source_sha256={p.name:value for p,value in hashes.items()},
                  interval_method='Exact rational atanh log expansion48terms and exp12terms with analytic tails, outward192bit grid; decimal root estimate used only to select a rational bracket proved by the exact endpoints.')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');start=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:receipts=list(pool.map(certify,ledgers))
    if any(sha256(p.read_bytes()).hexdigest()!=value for p,value in hashes.items()):
        raise ValueError('An exact interval source changed during certification')
    result=dict(status='PASS EXACT MOMENTS FOR DECLARED GEODESIC EDGE LEDGERS',cases=receipts,seconds=time.monotonic()-start)
    (args.output/'certificate.json').write_text(json.dumps(intervals.serializable(result),indent=2)+'\n')
    for case in receipts:
        print(json.dumps(dict(h=case['h'],root_lower=str(case['strict_rational_root_bracket']['lower']),
                              root_upper=str(case['strict_rational_root_bracket']['upper']),
                              exact_slack=str(case['exact_upper_slack']))),flush=True)


if __name__=='__main__':main()
