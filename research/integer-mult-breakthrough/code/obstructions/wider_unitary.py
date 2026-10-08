#!/usr/bin/env python3
"""Replay an exact three-coordinate escape from the two-coordinate row lemma.

The macro is literally three paid Gaussian-dyadic balanced unitary gates.
No free macro cost, compressed tensor recurrence or multiplication gain follows.
"""
import json
from fractions import Fraction as Q

from unitary_dyadic import ALPHA, Gaussian, identity, require_unitary


def balanced(matrix, i, j):
    x,y = matrix[i],matrix[j]
    matrix[i] = [ALPHA*(a+b) for a,b in zip(x,y)]
    matrix[j] = [ALPHA*(a-b) for a,b in zip(x,y)]


def replay():
    matrix = identity(3)
    word = [(0,1),(0,2),(0,1)]
    for i,j in word:
        balanced(matrix,i,j)
        require_unitary(matrix)
    direct = [
        [Gaussian(Q(-1,4),Q(3,4)),Gaussian(Q(-1,4),Q(-1,4)),Gaussian(Q(0),Q(1,2))],
        [Gaussian(Q(-1,4),Q(-1,4)),Gaussian(Q(-1,4),Q(3,4)),Gaussian(Q(0),Q(1,2))],
        [Gaussian(Q(0),Q(1,2)),Gaussian(Q(0),Q(1,2)),Gaussian(Q(-1,2),Q(-1,2))]
    ]
    if matrix != direct:
        raise ValueError("Literal word differs from the direct target matrix")
    probabilities = [[str(a.norm2()) for a in row] for row in matrix]
    if probabilities[0] != ["5/8","1/8","1/4"]:
        raise ValueError("The advertised nonbalanced three-coordinate row is absent")
    return {"status":"EXACT FINITE CERTIFICATE", "word":[list(pair) for pair in word],
            "literal_two_coordinate_gates":len(word),
            "all_intermediate_matrices_unitary":True,
            "squared_coordinate_norms":probabilities,
            "matrix":[[[str(a.real),str(a.imag)] for a in row] for row in matrix],
            "scope":"Exact three-coordinate Gaussian-dyadic macro; no multiplication, phase-recursion or asymptotic transfer claim",
            "not_proved":["lower cost for the macro than its three literal gates",
                          "admissible compressed phase/rank child distribution",
                          "kappa improvement"]}


if __name__ == "__main__":
    print(json.dumps(replay(),indent=2))
