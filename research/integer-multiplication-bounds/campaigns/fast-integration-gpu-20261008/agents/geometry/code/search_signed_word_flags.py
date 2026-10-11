#!/usr/bin/env python3
"""Bounded coherent coordinate-flag discovery on actual signed joint words.

Every signed symbol and forced coordinate receives the same permutation.
The native program performs its full rigorous prime-product rank replay.
Discovery keeps compact profiles; accepted winners need retained full matrix
audits and independent literal source/output relabeling checks.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.work.exists() and not args.output.exists()
    args.work.mkdir(parents=True)
    configurations = json.loads(args.input.read_text())
    rows = []
    cached = {}
    started = time.monotonic()
    environment = dict(os.environ)
    for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        environment[key] = '1'
    for config in configurations:
        source = Path(config['transitions'])
        if source not in cached:
            cached[source] = source.read_bytes()
        original = cached[source]
        h, vertices, roles, nf, nt, singles, mass, loss = struct.unpack_from('<6I2Q', original)
        assert len(original) == 40 + nf * (12 + h) + nt * 16
        order = config['order']
        assert sorted(order) == list(range(h))
        inverse = [0] * h
        for i, j in enumerate(order):
            inverse[j] = i
        packed = bytearray(original)
        for fid in range(nf):
            offset = 40 + fid * (12 + h)
            forced, rank = struct.unpack_from('<QI', original, offset)
            symbols = struct.unpack_from(f'<{h}b', original, offset + 12)
            relabeled = [0] * h
            for i, label in enumerate(symbols):
                relabeled[order[i]] = label
            forced_new = sum(1 << order[i] for i in range(h) if forced >> i & 1)
            assert sum(1 << inverse[i] for i in range(h) if forced_new >> i & 1) == forced
            assert tuple(relabeled[order[i]] for i in range(h)) == symbols
            struct.pack_into('<QI', packed, offset, forced_new, rank)
            struct.pack_into(f'<{h}b', packed, offset + 12, *relabeled)
        work = args.work / config['case_id']
        work.mkdir()
        input_path, profile_path = work / 'transitions.bin', work / 'profile.json'
        input_path.write_bytes(packed)
        command = [str(args.binary), str(input_path), config['basis'], str(profile_path)]
        with (work / 'run.log').open('wb') as log:
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=environment)
            (work / 'process.json').write_text(json.dumps(dict(pid=child.pid, command=command), indent=2) + '\n')
            print(json.dumps(dict(status='ACTUAL SIGNED WORD FLAG COMPUTING',
                pid=child.pid, case_id=config['case_id'], h=h)), flush=True)
            assert child.wait() == 0
        profile = json.loads(profile_path.read_text())
        assert profile['rank_sum'] == mass and profile['R'] == roles
        phi = sum(t * n * math.expm1(4e-5 * math.log(575 / t))
            for t, n in enumerate(profile['blocks']) if t and n)
        rows.append(dict(config=config, profile=profile, Phi_at_a_4e_5=phi,
            original_binary_sha256=sha256(original).hexdigest(),
            permuted_binary_sha256=sha256(packed).hexdigest(),
            permuted_binary_path=str(input_path), profile_path=str(profile_path),
            profile_sha256=sha256(profile_path.read_bytes()).hexdigest()))
        status = dict(utc=datetime.now(timezone.utc).isoformat(), completed=len(rows),
            total=len(configurations), elapsed_seconds=time.monotonic() - started, workers=1)
        (args.work / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
        (args.work / 'completed-rows.json').write_text(json.dumps(rows, indent=2) + '\n')
        print(json.dumps(status), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(status='PASS EXACT SIGNED WORD COORDINATE-FLAG DISCOVERY',
        rows=rows, completed_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=time.monotonic() - started,
        input_sha256=sha256(args.input.read_bytes()).hexdigest(),
        driver_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        native_sha256=sha256(Path(__file__).with_name('signed_joint_word_profiles.cpp').read_bytes()).hexdigest(),
        scope='Actual signed matrices, complete native CRT within every discovery run. '
            'Compact discovery profiles omit individual cleared-matrix audit tables. '
            'Accepted selected flags require fresh full audit output and literal '
            'source/center/output/both-dirty gate plus complete recurrence assembly.'
    ), indent=2) + '\n')


if __name__ == '__main__':
    main()
