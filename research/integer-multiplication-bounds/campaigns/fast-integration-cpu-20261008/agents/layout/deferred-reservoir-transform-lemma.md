# A deferred-reservoir transform with equal main axes

Written 2026-10-08. This is a proposed all-size conditional transfer of the
pinned compact-control layer and coordinate-router constructions. It removes
two specific O(Vd) transform charges. It does not remove Gaussian movement or
by itself improve a complete multiplication exponent. A separate local source
review supports the exact commutation and dirty-bank interface; this is not
external human review or formal verification.

## Why the one-chunk layout alone retains an O(Vd) charge

For E equal main axes of K-bit width, the compact layer chooses

`G=4 ceil(log2(p))+6`, `H=dG`,
`qF=ceil(2H/K)`, `qB=ceil(H/K)`,
`q0=ceil(log2(W)) ceil(log_m(2d))`.

The old schedule applies each selected kernel individually on the first
q0+qF and last qB axes at EVERY transform round. With K=ell, summing over
ell rounds costs `O(V ell*(q0+dG/K))`, which contains `O(VdG)`. The reservation
inequality `1-c<lambda_prime`, when K has exponent c relative to d, consequently
recovers `epsilon<1/(2-lambda_prime)=1/(1+q)` for q=1-lambda_prime. Merely
deleting a top-bit prefix does not remove this obstruction.

## Generalized box and polynomial suffix

Choose ell first and set `d=floor(N/ell)`, `h=N-d ell` for the scalar padded
address length N, so `N=d ell+h`, `0<=h<ell`. Choosing d first instead would
give a different remainder bound and is not the construction here.
Use E=d-1 transformed main axes of length `t=2^ell` and one polynomial suffix
`r=2^(ell+h)`. Their total scalar volume is exactly `T=2^N`.
There are no differing main-axis top bits. All main axes divide2r; their
synthetic Fourier root is `y^(2r/t)` in `C[y]/(y^r+1)`.

This generalizes the original `t_i in {r/2,r}` promise while retaining
`log2(r)/2<=log2(t_i)<=log2(r)`. Thus the minimum scalar axis length is at
least sqrt(r), still superpolynomial in precision for fixed epsilon<1 and
any fixed polynomial precision in log n. Prime searches, offset setup and
online coefficient descriptors must use that changed minimum explicitly.

The last coefficient axis is already a contiguous polynomial record. The twist
`f_k -> exp(pi*i*k/r)*f_k`, ring product and inverse twist implement cyclic
suffix convolution exactly. Inherited normalized ring products cost
`O(V log(rp))`; since log r<2ell they retain exponent margin epsilon.

## The external-field layer interface

The physical compiled layer operates on a supplied consecutive set of selected
axes, with a complete leading row range of at least `W^ceil(log_m(d))`, two
complete H-bit front fields and one complete H-bit back field. Extra fields
are spectators. The row region is disjoint from all three dirty work fields.
At return the layer is the desired normalized selected-axis tensor C and the
identity on every row/bank/spectator coordinate.

This interface is justified by the pinned compact-control-layout proof: roles
split only the row coordinate; every role retains the identical complete
within-row field space; all compact updates restore the dirty fields before
each scalar or recursive call; final row restoration returns every original
row. The old proof mentions previously performed individual kernels only to
state that they commute with this completed identity. It does not require those
kernels as a precondition for dirty bank use.

For the proposed second group, supply the row and work fields from OUTSIDE its
selected axes. Do not reserve and individually process another subset of the
second group. This is the changed external-field transfer; applying the old
black-box theorem while omitting its reservation cost would be invalid.

Keep the same global d,K,H and stopping threshold for both groups. The inherited
volume-weighted recurrence bound on any selected width e<=d is
`O(V d^lambda_prime polylog(p))` whenever the internal moment, leaf and strict
recurrence inequalities hold. The old reservation exponent is absent because
all work fields are separately supplied. Bank allocation, padding, parking and
clearing still cost their actual stream volumes.

