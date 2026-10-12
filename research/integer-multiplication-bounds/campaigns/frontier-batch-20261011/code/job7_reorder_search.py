#!/usr/bin/env python3
"""Time-limited search over gate order and frame timing of split-centre complex words (job 7).

Job 6 kept every gate's position and found the published frame timings of the #514/#522/#523/#527 words unbeaten.
Job 7 also moves gates. Within phase A and within phase B a gate may be moved past any gate that commutes with it:
  add(d1,s1) and add(d2,s2) commute iff d1 != s2 and d2 != s1;
  scale(e) commutes with add(d,s) iff e not in {d,s}; two scales always commute.
(For elementary matrices I + q e_d e_s^T the commutator is q1 q2 (e_d1 [s1 == d2] e_s2^T - e_d2 [s2 == d1] e_s1^T).)
Every order that keeps the relative order of each non-commuting pair has the same product, in the forward word and
in the backward (inverse-transpose) word the upstream emitter derives gate by gate, so the local linear map, every
coefficient and every register are unchanged. Gates never leave their phase; precondition, compensation, centres
and cleanup are untouched. Frame admissibility and the objective are job 6's (job6_retime_search.py): inclusion
chains per register in the new order, exact centre/target levels, Phi = sum over paid climbs of r*ln(73/r).

Search: simulated annealing with cyclic reheating. Moves: (i) job 6's plateau raise/lower with cascades, on the
current order; (ii) move one gate next to another gate of one of its registers, inside the window allowed by
commutation on all its registers, then give it the cheapest admissible frame among {its own, the tightest lower
bound, the loosest upper bound}. Orders are kept as real-valued keys per gate; each register's slot sequence is its
gates sorted by key between its fixed start, centre/target level and final slots.

Every reported state is checked from scratch (validate_order_state): permutation per phase, every non-commuting pair
in its original relative order, inclusion chains and levels in the new order, and, for final records, an exact
rational replay of phases A and B in both orders giving identical register contents.

usage: job7_reorder_search.py --out DIR (--word WORD.json.gz ... | --run RUN ...) [--hours H | --deadline-epoch S]
                              [--workers N] [--seed S] [--cycle-min M] [--progress-min M]
       job7_reorder_search.py --out DIR --summarize
"""
import argparse
import json
import math
import os
import random
import sys
import time
from bisect import bisect_left, insort
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import job6_retime_search as J6  # noqa: E402  (subspace arithmetic, word loading, format gate, centre profile)

from job6_retime_search import INF, PH, basis_of, canonical_basis, dim, elems, span2  # noqa: E402

STATES = 'annealer-states'
PHASE = {'A': (0.0, 1.0), 'B': (2.0, 3.0)}
K_START, K_FIX, K_FINAL = -1.0, 1.5, 4.0


def gate_regs(e):
    return [e[1]] + ([e[2]] if e[0] == 'add' else [])


def commute(a, b):
    if a[0] == 'scale' and b[0] == 'scale':
        return True
    if a[0] == 'scale':
        return a[1] not in gate_regs(b)
    if b[0] == 'scale':
        return b[1] not in gate_regs(a)
    return a[1] != b[2] and b[1] != a[2]


