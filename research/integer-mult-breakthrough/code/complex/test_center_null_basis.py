#!/usr/bin/env python3
"""Bounded complete scalar certificates for center/null basis changes."""
from fractions import Fraction
import json
from pathlib import Path
import unittest

from center_null_basis import identity,multiply,run as smith_run
from structured_center_basis import build,feature
from center_basis_scalar_word import complete_word,apply,run as word_run


class CenterNull(unittest.TestCase):
    def test_original_odd_obstruction_and_mixed_dyadic_inverse(self):
        original=smith_run(8,False)
        mixed=smith_run(8,True)
        self.assertFalse(original['inverse_is_gaussian_dyadic'])
        self.assertEqual(original['invariant_counts'],{'1':20,'2':1,'4':6,'20':1})
        self.assertTrue(mixed['inverse_is_gaussian_dyadic'])
        self.assertEqual(mixed['invariant_counts'],{'1':21,'4':6,'32':1})
        self.assertTrue(mixed['checked']['full_left_right_inverse'])

    def test_immutable_base_inverse_and_corruption(self):
        fixture=Path(__file__).resolve().parents[2]/'fixtures'/'complex'/'mixed-center-h7-inverse.json'
        value=json.loads(fixture.read_text())
        rows=[tuple(p) for p in value['features']]
        sources=[tuple(s) for s in value['sources']]
        matrix=[[feature(p,s) for s in sources] for p in rows]
        numerator=value['inverse_numerators']
        target=[[32*x for x in row] for row in identity(21)]
        self.assertEqual(multiply(matrix,numerator),target)
        self.assertEqual(multiply(numerator,matrix),target)
        wrong=[row[:] for row in numerator];wrong[0][0]+=1
        self.assertNotEqual(multiply(matrix,wrong),target)

    def test_explicit_border_induction(self):
        for h in (7,8,10,16):
            pairs,pivots,matrix,inverse,stages=build(h)
            self.assertEqual(stages[-1]['absolute_determinant'],2**(2*h+1))
            self.assertEqual(len(set(pivots)),len(pairs))
            self.assertEqual(multiply(matrix,inverse),identity(len(pairs)))

    def test_complete_dirty_scalar_words(self):
        for h in (8,10):
            result=word_run(h,True,20261008)
            self.assertEqual(result['extra_dirty_banks'],0)
            self.assertTrue(result['checked']['wrong_chronology_rejected'])
            self.assertEqual(result['checked']['complete_basis_columns'],result['volume'])

    def test_omitted_nonpivot_shear_is_not_transparent(self):
        specification=complete_word(8)
        word=specification['word']
        i,j,c=word[-1][1:]
        values=[Fraction(0)]*len(specification['source_order']);values[j]=1
        full=apply(word,values)
        self.assertNotEqual(apply(word[:-1],values),full)
        self.assertEqual(apply(word,full,True),values)


if __name__=='__main__':unittest.main()
