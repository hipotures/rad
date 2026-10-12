#!/usr/bin/env python3
"""Smoke test of job7_reorder_search.py (about a minute, stdlib only).

Two toy words over U = <1,2> (5 subspaces), found by a random search for cases where moving commuting gates beats
every frame timing of the original order (one rank-2 climb instead of two rank-1 climbs):
  toy189  source 0 is a centre at <1>; A: h4+=h3, s0+=h2, h2+=h3, h2+=s0; B: t1+=h3; all frames <1>.
          Hand-computed profile {1: 9}.
  toy359  helper 2 is a centre at <2>; A: h2+=s0, s0+=h4, h3+=h4, h3+=h2 (frames <2>); B: t1+=h4 (frame U).
Checks:
  1. the replay reproduces the hand-computed profile of toy189, and both toys pass the format gate
  2. brute force over all frame timings: the optimum over every admissible gate order is strictly below the
     optimum of the original order, for both toys
  3. job 6's annealer (fixed order) reaches exactly the fixed-order optimum; job 7's annealer reaches exactly the
     reorder optimum, and its final record passed validate_order_state with the exact rational replay
  4. validate_order_state rejects a swapped non-commuting pair, and the exact replay of that swap differs
  5. 3000 random accepted gate/frame moves on a real word (job 6's #527 word, else job 5's #502 word, else toy189)
     leave a state that passes validate_order_state with the exact replay; incremental Phi == from-scratch Phi
  6. the command line run (two toys, 2 workers, ~6 s) writes SUMMARY.json with the reorder optima

usage: test_job7_smoke.py [--real-word PATH]
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
import job6_retime_search as J6  # noqa: E402
import job7_reorder_search as J7  # noqa: E402

SUBS = [[], [1], [2], [3], [2, 1]]
FR = [J6.elems(x) for x in SUBS]


def toy(kind):
    base = dict(v=1, R=3, frames=SUBS, final=[4] * 5, cut=[], target_levels={}, precondition=[], compensation=[],
                cleanup=[], edges=[])
    if kind == 189:
        base.update(start=[1, 0, 0, 0, 0], centers=[0], center_frames=[1],
                    A=[['add', 4, 3, 1, 1, 1], ['add', 0, 2, 1, 1, 1], ['add', 2, 3, 1, 1, 1], ['add', 2, 0, 1, 1, 1]],
                    B=[['add', 1, 3, 1, 1, 1]], local_profile={'1': 9})
    else:
        base.update(start=[2, 0, 0, 0, 0], centers=[2], center_frames=[2],
                    A=[['add', 2, 0, 1, 1, 2], ['add', 0, 4, 1, 1, 2], ['add', 3, 4, 1, 1, 2], ['add', 3, 2, 1, 1, 2]],
                    B=[['add', 1, 4, 1, 1, 4]])
        w = J6.Word(base)
        base['local_profile'] = {str(k): v for k, v in J6.validate_state(base, [J6.canonical_basis(J6.basis_of(m))
                                                                               for m in w.g]).items()}
    return base


def evaluate(c, order, frames):
    """Phi of a toy timing (order = gate ids, A part then B part), or None if not admissible."""
    try:
        oa = [g for g in order if g < len(c['A'])]
        ob = [g for g in order if g >= len(c['A'])]
        return J6.phi_of(J7.validate_order_state(c, oa, ob, frames))
    except AssertionError:
        return None


def optimum(c, orders):
    G = c['A'] + c['B']
    best = None
    for order in orders:
        for combo in itertools.product(range(len(SUBS)), repeat=len(G)):
            v = evaluate(c, order, [SUBS[k] for k in combo])
            if v is not None and (best is None or v < best - 1e-12):
                best = v
    return best


def linear_extensions(c):
    G = c['A'] + c['B']
    nA = len(c['A'])
    out = []
    for p in itertools.permutations(range(nA)):
        pos = {g: i for i, g in enumerate(p)}
        if all(J7.commute(G[a], G[b]) or pos[a] < pos[b] for a in range(nA) for b in range(a + 1, nA)):
            out.append(list(p) + list(range(nA, len(G))))
    return out


def main():
    failures = []

    def expect(cond, what):
        print(('ok   ' if cond else 'FAIL ') + what, flush=True)
        if not cond:
            failures.append(what)

    toys = {k: toy(k) for k in (189, 359)}
    for k, c in toys.items():
        ok, why = J6.supported(c)
        expect(ok, f'toy{k}: format gate ({why})')
    expect(toys[189]['local_profile'] == {'1': 9}, 'toy189: hand-computed profile {1: 9}')

    tmp = Path(tempfile.mkdtemp(prefix='job7-smoke-'))
    opt = {}
    for k, c in toys.items():
        t0 = time.time()
        fixed = optimum(c, [list(range(len(c['A']) + len(c['B'])))])
        reord = optimum(c, linear_extensions(c))
        opt[k] = reord
        expect(reord < fixed - 1e-9, f'toy{k}: reorder optimum {reord:.4f} < fixed-order optimum {fixed:.4f} '
                                     f'(brute force {time.time() - t0:.1f} s)')
        path = tmp / f'toy{k}.json.gz'
        path.write_bytes(gzip.compress(json.dumps(c).encode(), mtime=0))
        r6 = J6.anneal(dict(path=str(path), word_id=f'toy{k}', seed=5, deadline=time.time() + 2, out_dir=str(tmp),
                            cycle_s=0.5))
        r7 = J7.anneal(dict(path=str(path), word_id=f'toy{k}', seed=5, deadline=time.time() + 3, out_dir=str(tmp),
                            cycle_s=0.5))
        expect(abs(r6['phi_climbs_best'] - fixed) < 1e-6, f'toy{k}: job 6 annealer reaches the fixed-order optimum')
        expect(abs(r7['phi_climbs_best'] - reord) < 1e-6 and r7['exact_replay_checked'] and r7['positions_changed'] > 0,
               f'toy{k}: job 7 annealer reaches the reorder optimum ({r7["positions_changed"]} positions moved, '
               f'exact replay checked)')

    c = toys[189]
    # gates 0 (h4+=h3) and 2 (h2+=h3) commute; gates 1 (s0+=h2) and 2 (h2+=h3) do not (2 writes what 1 reads)
    try:
        J7.validate_order_state(c, [0, 2, 1, 3], [4], [SUBS[4]] * 5)
        expect(False, 'validate rejects a swapped non-commuting pair')
    except AssertionError as exc:
        expect('non-commuting' in str(exc), 'validate rejects a swapped non-commuting pair')
    expect(J7._replay(c, [0, 1, 2, 3], [4]) != J7._replay(c, [0, 2, 1, 3], [4]),
           'exact replay differs for the swapped non-commuting pair')
    expect(J7._replay(c, [0, 1, 2, 3], [4]) == J7._replay(c, [1, 0, 2, 3], [4]),
           'exact replay agrees after swapping the commuting gates 0 and 1')

    real = None
    if '--real-word' in sys.argv:
        real = sys.argv[sys.argv.index('--real-word') + 1]
    else:
        root = Path(os.environ.get('RAD_WORK_ROOT', '/nonexistent'))
        for pat in ('runs/*-job6/out/pr-527-*/base112/split-centres/CANONICAL-WORD.json.gz',
                    'runs/*-job5/out/pr-502-*/gauge80-kernel42/split-centres/CANONICAL-WORD.json.gz'):
            cand = sorted(root.glob(pat))
            if cand:
                real = str(cand[0])
                break
    c = J6.load_word(real)[0] if real else toys[189]
    w = J7.OrderedWord(c)
    rng = random.Random(11)
    any_valid = lambda d: d < J6.INF  # noqa: E731
    gate_moves = frame_moves = 0
    for _ in range(400000):
        if rng.random() < 0.6:
            m, _d = w.gate_move(rng, any_valid)
            gate_moves += m
        else:
            m, _d = w.frame_move(rng, any_valid)
            frame_moves += m
        if gate_moves + frame_moves >= 3000:
            break
    oa, ob = w.order()
    fb = [J6.canonical_basis(J6.basis_of(m)) for m in w.frame]
    t0 = time.time()
    try:
        prof = J7.validate_order_state(c, oa, ob, fb, replay=True)
        moved = sum(a != b for a, b in zip(oa + ob, w.order0[0] + w.order0[1]))
        expect(abs(J6.phi_of(prof) - w.total()) < 1e-6 and gate_moves >= 1000 and moved > 0,
               f'{"real " + Path(real).parents[2].name if real else "toy189"}: {gate_moves} gate and {frame_moves} '
               f'frame moves ({moved} positions changed) pass validation with the exact replay '
               f'({time.time() - t0:.1f} s); incremental Phi == from-scratch Phi')
    except AssertionError as exc:
        expect(False, f'random moves on the real word stay valid ({exc!r})')

    out = tmp / 'cli'
    subprocess.run([sys.executable, '-B', str(HERE / 'job7_reorder_search.py'), '--out', str(out),
                    '--word', str(tmp / 'toy189.json.gz'), '--word', str(tmp / 'toy359.json.gz'),
                    '--hours', str(6 / 3600), '--workers', '2', '--cycle-min', '0.02'], check=True, capture_output=True)
    s = json.loads((out / 'SUMMARY.json').read_text())
    got = sorted(round(b['phi_climbs_best'], 6) for b in s['best'].values())
    expect(s['supported'] == 2 and got == sorted(round(v, 6) for v in opt.values())
           and all(b['exact_replay_checked'] for b in s['best'].values()), f'command line: best Phi {got}')
    print(f'\n{len(failures)} failure(s)')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