class OrderedWord:
    """Gates are 0..nA-1 (phase A, original order) and nA..nA+nB-1 (phase B). key[g] fixes the order; seq[r] is
    register r's slots sorted by key: ('s'|'f'|'e', mask) fixed entries and gate ids."""

    def __init__(self, c):
        self.c = c
        v, R = c['v'], c['R']
        self.n = 2 * v + R
        E = [elems(F) for F in c['frames']]
        self.G = list(c['A']) + list(c['B'])
        self.nA = len(c['A'])
        self.part = ['A'] * self.nA + ['B'] * len(c['B'])
        self.frame = [E[e[-1]] for e in self.G]
        self.regs = [gate_regs(e) for e in self.G]
        self.key = []
        for g in range(len(self.G)):
            lo, hi = PHASE[self.part[g]]
            k = g if g < self.nA else g - self.nA
            m = self.nA if g < self.nA else len(self.G) - self.nA
            self.key.append(lo + (hi - lo) * (k + 1) / (m + 1))
        lv = lambda r: c.get('target_levels', {}).get(str(r - v), 0)  # noqa: E731
        fixed = defaultdict(list)
        for r in range(self.n):
            fixed[r].append((K_START, ('s', E[c['start'][r]])))
            fixed[r].append((K_FINAL, ('e', E[c['final'][r]])))
        for r in range(v, 2 * v):
            fixed[r].append((K_FIX, ('f', E[lv(r)])))
        for k, r in enumerate(c['centers']):
            fixed[r].append((K_FIX, ('f', E[c['center_frames'][k]])))
        self.seq, self.keys = [], []
        for r in range(self.n):
            items = list(fixed[r])
            items += [(self.key[g], g) for g in range(len(self.G)) if r in self.regs[g]]
            items.sort(key=lambda t: t[0])
            assert len({k for k, _ in items}) == len(items), 'duplicate keys'
            self.seq.append([x for _, x in items])
            self.keys.append([k for k, _ in items])
        self.keyset = set(self.key)  # keys are globally unique: equal keys would leave the order ambiguous
        self.order0 = self.order()
        self.frame0 = list(self.frame)

    # ----- state access -----
    def order(self):
        return (sorted(range(self.nA), key=self.key.__getitem__),
                sorted(range(self.nA, len(self.G)), key=self.key.__getitem__))

    def fr(self, x, ov=None):
        if isinstance(x, int):
            return ov.get(x, self.frame[x]) if ov else self.frame[x]
        return x[1]

    def idx(self, r, g):
        i = bisect_left(self.keys[r], self.key[g])
        assert self.seq[r][i] == g
        return i

    def regcost(self, r, ov=None):
        t, prev = 0.0, None
        for x in self.seq[r]:
            f = self.fr(x, ov)
            if prev is not None and f != prev:
                if not isinstance(x, int) and x[0] == 'f':
                    return INF
                t += PH[dim(f) - dim(prev)]
            prev = f
        return t

    def total(self):
        return sum(self.regcost(r) for r in range(self.n))

    def plateaus(self, r):
        out, prev = [], None
        for j, x in enumerate(self.seq[r]):
            f = self.fr(x)
            if f != prev:
                out.append([j, j, f])
            else:
                out[-1][1] = j
            prev = f
        return out

    # ----- job 6 moves on the current order -----
    def raise_(self, r, i, F, ov, touched):
        work = [(r, i, F)]
        while work:
            r, i, F = work.pop()
            touched.add(r)
            sl = self.seq[r]
            for j in range(i, len(sl)):
                x = sl[j]
                cur = self.fr(x, ov)
                nf = span2(cur, F)
                if nf == cur:
                    break
                if not isinstance(x, int):
                    return False
                ov[x] = nf
                for p in self.regs[x]:
                    if p != r:
                        work.append((p, self.idx(p, x) + 1, nf))
        return True

    def lower_(self, r, i, F, ov, touched):
        work = [(r, i, F)]
        while work:
            r, i, F = work.pop()
            touched.add(r)
            sl = self.seq[r]
            for j in range(i, -1, -1):
                x = sl[j]
                cur = self.fr(x, ov)
                nf = cur & F
                if nf == cur:
                    break
                if not isinstance(x, int):
                    return False
                ov[x] = nf
                for p in self.regs[x]:
                    if p != r:
                        work.append((p, self.idx(p, x) - 1, nf))
        return True

    # ----- gate moves -----
    def window(self, g):
        """(lo, hi) open key interval in which g may sit, and per register the gates it may be placed next to."""
        lo, hi = PHASE[self.part[g]]
        near = []
        for r in self.regs[g]:
            sl, ks = self.seq[r], self.keys[r]
            i = self.idx(r, g)
            a = i - 1
            while a >= 0 and isinstance(sl[a], int) and commute(self.G[g], self.G[sl[a]]):
                near.append((r, sl[a]))
                a -= 1
            if a >= 0:
                lo = max(lo, ks[a])
            b = i + 1
            while b < len(sl) and isinstance(sl[b], int) and commute(self.G[g], self.G[sl[b]]):
                near.append((r, sl[b]))
                b += 1
            if b < len(sl):
                hi = min(hi, ks[b])
        return lo, hi, near

    def _remove(self, g):
        for r in self.regs[g]:
            i = self.idx(r, g)
            del self.seq[r][i]
            del self.keys[r][i]

    def _insert(self, g):
        for r in self.regs[g]:
            i = bisect_left(self.keys[r], self.key[g])
            self.keys[r].insert(i, self.key[g])
            self.seq[r].insert(i, g)

    def set_key(self, g, k):
        assert k not in self.keyset or k == self.key[g], 'key collision'
        self._remove(g)
        self.keyset.discard(self.key[g])
        self.key[g] = k
        self.keyset.add(k)
        self._insert(g)

    def renormalise(self, part):
        lo, hi = PHASE[part]
        gs = sorted((g for g in range(len(self.G)) if self.part[g] == part), key=self.key.__getitem__)
        for j, g in enumerate(gs):
            self.keyset.discard(self.key[g])
            self.key[g] = lo + (hi - lo) * (j + 1) / (len(gs) + 1)
            self.keyset.add(self.key[g])
        for r in range(self.n):
            self.keys[r] = [self.key[x] if isinstance(x, int) else self.keys[r][j] for j, x in enumerate(self.seq[r])]

    def frame_interval(self, g):
        """Tightest lower and loosest upper frame for g at its current position, from its registers' neighbours."""
        L, U = 1, None  # element masks: {0} and 'everything'
        for r in self.regs[g]:
            i = self.idx(r, g)
            L = span2(L, self.fr(self.seq[r][i - 1]))
            nx = self.fr(self.seq[r][i + 1])
            U = nx if U is None else U & nx
        return L, U


    # ----- annealing moves; accept(d) decides on a finite cost change d; return (moved, d) -----
    def gate_move(self, rng, accept):
        """Move one random gate next to a commuting neighbour on one of its registers and give it the cheapest
        admissible frame among {its own, tightest lower bound, loosest upper bound}."""
        g = rng.randrange(len(self.G))
        lo, hi, near = self.window(g)
        if not near:
            return False, 0.0
        r, h = near[rng.randrange(len(near))]
        j = self.idx(r, h)
        nb = j + 1 if rng.random() < 0.5 else j - 1
        if self.seq[r][nb] == g:  # already adjacent on that side
            return False, 0.0
        k_other = self.keys[r][nb]  # h is a gate, so both neighbours exist (fixed start/final slots)
        k = self.keys[r][j] + (k_other - self.keys[r][j]) * rng.uniform(0.25, 0.75)
        if not (lo < k < hi) or k in self.keyset or k == k_other:
            if abs(k_other - self.keys[r][j]) < 1e-9:
                self.renormalise(self.part[g])
            return False, 0.0
        old_key, old_frame = self.key[g], self.frame[g]
        before = sum(self.regcost(x) for x in self.regs[g])
        self.set_key(g, k)
        L, U = self.frame_interval(g)
        best = None
        if not (L & ~U):
            cands = {L, U} | ({old_frame} if not (L & ~old_frame) and not (old_frame & ~U) else set())
            for F in cands:
                self.frame[g] = F
                cc = sum(self.regcost(x) for x in self.regs[g])
                if best is None or cc < best[0]:
                    best = (cc, F)
        if best is not None and best[0] < INF and accept(best[0] - before):
            self.frame[g] = best[1]
            return True, best[0] - before
        self.frame[g] = old_frame
        self.set_key(g, old_key)
        return False, 0.0

    def frame_move(self, rng, accept):
        """Job 6's move on the current order: raise or lower one plateau of a random register, with cascades."""
        r = rng.randrange(self.n)
        pl = self.plateaus(r)
        if len(pl) < 2:
            return False, 0.0
        a = rng.randrange(1, len(pl))
        ov, touched = {}, set()
        if rng.random() < 0.5:
            if pl[a - 1][0] == 0:
                return False, 0.0
            F = J6.sub_between(pl[a - 1][2], pl[a][2], rng) if rng.random() < 0.3 else pl[a][2]
            if F == pl[a - 1][2]:
                return False, 0.0
            ok = self.raise_(r, pl[a - 1][0], F, ov, touched)
        else:
            F = J6.sub_between(pl[a - 1][2], pl[a][2], rng) if rng.random() < 0.3 else pl[a - 1][2]
            if F == pl[a][2]:
                return False, 0.0
            ok = self.lower_(r, pl[a][1], F, ov, touched)
        if not ok or not ov:
            return False, 0.0
        new = sum(self.regcost(x, ov) for x in touched)
        if new == INF:
            return False, 0.0
        d = new - sum(self.regcost(x) for x in touched)
        if not accept(d):
            return False, 0.0
        for gg, f in ov.items():
            self.frame[gg] = f
        return True, d


