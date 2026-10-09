# Partial Gaussian product fusion and its character boundary

Status: **EXACT FINITE ALGEBRAIC CONTROLS** and **SCOPED ANALYTICAL
DEDUCTIONS**. The proposed product interface changes the linear transform
contract, so the earlier four-port width obstruction does not apply to it.
The particular rank-minimal and real half-volume formats examined here do
not supply a larger log saving. No complete native multiplier, arbitrary
dirty Gaussian word, or new kappa is claimed.

## Hypothesis, leverage and first discriminator

A missing Gaussian transform can sometimes be fused into a following product
rather than rebuilt as an independent linear primitive. If a complete
product type could avoid a growing fraction of the missing transform axes
without increasing its whole payload or invoking a same-size improved
multiplier, it could change the binary/complex coupling. This is a genuine
change of interface, rather than a different frame for the same four ports.

For `D=2^f`, write `C_f=C_1` tensor-powered `f` times, where
`C_1=[[alpha,beta],[beta,alpha]]`, `alpha=(1+i)/2`, `beta=(1-i)/2`.
The required fused product is

    q_f(a,b) = C_f^-1 ((C_f a) pointwise (C_f b)).

This is not coefficient-basis XOR convolution. For one axis, putting
`e=(a0+a1)(b0+b1)`, its exact values are

    q_1(a,b) = (e/2-a1*b1, e/2-a0*b0).

All eight local structure coefficients are nonzero, with signs given by
`[[[1,1],[1,-1]],[[-1,1],[1,1]]]/2`. The identity element is `(1,1)`.
The element `(1,-1)` squares to minus the identity. The tensor algebra is
therefore

    B_f = Q(i)[t1,...,tf]/(tj^2+1) = Q(i)^D.

All its characters and inverses are Gaussian dyadic. In particular the same
splitting holds over `R=Z[i,1/2]`, not just after adjoining odd denominators.

## Why rank D alone restores the character evaluations

The bilinear rank over `Q(i)` is exactly `D`. Its lower bound follows from
multiplication by the identity, whose image has dimension `D`; `C_f`
evaluation, coordinate products and its inverse attain it.

A stronger statement describes every rank-`D` decomposition. Write
`q(a,b)=sum_k u_k(a)v_k(b)w_k`. The output vectors `w_k` form a basis, since
multiplication by the identity is surjective. Its matrix `W` is invertible.
Each `u_k(1)` and `v_k(1)` is nonzero, since otherwise that identity map
would have rank less than `D`. Normalize both forms to take value one on
the identity, absorbing their old values into `w_k`.

Let `U,V` be the normalized row matrices. Setting either input to the
identity gives `WU=WV=I`, hence `U=V=W^-1`. Consequently

    U q(a,b) = (Ua) pointwise (Ub).

Each row of `U` is a unital algebra character. Its values on every `t_j`
are `+i` or `-i`. The `D` rows must be distinct and therefore enumerate all
sign choices. These rows are exactly the rows of `C_f`, up to permutation.
Before normalization, nonzero row scalings are also possible. Every entry
of every such character row is nonzero.

This is an algebraic constraint on minimal-rank product decompositions.
It is **not** a lower bound on the time to compute the dense forms. It does
not exclude a faster circuit for those forms, a nonminimal decomposition,
an operand restriction, a partial output contract, or a different product
representation. Calling `D` scalar products rank-optimal alone does not
make the evaluations or recovery free.

The direct transform-avoiding three-product recursion uses `3^f` Gaussian
scalar products: recursively compute `P=q(a0,b0)`, `Q=q(a1,b1)` and
`S=q(a0+a1,b0+b1)`, then return `(S-2Q,S-2P)/2`. This is a valid named
upper construction, not a rank lower bound. Its product count per input
coefficient is `(3/2)^f`. In a format that materializes every such product,
that grows exponentially in the packet axes `f`. The actual native
budget is `V(EK)^tau`, where `E` is the selected width of the native call
and `K` is its chunk width. Exponential growth in `f` is not automatically
fatal if a changed product type leaves only logarithmically many packet
axes. In the inherited internal shape `E=mf`, fixed `m`,
`K=floor(d^c)`, `E>=d^beta`, the strict condition
`tau(1+c/beta)<lambda<1` makes that budget polynomial in `E`, while
`(3/2)^f` is exponential in `E`. Thus the named construction fails in
that full-size inherited shape. Small packets remain a separate
conditional possibility; their signed product bit widths, orbit layout
and full recurrence must be paid. See the
[complete packet prefix audit](partial-product-packet-prefix.md).

## Real inputs: an exact half-volume format

For real `a`, `conjugate(C_f a)=J_all C_f a`, because `C_f^2=J_all` and
`conjugate(C_f)=C_f^-1`. Coordinate products of two such spectra retain
the same conjugacy. Only `D/2` Gaussian spectrum coordinates are independent.
Arbitrary dirty Gaussian carriers have no such restriction.

There is a bijective source format which realizes this dimension count.
Split the last axis and pack

    v = alpha*a0 + beta*a1
      = ((a0+a1) + i*(a0-a1))/2.

Then `C_(f-1) v` is the lower half of `C_f a`; the other half is its
complement-conjugate. Pack `b` in the same way, transform both packed
operands, use `D/2` Gaussian scalar products, apply `C_(f-1)^-1`, and
unpack by `a0=Re(v)+Im(v)`, `a1=Re(v)-Im(v)`. The result is exactly `q_f`.
This preserves the leading number of real payload fields: `D` real fields
become `D/2` Gaussian records, each containing two real fields. It is not
sparse insertion into `2^f` orbit positions.