## Two complete groups, rather than reservations at every round

Let B consist of the first q0+qF and last qB complete main axes, and let A be
the remaining consecutive middle group. For eventual K/log(p)->infinity,

`|B|/E = O(log(d)/d + G/K) -> 0`.

Initially B supplies the old complete row and front/back fields. Apply the FULL
normalized synthetic transforms on A across all ell levels, leaving B untouched.
This costs `O(V ell d^lambda_prime polylog(p))` and requires no individual B
kernels at those levels.

Now route named main-axis bits once so that B becomes a consecutive active
middle group and complete fields taken from A supply the row and dirty banks.
There are enough A fields: the required donor count is at most
`q0+qF+qB=|B|=o(E)`, while |A|=E-|B|. Whole axes can be used as donors;
carving their bits into H-bit fields is a descriptor interpretation and not
a payload movement. Extra donor bits and all remaining A coordinates are
complete spectators. The polynomial suffix remains contiguous and untouched.

Apply the FULL B transforms, using the external-field layer interface, then
undo that known coordinate route. A's address fields now contain frequency
bits; they still form complete independent binary cubes and may be arbitrarily
dirty. Their Fourier values are payloads, so using their coordinates as row or
work fields requires no supposition that the payload is zero or untransformed.

Both coordinate routes are paid by the pinned arbitrary-coordinate router on
the complete main-axis rectangle with its superpolynomial polynomial suffix.
Their total cost is `O(V N^tau polylog(p))`, plus explicit polynomial setup.
No full-coordinate route is called at every Fourier level.

Temporary zero-row padding increases the current stream volume by at most2.
It is removed after each completed layer before the next layer, so it does not
accumulate a factor2^(number of layers). A fixed set of native control, recursion
and router tapes is reused for both groups.

## Algebra, rounding and multiplication alignment

Every axis's exact twiddle depends only on that axis's still-unprocessed input
bits. Different axes' exact butterflies and twiddles commute. Thus the exact
full A and B group transforms compose to the original full main-axis Fourier
transform. Bit-reversal frequency significance is preserved for each named axis.

Component truncations Q_p need not commute. The valid error argument uses
contractions: each completed group level is a normalized tensor butterfly
followed by monomial isometries and one component truncation, so error is
propagated with norm at most1. At most2ell levels give error at most
`2 sqrt(2) ell 2^-p` under the inherited per-completed-layer exactness/precision
contract. The full A and B exact group transforms are contractions as well.
The opposite schedule reverses group order, reverses the same paid route, and
has the same additive error estimate. This is a fixed-factor change to the
transform error, not a new depth exponent or a claim that Q_p commutes.

For BOTH multiplicands use the same physical forward schedule. After routing
is undone, frequency entry j lies in the original named slot rev_ell(j) of
each main axis. Pointwise ring products therefore align identical frequencies.
The opposite transform returns the scalar box through the same polynomial
suffix. Its convolution normalization remains1/T: M=T/r main records,
normalized forward/opposite transforms, pointwise division by r, and the
existing exact factor M after the opposite transform.

The resulting proposed transform/product cost is

`O(V [ell d^lambda_prime + N^tau + log(rp)] polylog(p))`.

There is no top-bit prefix or per-level individual-reservation term. This can
approach a native primitive saving as epsilon approaches1, provided another
construction removes the separate O(Vd) Gaussian exposure/application cost.
No new complete kappa is promoted here.

## Independent finite interface control

[check_wide_polynomial_axis.py](code/check_wide_polynomial_axis.py) imports no
historical/public producer or checker. It computes exact normalized DIF
synthetic transforms and the reverse schedule over rational polynomials in
formal zeta with zeta^r=-1. It compares stored frequencies against an independently
computed direct character formula, then compares the whole product with direct
scalar tensor cyclic convolution. Suffix-end inputs force wrap signs to matter.