def validate_order_state(c, order_a, order_b, frames, replay=False):
    """From scratch: order_a/order_b are permutations of the original gate indices of A and B; frames[g] is the
    canonical frame basis of original gate g (A first). Returns the climb profile; raises AssertionError."""
    A, B = c['A'], c['B']
    nA = len(A)
    G = list(A) + list(B)
    assert sorted(order_a) == list(range(nA)) and sorted(order_b) == list(range(nA, nA + len(B))), 'not a permutation'
    pos = {g: k for k, g in enumerate(list(order_a) + list(order_b))}
    by = defaultdict(list)
    for g, e in enumerate(G):
        for r in gate_regs(e):
            by[r].append(g)
    for r, gs in by.items():
        for i in range(len(gs)):
            for j in range(i + 1, len(gs)):
                a, b = gs[i], gs[j]
                if (a < nA) == (b < nA) and not commute(G[a], G[b]):
                    assert pos[a] < pos[b], ('non-commuting pair reordered', a, b)
    new = dict(c, A=[G[g] for g in order_a], B=[G[g] for g in order_b])  # validate_state reads registers, not e[-1]
    prof = J6.validate_state(new, [frames[g] for g in list(order_a) + list(order_b)])
    if replay:
        assert _replay(c, list(range(nA)), list(range(nA, nA + len(B)))) == _replay(c, order_a, order_b), \
            'reordered phases A and B give different register contents'
    return prof


