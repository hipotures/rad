#!/usr/bin/env python3
"""Exact screen of root/lattice line systems for the #370 five-stage bit-word template.

Template facts used (PR #370, research/e8-bit/code/bit/producer/{price,compile}.py):
- V lines in Q^h with an integral positive-definite form; target t is delivered at the
  hyperplane frame HYP[t] = span of the lines orthogonal to t (dimension h-1);
- y_t must end as x_t. Its need part carries HYP[t]; retained totals ("centres", at the
  full frame) supply the correction mask HYP[t] xor {t}. The number of centres is
  n_cent = rank over F_2 of the masks {HYP[t] xor e_t};
- five-stage price: H = 5*(chain steps + n_cent at rank h) + 2V*(2h-2, h-1, 2h+2, 4),
  W = 4V + R, m = 5h, and the saving s solves sum n (r/m)^(1-s) = W.

Then deficit = W*m - mass = 4V - 5*n_cent*h, independent of R. Adding a helper or
splitting a step lowers s, so single-step chains with R = 0 give an upper bound
s_ub on every word of this template for that line system. The script also reports
the largest helper ratio R/V at which the single-step bound still reaches the E8
reference c = 904072820242522/10^18 (PR #370).

Validation: the script recomputes the actual #370 R865 word's price with the same
price function when --e8-producer points at PR #370's producer directory.
"""
import argparse
import itertools
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

E8_REF_C = 904072820242522 / 10 ** 18


# ---------------------------------------------------------------- line systems

def canon_lines(vecs):
    seen, lines = set(), []
    for v in vecs:
        v = tuple(int(a) for a in v)
        if v in seen:
            continue
        n = tuple(-a for a in v)
        seen.add(v)
        seen.add(n)
        lines.append(v if [a for a in v if a][0] > 0 else n)
    return np.array(lines, dtype=np.int64)


