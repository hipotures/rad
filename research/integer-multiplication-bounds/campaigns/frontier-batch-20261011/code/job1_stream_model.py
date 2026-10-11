#!/usr/bin/env python3
"""Exact stream-model check of whole-residual hosting (#442) and cross-copy hosting (#448).

Model. In the upstream templates every register of a local word is bound to one
physical stream (owner family). A stream holds data indexed by its own address
space; distinct streams form a direct sum. A coordinate factor acts on the
addresses of one stream:

- bit: D_S exchanges x_i <-> y_i for i in S on the doubled address space
  F_q^m x F_q^m (data values in F_2);
- complex: C_S multiplies by i^(sum_{j in S} y_j) on binary addresses
  y in F_2^m (exact Gaussian integers).

The fixed local word uses its helper as genuinely dirty scratch:

    x += A h          (reads the helper's arbitrary prior content)
    h <- F_R h        (the helper's residual factor on its R coordinates)
    x -= A F_R^-1 h   (cancels the read; reads the same register again)
    x <- T x          (the invocation's data action)

so its endpoint is x -> T x and h -> F_R h for every prior helper value.

Programs compared on the live streams (invocation data X and the two copies
F, G of the idle pair), for every basis input of the direct sum:

- original: helper on a bank stream K; the idle child applies F_S to F and G;
- whole hosting (#442): helper bound to F with R mapped onto S' in S; the child
  keeps S minus S' on F;
- cross-copy (#448): pieces S1' on F and S2' on G, remainder children S minus
  S1' on F and S minus S2' on G. A single-register program must bind the helper
  to one stream; every binding and every coordinate placement is enumerated;
- two-register control: a different local word with one helper per piece.
  It realises the intended operator, but it has one more helper register per
  split residual than the word that was priced.

Writes one JSON result; exits non-zero only on an internal inconsistency
(e.g. whole hosting failing, which would mean the model itself is wrong).
"""
import argparse
import itertools
import json
import sys
import time

import numpy as np


# ----------------------------------------------------------------------------
# Bit side: data over F_2, addresses (x, y) in F_q^m x F_q^m.

def bit_perm(q, m, coords):
    """Index permutation of D_S on the q^(2m) addresses (an involution)."""
    n = q ** (2 * m)
    digits = np.array(list(itertools.product(range(q), repeat=2 * m)), dtype=np.int64)
    swapped = digits.copy()
    for i in coords:
        swapped[:, i], swapped[:, m + i] = digits[:, m + i], digits[:, i]
    weights = q ** np.arange(2 * m - 1, -1, -1, dtype=np.int64)
    perm = swapped @ weights
    assert sorted(perm.tolist()) == list(range(n))
    assert np.array_equal(perm[perm], np.arange(n))
    return perm


class BitState:
    """Column-stacked images of all basis vectors of the direct sum of streams."""

    def __init__(self, q, m, names):
        self.q, self.m, self.n = q, m, q ** (2 * m)
        self.names = list(names)
        total = self.n * len(self.names)
        eye = np.eye(total, dtype=np.uint8)
        self.data = {s: eye[k * self.n:(k + 1) * self.n].copy() for k, s in enumerate(self.names)}
        self.cache = {}

    def P(self, coords):
        key = tuple(sorted(coords))
        if key not in self.cache:
            self.cache[key] = bit_perm(self.q, self.m, key)
        return self.cache[key]

    def apply(self, stream, coords):
        self.data[stream] = self.data[stream][self.P(coords)]

    def add(self, dst, src, coords_a):
        self.data[dst] ^= self.data[src][self.P(coords_a)]


def bit_invocation(st, x, h, residual, a_coords, t_coords):
    st.add(x, h, a_coords)                   # x += A h  (dirty read)
    st.apply(h, residual)                    # h <- D_R h
    pa, pr = st.P(a_coords), st.P(residual)
    st.data[x] ^= st.data[h][pr][pa]         # x -= A D_R^-1 h  (D_R is an involution; F_2)
    st.apply(x, t_coords)                    # x <- T x