def _replay(c, order_a, order_b):
    """Exact rational contents of every register after phases A and B, from the identity (columns as dicts)."""
    G = list(c['A']) + list(c['B'])
    n = 2 * c['v'] + c['R']
    rows = [{r: Fraction(1)} for r in range(n)]
    for g in list(order_a) + list(order_b):
        e = G[g]
        if e[0] == 'add':
            d, s, q = e[1], e[2], Fraction(e[3], e[4]) if e[4] else Fraction(e[3])
            row = rows[d]
            for j, x in rows[s].items():
                z = row.get(j, 0) + q * x
                if z:
                    row[j] = z
                else:
                    row.pop(j, None)
        else:
            q = Fraction(e[2], e[3]) if e[3] else Fraction(e[2])
            rows[e[1]] = {j: q * x for j, x in rows[e[1]].items()}
    return rows


# ---------- annealing worker ----------

def anneal(task):
    path, word_id, seed, deadline, out_dir, cycle_s = (task[k] for k in
                                                       ('path', 'word_id', 'seed', 'deadline', 'out_dir', 'cycle_s'))
    heartbeat = task.get('heartbeat_s', 120)
    p_gate = task.get('p_gate', 0.6)
    c, sha = J6.load_word(path)
    w = OrderedWord(c)
    centre = J6.Word(c).centre_profile
    rng = random.Random(seed)
    start_phi = w.total()
    cur = best = start_phi
    snap = lambda: (list(w.key), list(w.frame))  # noqa: E731
    best_state = snap()
    it = acc = acc_gate = cycles = 0
    t_start = time.time()
    last_ckpt = 0.0
    ckpt = Path(out_dir) / f'{word_id}-seed{seed}.json'

    def restore(state):
        keys, frames = state
        w.key[:] = keys
        w.keyset = set(keys)
        w.frame[:] = frames
        for r in range(w.n):
            fixed = [(w.keys[r][j], x) for j, x in enumerate(w.seq[r]) if not isinstance(x, int)]
            items = fixed + [(w.key[g], g) for g in range(len(w.G)) if r in w.regs[g]]
            items.sort(key=lambda t: t[0])
            w.seq[r] = [x for _, x in items]
            w.keys[r] = [k for k, _ in items]

    def write(final):
        keys, frames = best_state
        oa = sorted(range(w.nA), key=keys.__getitem__)
        ob = sorted(range(w.nA, len(w.G)), key=keys.__getitem__)
        fb = [canonical_basis(basis_of(m)) for m in frames]
        prof = validate_order_state(c, oa, ob, fb, replay=final)
        full = Counter(prof)
        full.update(centre)
        moved = sum(a != b for a, b in zip(oa + ob, w.order0[0] + w.order0[1]))
        rec = dict(word=str(path), word_id=word_id, word_sha256=sha, seed=seed, final=final,
                   phi_climbs_start=round(start_phi, 6), phi_climbs_best=round(J6.phi_of(prof), 6),
                   phi_gain=round(start_phi - J6.phi_of(prof), 6),
                   local_profile_start={str(k): v for k, v in sorted((int(a), b) for a, b in c['local_profile'].items())},
                   local_profile_best={str(k): v for k, v in sorted(full.items())},
                   changed_frames=sum(a != b for a, b in zip(frames, w.frame0)), positions_changed=moved,
                   iterations=it, accepted=acc, accepted_gate_moves=acc_gate, cycles=cycles,
                   seconds=round(time.time() - t_start, 1), exact_replay_checked=final,
                   order_a_best=oa if final else None, order_b_best=ob if final else None,
                   gate_frames_best=fb if final else None)
        tmp = ckpt.with_suffix('.tmp')
        tmp.write_text(json.dumps(rec))
        tmp.replace(ckpt)
        return rec

    while time.time() < deadline:
        cycles += 1
        if cycles > 1 and rng.random() < 0.7:
            restore(best_state)
            cur = best
        T0 = math.exp(rng.uniform(math.log(0.2), math.log(8.0)))
        c0 = time.time()
        c_len = min(cycle_s, max(1.0, deadline - c0))
        T = T0
        while True:
            it += 1
            if it % 256 == 0:
                now = time.time()
                if now - c0 >= c_len or now >= deadline:
                    break
                T = T0 * max(0.0, 1 - (now - c0) / c_len) + 1e-4
                if now - last_ckpt > heartbeat:
                    write(False)
                    last_ckpt = now
            accept = lambda d: d < 0 or rng.random() < math.exp(-d / T)  # noqa: E731
            if rng.random() < p_gate:
                moved, d = w.gate_move(rng, accept)
                acc_gate += moved
            else:
                moved, d = w.frame_move(rng, accept)
            if not moved:
                continue
            cur += d
            acc += 1
            if cur < best - 1e-9:
                cur = w.total()  # resynchronise before recording a new best
                if cur < best - 1e-9:
                    best, best_state = cur, snap()
    return write(True)


