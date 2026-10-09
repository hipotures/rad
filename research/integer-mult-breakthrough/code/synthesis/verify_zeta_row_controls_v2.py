#!/usr/bin/env python3
"""Narrow nonzero-unit domain repair for immutable zeta row controls."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import verify_zeta_row_controls as original


ORIGINAL_SHA256 = '9514e482e72df80828021ac19239e41232abae28d3151fdd92f6060a7b8c131a'


def validate_word(word):
    for gate in word:
        if gate[0] == 'scale':
            value = gate[-1]
            a, b = (Q(value), Q(0)) if isinstance(value, str) else tuple(Q(v) for v in value)
            norm = a*a+b*b
            if norm <= 0 or norm.numerator & (norm.numerator-1) or norm.denominator & (norm.denominator-1):
                raise AssertionError('A row scale is not a nonzero Gaussian-dyadic unit')


def apply(rows, word):
    validate_word(word)
    return original.apply(rows, word)


def verify():
    source = Path(original.__file__)
    if sha256(source.read_bytes()).hexdigest() != ORIGINAL_SHA256:
        raise AssertionError('The retained pre-repair control verifier changed')
    fixture = original.ROOT/'fixtures/synthesis/reversible-zeta-small-controls.json'
    inputs = json.loads(fixture.read_text())
    # Every historical word is validated before the unchanged arithmetic replay.
    words = []
    for key, lift_key in [('modular_control', 'exact_lift'), ('binary_control', 'exact_sign_lift')]:
        words.append(original.integer_word(inputs[key][lift_key]['gates']))
    words.append([('add', receiver, donor, [str(sign), '0'])
                  for donor, receiver, sign in inputs['cnf_control']['exact_sign_lift']['gates']])
    for key in ('real_unit_control', 'gaussian_unit_control'):
        words.extend([inputs[key]['forward_word'], inputs[key]['backward_word']])
    for word in words:
        validate_word(word); validate_word(original.inverse(word))
    identity = [[(int(i == j), 0) for j in range(4)] for i in range(4)]
    # Retain a direct reproduction of the original boundary, not a claim that
    # any historical accepted circuit used a zero multiplier.
    bad_zero = [('scale', 0, ['0', '0'])]
    old = original.apply(identity, bad_zero)
    if any(entry != (0, 0) for entry in old[0]):
        raise AssertionError('The original zero-scale boundary was not reproduced')
    negatives = [('zero', ['0', '0']), ('odd-real-norm', ['3', '0']), ('odd-Gaussian-norm', ['1', '2'])]
    rejected = []
    for name, coefficient in negatives:
        try:
            apply(identity, [('scale', 0, coefficient)])
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('A deliberate nonunit scale was not rejected')
    for coefficient in (['-1', '0'], ['0', '1'], ['1', '1'], ['1/2', '1/2']):
        apply(identity, [('scale', 0, coefficient)])
    result = original.verify()
    result.update(status='PASS NONZERO-UNIT ROW CONTROLS V2',
                  original_zero_scale_boundary_reproduced=True,
                  explicit_nonunit_controls_rejected=rejected,
                  unit_domain_guard='Strictly positive norm; numerator and denominator powers of2.',
                  historical_accepted_operators_unchanged=True,
                  original_verifier_sha256=ORIGINAL_SHA256)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(); result = verify()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            raise FileExistsError('Refusing to replace an existing repaired receipt')
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
