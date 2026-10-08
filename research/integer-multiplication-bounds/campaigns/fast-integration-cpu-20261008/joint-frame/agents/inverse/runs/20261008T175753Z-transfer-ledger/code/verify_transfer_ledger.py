#!/usr/bin/env python3
"""Independent fixed-word, native-moment, row-stock and guard ledger.

Reads the immutable public PR58 snapshot. This is an arithmetic/interface
review, not another execution of the complete finite producer or a proof of
the inherited general residual compiler.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from math import comb, factorial
from pathlib import Path


def ceil_fraction(value):
    return -((-value.numerator) // value.denominator)


def log_interval(value):
    """64-term atanh with range reduction, then directed rational rounding."""
    assert value >= 1
    shifts = 0
    while value >= 2:
        value /= 2
        shifts += 1

    def small(x):
        z = (x - 1) / (x + 1)
        assert 0 <= z <= F(1, 3)
        lower = sum((2 * z ** (2*j+1) / (2*j+1) for j in range(64)), F(0))
        remainder = 2 * z**129 / (129 * (1-z*z))
        return lower, lower + remainder

    lower, upper = small(value)
    lo2, hi2 = small(F(2))
    lower += shifts * lo2
    upper += shifts * hi2
    scale = 10**60
    return F((lower*scale).numerator // (lower*scale).denominator, scale), F(ceil_fraction(upper*scale), scale)


def exp_interval(lower, upper):
    """Positive eight-term Taylor lower and a geometric remainder upper."""
    assert 0 <= lower <= upper < 1
    lo = sum((lower**k / factorial(k) for k in range(9)), F(0))
    hi = sum((upper**k / factorial(k) for k in range(9)), F(0))
    hi += upper**9 / (factorial(9) * (1-upper/10))
    return lo, hi


def moment(m, width, counts, saving):
    lower_word = upper_word = 0
    scale = 10**50
    for t, count in sorted(counts.items()):
        assert 0 < t < m and count > 0
        lo, hi = log_interval(F(m, t))
        lo, hi = exp_interval(saving*lo, saving*hi)
        weight = F(t*count, m*width)
        a, b = weight*lo*scale, weight*hi*scale
        lower_word += a.numerator // a.denominator
        upper_word += ceil_fraction(b)
    return {"saving": str(saving), "lower": str(F(lower_word, scale)),
            "upper": str(F(upper_word, scale)), "strict_gap_lower": str(F(scale-upper_word, scale)),
            "strictly_below_one": upper_word < scale,
            "strictly_above_one": lower_word > scale,
            "method": "64-term range-reduced atanh; degree-eight positive exponential Taylor with explicit geometric tail; directed 10^-50 summands"}


def depth_degree(m, maximum):
    degree = 1
    while m**degree <= 2*maximum**degree:
        degree += 1
    return degree


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), "use a fresh immutable receipt"
    paths = []

    def read(name):
        path = args.inputs / name
        paths.append(path)
        return json.loads(path.read_text())

    certificate = read("certificates/joint-dual-kappa.json")
    m, n = 575, comb(23, 3)*comb(25, 3)
    width = 2*n
    loss = 0
    rows = Counter({1: 19*n, 21: 2*n, 17: 2*n, 481: 2*n})
    local = []
    replicated_xors = 0
    replicated_events = 0
    for h in (23, 25):
        profile = read(f"certificates/joint-dual-profiles-{h}.json")
        transition = read(f"certificates/joint-dual-transitions-{h}.json")
        packed = args.inputs / f"certificates/joint-dual-word-{h}.json.gz"
        paths.append(packed)
        raw = gzip.decompress(packed.read_bytes())
        word = json.loads(raw)
        v, r = word["v"], word["R"]
        assert v == comb(h, 3) and r == profile["R"] == transition["R"]
        assert len(word["sources"]) == v and len(word["scatter"]) == 6*v
        assert len({o[0] for o in word["outputs"]}) == len(word["outputs"])
        assert all(0 <= a < r and 0 <= b < r and a != b for a, b, g in word["ops"])
        assert all(0 <= slot < r for slot, old, new in word["events"])
        wrapped = 4*len(word["ops"])+2*len(word["scatter"])+2*len(word["sources"])
        assert wrapped == 4*len(word["ops"])+14*v
        rep = n//v
        replicated_xors += rep*wrapped
        replicated_events += rep*len(word["events"])
        width += rep*r
        loss += rep*h*(h-1)
        internal = Counter({t: count*rep for t, count in enumerate(profile["blocks"]) if t and count})
        assert sum(t*count for t, count in enumerate(profile["blocks"])) == h*r+h*(h-1)
        assert profile["blocks"][h] == 0
        rows += internal
        rows += Counter({h: rep*r, m-2*h: rep*r, 1: 2*n, h-2: 2*n})
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == transition["word_sha256"]
        local.append({"h": h, "v": v, "R": r, "replications": rep,
                      "mixer_XORs": len(word["ops"]), "scatter_XORs": len(word["scatter"]),
                      "source_injections": len(word["sources"]), "wrapped_XORs": wrapped,
                      "literal_frame_events": len(word["events"]), "decompressed_word_sha256": digest,
                      "distinct_output_roles": len(word["outputs"]), "copied_rank_mass": profile["rank_sum"]})
    mass = sum(t*count for t, count in rows.items())
    assert dict(sorted(rows.items())) == {int(t): count for t, count in certificate["bit"]["child_multiplicities"].items()}
    assert (width, loss, mass, m*width-mass, max(rows)) == (150593466, 2226400, 86589396050, 1846900, 529)
    a = F(1187740349, 25000000000000)
    moments = [moment(m, width, rows, a), moment(m, width, rows, a+F(1, 10**14)),
               moment(m, width, rows, a*F(99999, 100000))]
    assert moments[0]["strictly_below_one"] and moments[1]["strictly_above_one"] and moments[2]["strictly_below_one"]
    bridge = certificate["finite_bridge"]
    db, dc = depth_degree(m, max(rows)), depth_degree(784, 756)
    wb, wc = width.bit_length(), 537696432 .bit_length()
    coefficient = db*wb+dc*wc
    assert (db, dc, wb, wc, coefficient) == (9, 20, 28, 30, 852)
    gap = F(2000)-F(51, 25)*coefficient
    assert gap == F(6548, 25) > 0
    s, g, w = 421548223824, 4793351472, 537696432
    e = 64*(w+784+g+1)**3
    b = s+e
    c0 = 32*784*b*b
    literal = 2*g*w*w+8*s+4*w+4+32*784
    assert e > literal and 2*b*(784-756) >= s+e and c0 > 2*b+18
    assert all(bridge["semantic"][key] == value for key, value in {"E": e, "B": b, "C0": c0, "literal_charge": literal}.items())
    receipt = {
        "status": "PASS_INDEPENDENT_FIXED_LEDGER_AND_ARITHMETIC", "source_commit": "bc2f7ed4c20dc18898305ab17165c0c995cbb804",
        "source_PR": "https://github.com/CrocSwap/integer-mult-bounds/pull/58", "local_words": local,
        "replicated_wrapped_XORs": replicated_xors, "replicated_literal_frame_events": replicated_events,
        "bit": {"m": m, "W": width, "rank_mass": mass, "deficit": m*width-mass,
                "number_of_native_children": sum(rows.values()), "maximum_child": max(rows), "child_multiplicities": dict(sorted(rows.items()))},
        "moments": moments, "row_stock": {"bit_halving_degree": db, "complex_halving_degree": dc,
            "bit_role_bits": wb, "complex_role_bits": wc, "product_coefficient": coefficient,
            "degree": 2000, "strict_degree_gap": str(gap), "suffix_slope": 8000},
        "unchanged_complex_arithmetic": {"scalar_groups_upper": g, "rank_mass": s, "E": e, "B": b, "C0": c0,
            "literal_charge": literal, "literal_gap": e-literal, "C1": 1},
        "binary_word_charge_scope": "2,206,597,276 is complete replicated LOCAL dirty-wrapper XOR charge; fixed residual basis/front/copy/scheduler operations remain separately paid inherited overhead. No exact full global gate count is claimed.",
        "all_size_status": "Conditional interface review required; this executable does not prove physical residual compilation, tapes, eligible primes or multiplication recovery.",
        "input_sha256": {str(p.relative_to(args.inputs)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps({"status": receipt["status"], "wrapped_local_XORs": replicated_xors,
                      "bit_moment_gap_lower": moments[0]["strict_gap_lower"], "row_degree_gap": str(gap)}))


if __name__ == "__main__":
    main()
