#!/usr/bin/env python3
"""Independent bounded control replay for retained reversible zeta searches."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def multiply(x, y):
    return x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0]


def apply(rows, word):
    rows = [[(Q(a), Q(b)) for a, b in row] for row in rows]
    for gate in word:
        kind = gate[0]
        if kind == 'swap':
            _, a, b = gate; rows[a], rows[b] = rows[b], rows[a]
            continue
        value = gate[-1]
        coefficient = (Q(value), Q(0)) if isinstance(value, str) else tuple(Q(v) for v in value)
        if kind == 'scale':
            _, receiver, _ = gate
            norm = coefficient[0]**2+coefficient[1]**2
            if norm.numerator & (norm.numerator-1) or norm.denominator & (norm.denominator-1):
                raise AssertionError('A replayed row scale is outside the dyadic-unit domain')
            rows[receiver] = [multiply(coefficient, entry) for entry in rows[receiver]]
        else:
            _, receiver, donor, _ = gate
            rows[receiver] = [(a+c, b+d) for (a, b), (c, d) in
                              zip(rows[receiver], [multiply(coefficient, entry) for entry in rows[donor]])]
        if any(v.denominator & (v.denominator-1) for row in rows for pair in row for v in pair):
            raise AssertionError('A replayed prefix leaves the Gaussian-dyadic grid')
    return rows


def integer_word(gates):
    return [('add', receiver, donor, [str(a), str(b)]) for donor, receiver, (a, b) in gates]


def inverse(word):
    result = []
    for gate in reversed(word):
        if gate[0] == 'add':
            _, receiver, donor, value = gate
            coefficient = (Q(value), Q(0)) if isinstance(value, str) else tuple(Q(v) for v in value)
            result.append(('add', receiver, donor, [str(-v) for v in coefficient]))
        elif gate[0] == 'scale':
            _, receiver, value = gate
            a, b = (Q(value), Q(0)) if isinstance(value, str) else tuple(Q(v) for v in value)
            norm = a*a+b*b
            result.append(('scale', receiver, [str(a/norm), str(-b/norm)]))
        else:
            result.append(gate)
    return result


def binary_counts():
    wanted = [1, 3, 5, 15]; counts = []
    pairs = [(a, b) for a in range(4) for b in range(4) if a != b]
    for gates in range(5):
        count = 0
        for word in product(pairs, repeat=gates):
            rows = [1, 2, 4, 8]
            for donor, receiver in word:
                rows[receiver] ^= rows[donor]
            count += sorted(rows) == wanted
        counts.append(count)
    return counts


def ternary_three_gate_count():
    wanted = [[1, 0, 0, 0], [1, 1, 0, 0], [1, 0, 1, 0], [1, 1, 1, 1]]
    accepted = 0
    choices = [(a, b, c) for a in range(4) for b in range(4) if a != b for c in (1, 2)]
    for gates in product(choices, repeat=3):
        rows = [[int(i == j) for j in range(4)] for i in range(4)]
        for donor, receiver, scalar in gates:
            rows[receiver] = [(a+scalar*b) % 3 for a, b in zip(rows[receiver], rows[donor])]
        matches = []
        for row in rows:
            possible = [i for i, target in enumerate(wanted) for scalar in (1, 2)
                        if row == [scalar*value % 3 for value in target]]
            if not possible:
                break
            matches.extend(possible)
        accepted += len(matches) == 4 and len(set(matches)) == 4
    return accepted


def verify():
    fixture = ROOT/'fixtures/synthesis/reversible-zeta-small-controls.json'
    inputs = json.loads(fixture.read_text())
    identity = [[(int(i == j), 0) for j in range(4)] for i in range(4)]
    zeta = [[(int(j & ~i == 0), 0) for j in range(4)] for i in range(4)]
    words = []
    for key, lift_key in [('modular_control', 'exact_lift'), ('binary_control', 'exact_sign_lift')]:
        words.append(integer_word(inputs[key][lift_key]['gates']))
    words.append([('add', receiver, donor, [str(sign), '0'])
                  for donor, receiver, sign in inputs['cnf_control']['exact_sign_lift']['gates']])
    for key in ('real_unit_control', 'gaussian_unit_control'):
        words.append(inputs[key]['forward_word'])
        if apply(zeta, inputs[key]['backward_word']) != identity:
            raise AssertionError('A retained independent inverse word failed')
    for word in words:
        if len([gate for gate in word if gate[0] == 'add']) != 4:
            raise AssertionError('A small control arithmetic bill differs')
        if apply(identity, word) != zeta or apply(zeta, inverse(word)) != identity:
            raise AssertionError('Independent full forward/inverse control replay failed')
        broken = list(word)
        for index, gate in enumerate(broken):
            if gate[0] == 'add':
                broken[index] = ('add', gate[1], gate[2], ['0', '0']); break
        if apply(identity, broken) == zeta:
            raise AssertionError('The omitted-addition negative control was not detected')
    counts = binary_counts()
    if counts != inputs['exhaustive_binary_h2_word_counts_0_to_4'] or ternary_three_gate_count() != 0:
        raise AssertionError('Independent binary/ternary exhaustive controls disagree')
    # All Gaussian-dyadic units have well-defined nonzero modulo3 images.
    powers = []; current = (1, 0)
    for _ in range(8):
        powers.append(current); a, b = multiply(current, (1, 1)); current = (a % 3, b % 3)
    if len(set(powers)) != 8 or current != (1, 0):
        raise AssertionError('The modulo3 Gaussian unit group control failed')
    return dict(status='PASS INDEPENDENT SMALL ROW CONTROLS', exact_forward_inverse_words=len(words),
                complete_columns_each=4, binary_exhaustive_counts=counts,
                ternary_three_gate_words=24**3, ternary_three_gate_witnesses=0,
                gaussian_unit_mod3_order=8, omitted_gate_controls_rejected=len(words),
                fixture_sha256=sha256(fixture.read_bytes()).hexdigest(),
                h3_eleven_gate_status='UNRESOLVED', native_supplier=False, larger_kappa=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); result = verify()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            raise FileExistsError('Refusing to replace an existing verification receipt')
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
