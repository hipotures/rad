# Graph orientation and an exact rank-seven pair-feature control

Bukh--Cox Lemma 12 does not settle the rational or real minimum rank
of the campaign's intersection-one zero pattern. Its graph is the
intersection-one graph itself, but its fitting matrices vanish on the
graph's nonedges. Our matrices vanish on the edges and therefore fit
the complement. The known `h=8` rank-seven control is nevertheless
available inside the pure degree-two pair-feature span, giving an exact
calibration for the parent's current feature search.

Campaign clock: 2026-10-07 22:25:21 UTC to 2026-10-08 08:25:21 UTC.
Reference: `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

## What the primary lemma says

Boris Bukh and Christopher Cox, *On a fractional version of Haemers'
bound*, arXiv:1802.00476v2, submitted 2018-12-13 01:31:26 UTC, Lemma 12
on printed pages 8-9, defines `J_h^p` on `(p+1)`-subsets, with distinct
vertices adjacent when their intersection is nonzero modulo `p`.
For `p=2`, this is exactly the triple intersection-one graph `G_h`.
Its ordinary Haemers number is `h` in characteristic two when `4` divides
`h`, matching its independence number. The fractional value is then
also `h`, by the independence lower bound. Lemma 12 also gives the
theta asymptotic `2h^2/9` and records the corrected exact expression
`h(h-2)(2h-11)/(3(3h-14))` for this graph.
[Primary author manuscript](https://arxiv.org/abs/1802.00476v2).

Their convention requires a nonzero diagonal and zero entries at
nonadjacent pairs. The incidence Gram matrix in characteristic two has
diagonal one, is nonzero at intersection one, and vanishes at
intersection zero or two. It fits `G_h`. The campaign's rational matrix
`|S intersect T|-1` has diagonal two and vanishes at intersection one.
It fits `complement(G_h)`. Interchanging these two graphs reverses the
zero pattern and invalidates the intended inference.

The lemma states no exact real/rational ordinary or fractional Haemers
number for `complement(G_h)`. Its independence lower bound on `G_h`
also holds over other fields, but is about the other fitting problem.
The theta value is not a lower bound on arbitrary indefinite fitting
rank; the point of the paper includes comparing parameters that need
not coincide. Consequently the lemma does not exclude the parent's
rank-23 rational/real search at `h=24`.

## Independently derived bounds for the actual zero pattern

A clique of `G_h` forces mutually orthogonal nondegenerate labels, or
an invertible block diagonal submatrix in an arbitrary fitting matrix.
Seven Fano triples form a clique whenever `h>=7`. A sunflower
`{0,2j+1,2j+2}` supplies a clique of size `floor((h-1)/2)`.
These are constructed cliques; no maximum-clique claim is needed.

The rational vertex Gram matrix `Q(I-J/9)Q^T` has rank `h`, except
rank `h-1` at `h=9`, and supplies the explicit upper bound. Thus,
without imposing positivity, the elementary bounds at `h=24` are

```text
11 <= H_f(complement(G_24);Q) <= H(complement(G_24);Q) <= 24.
```

At `h=9`, the current elementary interval is seven through eight.
The positive symmetric ambient model requires dimension at least eight
and the vertex construction attains eight; this does not exclude an
indefinite or nonsymmetric rank-seven fitting matrix. At `h=24`, the
positive symmetric rank-one bound is 19, as proved in
[the exact projector audit](review-projective-label-bound.md). This is
also below 23. Failed numerical caps are not evidence of a stronger
lower bound.

There is a genuine characteristic-two obstruction for the complement
problem. Let `A` be the triple incidence Gram matrix modulo two, of
rank at most `h`, and let `M` be a rank-`r` block fitting matrix with
invertible `k`-by-`k` diagonal blocks and zeros at intersection one.
Blockwise multiplication by `A` leaves only those diagonal blocks.
Factoring `A` into at most `h` outer products shows

```text
C(h,3)*k <= h*rank(M).
```

Thus the ambient rank per block rank is at least `C(h,3)/h`, equal to
`253/3` at `h=24`. This rules out a characteristic-two rank-23 scalar
fitting matrix and rational models that reduce regularly modulo two
with an invertible diagonal. It does not rule out rational models with
essential denominators or degenerate reduction at two. The original
vertex Gram diagonal is two, illustrating the exception.

## Exact eight-point degree-two construction

Index the eight ground points by `F_2^3`. A triple has two independent
binary differences, and hence a unique nonzero normal `n` annihilating
both. Its normal is a proper seven-coloring of the intersection-one
graph. Let `ell_n(i)` be the binary dot product of `n` and point `i`,
and put `k=sum_{i in T} ell_n(i)`. The corresponding color indicator is

```text
f_n(T) = 1-k+C(k,2).
```

For `k=0,3` it is one; for `k=1,2` it is zero. It is already a
constant-plus-point-plus-pair polynomial. On three-subsets the constant
and point terms also lie in the pure pair incidence span: each triple
contains three pairs, and each selected point occurs in two of them.
Therefore

```text
f_n(T) = sum_{pairs {a,b} subset T}
         [1/3-(ell_n(a)+ell_n(b))/2+ell_n(a)*ell_n(b)].
```

The pair coefficient is `1/3` for equal binary signs and `-1/6` for
different signs. Let `P` be the triple-by-pair incidence matrix and
let `C` be this 28-by-7 coefficient matrix. Then `F=PC` consists
of the seven disjoint color indicators, each supported on eight triples.
The matrix `FF^T` is rational, positive semidefinite, has rank seven,
diagonal one, and zeros at all intersection-one pairs. The Fano
seven-clique supplies the matching lower bound. Thus both ordinary and
fractional Haemers values of `complement(G_8)` over the rationals are
exactly seven.

This demonstrates that a degree-three feature is not required for the
known `h=8` control. A search over pure pair features can be initialized
with `C` and positive metric `I_7`, reaching zero residual immediately.
It is a calibration, not a construction at `h=24`. The current failure
of random rank-seven pair-feature starts should be interpreted as a
search failure in a model known to contain the control.

## Evidence and reproduction

[review_pair_feature_control.py](../code/review_pair_feature_control.py)
independently forms the pair coefficient matrix, checks its rational
rank, multiplies it by incidence, checks all 840 edge zeros and verifies
the Fano lower bound. The compact result includes the full small 28-by-7
coefficient fixture, with pair row names and normal column names.

Fresh protocol/result:
`runs/20261008T001048Z-review-haemers-pair-features`.
The primary PDF revision, immutable external path, byte size and SHA-256
are recorded there. Executed interpreter: CPython 3.14.4.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/integer-multiplication-bounds/code/review_pair_feature_control.py \
  --output "$OUT"
```

The report distinguishes source claims from the independently derived
complement bounds and the explicit small control. No new general
minimum-rank theorem or broad novelty claim is made.
