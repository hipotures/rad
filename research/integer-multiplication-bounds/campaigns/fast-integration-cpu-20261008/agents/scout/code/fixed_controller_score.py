#!/usr/bin/env python3
"""Complete two-axis copied-center controller moments, with exact enclosures.

Input fixed blocks MUST be paired with their own ORIGINAL-envelope R/loss.
The arithmetic follows pinned eligible PR40's copied-both-reversed witness.
Other dimensions can only be screened with explicitly optimistic data cost;
that option does not supply their missing physical data geometry.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from math import comb
from pathlib import Path


REFERENCE_A = Q(783777693, 2*10**13)
GRID = 1 << 100


def downward(value):
    return Q((value.numerator*GRID)//value.denominator, GRID)


def upward(value):
    return Q((value.numerator*GRID+value.denominator-1)//value.denominator, GRID)


@lru_cache(None)
def logarithms(value):
    value, power = Q(value), 0
    assert value >= 1
    while value > 2:
        value /= 2
        power += 1
    def small(x):
        z = (x-1)/(x+1)
        lower = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(24)), Q(0))
        return lower, lower+2*z**49/(49*(1-z*z))
    low, high = small(value)
    two_low, two_high = small(Q(2))
    return downward(low+power*two_low), upward(high+power*two_high)


def moment(m, W, widths, saving):
    low, high = Q(0), Q(0)
    for width, count in sorted(widths.items()):
        assert 0 < width < m and count >= 0
        log_low, log_high = logarithms(Q(m, width))
        x, y = saving*log_low, saving*log_high
        assert 0 <= x <= y < 1
        weight = Q(count*width, m*W)
        low += weight*(1+x+x*x/2+x*x*x/6)
        high += weight*(1+y+y*y/(2*(1-y/3)))
    return dict(saving=str(saving), exponent=str(1-saving), lower=str(low),
                upper=str(high), strict_gap=str(1-high),
                numerator_denominator=m*W, strictly_passes=high < 1,
                strictly_fails=low >= 1)


def profile(first, second, optimistic=False):
    a, b = first["h"], second["h"]
    m, N = a*b, comb(a, 3)*comb(b, 3)
    if not optimistic:
        assert (a, b) == (23, 25), "Inherited exact data geometry is ordered23/25 only"
    parts, L, banks = {}, 0, []
    for axis, row in enumerate((first, second)):
        h, roles, loss = row["h"], row["R"], row["loss"]
        assert row["v"] == comb(h, 3) and loss == h*(h-1)
        blocks = list(row["blocks"])
        assert len(blocks) == h+1 and all(isinstance(n, int) and n >= 0 for n in blocks)
        assert sum(t*n for t, n in enumerate(blocks)) == row["rank_sum"] == h*roles+2*loss
        assert blocks[h] >= h
        blocks[h] -= h
        blocks[1] += h
        assert sum(t*n for t, n in enumerate(blocks)) == h*roles+loss
        copies = N//row["v"]
        bank = copies*roles
        banks.append(bank)
        L += copies*loss
        parts["internal_%d_h%d" % (axis, h)] = Counter({t: n*copies for t, n in enumerate(blocks) if t and n})
        parts["exterior_%d_h%d" % (axis, h)] = Counter({h: bank, m-2*h: bank})
        parts["growth_%d_h%d" % (axis, h)] = Counter({1: 2*N, h-2: 2*N})
    d = a+b-1
    data = Counter({m-d: 2*N}) if optimistic else Counter({1: 9*2*N, 21: 2*N, 17: 2*N, 481: 2*N})
    assert sum(t*n for t, n in data.items()) == 2*N*(m-d)
    parts["data"] = data
    parts["paid_endpoint"] = Counter({1: N})
    widths = sum(parts.values(), Counter())
    W = 2*N+sum(banks)
    mass = sum(t*n for t, n in widths.items())
    assert all(0 < t < m and n > 0 for t, n in widths.items())
    assert mass == W*m-N+L
    return dict(dimensions=[a, b], m=m, N=N, banks=banks, W=W, L=L,
                total_rank=mass, deficit=N-L, maxchild=max(widths),
                child_multiplicities=dict(sorted(widths.items())), parts=parts,
                data_scope="OPTIMISTIC one-block lower cost, not a geometry certificate" if optimistic
                           else "Pinned ordered23/25 fixed-both geometry; unchanged output families")


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--first", required=True, type=Path)
    ap.add_argument("--second", required=True, type=Path)
    ap.add_argument("--saving", type=Q, default=REFERENCE_A)
    ap.add_argument("--optimistic-data", action="store_true")
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    assert args.saving > 0
    first, second = (json.loads(path.read_text()) for path in (args.first, args.second))
    counts = profile(first, second, args.optimistic_data)
    exact = moment(counts["m"], counts["W"], counts["child_multiplicities"], args.saving)
    result = dict(status="exact_complete_controller_arithmetic", counts=counts, moment=exact,
                  inputs=[dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                          for path in (args.first, args.second)],
                  wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="Finite arithmetic only; scalar/matrix/geometry/compiler premises remain separate",
                  caveat="Optimistic FAIL excludes this paid topology; optimistic PASS does not construct a controller"
                         if args.optimistic_data else "Retain the named fixed-basis and physical output-family hypotheses")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(jsonable(result), indent=2)+"\n")
    print(json.dumps(dict(saving=exact["saving"], strictly_passes=exact["strictly_passes"],
                          strictly_fails=exact["strictly_fails"], W=counts["W"], total_rank=counts["total_rank"],
                          deficit=counts["deficit"], data_scope=counts["data_scope"]), indent=2))


if __name__ == "__main__":
    main()