# ---------- driver ----------

def summarize(out):
    states = out / STATES
    recs = [json.loads(p.read_text()) for p in sorted(states.glob('*.json'))]
    per = defaultdict(list)
    for r in recs:
        per[r['word_id']].append(r)
    best = {}
    for wid, rs in sorted(per.items()):
        b = min(rs, key=lambda r: r['phi_climbs_best'])
        best[wid] = dict({k: b[k] for k in ('word', 'word_sha256', 'phi_climbs_start', 'phi_climbs_best', 'phi_gain',
                                            'changed_frames', 'positions_changed', 'local_profile_start',
                                            'local_profile_best')},
                         annealers=len(rs), iterations=sum(r['iterations'] for r in rs),
                         accepted=sum(r['accepted'] for r in rs), accepted_gate_moves=sum(r['accepted_gate_moves'] for r in rs),
                         seconds_max=max(r['seconds'] for r in rs), all_final=all(r['final'] for r in rs))
    summary = dict(source='annealer records', stopped_before_deadline=not all(r['final'] for r in recs),
                   annealers=len(recs), iterations=sum(r['iterations'] for r in recs), best=best,
                   annealer_records=[{k: r[k] for k in ('word_id', 'seed', 'final', 'phi_climbs_best', 'phi_gain', 'iterations',
                                                        'accepted', 'accepted_gate_moves', 'cycles', 'seconds')} for r in recs])
    (out / 'SUMMARY-FROM-RECORDS.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({wid: {k: b[k] for k in ('phi_climbs_start', 'phi_climbs_best', 'phi_gain', 'annealers', 'iterations',
                                              'accepted_gate_moves')} for wid, b in best.items()}, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    ap.add_argument('--run', action='append', default=[], help='run directory whose out/ trees hold built words')
    ap.add_argument('--word', action='append', default=[], help='an explicit CANONICAL-WORD.json.gz')
    ap.add_argument('--hours', type=float)
    ap.add_argument('--deadline-epoch', type=float)
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--cycle-min', type=float, default=10.0)
    ap.add_argument('--progress-min', type=float, default=10.0)
    ap.add_argument('--p-gate', type=float, default=0.6, help='share of gate moves among all moves')
    ap.add_argument('--seed', type=int, default=20261013)
    ap.add_argument('--summarize', action='store_true')
    a = ap.parse_args()
    out = Path(a.out)
    if a.summarize:
        return summarize(out)
    deadline = a.deadline_epoch if a.deadline_epoch else time.time() + 3600 * (a.hours if a.hours is not None else 1)
    (out / STATES).mkdir(parents=True, exist_ok=True)
    words = J6.discover(a.run, a.word)
    (out / 'WORDS.json').write_text(json.dumps(words, indent=1))
    rank = lambda w: (0 if '/pr-527-' in w['path'] else 1 if '/pr-523-' in w['path'] else 2, w['path'])  # noqa: E731
    ok = sorted((w for w in words if w.get('status') == 'ok'), key=rank)
    for w in words:
        print(f"{w.get('status'):<12} {w.get('detail', '')[:60]:<60} {w['path']}", flush=True)
    if not ok:
        print('no supported word found', flush=True)
        return 1
    for i, w in enumerate(ok):
        w['word_id'] = f'w{i:02d}-{w["sha256"][:10]}'
    # the newest words (#527, #523) get two annealer slots per round, every other word one
    slots = [w for w in ok for _ in range(2 if rank(w)[0] < 2 else 1)]
    tasks = [dict(path=slots[k % len(slots)]['path'], word_id=slots[k % len(slots)]['word_id'], seed=a.seed + k,
                  deadline=deadline, out_dir=str(out / STATES), cycle_s=60 * a.cycle_min,
                  heartbeat_s=min(120.0, 30 * a.progress_min), p_gate=a.p_gate)
             for k in range(max(a.workers, len(ok)))]
    label = {w['word_id']: '/'.join(w['path'].split('/out/')[-1].split('/')[:2]) for w in ok}
    seeds = Counter(t['word_id'] for t in tasks)
    print(f'{len(ok)} supported word(s), {len(tasks)} annealers on {a.workers} processes, '
          f'{(deadline - time.time()) / 3600:.2f} h left', flush=True)
    t_begin = time.time()

    def progress():
        best = {}
        for p in (out / STATES).glob('*.json'):
            try:
                r = json.loads(p.read_text())
            except (OSError, ValueError):
                continue
            b = best.setdefault(r['word_id'], dict(start=r['phi_climbs_start'], best=r['phi_climbs_best'], it=0, n=0, gm=0))
            b['best'] = min(b['best'], r['phi_climbs_best'])
            b['it'] += r['iterations']
            b['gm'] += r['accepted_gate_moves']
            b['n'] += 1
        print(f"--- progress {time.strftime('%H:%M:%S')}  elapsed {(time.time() - t_begin) / 3600:.2f} h, "
              f"left {max(0, deadline - time.time()) / 3600:.2f} h", flush=True)
        for wid in sorted(label):
            b = best.get(wid)
            if b is None:
                print(f'  {wid} {label[wid]:<44} no record yet ({seeds[wid]} annealers)', flush=True)
                continue
            g = b['start'] - b['best']
            print(f"  {wid} {label[wid]:<44} Phi {b['start']:.2f} -> {b['best']:.2f}  gain {g:8.2f} "
                  f"({100 * g / b['start']:.3f}% of local climbs)  {b['n']}/{seeds[wid]} annealers, "
                  f"{b['it'] / 1e6:.0f}M moves, {b['gm'] / 1e3:.0f}k gate moves accepted", flush=True)

    results = []
    with ProcessPoolExecutor(max_workers=a.workers) as pool:
        futs = {pool.submit(anneal, t): t for t in tasks}
        pending = set(futs)
        while pending:
            done, pending = wait(pending, timeout=60 * a.progress_min, return_when=FIRST_COMPLETED)
            if not done:
                progress()
            for f in done:
                t = futs[f]
                try:
                    r = f.result()
                except Exception as exc:  # a failing annealer never stops the others
                    r = dict(word_id=t['word_id'], seed=t['seed'], error=repr(exc))
                results.append(r)
                print(f"{r['word_id']} seed {r['seed']}: " + (r['error'] if 'error' in r else
                      f"Phi {r['phi_climbs_start']:.3f} -> {r['phi_climbs_best']:.3f} (gain {r['phi_gain']:.3f}, "
                      f"{r['positions_changed']} positions, {r['changed_frames']} frames, {r['iterations']} it)"), flush=True)
    progress()
    per_word = {}
    for r in results:
        if 'error' in r:
            continue
        b = per_word.get(r['word_id'])
        if b is None or r['phi_climbs_best'] < b['phi_climbs_best']:
            per_word[r['word_id']] = r
    for wid, r in per_word.items():
        (out / f'BEST-{wid}.json').write_text(json.dumps(r))
    summary = dict(deadline_epoch=deadline, words=len(words), supported=len(ok), annealers=len(tasks),
                   errors=sum('error' in r for r in results),
                   best={wid: {k: r[k] for k in ('word', 'word_sha256', 'phi_climbs_start', 'phi_climbs_best', 'phi_gain',
                                                 'positions_changed', 'changed_frames', 'local_profile_start',
                                                 'local_profile_best', 'exact_replay_checked')}
                         for wid, r in sorted(per_word.items())})
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({wid: dict(gain=s['phi_gain'], start=s['phi_climbs_start'], best=s['phi_climbs_best'])
                      for wid, s in summary['best'].items()}, indent=1), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
