#!/usr/bin/env python3
"""Time-limited search for cheaper frame timings of split-centre complex words (job 6).

A local word (CANONICAL-WORD.json.gz of the #433/#484 gauge-kernel lineage) is a fixed sequence of scalar gates.
Every gate of phases A and B carries a frame (a subspace of F_2^9); before a gate its registers climb to that frame,
and each climb from frame a to frame b >= a is a paid recursive child of rank dim b - dim a. This search keeps every
gate, coefficient, register, start frame, final frame, target level, centre frame and cut unchanged and only
re-chooses the frames of A/B gates. A timing is admissible when, for every register, the frames it meets form a
chain under inclusion: start <= gate frames ... <= final, and the frame in force when the centres phase begins equals
that register's centre or target level exactly (the upstream emitter asserts equality there and emits no climb).

The objective is the first-order recursive cost Phi = sum over paid climbs of r*ln(73/r). Rank mass is unchanged by
construction, so a lower Phi raises the complex saving b (to first order b = deficit / Phi_total). Centre steps are
unchanged and are reported but not optimized.

Search: simulated annealing with cyclic reheating. A move raises a register's frame plateau (from its first slot
on) or lowers it (up to its last slot) to the neighbouring plateau's frame or to a random intermediate subspace;
every changed gate frame cascades to the gate's other register (raises forward, lowers backward) until inclusion
holds again. A move that would change a fixed slot is rejected. Each worker keeps its best timing and writes a
checkpoint (best so far, moves tried) every two minutes and at the end; the driver prints a per-word progress
table from these checkpoints every --progress-min minutes; every reported state is re-validated from scratch
(validate_state) independently of the annealer's incremental bookkeeping.

usage: job6_retime_search.py --out DIR (--run RUN ... | --word WORD.json.gz ...) [--hours H | --deadline-epoch S]
                             [--workers N] [--seed S]
       job6_retime_search.py --out DIR --summarize     # summary of a stopped search from its checkpoints
"""
import argparse
import gzip
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

M = 73                       # ambient rank of the complex recursion
STATES = 'annealer-states'   # per-annealer records (not 'checkpoints': the archive validator skips that name)
PH = [r * math.log(M / r) if r else 0.0 for r in range(10)]
INF = float('inf')


# ---------- subspaces of F_2^9 as 512-bit element masks ----------

def elems(basis):
    s = {0}
    for b in basis:
        s |= {x ^ b for x in s}
    m = 0
    for x in s:
        m |= 1 << x
    return m


def basis_of(m):
    b = []
    while m:
        e = (m & -m).bit_length() - 1
        m &= m - 1
        y = e
        for z in b:
            y = min(y, y ^ z)
        if y:
            b.append(y)
    return b


def canonical_basis(vs):
    """The upstream emitters' basis(): reduced row echelon form, leading bits descending."""
    b = {}
    for x in vs:
        for p in sorted(b, reverse=True):
            if x >> p & 1:
                x ^= b[p]
        if x:
            p = x.bit_length() - 1
            for q in b:
                if b[q] >> p & 1:
                    b[q] ^= x
            b[p] = x
    return [b[p] for p in sorted(b, reverse=True)]


def dim(m):
    return m.bit_count().bit_length() - 1


def is_subspace(m):
    return m & 1 and elems(basis_of(m)) == m


_SPAN = {}


def span2(a, b):
    if not (b & ~a):
        return a
    if not (a & ~b):
        return b
    k = (a, b) if a < b else (b, a)
    r = _SPAN.get(k)
    if r is None:
        if len(_SPAN) > 1_000_000:
            _SPAN.clear()
        r = elems(basis_of(a) + basis_of(b))
        _SPAN[k] = r
    return r


# ---------- word model ----------

