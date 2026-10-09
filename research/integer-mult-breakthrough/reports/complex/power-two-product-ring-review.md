# Independent review of the power-two product-ring boundary

Status: **ACCEPTED ANALYTICAL SCOPE REVIEW**. This is an independent
internal mathematical review of the transfer track's all-size algebraic
argument and positive exception. It does not rerun the producer's full CRT
controls, certify their native execution or establish an exponent.

Reviewed on 2026-10-09 UTC: [the report](../transfers/bilinear-ring-packing-boundary.md),
SHA-256 `94c4560e5257109f3ab6518396550ae418e5cd8d092ae7b9765b19197f443336`,
and [power_two_ring_capacity.py](../../code/transfers/power_two_ring_capacity.py),
SHA-256 `7a29ed784283dbf29c1f9d41b800789152f1f4416f626fa2822c65b94c9a4e23`.
The accompanying packing source is pinned as
`ce5005636175faf19f531f76eb045ce75f7a77e6adfbdda2312019f126a4fb0b`;
this receipt does not independently bind every full CRT operand in it.
Existing unchanged finite runs are referenced by the reviewed report.

For a power-of-two degree `d`, every interior coefficient of `(X+1)^d`
is even. The shifted polynomial `(X+1)^d +/- i` has constant `1 +/- i`
with Gaussian `(1+i)` valuation exactly one and leading coefficient one.
The Eisenstein argument in the Gaussian integer UFD therefore applies,
including degree one. Translation by one is an invertible polynomial
change of variable, so `X^d +/- i` is irreducible over `Q(i)`.

The cyclic factorization splits each power-two cyclotomic factor into
those two Gaussian irreducibles. Its field-factor count is exactly `2n`
for modulus `X^(2^n)-1`, `n>=1`. The negacyclic modulus has exactly two
factors. Characteristic-zero separability guarantees distinct components;
it does not silently require every Gaussian coefficient to be a unit.

The source algebra has `D` nonzero orthogonal idempotents because each
generator's two roots `+i,-i` split and are distinct. An injective
multiplicative `Q(i)`-linear map preserves their nonzero and orthogonal
properties, whether or not it preserves the ambient unit. In a product
of `r` fields, each nonzero idempotent has nonempty coordinate support;
orthogonality makes these supports disjoint. Thus `D<=r` is sound. The
result excludes a faithful full cyclic ring at small power-two volume,
not general bilinear encoders with extra operand-dependent decoding.

The four-channel cyclic degree-four example is valid. Its first generator
has square minus one because the two `X^2` terms cancel and its cross term
is `-X^4`; the second generator `iX^2` also squares to minus one modulo
`X^4-1`. Their evaluations on `1,-1,i,-i` independently choose `+i,-i`
for the two generators, proving full basis rank four. This exception is
consistent with the field-factor theorem and distinguishes it from the
stricter monomial-generator exclusion. It does not turn the original
Gaussian basis conversion into a free operation.

This theorem is complementary to this track's [general Gaussian-dyadic
quotient degree bound](dyadic-quotient-channel-volume.md). The latter uses
reduction at `2+i`, whereas the Eisenstein proof uses `1+i`; these primes
serve different purposes. A rational field-factor argument and an integral
coefficient-volume argument must retain their respective denominator
premises. Neither proves a lower bound for arbitrary integer multiplication,
nonhomomorphic encoders, several convolutions, sparse formats, changed
outputs or a new recurrence.

Attribution: the transfer research agent derived the reviewed factor and
packing mechanisms. This analytical receipt was produced independently by
the complex research agent in the coordinated AI-assisted campaign. It is
not external human review or formal verification.
