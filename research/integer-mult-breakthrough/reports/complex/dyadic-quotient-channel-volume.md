# Gaussian-dyadic product channels in a monic polynomial quotient

Status: **SCOPED ANALYTICAL OBSTRUCTION** with **EXACT FINITE REDUCTION,
FACTOR AND CRT CONTROLS**. Faithful Gaussian-dyadic algebra encodings of the
partial product need a growing polynomial degree. A native volume penalty
follows only for the explicitly stated complete, uniform-width coefficient
stream format. No arbitrary bilinear-encoding or integer-multiplication
lower bound is claimed.

## Changed product hypothesis and contract

The [partial Gaussian product](partial-gaussian-product-fusion.md) on
`D=2^f` coefficients is the algebra `B_f=R^D`, with
`R=Z[i,1/2]`. An alternative supplier might encode this algebra into one
ordinary polynomial quotient and use integer products to replace missing
Gaussian transforms. This changes the product representation, so the fixed
four-port linear-frame lower bounds do not apply.

The first discriminator assumes a faithful unital `R`-algebra encoding

    B_f -> A = R[X]/P(X),

where `P` is monic of degree `N`. Products are literal quotient products;
the map preserves sums, scalars, the identity and multiplication. Its
coefficient representation uses the complete basis `1,X,...,X^(N-1)`.
Scaled operands with a separate bilinear decoder are not automatically
such an encoding. Neither is a modular, approximate, input-dependent or
nonhomomorphic map. The degree bound below does not assume a native
implementation, and does not by itself bound the cost of a sparse format.

## Idempotents survive a small Gaussian residue field

Use the Gaussian prime `pi=2+i`. The ring homomorphism `R -> F5` sends
`i` to `3` and `1/2` to `3`. The fact that `pi` is not inverted in `R` is
essential; this is not an argument over the field `Q(i)` with arbitrary
odd denominators.

A monic quotient has a free coefficient basis over `R`. Suppose a nonzero
idempotent `e` in it reduced to zero modulo `pi`. Then `e` belongs to
`pi A`. Since `e=e^2`, it belongs to `pi^2 A`; iteration puts it in
`pi^(2^k) A` for every `k`. All its finitely many coefficient valuations
would be arbitrarily large. A nonzero Gaussian-dyadic coefficient cannot
have that property. Thus every nonzero idempotent remains nonzero after
reduction.

The `D` standard idempotents of `R^D` have nonzero, pairwise orthogonal
images which sum to the identity. The same remains true in
`F5[X]/bar(P)`. If `bar(P)` has `s` distinct monic irreducible factors,
that quotient is a product of `s` primary local rings. Each such local
ring has only the idempotents zero and one: its maximal ideal is nilpotent,
so an idempotent in it is zero, and the complement handles the other case.
Orthogonal nonzero idempotents therefore occupy distinct nonempty sets of
these `s` components. It follows that

    s >= D.

Repeated factors add nilpotents, rather than new idempotent components.
The proof would also hold for an injective multiplicative `R`-linear map
whose unit image is an idempotent below the ambient unit. The declared
supplier contract is unital; general nonunital bilinear encoders with
adjusted decoding remain outside it.

## Exact degree floor and asymptotic meaning

Let `I5(j)` be the number of monic irreducible polynomials of degree `j`
over `F5`. The identity `5^n=sum_(j|n) j I5(j)` follows by factoring
`X^(5^n)-X`; Mobius inversion gives

    I5(n) = (1/n) sum_(j|n) mobius(n/j) 5^j.

The minimum possible degree with `D` distinct irreducible factors is the
sum of the degrees of the `D` smallest such polynomials. It is obtained
by taking all degree-one factors, then degree-two factors, and so forth
until the required count is reached. Multiplicities only increase degree.
This is a necessary residue-field degree floor, not a construction of a
Gaussian-dyadic lift.

| Missing axes f | Channels D | Necessary degree N | N/D |
|---:|---:|---:|---:|
| 1 | 2 | 2 | 1 |
| 2 | 4 | 4 | 1 |
| 3 | 8 | 11 | 1.375 |
| 4 | 16 | 28 | 1.75 |
| 6 | 64 | 181 | 2.828125 |
| 8 | 256 | 1000 | 3.90625 |
| 12 | 4096 | 24154 | 5.89794921875 |
| 16 | 65536 | 507418 | 7.742584228515625 |

There are at most `(5^(j+1)-5)/4` monic irreducibles of degree at most
`j`, even if one generously counts every monic polynomial instead. The
i-th smallest irreducible degree is therefore greater than
`log_5(4i)-1`. Summing yields

    N > log_5(D!) + D log_5(4) - D
      >= D log_5(D) - O(D).

Consequently `N/D=Omega(f)` for `D=2^f`. This conclusion is analytical;
the large cases retained by the source use the exact counting formula,
not exhaustive enumeration of huge polynomial sets.