class Word:
    """Slots per register: ('s', mask) start, ('g', gate) A/B gate, ('f', mask) fixed centre/target level,
    ('e', mask) final frame. Gate frames live in self.g (one mask per A/B gate, A first)."""

    def __init__(self, c):
        self.c = c
        v, R = c['v'], c['R']
        self.v, self.n = v, 2 * v + R
        E = [elems(F) for F in c['frames']]
        self.E = E
        lv = lambda r: c.get('target_levels', {}).get(str(r - v), 0)  # noqa: E731
        self.slots = [[('s', E[c['start'][r]])] for r in range(self.n)]
        self.g, self.regs, self.part = [], [], []

        def gate(part, e):
            regs = [e[1]] + ([e[2]] if e[0] == 'add' else [])
            gi = len(self.g)
            self.g.append(E[e[-1]])
            self.regs.append(regs)
            self.part.append(part)
            for r in regs:
                self.slots[r].append(('g', gi))
        for e in c['A']:
            gate('A', e)
        for r in range(v, 2 * v):
            self.slots[r].append(('f', E[lv(r)]))
        for k, r in enumerate(c['centers']):
            self.slots[r].append(('f', E[c['center_frames'][k]]))
        for e in c['B']:
            gate('B', e)
        for r in range(self.n):
            self.slots[r].append(('e', E[c['final'][r]]))
        self.pos = {}
        for r, sl in enumerate(self.slots):
            for i, (k, x) in enumerate(sl):
                if k == 'g':
                    self.pos[x, r] = i
        # centre steps (unchanged by the search): cf -> served target levels, descending
        self.centre_profile = Counter()
        for k, r in enumerate(c['centers']):
            cf = c['center_frames'][k]
            terms = [e for e in c['cut'] if e[2] == r]
            path = [cf] + sorted({lv(e[1]) for e in terms} - {cf}, key=lambda x: -len(c['frames'][x]))
            for a in range(1, len(path)):
                self.centre_profile[len(c['frames'][path[a - 1]]) - len(c['frames'][path[a]])] += 1
        self.g0 = list(self.g)

    def frame(self, r, i, ov=None):
        k, x = self.slots[r][i]
        if k != 'g':
            return x
        return ov.get(x, self.g[x]) if ov else self.g[x]

    def regcost(self, r, ov=None):
        """Phi of register r's climbs; INF if a fixed centre/target level would be entered by a climb."""
        t, prev = 0.0, None
        for i, (k, x) in enumerate(self.slots[r]):
            f = x if k != 'g' else (ov.get(x, self.g[x]) if ov else self.g[x])
            if prev is not None and f != prev:
                if k == 'f':
                    return INF
                t += PH[dim(f) - dim(prev)]
            prev = f
        return t

    def total(self):
        return sum(self.regcost(r) for r in range(self.n))

    def plateaus(self, r):
        out, prev = [], None
        for j in range(len(self.slots[r])):
            f = self.frame(r, j)
            if f != prev:
                out.append([j, j, f])
            else:
                out[-1][1] = j
            prev = f
        return out

    def raise_(self, r, i, F, ov, touched):
        work = [(r, i, F)]
        while work:
            r, i, F = work.pop()
            touched.add(r)
            sl = self.slots[r]
            for j in range(i, len(sl)):
                k, x = sl[j]
                cur = ov.get(x, self.g[x]) if k == 'g' else x
                nf = span2(cur, F)
                if nf == cur:
                    break
                if k != 'g':
                    return False
                ov[x] = nf
                for p in self.regs[x]:
                    if p != r:
                        work.append((p, self.pos[x, p] + 1, nf))
        return True

    def lower_(self, r, i, F, ov, touched):
        work = [(r, i, F)]
        while work:
            r, i, F = work.pop()
            touched.add(r)
            sl = self.slots[r]
            for j in range(i, -1, -1):
                k, x = sl[j]
                cur = ov.get(x, self.g[x]) if k == 'g' else x
                nf = cur & F
                if nf == cur:
                    break
                if k != 'g':
                    return False
                ov[x] = nf
                for p in self.regs[x]:
                    if p != r:
                        work.append((p, self.pos[x, p] - 1, nf))
        return True