For integral test inputs the pack has one fractional bit. The literal
retained product calculation uses grid `2+3(f-1)=3f-1`; the direct tensor
has grid `f`. Comparisons extend the coarser grid with zeros, and never
truncate numerators or assume cancellations authorize dropping bits.
These endpoint grids are finite arithmetic facts, not native prefix guards.
The complete payloads still need lawful layout, record lengths, carry
bounds and source/output lifecycles in a multiplier.

The packed input is an **arbitrary Gaussian vector**: any dyadic `v` is
obtained from real `a0=Re(v)+Im(v)` and `a1=Re(v)-Im(v)`. Its remaining
transform is therefore not another real-input half-spectrum problem. This
format removes exactly one global axis. For any fixed positive exponent,
`(f-1)^(1-b)` has the same log exponent as `f^(1-b)`. Constant transform
counts and a factor-two spectrum reduction also do not change that exponent.

Over `Q`, the real algebra is `Q(i)^(D/2)`. It needs `3D/2` scalar real
products, rather than the tensor upper count `3^f`: each complex component
uses three real products, and the Alder-Strassen bound `2 dim(A)-t`, with
`t=D/2` maximal ideals, gives the matching lower bound. The general bound
is stated in the primary publisher abstract of Markus Blaser's
[*A Complete Characterization of the Algebras of Minimal Bilinear Complexity*](https://epubs.siam.org/doi/10.1137/S0097539703438277),
SIAM Journal on Computing 34(2), pp.277-298, January 2005 issue, copyright
2004, online publication July 27, 2006. Only the publisher abstract and
bibliographic record were consulted; the argument above does not claim a
reading of the paywalled proof or novelty for this standard bound.

Pure record packing cannot remove a growing fraction of axes from arbitrary
real data while retaining one Gaussian field per reduced address. A block
of `D` real degrees of freedom needs at least `D/2` Gaussian fields. Reducing
to `D/2^r` such fields thus forces `r<=1`. Larger reductions require extra
channels, a growing extension field, or a genuine operand constraint; their
products and recombination must enter the new ledger.

## Evidence, target assessment and reproduction

The [standalone source](../../code/complex/partial_kernel_product_algebra.py)
uses Python integer Gaussian pairs, with no external dependency or floating
point arithmetic. Four-worker controls for `f=1,2,4,6` compare the literal
transform product, the direct signed tensor and the three-product recursion,
then check identity, generator squares, dense character invertibility, all
`D` character sign choices, real conjugacy and packed real recovery. The
incorrect coefficient-XOR identity is rejected in the one-axis negative.
One-axis characters are independently enumerated on dyadic grids of one
through four fractional bits.

The [initial run](../../runs/20261009T043532Z-complex-partial-product-first/report.md)
records 1032 counted real/imaginary product fields. The
[half-volume extension](../../runs/20261009T043835Z-complex-real-partial-product/report.md)
records 1204 counted fields. Counts do not include every ancillary identity
or basis calculation. The actual named three-product counts are `3,9,81,729`;
the packed Gaussian product counts are `1,2,8,32`. Seeds and exact hashes are
in each protocol. Both successes retain unchanged execution originals.
The first source is reconstructed exactly by the current-to-original
[recovery patch](../../fixtures/complex/partial-product-original-recovery.patch)
and [hash declaration](../../configs/complex/partial-product-recovery.json).

```sh
python3 -B research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py --workers 4
python3 -B research/integer-mult-breakthrough/code/complex/partial_kernel_product_algebra.py --workers 1 --bounded
```

In the inherited outer assembly, crossing `kappa=1e-4` still requires
`b>20/189981`, whereas the frozen full complex root is about
`0.000071744621`. Neither rank-minimal fusion nor the one-axis real format
raises `b` or replaces the outer inequalities. They fail as standalone
scale-changing routes. A new partial-product recurrence may change those
requirements, but must supply its own complete operations, decreasing
recursive sizes, payload volume and numerical/bit-time charges.

The continuation criterion is a typed bilinear mechanism which removes a
growing cost or changes the full child profile without returning all dense
characters at unchanged costs. Nonminimal algorithms, proper partial
outputs, and larger coefficient algebras remain open hypotheses; the
present controls do not refute them. An additional Gaussian-dyadic quotient
packing discriminator is investigated separately. Primary truncated FFT
reconnaissance found only the stated `O(n log n)` and constant-auxiliary-space
results in Harvey and Roche's [arXiv:1001.5272v1](https://arxiv.org/abs/1001.5272v1),
January 28, 2010; no exponent saving or native result is imported from it.

Attribution: the exact product identity, unit-normalization proof and
half-volume scalar packing were derived within this AI-assisted track.
The coordinator supplied the complement-conjugacy observation independently;
the transfer agent independently derived the one-axis product algebra and
reviewed the minimal-rank and real format arguments in the durable
[analytical receipt](../transfers/partial-product-character-independent-review.md). Internal mathematical
review is separate from formal verification and from a full native compiler.

## Parameter-scope correction

The initial unpublished analysis compared packet inflation to `f^tau`,
rather than the actual `(EK)^tau` native budget. The revised comparison
above separates packet axes from native selected width and retains the
chunk factor. The algebraic identities, character proof, source bytes and
all original run certificates are unchanged. Exact original report bytes
are recoverable with
[partial-product-budget-scope-recovery.patch](../../fixtures/complex/partial-product-budget-scope-recovery.patch);
the correction receipt records both hashes. This correction leaves
logarithmic packets open and preserves the full-size inherited exclusion.
