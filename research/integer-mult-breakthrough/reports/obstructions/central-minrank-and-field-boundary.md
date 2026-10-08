# Central completion rank and the characteristic-two boundary

Status: **SCOPED ANALYTICAL RANK BOUNDS WITH EXACT FINITE CONTROLS**.
No optimal completion, free data basis change or multiplication exponent is claimed.

## The shared-release question

For all k-subset labels, k=2d+1 odd, seek a central scalar matrix K with
K(T,T)=1 and K(T,U)=0 for distinct T,U with odd intersection. Then I-K is
supported only at orthogonal binary label pairs. Such a central bank could
release many diagonal coefficients jointly, avoiding an unjustified sum of
per-output cancellation penalties. The existing polynomial
f_k(t)=binom((t-1)/2,d) gives one completion of rank at most binom(h,d).
Changing its values at even intersections or breaking symmetry is allowed
by this question. Native phase geometry, dyadic inverses, dirty restoration
and all external data basis costs remain separate.

## A universal principal-minor lower bound

Fix one common coordinate and divide the other coordinates into q=floor((h-1)/2)
disjoint pairs. A label consists of the common coordinate and d chosen complete
pairs. Every label has weight k. Distinct labels have intersection
1+2j, where j<d, so every off-diagonal entry of the central matrix is forced
to zero. Its diagonal is one. The resulting principal submatrix is an identity
of order binom(q,d), over any field. Therefore every such completion has rank
at least binom(q,d), even without symmetry or positive semidefiniteness.

For fixed k and growing h, this is Omega(h^d). Broken symmetry cannot lower
the central feature order to h^(d-1) under these zero constraints. A constant
factor remains open: the ratio between the existing binom(h,d) upper bound
and this necessary lower bound tends to 2^d. At h20 k5 the bounds are 36 and
190. These are rank bounds, not physical role counts or child histograms.

The polynomial upper bound follows by expanding f in the Newton basis:
binom(|T intersect U|,j) is the Gram matrix of j-subset incidence. Every
j-incidence row for j<=d lies in the rational span of d-incidence rows,
because each contained j-feature has binom(k-j,d-j) supersets within T.
Thus all terms factor through at most binom(h,d) rational features. This
span argument does not supply a dyadic lattice inverse or a sparse paid
feature circuit.

## Why characteristic two gives a different bound

Define G to have even-intersection edges between distinct labels. A central
completion is a fitting matrix for G. Over F2, the matrix N(T,U)=|T intersect U|
modulo two fits the complementary odd-intersection graph: its diagonal is
one and its rank is at most h through binary point-incidence B^T B.

If M and N fit complementary graphs with nonzero diagonals, their entrywise
product is a nonsingular diagonal matrix. Factor each into rank-one terms;
their entrywise product has rank at most rank(M)rank(N). Consequently every
central fitting matrix over F2 has rank at least ceil(binom(h,k)/h).
The same lower bound applies to rational/Gaussian matrices integral at the
prime above two whose diagonal remains a unit on reduction: a nonzero reduced
minor is also a nonzero characteristic-zero minor.

At h20 k5, the characteristic-two bound is 776 while the rational polynomial
rank is at most 190. There is no contradiction. Dyadic entries such as 3/8
cannot be reduced modulo two. Clearing their power-of-two denominator makes
the diagonal zero, invalidating the fitting-matrix premise. Thus a lower bound
proved after unpaid reduction is inapplicable to the Gaussian-dyadic algorithm.
It also explains why precision and normalization costs cannot simply vanish
when a field-level feature compression is proposed. This is a representation
boundary, not a multiplication lower bound.

## Primary-source context and exact tests

Golovnev and Haviv's [published paper](https://theoryofcomputing.org/articles/v018a022/v018a022.pdf),
Theory of Computing18(22), 29 December2022, gives the fitting-matrix definition
in Definition1.8 and complement-product inequality in Fact3.9. Its Theorem3.2
concerns finite fields and threshold Kneser graphs. Our odd-intersection graph
has different zero constraints; that theorem is not imported as a Gaussian
primitive. The independent principal-minor construction above needs no such
transfer. The input manifest records the published PDF and its byte hash.

The [checker](../../code/obstructions/central_minrank_controls.py) imports no
producer. It checks the paired identity minors, all small polynomial entries
and ranks modulo101, and the binary complement rank. A nonzero minor modulo
an odd prime certifies a characteristic-zero lower bound because its denominators
are invertible there; the separate incidence argument supplies its upper bound.
Controls reject a forced off-diagonal corruption and undefined reduction at two.
Scaled dyadic kernels explicitly lose their diagonal units modulo two.

```sh
python3 -B research/integer-mult-breakthrough/code/obstructions/central_minrank_controls.py --workers 1 --bounded
```

The next discriminator is an actual dyadic invertible center/null-complement
basis with a favorable complete source/sink chronology. Rank alone neither
authorizes that basis change nor prices its internal guard. This analysis is
not formalized, and does not claim a new optimal minrank or external novelty.

The first four-worker run passed in 0.25 seconds. At h8/h10 k5,
modulo101 ranks 28/45 match the analytic feature bounds. Complete paired minors
include h20 k5 (36) and h24 k7 (165); their full entries are regenerated rather
than stored as a large matrix. The [protocol](../../runs/20261008T233150Z-central-minrank/protocol.json)
and [result](../../runs/20261008T233150Z-central-minrank/results/full.json) retain every setting and hash.

The complex agent independently accepted the paired principal minor, rational
feature-span upper and complementary-field rank proof. Its review explicitly
requires integrality at the Gaussian prime (1+i) and a surviving diagonal unit
for the characteristic-two transfer. It confirms that clearing dyadic
denominators removes that premise. This is internal team mathematical review,
not formal verification or external peer review.