If the supplier materializes all `N` coefficient records at the retained
payload width (within a fixed factor of the original width), this is an
`Omega(f)` whole-stream volume factor before conversion, carrying or
multiplication. The actual native budget is `V(EK)^tau`: `E` counts
selected axes of the call, and `f` here counts partial-product packet
axes. They cannot be silently identified in a new product interface.

In the inherited internal shape, `E=mf` for fixed `m`,
`K=floor(d^c)`, `E>=d^beta`, and
`tau(1+c/beta)<lambda<1`. Thus

    f/(EK)^tau = Theta(E^(1-tau)/d^(c*tau))
               >= constant*d^(beta*(1-tau)-c*tau) -> infinity.

The exponent is positive by the strict condition. Complete uniform-width
quotient streams cannot fit that inherited internal budget. Small packet
axes, smaller native calls at the stopping boundary, or a different
relation between `E` and `f` are not excluded by this comparison. The
[packet audit](partial-product-packet-prefix.md) keeps these scales
separate. A coefficient-degree lower bound alone is not a bit-time bound:
variable record widths, sparse support, partial decoding, or avoiding full
polynomial materialization need separate analysis.

The transfer track's [power-two cyclic field-factor result](../transfers/bilinear-ring-packing-boundary.md)
is complementary and stronger within its family. It counts only `2n`
field factors in `Q(i)[X]/(X^(2^n)-1)`, giving a much larger required
power-two degree. Its positive four-channel nonmonomial example is
consistent with the present degree-four residue floor. The coordinator's
[linear Walsh/circulant obstruction](../obstructions/walsh-single-cyclic-convolution-boundary.md)
has a different interface and does not establish either algebraic bound.

## Exact controls and recovery

The [standalone source](../../code/complex/dyadic_quotient_channel_capacity.py),
SHA-256 `fbda3f6bb70dac5906ea762c254005700efd497f2cb996039274a600a65c9d1b`,
uses only Python standard-library integer arithmetic. Its
[four-worker run](../../runs/20261009T045653Z-complex-dyadic-quotient-channels/report.md)
passes 14 tasks in about 1.48 seconds:

- Complete enumeration of all 19,530 monic `F5` polynomials of degrees
  one through six, using Frobenius/GCD irreducibility tests independent of
  the count formula. Counts are `5,10,40,150,624,2580`.
- Full polynomial CRT constructions for `D=2,4,8,16`, at minimum residue
  degrees `2,4,11,28`; all 185 self/orthogonal idempotent pairs and the
  sum-to-unit identities are exact.
- The doubled-linear-factor negative exhausts all 25 residues and finds
  only zero and one as idempotents. It cannot supply a second component.
- Complete direct signed Gaussian-product reductions for `f=1,2,3,4`:
  all 4680 output coefficients from every character-idempotent pair agree
  with the orthogonal-idempotent identities. No producer source is imported.
  Zero extension of dyadic grids preserves residue values in all 1620
  recorded denominator controls.

```sh
python3 -B research/integer-mult-breakthrough/code/complex/dyadic_quotient_channel_capacity.py --workers 4
python3 -B research/integer-mult-breakthrough/code/complex/dyadic_quotient_channel_capacity.py --workers 1 --bounded
```

A fresh optional `--output` retains a new certificate exclusively. The
original source snapshot, protocol, stdout and certificate remain unchanged
in the task-owned ignored run directory; durable copies, hashes and
reproduction commands are recorded separately. No new package or
third-party code is required.

## Scope and next hypothesis

The proof leaves rational encodings which invert `2+i`, general modular
methods, nonhomomorphic or input-dependent bilinear encoders, extension
coefficients, variable record-width packing, sparse products, partial
output recovery and approximate schemes open. Their complete native bill
must include conversion, denominators, full payload access, coefficient
products and well-founded recursive size decreases. In particular the
Gaussian-dyadic assumption is a precise contract restriction, not a general
claim that polynomial representations cannot work.

Before a larger search, a candidate outside this scope must identify why
its growing conversion/extension cost does not consume the desired log
saving. The inherited `b>20/189981` requirement is not met here; a changed
product assembly needs new sufficient inequalities. No numerical kappa is
inferred from field factor counts.

Attribution and review: the idempotent reduction and counting discriminator
were derived in this AI-assisted complex track. The coordinator and the
transfer agent independently accepted the monic/free coefficient premise
and valuation argument analytically. Their review is not formal
verification or an independent rerun of the literal finite controls.

## Parameter-scope correction

The initial unpublished report used `f^tau` in its native comparison.
This revision restores the actual `(EK)^tau` budget and states the
inherited relation `E=mf` explicitly. The idempotent and degree arguments,
source bytes and original finite certificate are unchanged. The original
report is exactly recoverable through
[dyadic-quotient-budget-scope-recovery.patch](../../fixtures/complex/dyadic-quotient-budget-scope-recovery.patch);
both versions are pinned by the correction receipt. Small packets and
changed size relations remain open hypotheses.