def validate_state(c, gate_frames):
    """Independent check of a timing given as one frame basis per A/B gate (A first). Returns the climb profile
    (dict rank -> count) or raises AssertionError. Recomputes every register's frame sequence from the word."""
    v, R = c['v'], c['R']
    n = 2 * v + R
    G = c['A'] + c['B']
    assert len(gate_frames) == len(G), 'one frame per A/B gate'
    for e, fb in zip(G, gate_frames):
        assert fb == canonical_basis(fb), 'gate frame not in canonical form'
    lv = lambda r: c.get('target_levels', {}).get(str(r - v), 0)  # noqa: E731
    sub = lambda a, b: all(not x for x in [_reduce(y, b) for y in a])  # noqa: E731
    cur = [list(c['frames'][c['start'][r]]) for r in range(n)]
    prof = Counter()

    def climb(r, fb):
        if canonical_basis(fb) == canonical_basis(cur[r]):
            return
        assert sub(cur[r], fb), ('frame decreases', r)
        prof[len(canonical_basis(fb)) - len(canonical_basis(cur[r]))] += 1
        cur[r] = list(fb)
    for e, fb in zip(c['A'], gate_frames[:len(c['A'])]):
        for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
            climb(r, fb)
    for r in range(v, 2 * v):
        assert canonical_basis(cur[r]) == canonical_basis(c['frames'][lv(r)]), ('target level not met exactly', r)
    for k, r in enumerate(c['centers']):
        assert canonical_basis(cur[r]) == canonical_basis(c['frames'][c['center_frames'][k]]), ('centre frame', r)
    for e, fb in zip(c['B'], gate_frames[len(c['A']):]):
        for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
            climb(r, fb)
    for r in range(n):
        climb(r, c['frames'][c['final'][r]])
    return dict(sorted(prof.items()))


def _reduce(y, basis):
    for z in canonical_basis(basis):
        if y >> (z.bit_length() - 1) & 1:
            y ^= z
    return y


def phi_of(profile):
    return sum(n * PH[r] for r, n in profile.items())


def load_word(path):
    raw = gzip.decompress(Path(path).read_bytes())
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def supported(c):
    """The search applies to a word only if this model's replay reproduces the word's own local_profile."""
    need = ('frames', 'start', 'final', 'A', 'B', 'centers', 'center_frames', 'cut', 'v', 'R', 'local_profile')
    if not all(k in c for k in need):
        return False, 'missing keys ' + ','.join(k for k in need if k not in c)
    try:
        w = Word(c)
        prof = Counter(validate_state(c, [canonical_basis(basis_of(m)) for m in w.g]))
    except (AssertionError, KeyError, IndexError, TypeError) as exc:
        return False, f'replay failed: {exc!r}'
    prof.update(w.centre_profile)
    want = {int(k): v for k, v in c['local_profile'].items() if v}
    got = {k: v for k, v in prof.items() if v}
    return (got == want), ('ok' if got == want else f'profile mismatch: replay {got} word {want}')


# ---------- annealing worker ----------

def sub_between(lo, hi, rng):
    X = lo
    hb = basis_of(hi)
    rng.shuffle(hb)
    k = rng.randint(1, max(1, dim(hi) - dim(lo) - 1)) if dim(hi) - dim(lo) > 1 else 0
    for b in hb:
        if k == 0:
            break
        if not (X >> b & 1):
            X = span2(X, elems([b]))
            k -= 1
    return X