[The result](results/wide-axis-operators.json) passes15 shapes in2/3/4 scalar
dimensions,5068 scalar output coefficients and1897 nonzero formal Fourier terms.
Cases include h>1 and root exponent2r/t>2, beyond the old r/2 versus r promise.
Input fixtures have random sparse dyadic values plus forced wrap terms; this is
not an exhaustive matrix-column test at every size. Omitting the coefficient
twist gives a retained explicit wrong-sign last-axis wrap.

The source review is [the scout's independently read contract review](../scout/deferred-reservoir-review.md).
Remaining obligations are a complete compiled external-field machine review,
changed prime/assembly inequalities and final scalar error constants. Those
should be completed before claiming a complete multiplication bound.

## Adversarial audit of the second group's external row fields

Rechecked against the pinned compact-control-layout proof at13:55 UTC.
For group B choose disjoint donor sets from A: q0 whole axes for ROW,
qF for FRONT, qB for BACK; all remaining A axes are spectators. The ONE
paid exchange route writes fields in the following explicit order:

`[ROW][FRONT1(H)][FRONT2(H)][front remainder][B active axes][BACK(H)][back remainder][spectators][polynomial suffix]`.

Whole donor axes have K bits; `qF K>=2H`, `qB K>=H`, and each unused remainder
is a complete spectator range. The front/back bits NEVER enter the row index.
Every A frequency address occurs, including both values of every donated
bit, because a Fourier transform changes payloads, not the physical address
set. Frequency interpretation therefore changes neither row cardinality nor
the fixed-tape basis placement. It also supplies no assertion that a donor
payload is zero; arbitrary dirty payload is explicitly allowed.

Let `R_row=2^(q0 K)` and `k0=ceil(log_m d)`. Use
`R_pad=W^k0 ceil(R_row/W^k0)`. Since R_row>=W^k0,
`R_pad<2 R_row`. Append complete zero rows, with exactly the same FRONT,
B, BACK, spectator and polynomial suffix shape, BEFORE the first role split.
At depth j the remaining row cardinality is divisible by W^(k0-j).
Split its row number u=Wg+w. Aligned coefficient gates use the same g and
within-row coordinates on every role. At every completed invocation the
row permutation and all compact fields are restored; the resulting operator
is identity on each external row. Thus the padded rows are zero on return
even though they may contain nonzero scratch payload while a call is active.
Delete ONLY those restored rows; carry neither padding nor a role permutation
to the next Fourier level. This pays a current volume below2V per invocation,
not2 raised to the number of Fourier levels.

For any base-m piece smaller than d^beta, the fallback processes its own
selected axes individually using the EXTERNAL banks; it does not reserve
more selected axes. Its cost is O(Vd^beta), absorbed by the supplied strict
leaf exponent. Intermediate exact arithmetic uses p=Q and the SAME global
d guard; each completed level returns to the Q grid and disk before the
next one. Long precision does not change m,W or require a rebuilt row basis.

This audit found no new divisibility or transformed-frequency counterexample.
It is a direct adaptation of the pinned physical proof with separately supplied
fields, and remains conditional on that proof's primitive row, guard and
restoration contracts. It is not a machine execution at the asymptotic cutoff.

## Reproduction and provenance

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B \
 research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/agents/layout/code/check_wide_polynomial_axis.py \
 --workers 4 --output research/integer-multiplication-bounds/campaigns/fast-integration-cpu-20261008/work/layout/fresh-wide-axis
```

Python3.14.4 standard library. The source digest, seeds and row results are in
the compact certificate. Native inputs are CrocSwap PR37, head
`cb86e50e9a07685068874d8e4174b2e6c209b95c`, compact-control-layout.tex and upstream
06-transforms/08-assembly; the public Swapnil one-chunk idea at
`c2c2f279d93643e5ff3fe121a0fbc68e0e6f4007`; and historical RaD arbitrary routing
at `6b32837aee0561af85e4efaca21af07b9f2749d2`. The wide suffix and deferred whole
reservoir-axis transforms are campaign-derived mechanisms. No worldwide novelty
or formal verification claim is made.
