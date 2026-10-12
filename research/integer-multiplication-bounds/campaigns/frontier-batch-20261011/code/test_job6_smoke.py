#!/usr/bin/env python3
"""Smoke test of job6_retime_search.py (about a minute, stdlib only).

Two toy words whose registers all end in U = <1,2,4> (dim 3), so every admissible gate frame is one of the 16
subspaces of U and the optimum is found by brute force:
  toy1   source starts at <1>, helpers and target at 0; hand-computed profile {1:5, 2:3},
         Phi = 3*Phi(2) + 5*Phi(1); optimum: every register climbs once (Phi(2) + 3*Phi(3))
  toy2   source is a centre at <1> and the target level is <1>: both must be exactly at <1> when the centres
         phase begins, so an A gate touching them cannot be moved; hand-computed profile {1:7, 2:2}
Checks:
  1. the replay reproduces the hand-computed profiles (supported() == ok)
  2. validate_state rejects a decreasing frame and a target that leaves its level before the centres phase
  3. brute force over all 16^4 timings equals the annealer's best for both toys
  4. up to 3000 random cascaded raise/lower moves (at least 1000 applied) on a real word (if job 5's #502 word is present, else on toy1) keep every
     state admissible: validate_state passes and the incremental Phi equals the from-scratch Phi
  5. the command line run (two toys, 2 workers, ~7 s) writes SUMMARY.json and BEST files with the brute-force gains

usage: test_job6_smoke.py [--real-word PATH]
"""
import gzip
import itertools
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job6_retime_search as J  # noqa: E402

PHI = lambda r: r * math.log(73 / r)  # noqa: E731
U = [4, 2, 1]
SUBS = sorted({tuple(J.canonical_basis(list(c))) for k in range(4) for c in itertools.combinations([1, 2, 3, 4, 5, 6, 7], k)})
assert len(SUBS) == 16, len(SUBS)


def toy(kind):
    # frame indices: 0 = {}, 1 = U, 2 = <1>, 3 = <2,1>
    frames = [[], U, [1], [2, 1]]
    c = dict(v=1, R=2, h=9, frames=frames, precondition=[], compensation=[], cleanup=[], cut=[], edges=[],
             final=[1, 1, 1, 1])
    if kind == 1:
        c.update(start=[2, 0, 0, 0], centers=[], center_frames=[],
                 A=[['add', 2, 0, 1, 1, 2], ['add', 3, 2, 1, 1, 3]],
                 B=[['add', 1, 2, 1, 1, 3], ['add', 1, 3, 1, 1, 1]],
                 local_profile={'1': 5, '2': 3})
    else:
        # source 0 is a centre at <1>; target 1 has level <1>; A: target += source at <1>, helper 2 += source at <1>
        # (both pinned); helper 3 is free. B: target += helper 2 at <2,1>, target += helper 3 at U.
        c.update(start=[2, 0, 0, 0], centers=[0], center_frames=[2], target_levels={'0': 2},
                 A=[['add', 1, 0, 1, 1, 2], ['add', 2, 0, 1, 1, 2], ['add', 3, 2, 1, 1, 3]],
                 B=[['add', 1, 2, 1, 1, 3], ['add', 1, 3, 1, 1, 1]],
                 local_profile={'1': 7, '2': 2})
        # climbs: source <1> -> U (2); target 0-><1>, <1>-><2,1>, <2,1>->U (1,1,1); helper 2 0-><1>, <1>-><2,1>,
        # <2,1>->U (1,1,1); helper 3 0-><2,1> (2), <2,1>->U (1)  =>  {1: 7, 2: 2}
    return c


def brute(c):
    best = None
    for combo in itertools.product(SUBS, repeat=len(c['A']) + len(c['B'])):
        try:
            prof = J.validate_state(c, [list(x) for x in combo])
        except AssertionError:
            continue
        p = J.phi_of(prof)
        best = p if best is None or p < best else best
    return best


