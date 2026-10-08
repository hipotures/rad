# A valid four-subset scalar replacement and its scoped ceiling

The four-subset E1 correction does not supply the triple scalar identity.
A distinct valid replacement uses intersections zero and two. It still
cannot beat the accepted bit primitive in the retained three-stage
incidence-center schedule, even with free side roles. This result includes
all rational intersection-invariant fitting values for this root set,
rather than only one guessed polynomial.

Write E_i for exact intersection i between four-subsets, and A_1 for
point incidence. Over the scalar bit domain F2,

```
I + E_0 + E_2 = J + A_1 A_1^T.
```

Both sides equal one at even intersections, including the diagonal
intersection four. Rational pair-incidence labels realize the minimum
degree fitting polynomial `P(i)=i(i-2)`: it vanishes at zero and two and
has nonzero norm P(4)=8. If B is four-subset/pair incidence and A is
point/pair incidence, then the label form on pair coordinates is
`2I-A^T A/9`, because `B A^T=3 A_1`. Its ambient dimension is binom(h,2),
except for the possible quotient at its two singular grounds h=10 and20.
This is a valid scalar alternative to E1, not a transfer of an E1 circuit.

The incidence representation has a constant center and h point centers.
The new point increments sum to zero in F2 because each input has four
members. Eliminating point zero therefore leaves one constant center and
h-1 point centers. At a target S, center i's reduced scatter coefficient
is `1_(i in S)+1_(0 in S)`. Dirty initial center values need not satisfy
the relation: early and late cancellation uses only their new increments.
This report retains this incidence/one-channel-elimination schedule.

Normalize P(4)=1. All rational intersection-invariant fitting matrices
with P(0)=P(2)=0 are described by the two rational values A=P(1), B=P(3).
Their Newton incidence coefficients are

```
(c0,c1,c2,c3,c4) = (0,A,-2A,3A+B,1-4A-4B).
```

For k-subsets of an n-set, the r-incidence Gram acts on the harmonic
j-subset space by

```
mu_(r,j) = C(k-j,r-j) C(n-r-j,k-r), j<=r;
mu_(r,j) = 0, j>r.
```

The space has dimension `C(n,j)-C(n,j-1)`, for
`j<=min(k,n-k)`. One elementary construction uses the balanced products
`prod_i(1_(a_i in S)-1_(b_i in S))` on disjoint point pairs. Summing
inclusions gives the displayed action; their lifts give the orthogonal
harmonic decomposition of the complete slice. Thus the fitting rank is
the sum of these multiplicities for its nonzero eigenvalues. The checker
independently evaluates the inclusion action on actual complete slices.

For a remaining point center, its scatter includes all targets containing
that point and omitting point zero. These are three-subsets of an
(h-2)-set after fixing the point. Their fitting values are
`(A,0,B,1)`, with Newton coefficients `(A,-A,A+B,1-A-3B)`.
Let q be their Gram rank and r the complete fitting rank. The constant
center sees all target labels and the other h-1 centers each see at least
this restricted star. The closed symmetric projection-path argument from
the [pair-star screen](downstream-pair-star-central-negative.md) gives

```
minimum local center loss >= r+(h-1)q.
```

The same argument applies to an indefinite rational label form F: multiply
each F-selfadjoint projection difference by F to obtain symmetric matrices
of the same ranks. The target Gram rank lower-bounds the span dimension.
As before, target frames stay in their final kernels during scatter, and
the center path starts and ends at the full gather frame. Changing those
conditions or the central scalar basis requires a new audit.

With v=binom(h,4), the optimistic bit deficit per v^2 is therefore at most
`v-6[r+(h-1)q]`. The global and star eigenvalues are affine functions of
(A,B). Their ranks are constant on the open plane, open eigenvalue-zero
lines, and their intersections. Exact representatives of every such
stratum cover all rational parameters. At h=5 through22 all 662 retained
rank strata have nonpositive optimistic deficit. This is a finite symbolic
case split, not a floating parameter search.

There is also an all-size tail bound. For h>=9, at least one degree-two,
three or four harmonic eigenvalue is nonzero: otherwise the triangular
incidence formula forces c4=c3=c2=0, and then A=B=0 contradicts c4=1.
Each of these harmonic multiplicities is at least `C(h,2)-h`. Hence
r>=C(h,2)-h for every fitting choice, regardless of center losses. For
h>=23 this gives r>=230. Even granting W=2N and zero center loss,
the relative rank deficit is at most eta=1/(2r^3). Since
`log(r^3)>2 floor(log2 r)`, using log2>2/3 and
`-log(1-eta)<=eta/(1-eta)` gives

```
primitive saving < 1/[14(2*230^3-1)]
                 = 1/340675986
                 < 3/10^9
                 < accepted bit saving.
```

Actual side roles and nondegeneracy restrictions only worsen this
optimistic ceiling. It excludes this root0/2 fitting family and retained
central schedule. It does not exclude other intersection root sets,
noninvariant labels, a different central scalar factorization, altered
target chronology, or a different movement algorithm.

The fresh run also passed 22,251 complete F2 scalar entries and 6,911
exact harmonic inclusion entries on small slices. No large finite graph,
E1/A3 discriminator, or degree-two five-subset experiment was replayed.
Source: [downstream_subset4_polynomial_screen.py](../code/downstream_subset4_polynomial_screen.py).
Run: [20261008T041949Z-downstream-subset4-polynomial](../runs/20261008T041949Z-downstream-subset4-polynomial/).
It took 0.473 seconds on one admitted worker, released after completion.
Immutable accepted R472879 semantic/bulk arithmetic supplies the strict
comparison saving. Campaign start and historical deadline are retained;
the authorized deadline is 2026-10-08T10:00:00Z. No stronger primitive,
kappa, or novelty claim is made.
