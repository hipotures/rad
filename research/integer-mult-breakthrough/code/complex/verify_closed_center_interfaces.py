#!/usr/bin/env python3
"""Bounded, disposable CI entrypoint for the independent center review.

The recorded producer source and immutable fixtures are never rewritten.
Default execution leaves no durable output; --output retains an exclusive
complete receipt when a campaign run needs publication evidence.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


REFERENCE_SHA256 = 'fd5861c9734abb73d898ad90b2fc6e6c365ae572da7b91ac9e83db3e84abfc39'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    source = Path(__file__).with_name('closed_center_interface_review.py')
    if sha256(source.read_bytes()).hexdigest() != REFERENCE_SHA256:
        raise ValueError('Frozen independent review source has changed')
    with TemporaryDirectory(prefix='rad-closed-center-interfaces-') as temporary:
        result_root = Path(temporary) / 'fresh-results'
        command = [sys.executable, '-B', str(source), '--workers', '1',
                   '--bounded', '--output', str(result_root)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        certificate = json.loads((result_root / 'certificate.json').read_text())
        protocol = json.loads((result_root / 'protocol.json').read_text())
    if sha256(source.read_bytes()).hexdigest() != REFERENCE_SHA256:
        raise ValueError('Frozen review source changed during verification')
    if certificate['status'] != 'PASS INDEPENDENT EXACT PHYSICAL CENTER AND ODD-LINE REVIEW':
        raise AssertionError('Review did not certify its declared finite scope')
    interfaces = [case for case in certificate['results'] if case['kind'] == 'interfaces']
    physical = [case['result'] for case in certificate['results'] if case['kind'] == 'physical']
    if len(interfaces) != 1 or len(interfaces[0]['cases']) != 15 or len(physical) != 3:
        raise AssertionError('Bounded review coverage changed')
    if not interfaces[0]['even_norm_label_rejected']:
        raise AssertionError('Missing even-norm negative control')
    if any(not case['omitted_feature_return_rejected'] or not case['wrong_raw_dirty_identity_rejected']
           or not case['virtual_dirty_restored'] for case in physical):
        raise AssertionError('Missing physical dirty-restoration controls')
    receipt = dict(status='PASS BOUNDED INDEPENDENT CENTER INTERFACES',
                   wrapper_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                   protocol=protocol, certificate=certificate,
                   scope=certificate['scope'])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(status=receipt['status'], odd_label_interfaces=15,
                          physical_cases=3, elapsed_seconds=certificate['elapsed_seconds'],
                          scope='Finite center-only Gaussian operators and dirty restoration; no native routing or exponent claim.')))


if __name__ == '__main__':
    main()
