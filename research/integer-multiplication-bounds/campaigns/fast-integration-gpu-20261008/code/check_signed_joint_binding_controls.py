#!/usr/bin/env python3
"""Targeted independent failure controls for signed physical-word binding.

Each deliberately incompatible input must fail the scientific binding. The
prime control rehashes its modified profile so rejection tests the rigorous
minor bound rather than merely detecting a stale file digest.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import bind_signed_joint_variant_certificate as verifier


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--axes', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    axes = verifier.read(args.axes)
    row = axes[0] if isinstance(axes, list) else axes['axes']['23']
    graph = verifier.read(args.word)
    cases = []
    for name in ['different-valid-coordinate-order', 'nonbijective-source-order',
                 'false-source-output-coherence', 'unrelated-word-transition',
                 'wrong-role-denominator', 'wrong-frame-codec',
                 'missing-reversed-orientation', 'insufficient-CRT-primes']:
        candidate, receipt = deepcopy(row), deepcopy(graph)
        if name == 'different-valid-coordinate-order':
            candidate['coordinate_order'][0:2] = candidate['coordinate_order'][1::-1]
        elif name == 'nonbijective-source-order':
            receipt['source_permutation'][0] = receipt['source_permutation'][1]
        elif name == 'false-source-output-coherence':
            receipt['coherent_source_output_labels'] = False
        elif name == 'unrelated-word-transition':
            receipt['transition_sha256'] = '0'*64
        elif name == 'wrong-role-denominator':
            receipt['R'] += 1
        elif name == 'wrong-frame-codec':
            receipt['frame_format'] = 'original-envelope-v1'
        elif name == 'missing-reversed-orientation':
            receipt['orientations'] = ['forward']
        else:
            candidate['profile']['primes'] = candidate['profile']['primes'][:1]
            profile = args.work/'insufficient-primes-profile.json'
            profile.write_text(json.dumps(candidate['profile'],indent=2)+'\n')
            candidate['profile_path'] = str(profile)
            candidate['profile_sha256'] = verifier.digest(profile)
        try:
            verifier.local(candidate, receipt)
        except AssertionError:
            cases.append(dict(case=name,status='REJECTED AS REQUIRED'))
        else:
            raise AssertionError('Incorrect scientific input was accepted: '+name)
    result = dict(status='PASS INDEPENDENT SIGNED-WORD ADVERSARIAL CONTROLS',
                  created_utc=datetime.now(timezone.utc).isoformat(),cases=cases,
                  verifier_sha256=verifier.digest(verifier.__file__),
                  source_sha256=verifier.digest(__file__),
                  inputs={str(p):verifier.digest(p) for p in [args.axes,args.word]},
                  scope='Targeted incompatible coordinates, word, roles, frame format, orientation and insufficient rigorous CRT bound.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],rejected=len(cases))))


if __name__ == '__main__':
    main()
