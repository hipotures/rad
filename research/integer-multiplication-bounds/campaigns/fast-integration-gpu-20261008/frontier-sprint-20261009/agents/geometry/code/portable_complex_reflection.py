#!/usr/bin/env python3
"""Replay the independent complex gate from a portable publication package.

This wrapper consumes a fresh constructor export; it neither imports nor
calls the producer. The separately published construction wrapper rebuilds
the signed DAG from source modules and compact frozen matching/frame inputs.
The independent reviewer regenerates module contracts, full closure, literal
carrier allocation and both complete physical orientations. Python3.11+,
stdlib only. Public metadata normalization gets its own provenance pin;
all eight exact mathematical input identities remain those independently
reviewed in the original winning research run.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


REVIEWER_SHA256 = '8c94c3fa8a717b284433f5eae09d028c7073466008e013948b11057e2e044fd8'
BASELINE_SHA256 = '0fd75e755e23eb4746397dd394ee8d5f38d7b35bbd71d215a32429bef23d6d97'
FORWARD_SHA256 = '1cec7820ae80b9e1be1fc9b489003f06d26c559d9d6d46944144f5ae62d98ecc'
REFLECTED_SHA256 = 'cd0f5fc725c22aa295645f6d28b3f10cbad1f1c21ddf6200613efa8aa0aac6cb'
FILES = ('graph.json','baseline.json','frames.json','word.json','profile-before.json',
         'physical-frames.json','physical-pairs.json','profile.json','protocol.json')
PIN_KEYS = {'graph.json':'graph','frames.json':'witness','word.json':'word',
            'profile-before.json':'record','physical-frames.json':'candidate_frames',
            'physical-pairs.json':'pairs','profile.json':'candidate_profile',
            'protocol.json':'fused_construction_protocol'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inside(root, relative):
    result = (root/relative).resolve()
    need(result.is_relative_to(root.resolve()), 'package path escapes its root')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2],
                        help='Publication package or repository root.')
    parser.add_argument('--export', type=Path, required=True, help='Fresh complete output from the separate source constructor.')
    parser.add_argument('--output-dir', type=Path, required=True, help='Fresh independent reviewer output directory.')
    args = parser.parse_args()
    need(sys.version_info >= (3,11), 'Python 3.11 or newer required')
    need(not sys.flags.optimize, 'assertion-disabled portable replay rejected')
    root = args.root.resolve()
    if (root/'research/lifetime-fused-frames').is_dir():
        root = root/'research/lifetime-fused-frames'
    reviewer = inside(root,'independent/code/reflected_paid_replay_fused168.py')
    tree = inside(root,'sources/pr168')
    helper = inside(root,'complex/code/screen_pr168_modules.py')
    pins_path = inside(root,'independent/complex-pins.json')
    need(sha256(reviewer.read_bytes()).hexdigest() == REVIEWER_SHA256, 'immutable independent reviewer changed')
    pins = json.loads(pins_path.read_text())
    export = args.export.resolve()
    output = args.output_dir.resolve()
    need(not output.is_relative_to(root) and not output.is_relative_to(export), 'outputs must be outside immutable inputs')
    output.mkdir(parents=True)
    restored = {}
    for name in FILES:
        content = (export/name).read_bytes()
        digest = sha256(content).hexdigest()
        if name in PIN_KEYS:
            need(digest == pins['sha256'][PIN_KEYS[name]], 'fresh constructor/independent pin mismatch: '+name)
        else:
            need(digest == BASELINE_SHA256, 'fresh baseline input differs')
        json.loads(content.decode('utf-8'))
        restored[name] = dict(sha256=digest, bytes=len(content))
    protocol = dict(scope='Consumed exact fresh constructor outputs; source DAG/module provenance is a separate check.',
                    reviewer_sha256=REVIEWER_SHA256,
                    pins_sha256=sha256(pins_path.read_bytes()).hexdigest(), files=restored)
    with (output/'portable-constructor-inputs.json').open('x') as stream:
        json.dump(protocol,stream,indent=2,sort_keys=True)
        stream.write('\n')
    command = [sys.executable,'-I',str(reviewer),'--export',str(export),'--tree',str(tree),
               '--frames',str(export/'physical-frames.json'),'--profile',str(export/'profile.json'),
               '--construction-code',str(helper),'--pins',str(pins_path),
               '--output',str(output/'independent-reflected-review.json'),
               '--events',str(output/'independent-forward-literal.jsonl.gz')]
    completed = subprocess.run(command)
    need(completed.returncode == 0, 'full independent reflected reviewer rejected the portable input')
    result = json.loads((output/'independent-reflected-review.json').read_text())
    need(result['forward_literal_sha256'] == FORWARD_SHA256 and result['reflected_literal_sha256'] == REFLECTED_SHA256,
         'portable full event streams differ from the exact frozen winner')
    transfer = dict(status='PORTABLE_FULL_REPLAY_REPRODUCES_EXACT_WINNER',
                    forward_literal_sha256=FORWARD_SHA256, reflected_literal_sha256=REFLECTED_SHA256,
                    reviewer_sha256=REVIEWER_SHA256, input_sha256=result['input_sha256'],
                    wrapper_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                    scope='Fresh complete finite replay with explicitly adapted public provenance pins; bit, prime, moment and assembly gates remain separate.')
    with (output/'portable-reflection-binding.json').open('x') as stream:
        json.dump(transfer,stream,indent=2,sort_keys=True)
        stream.write('\n')


if __name__ == '__main__':
    main()