# ----------------------------------------------------------------------------
# Complex side: exact Gaussian integers, binary addresses y in F_2^m.

class CplxState:
    def __init__(self, m, names):
        self.m, self.n = m, 2 ** m
        self.names = list(names)
        total = self.n * len(self.names)
        self.re = {}
        self.im = {}
        eye = np.eye(total, dtype=np.int64)
        for k, s in enumerate(self.names):
            self.re[s] = eye[k * self.n:(k + 1) * self.n].copy()
            self.im[s] = np.zeros_like(self.re[s])

    def phase(self, coords, sign=1):
        """Exponent of i per address: sign * sum_{j in coords} y_j (mod 4)."""
        y = np.arange(self.n)
        e = np.zeros(self.n, dtype=np.int64)
        for j in coords:
            e += (y >> j) & 1
        return (sign * e) % 4

    @staticmethod
    def mul_phase(re, im, e):
        out_re, out_im = re.copy(), im.copy()
        for k, (cr, ci) in enumerate(((1, 0), (0, 1), (-1, 0), (0, -1))):
            rows = e == k
            out_re[rows] = cr * re[rows] - ci * im[rows]
            out_im[rows] = cr * im[rows] + ci * re[rows]
        return out_re, out_im

    def apply(self, s, coords, sign=1):
        self.re[s], self.im[s] = self.mul_phase(self.re[s], self.im[s], self.phase(coords, sign))

    def add(self, dst, src, coords_a, sign=1, pre=None):
        re, im = self.re[src], self.im[src]
        if pre is not None:
            re, im = self.mul_phase(re, im, self.phase(pre, -1))
        re, im = self.mul_phase(re, im, self.phase(coords_a))
        self.re[dst] = self.re[dst] + sign * re
        self.im[dst] = self.im[dst] + sign * im


def cplx_invocation(st, x, h, residual, a_coords, t_coords):
    st.add(x, h, a_coords, +1)                       # x += A h
    st.apply(h, residual)                            # h <- C_R h
    st.add(x, h, a_coords, -1, pre=residual)         # x -= A C_R^-1 h
    st.apply(x, t_coords)                            # x <- T x


# ----------------------------------------------------------------------------

def run_case(side, q, m, r, w, w1):
    """One configuration. r: child rank on each copy; w: residual width; w1: piece on F."""
    w2 = w - w1
    S = list(range(r))                      # child's pending coordinates on F and on G
    A = [m - 1]                             # dirty-read address factor on the helper side
    T = [0]                                 # the invocation's own data action
    names = ['X', 'K', 'F', 'G']
    live = ['X', 'F', 'G']
    if side == 'bit':
        new = lambda: BitState(q, m, names)
        inv = bit_invocation

        def snapshot(st):
            return {s: st.data[s].copy() for s in live}

        def equal(a, b):
            return all(np.array_equal(a[s], b[s]) for s in live)
    else:
        new = lambda: CplxState(m, names)
        inv = cplx_invocation

        def snapshot(st):
            return {s: (st.re[s].copy(), st.im[s].copy()) for s in live}

        def equal(a, b):
            return all(np.array_equal(a[s][0], b[s][0]) and np.array_equal(a[s][1], b[s][1]) for s in live)

    # Original: helper on bank K at slot coordinates [0, w); idle child S on F and G.
    st = new()
    inv(st, 'X', 'K', list(range(w)), A, T)
    st.apply('F', S)
    st.apply('G', S)
    original = snapshot(st)

    result = dict(side=side, q=q if side == 'bit' else 2, m=m, child_rank=r, residual_width=w, pieces=[w1, w2])

    # Whole hosting (#442), only when the residual fits one copy.
    if w <= r:
        st = new()
        inv(st, 'X', 'F', S[:w], A, T)
        st.apply('F', S[w:])
        st.apply('G', S)
        result['whole_hosting_equals_original'] = equal(snapshot(st), original)

    # Cross-copy (#448) as a program of the fixed word: helper bound to one stream.
    if w1 > 0 and w2 > 0:
        tried = matched = 0
        witness = None
        for bound in ('F', 'G'):
            for placement in itertools.combinations(range(m), w):
                st = new()
                inv(st, 'X', bound, list(placement), A, T)
                st.apply('F', S[w1:])        # remainder children as #448 specifies
                st.apply('G', S[w2:])
                tried += 1
                if equal(snapshot(st), original):
                    matched += 1
                elif witness is None:
                    witness = dict(bound_stream=bound, placement=list(placement))
        result['cross_copy_single_register'] = dict(
            programs_tried=tried, programs_equal_to_original=matched, first_failing=witness)

        # Control: a different word with two helper registers, one per piece.
        st = new()
        inv(st, 'X', 'F', S[:w1], A, T)      # helper 1 on F, residual S1'
        inv(st, 'X', 'G', S[:w2], A, [])     # helper 2 on G, residual S2' (no second data action)
        st.apply('F', S[w1:])
        st.apply('G', S[w2:])
        result['two_register_word_equals_original'] = equal(snapshot(st), original)
        result['two_register_word_extra_helpers'] = 1
    return result


