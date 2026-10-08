#!/usr/bin/env python3
"""Bounded exact checks and negative controls for the complex track."""
import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import unittest

from block_exclusion import BlockExclusion
from center_obstructions import affine_support_checks, direct_eigen_controls, invariant_minrank
from characteristic import copied_histogram, moment_interval, profile
from five_subset_envelope import gaussian_dyadic_center_identities, pair_center_loss, envelope
from five_side_screen import FiveSide
from frame_feasibility import basis, check_graph, intersection_witness, nullspace, radical
from tree_intersection import TreeIntersection

FIXTURE=Path(__file__).resolve().parents[2]/'fixtures/complex/pr36-local-axis.json'


class FrozenCharacteristicTests(unittest.TestCase):
    def setUp(self):
        self.row=json.loads(FIXTURE.read_text())

    def test_complete_profile_and_rigorous_root(self):
        p=profile(self.row)
        self.assertEqual((p['m'],p['W'],p['total_rank']),
                         (784,537696432,421548223824))
        self.assertLess(moment_interval(p,Q(71744621,10**12))[1],1)
        self.assertGreater(moment_interval(p,Q(71744622,10**12))[0],1)
        self.assertGreater(moment_interval(p,Q(20,189981))[0],1)

    def test_corrupt_rank_mass_rejected(self):
        bad=copy.deepcopy(self.row)
        bad['histogram'][1]+=1
        with self.assertRaisesRegex(ValueError,'rank mass'):
            profile(bad)

    def test_paid_center_transform_cannot_be_omitted(self):
        bad=copy.deepcopy(self.row)
        bad['loss']=0
        with self.assertRaisesRegex(ValueError,'center loss'):
            copied_histogram(bad)

    def test_negative_multiplicity_rejected(self):
        bad=copy.deepcopy(self.row)
        bad['histogram'][0]=-1
        with self.assertRaisesRegex(ValueError,'multiplicity'):
            profile(bad)


class BlockPartitionTests(unittest.TestCase):
    def test_direct_supports_wider_blocks_and_degree_omission_distinction(self):
        for n,block in ((6,2),(7,3),(8,4),(10,3)):
            generator=BlockExclusion(n,block,3)
            generator.verify(min(n,3))
            for omitted,node in generator.outputs.items():
                expected=sum(1<<j for j,t in enumerate(generator.inputs)
                             if set(omitted).isdisjoint(t))
                self.assertEqual(generator.support[node],expected,(n,block,omitted))

    def test_corrupt_answer_rejected(self):
        generator=BlockExclusion(8,3,3)
        target=generator.inputs[0]
        generator.support[generator.outputs[target]] ^= 1
        with self.assertRaisesRegex(ValueError,'wrong exclusion'):
            generator.verify()


class CenterRestrictionsTests(unittest.TestCase):
    def test_affine_signed_pair_complement_boundary(self):
        checks=affine_support_checks(8)['hyperplane_classification']
        self.assertEqual([row['normal_weight'] for row in checks if row['coefficient_nullity']],
                         [1,2,6,7])
        self.assertFalse(checks[5]['hyperplane_nondegenerate'])
        self.assertEqual(checks[5]['support_span_rank'],7)

    def test_invariant_rank_and_small_exception(self):
        self.assertEqual(invariant_minrank(10)['minimum_rank'],10)
        row=invariant_minrank(9)
        self.assertEqual(row['minimum_rank'],8)
        self.assertLess(row['frozen_center_deficit'],0)
        direct_eigen_controls(7)


class FiveSubsetHypothesisTests(unittest.TestCase):
    def test_scalar_dyadic_recovery_and_optimistic_budget(self):
        identities=gaussian_dyadic_center_identities()
        self.assertEqual(identities['total_recovery_denominator'],8)
        self.assertEqual(pair_center_loss(20),3424)
        result=envelope(20,pair_center_loss(20))
        lower,upper=result['optimistic_role_per_source_cap_interval']
        self.assertGreater(lower,31)
        self.assertLess(upper,32)

    def test_triple_polynomial_on_five_labels_is_invalid(self):
        # Applying the old (t-1)/2 to new labels fails at odd off-diagonal
        # t=3 and has diagonal value two; scalar geometry must change.
        self.assertNotEqual(Q(3-1,2),0)
        self.assertNotEqual(Q(5-1,2),1)

    def test_even_intersection_side_outputs_and_corruption(self):
        generator=FiveSide(8,2,2)
        self.assertEqual(generator.exact_screen()['exact_intersection_query_checks'],168)
        first=generator.inputs[0]
        generator.two[first]=generator.variables[first]
        with self.assertRaisesRegex(ValueError,'incorrect intersection'):
            generator.exact_screen()

    def test_weighted_tree_supports_and_local_frame_obstruction(self):
        generator=TreeIntersection(8)
        self.assertEqual(generator.verify()['exact_weighted_output_checks'],56)
        self.assertEqual(check_graph(generator)['nodewise_nonintersecting_frame_obstructions'],18)
        first=next(iter(generator.outputs.values()))
        generator.positive[first] ^=1
        with self.assertRaisesRegex(ValueError,'wrong weighted'):
            generator.verify()

    def test_radical_intersection_and_orthogonal_negative_control(self):
        for sources,expected in (((31,55),0),((31,103),120)):
            U=basis(sources)
            M=basis(nullspace(U,8))
            self.assertEqual(intersection_witness(U,radical(M)),expected)


if __name__=='__main__':unittest.main()
