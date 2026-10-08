#!/usr/bin/env python3
"""Bounded exact checks for the scoped right-Toffoli block obstruction."""
import copy
from fractions import Fraction
import unittest

from nonlinear_common_frame_screen import (
    I,N,clifford_representatives,compose,graph_operator,inverse,
    nonlinear_permutation,single_child)
from nonuniform_phase_blocks import classify,reconstruct
from nonuniform_convex_certificate import run
from lagrangian_phase_screen import distance,graph_frames


class NonlinearBlocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reps=clifford_representatives()
        cls.graphs=graph_frames(N)
        cls.endpoints=[graph_operator(code) for code in range(64)]

    def test_complete_clifford_controls(self):
        for label,frame,_ in self.reps:
            self.assertEqual(compose(frame,inverse(frame)),I)
            for graph,endpoint in zip(self.graphs,self.endpoints):
                self.assertEqual(single_child(compose(frame,inverse(endpoint))),
                                 distance(label,graph,N))

    def test_literal_nonuniform_blocks_and_corrupt_gauge(self):
        permutation,_=nonlinear_permutation('toffoli0')
        frame=compose(self.reps[3][1],permutation)
        expected={0:Fraction(1),8:Fraction(3,2)}
        for code,mean in expected.items():
            edge=compose(frame,inverse(self.endpoints[code]))
            nf,reason=classify(edge,True)
            self.assertEqual(reason,'exact-direct-sum')
            self.assertEqual(Fraction(nf['average_rank']),mean)
            self.assertEqual(reconstruct(nf),edge)
            wrong=copy.deepcopy(nf)
            wrong['blocks'][0]['output_unit_exponents'][0]^=1
            self.assertNotEqual(reconstruct(wrong),edge)
        self.assertIsNone(single_child(compose(frame,inverse(self.endpoints[8]))))

    def test_fixed_mixture_beats_componentwise_test(self):
        permutation,_=nonlinear_permutation('toffoli0')
        frame=compose(self.reps[3][1],permutation)
        costs=[classify(compose(frame,inverse(endpoint)))[0]
               for endpoint in self.endpoints]
        valid=[c for c,value in enumerate(costs) if value is not None]
        baseline=[[distance(label,graph,N) for graph in self.graphs]
                  for label,_,_ in self.reps]
        self.assertFalse(any(all(row[c]<=costs[c] for c in valid)
                             for row in baseline))
        a=self.reps.index(next(rep for rep in self.reps if rep[0]==(4,2,1)))
        b=self.reps.index(next(rep for rep in self.reps if rep[0]==(17,10,4)))
        self.assertTrue(all(baseline[a][c]+baseline[b][c]<=2*costs[c]
                            for c in valid))
        # Replacing the mixture by its first endpoint fails at code2.
        self.assertGreater(baseline[a][2],costs[2])

    def test_complete_convex_certificates_all_four_families(self):
        for family in ('toffoli0','toffoli1','toffoli2','cycle'):
            result=run(family)
            self.assertEqual(result['certified_candidates'],135)
            self.assertEqual(result['unresolved_candidates'],[])
            expected=352 if family=='cycle' else 2112
            self.assertEqual(result['edge_classification']['exact-direct-sum'],expected)
            for cert in result['certificates']:
                self.assertEqual(cert['weights'],['1/2','1/2'])
                self.assertTrue(all(sum(ranks)<=2*Fraction(mean)
                                    for ranks,mean in zip(cert['dominating_rank_pairs'],
                                                          cert['mean_ranks'])))


if __name__=='__main__':unittest.main()
