#!/usr/bin/env python3
"""Bounded evidence validation for the generalized phase interface."""
from itertools import product
import unittest

from quadratic_rank_interface import (Quadratic,candidate_numerator,multiply,
                                      symmetric_rows,verify_case,walsh_reference)


class QuadraticControls(unittest.TestCase):
    def test_complete_two_coordinate_lifts(self):
        counts={}
        for code,even in product(range(8),range(4)):
            rows=symmetric_rows(2,code)
            linear=[((rows[j]>>j)&1)+2*((even>>j)&1) for j in range(2)]
            row=verify_case(Quadratic(rows,linear));counts[row['rank']]=counts.get(row['rank'],0)+1
        self.assertEqual(counts,{0:4,1:12,2:16})

    def test_reject_invalid_quadratic_contract(self):
        with self.assertRaises(ValueError):Quadratic([2,0],[0,0])
        with self.assertRaises(ValueError):Quadratic([1,0],[0,0])
        with self.assertRaises(ValueError):Quadratic([1],[5])

    def test_radical_translation_is_not_identity(self):
        q=Quadratic([0,0,0],[0,2,0]);nf=q.normal_form()
        self.assertEqual(nf['rank'],0)
        self.assertEqual(candidate_numerator(q,nf,2,0),(1,0))
        self.assertEqual(candidate_numerator(q,nf,2,0,omit_radical=True),(0,0))
        self.assertEqual(walsh_reference(q),[(0,0),(0,0),(8,0),(0,0),(0,0),(0,0),(0,0),(0,0)])

    def test_missing_arf_or_gaussian_unit_rejected(self):
        q=Quadratic([2,1],[2,2]);nf=q.normal_form()
        self.assertEqual(nf['gauss_sum'],(-2,0))
        self.assertEqual(candidate_numerator(q,nf,0,0),(-2,0))
        self.assertNotEqual(candidate_numerator(q,nf,0,0,omit_constant=True),(-2,0))
        nf['constant']=(1,0)
        self.assertNotEqual(candidate_numerator(q,nf,0,0),(-2,0))

    def test_difference_keeps_even_linear_lift(self):
        first=Quadratic([3,1],[1,0]);second=Quadratic([3,1],[3,2])
        delta=Quadratic([0,0],[2,2]);nf=delta.normal_form()
        self.assertEqual(nf['rank'],0)
        self.assertEqual(walsh_reference(delta)[3],(4,0))
        self.assertTrue(all(delta.value(x)==(first.value(x)-second.value(x))%4 for x in range(4)))

    def test_two_column_tensor_on_arbitrary_pair_addresses(self):
        q=Quadratic([3,1],[3,2]);nf=q.normal_form();reference=walsh_reference(q)
        for a,b in product(range(16),repeat=2):
            z=(1,0);expected=(1,0)
            for shift in (0,2):
                aa=(a>>shift)&3;bb=(b>>shift)&3
                z=multiply(z,candidate_numerator(q,nf,aa,bb))
                expected=multiply(expected,reference[aa^bb])
            scale=1<<(2*(q.n-nf['rank']))
            self.assertEqual(expected,tuple(scale*v for v in z))


if __name__=='__main__':unittest.main()
