#!/usr/bin/env python3
"""Bounded exact checks of hypothetical capacity and signed loss budgets."""
from fractions import Fraction as Q
from math import floor,ceil
import unittest

from center_native_leverage import TARGET,profile,run
from characteristic import moment_interval
from five_subset_envelope import pair_center_loss


class HypotheticalLeverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results={h:run(h) for h in (16,20)}

    def test_negative_allowance_is_outward_and_rejects_crossing(self):
        rows=self.results[16]['rows']
        worst=next(row for row in rows if 'proxy' in row['budget_hypothesis']
                   and row['profile']['local_distribution']=='rank1')
        lo,hi=worst['extra_local_rank_loss_per_source_interval']
        self.assertLessEqual(lo,hi)
        self.assertLess(hi,0)
        self.assertEqual(worst['target_crossing_status'],'above1')

    def test_loss_tolerance_matches_actual_rank_one_profile(self):
        result=self.results[20]
        row=next(row for row in result['rows'] if 'proxy' in row['budget_hypothesis']
                 and row['profile']['local_distribution']=='rank1')
        self.assertEqual(row['target_crossing_status'],'below1')
        lo,hi=row['extra_local_rank_loss_per_source_interval']
        v=result['volume'];R=result['expanded_scalar_gate_proxy'];loss=pair_center_loss(20)
        low=profile(20,R,loss+floor(lo*v),'rank1')
        high=profile(20,R,loss+ceil(hi*v),'rank1')
        self.assertLess(moment_interval(low,TARGET)[1],1)
        self.assertGreater(moment_interval(high,TARGET)[0],1)
        one_per_output=profile(20,R,loss+v,'rank1')
        self.assertGreater(moment_interval(one_per_output,TARGET)[0],1)

    def test_declared_tensor_width_scaling_preserves_moment(self):
        p=self.results[20]['rows'][2]['profile'];f=7
        scaled=dict(p,m=p['m']*f,
            child_multiplicities={t*f:n for t,n in p['child_multiplicities'].items()})
        self.assertEqual(moment_interval(p,TARGET),moment_interval(scaled,TARGET))
        # This tests a declared f-linear profile only. It does not tensor-lift
        # the independent minrank lower bound for arbitrary bulk frames.


if __name__=='__main__':unittest.main()
