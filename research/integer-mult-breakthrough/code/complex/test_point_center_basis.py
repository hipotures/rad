#!/usr/bin/env python3
"""Exact bounded scalar point-center controls, including the scope failure."""
from fractions import Fraction
import unittest

from point_center_basis import complete_word,pivot_basis,run
from center_basis_scalar_word import apply
from center_null_basis import identity,multiply


class PointCenter(unittest.TestCase):
    def test_literal_linear_completion_and_degenerate_star(self):
        seven=run(7,20261008);eight=run(8,20261008)
        self.assertTrue(seven['linear_completion_is_fitting'])
        self.assertTrue(eight['linear_completion_is_fitting'])
        self.assertEqual(seven['scalar_operation_counts']['add'],92)
        self.assertEqual(eight['scalar_operation_counts']['add'],261)
        self.assertTrue(all(s['radical_dimension']==1
                            for s in seven['feature_spans'][1:]))
        self.assertTrue(all(s['radical_dimension']==0 for s in eight['feature_spans']))

    def test_scope_fails_when_odd_one_intersection_appears(self):
        result=run(10,20261008)
        self.assertFalse(result['linear_completion_is_fitting'])
        witness=result['odd_intersection_counterexamples'][0]
        self.assertEqual(witness['intersection'],1)
        self.assertEqual(Fraction(witness['central_coefficient']),-1)

    def test_dyadic_pivot_extension_and_missing_shear(self):
        pivots,matrix,inverse=pivot_basis(12)
        self.assertEqual(multiply(matrix,inverse),identity(12))
        specification=complete_word(8);word=specification['word']
        values=[Fraction(0)]*len(specification['source_order'])
        values[word[-1][2]]=1
        full=apply(word,values)
        self.assertNotEqual(apply(word[:-1],values),full)
        self.assertEqual(apply(word,full,True),values)


if __name__=='__main__':unittest.main()
