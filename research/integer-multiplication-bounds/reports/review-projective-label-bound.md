# Exact positive-ambient obstruction for rank-two triple labels

Positive ambient constructions cannot give rank-two labels in the small
dimensions currently sought. For the graph of triples adjacent when
their intersection has size one, a positive-definite real or complex
ambient space of dimension `M` carrying orthogonal rank-`r` planes at
adjacent vertices must satisfy

```text
M/r >= (h-1)(3h-14) / [2(2h-11)]     (h>=7).
```

For `h=24,r=2` this requires `M>=37`; for `h=50,r=2`, `M>=75`.
The obstruction does not apply to indefinite ambient forms. Requiring
each plane to be positive within an indefinite ambient space does not
restore the missing hypothesis. Therefore the parent's signature
`22+2` positive-plane search and `12+12` split-plane search at `h=24`
remain mathematically open.

## Exact adjacency eigenvalues

Let `A` be the adjacency matrix on all three-subsets of an `h`-set. Its
degree is `k=3 C(h-3,2)`. For each `j<=3`, span the functions
`f_R(S)=1{R subset S}` with `|R|=j`; these spaces form a nested flag,
ending at the full coordinate space for `j=3`.

If `r=|R intersect S|`, then the number of adjacent triples containing
`R` is zero for `r>1`. For `r=1` it is
`C(h-j-2,3-j)`. For `r=0,j<=2` it is
`3 C(h-3-j,2-j)`, and for `r=0,j=3` it is zero. Expand this function
of `r` in the basis `C(r,l)`; the coefficient at `l=j` is its `j`th
finite difference. All lower coefficients lie in the preceding flag
space. Consequently the four possible eigenvalues are

```text
k = 3 C(h-3,2),
lambda_1 = (h-9)(h-4)/2,
lambda_2 = -(2h-11),
lambda_3 = 3.
```

For `h>=7`, the least is `lambda_2`, since
`lambda_1-lambda_2=(h-7)(h-2)/2>=0`. It occurs: the nonzero function
`(1{a in S}-1{b in S})(1{c in S}-1{d in S})`, with four distinct
points, cancels all lower terms and is a `lambda_2` eigenvector.
For `h=6`, the least is instead `-3`; the resulting ratio bound is four.
Using the `h>=7` expression at `h=6` would give an invalid stronger bound.

The exact small checker verifies the annihilating polynomial and the
first four trace moments on all adjacency entries at `h=6,8`. Their
four distinct eigenvalues have multiplicities
`C(h,j)-C(h,j-1)`, with `j=0` multiplicity one. This verification uses
integer and rational arithmetic, with no numerical eigensolver.

## Positive projector argument

Let `P_S` be the ordinary orthogonal projector onto the rank-`r` plane
at vertex `S`. Put `Y_ST=Tr(P_S P_T)`. This is a positive semidefinite
Gram matrix in the Hilbert-Schmidt inner product, its diagonal is `r`,
and its edge entries vanish. Set `v=C(h,3)` and `ell=lambda_min<0`.
The adjacency eigenvalues imply that

```text
A - ell I - (k-ell) J/v
```

is positive semidefinite. The trace of its product with `Y` is nonnegative.
Since `Tr(AY)=0` and `Tr(Y)=vr`, this gives

```text
sum_ST Y_ST <= (-ell) v^2 r / (k-ell).
```

On the other hand, Cauchy-Schwarz applied to the positive semidefinite
matrix `sum_S P_S` gives
`sum_ST Y_ST=Tr((sum P_S)^2)>=(vr)^2/M`. Combining them yields
`M/r>=1-k/ell`, exactly the displayed bound. No restriction on
nonadjacent vertex pairs is used.

The projector Gram matrix is not guaranteed positive semidefinite for
an indefinite bilinear ambient form. That is the precise reason this
argument cannot rule out the campaign's indefinite-label hypotheses.
An unsuccessful floating search in those signatures is also not a
nonexistence certificate.

## Exact control, literature, and novelty scope

At `h=8` the bound is `M/r>=7`. Regard the eight points as `F_2^3`.
Each triple determines the unique nonzero binary normal annihilating
its two independent differences. This gives seven colors. Two affine
planes with the same normal either are disjoint or intersect in four
points; two three-subsets within one such plane intersect in at least
two points. Therefore triples meeting once have distinct colors.
Place a rank-two coordinate plane at each color, in dimension 14.
The independent checker verifies every edge of this exact control;
it attains the positive ambient lower bound and calibrates the parent's
numerical rank-14 tests.

The relevant established parameter is projective rank, equivalently
fractional orthogonal rank. The terminology and rank-`r` orthogonal
representation interface are described by Leslie Hogben, Kevin F.
Palmowski, David E. Roberson, and Simone Severini, *Orthogonal
Representations, Projective Rank, and Fractional Minimum Positive
Semidefinite Rank: Connections and New Directions*, arXiv
1502.00016v2, submitted 2015-09-02 (manuscript title-page date
2015-09-03), later *Electronic Journal of Linear Algebra* 32 (2017),
98-115. [Primary author manuscript](https://arxiv.org/abs/1502.00016v2).

Boris Bukh and Christopher Cox study this same intersection-one triple
graph `J_h^2` in *On a fractional version of Haemers' bound*, arXiv
1802.00476v2, 2018-12-13. Their characteristic-dependent Haemers
comparison and graph theta calculation show why a positive semidefinite
bound is a poor proxy for arbitrary-field or indefinite constructions.
[Primary author manuscript](https://arxiv.org/abs/1802.00476v2).

This report does not claim a new spectral bound. It derives the relevant
specialization explicitly and records its hypotheses, a dimension-six
exception, and exact controls for the current search. The two immutable
primary PDFs and hashes are recorded in the fresh review protocol.

Fresh evidence is in `runs/20261007T234629Z-review-projective-bound`.
Reproduce with standard-library Python:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/integer-multiplication-bounds/code/review_projective_bound.py \
  --output "$OUT"
```

Campaign interval remains 2026-10-07 22:25:21 UTC to
2026-10-08 08:25:21 UTC. No scalar circuit count or headline depends on
this lower bound.