def anneal(task):
    path, word_id, seed, deadline, out_dir, cycle_s = (task[k] for k in
                                                       ('path', 'word_id', 'seed', 'deadline', 'out_dir', 'cycle_s'))
    heartbeat = task.get('heartbeat_s', 120)
    c, sha = load_word(path)
    w = Word(c)
    rng = random.Random(seed)
    start_phi = w.total()
    cur = best = start_phi
    best_g = list(w.g)
    it = acc = cycles = 0
    t_start = time.time()
    last_ckpt = 0.0
    ckpt = Path(out_dir) / f'{word_id}-seed{seed}.json'

    def write(final):
        prof = validate_state(c, [canonical_basis(basis_of(m)) for m in best_g])
        full = Counter(prof)
        full.update(w.centre_profile)
        rec = dict(word=str(path), word_id=word_id, word_sha256=sha, seed=seed, final=final,
                   phi_climbs_start=round(start_phi, 6), phi_climbs_best=round(phi_of(prof), 6),
                   phi_gain=round(start_phi - phi_of(prof), 6),
                   local_profile_start={str(k): v for k, v in sorted(map(lambda kv: (int(kv[0]), kv[1]),
                                                                         c['local_profile'].items()))},
                   local_profile_best={str(k): v for k, v in sorted(full.items())},
                   changed_gates=sum(a != b for a, b in zip(best_g, w.g0)),
                   iterations=it, accepted=acc, cycles=cycles, seconds=round(time.time() - t_start, 1),
                   gate_frames_best=[canonical_basis(basis_of(m)) for m in best_g] if final else None)
        tmp = ckpt.with_suffix('.tmp')
        tmp.write_text(json.dumps(rec))
        tmp.replace(ckpt)
        return rec

    while time.time() < deadline:
        cycles += 1
        if cycles > 1 and rng.random() < 0.7:  # restart the cycle from the best timing found so far
            w.g[:] = best_g
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
                if now - last_ckpt > heartbeat:  # progress record, also when nothing improved
                    write(False)
                    last_ckpt = now
            r = rng.randrange(w.n)
            pl = w.plateaus(r)
            if len(pl) < 2:
                continue
            a = rng.randrange(1, len(pl))
            ov, touched = {}, set()
            if rng.random() < 0.5:
                if pl[a - 1][0] == 0:
                    continue
                F = sub_between(pl[a - 1][2], pl[a][2], rng) if rng.random() < 0.3 else pl[a][2]
                if F == pl[a - 1][2]:
                    continue
                ok = w.raise_(r, pl[a - 1][0], F, ov, touched)
            else:
                F = sub_between(pl[a - 1][2], pl[a][2], rng) if rng.random() < 0.3 else pl[a - 1][2]
                if F == pl[a][2]:
                    continue
                ok = w.lower_(r, pl[a][1], F, ov, touched)
            if not ok or not ov:
                continue
            new = sum(w.regcost(x, ov) for x in touched)
            if new == INF:
                continue
            d = new - sum(w.regcost(x) for x in touched)
            if d < 0 or rng.random() < math.exp(-d / T):
                for g, f in ov.items():
                    w.g[g] = f
                cur += d
                acc += 1
                if cur < best - 1e-9:
                    cur = w.total()  # resynchronise before recording a new best
                    if cur < best - 1e-9:
                        best, best_g = cur, list(w.g)
    return write(True)


# ---------- driver ----------

def discover(runs, words):
    found = [Path(p) for p in words]
    for run in runs:
        found += sorted(Path(run).glob('**/out/**/CANONICAL-WORD.json.gz'))
    seen, out = {}, []
    for p in found:
        try:
            c, sha = load_word(p)
        except Exception as exc:  # unreadable file: recorded, not searched
            out.append(dict(path=str(p), status=f'unreadable: {exc!r}'))
            continue
        if sha in seen:
            seen[sha]['duplicates'].append(str(p))
            continue
        ok, why = supported(c)
        rec = dict(path=str(p), sha256=sha, status='ok' if ok else 'unsupported', detail=why, duplicates=[],
                   v=c.get('v'), gates=len(c.get('A', [])) + len(c.get('B', [])),
                   local_profile=c.get('local_profile'))
        seen[sha] = rec
        out.append(rec)
    return out


