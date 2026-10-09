#!/usr/bin/env python3
"""Bounded literal controls for conditioned Gaussian-dyadic C blocks."""
from fractions import Fraction as Q
from itertools import product
import random
import unittest

import conditioned_frame_screen as producer


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def reciprocal(a):
    denominator = a[0]*a[0]+a[1]*a[1]
    return a[0]/denominator, -a[1]/denominator


def literal_unit(exponent, phase):
    value = (Q(1), Q(0))
    step = (Q(1), Q(1)) if exponent >= 0 else (Q(1, 2), Q(-1, 2))
    for _ in range(abs(exponent)):
        value = multiply(value, step)
    for _ in range(phase % 4):
        value = -value[1], value[0]
    return value


def pack(rows):
    denominator = max(z.denominator.bit_length()-1 for row in rows for value in row for z in value)
    assert all(z.denominator == 1 << (z.denominator.bit_length()-1)
               for row in rows for value in row for z in value)
    return producer.normalize([[tuple(int(z*(1 << denominator)) for z in value)
                                for value in row] for row in rows], denominator)


def literal_block(rank, input_map, output_map, input_weights, output_weights, inverted=False):
    rows = [[(Q(0), Q(0))]*8 for _ in range(8)]
    for a, b in product(range(8), repeat=2):
        if a >> rank != b >> rank:
            continue
        value = (Q(1), Q(0))
        for j in range(rank):
            value = multiply(value, (Q(1, 2), Q(-1 if (a ^ b) >> j & 1 else 1, 2)))
        if inverted:
            value = value[0], -value[1]
            value = multiply(value, reciprocal(literal_unit(*input_weights[b])))
            value = multiply(value, reciprocal(literal_unit(*output_weights[a])))
            rows[input_map[b]][output_map[a]] = value
        else:
            value = multiply(value, literal_unit(*input_weights[b]))
            value = multiply(value, literal_unit(*output_weights[a]))
            rows[output_map[a]][input_map[b]] = value
    return pack(rows)


def apply(operator, vector):
    rows, denominator = operator
    return [tuple(sum(multiply(tuple(Q(z, 1 << denominator) for z in value), x)[k]
                      for value, x in zip(row, vector)) for k in range(2)) for row in rows]


class ConditionedFrames(unittest.TestCase):
    def test_unit_canonicalization_and_nonunits(self):
        for exponent, phase in product(range(-12, 13), range(4)):
            value = literal_unit(exponent, phase)
            operator = pack([[value]])
            self.assertEqual(producer.gaussian_unit(operator[0][0][0], operator[1]), (exponent, phase))
        for value in ((0, 0), (3, 0), (1, 2), (3, 3), (4, 1)):
            self.assertIsNone(producer.gaussian_unit(value, 0))

    def test_literal_forward_inverse_and_complete_dirty_fields(self):
        rng = random.Random(20261009)
        count = 0
        for rank in range(4):
            for _ in range(6):
                inputs = list(range(8)); outputs = list(range(8))
                rng.shuffle(inputs); rng.shuffle(outputs)
                input_weights = [(rng.randrange(-2, 3), rng.randrange(4)) for _ in range(8)]
                output_weights = [(rng.randrange(-2, 3), rng.randrange(4)) for _ in range(8)]
                forward = literal_block(rank, inputs, outputs, input_weights, output_weights)
                backward = literal_block(rank, inputs, outputs, input_weights, output_weights, True)
                for operator in (forward, backward):
                    normal_form, reason = producer.classify(operator, True)
                    self.assertIsNotNone(normal_form, reason)
                    self.assertEqual(producer.reconstruct(normal_form), operator)
                    self.assertEqual(Q(normal_form['average_rank']), rank)
                self.assertEqual(producer.compose(forward, backward), producer.I)
                self.assertEqual(producer.compose(backward, forward), producer.I)
                for _ in range(4):
                    dirty = [(Q(rng.randrange(-19, 20), 8), Q(rng.randrange(-19, 20), 8)) for _ in range(8)]
                    self.assertEqual(apply(backward, apply(forward, dirty)), dirty)
                    count += 8
        self.assertEqual(count, 768)

    def test_rejects_missing_scaling_inverse_and_invalid_block(self):
        weights = [(2, 3) if j == 7 else (0, 0) for j in range(8)]
        D = producer.diagonal(weights)
        wrong_inverse = producer.inverse(D)
        self.assertNotEqual(producer.compose(D, wrong_inverse), producer.I)
        dirty = [(Q(j+1), Q(1)) for j in range(8)]
        self.assertNotEqual(apply(wrong_inverse, apply(D, dirty)), dirty)
        rows, den = producer.graph_operator(63)
        changed = [list(row) for row in rows]
        changed[0] = [tuple(3*z for z in value) for value in changed[0]]
        self.assertEqual(producer.classify(producer.normalize(changed, den))[1], 'nonunit-Gaussian-entry')
        changed = [list(row) for row in rows]
        changed[0][0] = producer.unit(changed[0][0], 1)
        self.assertIsNone(producer.classify(producer.normalize(changed, den))[0])


if __name__ == '__main__':
    unittest.main()
