#!/usr/bin/env python3
"""Bounded exact controls for degenerate helper-frame interfaces."""
from copy import deepcopy
from fractions import Fraction
import unittest

from degenerate_frame_geodesics import (all_subspaces,branching_certificate,
    check_pair,lagrangian,perpendicular)
from degenerate_branching_component import (N,SIZE,common_frame,compile_edge,
    reconstruct_edge,full_c,schedule,execute,c_line)
from lagrangian_gate_witness import ZERO,ONE,compose,inverse,identity
from lagrangian_phase_screen import all_lagrangians,basis,distance


class DegenerateFrameTests(unittest.TestCase):
    def test_all_small_subspace_distances(self):
        spaces=all_subspaces(3)
        self.assertEqual(len(spaces),16)
        for E in spaces:
            for F in spaces:check_pair(E,F,3)

    def test_all_shortest_frames_are_subspace_embeddings(self):
        n=3;zero=lagrangian((),n);full=lagrangian((1,2,4),n)
        geodesic={L for L in all_lagrangians(n)
                  if distance(zero,L,n)+distance(L,full,n)==n}
        embedded={lagrangian(E,n) for E in all_subspaces(n)}
        self.assertEqual(geodesic,embedded)
        self.assertEqual(len(geodesic),16)
        for E in all_subspaces(n):
            for F in all_subspaces(n):
                path=distance(zero,lagrangian(E,n),n)+distance(lagrangian(E,n),lagrangian(F,n),n)+distance(lagrangian(F,n),full,n)
                self.assertEqual(path==n,len(basis(E+F))==len(F))

    def test_complete_branching_rank_ledger(self):
        certificate=branching_certificate()
        self.assertEqual(certificate['forward_total_rank'],12)
        self.assertEqual(certificate['all_symmetric_graph_minimum'],14)
        self.assertEqual(certificate['graph_assignment_count'],1048576)

    def test_actual_phase_normal_forms_both_orientations(self):
        for reverse in (False,True):
            spec=schedule(reverse,-1 if reverse else 1)
            self.assertEqual(sum(e['normal_form']['rank'] for e in spec['edges'] if e['auxiliary']),12)
            self.assertEqual(sum(e['normal_form']['rank'] for e in spec['edges'] if not e['auxiliary']),12)
            for edge in spec['edges']:
                A=reconstruct_edge(edge['normal_form'])
                self.assertEqual(compile_edge(A)['rank'],edge['normal_form']['rank'])
                self.assertEqual(compose(A,inverse(A)),identity(SIZE))
            self.assertNotEqual(compose(common_frame(False),common_frame(True)),full_c())

    def test_all_dirty_basis_inputs(self):
        spec=schedule();roles=list(spec['initial_frames'])
        for active_role in roles:
            for address in range(SIZE):
                initial={role:[ONE if role==active_role and j==address else ZERO for j in range(SIZE)] for role in roles}
                observed=execute(spec,initial,1,1,0)
                self.assertEqual(execute(spec,observed,1,1,0,True),initial)

    def test_corrupt_normal_form_and_retirement(self):
        spec=schedule();initial={role:[(Fraction(j+1),Fraction(2*j-3)) for j in range(SIZE)] for role in spec['initial_frames']}
        correct=execute(spec,initial,1,1,0)
        bad=deepcopy(spec);bad['edges'][0]['normal_form']['input_phase_exponents'][1]=(bad['edges'][0]['normal_form']['input_phase_exponents'][1]+1)%4
        self.assertNotEqual(execute(bad,initial,1,1,0),correct)
        bad=deepcopy(spec);bad['events']=[event for event in spec['events']
                                       if not(event[0]=='move' and spec['edges'][event[2]]['role']=='b' and spec['edges'][event[2]]['after']=='full')]
        self.assertNotEqual(execute(bad,initial,1,1,0),correct)

    def test_per_output_cancellation_common_frame_bound(self):
        n=3;full=lagrangian((1,2,4),n);line=lagrangian((7,),n)
        kernel=lagrangian(perpendicular((7,),n),n)
        costs=[distance(line,L,n)+2*distance(full,L,n)+distance(L,kernel,n)
               for L in all_lagrangians(n)]
        self.assertEqual(min(costs),n)


if __name__=='__main__':unittest.main()
