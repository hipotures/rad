#!/usr/bin/env python3
"""Profile a pinned executed joint word, including the conjugate I+J basis.

Transition extraction is inherited from pinned PR62/57 and independently
reconstructs the multiset from XOR operations before comparing compiler events.
The literal-word and dirty-basis verification is a separate graph-owned gate.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--h', type=int, choices=[23, 25], required=True)
    ap.add_argument('--binary', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--modes', nargs='+', default=['fixed', 'fixed-transpose', 'fixed-all', 'fixed-transpose-all'])
    args = ap.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    start = time.monotonic()
    sys.dont_write_bytecode = True
    scripts = args.source/'scripts/experiments'
    frame = args.source/'research/pair-assembly/frame'
    prepare_source = scripts/'binary_frame_profile_prepare.py'
    math_source = scripts/'binary_frame_math.py'
    prepare = load('pinned_joint_prepare', prepare_source).prepare
    exactness = load('pinned_joint_math', math_source).exactness(args.h)
    word = frame/f'frame-word-{args.h}.json.gz'
    transitions = args.work/'transitions.bin'
    (args.work/'process.json').write_text(json.dumps(dict(pid=os.getpid(),command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
    prepared = json.loads(json.dumps(prepare(word, transitions)))
    assert prepared == json.loads((frame/f'frame-transitions-{args.h}.json').read_text())
    expected = json.loads((frame/f'frame-profiles-{args.h}.json').read_text())
    profiles = {}
    env = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        env[key] = '1'
    for mode in args.modes:
        command = [str(args.binary), str(transitions), mode]
        with (args.work/f'{mode}.log').open('wb') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
            (args.work/'native-process.json').write_text(json.dumps(dict(pid=child.pid,command=command,started_utc=datetime.now(timezone.utc).isoformat()),indent=2)+'\n')
            print(json.dumps(dict(status='ACTUAL JOINT WORD PROFILES RUNNING',h=args.h,mode=mode,pid=child.pid)),flush=True)
            assert child.wait() == 0, mode
        path = Path(str(transitions)+'.'+mode+'.profiles.json')
        profile = json.loads(path.read_text())
        assert profile['rank_sum'] == prepared['rank_mass']
        assert profile['R'] == prepared['R'] and profile['loss'] == args.h*(args.h-1)
        if mode == 'fixed':
            assert profile == expected, 'Unmodified fixed-basis profile differs from pinned public result'
        profiles[mode] = profile
        status = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(profiles),total=len(args.modes),elapsed_seconds=time.monotonic()-start)
        (args.work/'status.json').write_text(json.dumps(status,indent=2)+'\n')
        print(json.dumps(dict(status='ACTUAL JOINT WORD PROFILE COMPLETE',h=args.h,mode=mode,blocks=profile['blocks'],**status)),flush=True)
    result = dict(status='PASS EXACT ACTUAL JOINT WORD CORNER PROFILES',utc=datetime.now(timezone.utc).isoformat(),h=args.h,
        prepared=prepared,profiles=profiles,exactness=exactness,elapsed_seconds=time.monotonic()-start,
        input_sha256={str(x):digest(x) for x in [word,prepare_source,math_source]},
        source_sha256=digest(Path(__file__)),native_source_sha256=digest(Path(__file__).with_name('joint_word_conjugate_profiles.cpp')),
        binary_sha256=digest(args.binary),transition_binary_sha256=digest(transitions),
        scope='Actual XOR-word transition multiset, fresh bounded-minor NE profiles. Literal physical chronology, source-only recovery, and complete recurrence are separate gates. The -all modes replace conservative rank-two singleton expansions with exact profiles.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
