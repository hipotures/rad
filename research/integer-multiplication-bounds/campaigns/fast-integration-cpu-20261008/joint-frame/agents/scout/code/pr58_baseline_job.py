#!/usr/bin/env python3
"""Focused replay jobs on the task-owned tested PR58 source copy.

Upstream source notices and AI-assistance disclosures remain unchanged.
This wrapper distinguishes those exact baseline replays from the separate
authored independent physical-word and complete-moment checks.
"""
import argparse
from datetime import datetime,timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root',required=True,type=Path)
    ap.add_argument('--kind',choices=('producer','profiles'),required=True)
    ap.add_argument('--h',type=int,choices=(23,25))
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    source=args.source_root.resolve();here=source/'scripts/experiments'
    args.output.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    inputs=['binary_frame_compiler.py','joint_dual_compiler.py','binary_frame_replay.py',
            'binary_frame_profile_prepare.py','binary_frame_profiles.cpp','binary_frame_math.py']
    protocol=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),
                  kind=args.kind,h=args.h,source_commit='bc2f7ed4c20dc18898305ab17165c0c995cbb804',
                  wrapper_sha256=sha(Path(__file__)),
                  focused_source_sha256={name:sha(here/name) for name in inputs},
                  source_root=str(source),native_threads=1,
                  scope='Focused unmodified upstream baseline replay; independently authored reviews are recorded separately')
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    sys.path.insert(0,str(here));sys.dont_write_bytecode=True
    if args.kind=='producer':
        assert args.h
        from joint_dual_compiler import compile_axis
        stored=json.loads((source/'certificates/joint-dual-compiler.json').read_text())
        compiled,word=compile_axis(args.h)
        expected=gzip.decompress((source/f'certificates/joint-dual-word-{args.h}.json.gz').read_bytes())
        raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
        assert raw==expected
        assert json.loads(json.dumps(compiled))==stored['axes'][str(args.h)]['compiled']
        (args.output/'word.json.gz').write_bytes(gzip.compress(raw,mtime=0))
        result=dict(status='UPSTREAM PRODUCER/COMPILER EXACT REGENERATION PASS',
                    compiled=compiled,complete_word_decompressed_sha256=hashlib.sha256(raw).hexdigest(),
                    input_word_gzip_sha256=sha(source/f'certificates/joint-dual-word-{args.h}.json.gz'),
                    tested_word_byte_equality=True)
    else:
        from binary_frame_profile_prepare import prepare
        cpp=here/'binary_frame_profiles.cpp';binary=args.output/'profiles'
        cmd=['c++','-O3','-std=c++17','-I',str(source/'references/frame-compiler/pr48/scripts/partial_swap'),str(cpp),'-o',str(binary)]
        with (args.output/'compile.log').open('w') as log:
            subprocess.run(cmd,check=True,stdout=log,stderr=log)
        axes=[]
        for h in (23,25):
            transitions=args.output/f'word{h}.bin'
            prepared=prepare(source/f'certificates/joint-dual-word-{h}.json.gz',transitions)
            expected=json.loads((source/f'certificates/joint-dual-transitions-{h}.json').read_text())
            assert json.loads(json.dumps(prepared))==expected
            with (args.output/f'profile{h}.log').open('w') as log:
                subprocess.run([str(binary.resolve()),str(transitions.resolve())],check=True,stdout=log,stderr=log)
            actual=json.loads(Path(str(transitions)+'.profiles.json').read_text())
            assert actual==json.loads((source/f'certificates/joint-dual-profiles-{h}.json').read_text())
            axes.append(dict(h=h,prepared=prepared,profile=actual,transitions_sha256=sha(transitions)))
            (args.output/'progress.json').write_text(json.dumps(dict(axes=axes),indent=2)+'\n')
        result=dict(status='UPSTREAM ACTUAL TRANSITIONS/CRT PROFILES EXACT REPLAY PASS',axes=axes,
                    compile_command=cmd,binary_sha256=sha(binary))
    result.update(completed_utc=datetime.now(timezone.utc).isoformat(),seconds=time.monotonic()-start,
                  protocol_sha256=sha(args.output/'protocol.json'),native_threads=1)
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],seconds=result['seconds'],h=args.h)),flush=True)


if __name__=='__main__':main()