CASES_BIT = [  # (q, m, r, w, w1): includes #448's toy cases and w > r
    (3, 2, 2, 2, 1), (3, 3, 2, 2, 1), (3, 3, 3, 2, 1), (3, 3, 2, 3, 2), (3, 3, 3, 3, 1),
    (5, 2, 2, 2, 1), (3, 4, 3, 3, 2), (3, 4, 2, 3, 1), (3, 4, 4, 4, 2),
]
CASES_CPLX = [  # (m, r, w, w1)
    (2, 2, 2, 1), (3, 2, 2, 1), (3, 3, 2, 1), (3, 2, 3, 2), (4, 3, 3, 2),
    (5, 4, 4, 2), (6, 4, 5, 2), (6, 5, 5, 3), (8, 4, 6, 3),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', required=True)
    parser.add_argument('--quick', action='store_true', help='first two cases per side only')
    args = parser.parse_args()
    t0 = time.monotonic()
    rows = []
    bit_cases = CASES_BIT[:2] if args.quick else CASES_BIT
    cplx_cases = CASES_CPLX[:2] if args.quick else CASES_CPLX
    for q, m, r, w, w1 in bit_cases:
        rows.append(run_case('bit', q, m, r, w, w1))
        print(json.dumps(rows[-1]), flush=True)
    for m, r, w, w1 in cplx_cases:
        rows.append(run_case('complex', None, m, r, w, w1))
        print(json.dumps(rows[-1]), flush=True)

    whole_ok = all(r_.get('whole_hosting_equals_original', True) for r_ in rows)
    two_reg_ok = all(r_.get('two_register_word_equals_original', True) for r_ in rows)
    split_rows = [r_ for r_ in rows if 'cross_copy_single_register' in r_]
    split_any = sum(r_['cross_copy_single_register']['programs_equal_to_original'] for r_ in split_rows)
    status = ('MODEL_CONSISTENT' if whole_ok and two_reg_ok else 'MODEL_INCONSISTENT')
    summary = dict(
        status=status,
        whole_hosting_valid_in_all_cases=whole_ok,
        two_register_control_valid_in_all_cases=two_reg_ok,
        cross_copy_cases=len(split_rows),
        cross_copy_single_register_programs_tried=sum(r_['cross_copy_single_register']['programs_tried'] for r_ in split_rows),
        cross_copy_single_register_programs_equal=split_any,
        seconds=round(time.monotonic() - t0, 2),
        rows=rows,
    )
    with open(args.out, 'w') as handle:
        json.dump(summary, handle, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}, indent=1))
    sys.exit(0 if status == 'MODEL_CONSISTENT' else 1)


if __name__ == '__main__':
    main()