def main():
    failures = []

    def expect(cond, what):
        print(('ok   ' if cond else 'FAIL ') + what, flush=True)
        if not cond:
            failures.append(what)

    toys = {1: toy(1), 2: toy(2)}
    for k, c in toys.items():
        ok, why = J.supported(c)
        expect(ok, f'toy{k}: replay reproduces the hand-computed profile ({why})')
    p1 = J.phi_of(J.validate_state(toys[1], [[1], [2, 1], [2, 1], U]))
    expect(abs(p1 - (3 * PHI(2) + 5 * PHI(1))) < 1e-9, 'toy1: Phi = 3*Phi(2) + 5*Phi(1)')

    for name, frames, msg in (('decreasing frame', [[1], [2, 1], [1], U], 'frame decreases'),):
        try:
            J.validate_state(toys[1], frames)
            expect(False, f'validate rejects {name}')
        except AssertionError as exc:
            expect(msg in str(exc), f'validate rejects {name}')
    try:
        J.validate_state(toys[2], [U, U, U, U, U])
        expect(False, 'validate rejects a target above its level before the centres phase')
    except AssertionError as exc:
        expect('target level' in str(exc), 'validate rejects a target above its level before the centres phase')

    tmp = Path(tempfile.mkdtemp(prefix='job6-smoke-'))
    paths = {}
    for k, c in toys.items():
        paths[k] = tmp / f'toy{k}.json.gz'
        paths[k].write_bytes(gzip.compress(json.dumps(c).encode(), mtime=0))
    opt = {}
    for k, c in toys.items():
        t0 = time.time()
        opt[k] = brute(c)
        r = J.anneal(dict(path=str(paths[k]), word_id=f'toy{k}', seed=7, deadline=time.time() + 3,
                          out_dir=str(tmp), cycle_s=1.0))
        start = J.phi_of(J.validate_state(c, [J.canonical_basis(c['frames'][e[-1]]) for e in c['A'] + c['B']]))
        expect(abs(r['phi_climbs_best'] - opt[k]) < 1e-6 and abs(r['phi_climbs_start'] - start) < 1e-6,
               f'toy{k}: annealer best {r["phi_climbs_best"]:.4f} == brute-force optimum {opt[k]:.4f} '
               f'(start {start:.4f}, brute force {time.time() - t0:.1f} s)')
        J.validate_state(c, r['gate_frames_best'])
    expect(abs(opt[1] - (PHI(2) + 3 * PHI(3))) < 1e-9, 'toy1: optimum is the one-climb-per-register bound')

    real = None
    if '--real-word' in sys.argv:
        real = sys.argv[sys.argv.index('--real-word') + 1]
    else:
        root = os.environ.get('RAD_WORK_ROOT', '')
        cand = list(Path(root).glob('runs/*-job5/out/pr-502-*/gauge80-kernel42/split-centres/CANONICAL-WORD.json.gz')) if root else []
        real = str(cand[0]) if cand else None
    c = J.load_word(real)[0] if real else toys[1]
    ok, why = J.supported(c)
    expect(ok, f'cascade test word supported ({"real " + Path(real).parent.parent.parent.name if real else "toy1"}: {why})')
    w = J.Word(c)
    rng = random.Random(3)
    applied = 0
    for _ in range(200000):
        r = rng.randrange(w.n)
        pl = w.plateaus(r)
        if len(pl) < 2:
            continue
        a = rng.randrange(1, len(pl))
        ov, touched = {}, set()
        if rng.random() < 0.5:
            if pl[a - 1][0] == 0:
                continue
            okm = w.raise_(r, pl[a - 1][0], J.sub_between(pl[a - 1][2], pl[a][2], rng) if rng.random() < .3 else pl[a][2], ov, touched)
        else:
            okm = w.lower_(r, pl[a][1], J.sub_between(pl[a - 1][2], pl[a][2], rng) if rng.random() < .3 else pl[a - 1][2], ov, touched)
        if okm and ov and sum(w.regcost(x, ov) for x in touched) < J.INF:
            for g, f in ov.items():
                w.g[g] = f
            applied += 1
            if applied >= 3000:
                break
    try:
        prof = J.validate_state(c, [J.canonical_basis(J.basis_of(m)) for m in w.g])
        expect(applied >= (1000 if real else 50), f'{applied} random cascaded moves applied')
        expect(abs(J.phi_of(prof) - w.total()) < 1e-6,
               f'the moves keep the timing admissible; incremental Phi {w.total():.4f} == from-scratch Phi {J.phi_of(prof):.4f}')
    except AssertionError as exc:
        expect(False, f'random cascaded moves keep the timing admissible ({exc!r})')

    out = tmp / 'cli'
    subprocess.run([sys.executable, '-B', str(HERE / 'job6_retime_search.py'), '--out', str(out), '--word', str(paths[1]),
                    '--word', str(paths[2]), '--hours', str(6 / 3600), '--workers', '2', '--cycle-min', '0.02'],
                   check=True, capture_output=True)
    s = json.loads((out / 'SUMMARY.json').read_text())
    gains = sorted(round(b['phi_climbs_best'], 6) for b in s['best'].values())
    expect(s['supported'] == 2 and gains == sorted(round(opt[k], 6) for k in (1, 2))
           and len(list(out.glob('BEST-*.json'))) == 2, f'command line: 2 words, best Phi {gains}')
    print(f'\n{len(failures)} failure(s)')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
