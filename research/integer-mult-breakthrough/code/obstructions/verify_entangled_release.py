#!/usr/bin/env python3
"""Replay exact fixed-word minima with product and entangled L_E frames.

This is a finite geometric discriminator, not a Gaussian circuit or an
all-size shared-release bound. The patched finite-factor engine is compiled
in a disposable directory. OpenAI Codex assisted this independent check.
"""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile

import entangled_release_probe as probe


def path_charge(data, assignment):
    geometry = probe.scalar.f
    current = list(data['starts'])
    charge = 0
    for gate, (destination, source, _) in enumerate(data['word']):
        frame = data['frames'][assignment[gate]]
        for role in (destination, source):
            charge += geometry.distance(current[role], frame, data['active_bits'])
            current[role] = frame
    for initial, endpoint in zip(current, data['ends']):
        charge += geometry.distance(initial, endpoint, data['active_bits'])
    return charge


def verify(work):
    generated = work / 'parallel.cpp'
    executable = work / 'finite-factor'
    subprocess.run(['patch', '-o', str(generated), str(probe.scalar.CPP),
                    str(probe.parallel.PATCH)], check=True, capture_output=True, text=True)
    subprocess.run(['c++', '-O3', '-std=c++17', '-fopenmp', str(generated),
                    '-o', str(executable)], check=True, capture_output=True, text=True)
    old_environment = {key: os.environ.get(key) for key in ('OMP_NUM_THREADS', 'OMP_DYNAMIC')}
    os.environ['OMP_NUM_THREADS'] = '2'
    os.environ['OMP_DYNAMIC'] = 'FALSE'
    cases = []
    try:
        for index, (copies, family) in enumerate([(1, 'all-LE'), (2, 'product'), (2, 'all-LE')]):
            data = probe.model(copies, family)
            n = 2 * copies
            geometry = probe.scalar.f
            source_labels = [tuple(1 << (2 * j + t) for j in range(copies)) for t in range(2)]
            zero = geometry.le((), n)
            full = geometry.le(tuple(1 << j for j in range(n)), n)
            expected_starts = [geometry.le(T, n) for T in source_labels] + [zero] * 3
            expected_ends = [full] * 2 + [geometry.le(geometry.perpendicular(T, n), n)
                                          for T in source_labels] + [full]
            assert data['starts'] == expected_starts and data['ends'] == expected_ends
            assert all(len(F) == n and not any(geometry.pairing(a, b, n) for a in F for b in F)
                       for F in data['frames'])
            probe.scalar.scalar_replay(data['word'], 2)
            answer = probe.parallel.full_solve(executable, work / f'case-{index}',
                                              data['edges'], data['unary'], data['table'],
                                              data['constant'], data['order'])
            assert answer['optimum'] == 10 * copies
            assert path_charge(data, answer['assignment']) == answer['optimum']
            cases.append(dict(copies=copies, family=family, frames=len(data['frames']),
                              optimum=answer['optimum'], capacity=5 * n,
                              graph_input_sha256=answer['graph_input_sha256'],
                              candidate_evaluations=data['preflight']['candidate_evaluations'],
                              payload_peak_bytes=data['preflight']['payload_peak_bytes']))
        # Completeness of the canonical four-dimensional subspace domain is
        # checked against the Gaussian-binomial counts in each dimension.
        subspaces = geometry.subspaces(4)
        assert Counter(map(len, subspaces)) == {0: 1, 1: 15, 2: 35, 3: 15, 4: 1}
        product_frames = set(probe.model(2, 'product')['frames'])
        all_frames = set(probe.model(2, 'all-LE')['frames'])
        assert product_frames < all_frames and len(all_frames - product_frames) == 42
    finally:
        for key, value in old_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    return dict(status='PASS EXACT FIXED-WORD PRODUCT/ENTANGLED DISCRIMINATOR',
                recorded_utc=datetime.now(timezone.utc).isoformat(), cases=cases,
                additional_entangled_frames=42,
                generated_parallel_source_sha256=sha256(generated.read_bytes()).hexdigest(),
                scope='Selected L_E domains and fixed side-inside scalar word only; general Lagrangians, Gaussian lifts, arbitrary words and an all-size f factor are not certified.')


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='rad-entangled-release-') as directory:
        print(json.dumps(verify(Path(directory)), indent=2))
