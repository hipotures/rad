#!/usr/bin/env python3
"""Independently bind fresh source/profile replays and rational recurrence bounds.

This does not generate graphs or take a candidate's scalar claims as evidence.
It requires separately reconstructed source-only graphs, full dirty-state audits
and fresh actual rational profiles, and reconstructs the physical child list.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import comb, factorial, prod
from pathlib import Path
from datetime import datetime, timezone
import json


def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def links(value):
    if isinstance(value, dict):
        value = value['links']
    pairs = [tuple(x) for x in value]
    assert len(set(pairs)) == len(pairs)
    assert len({x for x, _ in pairs}) == len(pairs)
    assert len({y for _, y in pairs}) == len(pairs)
    return set(pairs)


def prime(n):
    # Deterministic Miller--Rabin on unsigned 64-bit integers.
    assert 2 <= n < 2**64
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x*x % n
            if x == n - 1:
                break
        else:
            return False
    return True


@lru_cache(None)
def log_bounds(x):
    x = Q(x)
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    def series(y):
        z = (y - 1)/(y + 1)
        low = 2*sum((z**(2*j+1)/(2*j+1) for j in range(50)), Q())
        return low, low + 2*z**101/(101*(1-z*z))
    lo, hi = series(x)
    l2, u2 = series(Q(2))
    return lo+k*l2, hi+k*u2


def moment_bounds(hist, m, W, saving):
    lo, hi = Q(), Q()
    for t, count in hist.items():
        l, u = log_bounds(Q(m, t))
        l, u = saving*l, saving*u
        assert 0 <= l <= u < 1
        # Different exponential truncation from the producer certificate.
        lower = sum((l**j/factorial(j) for j in range(8)), Q())
        upper = sum((u**j/factorial(j) for j in range(8)), Q())
        upper += u**8/(factorial(8)*(1-u/9))
        weight = Q(t*count, m*W)
        lo += weight*lower
        hi += weight*upper
    return lo, hi


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--axes', type=Path, required=True)
    p.add_argument('--graph-receipts', type=Path, nargs=2, required=True)
    p.add_argument('--geometry-receipts', type=Path, nargs=2, required=True)
    p.add_argument('--certificate', type=Path, required=True)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists()
    axes, cert = read(a.axes), read(a.certificate)
    assert cert['input_sha256'][str(a.axes)] == digest(a.axes)
    rows = [x['producer'] for x in axes]
    assert [r['h'] for r in rows] == [23, 25]
    N, m = prod(r['v'] for r in rows), prod(r['h'] for r in rows)
    W = 2*N + sum(N//r['v']*r['R'] for r in rows)
    L = sum(N//r['v']*r['loss'] for r in rows)
    hist, bound_axes = Counter(), []
    for axis, gp, ep in zip(axes, a.graph_receipts, a.geometry_receipts):
        r, profile = axis['producer'], axis['fixed_profile']
        g = read(gp)
        independent = g['independent']
        assert g['source_head'] == '84eb0b067741dc2690da837743fda06d133da865'
        for key in ('h', 'R', 'c', 'q', 'v', 'matched', 'loss', 'dag_sha256', 'positive_sha256', 'histogram'):
            assert r[key] == g['producer'][key], key
        fresh_dag = Path(g['producer']['dag_path'])
        assert digest(fresh_dag) == r['dag_sha256'] == independent['dag_sha256']
        assert digest(str(fresh_dag)+'.positive') == r['positive_sha256']
        assert r['R'] == r['c']+r['q']-r['matched'] == independent['roles']
        assert r['v'] == comb(r['h'], 3)
        dirty = independent['complete_dirty_basis']
        assert dirty['all_dirty_restore'] and dirty['total_basis_vectors'] == 2*r['v']+r['R']
        assert set(dirty['orientations']) == {'forward', 'reverse-complement'}
        e = read(ep)
        assert len(e['rows']) == 1
        inner_path = Path(e['rows'][0]['receipt'])
        assert digest(inner_path) == e['rows'][0]['receipt_sha256']
        inner = read(inner_path)
        assert inner['source_receipt_sha256'] == digest(gp)
        assert inner['regenerated_dag_sha256'] == r['dag_sha256']
        assert inner['regenerated_labels_sha256'] == r['positive_sha256']
        assert digest(inner['profile']) == inner['profile_sha256']
        recovered = read(inner['profile'])
        for key in ('blocks', 'rank_histogram', 'rank_sum', 'R', 'matched', 'loss', 'basis', 'primes', 'maximum_minor_bound_bits'):
            assert profile[key] == recovered['fixed_profile'][key], key
        assert links(read(g['producer']['witness_path'])) == links(recovered['selected_links'])
        assert digest(inner['compiler_receipt']) == inner['compiler_sha256']
        assert profile['different_modular_profiles'] == 0
        primes = profile['primes']
        assert len(set(primes)) == len(primes) and all(prime(x) for x in primes)
        assert prod(primes) > 2**profile['maximum_minor_bound_bits']
        h, copies = r['h'], N//r['v']
        assert sum(t*n for t, n in enumerate(profile['blocks'])) == h*r['R']+2*r['loss']
        local = Counter({t: copies*n for t, n in enumerate(profile['blocks']) if t and n})
        local[h] -= copies*h
        local[1] += copies*h
        assert local[h] >= 0
        hist += +local
        hist[h] += copies*r['R']
        hist[m-2*h] += copies*r['R']
        hist[1] += 2*N
        hist[h-2] += 2*N
        bound_axes.append(dict(h=h, R=r['R'], dag_sha256=r['dag_sha256'], positive_sha256=r['positive_sha256'],
            graph_receipt=str(gp), graph_receipt_sha256=digest(gp), geometry_receipt=str(ep),
            geometry_receipt_sha256=digest(ep), fresh_profile_sha256=inner['profile_sha256'],
            independent_dirty=dirty, minor_bound_bits=profile['maximum_minor_bound_bits'],
            prime_product_bits=prod(primes).bit_length(), upstream_clones=g['upstream_paid_clone_count'],
            additional_clones=g['new_paid_clone_count']))
    data = read(a.data)
    assert data['pairs'] == N
    null = {int(t): n for t, n in data['null_blocks'].items()}
    assert sum(t*n for t, n in null.items()) == 47*N
    hist.update({t: 2*n for t, n in null.items()})
    hist[481] += 2*N
    hist[1] += N
    assert dict(hist) == {int(t): n for t, n in cert['bit']['child_multiplicities'].items()}
    rank = sum(t*n for t, n in hist.items())
    assert rank == W*m-N+L == cert['bit']['total_rank']
    assert (W, L, N, m) == tuple(cert['bit'][k] for k in ('W', 'L', 'N', 'm'))
    saving = Q(cert['bit_moment']['saving'])
    lo, hi = moment_bounds(hist, m, W, saving)
    assert hi < 1
    nlo, _ = moment_bounds(hist, m, W, Q(cert['bit_moment']['next_grid'], cert['bit_moment']['grid']))
    assert nlo > 1
    phase = cert['phase']
    _, phi = moment_bounds({int(t): n for t, n in phase['child_multiplicities'].items()}, phase['m'], phase['W'], Q(cert['phase_moment']['saving']))
    assert phi < 1
    constraints, margins = cert['assembly']['constraints'], cert['assembly']['margins']
    assert len(constraints) == 47 and len(margins) == 7
    assert all(Q(x) > 0 for x in constraints.values()) and all(Q(x) > 0 for x in margins.values())
    def gap_floor(upper):
        scaled = (1-upper)*10**40
        q = Q(scaled.numerator//scaled.denominator, 10**40)
        assert q > 0
        return str(q)
    result = dict(utc=datetime.now(timezone.utc).isoformat(), status='PASS INDEPENDENT SOURCE/PROFILE/RECURRENCE BINDING',
        kappa=cert['kappa'], bit_saving=str(saving), W=W, total_rank=rank, axes=bound_axes,
        independent_bit_gap_lower_bound=gap_floor(hi), independent_phase_gap_lower_bound=gap_floor(phi), next_grid_independently_excluded=True,
        strict_constraints=47, positive_margins=7, certificate_sha256=digest(a.certificate),
        source_sha256=digest(__file__), scope='Finite exact binding and recurrence bounds. Source-family data compatibility and inherited analytic/physical/fixed-tape interfaces remain explicit prerequisites.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'kappa', 'bit_saving', 'W', 'total_rank')}))


if __name__ == '__main__':
    main()
