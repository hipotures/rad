#!/usr/bin/env python3
"""Bounded exact certificates for the single-total center hypothesis."""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
import random
import unittest

from center_basis_scalar_word import apply
from center_null_basis import identity, multiply, dyadic
import total_center_basis as basis
import total_center_capacity as capacity


class TotalCenters(unittest.TestCase):
    def test_dyadic_minor_and_missing_pair(self):
        for h in (7, 8, 12):
            pairs, sources, minor, inverse = basis.build(h)
            self.assertEqual(multiply(minor, inverse), identity(len(pairs)))
            self.assertTrue(all(dyadic(x) for row in inverse for x in row))
            for source in sources:
                total = basis.feature((0, 1), source)
                recovered = 10*total-sum(basis.feature(pair, source) for pair in pairs if pair != (0, 1))
                self.assertEqual(recovered, int({0, 1} <= set(source)))
        self.assertFalse(dyadic(Q(1, 5)))

    def test_complete_common_frame_dirty_word_and_charges(self):
        h = 8
        compiled = basis.complete_word(h)
        pairs, sources, word = compiled['pair_order'], compiled['source_order'], compiled['word']
        q, v = len(pairs), len(sources)
        counts = capacity.counts(h)
        self.assertEqual(Counter(gate[0] for gate in word)['add'], counts['additions'])
        self.assertEqual(sum(int(abs(gate[3])) for gate in word if gate[0] == 'add'), counts['expanded_unit_additions'])
        self.assertEqual(counts['expanded_scalar_proxy'], counts['expanded_unit_additions']+4*counts['swaps']+counts['scalar_scale_charges'])
        rng = random.Random(20261009)
        originals = [[Q(int(i == j)) for i in range(v)] for j in range(v)]
        originals += [[Q(rng.randrange(-100, 101), 1 << rng.randrange(5)) for _ in range(v)] for _ in range(4)]
        for original in originals:
            expected = [sum(basis.feature(pair, source)*x for source, x in zip(sources, original))
                        for pair in pairs]+original[q:]
            actual = apply(word, original)
            self.assertEqual(actual, expected)
            self.assertEqual(apply(word, actual, True), original)
        original = originals[0]
        self.assertNotEqual(apply(list(reversed(word)), apply(word, original)), original)

    def test_scalar_decoder_and_complete_conditional_moment(self):
        control = basis.central_control(8)
        self.assertEqual(control['complete_ordered_entries'], 56**2)
        pairs, _ = basis.orders(8)
        witness = (0, 2, 3, 4, 5)
        coefficients = basis.decoder_numerators(pairs, witness)
        self.assertEqual(coefficients[0], -18)
        altered = coefficients[:]; altered[0] = 0
        source = (0, 1, 2, 6, 7)
        self.assertNotEqual(sum(c*basis.feature(pair, source) for c, pair in zip(altered, pairs)),
                            sum(c*basis.feature(pair, source) for c, pair in zip(coefficients, pairs)))
        result = capacity.run(30)
        closed = result['rows'][2]
        additive = result['rows'][3]
        self.assertLess(closed['target_moment_interval'][1], 1)
        self.assertGreater(additive['target_moment_interval'][0], 1)
        self.assertGreater(closed['root_bracket']['lower'], capacity.TARGET)
        p = closed['profile']
        self.assertEqual(sum(int(t)*n for t, n in p['child_multiplicities'].items()),
                         p['W']*p['m']-p['N']+2*result['scalar_counts']['volume']*p['assumed_center_loss'])


if __name__ == '__main__':
    unittest.main()
