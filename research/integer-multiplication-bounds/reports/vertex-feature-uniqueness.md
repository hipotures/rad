# Rational vertex-feature uniqueness and calibrated pair features

This is a scoped algebraic restriction and a search calibration, not a
new multiplication theorem. Let triples index the vertices of the
intersection-one graph. The campaign fitting map has diagonal one and
vanishes when two triples intersect in exactly one point; in the usual
Haemers convention it fits the complement of that graph.

## Vertex-feature columns are forced

Suppose `h >= 6`, work over the rationals, and require a fixed target
column to have the form

    M(S,T) = sum(i in S) z_i(T).

Fix a target triple `T`. Its complement has at least three points. For
every `i in T` and distinct `a,b outside T`, the zero condition gives
`z_i + z_a + z_b = 0`. Comparing pairs `(a,b)` and `(a,c)` shows that
all outside coordinates are one common value `u`. Each inside coordinate
is therefore `-2u`. The diagonal condition gives `-6u=1`. Thus

    z_i(T) = 1/3 inside T, and -1/6 outside T,
    M(S,T) = (|S intersect T| - 1)/2.

No symmetry, bilinear representation, or shared coefficient choice across
columns was assumed. This proves uniqueness throughout the vertex-column
ansatz. It does not prove uniqueness in the larger pair-feature ansatz.
The argument uses division by six and is not a characteristic-two proof.

Let `A` be the triple-to-point incidence matrix. Its columns have rank
`h`: differences of triples give every `e_i-e_j`, and any triple row has
nonzero sum. The unique map is

    M = A (I - J/9) A^T / 2.

Consequently its rational rank is `h`, except at `h=9`, where it is `8`.
The bounded exact checker verifies full constraint rank and consistency
at grounds 6 through 12, and independently computes the complete fitting
matrix ranks at 6, 8 and 9.

## A specific binary extension fails at h16

At h8, identify points with `F2^3`. Each triple has a unique nonzero
normal annihilating its two differences. For each normal `n`, assign a
pair coefficient `1/3` when the normal bits of the endpoints agree, and
`-1/6` otherwise. The triangle sum is the indicator that its three normal
bits agree. These seven columns yield the exact known rank-seven control.
The independent checker verifies every diagonal and all 840 undirected
intersection-one edges; a seven-triple Fano clique gives a matching rank
lower bound. See the [literature and exact fixture review](review-haemers-pair-features.md).

One tempting extension at h16 uses the fifteen nonzero normals of `F2^4`
as the same fixed source features. For target `(0,1,2)`, the 234 adjacent
source rows have exact rational rank 15. Adding the target row leaves the
rank 15. Hence no linear target coefficients in this particular source
row space can vanish on every required edge while giving a nonzero
diagonal. At h8 those ranks are respectively 6 and 7, as expected.
This excludes this fixed XOR/normal row space at h16; it does not exclude
general rank-fifteen pair-feature maps or other label constructions.

## The h9 quotient does not repair the retained deficit

At h9 the Hessian `I-J/9` has the all-ones kernel. The triple vectors
project to nonzero vectors in the positive eight-dimensional quotient;
the singular ambient space alone is therefore not a universal geometric
obstruction. In an optimistic count screen retaining the existing motif
layout, even the product `ground * ambient = 9*8` is too large relative
to the 84 triples. The uniform deficit divided by `N` would be
`1-6*72/84 = -29/7`. One middle h9 axis alone contributes a deficit loss
`2*72/84 = 12/7`, already exceeding one. An outer h9 factor contributes
`4*72/84 = 24/7`.

This is a count screen for the retained layout, not a completed quotient
transfer argument or a bound on every possible h9 construction. No new
algorithmic claim follows from the quotient observation.

## Reproduction

Run the standard-library checker with a fresh output path:

```bash
python3 -B research/integer-multiplication-bounds/code/vertex_feature_uniqueness.py \
  --output "$FRESH_OUTPUT"
```

The terminal run is `20261008T001749Z-vertex-feature-controls`. Its exact
source hash, interpreter command, field, grounds and measured resource
record are retained in its protocol. The all-size vertex proof above is
the mathematical justification; finite rank checks supplement it.
