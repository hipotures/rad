#!/usr/bin/env python3
"""Construct ballot completions with only unit shears, signs and exchanges.

An elementary Bier incidence recursion replaces the costly Euclidean base
word. Whole scalar maps and literal prefix charges are checked independently
against subset incidence and the odd-weight central polynomial.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

import ballot_center_completion as exact


TOPIC = Path(__file__).resolve().parents[2]
CONFIG = TOPIC/'configs/transfers/ballot-bier-words.json'


def offset(word, amount):
    return tuple((kind, a+amount, b+amount, c) for kind, a, b, c in word)


def zeta_word(features, h, upward):
    positions = {a:i for i, a in enumerate(features)}; events = []
    for bit in range(h):
        mask = 1 << bit
        for a in features:
            if not a & mask and a | mask in positions:
                small, large = positions[a], positions[a | mask]
                target, source = (small, large) if upward else (large, small)
                events.append(('add', target, source, 1))
    return tuple(events)


def complement_word(features, h, transpose):
    signs = tuple(('negate', i, i, -1) for i, a in enumerate(features) if a.bit_count() & 1)
    zeta = zeta_word(features, h, upward=transpose)
    return zeta+signs if transpose else signs+zeta


@lru_cache(None)
def bier(h, r):
    if not 0 <= 2*r <= h:
        raise ValueError('Bier recursion requires0<=2r<=h')
    if r == 0:
        return (0,), (0,), ()
    high = 1 << (h-1)
    if h == 2*r:
        F, R, W = bier(h-1, r-1); q = len(F); low_mask = high-1
        # New coordinates receive old original feature values before any
        # basis change. The old diagonal block is the complementary slice.
        coupling = tuple(('add', q+i, i, 1) for i in range(q))
        word = coupling+complement_word(F, h-1, transpose=True)+W+offset(W, q)
        return F+tuple(a | high for a in F), tuple(low_mask ^ a for a in R)+tuple(a | high for a in R), word
    F_old, R_old, W_old = bier(h-1, r)
    F_new, R_new, W_new = bier(h-1, r-1)
    q_old = len(F_old); positions = {a:i for i, a in enumerate(F_old)}
    coupling = tuple(('add', q_old+i, positions[a], 1) for i, a in enumerate(F_new))
    return (F_old+tuple(a | high for a in F_new), R_old+tuple(a | high for a in R_new),
            coupling+W_old+offset(W_new, q_old))


def transpose_word(word):
    # If execution gives P=E_last...E_first, reversed transposed gates give
    # P^T. Signs/exchanges are symmetric; an addition transposes its ports.
    return tuple((kind, b, a, c) if kind == 'add' else (kind, a, b, c)
                 for kind, a, b, c in reversed(word))


@lru_cache(None)
def layout(h, k, r):
    if not 0 <= r <= k or h < k+r:
        raise ValueError('Require0<=r<=k and h>=k+r')
    if r == 0:
        return (0,), ((1 << k)-1,)
    if h == k+r:
        F, R, _ = bier(h, r); all_mask = (1 << h)-1
        return F, tuple(all_mask ^ a for a in R)
    F_old, P_old = layout(h-1, k, r)
    F_new, P_new = layout(h-1, k-1, r-1); high = 1 << (h-1)
    return F_old+tuple(a | high for a in F_new), P_old+tuple(a | high for a in P_new)


@lru_cache(None)
def minor_word(h, k, r):
    F, P = layout(h, k, r)
    if r == 0:
        return ()
    if h == k+r:
        F_bier, R, W = bier(h, r)
        if F_bier != F:
            raise ValueError('Base feature order differs')
        return transpose_word(W)+complement_word(F, h, transpose=False)
    F_old, P_old = layout(h-1, k, r)
    F_new, P_new = layout(h-1, k-1, r-1); q_old = len(F_old)
    cross = tuple(('add', i, q_old+j, 1) for i, a in enumerate(F_old)
                  for j, s in enumerate(P_new) if a & s == a)
    return minor_word(h-1, k, r)+cross+offset(minor_word(h-1, k-1, r-1), q_old)


def complete(h, k, r):
    F, P = layout(h, k, r); used = set(P)
    nonpivots = tuple(s for s in exact.labels(h, k) if s not in used); q = len(F)
    gather = tuple(('add', i, q+j, 1) for i, a in enumerate(F) for j, s in enumerate(nonpivots) if a & s == a)
    return F, P+nonpivots, minor_word(h, k, r)+gather


def review(case):
    h, k = case; r = (k-1)//2; q, v = comb(h, r), comb(h, k)
    F, S, word = complete(h, k, r)
    if set(F) != set(exact.standard(h, r)) or len(S) != v or len(set(S)) != v:
        raise ValueError('Incomplete recursive source/feature layout')
    if any(kind not in ['add','negate','swap'] or (kind == 'add' and abs(c) != 1)
           for kind, a, b, c in word):
        raise ValueError('A nonunit scalar gate was introduced')
    observed, forward = exact.replay_matrix(word, v)
    expected = [[int(a & s == a) for s in S] for a in F]
    expected += [[int(j == i) for j in range(v)] for i in range(q, v)]
    if observed != expected:
        raise ValueError('Unit word differs from complete ballot incidence')
    inverse_word = exact.inverse_word(word)
    inverse, reverse = exact.replay_matrix(inverse_word, v)
    for event in inverse_word:
        exact.update(observed, event)
    if observed != [[int(i == j) for j in range(v)] for i in range(v)]:
        raise ValueError('Every source/null inverse column failed')
    M, Mi = [row[:q] for row in expected[:q]], [row[:q] for row in inverse[:q]]
    if exact.matrix_product(M, Mi) != [[int(i == j) for j in range(q)] for i in range(q)] or \
            exact.matrix_product(Mi, M) != [[int(i == j) for j in range(q)] for i in range(q)]:
        raise ValueError('Two-sided pivot inverse failed')
    denominator = max(exact.central(k, t).denominator for t in range(k+1))
    values = [int(exact.central(k, t)*denominator) for t in range(k+1)]
    feature_columns = [[i for i, a in enumerate(F) if a & s == a] for s in S]
    decoder_max, entries, digest = 0, 0, sha256()
    for target in S:
        original = [values[(target & s).bit_count()] for s in S[:q]]
        decoder = [sum(original[j]*Mi[j][i] for j in range(q)) for i in range(q)]
        decoder_max = max(decoder_max, *(abs(x) for x in decoder)); digest.update(json.dumps(decoder).encode())
        for source, column in zip(S, feature_columns):
            if sum(decoder[i] for i in column) != values[(target & source).bit_count()]:
                raise ValueError('All central decoder entries failed')
            entries += 1
    base_bounds = []
    for depth in range(r+1):
        kb, rb = k-depth, r-depth; hb = kb+rb
        base_word = minor_word(hb, kb, rb)
        _, bound = exact.replay_matrix(base_word, comb(hb, rb))
        base_bounds.append(bound['row_l1_prefix'])
    forward_bound = max(v, *base_bounds)
    if forward['row_l1_prefix'] > forward_bound:
        raise ValueError('Raw-new-pivot forward bound failed')
    # Negative controls bind timing and transpose: remove one actual gather
    # edge, and use the untransposed Bier word in the complementary base.
    reduced = list(word)
    omitted = next(i for i, event in enumerate(reduced) if event[0] == 'add')
    del reduced[omitted]
    if exact.replay_matrix(reduced, v)[0] == expected:
        raise ValueError('Omitted actual scalar edge was accepted')
    FB, RB, WB = bier(k+r, r)
    wrong = WB+complement_word(FB, k+r, transpose=False)
    wanted_base = [[int(a & (((1 << (k+r))-1)^s) == a) for s in RB] for a in FB]
    if exact.replay_matrix(wrong, len(FB))[0] == wanted_base:
        raise ValueError('Missing transpose control was not discriminating')
    return dict(h=h,k=k,r=r,v=v,q=q,full_basis_columns_and_inverses=v,full_central_entries=entries,
        complete_unit_word_gates=len(word),additions=sum(e[0]=='add' for e in word),
        exchanges=sum(e[0]=='swap' for e in word),negations=sum(e[0]=='negate' for e in word),
        common_decoder_denominator=denominator,decoder_maximum_numerator=decoder_max,
        decoder_sha256=digest.hexdigest(),pivot_inverse_maximum=max(abs(x) for row in Mi for x in row),
        forward_prefix=forward,inverse_prefix=reverse,all_size_forward_row_l1_bound=forward_bound,
        fixed_base_prefixes=base_bounds,negative_controls=['omitted actual scalar edge','missing Bier transpose'],
        native_frame_precision_transfer=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--small',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); config=json.loads(CONFIG.read_text())
    helper=Path(exact.__file__).resolve()
    if sha256(helper.read_bytes()).hexdigest()!=config['exact_helper_sha256']:
        raise ValueError('Pinned scalar arithmetic/baseline changed')
    paths=[Path(__file__).resolve(),helper,CONFIG]
    hashes={str(p.relative_to(TOPIC)):sha256(p.read_bytes()).hexdigest() for p in paths}
    cases=[tuple(c) for c in config['small_cases' if args.small else 'cases']]
    protocol=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
        source_config_sha256=hashes,cases=cases,seed=None,scope=config['scope'])
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    started=time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows=list(pool.map(review,cases))
    if any(sha256((TOPIC/p).read_bytes()).hexdigest()!=digest for p,digest in hashes.items()):
        raise ValueError('Source changed during attempt')
    result=dict(status='UNIT BIER WORD COMPLETION PASS',cases=rows,seconds=time.monotonic()-started,
        scope=config['scope'],uniform_all_h_inverse_prefix_proved=False,native_or_exponent_claim=False)
    if args.output:
        (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','seconds','scope']}))


if __name__=='__main__':
    main()
