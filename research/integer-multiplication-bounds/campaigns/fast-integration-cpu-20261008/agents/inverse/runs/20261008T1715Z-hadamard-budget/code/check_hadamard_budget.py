#!/usr/bin/env python3
"""Exact scalar discriminator for a literal complex-only basis self-route."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2))
             for j in range(2)] for i in range(2)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), "use a fresh result path"
    half = Fraction(1, 2)
    hbar = [[half, half], [half, -half]]
    identity = [[1, 0], [0, 1]]
    flip = [[0, 1], [1, 0]]
    for c, target in ((0, identity), (1, flip)):
        diagonal = [[1, 0], [0, (-1) ** c]]
        assert multiply(multiply(hbar, diagonal), hbar) == [
            [half * value for value in row] for row in target]
    m, w, s = 784, 537696432, 421548223824
    deficit = m * w - s
    add_budget = (deficit - 1) // 2
    h, v = 28, 3276
    coordinate_groups = h * h // (h - 1)
    noncoordinate_fronts = (v - coordinate_groups) * v
    assert deficit == 5778864 and add_budget == 2889431
    assert coordinate_groups == 29 and noncoordinate_fronts == 10637172
    assert 2 * noncoordinate_fronts > deficit
    result = {
        "status": "PASS_EXACT_ALGEBRA_AND_CONDITIONAL_BUDGET",
        "native_science_pin": "43f59ff533598762cbc43a5e14af2bbbc76fabbd",
        "hadamard_two_point_identity_exact": True,
        "m": m, "W": w, "s": s, "rank_deficit": deficit,
        "strict_basis_additions_budget": add_budget,
        "coordinate_group_upper": coordinate_groups,
        "noncoordinate_front_lower_if_retained": noncoordinate_fronts,
        "conditional_added_rank_mass_lower": 2 * noncoordinate_fronts,
        "source_front_transfer_verified": False,
        "scope": "Literal per-residual basis-wrapper substitution; no universal compiler exclusion or all-size physical execution",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "workers": 1,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
