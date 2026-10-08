#!/usr/bin/env python3
"""Prepare a distinct fixed I+J profiler that also profiles rank-two increments.

The original profiler conservatively pays two singletons for rank two. This
variant applies its existing ordered-corner/run decomposition to rank two as
well. It reuses the same proved rank-four CRT bound and retains rank-one and
identity fallbacks. It makes no improvement claim before a completed receipt.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess

from fixed_profiler_prepare import PIN, SOURCE, crt_enclosure


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--max-dimension', type=int, default=28)
    ap.add_argument('--compiler', default=os.environ.get('CXX', 'c++'))
    ap.add_argument('--no-compile', action='store_true')
    args = ap.parse_args()
    assert __debug__, 'Run without Python -O'
    if not 6 <= args.max_dimension <= 28:
        ap.error('Supported dimensions are6..28, except9')
    source_root = args.source_root.resolve()
    original = (source_root/SOURCE).read_text()
    assert original.count('assert(h==23)') == 2
    assert original.count('if(rr<=2)') == 1
    assert original.count('.h23_five_prime_profiles.json') == 1
    variant = original.replace('assert(h==23)', 'assert(h>=6&&h<=%d&&h!=9)' % args.max_dimension)
    variant = variant.replace('if(rr<=2)', 'if(rr<=1)')
    variant = variant.replace('.h23_five_prime_profiles.json', '.fixed_ij_rank2_profiles.json')
    variant = variant.replace('This adapted h23 run', 'This bounded rank-two-inclusive run')
    variant = variant.replace('Uniform h23 rank-four bound', 'Bounded general-h rank-four bound')
    enclosures = [crt_enclosure(h) for h in range(6,args.max_dimension+1) if h != 9]
    args.output.mkdir(parents=True,exist_ok=False)
    target, binary = args.output/'fixed_ij_rank2_profiles.cpp', args.output/'fixed_ij_rank2_profiles'
    target.write_text(variant)
    command = [*shlex.split(args.compiler), '-O3', '-std=c++17', '-I',
               str(source_root/'scripts/partial_swap'), str(target), '-o', str(binary)]
    receipt = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                   source_pin=PIN, source_file=SOURCE,
                   source_sha256=hashlib.sha256(original.encode()).hexdigest(),
                   generated_sha256=hashlib.sha256(variant.encode()).hexdigest(),
                   wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   bound_helper_sha256=hashlib.sha256((Path(__file__).parent/'fixed_profiler_prepare.py').read_bytes()).hexdigest(),
                   compile_command=command, max_dimension=args.max_dimension,
                   change='Profile rank-two increments with the same rational northeast-rank reconstruction',
                   fixed_output_suffix='.fixed_ij_rank2_profiles.json',
                   crt_enclosures=enclosures, compiled=False,
                   scope='No saving claim; compare completed blocks against an ORIGINAL-envelope base profile')
    if not args.no_compile:
        subprocess.run(command,check=True)
        receipt['compiled'] = True
        receipt['binary_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(source=str(target),binary=str(binary),compiled=receipt['compiled'],
                          output_suffix=receipt['fixed_output_suffix']),indent=2))


if __name__ == '__main__':
    main()
