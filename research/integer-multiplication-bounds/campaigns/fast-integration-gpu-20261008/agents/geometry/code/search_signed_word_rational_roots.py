#!/usr/bin/env python3
"""Discover exact rational entry loci and certify actual signed-word profiles.

Each locus is a necessary local discovery hint, not a rank or moment claim.
The selected bases receive complete native bounded-minor NE-rank replay on the
actual signed transition multiset. Source/data geometry and assembly are separate.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--extractor', type=Path, required=True)
    parser.add_argument('--profiler', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--top', type=int, default=24)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    sources = json.loads(args.input.read_text())
    configuration = []
    manifests = []
    for source in sources:
        transition = Path(source['transitions'])
        h = struct.unpack_from('<I', transition.read_bytes())[0]
        assert h in (23, 25)
        loci = args.work / f'h{h}-signed-entry-loci.json'
        command = [str(args.extractor), str(transition), str(loci)]
        with (args.work / f'h{h}-loci.log').open('wb') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        discovery = json.loads(loci.read_text())
        assert discovery['h'] == h
        scores = {}
        exclude = set(source.get('already_profiled_bases', []))
        for pattern in discovery['patterns']:
            a, b, c = map(int, pattern['coefficients'])
            for root in pattern['rational_roots']:
                if not root['admissible']:
                    continue
                beta = Fraction(int(root['numerator']), int(root['denominator']))
                assert a + b * beta + c * beta * beta == 0
                basis = f'beta:{beta.numerator}:{beta.denominator}'
                if basis not in exclude:
                    scores[basis] = scores.get(basis, 0) + pattern['weighted_entries']
        for basis, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:args.top]:
            configuration.append(dict(case_id=f'h{h}-signed-entry-root-{basis.replace(":", "-")}',
                basis=basis, transitions=str(transition), discovery_weighted_entries=score))
        manifests.append(dict(h=h, source_sha256=sha256(transition.read_bytes()).hexdigest(),
            loci_sha256=sha256(loci.read_bytes()).hexdigest(), command=command,
            exact_entry_patterns=discovery['unique_polynomials'],
            admissible_unprofiled_bases=len(scores)))
        print(json.dumps(dict(status='EXACT SIGNED WORD ENTRY LOCI DISCOVERED',
            h=h, patterns=discovery['unique_polynomials'], novel_bases=len(scores))), flush=True)
    assert configuration
    profiles = args.work / 'selected-rational-roots.json'
    profiles.write_text(json.dumps(configuration, indent=2) + '\n')
    protocol = dict(utc=datetime.now(timezone.utc).isoformat(), command=sys.argv,
        source_inputs=manifests, configurations=len(configuration),
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        extractor_sha256=sha256(args.extractor.read_bytes()).hexdigest())
    (args.work / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n')
    command = [sys.executable, '-u', str(Path(__file__).with_name('run_joint_word_parameters.py')),
        '--input', str(profiles), '--binary', str(args.profiler),
        '--work', str(args.work / 'actual-profile-replays'), '--output', str(args.output)]
    subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
