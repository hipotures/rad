#!/usr/bin/env python3
"""Bounded exact and corruption controls for the full-frame component."""
from itertools import product
import unittest

from lagrangian_gate_witness import (ZERO,ONE,add,apply_column,compile_edge,
                                    compose,graph_operator,hadamard_dyadic,
                                    inverse,reconstruct_edge)
from lagrangian_phase_screen import all_lagrangians,basis,distance,graph_frames


class LagrangianControls(unittest.TestCase):
    def test_complete_frame_counts_and_chart_gap(self):
        self.assertEqual(len(all_lagrangians(2)),15)
        full=all_lagrangians(3);graphs=graph_frames(3);codes=(3,23,35,56)
        cost=lambda lag:sum(distance(lag,graphs[c],3) for c in codes)
        self.assertEqual(len(full),135);self.assertEqual(len(graphs),64)
        self.assertEqual(min(map(cost,full)),5);self.assertEqual(min(map(cost,graphs)),6)
        self.assertEqual([lag for lag in full if cost(lag)==5],[(32,19,10)])

    def test_all_four_incident_operators_and_corrupted_chirp(self):
        frames=[graph_operator(c) for c in (3,23,35,56)]
        common=compose(frames[0],hadamard_dyadic(2))
        edges=[compose(common,inverse(frames[0])),compose(common,inverse(frames[1])),
               compose(frames[2],inverse(common)),compose(frames[3],inverse(common))]
        compiled=[compile_edge(edge) for edge in edges]
        self.assertEqual([nf['rank'] for nf in compiled],[1,1,1,2])
        for nf,edge in zip(compiled,edges):self.assertEqual(reconstruct_edge(nf),edge)
        compiled[0]['input_phase_exponents'][0] ^=1
        self.assertNotEqual(reconstruct_edge(compiled[0]),edges[0])

    def test_full_two_role_input_basis(self):
        frames=[graph_operator(c) for c in (3,23,35,56)]
        common=compose(frames[0],hadamard_dyadic(2))
        edges=[compose(common,inverse(frames[0])),compose(common,inverse(frames[1])),
               compose(frames[2],inverse(common)),compose(frames[3],inverse(common))]
        for role,address in product(range(2),range(8)):
            data=[[ZERO]*8 for _ in range(2)];data[role][address]=ONE;x,y=data
            ux=apply_column(inverse(frames[0]),x,[0,1,2]);uy=apply_column(inverse(frames[1]),y,[0,1,2])
            expectedx=apply_column(frames[2],ux,[0,1,2]);expectedy=apply_column(frames[3],[add(a,b) for a,b in zip(uy,ux)],[0,1,2])
            ax=apply_column(edges[0],x,[0,1,2]);ay=apply_column(edges[1],y,[0,1,2]);ay=[add(a,b) for a,b in zip(ay,ax)]
            self.assertEqual((apply_column(edges[2],ax,[0,1,2]),apply_column(edges[3],ay,[0,1,2])),(expectedx,expectedy))

    def test_selected_fields_preserve_spectators(self):
        matrix=hadamard_dyadic(2);data=[ZERO]*64;data[1]=ONE
        # Odd physical addresses differ only in an unselected spectator bit.
        out=apply_column(matrix,data,[1,3,5])
        self.assertTrue(all(z==ZERO for j,z in enumerate(out) if not j&1))
        self.assertEqual(apply_column(inverse(matrix),out,[1,3,5]),data)

    def test_basis_canonicalization(self):
        self.assertEqual(basis((32,19,10)),basis((51,25,10)))


if __name__=='__main__':unittest.main()