def summarize(out):
    """Per-word summary rebuilt from the annealers' checkpoints alone, for a search stopped before its deadline
    (no SUMMARY.json is written then). Written to SUMMARY-FROM-CHECKPOINTS.json; nothing else is changed."""
    words = json.loads((out / 'WORDS.json').read_text())
    states = out / STATES if (out / STATES).exists() else out / 'checkpoints'  # 'checkpoints': runs before 2026-10-12 08 UTC
    recs = [json.loads(p.read_text()) for p in sorted(states.glob('*.json'))]
    per = defaultdict(list)
    for r in recs:
        per[r['word_id']].append(r)
    best = {}
    for wid, rs in sorted(per.items()):
        b = min(rs, key=lambda r: r['phi_climbs_best'])
        best[wid] = dict({k: b[k] for k in ('word', 'word_sha256', 'phi_climbs_start', 'phi_climbs_best', 'phi_gain',
                                            'changed_gates', 'local_profile_start', 'local_profile_best')},
                         annealers=len(rs), iterations=sum(r['iterations'] for r in rs),
                         accepted=sum(r['accepted'] for r in rs), cycles=sum(r['cycles'] for r in rs),
                         seconds_max=max(r['seconds'] for r in rs), all_final=all(r['final'] for r in rs))
    summary = dict(source='annealer checkpoints', stopped_before_deadline=not all(r['final'] for r in recs),
                   words=len(words), supported=sum(w.get('status') == 'ok' for w in words), annealers=len(recs),
                   iterations=sum(r['iterations'] for r in recs), accepted=sum(r['accepted'] for r in recs),
                   best=best, annealer_records=[{k: r[k] for k in ('word_id', 'seed', 'final', 'phi_climbs_best', 'phi_gain',
                                                                   'iterations', 'accepted', 'cycles', 'seconds')}
                                                for r in recs])
    (out / 'SUMMARY-FROM-CHECKPOINTS.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({wid: {k: b[k] for k in ('phi_climbs_start', 'phi_climbs_best', 'phi_gain', 'annealers', 'iterations',
                                              'accepted', 'seconds_max')} for wid, b in best.items()}, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    ap.add_argument('--run', action='append', default=[], help='job run directory whose out/ trees hold built words')
    ap.add_argument('--word', action='append', default=[], help='an explicit CANONICAL-WORD.json.gz')
    ap.add_argument('--hours', type=float)
    ap.add_argument('--deadline-epoch', type=float, help='absolute end time (seconds since epoch); overrides --hours')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument('--cycle-min', type=float, default=10.0, help='length of one annealing cycle')
    ap.add_argument('--progress-min', type=float, default=10.0, help='interval of the console progress table')
    ap.add_argument('--seed', type=int, default=20261012)
    ap.add_argument('--summarize', action='store_true', help='only rebuild the summary of a stopped search from --out')
    a = ap.parse_args()
    if a.summarize:
        return summarize(Path(a.out))
    deadline = a.deadline_epoch if a.deadline_epoch else time.time() + 3600 * (a.hours if a.hours is not None else 1)
    out = Path(a.out)
    (out / STATES).mkdir(parents=True, exist_ok=True)
    words = discover(a.run, a.word)
    (out / 'WORDS.json').write_text(json.dumps(words, indent=1))
    # annealers are dealt round-robin, newest frontier words first (#527, then #523), then the rest
    rank = lambda w: (0 if '/pr-527-' in w['path'] else 1 if '/pr-523-' in w['path'] else 2, w['path'])  # noqa: E731
    ok = sorted((w for w in words if w.get('status') == 'ok'), key=rank)
    for w in words:
        print(f"{w.get('status'):<12} {w.get('detail', '')[:90]:<90} {w['path']}", flush=True)
    if not ok:
        print('no supported word found', flush=True)
        (out / 'SUMMARY.json').write_text(json.dumps(dict(words=len(words), supported=0), indent=1))
        return 1
    for i, w in enumerate(ok):
        w['word_id'] = f'w{i:02d}-{w["sha256"][:10]}'
    tasks = [dict(path=ok[k % len(ok)]['path'], word_id=ok[k % len(ok)]['word_id'], seed=a.seed + k,
                  deadline=deadline, out_dir=str(out / STATES), cycle_s=60 * a.cycle_min,
                  heartbeat_s=min(120.0, 30 * a.progress_min))
             for k in range(max(a.workers, len(ok)))]
    print(f'{len(ok)} supported word(s), {len(tasks)} annealers on {a.workers} processes, '
          f'{(deadline - time.time()) / 3600:.2f} h left', flush=True)
    label = {w['word_id']: '/'.join(w['path'].split('/out/')[-1].split('/')[:2]) for w in ok}
    seeds = Counter(t['word_id'] for t in tasks)
    t_begin = time.time()

    def progress():
        best = {}
        for p in (out / STATES).glob('*.json'):
            try:
                r = json.loads(p.read_text())
            except (OSError, ValueError):
                continue  # being replaced
            b = best.setdefault(r['word_id'], dict(start=r['phi_climbs_start'], best=r['phi_climbs_best'], it=0, n=0))
            b['best'] = min(b['best'], r['phi_climbs_best'])
            b['it'] += r['iterations']
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
                  f"({100 * g / b['start']:.3f}% of local climbs)  {b['n']}/{seeds[wid]} annealers, {b['it'] / 1e6:.0f}M moves",
                  flush=True)

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
                      f"{r['changed_gates']} gates, {r['iterations']} it)"), flush=True)
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
                                                 'changed_gates', 'local_profile_start', 'local_profile_best')}
                         for wid, r in sorted(per_word.items())})
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=1))
    print(json.dumps({wid: dict(gain=s['phi_gain'], start=s['phi_climbs_start'], best=s['phi_climbs_best'])
                      for wid, s in summary['best'].items()}, indent=1), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