def e8_shell(norm):
    """E8 vectors of norm `norm` in doubled coordinates (D8 u D8+1/2 construction)."""
    target = 4 * norm
    out = []
    r = int(math.isqrt(target)) + 1
    for parity in (0, 1):
        vals = [x for x in range(-r, r + 1) if x % 2 == parity]

        def rec(prefix, ss):
            if ss > target:
                return
            if len(prefix) == 8:
                if ss == target and (sum(prefix) // 2) % 2 == 0:
                    out.append(tuple(prefix))
                return
            for x in vals:
                rec(prefix + [x], ss + x * x)
        rec([], 0)
    return out


def d_n(n):
    out = []
    for i, j in itertools.combinations(range(n), 2):
        for a in (1, -1):
            for b in (1, -1):
                x = [0] * n
                x[i], x[j] = a, b
                out.append(tuple(x))
    return out


def a_n(n):
    out = []
    for i in range(n + 1):
        for j in range(n + 1):
            if i != j:
                x = [0] * (n + 1)
                x[i], x[j] = 1, -1
                out.append(tuple(x))
    return out


def golay_code():
    q = {(i * i) % 23 for i in range(1, 23)}
    g = [1 if (i in q or i == 0) else 0 for i in range(23)]
    gens = [[g[(i - k) % 23] for i in range(23)] for k in range(23)]
    gens = [w + [sum(w) % 2] for w in gens] + [[1] * 24]
    m = np.array(gens, dtype=np.uint8)
    r = 0
    for c in range(24):
        piv = [i for i in range(r, len(m)) if m[i, c]]
        if not piv:
            continue
        m[[r, piv[0]]] = m[[piv[0], r]]
        for i in range(len(m)):
            if i != r and m[i, c]:
                m[i] ^= m[r]
        r += 1
    basis = m[:r]
    assert r == 12
    words = (np.array(list(itertools.product((0, 1), repeat=12)), dtype=np.int64) @ basis) % 2
    assert sorted(set(words.sum(1).tolist())) == [0, 8, 12, 16, 24]
    return words


def leech_min():
    code = golay_code()
    out = []
    for i, j in itertools.combinations(range(24), 2):
        for a in (4, -4):
            for b in (4, -4):
                x = [0] * 24
                x[i], x[j] = a, b
                out.append(tuple(x))
    for w in code:
        if w.sum() != 8:
            continue
        idx = np.nonzero(w)[0]
        for sg in itertools.product((1, -1), repeat=8):
            if sg.count(-1) % 2:
                continue
            x = [0] * 24
            for i, s in zip(idx, sg):
                x[i] = 2 * s
            out.append(tuple(x))
    for w in code:
        for i in range(24):
            x = [1] * 24
            x[i] = -3
            out.append(tuple(-a if w[j] else a for j, a in enumerate(x)))
    assert len(out) == 196560
    return out


def bw16_min():
    g = [[1] * 16] + [[(i >> k) & 1 for i in range(16)] for k in range(4)]
    code = {tuple(sum(c[k] * g[k][i] for k in range(5)) % 2 for i in range(16))
            for c in itertools.product((0, 1), repeat=5)}
    out = []
    for i, j in itertools.combinations(range(16), 2):
        for a in (2, -2):
            for b in (2, -2):
                x = [0] * 16
                x[i], x[j] = a, b
                out.append(tuple(x))
    for w in code:
        if sum(w) != 8:
            continue
        idx = [i for i in range(16) if w[i]]
        for sg in itertools.product((1, -1), repeat=8):
            if sg.count(-1) % 2:
                continue
            x = [0] * 16
            for i, s in zip(idx, sg):
                x[i] = s
            out.append(tuple(x))
    assert len(out) == 4320
    return out


def systems(include_leech):
    e8 = canon_lines(e8_shell(2))
    a = e8[0]
    e7 = e8[(e8 @ a) == 0]
    b = next(r for r in e8 if abs(int(r @ a)) == 4)
    e6 = e8[((e8 @ a) == 0) & ((e8 @ b) == 0)]
    out = [('E8 roots', e8, 'transitive'), ('E7 roots', e7, 'transitive'), ('E6 roots', e6, 'transitive')]
    out += [(f'D{n} roots', canon_lines(d_n(n)), 'transitive') for n in (4, 5, 6, 8, 10, 12, 16, 20, 24)]
    out += [(f'A{n} roots', canon_lines(a_n(n)), 'transitive') for n in (4, 6, 8, 10, 12)]
    out += [('E8 norm-4 shell', canon_lines(e8_shell(4)), 'transitive'),
            ('E8 norm-6 shell', canon_lines(e8_shell(6)), 'all'),
            ('E8 norm-2+4 shells', np.vstack([e8, canon_lines(e8_shell(4))]), 'all'),
            ('BW16 minimal', canon_lines(bw16_min()), 'transitive')]
    if include_leech:
        out.append(('Leech minimal', canon_lines(leech_min()), 'transitive'))
    return out


# ---------------------------------------------------------------- F_2 rank

def pack_rows(mask):
    packed = np.packbits(mask.astype(np.uint8), axis=1, bitorder='little')
    pad = (-packed.shape[1]) % 8
    if pad:
        packed = np.hstack([packed, np.zeros((packed.shape[0], pad), np.uint8)])
    return packed.view(np.uint64).copy()


def f2_rref(packed, ncols):
    """Reduced row echelon form of packed rows; returns (basis rows, pivot columns)."""
    m = packed.copy()
    r, pivots = 0, []
    for c in range(ncols):
        wi, bi = divmod(c, 64)
        bit = np.uint64(1) << np.uint64(bi)
        if r == len(m):
            break
        cand = np.nonzero((m[r:, wi] & bit) != 0)[0]
        if len(cand) == 0:
            continue
        p = cand[0] + r
        if p != r:
            m[[r, p]] = m[[p, r]]
        rows = np.nonzero((m[:, wi] & bit) != 0)[0]
        rows = rows[rows != r]
        m[rows] ^= m[r]
        pivots.append(c)
        r += 1
    return m[:r], pivots


def correction_rows(lines, idx):
    g = lines[idx] @ lines.T
    mask = g == 0
    mask[np.arange(len(idx)), idx] = True
    return mask


def n_cent_exact(lines, log, batch=8192, seed=20261011):
    """Exact F_2 rank of the V x V correction matrix.

    Small systems: full elimination. Large systems: rank of random rows until it
    stabilises, then an exact span check of every row against the RREF basis
    (row == row[:, pivots] @ basis over F_2, as exact float32 matmuls; all sums are
    below 2^24). Uses CUDA when free, else multithreaded BLAS on the CPU.
    """
    v = len(lines)
    if v <= 4096:
        basis, piv = f2_rref(pack_rows(correction_rows(lines, np.arange(v))), v)
        return len(piv), dict(method='full elimination')
    rng = np.random.default_rng(seed)
    chosen = rng.permutation(v)
    take = 4096
    basis, piv = f2_rref(pack_rows(correction_rows(lines, chosen[:take])), v)
    while True:
        more = chosen[take:take + 4096]
        if len(more) == 0:
            break
        b2, p2 = f2_rref(np.vstack([basis, pack_rows(correction_rows(lines, more))]), v)
        take += len(more)
        log(f'  random rows {take}: rank {len(p2)}')
        if len(p2) == len(piv):
            basis, piv = b2, p2
            break
        basis, piv = b2, p2
    r = len(piv)
    assert r < 2 ** 24
    dense = np.unpackbits(basis.view(np.uint8), axis=1, bitorder='little')[:, :v].astype(np.float32)
    device = 'cpu'
    try:
        import torch
        if torch.cuda.is_available():
            free = max((torch.cuda.mem_get_info(d)[0], d) for d in range(torch.cuda.device_count()))
            need = dense.nbytes + 3 * batch * v * 4
            if free[0] > need:
                device = f'cuda:{free[1]}'
    except Exception:
        torch = None
    log(f'  span check of all {v} rows against rank {r} on {device}, batch {batch}')
    bad = 0
    t0 = time.monotonic()
    if device.startswith('cuda'):
        bt = torch.from_numpy(dense).to(device)
        lt = torch.from_numpy(lines.astype(np.float32)).to(device)
        pv = torch.tensor(piv, device=device)
        for s in range(0, v, batch):
            idx = torch.arange(s, min(v, s + batch), device=device)
            g = lt[idx] @ lt.T
            row = (g == 0)
            row[torch.arange(len(idx), device=device), idx] = True
            rowf = row.to(torch.float32)
            recon = torch.remainder(rowf[:, pv] @ bt, 2.0)
            bad += int((recon != rowf).any(dim=1).sum())
        torch.cuda.synchronize()
    else:
        pv = np.array(piv)
        for s in range(0, v, batch):
            idx = np.arange(s, min(v, s + batch))
            rowf = correction_rows(lines, idx).astype(np.float32)
            recon = np.remainder(rowf[:, pv] @ dense, 2.0)
            bad += int((recon != rowf).any(axis=1).sum())
            if s // batch % 4 == 0:
                log(f'    {min(v, s + batch)}/{v} rows, {time.monotonic() - t0:.0f}s')
    if bad:
        raise AssertionError(f'{bad} rows outside the claimed span; rank is larger than {r}')
    return r, dict(method='random-row basis + exact span check of every row', device=device,
                   rows_sampled=take, span_check_seconds=round(time.monotonic() - t0, 1))


# ---------------------------------------------------------------- price

def saving(h_counts, w, m):
    lo, hi = 0.0, 0.5
    for _ in range(200):
        s = (lo + hi) / 2
        if sum(n * (r / m) ** (1 - s) for r, n in h_counts.items()) > w:
            hi = s
        else:
            lo = s
    return lo


def single_step_bound(v, h, nc, r_help=0):
    m = 5 * h
    hc = {}
    for r, n in ((h - 1, 10 * v), (h, 5 * (nc + r_help))):
        hc[r] = hc.get(r, 0) + n
    for r in (2 * h - 2, h - 1, 2 * h + 2, 4):
        hc[r] = hc.get(r, 0) + 2 * v
    w = 4 * v + r_help
    deficit = w * m - sum(r * n for r, n in hc.items())
    return (saving(hc, w, m) if deficit > 0 else 0.0), deficit


def breakeven_ratio(v, h, nc, ref):
    if single_step_bound(v, h, nc)[0] < ref:
        return 0.0
    lo, hi = 0, 64 * v
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if single_step_bound(v, h, nc, mid)[0] >= ref:
            lo = mid
        else:
            hi = mid
    return lo / v


# ---------------------------------------------------------------- main

def analyse(name, lines, hyp_mode, log):
    t0 = time.monotonic()
    v = len(lines)
    h = int(np.linalg.matrix_rank(lines.astype(np.float64)))
    sample = range(v) if (hyp_mode == 'all' or v <= 4000) else np.random.default_rng(1).choice(v, 64, replace=False)
    hyp_ok = True
    ips = set()
    for t in sample:
        g = lines @ lines[t]
        ips.update(np.unique(np.abs(g)).tolist())
        if np.linalg.matrix_rank(lines[g == 0].astype(np.float64)) != h - 1:
            hyp_ok = False
            break
    nc, how = n_cent_exact(lines, log)
    s_ub, deficit = single_step_bound(v, h, nc)
    row = dict(system=name, V=v, h=h, abs_inner_products=sorted(int(x) for x in ips),
               hyperplane_targets=('checked for all targets' if hyp_mode == 'all' or v <= 4000
                                   else 'checked for 64 sampled targets; automorphism group transitive on lines'),
               hyperplane_frames_ok=hyp_ok, n_cent=nc, n_cent_method=how,
               deficit=deficit, s_upper_bound_R0=s_ub,
               breakeven_helpers_per_line_vs_E8_ref=breakeven_ratio(v, h, nc, E8_REF_C) if deficit > 0 else 0.0,
               seconds=round(time.monotonic() - t0, 1))
    return row


def e8_price_check(producer_dir, log):
    code = ("import json,ast,ham2,compile2 as C2,compile as C\n"
            "Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r865.json'))}\n"
            "ham2.P.update(Pd); h=ham2.build(0,True); W=C2.compile2(h)\n"
            "bad=C.f2_check(W); assert not bad[0] and not bad[1]\n"
            "s,de,D,steps=C.evaluate(W)\n"
            "print(json.dumps(dict(R=W.nh,saving=s,deficit=de,steps=sorted(steps.items()))))\n")
    env = dict(os.environ, E8COORD='ham')
    out = subprocess.run([sys.executable, '-B', '-c', code], cwd=producer_dir, env=env,
                         capture_output=True, text=True, check=True)
    res = json.loads(out.stdout.strip().splitlines()[-1])
    steps = {int(r): n for r, n in res['steps']}
    hc = {}
    for r, n in steps.items():
        hc[r] = hc.get(r, 0) + 5 * n
    hc[8] = hc.get(8, 0) + 5 * 9
    for r in (14, 7, 18, 4):
        hc[r] = hc.get(r, 0) + 240
    ours = saving(hc, 480 + res['R'], 40)
    res.update(our_price=ours, matches_reference=abs(ours - E8_REF_C) < 1e-12,
               formula_deficit=4 * 120 - 5 * 9 * 8)
    log(f"  E8 R{res['R']}: producer saving {res['saving']:.15e}, ours {ours:.15e}, deficit {res['deficit']}")
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    ap.add_argument('--e8-producer', help='PR #370 research/e8-bit/code/bit/producer directory')
    ap.add_argument('--quick', action='store_true', help='skip the Leech lattice')
    args = ap.parse_args()
    log = lambda s: print(s, flush=True)
    t0 = time.monotonic()
    result = dict(template='PR #370 five-stage bit word', e8_reference_c=E8_REF_C, rows=[])
    if args.e8_producer:
        result['e8_price_validation'] = e8_price_check(args.e8_producer, log)
    for name, lines, mode in systems(include_leech=not args.quick):
        log(f'{name}: V={len(lines)}')
        row = analyse(name, lines, mode, log)
        log('  ' + json.dumps({k: row[k] for k in ('V', 'h', 'n_cent', 'deficit', 's_upper_bound_R0',
                                                    'breakeven_helpers_per_line_vs_E8_ref', 'hyperplane_frames_ok')}))
        result['rows'].append(row)
        with open(args.out, 'w') as handle:
            json.dump(result, handle, indent=1)
    result['seconds'] = round(time.monotonic() - t0, 1)
    with open(args.out, 'w') as handle:
        json.dump(result, handle, indent=1)
    log(f'done in {result["seconds"]}s')


if __name__ == '__main__':
    main()
