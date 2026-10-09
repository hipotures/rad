#!/usr/bin/env python3
"""Disposable bounded checks for actual subspace and two-axis phase frames."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


SOURCES = {
    'outer_axis_interface_review.py': 'b4db409f7ff3e1a2d0dc55fdd8a84a6447931a66d5f66a1111db70fe51f735b6',
    'canonical_subspace_frames.py': 'ddb0255a0668d43dd61c5183f3a0de56015f02b6acc462c4b8ad5b3f8173598b',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    certificates = {}
    with TemporaryDirectory(prefix='rad-phase-frame-primitives-') as temporary:
        for name, expected_hash in SOURCES.items():
            source = Path(__file__).with_name(name)
            if sha256(source.read_bytes()).hexdigest() != expected_hash:
                raise ValueError('Pinned finite verifier source changed: ' + name)
            output = Path(temporary) / name.removesuffix('.py')
            subprocess.run([sys.executable, '-B', str(source), '--workers', '1',
                            '--bounded', '--output', str(output)],
                           check=True, capture_output=True, text=True)
            certificates[name] = dict(protocol=json.loads((output / 'protocol.json').read_text()),
                                      certificate=json.loads((output / 'certificate.json').read_text()))
            if sha256(source.read_bytes()).hexdigest() != expected_hash:
                raise ValueError('Effective source changed during verification')
    outer = certificates['outer_axis_interface_review.py']['certificate']
    frames = certificates['canonical_subspace_frames.py']['certificate']
    if outer['status'] != 'PASS INDEPENDENT EXACT TWO-AXIS PHASE INTERFACE' or len(outer['cases']) != 4:
        raise AssertionError('Two-axis finite coverage changed')
    if any(case['source_sink_relative_rank'] != 4 or case['spectator_phi_rank'] != 6
           or case['omitted_line_rank'] != 5 for case in outer['cases']):
        raise AssertionError('Missing two-axis rank/line controls')
    if frames['status'] != 'PASS EXACT CANONICAL SUBSPACE FRAMES' or len(frames['cases']) != 1:
        raise AssertionError('Canonical finite coverage changed')
    case = frames['cases'][0]
    if case['subspaces'] != 16 or case['nested_interfaces'] != 66 or not case['even_line_C_shortcut_rejected']:
        raise AssertionError('Missing canonical subspace or degenerate controls')
    receipt = dict(status='PASS BOUNDED ACTUAL PHASE FRAME PRIMITIVES',
                   wrapper_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                   source_sha256=SOURCES, complete_bounded_receipts=certificates,
                   scope='Finite exact phase operators, affine/unit corrections and nested subspace frames. Native tape synthesis, full dirty master chronology and multiplier exponent remain open.')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as stream:
            stream.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(status=receipt['status'], canonical_subspaces=16,
                          nested_interfaces=66, outer_axis_cases=4, scope=receipt['scope'])))


if __name__ == '__main__':
    main()
