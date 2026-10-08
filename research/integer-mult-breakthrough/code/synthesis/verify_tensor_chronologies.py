#!/usr/bin/env python3
"""Bounded literal tensor-word controls; no native cost or exponent claim."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

import compressed_tensor_chronology as c
import pauli_tensor_discriminator as p


def verify():
    direct=[p.tensor_probe(1,f) for f in (1,2)]
    compressed=[c.probe(1,f) for f in (1,2)]
    # Regression of the failed initial inverse: exchanging low/high dyadic
    # coefficients preserves formal invertibility but corrupts all source rows.
    old=c.word
    def corrupt(h,f):
        answer=old(h,f)
        for j,event in enumerate(answer):
            if event[0]=='conditional_scale' and event[3]==c.ALPHA_INVERSE:
                answer[j]=(event[0],event[1],event[2],event[4],event[3]);return answer
        raise ValueError('Regression control did not find an inverse scale')
    c.word=corrupt
    try:
        try:c.replay(1,1)
        except ValueError as e:
            if 'Full in-place address/dirty operator replay failed' not in str(e):raise
        else:raise ValueError('Inverse low/high regression was not detected')
    finally:c.word=old
    return dict(status='PASS EXACT BOUNDED TENSOR WORDS',recorded_utc=datetime.now(timezone.utc).isoformat(),
                direct_cases=direct,compressed_cases=compressed,inverse_low_high_regression_detected=True,
                scope='Exact finite Gaussian-rational source/sink/dirty operator words, complete Pauli projections, exponential direct-sum support and small-factor Gram controls. Compressed stage counts scale with h*f. No old common-frame histogram, fixed-tape cost, precision guarantee or kappa is certified.')


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path);args=a.parse_args()
    result=verify();files=[Path(__file__),Path(c.__file__),Path(p.__file__)]
    result['source_sha256']={f.name:sha256(f.read_bytes()).hexdigest() for f in files}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],direct_cases=len(result['direct_cases']),compressed_cases=len(result['compressed_cases']),scope=result['scope'])))


if __name__=='__main__':main()
