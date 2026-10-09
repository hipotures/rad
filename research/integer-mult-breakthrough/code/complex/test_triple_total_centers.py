#!/usr/bin/env python3
"""Bounded scalar/guard/capacity controls for the triple-total quotient."""
from fractions import Fraction as Q
import unittest

from center_basis_scalar_word import apply
import triple_total_centers as centers
import triple_total_guard as guards


class TripleTotal(unittest.TestCase):
    def test_unimodular_source_word_and_decoder(self):
        for h in (4, 6, 8):
            result = centers.scalar_control(h)
            self.assertEqual(result['central_entries'], result['scalar_counts']['volume']**2)
            self.assertEqual(result['scalar_counts']['additional_fractional_bits'], 0)
            self.assertTrue(result['wrong_inverse_rejected'])

    def test_actual_inverse_prefix_and_temporary_guard(self):
        result = guards.probe(8)
        self.assertEqual(result['forward']['maximum_row_l1'], 56)
        self.assertLessEqual(result['inverse']['maximum_row_l1'], 3*56)
        self.assertEqual(result['inverse']['maximum_coefficient'], 3)
        compiled = centers.word(8)
        j = compiled['source_order'].index((4, 5, 6))
        original = [Q(int(i == j)) for i in range(56)]
        partial = apply(compiled['gates'][9:], original, True)
        self.assertEqual(partial[1], 3)
        self.assertEqual(partial[0], 2)
        self.assertGreater(abs(partial[1]), 2)

    def test_complete_triple_profile_is_conditional_and_closed(self):
        result = centers.capacity(48)
        closed, additive = result['rows'][2], result['rows'][3]
        self.assertLess(closed['target_moment_interval'][1], 1)
        self.assertGreater(additive['target_moment_interval'][0], 1)
        self.assertGreater(closed['root_bracket']['lower'], centers.TARGET)
        p = closed['profile']
        self.assertEqual(p['volume'], 17_296)
        self.assertEqual(p['source_weight'], 3)
        self.assertEqual(sum(int(t)*n for t, n in p['child_multiplicities'].items()),
                         p['W']*p['m']-p['N']+2*p['volume']*p['assumed_center_loss'])


if __name__ == '__main__':
    unittest.main()
